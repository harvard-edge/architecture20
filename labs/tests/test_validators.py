from pathlib import Path

from arch2_labs.validators import validate_receipt


def test_validator_reports_missing_receipt_files(tmp_path: Path) -> None:
    errors = validate_receipt(tmp_path)

    assert "missing required file: card.yaml" in errors
    assert "missing required file: decision.md" in errors
