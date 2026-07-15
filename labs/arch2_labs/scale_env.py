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
from arch2_labs.schemas import (
    Candidate,
    WorkloadLayer,
    load_candidates,
    require_safe_slug,
)

LABS_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_ROOT = LABS_ROOT / "examples"


def example_dir(example_name: str) -> Path:
    require_safe_slug(example_name, "example name")
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
            dimensions = {field: int(row[field]) for field in ("M", "N", "K")}
            if any(value <= 0 for value in dimensions.values()):
                raise ValueError(
                    f"workload layer {row['Layer']} dimensions must be positive"
                )
            layers.append(
                WorkloadLayer(
                    name=row["Layer"],
                    m=dimensions["M"],
                    n=dimensions["N"],
                    k=dimensions["K"],
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
    """Apply the two pass/fail rejection checks. Utilization remains diagnostic.

    We learned empirically that a low-utilization array can still be the best on
    latency and energy, so rejecting on utilization rejects the wrong candidate.
    Utilization and roofline stay as diagnostics (in the metrics) that explain a
    result. The two checks enforce the PE budget (cheap and knowable before the
    simulator) and the real-time deadline (revealed by the simulator).
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
    baseline_id: str,
    proxy_winner: dict[str, Any],
    recommended: dict[str, Any],
    negative_traces: list[dict[str, Any]],
    objective_rankings: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "arch2-machine-recommendation/v0.1",
        "lab_id": lab_id,
        "lab_title": lab_title,
        "baseline_id": baseline_id,
        "candidate_id": recommended["candidate_id"],
        "basis": "lowest derived latency among candidates that passed the declared rejection checks",
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
    receipt_root: Path,
    receipt_id: str,
    baseline_id: str,
    scale_records: list[dict[str, Any]],
    negative_traces: list[dict[str, Any]],
) -> dict[str, Any]:
    successful = [record for record in scale_records if record["status"] == "ok"]
    if not successful:
        raise ValueError("a replayable card requires at least one successful run")
    tool_version = successful[0]["tool"]["version"]
    receipt_root = receipt_root.resolve()

    def relative(raw_path: str) -> str:
        return Path(raw_path).resolve().relative_to(receipt_root).as_posix()

    rejected_by_id = {trace["candidate_id"]: trace for trace in negative_traces}
    eligible = [
        record for record in successful if record["candidate_id"] not in rejected_by_id
    ]
    recommended = min(
        eligible,
        key=lambda record: record["estimates"]["derived"]["latency_us"],
    )
    baseline = next(
        record for record in successful if record["candidate_id"] == baseline_id
    )
    evidence_records: list[dict[str, Any]] = []
    replay_inputs_by_uri: dict[str, dict[str, str]] = {}
    replay_outputs_by_uri: dict[str, dict[str, str]] = {}
    replay_commands: list[dict[str, str]] = []
    for record in successful:
        candidate_id = record["candidate_id"]
        inputs = []
        for name in ("config", "topology", "layout"):
            uri = relative(record["inputs"][name])
            artifact = {
                "artifact_id": f"{candidate_id}-{name}",
                "uri": uri,
                "integrity": {"sha256": f"sha256:{record['inputs'][f'{name}_sha256']}"},
            }
            inputs.append(artifact)
            replay_inputs_by_uri[uri] = {
                "artifact_id": artifact["artifact_id"],
                "uri": uri,
                "sha256": artifact["integrity"]["sha256"],
            }

        outputs = []
        for raw in record["outputs"]["raw_files"]:
            uri = relative(raw["path"])
            artifact = {
                "artifact_id": f"{candidate_id}-{Path(uri).stem.lower()}",
                "uri": uri,
                "integrity": {"sha256": f"sha256:{raw['sha256']}"},
            }
            outputs.append(artifact)
            replay_outputs_by_uri[uri] = {
                "artifact_id": artifact["artifact_id"],
                "uri": uri,
                "sha256": artifact["integrity"]["sha256"],
            }

        compute_output = next(
            artifact
            for artifact in outputs
            if Path(artifact["uri"]).name == "COMPUTE_REPORT.csv"
        )
        evidence_records.append(
            {
                "evidence_id": f"scalesim-{candidate_id}",
                "producer": {
                    "producer_id": "arch2-labs-runner",
                    "producer_type": "pipeline",
                },
                "kind": "SCALE-Sim raw report set",
                "status": "computed",
                "tool": {
                    "name": "SCALE-Sim",
                    "version": record["tool"]["version"],
                },
                "inputs": inputs,
                "outputs": outputs,
                "scope": (
                    f"Candidate {candidate_id}, the fixed XR-like GEMM slice, "
                    "weight-stationary dataflow, and declared simulator settings."
                ),
                "uncertainty": (
                    "Architecture simulation does not establish compiler, RTL, "
                    "physical-design, power, thermal, or product outcomes."
                ),
                "limitations": [
                    "The workload is a compact slice rather than a full XR model.",
                    "First-order energy and area estimates are not signoff evidence.",
                ],
                "integrity": compute_output["integrity"],
            }
        )
        command = (
            "python -m scalesim.scale "
            f"-c {relative(record['inputs']['config'])} "
            f"-t {relative(record['inputs']['topology'])} "
            f"-l {relative(record['inputs']['layout'])} "
            f"-p runs/{candidate_id}/scalesim-results -i gemm -s N"
        )
        replay_commands.append({"command": command, "working_directory": "."})

    gates: list[dict[str, Any]] = []
    failed_or_rejected: list[dict[str, Any]] = []
    for record in scale_records:
        candidate_id = record["candidate_id"]
        evidence_refs = [f"scalesim-{candidate_id}"] if record["status"] == "ok" else []
        trace = rejected_by_id.get(candidate_id)
        if record["status"] != "ok":
            gate_id = f"gate-simulator-execution-{candidate_id}"
            gates.append(
                {
                    "gate_id": gate_id,
                    "category": "process",
                    "criterion": "SCALE-Sim must exit successfully before the architecture rejection checks are evaluated.",
                    "result": "not_run",
                    "authority_id": "declared-gate-evaluator",
                    "waiver_rule": {"allowed": False},
                    "evidence_refs": [],
                    "disposition": "reject",
                    "notes": "The environment-failure trace records the unsuccessful execution.",
                }
            )
            failed_or_rejected.append(
                {
                    "record_id": f"environment-failure-{candidate_id}",
                    "kind": "environment_failure",
                    "candidate_id": candidate_id,
                    "stage": trace["stage"],
                    "reason": trace["reason"],
                    "gate_ref": gate_id,
                    "evidence_refs": [],
                }
            )
            continue

        failed_gate = trace.get("gate") if trace else None
        area_gate_id = f"gate-area-budget-{candidate_id}"
        deadline_gate_id = f"gate-deadline-{candidate_id}"
        gates.extend(
            [
                {
                    "gate_id": area_gate_id,
                    "category": "area",
                    "criterion": "Candidate processing-element count must not exceed its declared 1024-PE budget.",
                    "result": "failed"
                    if failed_gate == "area_budget_pes"
                    else "passed",
                    "authority_id": "declared-gate-evaluator",
                    "waiver_rule": {"allowed": False},
                    "evidence_refs": evidence_refs,
                    "disposition": "reject"
                    if failed_gate == "area_budget_pes"
                    else "continue",
                },
                {
                    "gate_id": deadline_gate_id,
                    "category": "performance",
                    "criterion": "SCALE-Sim total cycles must not exceed the declared 90000-cycle deadline.",
                    "result": (
                        "not_run"
                        if failed_gate == "area_budget_pes"
                        else "failed"
                        if failed_gate == "deadline_cycles"
                        else "passed"
                    ),
                    "authority_id": "declared-gate-evaluator",
                    "waiver_rule": {"allowed": False},
                    "evidence_refs": (
                        [] if failed_gate == "area_budget_pes" else evidence_refs
                    ),
                    "disposition": "reject"
                    if failed_gate == "deadline_cycles"
                    else "continue",
                },
            ]
        )
        if trace:
            failed_or_rejected.append(
                {
                    "record_id": f"failed-gate-{candidate_id}",
                    "kind": "failed_gate",
                    "candidate_id": candidate_id,
                    "stage": trace["stage"],
                    "reason": trace["reason"],
                    "gate_ref": (
                        area_gate_id
                        if failed_gate == "area_budget_pes"
                        else deadline_gate_id
                    ),
                    "evidence_refs": evidence_refs,
                    "x-arch2-labs": {
                        "observed": trace.get("observed"),
                        "threshold": trace.get("threshold"),
                    },
                }
            )

    evidence_refs = [record["evidence_id"] for record in evidence_records]
    objective_specs = {
        "latency_under_declared_gates": {
            "claim_id": "claim-gate-passing-latency",
            "label": "derived latency",
            "path": ("derived", "latency_us"),
            "unit": "us",
            "maximize": False,
        },
        "energy_under_declared_gates": {
            "claim_id": "claim-gate-passing-energy",
            "label": "first-order total energy estimate",
            "path": ("energy", "e_total_uj"),
            "unit": "uJ",
            "maximize": False,
        },
        "area_efficiency_under_declared_gates": {
            "claim_id": "claim-gate-passing-area-efficiency",
            "label": "first-order area efficiency estimate",
            "path": ("derived", "tops_per_mm2"),
            "unit": "TOPS/mm^2",
            "maximize": True,
        },
    }
    objective_claims = []
    for spec in objective_specs.values():
        section, metric = spec["path"]
        chooser = max if spec["maximize"] else min
        winner = chooser(
            eligible,
            key=lambda record: record["estimates"][section][metric],
        )
        winner_value = winner["estimates"][section][metric]
        baseline_value = baseline["estimates"][section][metric]
        comparison = "highest" if spec["maximize"] else "lowest"
        objective_claims.append(
            {
                "claim_id": spec["claim_id"],
                "claim_type": "architecture_outcome",
                "statement": (
                    f"{winner['candidate_id']} has the {comparison} {spec['label']} "
                    "among candidates that passed the declared rejection checks."
                ),
                "baseline_or_comparator": (
                    f"Baseline {baseline_id} and every evaluated candidate that passed the declared checks."
                ),
                "outcome": (
                    f"{winner['candidate_id']} has {winner_value:.6g} {spec['unit']}; "
                    f"baseline {baseline_id} has {baseline_value:.6g} {spec['unit']}."
                ),
                "scope": "The fixed XR-like GEMM slice, SCALE-Sim configuration, selected candidates, and declared first-order estimates in this run archive.",
                "non_claims": [
                    "The result is RTL-ready, signoff-ready, tapeout-ready, or product-ready.",
                    "The ranking generalizes to a full workload or another simulator configuration.",
                ],
                "status": "supported",
                "evidence_refs": evidence_refs,
            }
        )
    card = {
        "card_id": "scale-proxy-mirage",
        "profiles": {
            "context": "complete",
            "inspectability": "complete",
            "replay": "partial",
            "independent_review": "not_claimed",
            "disclosure": "complete",
            "decision_rights": "complete",
        },
        "profile_gaps": {
            "replay": [
                "The run archive binds the original successful runs, but a separate replay has not been attempted."
            ]
        },
        "intent": template["design_loop_card"]["intent"],
        "task": template["design_loop_card"]["task"],
        "design_space": template["design_loop_card"]["design_space"],
        "representation": {
            "state_schema_id": "arch2-labs.scale-proxy-mirage-state.v2",
            "abstraction": "GEMM layer dimensions, array geometry, and fixed memory parameters.",
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
            "environment_id": f"scale-sim-{tool_version}-proxy-mirage-v2",
            "actions": ["Evaluate one of the declared array shapes."],
            "invalid_actions": [
                "Change the workload, dataflow, SRAM allocation, or bandwidth.",
                "Advance a candidate that fails a declared area or deadline check.",
            ],
            "blast_radius_limit": "Analysis-only output under one run directory; no RTL or project source is modified.",
            "observations": [
                "Proxy cycle rank.",
                "SCALE-Sim cycle, utilization, bandwidth, and memory-access reports.",
                "Declared rejection-check records.",
            ],
            "fidelity": "Architecture simulation plus first-order estimates.",
        },
        "method_roles": [
            {
                "actor_id": "arch2-labs-runner",
                "actor_type": "pipeline",
                "roles": ["predict", "verify"],
                "reads": ["Declared candidates and environment inputs."],
                "writes": [
                    "Evidence, rejected-alternative records, and a noncommitting recommendation."
                ],
                "limitations": ["Cannot make or own the final decision."],
            },
            {
                "actor_id": "declared-gate-evaluator",
                "actor_type": "policy",
                "roles": ["critique", "verify"],
                "reads": ["Candidate PE count and simulated cycle count."],
                "writes": ["Typed rejection-check results and rejection records."],
                "limitations": [
                    "Cannot select or authorize a candidate that passes the checks."
                ],
            },
            {
                "actor_id": "architecture-lab-learner",
                "actor_type": "person",
                "roles": ["critique", "plan"],
                "reads": ["The complete run archive and machine recommendation."],
                "writes": ["The decision record."],
                "limitations": [
                    "May authorize only one next-fidelity study in this exercise."
                ],
            },
        ],
        "feedback_budget": {
            "evaluations": len(scale_records),
            "latency": "One local SCALE-Sim process per candidate with a 120-second timeout.",
            "compute_or_tool_cost": "Local CPU execution only.",
            "human_review": "One explicit architecture decision after evidence review.",
            "fidelity": "One cheap proxy pass followed by architecture simulation.",
            "model_calls": 0,
            "energy_or_carbon": "No model inference is used by this example.",
        },
        "claims": objective_claims,
        "evidence": {
            "records": evidence_records,
            "x-arch2-labs": {"baseline_id": baseline_id},
        },
        "failed_or_rejected": failed_or_rejected,
        "gates": gates,
        "decision_rights": [
            {
                "action": "propose",
                "holder_id": "architecture-lab-learner",
                "holder_type": "person",
                "scope": "May propose one of the declared candidates.",
                "conditions": "Must preserve the frozen workload and design space.",
            },
            {
                "action": "execute",
                "holder_id": "arch2-labs-runner",
                "holder_type": "pipeline",
                "scope": "May execute the declared proxy and SCALE-Sim stages.",
                "conditions": "Commands, inputs, and outputs must remain bound in the run archive.",
            },
            {
                "action": "reject",
                "holder_id": "declared-gate-evaluator",
                "holder_type": "policy",
                "scope": "May reject candidates that fail the fixed PE-budget or deadline check.",
                "conditions": "Every rejection must cite its rejection check and evidence.",
            },
            {
                "action": "waive",
                "holder_id": "architecture-lab-learner",
                "holder_type": "person",
                "scope": "May waive only a rejection check whose recorded waiver rule permits it.",
                "conditions": "Neither rejection check in this exercise permits a waiver.",
            },
            {
                "action": "recommend",
                "holder_id": "arch2-labs-runner",
                "holder_type": "pipeline",
                "scope": "May recommend the lowest-latency candidate that passed the declared checks.",
                "conditions": "The recommendation carries no commitment authority.",
            },
            {
                "action": "commit",
                "holder_id": "architecture-lab-learner",
                "holder_type": "person",
                "scope": "May authorize one next-fidelity architecture study.",
                "conditions": "No RTL, signoff, tapeout, or product commitment follows.",
            },
        ],
        "recommendation": {
            "recommender_id": "arch2-labs-runner",
            "action": f"Advance {recommended['candidate_id']} to one next-fidelity architecture study.",
            "basis": "Lowest derived latency among candidates that passed both declared rejection checks.",
            "claim_refs": ["claim-gate-passing-latency"],
            "authority_limit": "The runner recommends; it cannot make the final decision.",
        },
        "accountable_decision": {
            "status": "pending",
            "holder_id": "architecture-lab-learner",
            "action": "Decide whether one candidate advances to a next-fidelity architecture study.",
            "rationale": "The machine recommendation awaits a decision from the named owner.",
            "claim_refs": ["claim-gate-passing-latency"],
            "authorized_scope": "No advancement is authorized while status is pending.",
            "reopen_conditions": [
                "The decision owner records a supported selection and rationale."
            ],
        },
        "replay": {
            "commands": replay_commands,
            "environment_binding": {
                "artifact_id": "environment-contract",
                "uri": "environment.yaml",
                "sha256": f"sha256:{sha256_file(receipt_root / 'environment.yaml')}",
            },
            "inputs": list(replay_inputs_by_uri.values()),
            "outputs": list(replay_outputs_by_uri.values()),
            "expected_status": "Every bound SCALE-Sim command exits 0 and emits the named report set.",
            "observed_status": "Every evidence-producing SCALE-Sim run exited 0 and its input and output hashes were recorded.",
            "validation_status": "bindings_verified",
            "validated_at": max(record["completed_at"] for record in successful),
            "validator": "arch2-labs run-archive generator 0.1.0",
        },
        "disclosure": {
            "data_classes": [
                "Public synthetic workload, simulator inputs, outputs, and teaching decisions."
            ],
            "redactions": [],
            "reviewer_roles": ["Course learner, instructor, and public reader."],
            "release_boundary_or_compliance_review_id": "Public course run archive with no confidential or personal workload data.",
        },
        "x-arch2-labs": {
            "lab_id": "scale_proxy_mirage",
            "receipt_id": receipt_id,
            "template_status": "replayable_evidence",
            "environment_contract": "environment.yaml",
            "recommendation_record": "recommendation.json",
        },
    }
    template["schema_version"] = "2.0"
    template["design_loop_card"] = card
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
    if candidate_ids is not None:
        for candidate_id in candidate_ids:
            require_safe_slug(candidate_id, "selected candidate ID")
    candidates = [
        c
        for c in spec.candidates
        if candidate_ids is None or c.candidate_id in candidate_ids
    ]
    selected_ids = candidate_ids or {candidate.candidate_id for candidate in candidates}
    declared_ids = {candidate.candidate_id for candidate in spec.candidates}
    unknown_ids = selected_ids - declared_ids
    if unknown_ids:
        raise ValueError(f"unknown candidate IDs: {', '.join(sorted(unknown_ids))}")
    if not candidates:
        raise ValueError("No candidates selected for the run")
    if spec.baseline_id not in selected_ids:
        raise ValueError(
            f"selected candidates must include baseline: {spec.baseline_id}"
        )

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
                "is_baseline": candidate.candidate_id == spec.baseline_id,
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
        raise RuntimeError("No candidate survived the SCALE-Sim rejection checks")
    if not negative_traces:
        raise ValueError(
            "selected candidates must include at least one candidate rejected "
            "by a declared rejection check"
        )

    recommended = min(
        accepted, key=lambda item: item["estimates"]["derived"]["latency_us"]
    )
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
        "latency_under_declared_gates": _pick(accepted, ["derived", "latency_us"]),
        "energy_under_declared_gates": _pick(accepted, ["energy", "e_total_uj"]),
        "area_efficiency_under_declared_gates": _pick(
            accepted, ["derived", "tops_per_mm2"], maximize=True
        ),
    }

    created_at = datetime.now(timezone.utc).isoformat()
    evidence_record = {
        "schema_version": "arch2-loop-evidence/v0.1",
        "created_at": created_at,
        "lab_id": spec.lab_id,
        "precision": precision,
        "baseline_id": spec.baseline_id,
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
                "supports": f"{recommended['candidate_id']} has the lowest derived latency among candidates that passed the declared checks",
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
    (out_dir / "evidence_record.json").write_text(
        json.dumps(evidence_record, indent=2, sort_keys=True) + "\n"
    )
    _write_jsonl(out_dir / "negative_traces.jsonl", negative_traces)
    recommendation = build_recommendation(
        spec.lab_id,
        spec.title,
        spec.baseline_id,
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
        out_dir,
        receipt_id,
        spec.baseline_id,
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
    """Build a run archive in staging and promote it after generation succeeds."""
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
                    "generated run archive failed validation: " + "; ".join(errors)
                )
        else:
            from arch2_labs.validators import validate_decision_draft

            validate_decision_draft(staging)
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
        "--out", required=True, type=Path, help="Output run-archive directory."
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
            "Decision YAML with a named owner. Without it, the runner emits an "
            "evidence-only draft that does not validate as a complete run archive."
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
