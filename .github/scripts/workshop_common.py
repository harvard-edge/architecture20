"""Shared constants for the Architecture 2.0 workshop registry."""

import os
import re

WORKSHOPS_PATH = os.environ.get("ARCH2_WORKSHOP_INDEX", "www/workshops.yml")
WORKSHOPS_DIR = os.environ.get("ARCH2_WORKSHOP_REGISTRY", "www/workshops")

ALLOWED_WORKSHOP_CATEGORIES = [
    "Architecture 2.0",
    "ML for Systems",
    "Agentic AI",
    "Computer Architecture",
    "EDA and Tools",
    "Benchmarks and Datasets",
    "Education",
    "Community",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workshop"
