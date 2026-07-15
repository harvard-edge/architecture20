from __future__ import annotations

import argparse
import json
import math
import platform
import re
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

from jsonschema import Draft202012Validator

from arch2_labs.receipts import sha256_file
from arch2_labs.scale_env import example_dir, load_workload, run_scalesim
from arch2_labs.schemas import Candidate, WorkloadLayer

STUDY_ID = "arch2_scale_ai_study_v1"
EXAMPLE_NAME = "ai_systolic_array_study"
MODEL_SCHEMA_VERSION = "arch2-ai-proposal/v1"
RESULT_SCHEMA_VERSION = "arch2-ai-study-results/v1"
MANIFEST_SCHEMA_VERSION = "arch2-ai-study-reference/v1"
DIMENSIONS = (8, 16, 32, 64, 128)
BASELINE_SHAPE = (32, 32)
AREA_BUDGET_PES = 1024
DEADLINE_CYCLES = 90000
SCORE_MARGIN_PCT = 1.0
PREDICTION_PATTERN = re.compile(
    r"\b(16x64|64x16)\s+should\s+outperform\s+(16x64|64x16)\b",
    re.IGNORECASE,
)
RETAINED_SCALE_REPORTS = {
    "BANDWIDTH_REPORT.csv",
    "COMPUTE_REPORT.csv",
    "DETAILED_ACCESS_REPORT.csv",
    "RUN_CONFIG.csv",
}


class ProposalValidationError(ValueError):
    pass


@dataclass(frozen=True)
class EvaluationSpec:
    evaluation_id: str
    arm: str
    workload_id: str
    topology: Path
    candidate: Candidate


def study_example_dir() -> Path:
    return example_dir(EXAMPLE_NAME)


def _read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ProposalValidationError(f"could not parse {path}: {exc}") from exc


def _schema_errors(payload: Any, schema: Mapping[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema)
    errors: list[str] = []
    for error in sorted(
        validator.iter_errors(payload), key=lambda item: list(item.path)
    ):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{location}: {error.message}")
    return errors


def _prediction_winner(text: Any) -> str | None:
    if not isinstance(text, str):
        return None
    match = PREDICTION_PATTERN.search(text)
    if match is None or match.group(1).lower() == match.group(2).lower():
        return None
    return match.group(1).lower()


def model_payload_errors(payload: Any, schema: Mapping[str, Any]) -> list[str]:
    errors = _schema_errors(payload, schema)
    if not isinstance(payload, Mapping):
        return errors

    candidates = payload.get("candidates")
    if isinstance(candidates, list):
        identifiers: list[str] = []
        shapes: list[tuple[int, int]] = []
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, Mapping):
                continue
            candidate_id = candidate.get("candidate_id")
            if isinstance(candidate_id, str):
                identifiers.append(candidate_id)
            rows = candidate.get("array_rows")
            cols = candidate.get("array_cols")
            if (
                isinstance(rows, int)
                and not isinstance(rows, bool)
                and isinstance(cols, int)
                and not isinstance(cols, bool)
            ):
                shape = (rows, cols)
                shapes.append(shape)
                if rows not in DIMENSIONS or cols not in DIMENSIONS:
                    errors.append(
                        f"candidates.{index}: dimensions must use the declared set"
                    )
                if rows * cols > AREA_BUDGET_PES:
                    errors.append(
                        f"candidates.{index}: shape {rows}x{cols} exceeds 1024 PEs"
                    )
                if shape == BASELINE_SHAPE:
                    errors.append(
                        f"candidates.{index}: 32x32 is inserted as the baseline"
                    )
        if len(identifiers) != len(set(identifiers)):
            errors.append("candidate identifiers must be unique")
        if len(shapes) != len(set(shapes)):
            errors.append("candidate shapes must be unique")

    test = payload.get("discriminating_test")
    if isinstance(test, Mapping):
        original = _prediction_winner(test.get("original_workload_prediction"))
        transposed = _prediction_winner(test.get("transposed_workload_prediction"))
        if original is None:
            errors.append(
                "discriminating_test.original_workload_prediction must state "
                "which mirrored shape should outperform the other"
            )
        if transposed is None:
            errors.append(
                "discriminating_test.transposed_workload_prediction must state "
                "which mirrored shape should outperform the other"
            )
        if original is not None and transposed is not None and original == transposed:
            errors.append("the transposed-workload prediction must reverse direction")
    return sorted(set(errors))


def select_recorded_model_payload(root: Path) -> tuple[dict[str, Any], str, bool]:
    schema = _read_json(root / "context" / "model_output.schema.json")
    if not isinstance(schema, Mapping):
        raise ProposalValidationError("model output schema must be an object")

    original_path = root / "recorded" / "model" / "original_response.json"
    original = _read_json(original_path)
    initial_errors = model_payload_errors(original, schema)
    if not initial_errors:
        assert isinstance(original, dict)
        return original, original_path.relative_to(root).as_posix(), False

    repair_path = root / "recorded" / "model" / "repair_response.json"
    if not repair_path.is_file():
        raise ProposalValidationError(
            "initial response invalid and repair exhausted: "
            + "; ".join(initial_errors)
        )
    repair = _read_json(repair_path)
    repair_errors = model_payload_errors(repair, schema)
    if repair_errors:
        raise ProposalValidationError(
            "repair response invalid and repair exhausted: " + "; ".join(repair_errors)
        )
    assert isinstance(repair, dict)
    return repair, repair_path.relative_to(root).as_posix(), True


def legal_shapes() -> list[tuple[int, int]]:
    return [
        (rows, cols)
        for rows in DIMENSIONS
        for cols in DIMENSIONS
        if rows * cols <= AREA_BUDGET_PES
    ]


def conventional_shapes(layers: Iterable[WorkloadLayer]) -> list[tuple[int, int]]:
    layer_list = list(layers)
    target_ratio = sum(layer.n for layer in layer_list) / sum(
        layer.m for layer in layer_list
    )

    def key(shape: tuple[int, int]) -> tuple[float, float, int, int]:
        rows, cols = shape
        return (
            -(rows * cols),
            abs(math.log2((cols / rows) / target_ratio)),
            rows,
            cols,
        )

    ranked = sorted(
        (shape for shape in legal_shapes() if shape != BASELINE_SHAPE), key=key
    )
    selected = ranked[:3]
    frozen = [(16, 64), (8, 128), (64, 16)]
    if selected != frozen:
        raise ValueError(
            f"conventional heuristic drifted from preregistration: {selected}"
        )
    return selected


def _candidate(candidate_id: str, source: str, rows: int, cols: int) -> Candidate:
    return Candidate(
        candidate_id=candidate_id,
        label=f"{rows}x{cols} systolic array",
        source=source,
        array_rows=rows,
        array_cols=cols,
        dataflow="ws",
        sram_kb=128,
        dram_bandwidth_words_per_cycle=64,
        clock_mhz=800,
        area_budget_pes=AREA_BUDGET_PES,
        deadline_cycles=DEADLINE_CYCLES,
        min_layer_util_pct=1.0,
    )


def evaluation_specs(root: Path, payload: Mapping[str, Any]) -> list[EvaluationSpec]:
    workload = root / "workloads" / "xr_slice_gemm.csv"
    transposed = root / "workloads" / "xr_slice_gemm_transposed.csv"
    layers = load_workload(workload)
    specs: list[EvaluationSpec] = []

    specs.append(
        EvaluationSpec(
            "model_baseline_32x32",
            "model",
            "original",
            workload,
            _candidate(
                "model_baseline_32x32", "mandatory baseline in model arm", 32, 32
            ),
        )
    )
    for entry in payload["candidates"]:
        candidate_id = entry["candidate_id"]
        specs.append(
            EvaluationSpec(
                candidate_id,
                "model",
                "original",
                workload,
                _candidate(
                    candidate_id,
                    "recorded model proposal",
                    entry["array_rows"],
                    entry["array_cols"],
                ),
            )
        )

    specs.append(
        EvaluationSpec(
            "conventional_baseline_32x32",
            "conventional",
            "original",
            workload,
            _candidate(
                "conventional_baseline_32x32",
                "mandatory baseline in conventional arm",
                32,
                32,
            ),
        )
    )
    for rows, cols in conventional_shapes(layers):
        candidate_id = f"heuristic_{rows}x{cols}"
        specs.append(
            EvaluationSpec(
                candidate_id,
                "conventional",
                "original",
                workload,
                _candidate(
                    candidate_id,
                    "preregistered aggregate-aspect-ratio heuristic",
                    rows,
                    cols,
                ),
            )
        )

    for workload_id, topology in (("original", workload), ("transposed", transposed)):
        for rows, cols in ((16, 64), (64, 16)):
            candidate_id = f"probe_{workload_id}_{rows}x{cols}"
            specs.append(
                EvaluationSpec(
                    candidate_id,
                    "mechanism_probe",
                    workload_id,
                    topology,
                    _candidate(
                        candidate_id,
                        "preregistered shared mirrored-shape mechanism probe",
                        rows,
                        cols,
                    ),
                )
            )
    return specs


def _relative_path(path_value: Any, output_root: Path) -> str:
    path = Path(str(path_value)).resolve()
    try:
        return path.relative_to(output_root.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"simulator path escapes study output: {path}") from exc


def _score(metrics: Mapping[str, Any]) -> float:
    utilization = float(metrics["avg_layer_util_pct"])
    if utilization <= 0:
        raise ValueError("average layer utilization must be positive")
    return float(metrics["total_cycles"]) / (utilization / 100.0)


def _retain_summary_reports(record: dict[str, Any]) -> dict[str, Any]:
    """Keep raw summary reports and discard reproducible per-access traces.

    SCALE-Sim emits large intermediate layer traces in addition to the four CSV
    reports that support this study's parsed metrics. Offline replay regenerates
    those intermediates; the release fixture retains the exact inputs and raw
    summary reports instead of adding hundreds of megabytes to the repository.
    """
    outputs = record.get("outputs")
    raw_files = outputs.get("raw_files") if isinstance(outputs, dict) else None
    if not isinstance(raw_files, list):
        raise ValueError("successful SCALE-Sim run declares no raw files")
    retained: list[dict[str, Any]] = []
    report_dir = Path(outputs["report_dir"])
    for item in raw_files:
        path = Path(item["path"])
        if path.name in RETAINED_SCALE_REPORTS:
            retained.append(item)
        else:
            path.unlink()
    for path in sorted(
        (item for item in report_dir.rglob("*") if item.is_dir()),
        key=lambda item: len(item.parts),
        reverse=True,
    ):
        try:
            path.rmdir()
        except OSError:
            pass
    retained_names = {Path(item["path"]).name for item in retained}
    required = RETAINED_SCALE_REPORTS - {"RUN_CONFIG.csv"}
    missing = required - retained_names
    if missing:
        raise ValueError(
            "SCALE-Sim run is missing required summary reports: "
            + ", ".join(sorted(missing))
        )
    outputs["raw_files"] = retained
    return record


def evaluate_spec(
    spec: EvaluationSpec,
    output_root: Path,
    layout: Path,
    runner: Callable[..., dict[str, Any]] = run_scalesim,
) -> dict[str, Any]:
    run_dir = output_root / "runs" / spec.evaluation_id
    base = {
        "evaluation_id": spec.evaluation_id,
        "arm": spec.arm,
        "workload_id": spec.workload_id,
        "candidate_id": spec.candidate.candidate_id,
        "source": spec.candidate.source,
        "array_rows": spec.candidate.array_rows,
        "array_cols": spec.candidate.array_cols,
        "pe_count": spec.candidate.pe_count,
    }
    try:
        record = runner(spec.candidate, spec.topology, layout, run_dir)
    except Exception as exc:  # simulator failures are evidence, not replacements
        return {
            **base,
            "status": "failed",
            "gate_result": "simulator_failure",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    if record.get("status") != "ok":
        return {
            **base,
            "status": "failed",
            "gate_result": "simulator_failure",
            "returncode": record.get("returncode"),
            "tool": record.get("tool"),
        }

    record = _retain_summary_reports(record)

    metrics = dict(record["metrics"])
    area_pass = spec.candidate.pe_count <= AREA_BUDGET_PES
    deadline_pass = float(metrics["total_cycles"]) <= DEADLINE_CYCLES
    gate_result = "pass" if area_pass and deadline_pass else "rejected"
    raw_files = [
        {
            "path": _relative_path(item["path"], output_root),
            "sha256": item["sha256"],
        }
        for item in record["outputs"]["raw_files"]
    ]
    inputs = {
        name: {
            "path": _relative_path(record["inputs"][name], output_root),
            "sha256": record["inputs"][f"{name}_sha256"],
        }
        for name in ("config", "topology", "layout")
    }
    return {
        **base,
        "status": "ok",
        "gate_result": gate_result,
        "gates": {
            "area_budget": {
                "criterion": "pe_count <= 1024",
                "observed": spec.candidate.pe_count,
                "passed": area_pass,
            },
            "deadline": {
                "criterion": "total_cycles <= 90000",
                "observed": metrics["total_cycles"],
                "passed": deadline_pass,
            },
        },
        "decision_score": _score(metrics),
        "metrics": metrics,
        "tool": record["tool"],
        "inputs": inputs,
        "raw_outputs": raw_files,
    }


def _best(evaluations: Iterable[dict[str, Any]]) -> dict[str, Any]:
    eligible = [
        item
        for item in evaluations
        if item.get("status") == "ok" and item.get("gate_result") == "pass"
    ]
    if not eligible:
        raise RuntimeError("no candidate passed both rejection checks")
    return min(eligible, key=lambda item: float(item["decision_score"]))


def _percent_better(reference: float, candidate: float) -> float:
    return (reference - candidate) / reference * 100.0


def _probe_winner(
    evaluations: list[dict[str, Any]], workload_id: str
) -> tuple[str | None, float]:
    rows = [
        item
        for item in evaluations
        if item["arm"] == "mechanism_probe"
        and item["workload_id"] == workload_id
        and item.get("gate_result") == "pass"
    ]
    if len(rows) != 2:
        return None, 0.0
    rows.sort(key=lambda item: float(item["decision_score"]))
    margin = _percent_better(
        float(rows[1]["decision_score"]), float(rows[0]["decision_score"])
    )
    if margin < SCORE_MARGIN_PCT:
        return None, margin
    winner = f"{rows[0]['array_rows']}x{rows[0]['array_cols']}"
    return winner, margin


def build_results(
    root: Path,
    payload: Mapping[str, Any],
    selected_response: str,
    repair_used: bool,
    evaluations: list[dict[str, Any]],
) -> dict[str, Any]:
    model_rows = [item for item in evaluations if item["arm"] == "model"]
    conventional_rows = [item for item in evaluations if item["arm"] == "conventional"]
    if len(model_rows) != 4 or len(conventional_rows) != 4:
        raise RuntimeError("proposal-arm evaluation budgets are not four and four")

    model_best = _best(model_rows)
    conventional_best = _best(conventional_rows)
    model_advantage = _percent_better(
        float(conventional_best["decision_score"]),
        float(model_best["decision_score"]),
    )
    if model_advantage >= SCORE_MARGIN_PCT:
        ai_status = "supported"
    elif model_advantage <= -SCORE_MARGIN_PCT:
        ai_status = "adverse"
    else:
        ai_status = "tie"

    baseline = next(
        item for item in model_rows if item["candidate_id"] == "model_baseline_32x32"
    )
    nonbaseline = [
        item
        for item in model_rows + conventional_rows
        if "baseline" not in item["candidate_id"] and item.get("gate_result") == "pass"
    ]
    architecture_best = _best(nonbaseline)
    architecture_improvement = _percent_better(
        float(baseline["decision_score"]),
        float(architecture_best["decision_score"]),
    )
    architecture_status = (
        "supported"
        if architecture_improvement >= SCORE_MARGIN_PCT
        else "null_at_preregistered_margin"
    )

    test = payload["discriminating_test"]
    predicted_original = _prediction_winner(test["original_workload_prediction"])
    predicted_transposed = _prediction_winner(test["transposed_workload_prediction"])
    observed_original, original_margin = _probe_winner(evaluations, "original")
    observed_transposed, transposed_margin = _probe_winner(evaluations, "transposed")
    if observed_original is None or observed_transposed is None:
        mechanism_status = "inconclusive_at_preregistered_margin"
    elif (
        observed_original == predicted_original
        and observed_transposed == predicted_transposed
        and observed_original != observed_transposed
    ):
        mechanism_status = "supported"
    else:
        mechanism_status = "falsified"

    shape_overlap = sorted(
        {
            (item["array_rows"], item["array_cols"])
            for item in model_rows
            if "baseline" not in item["candidate_id"]
        }
        & {
            (item["array_rows"], item["array_cols"])
            for item in conventional_rows
            if "baseline" not in item["candidate_id"]
        }
    )
    for arm_rows, arm_best in (
        (model_rows, model_best),
        (conventional_rows, conventional_best),
    ):
        for item in arm_rows:
            if item.get("gate_result") != "pass":
                item["disposition"] = "rejected_by_declared_gate_or_tool_failure"
            elif (
                abs(
                    _percent_better(
                        float(arm_best["decision_score"]),
                        float(item["decision_score"]),
                    )
                )
                < SCORE_MARGIN_PCT
            ):
                item["disposition"] = "tied_best_in_arm_at_preregistered_margin"
            else:
                item["disposition"] = "evaluated_and_dominated_in_arm"

    if architecture_status == "supported":
        recommendation_candidate_id = architecture_best["candidate_id"]
        recommendation_shape = [
            architecture_best["array_rows"],
            architecture_best["array_cols"],
        ]
        recommendation_action = "at_most_a_bounded_higher_fidelity_study"
        recommendation_basis = (
            "nonbaseline improvement cleared the preregistered margin"
        )
    else:
        recommendation_candidate_id = baseline["candidate_id"]
        recommendation_shape = [baseline["array_rows"], baseline["array_cols"]]
        recommendation_action = "retain_the_32x32_baseline_and_stop_this_bounded_search"
        recommendation_basis = (
            "no nonbaseline candidate cleared the preregistered margin"
        )

    return {
        "schema_version": RESULT_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "evidence_status": "computed_by_scale_sim_not_measured_silicon",
        "storage_policy": {
            "retained": "exact inputs and raw SCALE-Sim summary CSV reports",
            "regenerated_on_replay": "per-layer access traces",
            "reason": "intermediate traces are deterministic and not needed to support the published metrics",
        },
        "freeze": {
            "preregistration": "context/pre_registration.yaml",
            "workload_sha256": sha256_file(root / "workloads" / "xr_slice_gemm.csv"),
            "transposed_workload_sha256": sha256_file(
                root / "workloads" / "xr_slice_gemm_transposed.csv"
            ),
            "layout_sha256": sha256_file(root / "layouts" / "default_layout.csv"),
        },
        "model_interaction": {
            "selected_response": selected_response,
            "repair_used": repair_used,
            "provenance": "recorded/model/provenance.json",
        },
        "budgets": {
            "model_arm_scalesim_evaluations": len(model_rows),
            "conventional_arm_scalesim_evaluations": len(conventional_rows),
            "shared_mechanism_probe_evaluations": len(
                [item for item in evaluations if item["arm"] == "mechanism_probe"]
            ),
        },
        "architecture_outcome_claim": {
            "status": architecture_status,
            "baseline_candidate_id": baseline["candidate_id"],
            "baseline_score": baseline["decision_score"],
            "best_candidate_id": architecture_best["candidate_id"],
            "best_shape": [
                architecture_best["array_rows"],
                architecture_best["array_cols"],
            ],
            "best_score": architecture_best["decision_score"],
            "improvement_pct": architecture_improvement,
            "scope": "frozen three-layer GEMM slice and SCALE-Sim configuration only",
        },
        "ai_contribution_claim": {
            "status": ai_status,
            "model_best_candidate_id": model_best["candidate_id"],
            "model_best_shape": [model_best["array_rows"], model_best["array_cols"]],
            "model_best_score": model_best["decision_score"],
            "conventional_best_candidate_id": conventional_best["candidate_id"],
            "conventional_best_shape": [
                conventional_best["array_rows"],
                conventional_best["array_cols"],
            ],
            "conventional_best_score": conventional_best["decision_score"],
            "model_advantage_pct": model_advantage,
            "nonbaseline_shape_overlap": [list(shape) for shape in shape_overlap],
            "scope": "one recorded call and one fixed heuristic at four evaluations per arm",
        },
        "mechanism_claim": {
            "status": mechanism_status,
            "predicted_original_winner": predicted_original,
            "observed_original_winner": observed_original,
            "original_margin_pct": original_margin,
            "predicted_transposed_winner": predicted_transposed,
            "observed_transposed_winner": observed_transposed,
            "transposed_margin_pct": transposed_margin,
            "falsifier": test["falsifier"],
        },
        "recommendation": {
            "candidate_id": recommendation_candidate_id,
            "shape": recommendation_shape,
            "recommended_next_action": recommendation_action,
            "basis": recommendation_basis,
            "not_authorized": ["RTL implementation", "tapeout", "product decision"],
            "accountable_decision_status": "awaiting_author_confirmation",
        },
        "evaluations": evaluations,
    }


def _package_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not-installed"


def _write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def _write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows))


def _manifest_entries(output_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(output_root.rglob("*")):
        if not path.is_file() or path.name == "reference_manifest.json":
            continue
        relative = path.relative_to(output_root).as_posix()
        entries.append(
            {
                "path": relative,
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "replay_stable": relative != "execution_provenance.json",
            }
        )
    return entries


def write_reference_manifest(output_root: Path) -> dict[str, Any]:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "study_id": STUDY_ID,
        "files": _manifest_entries(output_root),
    }
    _write_json(output_root / "reference_manifest.json", manifest)
    return manifest


def reference_errors(reference_root: Path) -> list[str]:
    manifest_path = reference_root / "reference_manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        return [f"could not parse reference manifest: {exc}"]
    errors: list[str] = []
    if manifest.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        errors.append("reference manifest schema version is unsupported")
    if manifest.get("study_id") != STUDY_ID:
        errors.append("reference manifest study ID does not match")
    files = manifest.get("files")
    if not isinstance(files, list):
        return errors + ["reference manifest files must be a list"]
    declared: set[str] = set()
    for entry in files:
        if not isinstance(entry, Mapping) or not isinstance(entry.get("path"), str):
            errors.append("reference manifest contains a malformed file entry")
            continue
        relative = entry["path"]
        if relative in declared:
            errors.append(f"reference manifest duplicates {relative}")
            continue
        declared.add(relative)
        path = reference_root / relative
        try:
            path.resolve().relative_to(reference_root.resolve())
        except ValueError:
            errors.append(f"reference manifest path escapes root: {relative}")
            continue
        if not path.is_file():
            errors.append(f"reference file is missing: {relative}")
            continue
        if entry.get("sha256") != sha256_file(path):
            errors.append(f"reference sha256 mismatch: {relative}")
        if entry.get("size_bytes") != path.stat().st_size:
            errors.append(f"reference size mismatch: {relative}")
    actual = {
        path.relative_to(reference_root).as_posix()
        for path in reference_root.rglob("*")
        if path.is_file() and path.name != "reference_manifest.json"
    }
    for relative in sorted(actual - declared):
        errors.append(f"undeclared reference file: {relative}")
    return errors


def run_study(
    root: Path,
    output_root: Path,
    runner: Callable[..., dict[str, Any]] = run_scalesim,
) -> dict[str, Any]:
    if output_root.exists():
        raise FileExistsError(f"study output already exists: {output_root}")
    output_root.mkdir(parents=True)
    started = datetime.now(timezone.utc)
    monotonic_start = time.monotonic()
    payload, selected_response, repair_used = select_recorded_model_payload(root)
    layout = root / "layouts" / "default_layout.csv"
    specs = evaluation_specs(root, payload)
    evaluations = [
        evaluate_spec(spec, output_root, layout, runner=runner) for spec in specs
    ]
    results = build_results(root, payload, selected_response, repair_used, evaluations)
    _write_json(output_root / "study_results.json", results)
    _write_jsonl(output_root / "evaluations.jsonl", evaluations)
    completed = datetime.now(timezone.utc)
    provenance = {
        "schema_version": "arch2-study-execution/v1",
        "study_id": STUDY_ID,
        "started_at_utc": started.isoformat(),
        "completed_at_utc": completed.isoformat(),
        "wall_time_seconds": time.monotonic() - monotonic_start,
        "runtime": {
            "python": platform.python_version(),
            "executable": sys.executable,
            "platform": platform.platform(),
            "scalesim": _package_version("scalesim"),
            "arch2_labs": _package_version("arch2-labs"),
        },
        "evaluation_count": len(evaluations),
        "failure_count": len(
            [item for item in evaluations if item.get("status") != "ok"]
        ),
    }
    _write_json(output_root / "execution_provenance.json", provenance)
    write_reference_manifest(output_root)
    return results


def replay_reference(root: Path, reference_root: Path) -> list[str]:
    integrity_errors = reference_errors(reference_root)
    if integrity_errors:
        return integrity_errors
    expected = json.loads((reference_root / "reference_manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="arch2-study-replay-") as temp:
        replay_root = Path(temp) / "reference"
        run_study(root, replay_root)
        actual = json.loads((replay_root / "reference_manifest.json").read_text())
        expected_stable = {
            entry["path"]: entry["sha256"]
            for entry in expected["files"]
            if entry.get("replay_stable")
        }
        actual_stable = {
            entry["path"]: entry["sha256"]
            for entry in actual["files"]
            if entry.get("replay_stable")
        }
        errors: list[str] = []
        for relative in sorted(expected_stable.keys() - actual_stable.keys()):
            errors.append(f"replay is missing stable file: {relative}")
        for relative in sorted(actual_stable.keys() - expected_stable.keys()):
            errors.append(f"replay produced unexpected stable file: {relative}")
        for relative in sorted(expected_stable.keys() & actual_stable.keys()):
            if expected_stable[relative] != actual_stable[relative]:
                errors.append(f"replay sha256 mismatch: {relative}")
        return errors


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run and verify the recorded Architecture 2.0 SCALE-Sim study."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-model")
    record = subparsers.add_parser("record")
    record.add_argument("--out", type=Path, required=True)
    verify = subparsers.add_parser("verify-reference")
    verify.add_argument("--reference", type=Path, required=True)
    replay = subparsers.add_parser("replay")
    replay.add_argument("--reference", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    root = study_example_dir()
    if args.command == "validate-model":
        payload, path, repair_used = select_recorded_model_payload(root)
        print(
            json.dumps(
                {
                    "status": "valid",
                    "selected_response": path,
                    "repair_used": repair_used,
                    "candidate_count": len(payload["candidates"]),
                },
                sort_keys=True,
            )
        )
        return 0
    if args.command == "record":
        results = run_study(root, args.out)
        print(
            json.dumps(
                {
                    "status": "recorded",
                    "architecture_outcome": results["architecture_outcome_claim"][
                        "status"
                    ],
                    "ai_contribution": results["ai_contribution_claim"]["status"],
                    "mechanism": results["mechanism_claim"]["status"],
                },
                sort_keys=True,
            )
        )
        return 0
    if args.command == "verify-reference":
        errors = reference_errors(args.reference)
    else:
        errors = replay_reference(root, args.reference)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(
        "reference is valid" if args.command == "verify-reference" else "replay matches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
