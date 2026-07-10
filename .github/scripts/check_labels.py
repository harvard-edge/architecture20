#!/usr/bin/env python3
"""Ensure every issue-form and workflow label has a declared definition."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
LABEL_COLOR_RE = re.compile(r"^[0-9a-fA-F]{6}$")
ISSUE_LABEL_CONDITION_RE = re.compile(
    r"contains\(github\.event\.issue\.labels\.\*\.name,\s*['\"]([^'\"]+)['\"]\)"
)


def label_values(value: Any) -> set[str]:
    if isinstance(value, list):
        return {str(item).strip() for item in value if str(item).strip()}
    if isinstance(value, str):
        if "${{" in value:
            raise ValueError("dynamic label expressions cannot be checked statically")
        return {part.strip() for part in value.split(",") if part.strip()}
    raise ValueError(f"labels must be a string or list, not {type(value).__name__}")


def labels_in_yaml(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "labels":
                found.update(label_values(child))
            else:
                found.update(labels_in_yaml(child))
    elif isinstance(value, list):
        for child in value:
            found.update(labels_in_yaml(child))
    return found


def labels_in_file(path: Path) -> set[str]:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    labels = labels_in_yaml(data)
    labels.update(ISSUE_LABEL_CONDITION_RE.findall(text))
    return labels


def declared_labels(path: Path) -> tuple[set[str], list[str]]:
    errors: list[str] = []
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        return set(), [f"{path}: label manifest must be a list"]

    declared: set[str] = set()
    for index, item in enumerate(data, start=1):
        where = f"{path}: item {index}"
        if not isinstance(item, dict):
            errors.append(f"{where} must be a mapping")
            continue
        name = str(item.get("name", "")).strip()
        color = str(item.get("color", "")).strip()
        description = str(item.get("description", "")).strip()
        if not name:
            errors.append(f"{where} has no name")
        elif name in declared:
            errors.append(f"{where} duplicates label {name!r}")
        else:
            declared.add(name)
        if not LABEL_COLOR_RE.fullmatch(color):
            errors.append(f"{where} has invalid six-digit color {color!r}")
        if not description:
            errors.append(f"{where} has no description")
    return declared, errors


def check_labels(root: Path = ROOT) -> list[str]:
    manifest = root / ".github" / "labels.yml"
    try:
        declared, errors = declared_labels(manifest)
    except (OSError, yaml.YAMLError) as exc:
        return [f"cannot read {manifest}: {exc}"]

    used: set[str] = set()
    sources: list[Path] = []
    for directory in ("ISSUE_TEMPLATE", "workflows"):
        root_dir = root / ".github" / directory
        for pattern in ("*.yml", "*.yaml"):
            sources.extend(sorted(root_dir.glob(pattern)))
    for path in sources:
        try:
            used.update(labels_in_file(path))
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{path}: {exc}")

    for label in sorted(used - declared):
        errors.append(f"label {label!r} is used but not declared in {manifest}")
    return errors


def main() -> None:
    errors = check_labels()
    if errors:
        print("Label consistency check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("All issue-form and workflow labels are declared.")


if __name__ == "__main__":
    main()
