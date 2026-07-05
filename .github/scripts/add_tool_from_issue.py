#!/usr/bin/env python3
"""Append a tool to tools/tools.yml from a 'Submit a tool' issue form.

Reads the issue body from the ISSUE_BODY environment variable, validates the
required fields, and (if valid and not a duplicate) appends the tool to the
registry. Writes GitHub Actions outputs to $GITHUB_OUTPUT:

    success=true|false
    tool_name=<name>       (only when success=true)
    reason=<message>       (only when success=false)

Run by .github/workflows/process-tool-submission.yml.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import yaml

from build_catalog_index import main as build_catalog_index
from catalog_common import ALLOWED_CATEGORIES, ALLOWED_STATUSES, CATALOG_DIR, slugify

# Labels here must match the field labels in the issue form exactly. GitHub
# renders each issue-form field as "### <label>" in the issue body.
LABELS = {
    "name": "Tool name",
    "url": "Repository or website URL",
    "category": "Category",
    "description": "Short description",
    "authors": "Author(s)",
    "institution": "Institution(s)",
    "paper_url": "Paper or preprint URL",
    "status": "Artifact status",
    "example_loop": "Example loop",
}


def field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, body, re.S | re.M)
    if not match:
        return ""
    value = match.group(1).strip()
    return "" if value in ("_No response_", "No response") else value


def emit(**outputs: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        for key, value in outputs.items():
            value = value or ""
            if "\n" in value:
                delimiter = f"EOF_{key}"
                handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                handle.write(f"{key}={value}\n")


def fail(reason: str) -> None:
    print(f"Submission rejected: {reason}")
    emit(success="false", reason=reason)


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "").replace("\r\n", "\n")

    name = field(body, LABELS["name"])
    url = field(body, LABELS["url"])
    category = field(body, LABELS["category"])
    description = field(body, LABELS["description"])
    authors = field(body, LABELS["authors"])
    institution = field(body, LABELS["institution"])
    paper_url = field(body, LABELS["paper_url"])
    status = field(body, LABELS["status"])
    example_loop = field(body, LABELS["example_loop"])

    missing = [
        human
        for key, human in (
            ("name", "tool name"),
            ("url", "repository/website URL"),
            ("category", "category"),
            ("description", "short description"),
        )
        if not {
            "name": name,
            "url": url,
            "category": category,
            "description": description,
        }[key]
    ]
    if missing:
        return fail(f"missing required field(s): {', '.join(missing)}")

    if not re.match(r"^https?://", url):
        return fail("the URL must start with http:// or https://")

    if category not in ALLOWED_CATEGORIES:
        return fail(
            f"category '{category}' is not one of: {', '.join(ALLOWED_CATEGORIES)}"
        )
    if paper_url and not re.match(r"^https?://", paper_url):
        return fail("the paper or preprint URL must start with http:// or https://")
    if status and status not in ALLOWED_STATUSES:
        return fail(f"status '{status}' is not one of: {', '.join(ALLOWED_STATUSES)}")

    tools = []
    for path in sorted(Path(CATALOG_DIR).glob("*.yml")):
        with path.open(encoding="utf-8") as handle:
            item = yaml.safe_load(handle) or {}
        if isinstance(item, dict):
            tools.append(item)

    if any((tool.get("title") or "").lower() == name.lower() for tool in tools):
        return fail(f"a tool named '{name}' is already in the registry")
    if any(tool.get("url") == url for tool in tools):
        return fail("that URL is already in the registry")

    entry = {
        "title": name,
        "url": url,
        "categories": [category],
        "description": description,
    }
    optional_fields = {
        "authors": authors,
        "institution": institution,
        "paper_url": paper_url,
        "status": status,
        "example_loop": example_loop,
    }
    entry.update({key: value for key, value in optional_fields.items() if value})
    target = Path(CATALOG_DIR) / f"{slugify(name)}.yml"
    counter = 2
    while target.exists():
        target = Path(CATALOG_DIR) / f"{slugify(name)}-{counter}.yml"
        counter += 1

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.dump(
            entry, handle, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    build_catalog_index()

    print(f"Added '{name}' to {target}")
    emit(
        success="true",
        tool_file=one_line(str(target)),
        tool_name=one_line(name),
        tool_url=one_line(url),
        tool_category=one_line(category),
        tool_description=one_line(description),
        tool_authors=one_line(authors) or "Not provided",
        tool_institution=one_line(institution) or "Not provided",
        tool_paper_url=one_line(paper_url) or "Not provided",
        tool_status=one_line(status) or "Not provided",
        tool_example_loop=one_line(example_loop) or "Not provided",
    )


if __name__ == "__main__":
    sys.exit(main())
