from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from arch2_labs.receipts import ReceiptMetadata, seal_receipt
from arch2_labs.validators import _card_errors, validate_receipt


def test_validator_reports_missing_receipt_files(tmp_path: Path) -> None:
    errors = validate_receipt(tmp_path)

    assert "missing required file: manifest.yaml" in errors
    assert "missing required file: card.yaml" in errors
    assert "missing required file: decision.md" in errors


def _reseal(receipt_dir: Path) -> None:
    old_manifest = yaml.safe_load((receipt_dir / "manifest.yaml").read_text())
    seal_receipt(
        receipt_dir,
        ReceiptMetadata(
            receipt_id=old_manifest["receipt_id"],
            lab_id=old_manifest["lab_id"],
            example=old_manifest["example"],
            created_at=old_manifest["created_at"],
            status=old_manifest["status"],
        ),
    )


def _rewrite_manifest_marker(receipt_dir: Path, manifest: dict[str, object]) -> None:
    from arch2_labs.receipts import sha256_file

    manifest_path = receipt_dir / "manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    marker_path = receipt_dir / ".arch2-receipt.json"
    marker = json.loads(marker_path.read_text())
    marker["manifest_sha256"] = sha256_file(manifest_path)
    marker_path.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")


def _set_lab_id(receipt_dir: Path, record: str, value: str | None) -> None:
    if record == "card":
        path = receipt_dir / "card.yaml"
        data = yaml.safe_load(path.read_text())
        target = data["design_loop_card"]["x-arch2-labs"]
    elif record in {"environment", "decision", "manifest"}:
        filename = {
            "environment": "environment.yaml",
            "decision": "decision.yaml",
            "manifest": "manifest.yaml",
        }[record]
        path = receipt_dir / filename
        data = yaml.safe_load(path.read_text())
        target = data
    else:
        filename = {
            "evidence": "evidence_record.json",
            "recommendation": "recommendation.json",
        }[record]
        path = receipt_dir / filename
        data = json.loads(path.read_text())
        target = data
    if value is None:
        target.pop("lab_id", None)
    else:
        target["lab_id"] = value
    if record in {"evidence", "recommendation"}:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    elif record == "manifest":
        _rewrite_manifest_marker(receipt_dir, data)
        return
    else:
        path.write_text(yaml.safe_dump(data, sort_keys=False))
    _reseal(receipt_dir)


def test_validator_accepts_complete_receipt(valid_receipt: Path) -> None:
    assert validate_receipt(valid_receipt) == []


def test_card_validator_keeps_v1_0_legacy_dispatch() -> None:
    labs_root = Path(__file__).resolve().parents[1]
    card = yaml.safe_load(
        (labs_root.parent / "tests/fixtures/cards/valid-v1.0-legacy.yaml").read_text()
    )

    assert _card_errors(card) == []


@pytest.mark.parametrize(
    "record",
    ["manifest", "card", "environment", "evidence", "recommendation", "decision"],
)
def test_validator_requires_lab_id_on_every_lab_record(
    valid_receipt: Path, record: str
) -> None:
    _set_lab_id(valid_receipt, record, None)

    errors = validate_receipt(valid_receipt)

    assert f"{record} missing lab_id" in errors


@pytest.mark.parametrize(
    "record", ["card", "environment", "evidence", "recommendation", "decision"]
)
def test_validator_rejects_every_lab_id_mismatch(
    valid_receipt: Path, record: str
) -> None:
    _set_lab_id(valid_receipt, record, "other_lab")

    errors = validate_receipt(valid_receipt)

    assert any(f"{record} lab_id does not match manifest" in error for error in errors)


def test_validator_requires_card_lab_extension_and_receipt_id(
    valid_receipt: Path,
) -> None:
    path = valid_receipt / "card.yaml"
    data = yaml.safe_load(path.read_text())
    data["design_loop_card"].pop("x-arch2-labs")
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert "card missing x-arch2-labs mapping" in errors
    assert "card x-arch2-labs missing receipt_id" in errors


def test_validator_detects_payload_tampering(valid_receipt: Path) -> None:
    with (valid_receipt / "card.yaml").open("a") as card:
        card.write("tampered: true\n")

    errors = validate_receipt(valid_receipt)

    assert any("card.yaml sha256 mismatch" in error for error in errors)


def test_validator_detects_raw_output_tampering(valid_receipt: Path) -> None:
    runs = [
        json.loads(line)
        for line in (valid_receipt / "runs.jsonl").read_text().splitlines()
    ]
    scale_run = next(record for record in runs if record["stage"] == "scalesim")
    raw_path = valid_receipt / scale_run["outputs"]["raw_files"][0]["path"]
    raw_path.write_text("tampered raw output\n")

    errors = validate_receipt(valid_receipt)

    assert any("raw output sha256 mismatch" in error for error in errors)


def test_validator_requires_declared_raw_outputs(valid_receipt: Path) -> None:
    runs_path = valid_receipt / "runs.jsonl"
    runs = [json.loads(line) for line in runs_path.read_text().splitlines()]
    scale_run = next(record for record in runs if record["stage"] == "scalesim")
    scale_run["outputs"]["raw_files"] = []
    runs_path.write_text("".join(json.dumps(record) + "\n" for record in runs))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any("declares no raw output files" in error for error in errors)


def test_validator_rejects_raw_file_not_declared_by_run(valid_receipt: Path) -> None:
    runs = [
        json.loads(line)
        for line in (valid_receipt / "runs.jsonl").read_text().splitlines()
    ]
    scale_run = next(record for record in runs if record["stage"] == "scalesim")
    report_dir = valid_receipt / scale_run["outputs"]["report_dir"]
    extra = report_dir / "UNDECLARED_REPORT.csv"
    extra.write_text("undeclared raw report\n")
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any("raw output is not declared by the run" in error for error in errors)


def test_validator_rejects_cross_record_candidate_id(valid_receipt: Path) -> None:
    decision_path = valid_receipt / "decision.yaml"
    decision = yaml.safe_load(decision_path.read_text())
    decision["selected_candidate_id"] = "unknown_candidate"
    decision_path.write_text(yaml.safe_dump(decision, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert (
        "decision selected_candidate_id is not a declared candidate: unknown_candidate"
        in errors
    )


def test_validator_rejects_card_decision_drift(valid_receipt: Path) -> None:
    decision_path = valid_receipt / "decision.yaml"
    decision = yaml.safe_load(decision_path.read_text())
    decision[
        "rationale"
    ] = "The human changed this rationale after the card was recorded."
    decision_path.write_text(yaml.safe_dump(decision, sort_keys=False))
    from arch2_labs.decisions import parse_human_decision, render_decision

    (valid_receipt / "decision.md").write_text(
        render_decision(parse_human_decision(decision))
    )
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert "card learner decision does not match decision.yaml: rationale" in errors


def test_validator_rejects_card_receipt_id_drift(valid_receipt: Path) -> None:
    card_path = valid_receipt / "card.yaml"
    card = yaml.safe_load(card_path.read_text())
    card["design_loop_card"]["x-arch2-labs"]["receipt_id"] = "other-receipt"
    card_path.write_text(yaml.safe_dump(card, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert "card receipt_id does not match the manifest" in errors


@pytest.mark.parametrize("record", ["card", "evidence", "recommendation"])
def test_validator_rejects_baseline_drift(valid_receipt: Path, record: str) -> None:
    if record == "card":
        path = valid_receipt / "card.yaml"
        data = yaml.safe_load(path.read_text())
        data["design_loop_card"]["evidence"]["x-arch2-labs"]["baseline_id"] = "tiny_8x8"
        path.write_text(yaml.safe_dump(data, sort_keys=False))
    else:
        filename = {
            "evidence": "evidence_record.json",
            "recommendation": "recommendation.json",
        }[record]
        path = valid_receipt / filename
        data = json.loads(path.read_text())
        data["baseline_id"] = "tiny_8x8"
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any("baseline_id mismatch" in error for error in errors)


@pytest.mark.parametrize(
    "objective",
    [
        "latency_under_declared_gates",
        "energy_under_declared_gates",
        "area_efficiency_under_declared_gates",
    ],
)
def test_validator_rejects_rejected_candidate_as_objective_winner(
    valid_receipt: Path, objective: str
) -> None:
    path = valid_receipt / "evidence_record.json"
    evidence = json.loads(path.read_text())
    evidence["objective_rankings"][objective]["candidate_id"] = "proxy_hero_64x64"
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n")
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any(
        f"objective ranking {objective} does not select a candidate that passed the declared checks"
        in error
        for error in errors
    )


def test_validator_cross_checks_recommendation_objective_rankings(
    valid_receipt: Path,
) -> None:
    path = valid_receipt / "recommendation.json"
    recommendation = json.loads(path.read_text())
    recommendation["objective_rankings"]["energy_under_declared_gates"][
        "candidate_id"
    ] = "balanced_16x16"
    path.write_text(json.dumps(recommendation, indent=2, sort_keys=True) + "\n")
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert (
        "recommendation objective rankings do not match the supporting evidence record"
        in errors
    )


@pytest.mark.parametrize(
    "commitment_level",
    ["advance_to_rtl", "ready_for_signoff", "tapeout", "product_commitment"],
)
def test_validator_rejects_unsupported_commitment_levels(
    valid_receipt: Path, commitment_level: str
) -> None:
    decision_path = valid_receipt / "decision.yaml"
    decision = yaml.safe_load(decision_path.read_text())
    decision["commitment_level"] = commitment_level
    decision_path.write_text(yaml.safe_dump(decision, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert f"unsupported commitment level: {commitment_level}" in errors


@pytest.mark.parametrize(
    "overclaim",
    [
        "Advance this candidate to RTL.",
        "This design is ready for signoff.",
        "The candidate is tapeout-ready.",
        "Commit this configuration to the product.",
    ],
)
def test_validator_rejects_free_text_overclaims(
    valid_receipt: Path, overclaim: str
) -> None:
    decision_path = valid_receipt / "decision.yaml"
    decision = yaml.safe_load(decision_path.read_text())
    decision["rationale"] = overclaim
    decision_path.write_text(yaml.safe_dump(decision, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any("decision.yaml appears to overclaim" in error for error in errors)


def test_validator_requires_explicit_runtime_versions(valid_receipt: Path) -> None:
    manifest_path = valid_receipt / "manifest.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["runtime"]["tools"].pop("SCALE-Sim")
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))
    marker_path = valid_receipt / ".arch2-receipt.json"
    marker = json.loads(marker_path.read_text())
    from arch2_labs.receipts import sha256_file

    marker["manifest_sha256"] = sha256_file(manifest_path)
    marker_path.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")

    errors = validate_receipt(valid_receipt)

    assert "manifest runtime missing tool version: SCALE-Sim" in errors


@pytest.mark.parametrize("layer", ["manifest", "run", "card"])
def test_validator_cross_checks_scalesim_version(
    valid_receipt: Path, layer: str
) -> None:
    if layer == "manifest":
        path = valid_receipt / "manifest.yaml"
        manifest = yaml.safe_load(path.read_text())
        manifest["runtime"]["tools"]["SCALE-Sim"] = "999.0"
        _rewrite_manifest_marker(valid_receipt, manifest)
    elif layer == "run":
        path = valid_receipt / "runs.jsonl"
        runs = [json.loads(line) for line in path.read_text().splitlines()]
        scale_run = next(record for record in runs if record["stage"] == "scalesim")
        scale_run["tool"]["version"] = "999.0"
        path.write_text("".join(json.dumps(record) + "\n" for record in runs))
        _reseal(valid_receipt)
    else:
        path = valid_receipt / "card.yaml"
        card = yaml.safe_load(path.read_text())
        card["design_loop_card"]["evidence"]["records"][0]["tool"]["version"] = "999.0"
        path.write_text(yaml.safe_dump(card, sort_keys=False))
        _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any("version does not match" in error for error in errors)


def test_validator_cross_checks_card_and_run_config_hash(
    valid_receipt: Path,
) -> None:
    path = valid_receipt / "card.yaml"
    card = yaml.safe_load(path.read_text())
    inputs = card["design_loop_card"]["evidence"]["records"][0]["inputs"]
    config = next(
        artifact for artifact in inputs if artifact["artifact_id"].endswith("-config")
    )
    config["integrity"]["sha256"] = f"sha256:{'9' * 64}"
    path.write_text(yaml.safe_dump(card, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any(
        "config binding does not match run" in error or "sha256 mismatch" in error
        for error in errors
    )


def test_validator_cross_checks_card_replay_source(valid_receipt: Path) -> None:
    path = valid_receipt / "card.yaml"
    card = yaml.safe_load(path.read_text())
    outputs = card["design_loop_card"]["evidence"]["records"][0]["outputs"]
    compute = next(
        artifact
        for artifact in outputs
        if artifact["uri"].endswith("/COMPUTE_REPORT.csv")
    )
    compute["uri"] = "evidence/not-the-run.json"
    path.write_text(yaml.safe_dump(card, sort_keys=False))
    _reseal(valid_receipt)

    errors = validate_receipt(valid_receipt)

    assert any(
        "compute output does not match run" in error
        or "local artifact is missing" in error
        for error in errors
    )


def test_validator_rejects_undeclared_payload(valid_receipt: Path) -> None:
    extra = valid_receipt / "unreviewed.txt"
    extra.write_text("not in manifest\n")

    errors = validate_receipt(valid_receipt)

    assert "payload file is not declared in manifest: unreviewed.txt" in errors
