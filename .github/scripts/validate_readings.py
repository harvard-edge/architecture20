#!/usr/bin/env python3
"""Validate www/readings.yml so reading cards render consistently."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from reading_common import (
    ALLOWED_READING_CATEGORIES,
    ALLOWED_RESOURCE_TYPES,
    READINGS_DIR,
)

REQUIRED = ("title", "url", "kind", "description", "categories")


def load_readings() -> list[tuple[Path, dict]]:
    paths = sorted(Path(READINGS_DIR).glob("*.yml"))
    readings: list[tuple[Path, dict]] = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            item = yaml.safe_load(handle) or {}
        readings.append((path, item))
    return readings


def main() -> int:
    readings = load_readings()
    if not readings:
        print(f"{READINGS_DIR}: no reading resource files found")
        return 1

    errors: list[str] = []
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()

    for path, reading in readings:
        where = f"{path} ({reading.get('title', '?') if isinstance(reading, dict) else '?'})"
        if not isinstance(reading, dict):
            errors.append(f"{where}: not a mapping")
            continue

        for key in REQUIRED:
            if not reading.get(key):
                errors.append(f"{where}: missing '{key}'")

        url = reading.get("url", "") or ""
        if url and not url.startswith(("http://", "https://")):
            errors.append(f"{where}: url must start with http:// or https://")

        kind = reading.get("kind", "") or ""
        if kind and kind not in ALLOWED_RESOURCE_TYPES:
            errors.append(
                f"{where}: kind '{kind}' not in allowed set "
                f"({', '.join(ALLOWED_RESOURCE_TYPES)})"
            )

        categories = reading.get("categories") or []
        if not isinstance(categories, list):
            errors.append(f"{where}: 'categories' must be a list")
        else:
            for category in categories:
                if category not in ALLOWED_READING_CATEGORIES:
                    errors.append(
                        f"{where}: category '{category}' not in allowed set "
                        f"({', '.join(ALLOWED_READING_CATEGORIES)})"
                    )

        title_key = (reading.get("title") or "").lower()
        if title_key:
            if title_key in seen_titles:
                errors.append(f"{where}: duplicate title")
            seen_titles.add(title_key)

        if url:
            if url in seen_urls:
                errors.append(f"{where}: duplicate url")
            seen_urls.add(url)

    if errors:
        print(f"Reading validation FAILED ({len(errors)} problem(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Reading list OK: {len(readings)} resources, all categories within the allowed set."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
