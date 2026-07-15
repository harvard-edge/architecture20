from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from arch2_labs.decisions import record_human_decision
from arch2_labs.validators import validate_receipt


def _snapshot(directory: Path) -> dict[str, bytes]:
    return {
        path.relative_to(directory).as_posix(): path.read_bytes()
        for path in directory.rglob("*")
        if path.is_file() and not path.is_symlink()
    }


def _decision(
    candidate_id: str = "throughput_32x32",
    objective: str = "latency_under_declared_gates",
    *,
    override: bool = False,
    override_reason: str | None = None,
) -> dict[str, object]:
    return {
        "schema_version": "arch2-human-decision/v0.2",
        "lab_id": "scale_proxy_mirage",
        "human_owner": "Decision integrity test author",
        "authored_at": "2026-07-11T00:00:00+00:00",
        "selected_candidate_id": candidate_id,
        "governing_objective": objective,
        "objective_override": override,
        "override_reason": override_reason,
        "commitment_level": "next_fidelity_study",
        "rationale": "This candidate is the gate-filtered latency winner.",
        "residual_risk": "The simulator omits physical effects.",
        "would_overturn": "A higher-fidelity result that reverses the ranking.",
    }


def test_record_decision_refuses_tampered_draft_without_writing(
    draft_receipt: Path,
) -> None:
    environment = draft_receipt / "environment.yaml"
    environment.write_text(environment.read_text() + "tampered: true\n")
    before = _snapshot(draft_receipt)

    with pytest.raises(ValueError, match="draft run archive failed integrity"):
        record_human_decision(draft_receipt, _decision())

    assert _snapshot(draft_receipt) == before
    assert not (draft_receipt / "decision.yaml").exists()
    assert not (draft_receipt / "decision.md").exists()


def test_record_decision_refuses_completed_receipt_without_writing(
    valid_receipt: Path,
) -> None:
    before = _snapshot(valid_receipt)

    with pytest.raises(ValueError, match="awaiting_human_decision"):
        record_human_decision(valid_receipt, _decision())

    assert _snapshot(valid_receipt) == before


def test_decision_module_attaches_decision_to_intact_draft(
    draft_receipt: Path, tmp_path: Path
) -> None:
    decision_path = tmp_path / "decision.yaml"
    import yaml

    decision_path.write_text(yaml.safe_dump(_decision(), sort_keys=False))

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "arch2_labs.decisions",
            str(draft_receipt),
            str(decision_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "decision recorded" in completed.stdout
    assert validate_receipt(draft_receipt) == []


def test_decision_module_help_is_discoverable() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "arch2_labs.decisions", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert "Attach a decision record" in completed.stdout
    assert "receipt_dir" in completed.stdout
    assert "decision_file" in completed.stdout


@pytest.mark.parametrize(
    "objective",
    [
        "latency_under_declared_gates",
        "energy_under_declared_gates",
        "area_efficiency_under_declared_gates",
    ],
)
def test_each_objective_accepts_its_gate_filtered_winner(
    draft_receipt: Path, objective: str
) -> None:
    evidence = json.loads((draft_receipt / "evidence_record.json").read_text())
    winner = evidence["objective_rankings"][objective]["candidate_id"]

    record_human_decision(draft_receipt, _decision(winner, objective))

    assert validate_receipt(draft_receipt) == []


def test_non_winner_requires_explicit_override_without_writing(
    draft_receipt: Path,
) -> None:
    before = _snapshot(draft_receipt)

    with pytest.raises(ValueError, match="differs from the governing objective winner"):
        record_human_decision(draft_receipt, _decision("balanced_16x16"))

    assert _snapshot(draft_receipt) == before


def test_justified_objective_override_is_persisted(draft_receipt: Path) -> None:
    record_human_decision(
        draft_receipt,
        _decision(
            "balanced_16x16",
            override=True,
            override_reason="Prefer the declared baseline for this bounded teaching comparison.",
        ),
    )

    assert validate_receipt(draft_receipt) == []


def test_objective_override_reason_cannot_launder_overclaim(
    draft_receipt: Path,
) -> None:
    before = _snapshot(draft_receipt)

    with pytest.raises(ValueError, match="appears to overclaim in override_reason"):
        record_human_decision(
            draft_receipt,
            _decision(
                "balanced_16x16",
                override=True,
                override_reason="Advance this candidate to RTL.",
            ),
        )

    assert _snapshot(draft_receipt) == before
