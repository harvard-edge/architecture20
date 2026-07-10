from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from cli.arch2 import CARD_SCHEMA_PATH, ROOT, card_validation_findings


VALID_CARD_DIR = ROOT / "examples" / "design-loop-cards"
INVALID_CARD_DIR = ROOT / "tests" / "fixtures" / "cards"


def test_schema_is_valid_draft_2020_12() -> None:
    schema = json.loads(CARD_SCHEMA_PATH.read_text(encoding="utf-8"))
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
    assert card_validation_findings(VALID_CARD_DIR / filename) == []


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
