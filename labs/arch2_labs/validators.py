from __future__ import annotations

import argparse
import json
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from arch2_labs.decisions import decision_errors, parse_human_decision, render_decision
from arch2_labs.receipts import (
    MANIFEST_FILENAME,
    MARKER_FILENAME,
    manifest_payload_errors,
    sha256_file,
    verify_receipt_integrity,
    verify_receipt_ownership,
)

LABS_ROOT = Path(__file__).resolve().parents[1]
CARD_SCHEMA_SOURCES = {
    "1.0": LABS_ROOT.parent / "schemas" / "design-loop-card.v1.schema.json",
    "1.1": LABS_ROOT.parent / "schemas" / "design-loop-card.v1.1.schema.json",
    "2.0": LABS_ROOT.parent / "schemas" / "design-loop-card.v2.schema.json",
}

REQUIRED_FILES = [
    MARKER_FILENAME,
    MANIFEST_FILENAME,
    "card.yaml",
    "environment.yaml",
    "candidates.jsonl",
    "runs.jsonl",
    "evidence_record.json",
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
    errors = manifest_payload_errors(receipt_dir, manifest)
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

    return errors


def _card_schema(version: str = "2.0") -> dict[str, Any]:
    source = CARD_SCHEMA_SOURCES.get(version)
    if source is None:
        raise ValueError(f"unsupported design-loop card schema: {version}")
    if source.is_file():
        return json.loads(source.read_text())
    filename = {
        "1.0": "design-loop-card.v1.schema.json",
        "1.1": "design-loop-card.v1.1.schema.json",
        "2.0": "design-loop-card.v2.schema.json",
    }[version]
    resource = files("arch2_labs").joinpath("resources", filename)
    return json.loads(resource.read_text())


def _card_errors(card: Any, base_dir: Path | None = None) -> list[str]:
    version = card.get("schema_version") if isinstance(card, dict) else None
    try:
        schema = _card_schema(version)
    except ValueError as exc:
        return [f"card.yaml <root>: {exc}"]
    schemas = [_card_schema("1.0"), _card_schema("1.1"), _card_schema("2.0")]
    registry = Registry()
    for registered_schema in schemas:
        registry = registry.with_resource(
            registered_schema["$id"], Resource.from_contents(registered_schema)
        )
    validator = Draft202012Validator(
        schema, format_checker=FormatChecker(), registry=registry
    )
    messages = []
    for error in sorted(validator.iter_errors(card), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        messages.append(f"card.yaml {location}: {error.message}")
    if not messages and version == "2.0":
        messages.extend(_card_v2_semantic_errors(card, base_dir))
    return messages


def _card_v2_semantic_errors(
    document: dict[str, Any], base_dir: Path | None
) -> list[str]:
    """Check v2 references, authority bindings, and local content hashes."""
    errors: list[str] = []
    card = document["design_loop_card"]

    def duplicate_errors(
        records: list[dict[str, Any]], key: str, path: str
    ) -> set[str]:
        identifiers: set[str] = set()
        for index, record in enumerate(records):
            identifier = record[key]
            if identifier in identifiers:
                errors.append(
                    f"card.yaml {path}[{index}].{key}: duplicate identifier {identifier}"
                )
            identifiers.add(identifier)
        return identifiers

    evidence_records = card["evidence"]["records"]
    claims = card["claims"]
    gates = card["gates"]
    rejected = card["failed_or_rejected"]
    evidence_ids = duplicate_errors(
        evidence_records, "evidence_id", "design_loop_card.evidence.records"
    )
    claim_ids = duplicate_errors(claims, "claim_id", "design_loop_card.claims")
    gate_ids = duplicate_errors(gates, "gate_id", "design_loop_card.gates")
    duplicate_errors(rejected, "record_id", "design_loop_card.failed_or_rejected")

    def refs(values: list[str], known: set[str], path: str, label: str) -> None:
        for index, value in enumerate(values):
            if value not in known:
                errors.append(
                    f"card.yaml {path}[{index}]: unknown {label} reference {value}"
                )

    for index, claim in enumerate(claims):
        refs(
            claim["evidence_refs"],
            evidence_ids,
            f"design_loop_card.claims[{index}].evidence_refs",
            "evidence",
        )
    for index, gate in enumerate(gates):
        refs(
            gate["evidence_refs"],
            evidence_ids,
            f"design_loop_card.gates[{index}].evidence_refs",
            "evidence",
        )
    for index, record in enumerate(rejected):
        refs(
            record["evidence_refs"],
            evidence_ids,
            f"design_loop_card.failed_or_rejected[{index}].evidence_refs",
            "evidence",
        )
        gate_ref = record.get("gate_ref")
        if gate_ref is not None and gate_ref not in gate_ids:
            errors.append(
                "card.yaml "
                f"design_loop_card.failed_or_rejected[{index}].gate_ref: "
                f"unknown gate reference {gate_ref}"
            )

    recommendation = card.get("recommendation")
    if recommendation:
        refs(
            recommendation["claim_refs"],
            claim_ids,
            "design_loop_card.recommendation.claim_refs",
            "claim",
        )
    decision_record = card["accountable_decision"]
    refs(
        decision_record["claim_refs"],
        claim_ids,
        "design_loop_card.accountable_decision.claim_refs",
        "claim",
    )
    review = card.get("independent_review")
    if review:
        refs(
            review["claim_refs"],
            claim_ids,
            "design_loop_card.independent_review.claim_refs",
            "claim",
        )
        refs(
            review["evidence_refs"],
            evidence_ids,
            "design_loop_card.independent_review.evidence_refs",
            "evidence",
        )

    rights = {
        (right["holder_id"], right["action"]) for right in card["decision_rights"]
    }
    if card["profiles"]["decision_rights"] == "complete":
        for index, gate in enumerate(gates):
            if (gate["authority_id"], "reject") not in rights:
                errors.append(
                    "card.yaml "
                    f"design_loop_card.gates[{index}].authority_id: "
                    "rejection-check authority lacks a declared reject right"
                )
            waiver = gate["waiver_rule"]
            if waiver["allowed"] and (waiver["authority_id"], "waive") not in rights:
                errors.append(
                    "card.yaml "
                    f"design_loop_card.gates[{index}].waiver_rule.authority_id: "
                    "waiver authority lacks a declared waive right"
                )
        if (
            recommendation
            and (recommendation["recommender_id"], "recommend") not in rights
        ):
            errors.append(
                "card.yaml design_loop_card.recommendation.recommender_id: "
                "recommender lacks a declared recommend right"
            )
        if (decision_record["holder_id"], "commit") not in rights:
            errors.append(
                "card.yaml design_loop_card.accountable_decision.holder_id: "
                "decision owner lacks a declared commit right"
            )

    if base_dir is None:
        return errors

    def verify_artifact(uri: str, expected: str, path: str) -> None:
        parsed = urlsplit(uri)
        if parsed.scheme or parsed.netloc:
            return
        if parsed.query or parsed.fragment:
            errors.append(f"card.yaml {path}: local URI has query or fragment")
            return
        target = _safe_payload_path(base_dir, unquote(parsed.path))
        if target is None:
            errors.append(f"card.yaml {path}: local artifact path is unsafe")
            return
        if not target.is_file():
            errors.append(f"card.yaml {path}: local artifact is missing: {uri}")
            return
        observed = f"sha256:{sha256_file(target)}"
        if observed != expected:
            errors.append(
                f"card.yaml {path}: sha256 mismatch for {uri}: "
                f"{expected} != {observed}"
            )

    for record_index, record in enumerate(evidence_records):
        for collection in ("inputs", "outputs"):
            for artifact_index, artifact in enumerate(record[collection]):
                digest = artifact["integrity"].get("sha256")
                if digest:
                    verify_artifact(
                        artifact["uri"],
                        digest,
                        (
                            "design_loop_card.evidence.records"
                            f"[{record_index}].{collection}[{artifact_index}].uri"
                        ),
                    )

    replay = card.get("replay")
    if replay:
        artifacts = [("environment_binding", replay["environment_binding"])]
        artifacts.extend(
            (f"inputs[{index}]", artifact)
            for index, artifact in enumerate(replay["inputs"])
        )
        artifacts.extend(
            (f"outputs[{index}]", artifact)
            for index, artifact in enumerate(replay["outputs"])
        )
        for suffix, artifact in artifacts:
            verify_artifact(
                artifact["uri"],
                artifact["sha256"],
                f"design_loop_card.replay.{suffix}.uri",
            )
    return errors


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


def _provenance_errors(
    manifest: dict[str, Any], lab_card: dict[str, Any], runs: list[dict[str, Any]]
) -> list[str]:
    errors: list[str] = []
    manifest_runtime = manifest.get("runtime", {})
    manifest_tools = (
        manifest_runtime.get("tools", {}) if isinstance(manifest_runtime, dict) else {}
    )
    manifest_python = (
        manifest_runtime.get("python", {}) if isinstance(manifest_runtime, dict) else {}
    )
    expected_scale_version = manifest_tools.get("SCALE-Sim")
    card_evidence = lab_card.get("evidence", {})
    card_records = (
        card_evidence.get("records", []) if isinstance(card_evidence, dict) else []
    )
    card_by_id = {
        record.get("evidence_id"): record
        for record in card_records
        if isinstance(record, dict) and record.get("evidence_id")
    }
    expected_evidence_ids: set[str] = set()

    for run in runs:
        if run.get("stage") != "scalesim" or run.get("status") != "ok":
            continue
        candidate_id = run.get("candidate_id")
        evidence_id = f"scalesim-{candidate_id}"
        expected_evidence_ids.add(evidence_id)
        tool = run.get("tool", {})
        run_version = tool.get("version") if isinstance(tool, dict) else None
        if run_version != expected_scale_version:
            errors.append(
                f"SCALE-Sim run {candidate_id} version does not match manifest: "
                f"{run_version} != {expected_scale_version}"
            )
        runtime = run.get("runtime", {})
        if not isinstance(runtime, dict):
            runtime = {}
        if runtime.get("python") != manifest_python.get("version"):
            errors.append(
                f"SCALE-Sim run {candidate_id} Python version does not match manifest"
            )
        if runtime.get("executable") != manifest_python.get("executable"):
            errors.append(
                f"SCALE-Sim run {candidate_id} Python executable does not match manifest"
            )

        card_record = card_by_id.get(evidence_id)
        if not isinstance(card_record, dict):
            errors.append(
                f"card evidence is missing for successful run: {candidate_id}"
            )
            continue
        inputs = run.get("inputs", {})
        config_hash = inputs.get("config_sha256") if isinstance(inputs, dict) else None
        expected_source = (
            f"runs/{candidate_id}/scalesim-results/{candidate_id}/COMPUTE_REPORT.csv"
        )
        provenance = card_record.get("provenance")
        if isinstance(provenance, dict):
            expected_tool = f"SCALE-Sim {expected_scale_version}"
            if provenance.get("tool_version") != expected_tool:
                errors.append(
                    f"card evidence {evidence_id} tool version does not match manifest/run"
                )
            if provenance.get("parameter_hash") != f"sha256:{config_hash}":
                errors.append(
                    f"card evidence {evidence_id} parameter hash does not match run config"
                )
            if provenance.get("source_uri") != expected_source:
                errors.append(
                    f"card evidence {evidence_id} replay source does not match run output"
                )
            continue

        card_tool = card_record.get("tool", {})
        if (
            not isinstance(card_tool, dict)
            or card_tool.get("name") != "SCALE-Sim"
            or card_tool.get("version") != expected_scale_version
        ):
            errors.append(
                f"card evidence {evidence_id} tool version does not match manifest/run"
            )
        card_inputs = {
            artifact.get("artifact_id"): artifact
            for artifact in card_record.get("inputs", [])
            if isinstance(artifact, dict)
        }
        for name in ("config", "topology", "layout"):
            artifact = card_inputs.get(f"{candidate_id}-{name}", {})
            expected_uri = f"runs/{candidate_id}/inputs/{'scale.cfg' if name == 'config' else name + '.csv'}"
            expected_digest = f"sha256:{inputs.get(f'{name}_sha256')}"
            if (
                artifact.get("uri") != expected_uri
                or artifact.get("integrity", {}).get("sha256") != expected_digest
            ):
                errors.append(
                    f"card evidence {evidence_id} {name} binding does not match run"
                )
        card_outputs = card_record.get("outputs", [])
        compute_output = next(
            (
                artifact
                for artifact in card_outputs
                if isinstance(artifact, dict) and artifact.get("uri") == expected_source
            ),
            None,
        )
        raw_files = run.get("outputs", {}).get("raw_files", [])
        expected_compute_hash = next(
            (
                raw.get("sha256")
                for raw in raw_files
                if Path(str(raw.get("path"))).name == "COMPUTE_REPORT.csv"
            ),
            None,
        )
        if (
            not isinstance(compute_output, dict)
            or compute_output.get("integrity", {}).get("sha256")
            != f"sha256:{expected_compute_hash}"
        ):
            errors.append(
                f"card evidence {evidence_id} compute output does not match run"
            )

    extra_card_ids = set(card_by_id) - expected_evidence_ids
    for evidence_id in sorted(extra_card_ids):
        errors.append(f"card evidence has no successful run: {evidence_id}")
    return errors


def validate_receipt(receipt_dir: Path) -> list[str]:
    errors: list[str] = []
    receipt_dir = receipt_dir.expanduser().absolute()
    if receipt_dir.is_symlink():
        return [f"run archive directory must not be a symbolic link: {receipt_dir}"]
    if not receipt_dir.is_dir():
        return [f"run archive directory does not exist: {receipt_dir}"]

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
        errors.append("course run archive awaits its required decision record")

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
        _load_json(receipt_dir / "evidence_record.json", errors)
        if present("evidence_record.json")
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
        errors.extend(_card_errors(card, receipt_dir))
    else:
        errors.append("card.yaml must contain a mapping")
    lab_card = card.get("design_loop_card", {}) if isinstance(card, dict) else {}
    card_extension = (
        lab_card.get("x-arch2-labs") if isinstance(lab_card, dict) else None
    )
    if not isinstance(card_extension, dict):
        errors.append("card missing x-arch2-labs mapping")
        card_extension = {}
    if not card_extension.get("receipt_id"):
        errors.append("card x-arch2-labs missing receipt_id")
    elif manifest and card_extension["receipt_id"] != manifest.get("receipt_id"):
        errors.append("card receipt_id does not match the manifest")
    lab_ids = {
        "manifest": manifest.get("lab_id"),
        "card": card_extension.get("lab_id"),
        "environment": environment.get("lab_id")
        if isinstance(environment, dict)
        else None,
        "evidence": evidence.get("lab_id") if isinstance(evidence, dict) else None,
        "recommendation": recommendation.get("lab_id")
        if isinstance(recommendation, dict)
        else None,
    }
    if manifest.get("status") == "complete":
        lab_ids["decision"] = (
            decision.get("lab_id") if isinstance(decision, dict) else None
        )
    expected_lab_id = manifest.get("lab_id")
    for record, lab_id in lab_ids.items():
        if not lab_id:
            errors.append(f"{record} missing lab_id")
        elif expected_lab_id and lab_id != expected_lab_id:
            errors.append(
                f"{record} lab_id does not match manifest: {lab_id} != {expected_lab_id}"
            )

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
    baseline_candidates = [
        record.get("candidate_id")
        for record in candidates
        if record.get("is_baseline") is True
    ]
    baseline_id = baseline_candidates[0] if len(baseline_candidates) == 1 else None
    if len(baseline_candidates) != 1:
        errors.append("candidates.jsonl must mark exactly one baseline candidate")

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
    successful_scale_ids = {
        run.get("candidate_id")
        for run in runs
        if run.get("stage") == "scalesim" and run.get("status") == "ok"
    }
    if baseline_id is not None and baseline_id not in successful_scale_ids:
        errors.append(
            f"baseline candidate has no successful SCALE-Sim run: {baseline_id}"
        )

    if not negative_traces:
        errors.append("negative_traces.jsonl is empty")
    rejected_ids: set[str] = set()
    for trace in negative_traces:
        candidate_id = trace.get("candidate_id")
        rejected_ids.add(candidate_id)
        if candidate_id not in declared_ids:
            errors.append(
                f"rejected-alternative record references an undeclared candidate: {candidate_id}"
            )
        for field in ("stage", "gate", "reason"):
            if not trace.get(field):
                errors.append(
                    f"rejected-alternative record {candidate_id} missing field: {field}"
                )
    card_trace_records = lab_card.get(
        "failed_or_rejected", lab_card.get("negative_traces", [])
    )
    card_negative_ids = {
        trace.get("candidate_id")
        for trace in card_trace_records
        if isinstance(trace, dict)
    }
    if card_negative_ids != rejected_ids:
        errors.append("card negative-trace IDs do not match negative_traces.jsonl")

    if isinstance(evidence, dict):
        stages = {stage.get("stage") for stage in evidence.get("stages", [])}
        for stage in ("proxy", "scalesim"):
            if stage not in stages:
                errors.append(f"evidence_record.json has no {stage} evidence stage")
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
            errors.append(
                "supporting evidence record contains an undeclared candidate outcome"
            )
        accepted_ids = {
            outcome.get("candidate_id")
            for outcome in evidence.get("candidate_outcomes", [])
            if isinstance(outcome, dict) and outcome.get("accepted") is True
        }
        required_objectives = {
            "latency_under_declared_gates",
            "energy_under_declared_gates",
            "area_efficiency_under_declared_gates",
        }
        rankings = evidence.get("objective_rankings")
        if not isinstance(rankings, dict) or set(rankings) != required_objectives:
            errors.append(
                "supporting evidence record must contain exactly the three supported objective rankings"
            )
            rankings = {}
        for objective in sorted(required_objectives):
            ranking = rankings.get(objective)
            ranked_id = (
                ranking.get("candidate_id") if isinstance(ranking, dict) else None
            )
            if ranked_id not in accepted_ids or ranked_id in rejected_ids:
                errors.append(
                    f"objective ranking {objective} does not select a candidate that passed the declared checks: {ranked_id}"
                )
        for field in ("machine_recommendation", "proxy_winner"):
            candidate_id = evidence.get(field)
            if candidate_id not in declared_ids:
                errors.append(
                    f"supporting evidence record {field} is not a declared candidate: {candidate_id}"
                )
        if evidence.get("rejected_count") != len(negative_traces):
            errors.append(
                "supporting evidence record rejected_count does not match rejected-alternative records"
            )

    card_evidence = lab_card.get("evidence", {})
    card_evidence_extension = (
        card_evidence.get("x-arch2-labs", {}) if isinstance(card_evidence, dict) else {}
    )
    baseline_records = {
        "candidates": baseline_id,
        "card": (
            card_evidence.get("baseline_id")
            if isinstance(card_evidence, dict) and "baseline_id" in card_evidence
            else card_evidence_extension.get("baseline_id")
            if isinstance(card_evidence_extension, dict)
            else None
        ),
        "evidence": evidence.get("baseline_id") if isinstance(evidence, dict) else None,
        "recommendation": recommendation.get("baseline_id")
        if isinstance(recommendation, dict)
        else None,
    }
    if baseline_id is None or any(
        value != baseline_id for value in baseline_records.values()
    ):
        errors.append(
            f"baseline_id mismatch across run-archive records: {baseline_records}"
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
            errors.append("recommendation must state that it is not a final decision")
        if recommendation.get("commitment") != "none":
            errors.append("machine recommendation must not claim commitment authority")
        if evidence and recommendation.get("candidate_id") != evidence.get(
            "machine_recommendation"
        ):
            errors.append(
                "recommendation candidate does not match the supporting evidence record"
            )
        latency_ranking = (
            evidence.get("objective_rankings", {}).get(
                "latency_under_declared_gates", {}
            )
            if isinstance(evidence, dict)
            else {}
        )
        if recommendation.get("candidate_id") != latency_ranking.get("candidate_id"):
            errors.append(
                "machine recommendation must match the check-filtered latency ranking"
            )
        if evidence and recommendation.get("proxy_winner") != evidence.get(
            "proxy_winner"
        ):
            errors.append(
                "recommendation proxy winner does not match the supporting evidence record"
            )
        if evidence and recommendation.get("objective_rankings") != evidence.get(
            "objective_rankings"
        ):
            errors.append(
                "recommendation objective rankings do not match the supporting evidence record"
            )

    declared_manifest_files = {
        entry.get("path")
        for entry in manifest.get("files", [])
        if isinstance(entry, dict) and isinstance(entry.get("path"), str)
    }
    errors.extend(_validate_run_files(receipt_dir, runs, declared_manifest_files))
    if isinstance(lab_card, dict):
        errors.extend(_provenance_errors(manifest, lab_card, runs))

    if decision:
        errors.extend(decision_errors(decision))
        if isinstance(decision, dict):
            selected_id = decision.get("selected_candidate_id")
            if decision.get("lab_id") != expected_lab_id:
                errors.append("decision lab_id does not match the run archive")
            if selected_id not in declared_ids:
                errors.append(
                    "decision selected_candidate_id is not a declared candidate: "
                    f"{selected_id}"
                )
            if selected_id in rejected_ids:
                errors.append(f"decision selects a rejected candidate: {selected_id}")
            objective = decision.get("governing_objective")
            ranking = (
                evidence.get("objective_rankings", {}).get(objective, {})
                if isinstance(evidence, dict)
                else {}
            )
            expected_id = (
                ranking.get("candidate_id") if isinstance(ranking, dict) else None
            )
            differs = selected_id != expected_id
            if differs and decision.get("objective_override") is not True:
                errors.append(
                    "decision differs from governing objective winner without an explicit override"
                )
            if not differs and decision.get("objective_override") is True:
                errors.append(
                    "decision declares an objective override but selects the objective winner"
                )
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
        card_decision = lab_card.get("accountable_decision", {})
        if (
            not isinstance(card_decision, dict)
            or card_decision.get("status") != "authorized"
        ):
            errors.append(
                "completed run archive must contain an authorized accountable_decision field"
            )
        learner = card_extension.get("learner_decision", {})
        for field in ("governing_objective", "selected_candidate_id", "rationale"):
            if not isinstance(learner, dict) or not learner.get(field):
                errors.append(f"card learner decision missing field: {field}")
        if isinstance(decision, dict) and isinstance(learner, dict):
            field_map = {
                "governing_objective": "governing_objective",
                "selected_candidate_id": "selected_candidate_id",
                "objective_override": "objective_override",
                "override_reason": "override_reason",
                "rationale": "rationale",
                "residual_risk": "residual_risk",
            }
            for learner_field, decision_field in field_map.items():
                if learner.get(learner_field) != decision.get(decision_field):
                    errors.append(
                        f"card learner decision does not match decision.yaml: {learner_field}"
                    )
        if isinstance(decision, dict):
            if not isinstance(card_decision, dict) or card_decision.get(
                "holder_id"
            ) != decision.get("human_owner"):
                errors.append("card decision owner does not match decision.yaml")
            reopen_conditions = (
                card_decision.get("reopen_conditions", [])
                if isinstance(card_decision, dict)
                else []
            )
            if decision.get("would_overturn") not in reopen_conditions:
                errors.append(
                    "card commitment overturn condition does not match decision.yaml"
                )
            if card_decision.get("rationale") != decision.get("rationale"):
                errors.append("card decision rationale does not match decision.yaml")

    return errors


def validate_decision_draft(receipt_dir: Path) -> dict[str, Any]:
    """Require an intact evidence-bound v2 draft before a decision transition."""
    receipt_dir = receipt_dir.expanduser().absolute()
    try:
        manifest = verify_receipt_integrity(
            receipt_dir, expected_status="awaiting_human_decision"
        )
    except ValueError as exc:
        raise ValueError(f"draft run archive failed integrity: {exc}") from exc

    forbidden = [
        name
        for name in ("decision.yaml", "decision.md")
        if (receipt_dir / name).exists()
    ]
    errors = [f"draft run archive already contains {name}" for name in forbidden]
    card_path = receipt_dir / "card.yaml"
    try:
        card = yaml.safe_load(card_path.read_text())
        card_body = card["design_loop_card"]
    except (OSError, yaml.YAMLError, KeyError, TypeError) as exc:
        errors.append(f"draft card is unreadable: {exc}")
        card_body = {}
    profiles = card_body.get("profiles", {})
    for profile in ("inspectability", "disclosure", "decision_rights"):
        if not isinstance(profiles, dict) or profiles.get(profile) != "complete":
            errors.append(f"draft card must complete the {profile} profile")
    if not isinstance(profiles, dict) or profiles.get("replay") != "partial":
        errors.append(
            "draft card must mark replay partial until a separate replay succeeds"
        )
    replay = card_body.get("replay", {})
    if (
        not isinstance(replay, dict)
        or replay.get("validation_status") != "bindings_verified"
    ):
        errors.append("draft card must verify its replay bindings")
    decision_record = card_body.get("accountable_decision", {})
    if (
        not isinstance(decision_record, dict)
        or decision_record.get("status") != "pending"
    ):
        errors.append("draft card accountable_decision must remain pending")
    if isinstance(decision_record, dict) and "recorded_at" in decision_record:
        errors.append("draft card accountable_decision must not have recorded_at")

    expected_incomplete_errors = {
        "missing required file: decision.yaml",
        "missing required file: decision.md",
        "course run archive awaits its required decision record",
    }
    errors.extend(
        error
        for error in validate_receipt(receipt_dir)
        if error not in expected_incomplete_errors
    )
    if errors:
        raise ValueError("draft run archive failed integrity: " + "; ".join(errors))
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Architecture 2.0 run archive."
    )
    parser.add_argument("receipt_dir", type=Path)
    args = parser.parse_args(argv)
    errors = validate_receipt(args.receipt_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"run archive ok: {args.receipt_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
