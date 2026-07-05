#!/usr/bin/env python3
"""Validate www/workshops.yml so workshop cards render consistently."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from workshop_common import ALLOWED_WORKSHOP_CATEGORIES, WORKSHOPS_DIR

REQUIRED = ("title", "url", "venue", "when", "description", "categories")


def main() -> int:
    paths = sorted(Path(WORKSHOPS_DIR).glob("*.yml"))
    if not paths:
        print(f"{WORKSHOPS_DIR}: no workshop files found")
        return 1

    errors: list[str] = []
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()

    for path in paths:
        with path.open(encoding="utf-8") as handle:
            workshop = yaml.safe_load(handle) or {}

        where = f"{path} ({workshop.get('title', '?') if isinstance(workshop, dict) else '?'})"
        if not isinstance(workshop, dict):
            errors.append(f"{where}: not a mapping")
            continue

        for key in REQUIRED:
            if not workshop.get(key):
                errors.append(f"{where}: missing '{key}'")

        for key in ("url", "submission_url"):
            value = workshop.get(key, "") or ""
            if value and not value.startswith(("http://", "https://")):
                errors.append(f"{where}: {key} must start with http:// or https://")

        categories = workshop.get("categories") or []
        if not isinstance(categories, list):
            errors.append(f"{where}: 'categories' must be a list")
        else:
            for category in categories:
                if category not in ALLOWED_WORKSHOP_CATEGORIES:
                    errors.append(
                        f"{where}: category '{category}' not in allowed set "
                        f"({', '.join(ALLOWED_WORKSHOP_CATEGORIES)})"
                    )

        history = workshop.get("history") or []
        if history and not isinstance(history, list):
            errors.append(f"{where}: 'history' must be a list")
        else:
            for history_index, event in enumerate(history):
                event_where = f"{where}: history {history_index}"
                if not isinstance(event, dict):
                    errors.append(f"{event_where}: not a mapping")
                    continue
                for key in ("label", "url"):
                    if not event.get(key):
                        errors.append(f"{event_where}: missing '{key}'")
                event_url = event.get("url", "") or ""
                if event_url and not event_url.startswith(("http://", "https://")):
                    errors.append(
                        f"{event_where}: url must start with http:// or https://"
                    )

        title_key = (workshop.get("title") or "").lower()
        if title_key:
            if title_key in seen_titles:
                errors.append(f"{where}: duplicate title")
            seen_titles.add(title_key)

        url = workshop.get("url", "") or ""
        if url:
            if url in seen_urls:
                errors.append(f"{where}: duplicate url")
            seen_urls.add(url)

    if errors:
        print(f"Workshop validation FAILED ({len(errors)} problem(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Workshop registry OK: {len(paths)} workshops, all categories within the allowed set."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
