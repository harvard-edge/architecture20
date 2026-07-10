from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class WorkloadLayer:
    name: str
    m: int
    n: int
    k: int
    sparsity: str = "1:1"

    @property
    def macs(self) -> int:
        return self.m * self.n * self.k


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    label: str
    source: str
    array_rows: int
    array_cols: int
    dataflow: str
    sram_kb: int
    dram_bandwidth_words_per_cycle: int
    clock_mhz: int
    area_budget_pes: int
    deadline_cycles: int
    min_layer_util_pct: float

    @property
    def pe_count(self) -> int:
        return self.array_rows * self.array_cols

    def action_dict(self) -> dict[str, Any]:
        return {
            "array_rows": self.array_rows,
            "array_cols": self.array_cols,
            "dataflow": self.dataflow,
            "sram_kb_each": self.sram_kb,
            "dram_bandwidth_words_per_cycle": self.dram_bandwidth_words_per_cycle,
        }


@dataclass(frozen=True)
class ExampleSpec:
    lab_id: str
    title: str
    topology: Path
    layout: Path
    candidates: tuple[Candidate, ...]


def load_candidates(config_path: Path, example_dir: Path) -> ExampleSpec:
    data = yaml.safe_load(config_path.read_text())
    candidates = tuple(Candidate(**entry) for entry in data["candidates"])
    return ExampleSpec(
        lab_id=data["lab_id"],
        title=data["title"],
        topology=example_dir / data["topology"],
        layout=example_dir / data["layout"],
        candidates=candidates,
    )
