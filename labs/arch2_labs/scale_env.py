from __future__ import annotations

import argparse
import csv
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from importlib.resources import files
from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml

from arch2_labs.decisions import HumanDecision, record_human_decision
from arch2_labs.estimates import ESTIMATE_SOURCES, estimate_candidate
from arch2_labs.receipts import (
    ReceiptMetadata,
    seal_receipt,
    sha256_file,
    verify_receipt_ownership,
)
from arch2_labs.schemas import Candidate, WorkloadLayer, load_candidates

LABS_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = LABS_ROOT / "examples"


def example_dir(example_name: str) -> Path:
    source_path = EXAMPLES_ROOT / example_name
    if source_path.is_dir():
        return source_path

    resource = files("arch2_labs").joinpath("examples", example_name)
    if resource.is_dir():
        try:
            return Path(resource)
        except TypeError as exc:
            raise RuntimeError(
                "Packaged examples must be installed on a filesystem before use"
            ) from exc
    raise FileNotFoundError(f"Unknown lab example: {example_name}")


def _distribution_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "unknown"


def load_workload(topology_path: Path) -> list[WorkloadLayer]:
    with topology_path.open(newline="") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        layers = []
        for row in reader:
            if not row.get("Layer"):
                continue
            layers.append(
                WorkloadLayer(
                    name=row["Layer"],
                    m=int(row["M"]),
                    n=int(row["N"]),
                    k=int(row["K"]),
                    sparsity=row.get("Sparsity") or "1:1",
                )
            )
    if not layers:
        raise ValueError(f"No workload layers found in {topology_path}")
    return layers


file_sha256 = sha256_file


def proxy_cycles(candidate: Candidate, layers: Iterable[WorkloadLayer]) -> int:
    total_macs = sum(layer.macs for layer in layers)
    return math.ceil(total_macs / candidate.pe_count)


def write_scale_config(candidate: Candidate, config_path: Path) -> None:
    bw = candidate.dram_bandwidth_words_per_cycle
    text = f"""[general]
run_name = {candidate.candidate_id}

[run_presets]
InterfaceBandwidth = USER
UseRamulatorTrace = False

[architecture_presets]
ArrayHeight = {candidate.array_rows}
ArrayWidth = {candidate.array_cols}
ifmapsramszkB = {candidate.sram_kb}
filtersramszkB = {candidate.sram_kb}
ofmapsramszkB = {candidate.sram_kb}
IfmapOffset = 0
FilterOffset = 10000000
OfmapOffset = 20000000
Dataflow = {candidate.dataflow}
Bandwidth = {bw},{bw},{bw}
ReadRequestBuffer = 64
WriteRequestBuffer = 64

[layout]
IfmapCustomLayout = False
IfmapSRAMBankBandwidth = {bw}
IfmapSRAMBankNum = 1
IfmapSRAMBankPort = 2
FilterCustomLayout = False
FilterSRAMBankBandwidth = {bw}
FilterSRAMBankNum = 1
FilterSRAMBankPort = 2

[sparsity]
SparsitySupport = False
SparseRep = dense
OptimizedMapping = False
BlockSize = 4
RandomNumberGeneratorSeed = 40
"""
    config_path.write_text(text)


def _clean_row(row: dict[str, str]) -> dict[str, str]:
    return {
        str(k).strip(): str(v).strip()
        for k, v in row.items()
        if k is not None and str(k).strip()
    }


def _read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as f:
        return [_clean_row(row) for row in csv.DictReader(f, skipinitialspace=True)]


def parse_scale_reports(report_dir: Path) -> dict[str, Any]:
    compute_rows = _read_csv_dicts(report_dir / "COMPUTE_REPORT.csv")
    bandwidth_rows = _read_csv_dicts(report_dir / "BANDWIDTH_REPORT.csv")
    access_rows = _read_csv_dicts(report_dir / "DETAILED_ACCESS_REPORT.csv")

    total_cycles = sum(float(row["Total Cycles"]) for row in compute_rows)
    stall_cycles = sum(float(row["Stall Cycles"]) for row in compute_rows)
    util_values = [float(row["Overall Util %"]) for row in compute_rows]
    mapping_values = [float(row["Mapping Efficiency %"]) for row in compute_rows]
    compute_util_values = [float(row["Compute Util %"]) for row in compute_rows]

    dram_bw_fields = ["Avg IFMAP DRAM BW", "Avg FILTER DRAM BW", "Avg OFMAP DRAM BW"]
    max_dram_bw = max(
        float(row[field]) for row in bandwidth_rows for field in dram_bw_fields
    )

    dram_reads = sum(
        float(row["DRAM IFMAP Reads"]) + float(row["DRAM Filter Reads"])
        for row in access_rows
    )
    dram_writes = sum(float(row["DRAM OFMAP Writes"]) for row in access_rows)
    sram_reads = sum(
        float(row["SRAM IFMAP Reads"]) + float(row["SRAM Filter Reads"])
        for row in access_rows
    )
    sram_writes = sum(float(row["SRAM OFMAP Writes"]) for row in access_rows)

    return {
        "total_cycles": round(total_cycles),
        "stall_cycles": round(stall_cycles),
        "min_layer_util_pct": min(util_values),
        "avg_layer_util_pct": sum(util_values) / len(util_values),
        "avg_mapping_efficiency_pct": sum(mapping_values) / len(mapping_values),
        "avg_compute_util_pct": sum(compute_util_values) / len(compute_util_values),
        "max_observed_dram_bw_words_per_cycle": max_dram_bw,
        "dram_reads": round(dram_reads),
        "dram_writes": round(dram_writes),
        "sram_reads": round(sram_reads),
        "sram_writes": round(sram_writes),
        "sram_accesses": round(sram_reads + sram_writes),
        "dram_accesses": round(dram_reads + dram_writes),
        "layers": compute_rows,
    }


def assess_candidate(
    candidate: Candidate, metrics: dict[str, Any]
) -> tuple[bool, dict[str, Any] | None]:
    """Apply the two HARD gates. Utilization is deliberately NOT a hard gate.

    We learned empirically that a low-utilization array can still be the best on
    latency and energy, so rejecting on utilization rejects the wrong candidate.
    Utilization and roofline stay as diagnostics (in the metrics) that explain a
    result; the hard gates are the two an architect actually commits against: a
    stated silicon/area budget (cheap, knowable before the simulator) and the
    real-time deadline (revealed by the simulator).
    """
    if candidate.pe_count > candidate.area_budget_pes:
        return False, {
            "gate": "area_budget_pes",
            "observed": candidate.pe_count,
            "threshold": candidate.area_budget_pes,
            "reason": "candidate exceeds the declared silicon/area budget",
        }
    if metrics["total_cycles"] > candidate.deadline_cycles:
        return False, {
            "gate": "deadline_cycles",
            "observed": metrics["total_cycles"],
            "threshold": candidate.deadline_cycles,
            "reason": "SCALE-Sim cycle count misses the loop deadline",
        }
    return True, None


def run_scalesim(
    candidate: Candidate,
    topology_path: Path,
    layout_path: Path,
    candidate_dir: Path,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    inputs_dir = candidate_dir / "inputs"
    results_dir = candidate_dir / "scalesim-results"
    inputs_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    config_path = inputs_dir / "scale.cfg"
    topology_copy = inputs_dir / "topology.csv"
    layout_copy = inputs_dir / "layout.csv"
    write_scale_config(candidate, config_path)
    shutil.copy2(topology_path, topology_copy)
    shutil.copy2(layout_path, layout_copy)

    command = [
        sys.executable,
        "-m",
        "scalesim.scale",
        "-c",
        str(config_path),
        "-t",
        str(topology_copy),
        "-l",
        str(layout_copy),
        "-p",
        str(results_dir),
        "-i",
        "gemm",
        "-s",
        "N",
    ]
    started_at = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(
        command, text=True, capture_output=True, timeout=timeout_seconds
    )
    completed_at = datetime.now(timezone.utc).isoformat()

    report_dir = results_dir / candidate.candidate_id
    record: dict[str, Any] = {
        "candidate_id": candidate.candidate_id,
        "stage": "scalesim",
        "status": "ok" if proc.returncode == 0 else "failed",
        "command": command,
        "returncode": proc.returncode,
        "started_at": started_at,
        "completed_at": completed_at,
        "stdout_tail": proc.stdout.splitlines()[-20:],
        "stderr_tail": proc.stderr.splitlines()[-20:],
        "tool": {"name": "SCALE-Sim", "version": _distribution_version("scalesim")},
        "runtime": {
            "python": platform.python_version(),
            "executable": sys.executable,
        },
        "inputs": {
            "config": str(config_path),
            "config_sha256": file_sha256(config_path),
            "topology": str(topology_copy),
            "layout": str(layout_copy),
            "topology_sha256": file_sha256(topology_copy),
            "layout_sha256": file_sha256(layout_copy),
        },
        "outputs": {
            "report_dir": str(report_dir),
        },
    }

    if proc.returncode == 0:
        record["metrics"] = parse_scale_reports(report_dir)
        record["outputs"]["raw_files"] = [
            {"path": str(path), "sha256": file_sha256(path)}
            for path in sorted(report_dir.rglob("*"))
            if path.is_file()
        ]
    return record


def _verify_replaceable_dir(path: Path) -> Path:
    expanded = path.expanduser().absolute()
    if expanded.is_symlink():
        raise ValueError(f"refusing to replace a symbolic link: {expanded}")
    resolved = expanded.resolve()
    protected = {Path.home().resolve(), LABS_ROOT.resolve()}
    protected.update(LABS_ROOT.resolve().parents)
    if resolved in protected:
        raise ValueError(f"refusing to replace protected path: {resolved}")
    verify_receipt_ownership(resolved)
    return resolved


def _safe_replace_dir(path: Path) -> None:
    resolved = _verify_replaceable_dir(path)
    shutil.rmtree(resolved)


def _write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    with path.open("w") as f:
        for record in records:
            f.write(json.dumps(record, sort_keys=True) + "\n")


def _relative_records(
    records: Iterable[dict[str, Any]], root: Path
) -> list[dict[str, Any]]:
    root = root.resolve()

    def convert(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: convert(item) for key, item in value.items()}
        if isinstance(value, list):
            return [convert(item) for item in value]
        if isinstance(value, str):
            path = Path(value)
            if path.is_absolute():
                try:
                    return str(path.resolve().relative_to(root))
                except ValueError:
                    return value
        return value

    return [convert(record) for record in records]


def build_recommendation(
    lab_id: str,
    lab_title: str,
    proxy_winner: dict[str, Any],
    recommended: dict[str, Any],
    negative_traces: list[dict[str, Any]],
    objective_rankings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "arch2-machine-recommendation/v0.1",
        "lab_id": lab_id,
        "lab_title": lab_title,
        "candidate_id": recommended["candidate_id"],
        "basis": "lowest SCALE-Sim cycle count among candidates that passed the declared gates",
        "evidence_source": "scalesim",
        "human_decision": False,
        "commitment": "none",
        "proxy_winner": proxy_winner["candidate_id"],
        "objective_rankings": objective_rankings,
        "rejected_candidate_ids": [trace["candidate_id"] for trace in negative_traces],
        "limits": [
            "compact GEMM workload slice",
            "no compiler scheduling evidence",
            "no RTL or physical-design evidence",
            "no power, thermal, or product evidence",
        ],
    }


def build_replayable_card(
    template: dict[str, Any],
    receipt_id: str,
    scale_records: list[dict[str, Any]],
    negative_traces: list[dict[str, Any]],
) -> dict[str, Any]:
    card = template["design_loop_card"]
    successful = [record for record in scale_records if record["status"] == "ok"]
    if not successful:
        raise ValueError("a replayable card requires at least one successful run")
    tool_version = successful[0]["tool"]["version"]
    card.update(
        {
            "conformance_level": 2,
            "representation": {
                "state_schema_id": "arch2-labs.scale-proxy-mirage-state.v1",
                "ir_level": "GEMM layer dimensions, array geometry, and fixed memory parameters.",
                "reads": [
                    "Candidate action records.",
                    "XR-like GEMM topology and layout inputs.",
                ],
                "writes": [
                    "SCALE-Sim cycle, utilization, bandwidth, and access reports.",
                    "First-order energy, roofline, and area estimates.",
                ],
                "uncertainties": [
                    "The workload is a compact slice rather than a full XR model.",
                    "The simulator omits compiler, physical, power, and thermal effects.",
                ],
            },
            "environment": {
                "environment_id": f"scale-sim-{tool_version}-proxy-mirage-v1",
                "actions": ["Evaluate one of the four declared array shapes."],
                "invalid_actions": [
                    "Change the workload, dataflow, SRAM allocation, or bandwidth.",
                    "Advance a candidate that fails a declared area or deadline gate.",
                ],
                "blast_radius_limit": "Analysis-only output under one receipt directory; no RTL or project source is modified.",
                "observations": [
                    "Proxy cycle rank.",
                    "SCALE-Sim cycle, utilization, bandwidth, and memory-access reports.",
                    "Declared-gate rejection records.",
                ],
                "fidelity": "simulation",
            },
            "method_role": {
                "roles": ["predict", "critique", "verify"],
                "actor_map": [
                    {
                        "actor_id": "arch2-labs-runner",
                        "role": "Generate the proxy ranking, run the simulator, and make a noncommitting recommendation.",
                        "reads": ["Declared candidates and environment inputs."],
                        "writes": [
                            "Evidence, negative traces, and recommendation.json."
                        ],
                        "authority": "May recommend a gate passer; cannot make or own the human commitment.",
                    },
                    {
                        "actor_id": "declared-gate-evaluator",
                        "role": "Apply the fixed area and deadline rejection gates.",
                        "reads": ["Candidate PE count and simulated cycle count."],
                        "writes": ["Negative traces."],
                        "authority": "May reject candidates; cannot select the human commitment.",
                    },
                ],
            },
            "feedback_budget": {
                "evaluations": len(scale_records),
                "latency": "One local SCALE-Sim process per candidate with a 120-second timeout.",
                "cost": "Local CPU execution only.",
                "fidelity": "One cheap proxy pass followed by architecture simulation.",
                "model_side_cost": {
                    "model_calls": 0,
                    "gpu_hours": 0,
                    "energy_or_carbon": "No model inference is used by this example.",
                    "human_review": "One explicit architecture decision after evidence review.",
                },
            },
            "evidence": {
                "baseline_id": successful[-1]["candidate_id"],
                "records": [
                    {
                        "evidence_id": f"scalesim-{record['candidate_id']}",
                        "kind": "SCALE-Sim raw report set",
                        "workload_id": "xr-slice-gemm-v1",
                        "seed": "SCALE-Sim deterministic configuration",
                        "provenance": {
                            "tool_version": f"SCALE-Sim {record['tool']['version']}",
                            "parameter_hash": f"sha256:{record['inputs']['config_sha256']}",
                        },
                    }
                    for record in successful
                ],
            },
            "negative_traces": [
                {
                    "candidate_id": trace["candidate_id"],
                    "reason": trace["reason"],
                    "stage": trace["stage"],
                    "gate": trace["gate"],
                }
                for trace in negative_traces
            ],
        }
    )
    card["x-arch2-labs"].update(
        {
            "receipt_id": receipt_id,
            "template_status": "replayable_evidence",
            "environment_contract": "environment.yaml",
            "recommendation_record": "recommendation.json",
        }
    )
    return template


def _generate_example(
    example_name: str,
    out_dir: Path,
    candidate_ids: set[str] | None = None,
    precision: str = "int8",
    human_decision: Path | Mapping[str, Any] | HumanDecision | None = None,
) -> dict[str, Any]:
    ex_dir = example_dir(example_name)
    spec = load_candidates(ex_dir / "configs" / "candidates.yaml", ex_dir)
    layers = load_workload(spec.topology)
    workload_macs = sum(layer.macs for layer in layers)
    candidates = [
        c
        for c in spec.candidates
        if candidate_ids is None or c.candidate_id in candidate_ids
    ]
    if not candidates:
        raise ValueError("No candidates selected for the run")

    out_dir = out_dir.absolute()

    receipt_id = str(uuid.uuid4())
    shutil.copy2(ex_dir / "starter_receipt" / "card.yaml", out_dir / "card.yaml")
    shutil.copy2(
        ex_dir / "starter_receipt" / "environment.yaml", out_dir / "environment.yaml"
    )

    proxy_records = []
    for candidate in candidates:
        proxy_records.append(
            {
                **asdict(candidate),
                "stage": "proxy",
                "action": candidate.action_dict(),
                "proxy_cycles": proxy_cycles(candidate, layers),
                "workload_macs": sum(layer.macs for layer in layers),
            }
        )
    proxy_records.sort(key=lambda item: item["proxy_cycles"])
    for rank, record in enumerate(proxy_records, start=1):
        record["proxy_rank"] = rank

    runs: list[dict[str, Any]] = [
        {
            "candidate_id": record["candidate_id"],
            "stage": "proxy",
            "status": "ok",
            "proxy_cycles": record["proxy_cycles"],
            "proxy_rank": record["proxy_rank"],
            "cost": "static MAC/PE estimate",
        }
        for record in proxy_records
    ]

    negative_traces: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    estimated: list[dict[str, Any]] = []

    for candidate in candidates:
        run_dir = out_dir / "runs" / candidate.candidate_id
        scale_record = run_scalesim(candidate, spec.topology, spec.layout, run_dir)
        runs.append(scale_record)

        if scale_record["status"] != "ok":
            negative_traces.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "stage": "scalesim",
                    "gate": "simulator_execution",
                    "observed": scale_record["returncode"],
                    "threshold": 0,
                    "reason": "SCALE-Sim did not complete successfully",
                }
            )
            continue

        metrics = scale_record["metrics"]
        metrics["workload_macs"] = workload_macs
        estimates = estimate_candidate(metrics, candidate, precision)
        scale_record["estimates"] = estimates
        accepted_flag, rejection = assess_candidate(candidate, metrics)
        candidate_result = {
            "candidate_id": candidate.candidate_id,
            "action": candidate.action_dict(),
            "metrics": metrics,
            "estimates": estimates,
            "accepted": accepted_flag,
        }
        estimated.append(candidate_result)
        if accepted_flag:
            accepted.append(candidate_result)
        else:
            assert rejection is not None
            negative_traces.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "stage": "scalesim",
                    **rejection,
                }
            )

    if not accepted:
        raise RuntimeError("No candidate survived the SCALE-Sim rejection gates")

    recommended = min(accepted, key=lambda item: item["metrics"]["total_cycles"])
    proxy_winner = proxy_records[0]

    def _pick(
        items: list[dict[str, Any]], path: list[str], maximize: bool = False
    ) -> dict[str, Any]:
        def value(item: dict[str, Any]) -> float:
            node: Any = item["estimates"]
            for key in path:
                node = node[key]
            return node

        chosen = (max if maximize else min)(items, key=value)
        return {"candidate_id": chosen["candidate_id"], "value": value(chosen)}

    # The machine recommendation minimizes latency among gate-passers. Other
    # objectives remain visible so a human can make and own the commitment.
    objective_rankings = {
        "min_latency_us": _pick(estimated, ["derived", "latency_us"]),
        "min_energy_uj": _pick(estimated, ["energy", "e_total_uj"]),
        "min_edp": _pick(estimated, ["derived", "edp_uj_us"]),
        "max_tops_per_watt": _pick(
            estimated, ["derived", "tops_per_watt"], maximize=True
        ),
        "max_tops_per_mm2": _pick(
            estimated, ["derived", "tops_per_mm2"], maximize=True
        ),
        "latency_under_declared_gates": recommended["candidate_id"],
    }

    created_at = datetime.now(timezone.utc).isoformat()
    evidence_ledger = {
        "schema_version": "arch2-loop-evidence/v0.1",
        "created_at": created_at,
        "lab_id": spec.lab_id,
        "precision": precision,
        "recommendation_evidence_source": "scalesim",
        "objective_rankings": objective_rankings,
        "estimate_sources": ESTIMATE_SOURCES,
        "stages": [
            {
                "stage": "proxy",
                "fidelity": "cheap estimate",
                "supports": f"{proxy_winner['candidate_id']} appears fastest by MACs divided by PEs",
                "limits": "ignores utilization, mapping behavior, bandwidth effects, and validation risk",
            },
            {
                "stage": "scalesim",
                "fidelity": "simulator CSV reports",
                "supports": f"{recommended['candidate_id']} has the lowest measured cycles among declared-gate passers",
                "limits": "does not cover compiler, RTL, physical design, power, or full-model accuracy",
            },
        ],
        "candidate_outcomes": estimated,
        "machine_recommendation": recommended["candidate_id"],
        "proxy_winner": proxy_winner["candidate_id"],
        "rejected_count": len(negative_traces),
    }

    _write_jsonl(out_dir / "candidates.jsonl", proxy_records)
    _write_jsonl(out_dir / "runs.jsonl", _relative_records(runs, out_dir))
    (out_dir / "evidence_ledger.json").write_text(
        json.dumps(evidence_ledger, indent=2, sort_keys=True) + "\n"
    )
    _write_jsonl(out_dir / "negative_traces.jsonl", negative_traces)
    recommendation = build_recommendation(
        spec.lab_id,
        spec.title,
        proxy_winner,
        recommended,
        negative_traces,
        objective_rankings,
    )
    (out_dir / "recommendation.json").write_text(
        json.dumps(recommendation, indent=2, sort_keys=True) + "\n"
    )
    card_template = yaml.safe_load((out_dir / "card.yaml").read_text())
    card = build_replayable_card(
        card_template,
        receipt_id,
        [record for record in runs if record["stage"] == "scalesim"],
        negative_traces,
    )
    (out_dir / "card.yaml").write_text(yaml.safe_dump(card, sort_keys=False))

    seal_receipt(
        out_dir,
        ReceiptMetadata(
            receipt_id=receipt_id,
            lab_id=spec.lab_id,
            example=example_name,
            created_at=created_at,
            status="awaiting_human_decision",
        ),
    )
    status = "awaiting_human_decision"
    if human_decision is not None:
        record_human_decision(out_dir, human_decision)
        status = "complete"

    return {
        "out_dir": str(out_dir),
        "lab_id": spec.lab_id,
        "proxy_winner": proxy_winner["candidate_id"],
        "recommended_candidate": recommended["candidate_id"],
        "rejected_count": len(negative_traces),
        "status": status,
    }


def _promote_staged_receipt(staging: Path, out_dir: Path, force: bool) -> None:
    if out_dir.is_symlink():
        raise ValueError(f"refusing to replace a symbolic link: {out_dir}")
    if not out_dir.exists():
        os.replace(staging, out_dir)
        return
    if not force:
        raise FileExistsError(f"{out_dir} already exists. Use --force to replace it.")

    _verify_replaceable_dir(out_dir)
    backup = out_dir.with_name(f".{out_dir.name}.arch2-backup-{uuid.uuid4().hex}")
    os.replace(out_dir, backup)
    try:
        os.replace(staging, out_dir)
    except BaseException:
        os.replace(backup, out_dir)
        raise
    _safe_replace_dir(backup)


def run_example(
    example_name: str,
    out_dir: Path,
    force: bool = False,
    candidate_ids: set[str] | None = None,
    precision: str = "int8",
    human_decision: Path | Mapping[str, Any] | HumanDecision | None = None,
) -> dict[str, Any]:
    """Build a receipt in staging and promote it only after generation succeeds."""
    out_dir = out_dir.expanduser().absolute()
    if out_dir.is_symlink():
        raise ValueError(f"refusing to replace a symbolic link: {out_dir}")
    if out_dir.exists():
        if not force:
            raise FileExistsError(
                f"{out_dir} already exists. Use --force to replace it."
            )
        _verify_replaceable_dir(out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    staging = Path(
        tempfile.mkdtemp(
            prefix=f".{out_dir.name}.arch2-staging-", dir=str(out_dir.parent)
        )
    )
    try:
        summary = _generate_example(
            example_name=example_name,
            out_dir=staging,
            candidate_ids=candidate_ids,
            precision=precision,
            human_decision=human_decision,
        )
        if summary["status"] == "complete":
            from arch2_labs.validators import validate_receipt

            errors = validate_receipt(staging)
            if errors:
                raise RuntimeError(
                    "generated receipt failed validation: " + "; ".join(errors)
                )
        else:
            verify_receipt_ownership(staging)
        _promote_staged_receipt(staging, out_dir, force)
    except BaseException:
        if staging.exists():
            shutil.rmtree(staging)
        raise
    summary["out_dir"] = str(out_dir)
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run an Architecture 2.0 lab environment."
    )
    parser.add_argument(
        "--example",
        default="scale_proxy_mirage",
        help="Example name under labs/examples.",
    )
    parser.add_argument(
        "--out", required=True, type=Path, help="Output loop receipt directory."
    )
    parser.add_argument(
        "--force", action="store_true", help="Replace an existing output directory."
    )
    parser.add_argument(
        "--candidate",
        action="append",
        dest="candidates",
        help="Run only this candidate ID. Repeat to run multiple candidates.",
    )
    parser.add_argument(
        "--precision",
        default="int8",
        choices=["int8", "fp16", "fp32"],
        help="Operand precision for first-order energy/area estimates.",
    )
    parser.add_argument(
        "--decision-file",
        type=Path,
        help=(
            "Explicit human decision YAML. Without it, the runner emits an "
            "evidence-only draft that does not validate as a complete receipt."
        ),
    )
    args = parser.parse_args(argv)
    summary = run_example(
        example_name=args.example,
        out_dir=args.out,
        force=args.force,
        candidate_ids=set(args.candidates) if args.candidates else None,
        precision=args.precision,
        human_decision=args.decision_file,
    )
    print(yaml.safe_dump(summary, sort_keys=False).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
