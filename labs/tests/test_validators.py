from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
import yaml

from arch2_labs.receipts import ReceiptMetadata, seal_receipt
from arch2_labs.validators import validate_receipt


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


def test_validator_accepts_complete_receipt(valid_receipt: Path) -> None:
    assert validate_receipt(valid_receipt) == []


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


def test_validator_rejects_undeclared_payload(valid_receipt: Path) -> None:
    extra = valid_receipt / "unreviewed.txt"
    extra.write_text("not in manifest\n")

    errors = validate_receipt(valid_receipt)

    assert "payload file is not declared in manifest: unreviewed.txt" in errors
