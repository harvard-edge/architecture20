#!/usr/bin/env python3
"""Append a resource to www/readings.yml from a resource issue form."""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

from build_readings_index import main as build_readings_index
from github_output import emit_outputs as emit
from reading_common import (
    ALLOWED_READING_CATEGORIES,
    ALLOWED_RESOURCE_TYPES,
    READINGS_DIR,
    slugify,
)

LABELS = {
    "title": "Resource title",
    "url": "URL",
    "kind": "Resource type",
    "venue": "Venue or source",
    "date": "Date or year",
    "authors": "Author(s)",
    "doi": "DOI",
    "category": "Primary topic",
    "description": "Short description",
}


def field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, body, re.S | re.M)
    if not match:
        return ""
    value = match.group(1).strip()
    return "" if value in ("_No response_", "No response") else value


def fail(reason: str) -> None:
    print(f"Resource submission rejected: {reason}")
    emit(success="false", reason=reason)


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "").replace("\r\n", "\n")

    title = field(body, LABELS["title"])
    url = field(body, LABELS["url"])
    kind = field(body, LABELS["kind"])
    venue = field(body, LABELS["venue"])
    when = field(body, LABELS["date"])
    authors = field(body, LABELS["authors"])
    doi = field(body, LABELS["doi"])
    category = field(body, LABELS["category"])
    description = field(body, LABELS["description"])

    missing = [
        human
        for key, human in (
            ("title", "resource title"),
            ("url", "URL"),
            ("kind", "resource type"),
            ("category", "primary topic"),
            ("description", "short description"),
        )
        if not {
            "title": title,
            "url": url,
            "kind": kind,
            "category": category,
            "description": description,
        }[key]
    ]
    if missing:
        return fail(f"missing required field(s): {', '.join(missing)}")

    if not re.match(r"^https?://", url):
        return fail("the URL must start with http:// or https://")
    if kind not in ALLOWED_RESOURCE_TYPES:
        return fail(
            f"resource type '{kind}' is not one of: {', '.join(ALLOWED_RESOURCE_TYPES)}"
        )
    if category not in ALLOWED_READING_CATEGORIES:
        return fail(
            f"primary topic '{category}' is not one of: "
            f"{', '.join(ALLOWED_READING_CATEGORIES)}"
        )

    paths = sorted(Path(READINGS_DIR).glob("*.yml"))
    readings = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            item = yaml.safe_load(handle) or {}
        if isinstance(item, dict):
            readings.append(item)

    if any((item.get("title") or "").lower() == title.lower() for item in readings):
        return fail(f"a resource named '{title}' is already in the reading list")
    if any(item.get("url") == url for item in readings):
        return fail("that URL is already in the reading list")

    entry = {
        "title": title,
        "url": url,
        "kind": kind,
        "categories": [category],
        "description": description,
    }
    optional_fields = {
        "venue": venue,
        "when": when,
        "authors": authors,
        "doi": doi,
    }
    entry.update({key: value for key, value in optional_fields.items() if value})

    target = Path(READINGS_DIR) / f"{slugify(title)}.yml"
    counter = 2
    while target.exists():
        target = Path(READINGS_DIR) / f"{slugify(title)}-{counter}.yml"
        counter += 1

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.dump(
            entry, handle, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    build_readings_index()

    print(f"Added '{title}' to {target}")
    emit(
        success="true",
        resource_file=one_line(str(target)),
        resource_title=one_line(title),
        resource_url=one_line(url),
        resource_kind=one_line(kind),
        resource_venue=one_line(venue) or "Not provided",
        resource_when=one_line(when) or "Not provided",
        resource_authors=one_line(authors) or "Not provided",
        resource_doi=one_line(doi) or "Not provided",
        resource_category=one_line(category),
        resource_description=one_line(description),
    )


if __name__ == "__main__":
    sys.exit(main())
