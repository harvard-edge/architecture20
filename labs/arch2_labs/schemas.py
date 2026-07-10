from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")


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
    baseline_id: str
    candidates: tuple[Candidate, ...]


def require_safe_slug(value: Any, field: str) -> str:
    if not isinstance(value, str) or not SAFE_SLUG.fullmatch(value):
        raise ValueError(
            f"{field} must be a safe slug containing lowercase letters, digits, "
            "underscores, or hyphens"
        )
    return value


def _resolve_example_file(example_dir: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field} must be a nonempty relative path")
    relative = Path(value)
    if relative.is_absolute():
        raise ValueError(f"{field} must resolve under the example directory")
    root = example_dir.resolve()
    resolved = (root / relative).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"{field} must resolve under the example directory") from exc
    if not resolved.is_file():
        raise ValueError(f"{field} does not name an example file: {value}")
    return resolved


def _validate_candidate(entry: Any, index: int) -> Candidate:
    if not isinstance(entry, Mapping):
        raise ValueError(f"candidate {index} must be a mapping")
    candidate_id = require_safe_slug(entry.get("candidate_id"), "candidate_id")
    for field in (
        "array_rows",
        "array_cols",
        "sram_kb",
        "dram_bandwidth_words_per_cycle",
        "clock_mhz",
        "area_budget_pes",
        "deadline_cycles",
    ):
        value = entry.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(
                f"candidate {candidate_id} field {field} must be a positive integer"
            )
    utilization = entry.get("min_layer_util_pct")
    if (
        isinstance(utilization, bool)
        or not isinstance(utilization, (int, float))
        or not 0 < utilization <= 100
    ):
        raise ValueError(
            f"candidate {candidate_id} field min_layer_util_pct must be in (0, 100]"
        )
    for field in ("label", "source", "dataflow"):
        if not isinstance(entry.get(field), str) or not entry[field].strip():
            raise ValueError(
                f"candidate {candidate_id} field {field} must be a nonempty string"
            )
    try:
        return Candidate(**entry)
    except TypeError as exc:
        raise ValueError(f"candidate {candidate_id} has invalid fields: {exc}") from exc


def load_candidates(config_path: Path, example_dir: Path) -> ExampleSpec:
    data = yaml.safe_load(config_path.read_text())
    if not isinstance(data, Mapping):
        raise ValueError("candidate config must contain a mapping")
    entries = data.get("candidates")
    if not isinstance(entries, list) or not entries:
        raise ValueError("candidate config must declare at least one candidate")
    candidates = tuple(
        _validate_candidate(entry, index) for index, entry in enumerate(entries)
    )
    candidate_ids = [candidate.candidate_id for candidate in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ValueError("candidate IDs must be unique")
    baseline_id = require_safe_slug(data.get("baseline_id"), "baseline_id")
    if baseline_id not in candidate_ids:
        raise ValueError("baseline_id must name a declared candidate")
    return ExampleSpec(
        lab_id=require_safe_slug(data.get("lab_id"), "lab_id"),
        title=data["title"],
        topology=_resolve_example_file(example_dir, data.get("topology"), "topology"),
        layout=_resolve_example_file(example_dir, data.get("layout"), "layout"),
        baseline_id=baseline_id,
        candidates=candidates,
    )
