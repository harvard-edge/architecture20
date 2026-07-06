#!/usr/bin/env python3
"""Validate tools/tools.yml so the tool registry never breaks the site.

Checks that every entry has the required fields, that every category is in the
allowed set (keeps the filter from fragmenting), that URLs are well-formed, and
that there are no duplicate titles or URLs. Exits non-zero on any problem so CI
can block a bad submission before it merges.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import yaml

from catalog_common import (
    ALLOWED_ARTIFACT_TYPES,
    ALLOWED_CATEGORIES,
    ALLOWED_STATUSES,
    CATALOG_DIR,
    DESCRIPTION_MAX_CHARS,
    FIT_NOTE_MAX_CHARS,
    OPTIONAL_URL_FIELDS,
    TRIAGE_CATEGORY,
    is_http_url,
    one_line,
    tag_errors,
)

REQUIRED = ("title", "url", "artifact_type", "description", "fit_note", "categories")


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
        if url and not is_http_url(url):
            errors.append(f"{where}: url must start with http:// or https://")

        artifact_type = tool.get("artifact_type", "") or ""
        if artifact_type and artifact_type not in ALLOWED_ARTIFACT_TYPES:
            errors.append(
                f"{where}: artifact_type '{artifact_type}' not in allowed set "
                f"({', '.join(ALLOWED_ARTIFACT_TYPES)})"
            )

        for field in OPTIONAL_URL_FIELDS:
            value = tool.get(field, "") or ""
            if value and not is_http_url(value):
                errors.append(f"{where}: {field} must start with http:// or https://")

        description = one_line(tool.get("description", "") or "")
        if description and len(description) > DESCRIPTION_MAX_CHARS:
            errors.append(
                f"{where}: description is {len(description)} chars; "
                f"maximum is {DESCRIPTION_MAX_CHARS}"
            )

        fit_note = one_line(tool.get("fit_note", "") or "")
        if fit_note and len(fit_note) > FIT_NOTE_MAX_CHARS:
            errors.append(
                f"{where}: fit_note is {len(fit_note)} chars; "
                f"maximum is {FIT_NOTE_MAX_CHARS}"
            )

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
            if len(categories) != 1:
                errors.append(
                    f"{where}: use exactly one primary category; use tags for "
                    "secondary labels"
                )
            for category in categories:
                allowed = category in ALLOWED_CATEGORIES
                triage_allowed = (
                    category == TRIAGE_CATEGORY
                    and os.environ.get("ARCH2_ALLOW_TRIAGE_CATEGORY") == "1"
                )
                if not (allowed or triage_allowed):
                    errors.append(
                        f"{where}: category '{category}' not in allowed set "
                        f"({', '.join(ALLOWED_CATEGORIES)})"
                    )

        tags = tool.get("tags") or []
        for error in tag_errors(tags):
            errors.append(f"{where}: {error}")

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
