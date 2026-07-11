from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from arch2_labs.environment import (
    load_environment_contract,
    rejection_threshold,
    validate_action,
)
from arch2_labs.scale_env import example_dir


def _canonical_contract() -> dict:
    path = example_dir("scale_proxy_mirage") / "starter_receipt" / "environment.yaml"
    return load_environment_contract(path)


def test_canonical_environment_contract_accepts_declared_action() -> None:
    contract = _canonical_contract()
    action = {
        "array_rows": 32,
        "array_cols": 32,
        "dataflow": "ws",
        "sram_kb_each": 128,
        "dram_bandwidth_words_per_cycle": 64,
    }

    assert validate_action(contract, action) == []


def test_environment_contract_reports_each_action_boundary() -> None:
    contract = _canonical_contract()
    action = {
        "array_rows": 128,
        "array_cols": 32,
        "dataflow": "os",
        "sram_kb_each": 128,
        "extra": "undeclared",
    }

    errors = validate_action(contract, action)

    assert any("array_rows=128" in error for error in errors)
    assert any("dataflow='os'" in error for error in errors)
    assert any("dram_bandwidth_words_per_cycle is missing" in error for error in errors)
    assert any("extra is not a declared action field" in error for error in errors)


def test_environment_contract_exposes_declared_rejection_thresholds() -> None:
    contract = _canonical_contract()

    assert rejection_threshold(contract, "area_budget_pes") == 1024
    assert rejection_threshold(contract, "deadline_cycles") == 90000
    with pytest.raises(ValueError, match="does not declare gate"):
        rejection_threshold(contract, "utilization")


def test_environment_contract_requires_review_surface(tmp_path: Path) -> None:
    path = tmp_path / "environment.yaml"
    path.write_text(yaml.safe_dump({"schema_version": "test"}))

    with pytest.raises(ValueError, match="missing required fields"):
        load_environment_contract(path)


def test_environment_action_sets_must_be_nonempty_lists() -> None:
    contract = _canonical_contract()
    contract["legal_actions"]["array_rows"] = []

    with pytest.raises(ValueError, match="must be a nonempty list"):
        validate_action(contract, {"array_rows": 32})


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("observations", [], "observations must contain a nonempty mapping"),
        ("invalid_actions", {}, "invalid_actions must be a nonempty string list"),
        ("provenance", [], "provenance must contain a nonempty mapping"),
        (
            "rejection_authority",
            [{"gate": "deadline_cycles", "threshold": "fast"}],
            "has no numeric threshold",
        ),
    ],
)
def test_environment_contract_rejects_malformed_review_fields(
    tmp_path: Path, field: str, value: object, message: str
) -> None:
    contract = _canonical_contract()
    contract[field] = value
    path = tmp_path / "environment.yaml"
    path.write_text(yaml.safe_dump(contract, sort_keys=False))

    with pytest.raises(ValueError, match=message):
        load_environment_contract(path)


def test_environment_contract_rejects_duplicate_gates(tmp_path: Path) -> None:
    contract = _canonical_contract()
    contract["rejection_authority"].append(
        {"gate": "deadline_cycles", "threshold": 100000}
    )
    path = tmp_path / "environment.yaml"
    path.write_text(yaml.safe_dump(contract, sort_keys=False))

    with pytest.raises(ValueError, match="repeats gate: deadline_cycles"):
        load_environment_contract(path)
