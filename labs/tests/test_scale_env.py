import json
from pathlib import Path

import pytest

from arch2_labs.receipts import ReceiptMetadata, seal_receipt
from arch2_labs.scale_env import example_dir, load_workload, proxy_cycles, run_example
from arch2_labs.schemas import load_candidates
from arch2_labs.validators import validate_receipt


def _human_decision(candidate_id: str) -> dict[str, str]:
    return {
        "schema_version": "arch2-human-decision/v0.1",
        "lab_id": "scale_proxy_mirage",
        "human_owner": "Architecture lab test author",
        "authored_at": "2026-07-10T00:00:00+00:00",
        "selected_candidate_id": candidate_id,
        "governing_objective": "latency_under_declared_gates",
        "commitment_level": "next_fidelity_study",
        "rationale": "This candidate survives both declared gates with the lowest measured latency.",
        "residual_risk": "The compact workload omits compiler and physical-design behavior.",
        "would_overturn": "A fuller workload or physical evidence that invalidates the gate result.",
    }


def test_proxy_ranks_largest_array_first() -> None:
    ex_dir = example_dir("scale_proxy_mirage")
    spec = load_candidates(ex_dir / "configs" / "candidates.yaml", ex_dir)
    layers = load_workload(spec.topology)

    ranked = sorted(
        (proxy_cycles(candidate, layers), candidate.candidate_id)
        for candidate in spec.candidates
    )

    assert ranked[0][1] == "proxy_hero_64x64"
    assert ranked[-1][1] == "tiny_8x8"


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_run_example_and_validate_receipt(tmp_path: Path) -> None:
    out_dir = tmp_path / "receipt"

    summary = run_example(
        "scale_proxy_mirage",
        out_dir,
        force=True,
        candidate_ids={"proxy_hero_64x64", "balanced_16x16"},
        human_decision=_human_decision("balanced_16x16"),
    )

    assert summary["proxy_winner"] == "proxy_hero_64x64"
    assert summary["recommended_candidate"] == "balanced_16x16"
    assert summary["rejected_count"] == 1
    assert summary["status"] == "complete"
    assert validate_receipt(out_dir) == []

    recommendation = json.loads((out_dir / "recommendation.json").read_text())
    assert recommendation["candidate_id"] == "balanced_16x16"
    assert recommendation["human_decision"] is False

    decision = (out_dir / "decision.yaml").read_text()
    assert "Architecture lab test author" in decision
    assert "next_fidelity_study" in decision


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_full_example_recommends_budget_feasible_candidate(tmp_path: Path) -> None:
    out_dir = tmp_path / "receipt"

    summary = run_example(
        "scale_proxy_mirage",
        out_dir,
        force=True,
        human_decision=_human_decision("throughput_32x32"),
    )

    assert summary["proxy_winner"] == "proxy_hero_64x64"
    assert summary["recommended_candidate"] == "throughput_32x32"
    assert summary["rejected_count"] == 2
    assert validate_receipt(out_dir) == []


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_run_without_human_decision_emits_noncommitting_draft(tmp_path: Path) -> None:
    out_dir = tmp_path / "receipt"

    summary = run_example(
        "scale_proxy_mirage",
        out_dir,
        candidate_ids={"proxy_hero_64x64", "balanced_16x16"},
    )

    assert summary["status"] == "awaiting_human_decision"
    assert (out_dir / "recommendation.json").is_file()
    assert not (out_dir / "decision.yaml").exists()
    assert not (out_dir / "decision.md").exists()
    assert "receipt awaits a required human decision" in validate_receipt(out_dir)


def test_force_failure_preserves_existing_owned_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out_dir = tmp_path / "receipt"
    out_dir.mkdir()
    sentinel = out_dir / "previous-result.txt"
    sentinel.write_text("preserve on generation failure\n")
    seal_receipt(
        out_dir,
        ReceiptMetadata(
            receipt_id="previous-receipt",
            lab_id="scale_proxy_mirage",
            example="scale_proxy_mirage",
            created_at="2026-07-10T00:00:00+00:00",
            status="awaiting_human_decision",
        ),
    )

    def fail_run(*args: object, **kwargs: object) -> dict[str, object]:
        raise RuntimeError("simulator failed")

    monkeypatch.setattr("arch2_labs.scale_env.run_scalesim", fail_run)

    with pytest.raises(RuntimeError, match="simulator failed"):
        run_example("scale_proxy_mirage", out_dir, force=True)

    assert sentinel.read_text() == "preserve on generation failure\n"
