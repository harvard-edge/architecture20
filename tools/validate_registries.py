#!/usr/bin/env python3
"""Validate source registries and their generated indexes."""

from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TOOL_DIR = ROOT / "tools" / "registry"
TOOL_SCHEMA = ROOT / "tools" / "schemas" / "tool.schema.json"
TOOL_INDEX = ROOT / "tools" / "tools.yml"
WORKSHOP_DIR = ROOT / "www" / "workshops"
WORKSHOP_SCHEMA = ROOT / "www" / "schemas" / "workshop.schema.json"
WORKSHOP_INDEX = ROOT / "www" / "workshops.yml"


def _load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _normalize_dates(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _normalize_dates(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normalize_dates(item) for item in value]
    return value


def _json_path(parts: list[Any]) -> str:
    path = "$"
    for part in parts:
        path += f"[{part}]" if isinstance(part, int) else f".{part}"
    return path


def _schema_errors(path: Path, schema_path: Path) -> list[str]:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    document = _normalize_dates(_load_yaml(path))
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    relative = _display_path(path)
    return [
        f"{relative}:{_json_path(list(error.absolute_path))}: {error.message}"
        for error in errors
    ]


def _duplicate_errors(paths: list[Path], fields: tuple[str, ...]) -> list[str]:
    errors: list[str] = []
    for field in fields:
        seen: dict[str, Path] = {}
        for path in paths:
            document = _load_yaml(path) or {}
            value = str(document.get(field, "")).strip().lower()
            if not value:
                continue
            if value in seen:
                errors.append(
                    f"{_display_path(path)}: duplicate {field} also used by "
                    f"{_display_path(seen[value])}"
                )
            else:
                seen[value] = path
    return errors


def _date_value(value: Any) -> dt.date | None:
    if isinstance(value, dt.datetime):
        return value.date()
    if isinstance(value, dt.date):
        return value
    if isinstance(value, str):
        try:
            return dt.date.fromisoformat(value)
        except ValueError:
            return None
    return None


def _semantic_errors(tool_paths: list[Path], workshop_paths: list[Path]) -> list[str]:
    errors: list[str] = []
    today = dt.date.today()

    for path in tool_paths:
        item = _load_yaml(path) or {}
        verified = _date_value(item.get("last_verified"))
        if verified and verified > today:
            errors.append(f"{_display_path(path)}: last_verified is in the future")
        if item.get("artifact_availability") == "runnable" and not item.get(
            "verification_note"
        ):
            errors.append(
                f"{_display_path(path)}: runnable entries require a verification_note"
            )

    for path in workshop_paths:
        item = _load_yaml(path) or {}
        verified = _date_value(item.get("last_verified"))
        event_end = _date_value(item.get("event_end"))
        if verified and verified > today:
            errors.append(f"{_display_path(path)}: last_verified is in the future")
        if item.get("status") == "active" and event_end and event_end < today:
            errors.append(
                f"{_display_path(path)}: active workshop ended on {event_end}; archive or update it"
            )
    return errors


def _expected_index(paths: list[Path]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for path in paths:
        item = _load_yaml(path) or {}
        item.setdefault("source_file", path.name)
        items.append(item)
    return sorted(
        items, key=lambda item: (item.get("order", 9999), item.get("title", ""))
    )


def _index_errors(paths: list[Path], index_path: Path) -> list[str]:
    if not index_path.exists():
        return [f"{index_path.relative_to(ROOT)}: generated index is missing"]
    actual = _load_yaml(index_path)
    expected = _expected_index(paths)
    if actual == expected:
        return []
    return [
        f"{index_path.relative_to(ROOT)}: generated index is stale; rebuild it from source entries"
    ]


def validate() -> list[str]:
    tool_paths = sorted(TOOL_DIR.glob("*.yml"))
    workshop_paths = sorted(WORKSHOP_DIR.glob("*.yml"))
    errors: list[str] = []
    if not tool_paths:
        errors.append("tools/registry: no source entries found")
    if not workshop_paths:
        errors.append("www/workshops: no source entries found")
    for path in tool_paths:
        errors.extend(_schema_errors(path, TOOL_SCHEMA))
    for path in workshop_paths:
        errors.extend(_schema_errors(path, WORKSHOP_SCHEMA))
    errors.extend(_duplicate_errors(tool_paths, ("title", "url")))
    errors.extend(_duplicate_errors(workshop_paths, ("title", "url")))
    errors.extend(_semantic_errors(tool_paths, workshop_paths))
    errors.extend(_index_errors(tool_paths, TOOL_INDEX))
    errors.extend(_index_errors(workshop_paths, WORKSHOP_INDEX))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print(f"Registry contract validation FAILED ({len(errors)} problem(s))")
        for error in errors:
            print(f"  - {error}")
        return 1
    tool_count = len(list(TOOL_DIR.glob("*.yml")))
    workshop_count = len(list(WORKSHOP_DIR.glob("*.yml")))
    print(f"Registry contracts OK: {tool_count} tools, {workshop_count} workshops")
    return 0


if __name__ == "__main__":
    sys.exit(main())
