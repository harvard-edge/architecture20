#!/usr/bin/env python3
"""Validate stable and rendered Architecture 2.0 release metadata."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
VERSION_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
RENDERED_VERSION_RE = re.compile(
    r'<span[^>]+id=["\']arch2-release-metadata["\'][^>]*>([^<]+)</span>'
)


def git_output(args: list[str]) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or f"git {' '.join(args)} failed")
    return proc.stdout.strip()


def latest_release() -> tuple[str, str]:
    tag = git_output(["describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"])
    if not VERSION_RE.fullmatch(tag):
        raise ValueError(f"latest release tag is malformed: {tag!r}")
    released = git_output(
        ["for-each-ref", f"refs/tags/{tag}", "--format=%(creatordate:short)"]
    )
    try:
        date.fromisoformat(released)
    except ValueError as exc:
        raise ValueError(f"release tag date is malformed: {released!r}") from exc
    return tag, released


def check_cff(path: Path, tag: str, released: str) -> list[str]:
    errors: list[str] = []
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [f"cannot read {path}: {exc}"]
    if not isinstance(data, dict):
        return [f"{path} must contain a YAML mapping"]

    expected_version = tag.removeprefix("v")
    actual_version = str(data.get("version", ""))
    if actual_version != expected_version:
        errors.append(
            f"{path}: version {actual_version!r} does not match {expected_version!r}"
        )

    raw_date = data.get("date-released", "")
    actual_date = raw_date.isoformat() if isinstance(raw_date, date) else str(raw_date)
    if actual_date != released:
        errors.append(
            f"{path}: date-released {actual_date!r} does not match {released!r}"
        )
    return errors


def rendered_html_version(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    match = RENDERED_VERSION_RE.search(text)
    if not match:
        raise ValueError(f"{path}: release metadata marker is missing")
    return match.group(1).strip()


def rendered_epub_contains(path: Path, expected: str) -> bool:
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if name.endswith((".html", ".xhtml")):
                if expected.encode() in archive.read(name):
                    return True
    return False


def rendered_pdf_contains(path: Path, expected: str) -> bool:
    pdftotext = shutil.which("pdftotext")
    if not pdftotext:
        raise ValueError("pdftotext is required to validate rendered PDF metadata")
    proc = subprocess.run(
        [pdftotext, str(path), "-"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        raise ValueError(proc.stderr.strip() or f"cannot extract text from {path}")
    return expected in proc.stdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cff", type=Path, default=ROOT / "CITATION.cff")
    parser.add_argument("--expected-version")
    parser.add_argument("--rendered-html", type=Path)
    parser.add_argument("--rendered-pdf", type=Path)
    parser.add_argument("--rendered-epub", type=Path)
    args = parser.parse_args()

    errors: list[str] = []
    try:
        tag, released = latest_release()
        errors.extend(check_cff(args.cff, tag, released))
    except ValueError as exc:
        errors.append(str(exc))

    rendered_paths = [args.rendered_html, args.rendered_pdf, args.rendered_epub]
    if any(rendered_paths) and not args.expected_version:
        errors.append("--expected-version is required with rendered artifacts")
    elif args.expected_version:
        try:
            if args.rendered_html:
                actual = rendered_html_version(args.rendered_html)
                if actual != args.expected_version:
                    errors.append(
                        f"{args.rendered_html}: rendered version {actual!r} does not "
                        f"match {args.expected_version!r}"
                    )
            if args.rendered_pdf and not rendered_pdf_contains(
                args.rendered_pdf, f"Preview {args.expected_version}"
            ):
                errors.append(
                    f"{args.rendered_pdf}: Preview {args.expected_version} is missing"
                )
            if args.rendered_epub and not rendered_epub_contains(
                args.rendered_epub, args.expected_version
            ):
                errors.append(
                    f"{args.rendered_epub}: {args.expected_version} is missing"
                )
        except (OSError, ValueError, zipfile.BadZipFile) as exc:
            errors.append(str(exc))

    if errors:
        print("Release consistency check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Release metadata matches {tag} ({released}).")


if __name__ == "__main__":
    main()
