"""Shared helpers for the Architecture 2.0 tool registry."""

import os
import re

CATALOG_PATH = os.environ.get("ARCH2_TOOL_INDEX", "tools/tools.yml")
CATALOG_DIR = os.environ.get("ARCH2_TOOL_REGISTRY", "tools/registry")

DESCRIPTION_MAX_CHARS = 220
MAX_TAGS = 5
TAG_MAX_CHARS = 32

SUGGESTED_CATEGORY_OPTION = "Not sure / suggest a category"
TRIAGE_CATEGORY = "Needs Triage"

ALLOWED_CATEGORIES = [
    "Simulation",
    "Proxy Models",
    "Agentic Workflows",
    "Data Representations",
    "Verification",
    "Benchmarks and Datasets",
    "Physical Design",
]

SUBMISSION_CATEGORIES = ALLOWED_CATEGORIES + [SUGGESTED_CATEGORY_OPTION]

ALLOWED_STATUSES = [
    "Active project",
    "Published artifact",
    "Preprint or paper artifact",
    "Prototype",
    "Dataset or benchmark",
    "Other",
]

OPTIONAL_URL_FIELDS = ("paper_url", "docs_url", "artifact_url")


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tool"


def one_line(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def is_http_url(value: str) -> bool:
    return bool(re.match(r"^https?://", value or ""))


def split_tags(value: str) -> list[str]:
    tags = [one_line(part) for part in re.split(r"[,;\n]+", value or "")]
    return [tag for tag in tags if tag]


def tag_errors(tags: object) -> list[str]:
    if not tags:
        return []
    if not isinstance(tags, list):
        return ["tags must be a list"]

    errors: list[str] = []
    if len(tags) > MAX_TAGS:
        errors.append(f"tags has more than {MAX_TAGS} entries")

    seen_tags: set[str] = set()
    for tag in tags:
        tag_value = one_line(str(tag))
        tag_key = tag_value.lower()
        if not tag_value:
            errors.append("tags must not contain empty values")
        if len(tag_value) > TAG_MAX_CHARS:
            errors.append(f"tag '{tag_value}' is longer than {TAG_MAX_CHARS} chars")
        if tag_key in seen_tags:
            errors.append(f"duplicate tag '{tag_value}'")
        seen_tags.add(tag_key)
    return errors
