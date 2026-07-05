#!/usr/bin/env python3
"""Resolve Architecture 2.0 release metadata for site publishing."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

VERSION_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")


def git_output(args: list[str]) -> str | None:
    proc = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def base_version() -> str:
    explicit = os.environ.get("ARCH2_VERSION", "").strip()
    if explicit:
        return explicit
    current = os.environ.get("ARCH2_CURRENT_VERSION", "").strip()
    if current:
        return current
    exact = git_output(["describe", "--tags", "--exact-match", "--match", "v[0-9]*"])
    if exact:
        return exact
    latest = git_output(["describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"])
    return latest or "v0.0.0"


def bump_version(version: str, bump: str) -> str:
    match = VERSION_RE.match(version)
    if not match:
        raise SystemExit(f"cannot bump non-semver release version: {version}")
    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))
    if bump == "major":
        return f"v{major + 1}.0.0"
    if bump == "minor":
        return f"v{major}.{minor + 1}.0"
    if bump == "patch":
        return f"v{major}.{minor}.{patch + 1}"
    return version


def github_env_path() -> Path | None:
    value = os.environ.get("GITHUB_ENV", "").strip()
    return Path(value) if value else None


def github_output_path() -> Path | None:
    value = os.environ.get("GITHUB_OUTPUT", "").strip()
    return Path(value) if value else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bump",
        choices=("skip", "patch", "minor", "major"),
        default=os.environ.get("ARCH2_VERSION_BUMP", "skip"),
        help="How to derive the preview version from the current release tag.",
    )
    args = parser.parse_args()

    version = bump_version(base_version(), args.bump)
    publish_date = os.environ.get("ARCH2_PUBLISH_DATE", "").strip()
    if not publish_date:
        publish_date = datetime.now(timezone.utc).date().isoformat()

    lines = [
        f"ARCH2_VERSION={version}",
        f"ARCH2_PUBLISH_DATE={publish_date}",
        f"ARCH2_VERSION_BUMP={args.bump}",
    ]
    env_path = github_env_path()
    if env_path:
        with env_path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines))
            handle.write("\n")

    output_path = github_output_path()
    if output_path:
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(f"arch2_version={version}\n")
            handle.write(f"arch2_publish_date={publish_date}\n")
            handle.write(f"arch2_version_bump={args.bump}\n")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
