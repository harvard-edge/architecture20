#!/usr/bin/env python3
"""Validate tools/tools.yml so the tool registry never breaks the site.

Checks that every entry has the required fields, that every category is in the
allowed set (keeps the filter from fragmenting), that URLs are well-formed, and
that there are no duplicate titles or URLs. Exits non-zero on any problem so CI
can block a bad submission before it merges.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

from catalog_common import ALLOWED_CATEGORIES, ALLOWED_STATUSES, CATALOG_DIR

REQUIRED = ("title", "url", "description", "categories")


def main() -> int:
    paths = sorted(Path(CATALOG_DIR).glob("*.yml"))
    if not paths:
        print(f"{CATALOG_DIR}: no tool files found")
        return 1

    errors: list[str] = []
    seen_titles: set[str] = set()
    seen_urls: set[str] = set()

    for path in paths:
        with path.open(encoding="utf-8") as handle:
            tool = yaml.safe_load(handle) or {}

        where = f"{path} ({tool.get('title', '?') if isinstance(tool, dict) else '?'})"
        if not isinstance(tool, dict):
            errors.append(f"{where}: not a mapping")
            continue

        for key in REQUIRED:
            if not tool.get(key):
                errors.append(f"{where}: missing '{key}'")

        url = tool.get("url", "") or ""
        if url and not url.startswith(("http://", "https://")):
            errors.append(f"{where}: url must start with http:// or https://")

        paper_url = tool.get("paper_url", "") or ""
        if paper_url and not paper_url.startswith(("http://", "https://")):
            errors.append(f"{where}: paper_url must start with http:// or https://")

        status = tool.get("status", "") or ""
        if status and status not in ALLOWED_STATUSES:
            errors.append(
                f"{where}: status '{status}' not in allowed set "
                f"({', '.join(ALLOWED_STATUSES)})"
            )

        categories = tool.get("categories") or []
        if not isinstance(categories, list):
            errors.append(f"{where}: 'categories' must be a list")
        else:
            for category in categories:
                if category not in ALLOWED_CATEGORIES:
                    errors.append(
                        f"{where}: category '{category}' not in allowed set "
                        f"({', '.join(ALLOWED_CATEGORIES)})"
                    )

        title_key = (tool.get("title") or "").lower()
        if title_key:
            if title_key in seen_titles:
                errors.append(f"{where}: duplicate title")
            seen_titles.add(title_key)
        if url:
            if url in seen_urls:
                errors.append(f"{where}: duplicate url")
            seen_urls.add(url)

    if errors:
        print(f"Tool registry validation FAILED ({len(errors)} problem(s)):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(
        f"Tool registry OK: {len(paths)} tools, all categories within the allowed set."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
