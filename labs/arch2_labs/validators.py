from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from arch2_labs.decisions import decision_errors, parse_human_decision, render_decision
from arch2_labs.receipts import (
    MANIFEST_FILENAME,
    MARKER_FILENAME,
    sha256_file,
    verify_receipt_ownership,
)

LABS_ROOT = Path(__file__).resolve().parents[1]
CARD_SCHEMA_SOURCE = LABS_ROOT.parent / "schemas" / "design-loop-card.v1.schema.json"

REQUIRED_FILES = [
    MARKER_FILENAME,
    MANIFEST_FILENAME,
    "card.yaml",
    "environment.yaml",
    "candidates.jsonl",
    "runs.jsonl",
    "evidence_ledger.json",
    "negative_traces.jsonl",
    "recommendation.json",
    "decision.yaml",
    "decision.md",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row") from exc
            if not isinstance(row, dict):
                raise ValueError(f"{path}:{line_number}: JSONL row must be an object")
            rows.append(row)
    return rows


def _load_yaml(path: Path, errors: list[str]) -> Any:
    try:
        return yaml.safe_load(path.read_text())
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"could not parse {path.name}: {exc}")
        return None


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"could not parse {path.name}: {exc}")
        return None


def _load_jsonl(path: Path, errors: list[str]) -> list[dict[str, Any]]:
    try:
        return read_jsonl(path)
    except (OSError, ValueError) as exc:
        errors.append(str(exc))
        return []


def _safe_payload_path(receipt_dir: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative:
        return None
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        return None
    path = receipt_dir.joinpath(*pure.parts)
    try:
        path.resolve().relative_to(receipt_dir.resolve())
    except ValueError:
        return None
    return path


def _manifest_errors(receipt_dir: Path, manifest: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        errors.append("manifest missing runtime versions")
        runtime = {}
    python_runtime = runtime.get("python")
    for field in ("version", "implementation", "executable"):
        if not isinstance(python_runtime, dict) or not python_runtime.get(field):
            errors.append(f"manifest runtime missing Python field: {field}")
    if not runtime.get("platform"):
        errors.append("manifest runtime missing platform")
    tools = runtime.get("tools")
    for tool in ("arch2-labs", "numpy", "PyYAML", "SCALE-Sim"):
        if not isinstance(tools, dict) or not tools.get(tool):
            errors.append(f"manifest runtime missing tool version: {tool}")

    entries = manifest.get("files")
    if not isinstance(entries, list):
        return errors + ["manifest files must be a list"]
    declared: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"manifest file entry {index} must be an object")
            continue
        relative = entry.get("path")
        path = _safe_payload_path(receipt_dir, relative)
        if path is None:
            errors.append(f"manifest contains unsafe payload path: {relative}")
            continue
        if relative in declared:
            errors.append(f"manifest declares payload more than once: {relative}")
            continue
        declared.add(relative)
        if path.is_symlink():
            errors.append(f"manifest payload is a symbolic link: {relative}")
            continue
        if not path.is_file():
            errors.append(f"manifest payload is missing: {relative}")
            continue
        if entry.get("sha256") != sha256_file(path):
            errors.append(f"manifest payload {relative} sha256 mismatch")
        if entry.get("size_bytes") != path.stat().st_size:
            errors.append(f"manifest payload {relative} size mismatch")

    actual: set[str] = set()
    for path in receipt_dir.rglob("*"):
        relative = path.relative_to(receipt_dir).as_posix()
        if path.is_symlink():
            errors.append(f"receipt contains a symbolic link: {relative}")
        elif path.is_file() and relative not in {MARKER_FILENAME, MANIFEST_FILENAME}:
            actual.add(relative)
    for relative in sorted(actual - declared):
        errors.append(f"payload file is not declared in manifest: {relative}")
    for relative in sorted(declared - actual):
        errors.append(f"manifest payload is not a regular file: {relative}")
    return errors


def _card_schema() -> dict[str, Any]:
    if CARD_SCHEMA_SOURCE.is_file():
        return json.loads(CARD_SCHEMA_SOURCE.read_text())
    resource = files("arch2_labs").joinpath(
        "resources", "design-loop-card.v1.schema.json"
    )
    return json.loads(resource.read_text())


def _card_errors(card: Any) -> list[str]:
    validator = Draft202012Validator(_card_schema(), format_checker=FormatChecker())
    messages = []
    for error in sorted(validator.iter_errors(card), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"card.yaml {location}: {error.message}")
    return messages


def _validate_run_files(
    receipt_dir: Path,
    runs: list[dict[str, Any]],
    declared_manifest_files: set[str],
) -> list[str]:
    errors: list[str] = []
    required_reports = {
        "COMPUTE_REPORT.csv",
        "BANDWIDTH_REPORT.csv",
        "DETAILED_ACCESS_REPORT.csv",
    }
    for run in runs:
        if run.get("stage") != "scalesim" or run.get("status") != "ok":
            continue
        candidate_id = run.get("candidate_id", "<missing>")
        tool = run.get("tool")
        if (
            not isinstance(tool, dict)
            or tool.get("name") != "SCALE-Sim"
            or not tool.get("version")
        ):
            errors.append(
                f"SCALE-Sim run {candidate_id} lacks an explicit tool version"
            )
        runtime = run.get("runtime")
        if not isinstance(runtime, dict) or not runtime.get("python"):
            errors.append(
                f"SCALE-Sim run {candidate_id} lacks an explicit Python runtime"
            )

        inputs = run.get("inputs")
        if not isinstance(inputs, dict):
            errors.append(f"SCALE-Sim run {candidate_id} has no input provenance")
            inputs = {}
        for name in ("config", "topology", "layout"):
            relative = inputs.get(name)
            path = _safe_payload_path(receipt_dir, relative)
            if path is None or not path.is_file():
                errors.append(f"SCALE-Sim run {candidate_id} input is missing: {name}")
                continue
            if inputs.get(f"{name}_sha256") != sha256_file(path):
                errors.append(
                    f"SCALE-Sim run {candidate_id} input sha256 mismatch: {name}"
                )
            if relative not in declared_manifest_files:
                errors.append(
                    f"SCALE-Sim run {candidate_id} input is absent from the manifest: {relative}"
                )

        outputs = run.get("outputs")
        raw_files = outputs.get("raw_files") if isinstance(outputs, dict) else None
        if not isinstance(raw_files, list) or not raw_files:
            errors.append(f"SCALE-Sim run {candidate_id} declares no raw output files")
            continue
        declared_reports: set[str] = set()
        declared_raw_paths: set[str] = set()
        for raw in raw_files:
            if not isinstance(raw, dict):
                errors.append(f"SCALE-Sim run {candidate_id} has malformed raw output")
                continue
            relative = raw.get("path")
            path = _safe_payload_path(receipt_dir, relative)
            if path is None or not path.is_file():
                errors.append(
                    f"SCALE-Sim run {candidate_id} raw output is missing: {relative}"
                )
                continue
            declared_reports.add(path.name)
            declared_raw_paths.add(relative)
            if raw.get("sha256") != sha256_file(path):
                errors.append(
                    f"SCALE-Sim run {candidate_id} raw output sha256 mismatch: {relative}"
                )
            if relative not in declared_manifest_files:
                errors.append(
                    f"SCALE-Sim run {candidate_id} raw output is absent from the manifest: {relative}"
                )
        missing_reports = required_reports - declared_reports
        for report in sorted(missing_reports):
            errors.append(
                f"SCALE-Sim run {candidate_id} is missing required raw report: {report}"
            )
        report_dir = _safe_payload_path(receipt_dir, outputs.get("report_dir"))
        if report_dir is None or not report_dir.is_dir():
            errors.append(
                f"SCALE-Sim run {candidate_id} report directory is missing or unsafe"
            )
        else:
            actual_raw_paths = {
                path.relative_to(receipt_dir).as_posix()
                for path in report_dir.rglob("*")
                if path.is_file() and not path.is_symlink()
            }
            for relative in sorted(actual_raw_paths - declared_raw_paths):
                errors.append(
                    f"SCALE-Sim run {candidate_id} raw output is not declared by the run: {relative}"
                )
    return errors


def validate_receipt(receipt_dir: Path) -> list[str]:
    errors: list[str] = []
    receipt_dir = receipt_dir.expanduser().absolute()
    if receipt_dir.is_symlink():
        return [f"receipt directory must not be a symbolic link: {receipt_dir}"]
    if not receipt_dir.is_dir():
        return [f"receipt directory does not exist: {receipt_dir}"]

    for name in REQUIRED_FILES:
        if not (receipt_dir / name).is_file():
            errors.append(f"missing required file: {name}")

    manifest: dict[str, Any] = {}
    if (receipt_dir / MARKER_FILENAME).is_file() and (
        receipt_dir / MANIFEST_FILENAME
    ).is_file():
        try:
            manifest = verify_receipt_ownership(receipt_dir)
        except ValueError as exc:
            errors.append(str(exc))
            loaded = _load_yaml(receipt_dir / MANIFEST_FILENAME, errors)
            if isinstance(loaded, dict):
                manifest = loaded
        if manifest:
            errors.extend(_manifest_errors(receipt_dir, manifest))
    if manifest.get("status") != "complete":
        errors.append("receipt awaits a required human decision")

    def present(name: str) -> bool:
        return (receipt_dir / name).is_file()

    card = _load_yaml(receipt_dir / "card.yaml", errors) if present("card.yaml") else {}
    environment = (
        _load_yaml(receipt_dir / "environment.yaml", errors)
        if present("environment.yaml")
        else {}
    )
    candidates = (
        _load_jsonl(receipt_dir / "candidates.jsonl", errors)
        if present("candidates.jsonl")
        else []
    )
    runs = (
        _load_jsonl(receipt_dir / "runs.jsonl", errors) if present("runs.jsonl") else []
    )
    negative_traces = (
        _load_jsonl(receipt_dir / "negative_traces.jsonl", errors)
        if present("negative_traces.jsonl")
        else []
    )
    evidence = (
        _load_json(receipt_dir / "evidence_ledger.json", errors)
        if present("evidence_ledger.json")
        else {}
    )
    recommendation = (
        _load_json(receipt_dir / "recommendation.json", errors)
        if present("recommendation.json")
        else {}
    )
    decision = (
        _load_yaml(receipt_dir / "decision.yaml", errors)
        if present("decision.yaml")
        else {}
    )

    if isinstance(card, dict):
        errors.extend(_card_errors(card))
    else:
        errors.append("card.yaml must contain a mapping")
    lab_card = card.get("design_loop_card", {}) if isinstance(card, dict) else {}
    card_extension = (
        lab_card.get("x-arch2-labs", {}) if isinstance(lab_card, dict) else {}
    )
    if isinstance(card_extension, dict) and manifest:
        if card_extension.get("receipt_id") != manifest.get("receipt_id"):
            errors.append("card receipt_id does not match the manifest")
    lab_ids = {
        "manifest": manifest.get("lab_id"),
        "card": card_extension.get("lab_id")
        if isinstance(card_extension, dict)
        else None,
        "environment": environment.get("lab_id")
        if isinstance(environment, dict)
        else None,
        "evidence": evidence.get("lab_id") if isinstance(evidence, dict) else None,
        "recommendation": recommendation.get("lab_id")
        if isinstance(recommendation, dict)
        else None,
    }
    nonempty_lab_ids = {value for value in lab_ids.values() if value}
    if len(nonempty_lab_ids) != 1:
        errors.append(f"lab_id mismatch across receipt records: {lab_ids}")

    if isinstance(environment, dict):
        for field in (
            "legal_actions",
            "invalid_actions",
            "observations",
            "rejection_authority",
        ):
            if not environment.get(field):
                errors.append(f"environment.yaml missing field: {field}")

    candidate_ids = [record.get("candidate_id") for record in candidates]
    declared_ids = {candidate_id for candidate_id in candidate_ids if candidate_id}
    if not candidates:
        errors.append("candidates.jsonl has no candidates")
    if len(declared_ids) != len(candidate_ids):
        errors.append("candidates.jsonl contains missing or duplicate candidate IDs")

    run_stages: dict[str, set[str]] = {
        candidate_id: set() for candidate_id in declared_ids
    }
    for run in runs:
        candidate_id = run.get("candidate_id")
        if candidate_id not in declared_ids:
            errors.append(f"run references an undeclared candidate: {candidate_id}")
            continue
        run_stages[candidate_id].add(str(run.get("stage")))
    for candidate_id, stages in run_stages.items():
        for stage in ("proxy", "scalesim"):
            if stage not in stages:
                errors.append(f"candidate {candidate_id} has no {stage} run")

    if not negative_traces:
        errors.append("negative_traces.jsonl is empty")
    rejected_ids: set[str] = set()
    for trace in negative_traces:
        candidate_id = trace.get("candidate_id")
        rejected_ids.add(candidate_id)
        if candidate_id not in declared_ids:
            errors.append(
                f"negative trace references an undeclared candidate: {candidate_id}"
            )
        for field in ("stage", "gate", "reason"):
            if not trace.get(field):
                errors.append(f"negative trace {candidate_id} missing field: {field}")
    card_negative_ids = {
        trace.get("candidate_id")
        for trace in lab_card.get("negative_traces", [])
        if isinstance(trace, dict)
    }
    if card_negative_ids != rejected_ids:
        errors.append("card negative-trace IDs do not match negative_traces.jsonl")

    if isinstance(evidence, dict):
        stages = {stage.get("stage") for stage in evidence.get("stages", [])}
        for stage in ("proxy", "scalesim"):
            if stage not in stages:
                errors.append(f"evidence_ledger.json has no {stage} evidence stage")
        if evidence.get("recommendation_evidence_source") != "scalesim":
            errors.append(
                "machine recommendation must cite SCALE-Sim as its evidence source"
            )
        outcome_ids = {
            outcome.get("candidate_id")
            for outcome in evidence.get("candidate_outcomes", [])
            if isinstance(outcome, dict)
        }
        if not outcome_ids.issubset(declared_ids):
            errors.append("evidence ledger contains an undeclared candidate outcome")
        for field in ("machine_recommendation", "proxy_winner"):
            candidate_id = evidence.get(field)
            if candidate_id not in declared_ids:
                errors.append(
                    f"evidence ledger {field} is not a declared candidate: {candidate_id}"
                )
        if evidence.get("rejected_count") != len(negative_traces):
            errors.append(
                "evidence ledger rejected_count does not match negative traces"
            )

    recommended_id = (
        recommendation.get("candidate_id") if isinstance(recommendation, dict) else None
    )
    if recommended_id not in declared_ids:
        errors.append(
            f"recommendation references an undeclared candidate: {recommended_id}"
        )
    if recommended_id in rejected_ids:
        errors.append(f"recommendation selects a rejected candidate: {recommended_id}")
    if isinstance(recommendation, dict):
        if recommendation.get("human_decision") is not False:
            errors.append("recommendation must state that it is not a human decision")
        if recommendation.get("commitment") != "none":
            errors.append("machine recommendation must not claim commitment authority")
        if evidence and recommendation.get("candidate_id") != evidence.get(
            "machine_recommendation"
        ):
            errors.append("recommendation candidate does not match the evidence ledger")
        if evidence and recommendation.get("proxy_winner") != evidence.get(
            "proxy_winner"
        ):
            errors.append(
                "recommendation proxy winner does not match the evidence ledger"
            )

    declared_manifest_files = {
        entry.get("path")
        for entry in manifest.get("files", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    errors.extend(_validate_run_files(receipt_dir, runs, declared_manifest_files))

    if decision:
        errors.extend(decision_errors(decision))
        if isinstance(decision, dict):
            selected_id = decision.get("selected_candidate_id")
            if decision.get("lab_id") not in nonempty_lab_ids:
                errors.append("decision lab_id does not match the receipt")
            if selected_id not in declared_ids:
                errors.append(
                    "decision selected_candidate_id is not a declared candidate: "
                    f"{selected_id}"
                )
            if selected_id in rejected_ids:
                errors.append(f"decision selects a rejected candidate: {selected_id}")
            try:
                parsed_decision = parse_human_decision(decision)
            except ValueError:
                parsed_decision = None
            if parsed_decision and present("decision.md"):
                if (receipt_dir / "decision.md").read_text() != render_decision(
                    parsed_decision
                ):
                    errors.append(
                        "decision.md does not match the explicit decision.yaml"
                    )

    if manifest.get("status") == "complete":
        if lab_card.get("conformance_level") != 3:
            errors.append("complete receipt card must have conformance_level 3")
        if isinstance(card_extension, dict):
            learner = card_extension.get("learner_decision", {})
            for field in ("governing_objective", "selected_candidate_id", "rationale"):
                if not isinstance(learner, dict) or not learner.get(field):
                    errors.append(f"card learner decision missing field: {field}")
            if isinstance(decision, dict) and isinstance(learner, dict):
                field_map = {
                    "governing_objective": "governing_objective",
                    "selected_candidate_id": "selected_candidate_id",
                    "rationale": "rationale",
                    "residual_risk": "residual_risk",
                }
                for learner_field, decision_field in field_map.items():
                    if learner.get(learner_field) != decision.get(decision_field):
                        errors.append(
                            f"card learner decision does not match decision.yaml: {learner_field}"
                        )
        card_human = lab_card.get("human_decision", {})
        if isinstance(decision, dict):
            if not isinstance(card_human, dict) or card_human.get(
                "owner"
            ) != decision.get("human_owner"):
                errors.append("card human decision owner does not match decision.yaml")
            card_boundary = lab_card.get("commitment_boundary", {})
            if not isinstance(card_boundary, dict) or card_boundary.get(
                "would_overturn"
            ) != decision.get("would_overturn"):
                errors.append(
                    "card commitment overturn condition does not match decision.yaml"
                )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Architecture 2.0 loop receipt."
    )
    parser.add_argument("receipt_dir", type=Path)
    args = parser.parse_args(argv)
    errors = validate_receipt(args.receipt_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"receipt ok: {args.receipt_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
