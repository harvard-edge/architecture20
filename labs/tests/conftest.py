from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

from arch2_labs.receipts import sha256_file
from arch2_labs.scale_env import run_example

LAB_TEST_ROOT = Path(__file__).resolve().parent


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    if (3, 10) <= sys.version_info[:2] < (3, 12):
        return
    unsupported = pytest.mark.skip(
        reason=(
            "arch2-labs supports Python >=3.10,<3.12; "
            f"current interpreter is {sys.version_info.major}.{sys.version_info.minor}"
        )
    )
    for item in items:
        try:
            Path(item.path).resolve().relative_to(LAB_TEST_ROOT)
        except ValueError:
            continue
        item.add_marker(unsupported)


def _fake_scalesim_run(
    candidate: Any,
    topology_path: Path,
    layout_path: Path,
    candidate_dir: Path,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    del timeout_seconds
    inputs_dir = candidate_dir / "inputs"
    report_dir = candidate_dir / "scalesim-results" / candidate.candidate_id
    inputs_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)

    config = inputs_dir / "scale.cfg"
    topology = inputs_dir / "topology.csv"
    layout = inputs_dir / "layout.csv"
    config.write_text(f"candidate={candidate.candidate_id}\n")
    topology.write_bytes(topology_path.read_bytes())
    layout.write_bytes(layout_path.read_bytes())

    raw_files = []
    for name in (
        "COMPUTE_REPORT.csv",
        "BANDWIDTH_REPORT.csv",
        "DETAILED_ACCESS_REPORT.csv",
    ):
        path = report_dir / name
        path.write_text(f"fixture report for {candidate.candidate_id}\n")
        raw_files.append({"path": str(path), "sha256": sha256_file(path)})

    total_cycles = {
        "proxy_hero_64x64": 10_000,
        "throughput_32x32": 25_000,
        "balanced_16x16": 50_000,
        "tiny_8x8": 100_000,
    }[candidate.candidate_id]
    now = datetime.now(timezone.utc).isoformat()
    return {
        "candidate_id": candidate.candidate_id,
        "stage": "scalesim",
        "status": "ok",
        "command": ["python", "-m", "scalesim.scale"],
        "returncode": 0,
        "started_at": now,
        "completed_at": now,
        "tool": {"name": "SCALE-Sim", "version": "3.0.0"},
        "runtime": {"python": "3.11.test"},
        "inputs": {
            "config": str(config),
            "config_sha256": sha256_file(config),
            "topology": str(topology),
            "topology_sha256": sha256_file(topology),
            "layout": str(layout),
            "layout_sha256": sha256_file(layout),
        },
        "outputs": {"report_dir": str(report_dir), "raw_files": raw_files},
        "metrics": {
            "total_cycles": total_cycles,
            "stall_cycles": 0,
            "min_layer_util_pct": 50.0,
            "avg_layer_util_pct": 60.0,
            "avg_mapping_efficiency_pct": 60.0,
            "avg_compute_util_pct": 60.0,
            "max_observed_dram_bw_words_per_cycle": 10.0,
            "dram_reads": 100,
            "dram_writes": 50,
            "sram_reads": 500,
            "sram_writes": 250,
            "sram_accesses": 750,
            "dram_accesses": 150,
            "layers": [],
        },
    }


@pytest.fixture
def valid_receipt(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setattr("arch2_labs.scale_env.run_scalesim", _fake_scalesim_run)
    receipt_dir = tmp_path / "receipt"
    decision = {
        "schema_version": "arch2-human-decision/v0.1",
        "lab_id": "scale_proxy_mirage",
        "human_owner": "Receipt validator test author",
        "authored_at": "2026-07-10T00:00:00+00:00",
        "selected_candidate_id": "throughput_32x32",
        "governing_objective": "latency_under_declared_gates",
        "commitment_level": "next_fidelity_study",
        "rationale": "It has the lowest measured latency among candidates that pass both gates.",
        "residual_risk": "The workload and simulator omit physical effects.",
        "would_overturn": "A full workload or physical study that reverses the ranking.",
    }
    run_example(
        "scale_proxy_mirage",
        receipt_dir,
        human_decision=decision,
    )
    return receipt_dir
