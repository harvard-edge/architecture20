from __future__ import annotations

import json
from pathlib import Path

import pytest

from arch2_labs.presentation import (
    render_objective_summary,
    render_receipt_validation,
)


def test_objective_presentation_executes_against_generated_evidence_record(
    draft_receipt: Path,
) -> None:
    evidence = json.loads((draft_receipt / "evidence_record.json").read_text())

    rendered = render_objective_summary(evidence)

    assert "Lowest latency" in rendered
    assert "Lowest first-order energy" in rendered
    assert "Highest area efficiency" in rendered
    assert "gate_survivor" not in rendered


def test_objective_presentation_rejects_stale_contract() -> None:
    with pytest.raises(ValueError, match="latency_under_declared_gates"):
        render_objective_summary(
            {"objective_rankings": {"gate_survivor": "throughput_32x32"}}
        )


def test_receipt_validation_never_renders_errors_as_green() -> None:
    rendered = render_receipt_validation(["manifest hash mismatch"])

    assert "Run archive invalid" in rendered
    assert "manifest hash mismatch" in rendered
    assert "✅" not in rendered


def test_receipt_validation_renders_clean_receipt_as_green() -> None:
    rendered = render_receipt_validation([])

    assert "Run archive valid" in rendered
    assert "✅" in rendered
