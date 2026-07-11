from __future__ import annotations

import importlib.util
from pathlib import Path

NOTEBOOKS = [
    Path("examples/scale_proxy_mirage/lab.py"),
    Path("notebooks/lab_01_prompt_to_card.py"),
    Path("notebooks/lab_02_scissors_gap.py"),
]


def test_marimo_notebooks_import() -> None:
    labs_root = Path(__file__).resolve().parents[1]
    for index, notebook in enumerate(NOTEBOOKS):
        path = labs_root / notebook
        spec = importlib.util.spec_from_file_location(f"arch2_notebook_{index}", path)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        assert module.app is not None


def test_prompt_bootstrap_does_not_claim_canonical_completion() -> None:
    source = Path("notebooks/lab_01_prompt_to_card.py").read_text()

    assert "Four-field bootstrap complete" in source
    assert "not a complete canonical design-loop card" in source
    assert "Card complete" not in source


def test_proxy_lab_persists_explicit_learner_decision() -> None:
    source = Path("examples/scale_proxy_mirage/lab.py").read_text()

    assert "record_human_decision" in source
    assert "render_objective_summary" in source
    assert "render_receipt_validation" in source
    assert '"selected_candidate_id": choice.value' in source
    assert '"governing_objective": objective.value' in source
    assert '"rationale": rationale.value.strip()' in source
    assert "Rationale (optional)" not in source
    assert "gate_survivor" not in source
    assert "SCALE-Sim v2" not in source


def test_scissors_gap_separates_queue_load_from_search_effort() -> None:
    source = Path("notebooks/lab_02_scissors_gap.py").read_text()

    assert "offered_load = proposal_rate / adjudication_capacity" in source
    assert "queue_growth = max(0.0, proposal_rate - adjudication_capacity)" in source
    assert "trusted_throughput = min(proposal_rate, adjudication_capacity)" in source
    assert "evaluations_to_target" in source
    assert "generated candidates wait behind" not in source
    assert "Only raising" not in source
    assert "this book's remedy buys them little" not in source
    assert "return (warmup_unlocked,)" in source
    assert "return (prediction_locked,)" in source
    assert "return (investment_committed,)" in source
