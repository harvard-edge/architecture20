from pathlib import Path

import pytest

from arch2_labs.scale_env import example_dir, load_workload, proxy_cycles, run_example
from arch2_labs.schemas import load_candidates
from arch2_labs.validators import validate_receipt


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
    )

    assert summary["proxy_winner"] == "proxy_hero_64x64"
    assert summary["survivor"] == "balanced_16x16"
    assert summary["rejected_count"] == 1
    assert validate_receipt(out_dir) == []


@pytest.mark.filterwarnings("ignore::DeprecationWarning")
def test_full_example_selects_budget_feasible_survivor(tmp_path: Path) -> None:
    out_dir = tmp_path / "receipt"

    summary = run_example("scale_proxy_mirage", out_dir, force=True)

    assert summary["proxy_winner"] == "proxy_hero_64x64"
    assert summary["survivor"] == "throughput_32x32"
    assert summary["rejected_count"] == 2
    assert validate_receipt(out_dir) == []
