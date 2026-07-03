#!/usr/bin/env python3
"""Prepare generated and chapter-local figures before Quarto renders."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

BOOK_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BOOK_DIR.parent
FIGURE_SRC_DIR = REPO_ROOT / "assets" / "figures" / "src"
FIGURE_OUT_DIR = REPO_ROOT / "assets" / "figures" / "generated"
DRAFT_SVGS = {"F2-corpus-pilot-topic-shift.svg"}
IMAGE_REF_RE = re.compile(
    r"images/(?P<name>[^)\s.]+?)(?:\.(?P<ext>pdf|svg|png))?(?=[)\s])"
)


def image_ref_stems(text: str) -> list[str]:
    return sorted({match.group("name") for match in IMAGE_REF_RE.finditer(text)})


def is_stale(source: Path, target: Path) -> bool:
    return not target.exists() or source.stat().st_mtime > target.stat().st_mtime


def audit_svg_text_fit(svg: Path) -> None:
    subprocess.run(
        [str(REPO_ROOT / "arch2"), "validate", "svg", str(svg)],
        check=True,
    )


def convert_svg_figures() -> None:
    FIGURE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for svg in sorted(FIGURE_SRC_DIR.glob("*.svg")):
        if svg.name in DRAFT_SVGS:
            continue
        target = FIGURE_OUT_DIR / f"{svg.stem}.pdf"
        if not is_stale(svg, target):
            continue
        audit_svg_text_fit(svg)
        subprocess.run(
            ["rsvg-convert", "-f", "pdf", "-o", str(target), str(svg)],
            check=True,
        )


def copy_chapter_images() -> None:
    missing: list[str] = []
    for qmd in sorted(
        [
            *BOOK_DIR.glob("chapters/*/index.qmd"),
            *BOOK_DIR.glob("appendices/*/index.qmd"),
        ]
    ):
        chapter_dir = qmd.parent
        image_dir = chapter_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        refs = image_ref_stems(qmd.read_text(encoding="utf-8"))
        referenced = {f"{ref}{suffix}" for ref in refs for suffix in (".pdf", ".svg")}
        for existing in [*image_dir.glob("*.pdf"), *image_dir.glob("*.svg")]:
            if existing.name not in referenced:
                existing.unlink()
        for ref in refs:
            pdf_source = FIGURE_OUT_DIR / f"{ref}.pdf"
            pdf_target = image_dir / f"{ref}.pdf"
            svg_source = FIGURE_SRC_DIR / f"{ref}.svg"
            svg_target = image_dir / f"{ref}.svg"

            if not pdf_source.exists():
                missing.append(f"{qmd.relative_to(BOOK_DIR)} -> {ref}.pdf")
            elif is_stale(pdf_source, pdf_target):
                shutil.copy2(pdf_source, pdf_target)

            if not svg_source.exists():
                missing.append(f"{qmd.relative_to(BOOK_DIR)} -> {ref}.svg")
            elif is_stale(svg_source, svg_target):
                shutil.copy2(svg_source, svg_target)

    if missing:
        print("Missing generated figure PDFs:", file=sys.stderr)
        for item in missing:
            print(f"  {item}", file=sys.stderr)
        raise SystemExit(1)


def run_book_integrity_checks() -> None:
    subprocess.run(
        [str(REPO_ROOT / "arch2"), "validate", "refs"],
        check=True,
    )


def main() -> None:
    convert_svg_figures()
    copy_chapter_images()
    run_book_integrity_checks()


if __name__ == "__main__":
    main()
