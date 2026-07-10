from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from arch2_labs.scale_env import example_dir, load_workload, run_example
from arch2_labs.schemas import load_candidates


@pytest.fixture
def example_config() -> tuple[Path, dict[str, object]]:
    root = example_dir("scale_proxy_mirage")
    return root, yaml.safe_load((root / "configs" / "candidates.yaml").read_text())


def _write_config(tmp_path: Path, data: dict[str, object]) -> Path:
    path = tmp_path / "candidates.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False))
    return path


@pytest.mark.parametrize(
    "name", ["../scale_proxy_mirage", "scale_proxy_mirage/..", "/tmp/example", "."]
)
def test_example_dir_rejects_traversal(name: str) -> None:
    with pytest.raises(ValueError, match="safe slug"):
        example_dir(name)


@pytest.mark.parametrize("field", ["topology", "layout"])
def test_load_candidates_rejects_paths_outside_example(
    tmp_path: Path,
    example_config: tuple[Path, dict[str, object]],
    field: str,
) -> None:
    root, original = example_config
    data = deepcopy(original)
    data[field] = "../../outside.csv"

    with pytest.raises(ValueError, match=f"{field} must resolve under the example"):
        load_candidates(_write_config(tmp_path, data), root)


def test_load_candidates_rejects_duplicate_ids(
    tmp_path: Path, example_config: tuple[Path, dict[str, object]]
) -> None:
    root, original = example_config
    data = deepcopy(original)
    data["candidates"][1]["candidate_id"] = data["candidates"][0]["candidate_id"]

    with pytest.raises(ValueError, match="candidate IDs must be unique"):
        load_candidates(_write_config(tmp_path, data), root)


@pytest.mark.parametrize("candidate_id", ["../escape", "bad/id", "UPPER", " space"])
def test_load_candidates_rejects_unsafe_candidate_ids(
    tmp_path: Path,
    example_config: tuple[Path, dict[str, object]],
    candidate_id: str,
) -> None:
    root, original = example_config
    data = deepcopy(original)
    data["candidates"][0]["candidate_id"] = candidate_id

    with pytest.raises(ValueError, match="candidate_id must be a safe slug"):
        load_candidates(_write_config(tmp_path, data), root)


@pytest.mark.parametrize(
    "field,bad_value",
    [
        ("array_rows", 0),
        ("array_cols", -1),
        ("sram_kb", 0),
        ("dram_bandwidth_words_per_cycle", 0),
        ("clock_mhz", 0),
        ("area_budget_pes", -1),
        ("deadline_cycles", 0),
        ("min_layer_util_pct", 0),
        ("min_layer_util_pct", 101),
    ],
)
def test_load_candidates_rejects_invalid_numeric_bounds(
    tmp_path: Path,
    example_config: tuple[Path, dict[str, object]],
    field: str,
    bad_value: int,
) -> None:
    root, original = example_config
    data = deepcopy(original)
    data["candidates"][0][field] = bad_value

    with pytest.raises(ValueError, match=field):
        load_candidates(_write_config(tmp_path, data), root)


def test_load_candidates_requires_declared_baseline(
    tmp_path: Path, example_config: tuple[Path, dict[str, object]]
) -> None:
    root, original = example_config
    data = deepcopy(original)
    data["baseline_id"] = "missing_baseline"

    with pytest.raises(ValueError, match="baseline_id must name a declared candidate"):
        load_candidates(_write_config(tmp_path, data), root)


def test_run_requires_baseline_in_selected_candidates(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="selected candidates must include baseline"):
        run_example(
            "scale_proxy_mirage",
            tmp_path / "receipt",
            candidate_ids={"proxy_hero_64x64", "throughput_32x32"},
        )


def test_run_rejects_unknown_selected_candidate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown candidate IDs"):
        run_example(
            "scale_proxy_mirage",
            tmp_path / "receipt",
            candidate_ids={"balanced_16x16", "not_declared"},
        )


def test_run_rejects_unsafe_selected_candidate(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="selected candidate ID must be a safe slug"):
        run_example(
            "scale_proxy_mirage",
            tmp_path / "receipt",
            candidate_ids={"balanced_16x16", "../escape"},
        )


def test_load_workload_requires_positive_dimensions(tmp_path: Path) -> None:
    topology = tmp_path / "bad.csv"
    topology.write_text("Layer,M,N,K,Sparsity\nbad,32,0,64,1:1\n")

    with pytest.raises(ValueError, match="dimensions must be positive"):
        load_workload(topology)
