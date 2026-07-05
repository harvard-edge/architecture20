"""Shared constants for the Architecture 2.0 reading list."""

import re

READINGS_PATH = "www/readings.yml"
READINGS_DIR = "www/readings"

ALLOWED_READING_CATEGORIES = [
    "Architecture 2.0",
    "Papers",
    "Blog posts",
    "Agentic AI",
    "Benchmarks and Datasets",
    "Tools and Infrastructure",
    "Talks",
    "Computer Architecture",
    "Foundations",
    "Workshops",
]

ALLOWED_RESOURCE_TYPES = [
    "Paper",
    "Article",
    "Blog post",
    "Podcast",
    "Talk",
    "Report",
    "Dataset",
    "Tool documentation",
    "Workshop writeup",
    "Other",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "resource"
