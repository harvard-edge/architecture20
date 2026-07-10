from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator

from cli.arch2 import (
    CARD_SCHEMA_PATHS,
    CARD_SCHEMA_VERSION,
    ROOT,
    card_validation_findings,
)

VALID_CARD_DIR = ROOT / "examples" / "design-loop-cards"
INVALID_CARD_DIR = ROOT / "tests" / "fixtures" / "cards"


@pytest.mark.parametrize("schema_path", CARD_SCHEMA_PATHS.values())
def test_schema_is_valid_draft_2020_12(schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize(
    "filename",
    [
        "level-0-context.yaml",
        "level-1-auditable.yaml",
        "level-2-replayable.yaml",
        "level-3-independent.yaml",
    ],
)
def test_valid_conformance_fixture(filename: str) -> None:
    path = VALID_CARD_DIR / filename
    assert (
        yaml.safe_load(path.read_text(encoding="utf-8"))["schema_version"]
        == CARD_SCHEMA_VERSION
    )
    assert card_validation_findings(path) == []


def test_legacy_v1_card_still_uses_v1_contract() -> None:
    assert card_validation_findings(INVALID_CARD_DIR / "valid-v1.0-legacy.yaml") == []


def test_explicit_legacy_contract_reports_its_own_version() -> None:
    findings = card_validation_findings(
        VALID_CARD_DIR / "level-0-context.yaml",
        schema_path=CARD_SCHEMA_PATHS["1.0"],
    )
    assert any("contract '1.0'" in finding.message for finding in findings)


def test_level_0_template_validates_after_only_level_0_fields_are_filled(
    tmp_path: Path,
) -> None:
    template_path = ROOT / "design-loop-card" / "template.yaml"
    document = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    card = document["design_loop_card"]
    assert set(card) == {
        "card_id",
        "conformance_level",
        "intent",
        "task",
        "design_space",
    }
    card["card_id"] = "starter-level-0"
    card["intent"]["objective"] = "Bound a first architecture experiment."
    card["intent"]["constraints"] = ["Hold the workload constant."]
    card["intent"]["non_goals"] = ["Authorize implementation."]
    card["design_space"]["legal"] = ["Compare two fixed candidates."]
    card["design_space"]["invalid"] = ["Change the workload."]
    card["design_space"]["deferred"] = ["Physical design."]

    completed = tmp_path / "level-0.yaml"
    completed.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    assert card_validation_findings(completed) == []


def test_start_workflow_uses_minimal_version_bounded_requirements() -> None:
    start = (ROOT / "www" / "start.qmd").read_text(encoding="utf-8")
    setup = """python3 -m venv .venv-card
.venv-card/bin/python -m pip install --upgrade pip==26.1.2
.venv-card/bin/python -m pip install -r requirements-card.txt
.venv-card/bin/python cli/arch2.py validate card my-card.yaml"""
    assert setup in start
    assert "pip install -r requirements-card.txt" in start
    assert "pip install -r requirements.txt" not in start
    assert ".venv-card/" in (ROOT / ".gitignore").read_text(encoding="utf-8")

    requirements = (ROOT / "requirements-card.txt").read_text(encoding="utf-8")
    for package in ("typer", "rich", "PyYAML", "jsonschema", "referencing"):
        line = next(
            line for line in requirements.splitlines() if line.startswith(package)
        )
        assert ">=" in line
        assert "<" in line


@pytest.mark.parametrize(
    ("filename", "message"),
    [
        ("invalid-level-1-missing-evidence.yaml", "level 1 requires 'evidence'"),
        ("invalid-level-3-dependent-gate.yaml", "True was expected"),
        ("invalid-top-level-claim.yaml", "use intent.claim_boundary.claim"),
        ("invalid-version.yaml", "unsupported schema version"),
    ],
)
def test_invalid_fixture_has_actionable_diagnostic(filename: str, message: str) -> None:
    findings = card_validation_findings(INVALID_CARD_DIR / filename)
    assert findings
    assert message in "\n".join(finding.message for finding in findings)


def test_cli_reports_success_and_failure() -> None:
    valid = subprocess.run(
        [
            sys.executable,
            str(ROOT / "cli" / "arch2.py"),
            "validate",
            "card",
            str(VALID_CARD_DIR / "level-3-independent.yaml"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert valid.returncode == 0, valid.stdout + valid.stderr
    assert "passed" in valid.stdout

    invalid = subprocess.run(
        [
            sys.executable,
            str(ROOT / "cli" / "arch2.py"),
            "validate",
            "card",
            str(INVALID_CARD_DIR / "invalid-top-level-claim.yaml"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert invalid.returncode == 1
    assert "intent.claim_boundary.claim" in re.sub(r"\s+", "", invalid.stdout)


def test_level_1_rejects_empty_load_bearing_content() -> None:
    findings = card_validation_findings(
        INVALID_CARD_DIR / "invalid-v1.1-empty-level-1.yaml"
    )
    locations = "\n".join(finding.location for finding in findings)
    for path in (
        "representation.reads",
        "representation.writes",
        "representation.uncertainties",
        "environment.actions",
        "environment.invalid_actions",
        "environment.observations",
        "method_role.actor_map",
        "feedback_budget.evaluations",
        "negative_traces",
    ):
        assert path in locations


@pytest.mark.parametrize(
    "path",
    [
        ("method_role", "actor_map", 0, "reads"),
        ("method_role", "actor_map", 0, "writes"),
        ("evidence", "records"),
    ],
)
def test_level_1_rejects_empty_nested_structures(
    tmp_path: Path, path: tuple[str | int, ...]
) -> None:
    document = yaml.safe_load(
        (VALID_CARD_DIR / "level-1-auditable.yaml").read_text(encoding="utf-8")
    )
    value = document["design_loop_card"]
    for part in path[:-1]:
        value = value[part]
    value[path[-1]] = []

    candidate = tmp_path / "empty-structure.yaml"
    candidate.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    findings = card_validation_findings(candidate)
    expected = "".join(
        f"[{part}]" if isinstance(part, int) else f".{part}" for part in path
    )
    assert any(expected in finding.location for finding in findings)


def test_level_2_requires_digest_and_replay_pointer() -> None:
    findings = card_validation_findings(
        INVALID_CARD_DIR / "invalid-v1.1-level-2-provenance.yaml"
    )
    messages = "\n".join(
        f"{finding.location} {finding.message}" for finding in findings
    )
    assert "parameter_hash" in messages
    assert "sha256:" in messages
    assert "source_uri" in messages
