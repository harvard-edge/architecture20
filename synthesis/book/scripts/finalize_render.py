#!/usr/bin/env python3
"""Verify the Quarto PDF after render and remove LaTeX scratch files."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


BOOK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BOOK_DIR.parent
BUILD_DIR = BOOK_DIR / "_build"
PDF_TARGET = BUILD_DIR / "Architecture-2.0.pdf"
HTML_TARGET = BUILD_DIR / "index.html"
SCRATCH_PATTERNS = [
    "*.aux",
    "*.bbl",
    "*.blg",
    "*.idx",
    "*.ilg",
    "*.ind",
    "*.log",
    "*.out",
    "*.run.xml",
    "*.synctex.gz",
    "*.tex",
    "DescriptionTexts.txt",
]


def rendered_pdf() -> Path:
    if PDF_TARGET.exists():
        return PDF_TARGET
    print(f"error: Quarto did not produce {PDF_TARGET}", file=sys.stderr)
    raise SystemExit(1)


def run_checks(pdf_path: Path) -> None:
    subprocess.run(
        [str(REPO_ROOT / "arch2"), "verify", "figures", "--pdf", str(pdf_path)],
        check=True,
    )


def remove_scratch_files() -> None:
    if os.environ.get("ARCH2_KEEP_LATEX_LOGS"):
        return
    for pattern in SCRATCH_PATTERNS:
        for path in BOOK_DIR.glob(pattern):
            if path.is_file():
                path.unlink()


def main() -> None:
    target = os.environ.get("ARCH2_RENDER_TARGET", "all")
    if target == "html":
        if not HTML_TARGET.exists():
            print(f"error: Quarto did not produce {HTML_TARGET}", file=sys.stderr)
            raise SystemExit(1)
        return

    pdf_path = rendered_pdf()
    run_checks(pdf_path)
    remove_scratch_files()


if __name__ == "__main__":
    main()
