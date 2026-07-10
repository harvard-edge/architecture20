from __future__ import annotations

import datetime as dt
from pathlib import Path

import yaml

from tools.render_awesome import OUTPUT_PATH, render
from tools.validate_registries import (
    ROOT,
    TOOL_DIR,
    WORKSHOP_DIR,
    WORKSHOP_SCHEMA,
    TOOL_SCHEMA,
    _schema_errors,
    _semantic_errors,
    validate,
)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def test_registry_contracts_and_generated_indexes_are_current() -> None:
    assert validate() == []


def test_every_tool_exposes_availability_and_verification_date() -> None:
    for path in TOOL_DIR.glob("*.yml"):
        tool = _load(path)
        assert tool["artifact_availability"]
        assert tool["last_verified"]


def test_unverified_tool_uses_explicit_null_date(tmp_path: Path) -> None:
    tool = {
        "title": "Unverified test",
        "url": "https://example.com/tool",
        "artifact_type": "Tool",
        "categories": ["Simulation"],
        "description": "A fixture for the unverified state.",
        "fit_note": "Exercises availability validation.",
        "artifact_availability": "unverified",
    }
    path = tmp_path / "unverified.yml"
    path.write_text(yaml.safe_dump(tool), encoding="utf-8")
    assert _schema_errors(path, TOOL_SCHEMA) == []

    tool["last_verified"] = "2026-07-10"
    path.write_text(yaml.safe_dump(tool), encoding="utf-8")
    assert _schema_errors(path, TOOL_SCHEMA)


def test_apollo_uses_reachable_authoritative_paper_record() -> None:
    apollo = _load(TOOL_DIR / "apollo.yml")
    assert apollo["url"] == "https://arxiv.org/abs/2102.01723"
    assert apollo["artifact_availability"] == "paper_only"


def test_all_current_workshops_are_archived_without_submission_links() -> None:
    workshops = [_load(path) for path in WORKSHOP_DIR.glob("*.yml")]
    assert workshops
    assert all(item["status"] == "archived" for item in workshops)
    assert all("submission_url" not in item for item in workshops)


def test_expired_active_workshop_is_rejected(tmp_path: Path) -> None:
    workshop = {
        "title": "Expired test",
        "url": "https://example.com/event",
        "venue": "Test",
        "when": "2000",
        "event_start": "2000-01-01",
        "event_end": "2000-01-02",
        "status": "active",
        "last_verified": dt.date.today().isoformat(),
        "description": "Expired active fixture.",
        "categories": ["Architecture 2.0"],
    }
    path = tmp_path / "expired.yml"
    path.write_text(yaml.safe_dump(workshop), encoding="utf-8")
    errors = _semantic_errors([], [path])
    assert any("active workshop ended" in error for error in errors)


def test_archived_workshop_cannot_retain_submission_link(tmp_path: Path) -> None:
    workshop = {
        "title": "Archived test",
        "url": "https://example.com/event",
        "venue": "Test",
        "when": "2000",
        "event_end": "2000-01-02",
        "status": "archived",
        "last_verified": "2026-07-10",
        "description": "Archived fixture.",
        "categories": ["Architecture 2.0"],
        "submission_url": "https://example.com/closed",
    }
    path = tmp_path / "archived.yml"
    path.write_text(yaml.safe_dump(workshop), encoding="utf-8")
    assert _schema_errors(path, WORKSHOP_SCHEMA)


def test_awesome_is_generated_from_registry() -> None:
    assert OUTPUT_PATH.read_text(encoding="utf-8") == render()
