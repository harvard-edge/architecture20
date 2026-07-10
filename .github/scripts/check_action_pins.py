#!/usr/bin/env python3
"""Reject mutable third-party references in GitHub Actions workflows."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
USE_RE = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)(?:\s+#\s*(.+))?$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
DOCKER_DIGEST_RE = re.compile(r"^docker://[^@\s]+@sha256:[0-9a-f]{64}$")
VERSION_COMMENT_RE = re.compile(r"^v\d+(?:\.\d+){0,2}(?:\s|$)")


def check_workflow(path: Path) -> list[str]:
    errors: list[str] = []
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = USE_RE.match(line)
        if not match:
            continue
        target, comment = match.groups()
        where = f"{path}:{line_number}"
        if target.startswith("./"):
            continue
        if target.startswith("docker://"):
            if not DOCKER_DIGEST_RE.fullmatch(target):
                errors.append(
                    f"{where}: container action must use a 64-character sha256 digest"
                )
            continue
        if "@" not in target:
            errors.append(f"{where}: action reference has no commit pin: {target}")
            continue
        _, revision = target.rsplit("@", 1)
        if not COMMIT_RE.fullmatch(revision):
            errors.append(f"{where}: action reference is mutable: {target}")
        if not comment or not VERSION_COMMENT_RE.match(comment):
            errors.append(f"{where}: pinned action needs a trailing version comment")
    return errors


def check_action_pins(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    workflows = sorted((root / ".github" / "workflows").glob("*.yml"))
    workflows.extend(sorted((root / ".github" / "workflows").glob("*.yaml")))
    if not workflows:
        return [f"{root}: no GitHub Actions workflows found"]
    for path in workflows:
        try:
            errors.extend(check_workflow(path))
        except OSError as exc:
            errors.append(f"cannot read {path}: {exc}")
    return errors


def main() -> None:
    errors = check_action_pins()
    if errors:
        print("GitHub Actions pin check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        raise SystemExit(1)
    print("All GitHub Actions use immutable commit pins.")


if __name__ == "__main__":
    main()
