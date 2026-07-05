"""Shared constants for the Architecture 2.0 tool registry.

The category set here is the single source of truth. It must stay in sync with
the dropdown in .github/ISSUE_TEMPLATE/submit_tool.yml and the facets used in
tools/tools.yml, so the site's category filter never fragments.
"""

import re

CATALOG_PATH = "tools/tools.yml"
CATALOG_DIR = "tools/registry"

ALLOWED_CATEGORIES = [
    "Simulation",
    "Proxy Models",
    "Agentic Workflows",
    "Data Representations",
    "Verification",
    "Benchmarks",
    "Physical Design",
]

ALLOWED_STATUSES = [
    "Active project",
    "Published artifact",
    "Preprint or paper artifact",
    "Prototype",
    "Dataset or benchmark",
    "Other",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "tool"
