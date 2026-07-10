from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from arch2_labs.estimates import ESTIMATE_SOURCES, estimate_candidate
from arch2_labs.schemas import Candidate, WorkloadLayer, load_candidates

LABS_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = LABS_ROOT / "examples"


def example_dir(example_name: str) -> Path:
    path = EXAMPLES_ROOT / example_name
    if not path.exists():
        raise FileNotFoundError(f"Unknown lab example: {example_name}")
    return path


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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


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
        "inputs": {
            "config": str(config_path),
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
    return record


def _safe_replace_dir(path: Path) -> None:
    resolved = path.resolve()
    if len(resolved.parts) < 4:
        raise ValueError(f"Refusing to remove shallow path: {resolved}")
    if resolved.exists():
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


def build_decision(
    lab_title: str,
    proxy_winner: dict[str, Any],
    survivor: dict[str, Any],
    negative_traces: list[dict[str, Any]],
    objective_rankings: dict[str, Any],
) -> str:
    rejected_lines = "\n".join(
        f"- `{trace['candidate_id']}` rejected at `{trace['gate']}`. "
        f"Observed {trace['observed']} against threshold {trace['threshold']}."
        for trace in negative_traces
    )
    est = survivor["estimates"]
    obj_lines = "\n".join(
        f"- **{name}**: `{pick['candidate_id']}` ({pick['value']})"
        for name, pick in objective_rankings.items()
        if isinstance(pick, dict)
    )
    return f"""# Loop Decision

Lab: {lab_title}

Selected survivor: `{survivor['candidate_id']}`.

The cheap proxy ranked `{proxy_winner['candidate_id']}` first because it divided
total MACs by nominal PE count. The loop does not let that proxy make the final
commitment. SCALE-Sim supplied the stronger evidence, and the rejection gate
kept the proxy winner from advancing.

## Evidence Summary

- Proxy winner: `{proxy_winner['candidate_id']}` with {proxy_winner['proxy_cycles']} proxy cycles.
- Selected candidate: `{survivor['candidate_id']}` with {survivor['metrics']['total_cycles']} SCALE-Sim cycles.
- Selected minimum layer utilization: {survivor['metrics']['min_layer_util_pct']:.2f}%.
- Selected first-order energy: {est['energy']['e_total_uj']} uJ ({est['energy']['dram_energy_fraction'] * 100:.0f}% in DRAM movement); roofline bound: {est['roofline']['bound']}.

## Objective Sensitivity

The gate survivor minimizes latency among gate-passers, but the best candidate
depends on the declared objective. These first-order estimates (Horowitz 45 nm,
order-of-magnitude; see `evidence_ledger.json` sources) are decision support, not
signoff:

{obj_lines}

If two of these disagree, the loop has not yet earned a single commitment; the
architect must state which objective governs before selecting a winner.

## Rejected Alternatives

{rejected_lines}

## Commitment Boundary

Advance `{survivor['candidate_id']}` only to the next-fidelity architecture
study for this workload slice. This receipt does not claim RTL readiness,
physical-design feasibility, power signoff, or product suitability.

## Residual Risk

The workload is a compact GEMM slice, not a full XR model. The loop uses
SCALE-Sim cycle, bandwidth, and utilization reports, but it does not model
compiler scheduling, physical layout, power, thermal behavior, or quality.

## Would Overturn This Decision

A fuller workload, a different dataflow, a tighter SRAM budget, power evidence,
or a compiler mapping that improves the rejected array's utilization would
reopen the decision.
"""


def run_example(
    example_name: str,
    out_dir: Path,
    force: bool = False,
    candidate_ids: set[str] | None = None,
    precision: str = "int8",
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

    out_dir = out_dir.resolve()
    if out_dir.exists():
        if force:
            _safe_replace_dir(out_dir)
        else:
            raise FileExistsError(
                f"{out_dir} already exists. Use --force to replace it."
            )
    out_dir.mkdir(parents=True, exist_ok=True)

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

    scale_records: list[dict[str, Any]] = []
    negative_traces: list[dict[str, Any]] = []
    accepted: list[dict[str, Any]] = []
    estimated: list[dict[str, Any]] = []

    for candidate in candidates:
        run_dir = out_dir / "runs" / candidate.candidate_id
        scale_record = run_scalesim(candidate, spec.topology, spec.layout, run_dir)
        scale_records.append(scale_record)
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

    survivor = min(accepted, key=lambda item: item["metrics"]["total_cycles"])
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

    # The gate survivor minimizes latency among gate-passers, but the "best"
    # candidate depends on the declared objective. Surfacing these side by side
    # is the point: a loop that does not state its objective cannot defend a winner.
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
        "gate_survivor": survivor["candidate_id"],
    }

    evidence_ledger = {
        "schema_version": "arch2-loop-evidence/v0.1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "lab_id": spec.lab_id,
        "precision": precision,
        "final_decision_source": "scalesim",
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
                "supports": f"{survivor['candidate_id']} is the fastest candidate that survived the declared gates",
                "limits": "does not cover compiler, RTL, physical design, power, or full-model accuracy",
            },
        ],
        "survivor": survivor,
        "proxy_winner": proxy_winner["candidate_id"],
        "rejected_count": len(negative_traces),
    }

    _write_jsonl(out_dir / "candidates.jsonl", proxy_records)
    _write_jsonl(out_dir / "runs.jsonl", _relative_records(runs, out_dir))
    (out_dir / "evidence_ledger.json").write_text(
        json.dumps(evidence_ledger, indent=2, sort_keys=True) + "\n"
    )
    _write_jsonl(out_dir / "negative_traces.jsonl", negative_traces)
    (out_dir / "decision.md").write_text(
        build_decision(
            spec.title, proxy_winner, survivor, negative_traces, objective_rankings
        )
    )
    (out_dir / "manifest.yaml").write_text(
        yaml.safe_dump(
            {
                "lab_id": spec.lab_id,
                "example": example_name,
                "created_at": evidence_ledger["created_at"],
                "receipt_files": [
                    "card.yaml",
                    "environment.yaml",
                    "candidates.jsonl",
                    "runs.jsonl",
                    "evidence_ledger.json",
                    "negative_traces.jsonl",
                    "decision.md",
                ],
            },
            sort_keys=False,
        )
    )

    return {
        "out_dir": str(out_dir),
        "lab_id": spec.lab_id,
        "proxy_winner": proxy_winner["candidate_id"],
        "survivor": survivor["candidate_id"],
        "rejected_count": len(negative_traces),
    }


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
    args = parser.parse_args(argv)
    summary = run_example(
        example_name=args.example,
        out_dir=args.out,
        force=args.force,
        candidate_ids=set(args.candidates) if args.candidates else None,
        precision=args.precision,
    )
    print(yaml.safe_dump(summary, sort_keys=False).strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
