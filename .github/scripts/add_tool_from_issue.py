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
from catalog_common import (
    ALLOWED_ARTIFACT_TYPES,
    ALLOWED_STATUSES,
    CATALOG_DIR,
    DESCRIPTION_MAX_CHARS,
    FIT_NOTE_MAX_CHARS,
    SUBMISSION_CATEGORIES,
    SUGGESTED_CATEGORY_OPTION,
    TRIAGE_CATEGORY,
    is_http_url,
    one_line,
    slugify,
    split_tags,
    tag_errors,
)
from github_output import emit_outputs as emit

# Labels here must match the field labels in the issue form exactly. GitHub
# renders each issue-form field as "### <label>" in the issue body.
LABELS = {
    "name": "Tool name",
    "url": "Repository or website URL",
    "artifact_type": "Artifact type",
    "category": "Primary category",
    "category_suggestion": "Suggested category",
    "description": "Short description",
    "fit_note": "Why does this belong in Architecture 2.0?",
    "inputs": "Inputs",
    "outputs": "Outputs",
    "evidence": "Evidence produced",
    "limitations": "Known limitations",
    "tags": "Tags",
    "authors": "Author(s)",
    "institution": "Institution(s)",
    "submitted_by": "Submitted by",
    "paper_url": "Paper or preprint URL",
    "docs_url": "Documentation URL",
    "artifact_url": "Artifact URL",
    "license": "License",
    "citation": "Citation",
    "status": "Artifact status",
    "maintainer_note": "Maintainer note",
}


def field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, body, re.S | re.M)
    if not match:
        return ""
    value = match.group(1).strip()
    return "" if value in ("_No response_", "No response") else value


def fail(reason: str) -> None:
    print(f"Submission rejected: {reason}")
    emit(success="false", reason=reason)


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "").replace("\r\n", "\n")

    name = field(body, LABELS["name"])
    url = field(body, LABELS["url"])
    artifact_type = field(body, LABELS["artifact_type"])
    category = field(body, LABELS["category"])
    category_suggestion = field(body, LABELS["category_suggestion"])
    description = field(body, LABELS["description"])
    fit_note = field(body, LABELS["fit_note"])
    inputs = field(body, LABELS["inputs"])
    outputs = field(body, LABELS["outputs"])
    evidence = field(body, LABELS["evidence"])
    limitations = field(body, LABELS["limitations"])
    tags = split_tags(field(body, LABELS["tags"]))
    authors = field(body, LABELS["authors"])
    institution = field(body, LABELS["institution"])
    submitted_by = field(body, LABELS["submitted_by"])
    paper_url = field(body, LABELS["paper_url"])
    docs_url = field(body, LABELS["docs_url"])
    artifact_url = field(body, LABELS["artifact_url"])
    license_text = field(body, LABELS["license"])
    citation = field(body, LABELS["citation"])
    status = field(body, LABELS["status"])
    maintainer_note = field(body, LABELS["maintainer_note"])

    missing = [
        human
        for key, human in (
            ("name", "tool name"),
            ("url", "repository/website URL"),
            ("artifact_type", "artifact type"),
            ("category", "category"),
            ("description", "short description"),
            ("fit_note", "Architecture 2.0 fit"),
        )
        if not {
            "name": name,
            "url": url,
            "artifact_type": artifact_type,
            "category": category,
            "description": description,
            "fit_note": fit_note,
        }[key]
    ]
    if missing:
        return fail(f"missing required field(s): {', '.join(missing)}")

    name = one_line(name)
    url = one_line(url)
    artifact_type = one_line(artifact_type)
    category = one_line(category)
    category_suggestion = one_line(category_suggestion)
    description = one_line(description)
    fit_note = one_line(fit_note)
    inputs = one_line(inputs)
    outputs = one_line(outputs)
    evidence = one_line(evidence)
    limitations = one_line(limitations)
    authors = one_line(authors)
    institution = one_line(institution)
    submitted_by = one_line(submitted_by)
    paper_url = one_line(paper_url)
    docs_url = one_line(docs_url)
    artifact_url = one_line(artifact_url)
    license_text = one_line(license_text)
    citation = one_line(citation)
    status = one_line(status)
    maintainer_note = one_line(maintainer_note)

    if not is_http_url(url):
        return fail("the URL must start with http:// or https://")

    if artifact_type not in ALLOWED_ARTIFACT_TYPES:
        return fail(
            f"artifact type '{artifact_type}' is not one of: "
            f"{', '.join(ALLOWED_ARTIFACT_TYPES)}"
        )

    if category not in SUBMISSION_CATEGORIES:
        return fail(
            f"category '{category}' is not one of: {', '.join(SUBMISSION_CATEGORIES)}"
        )

    categories = [category]
    if category == SUGGESTED_CATEGORY_OPTION:
        if not category_suggestion:
            return fail(
                "please provide a suggested category when choosing "
                f"'{SUGGESTED_CATEGORY_OPTION}'"
            )
        categories = [TRIAGE_CATEGORY]

    for key, value in {
        "paper or preprint URL": paper_url,
        "documentation URL": docs_url,
        "artifact URL": artifact_url,
    }.items():
        if value and not is_http_url(value):
            return fail(f"the {key} must start with http:// or https://")

    if len(description) > DESCRIPTION_MAX_CHARS:
        return fail(
            f"the short description is {len(description)} characters; "
            f"the maximum is {DESCRIPTION_MAX_CHARS}"
        )
    if len(fit_note) > FIT_NOTE_MAX_CHARS:
        return fail(
            f"the Architecture 2.0 fit note is {len(fit_note)} characters; "
            f"the maximum is {FIT_NOTE_MAX_CHARS}"
        )
    tag_problems = tag_errors(tags)
    if tag_problems:
        return fail("; ".join(tag_problems))

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
        "artifact_type": artifact_type,
        "categories": categories,
        "description": description,
        "fit_note": fit_note,
        # Availability is a maintainer-verified claim, not a submitter claim.
        "artifact_availability": "unverified",
    }
    optional_fields = {
        "tags": tags,
        "authors": authors,
        "institution": institution,
        "submitted_by": submitted_by,
        "inputs": inputs,
        "outputs": outputs,
        "evidence": evidence,
        "limitations": limitations,
        "paper_url": paper_url,
        "docs_url": docs_url,
        "artifact_url": artifact_url,
        "license": license_text,
        "citation": citation,
        "status": status,
        "category_suggestion": category_suggestion,
        "maintainer_note": maintainer_note,
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
        tool_artifact_type=one_line(artifact_type),
        tool_category=one_line(", ".join(categories)),
        tool_category_suggestion=one_line(category_suggestion) or "Not provided",
        tool_description=one_line(description),
        tool_fit_note=one_line(fit_note),
        tool_artifact_availability="unverified",
        tool_tags=one_line(", ".join(tags)) or "Not provided",
        tool_authors=one_line(authors) or "Not provided",
        tool_institution=one_line(institution) or "Not provided",
        tool_submitted_by=one_line(submitted_by) or "Not provided",
        tool_inputs=one_line(inputs) or "Not provided",
        tool_outputs=one_line(outputs) or "Not provided",
        tool_evidence=one_line(evidence) or "Not provided",
        tool_limitations=one_line(limitations) or "Not provided",
        tool_paper_url=one_line(paper_url) or "Not provided",
        tool_docs_url=one_line(docs_url) or "Not provided",
        tool_artifact_url=one_line(artifact_url) or "Not provided",
        tool_license=one_line(license_text) or "Not provided",
        tool_citation=one_line(citation) or "Not provided",
        tool_status=one_line(status) or "Not provided",
        tool_maintainer_note=one_line(maintainer_note) or "Not provided",
    )


if __name__ == "__main__":
    sys.exit(main())
