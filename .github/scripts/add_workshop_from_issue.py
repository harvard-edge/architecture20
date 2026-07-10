#!/usr/bin/env python3
"""Append a workshop to www/workshops.yml from a workshop issue form."""
from __future__ import annotations

import os
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from build_workshops_index import main as build_workshops_index
from github_output import emit_outputs as emit
from workshop_common import ALLOWED_WORKSHOP_CATEGORIES, WORKSHOPS_DIR, slugify

LABELS = {
    "title": "Workshop or venue name",
    "url": "Website URL",
    "venue": "Venue or host",
    "date": "Date or year",
    "event_start": "Event start date",
    "event_end": "Event end date",
    "category": "Primary topic",
    "description": "Short description",
    "location": "Location",
    "organizers": "Organizer(s)",
    "institution": "Institution(s)",
    "submission_url": "CFP or submission URL",
    "deadline": "Submission deadline",
}


def field(body: str, label: str) -> str:
    pattern = rf"^###\s+{re.escape(label)}\s*\n+(.*?)(?=\n###\s|\Z)"
    match = re.search(pattern, body, re.S | re.M)
    if not match:
        return ""
    value = match.group(1).strip()
    return "" if value in ("_No response_", "No response") else value


def fail(reason: str) -> None:
    print(f"Workshop submission rejected: {reason}")
    emit(success="false", reason=reason)


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def parse_event_date(value: str, label: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"the {label} must use YYYY-MM-DD") from exc


def main() -> None:
    body = os.environ.get("ISSUE_BODY", "").replace("\r\n", "\n")

    title = field(body, LABELS["title"])
    url = field(body, LABELS["url"])
    venue = field(body, LABELS["venue"])
    when = field(body, LABELS["date"])
    event_start_text = field(body, LABELS["event_start"])
    event_end_text = field(body, LABELS["event_end"])
    category = field(body, LABELS["category"])
    description = field(body, LABELS["description"])
    location = field(body, LABELS["location"])
    organizers = field(body, LABELS["organizers"])
    institution = field(body, LABELS["institution"])
    submission_url = field(body, LABELS["submission_url"])
    deadline = field(body, LABELS["deadline"])

    missing = [
        human
        for key, human in (
            ("title", "workshop or venue name"),
            ("url", "website URL"),
            ("venue", "venue or host"),
            ("when", "date or year"),
            ("event_start", "event start date"),
            ("event_end", "event end date"),
            ("category", "primary topic"),
            ("description", "short description"),
        )
        if not {
            "title": title,
            "url": url,
            "venue": venue,
            "when": when,
            "event_start": event_start_text,
            "event_end": event_end_text,
            "category": category,
            "description": description,
        }[key]
    ]
    if missing:
        return fail(f"missing required field(s): {', '.join(missing)}")

    title = one_line(title)
    url = one_line(url)
    venue = one_line(venue)
    when = one_line(when)
    event_start_text = one_line(event_start_text)
    event_end_text = one_line(event_end_text)
    category = one_line(category)
    description = one_line(description)
    location = one_line(location)
    organizers = one_line(organizers)
    institution = one_line(institution)
    submission_url = one_line(submission_url)
    deadline = one_line(deadline)

    try:
        event_start = parse_event_date(event_start_text, "event start date")
        event_end = parse_event_date(event_end_text, "event end date")
    except ValueError as exc:
        return fail(str(exc))
    if event_end < event_start:
        return fail("the event end date must not be before the event start date")

    if not re.match(r"^https?://", url):
        return fail("the website URL must start with http:// or https://")
    if submission_url and not re.match(r"^https?://", submission_url):
        return fail("the CFP or submission URL must start with http:// or https://")
    if category not in ALLOWED_WORKSHOP_CATEGORIES:
        return fail(
            f"primary topic '{category}' is not one of: "
            f"{', '.join(ALLOWED_WORKSHOP_CATEGORIES)}"
        )

    workshops = []
    for path in sorted(Path(WORKSHOPS_DIR).glob("*.yml")):
        with path.open(encoding="utf-8") as handle:
            item = yaml.safe_load(handle) or {}
        if isinstance(item, dict):
            workshops.append(item)

    if any((item.get("title") or "").lower() == title.lower() for item in workshops):
        return fail(f"a workshop named '{title}' is already in the registry")
    if any(item.get("url") == url for item in workshops):
        return fail("that URL is already in the workshop registry")

    entry = {
        "title": title,
        "url": url,
        "venue": venue,
        "when": when,
        "event_start": event_start_text,
        "event_end": event_end_text,
        # A maintainer promotes the entry only after verifying dates and links.
        "status": "proposed",
        "categories": [category],
        "description": description,
    }
    optional_fields = {
        "location": location,
        "organizers": organizers,
        "institution": institution,
        "submission_url": submission_url,
        "deadline": deadline,
    }
    entry.update({key: value for key, value in optional_fields.items() if value})

    target = Path(WORKSHOPS_DIR) / f"{slugify(title)}.yml"
    counter = 2
    while target.exists():
        target = Path(WORKSHOPS_DIR) / f"{slugify(title)}-{counter}.yml"
        counter += 1

    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.dump(
            entry, handle, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    build_workshops_index()

    print(f"Added '{title}' to {target}")
    emit(
        success="true",
        workshop_file=one_line(str(target)),
        workshop_name=one_line(title),
        workshop_url=one_line(url),
        workshop_venue=one_line(venue),
        workshop_when=one_line(when),
        workshop_event_start=event_start_text,
        workshop_event_end=event_end_text,
        workshop_status="proposed",
        workshop_category=one_line(category),
        workshop_description=one_line(description),
        workshop_location=one_line(location) or "Not provided",
        workshop_organizers=one_line(organizers) or "Not provided",
        workshop_institution=one_line(institution) or "Not provided",
        workshop_submission_url=one_line(submission_url) or "Not provided",
        workshop_deadline=one_line(deadline) or "Not provided",
    )


if __name__ == "__main__":
    sys.exit(main())
