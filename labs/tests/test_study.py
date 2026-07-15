from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from arch2_labs.study import (
    EXAMPLE_NAME,
    ProposalValidationError,
    conventional_shapes,
    evaluate_spec,
    evaluation_specs,
    model_payload_errors,
    reference_errors,
    select_recorded_model_payload,
    study_example_dir,
    write_reference_manifest,
)
from arch2_labs.scale_env import load_workload


def _payload_and_schema() -> tuple[dict[str, object], dict[str, object]]:
    root = study_example_dir()
    payload = json.loads(
        (root / "recorded" / "model" / "original_response.json").read_text()
    )
    schema = json.loads((root / "context" / "model_output.schema.json").read_text())
    return payload, schema


def test_recorded_model_output_is_valid_without_repair() -> None:
    payload, selected, repair_used = select_recorded_model_payload(study_example_dir())

    assert len(payload["candidates"]) == 3
    assert selected == "recorded/model/original_response.json"
    assert repair_used is False


def test_model_validator_rejects_malformed_output() -> None:
    _, schema = _payload_and_schema()

    errors = model_payload_errors(["not", "an", "object"], schema)

    assert errors


def test_model_validator_rejects_illegal_geometry() -> None:
    payload, schema = _payload_and_schema()
    payload["candidates"][0]["array_rows"] = 128
    payload["candidates"][0]["array_cols"] = 16

    errors = model_payload_errors(payload, schema)

    assert any("exceeds 1024 PEs" in error for error in errors)


def test_model_validator_rejects_duplicates() -> None:
    payload, schema = _payload_and_schema()
    payload["candidates"][1]["candidate_id"] = payload["candidates"][0]["candidate_id"]
    payload["candidates"][1]["array_rows"] = payload["candidates"][0]["array_rows"]
    payload["candidates"][1]["array_cols"] = payload["candidates"][0]["array_cols"]

    errors = model_payload_errors(payload, schema)

    assert "candidate identifiers must be unique" in errors
    assert "candidate shapes must be unique" in errors


def test_model_validator_requires_rationale() -> None:
    payload, schema = _payload_and_schema()
    del payload["candidates"][0]["rationale"]

    errors = model_payload_errors(payload, schema)

    assert any("rationale" in error and "required" in error for error in errors)


def test_invalid_repair_exhausts_declared_repair_budget(tmp_path: Path) -> None:
    source = study_example_dir()
    root = tmp_path / EXAMPLE_NAME
    (root / "context").mkdir(parents=True)
    (root / "recorded" / "model").mkdir(parents=True)
    (root / "context" / "model_output.schema.json").write_text(
        (source / "context" / "model_output.schema.json").read_text()
    )
    payload, _ = _payload_and_schema()
    payload["candidates"][0]["array_rows"] = 128
    payload["candidates"][0]["array_cols"] = 128
    for name in ("original_response.json", "repair_response.json"):
        (root / "recorded" / "model" / name).write_text(json.dumps(payload))

    with pytest.raises(ProposalValidationError, match="repair exhausted"):
        select_recorded_model_payload(root)


def test_conventional_arm_matches_preregistration() -> None:
    root = study_example_dir()
    layers = load_workload(root / "workloads" / "xr_slice_gemm.csv")

    assert conventional_shapes(layers) == [(16, 64), (8, 128), (64, 16)]


def test_evaluation_budgets_are_equal_and_mechanism_probe_is_separate() -> None:
    root = study_example_dir()
    payload, _, _ = select_recorded_model_payload(root)
    specs = evaluation_specs(root, payload)

    assert len([spec for spec in specs if spec.arm == "model"]) == 4
    assert len([spec for spec in specs if spec.arm == "conventional"]) == 4
    assert len([spec for spec in specs if spec.arm == "mechanism_probe"]) == 4


def test_recorded_recommendation_does_not_claim_authorization() -> None:
    result = json.loads(
        (
            study_example_dir() / "recorded" / "reference" / "study_results.json"
        ).read_text()
    )
    recommendation = result["recommendation"]

    assert (
        recommendation["accountable_decision_status"] == "awaiting_author_confirmation"
    )
    assert recommendation["recommended_next_action"]
    assert "authorized_next_action" not in recommendation


def test_simulator_failure_is_recorded_without_replacement(tmp_path: Path) -> None:
    root = study_example_dir()
    payload, _, _ = select_recorded_model_payload(root)
    spec = evaluation_specs(root, payload)[0]

    def fail(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError("simulator failed")

    result = evaluate_spec(
        spec, tmp_path, root / "layouts" / "default_layout.csv", runner=fail
    )

    assert result["status"] == "failed"
    assert result["gate_result"] == "simulator_failure"
    assert result["error_type"] == "RuntimeError"


def test_reference_hash_mismatch_is_detected(tmp_path: Path) -> None:
    reference = tmp_path / "reference"
    reference.mkdir()
    result = reference / "study_results.json"
    result.write_text('{"status":"original"}\n')
    write_reference_manifest(reference)
    result.write_text('{"status":"tampered"}\n')

    errors = reference_errors(reference)

    assert "reference sha256 mismatch: study_results.json" in errors
