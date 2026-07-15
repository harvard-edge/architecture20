#!/usr/bin/env python3
"""Validate local links and resources in the assembled Architecture 2.0 site."""

from __future__ import annotations

import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REFERENCE_ATTRIBUTES = {
    "a": ("href",),
    "img": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src",),
}


class ReferenceParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.identifiers: set[str] = set()
        self.references: list[tuple[str, str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        identifier = attributes.get("id")
        if identifier:
            self.identifiers.add(identifier)
        if tag == "a" and attributes.get("name"):
            self.identifiers.add(attributes["name"] or "")
        for attribute in REFERENCE_ATTRIBUTES.get(tag, ()):
            value = attributes.get(attribute)
            if value:
                self.references.append((tag, attribute, value))

    handle_startendtag = handle_starttag


def parse_page(path: Path) -> ReferenceParser:
    parser = ReferenceParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def resolve_local_target(
    site_root: Path, source: Path, raw_url: str
) -> tuple[Path, str] | None:
    if raw_url.startswith("//"):
        return None
    parsed = urlsplit(raw_url)
    if parsed.scheme or parsed.netloc:
        return None

    path_text = unquote(parsed.path)
    if path_text.startswith("/"):
        target = site_root / path_text.lstrip("/")
    elif path_text:
        target = source.parent / path_text
    else:
        target = source

    target = target.resolve(strict=False)
    root = site_root.resolve()
    if target != root and root not in target.parents:
        return target, parsed.fragment
    if target.is_dir() or path_text.endswith("/"):
        target = target / "index.html"
    return target, unquote(parsed.fragment)


def findings(site_root: Path) -> list[str]:
    site_root = site_root.resolve()
    pages = sorted(site_root.rglob("*.html"))
    parsed_pages = {page: parse_page(page) for page in pages}
    problems: list[str] = []

    for source, parser in parsed_pages.items():
        for tag, attribute, raw_url in parser.references:
            resolved = resolve_local_target(site_root, source, raw_url)
            if resolved is None:
                continue
            target, fragment = resolved
            location = source.relative_to(site_root)
            if not target.is_file():
                problems.append(
                    f"{location}: <{tag}> {attribute}={raw_url!r} targets missing "
                    f"{target.relative_to(site_root) if site_root in target.parents else target}"
                )
                continue
            if fragment and target.suffix.lower() in {".html", ".htm"}:
                target_parser = parsed_pages.get(target)
                if target_parser is None:
                    target_parser = parse_page(target)
                    parsed_pages[target] = target_parser
                if fragment not in target_parser.identifiers:
                    problems.append(
                        f"{location}: {raw_url!r} targets missing fragment #{fragment}"
                    )
    return problems


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("usage: check_site_links.py ASSEMBLED_SITE_ROOT", file=sys.stderr)
        return 2
    site_root = Path(arguments[0])
    if not site_root.is_dir():
        print(f"{site_root}: assembled site directory does not exist", file=sys.stderr)
        return 2
    problems = findings(site_root)
    if problems:
        for problem in problems:
            print(problem, file=sys.stderr)
        return 1
    page_count = sum(1 for _ in site_root.rglob("*.html"))
    print(f"Assembled-site local link contract passed for {page_count} page(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
