#!/usr/bin/env python3
"""Resolve Architecture 2.0 release metadata for site publishing."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path

VERSION_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
DEVELOPMENT_VERSION_RE = re.compile(
    r"^(?P<base>v\d+\.\d+\.\d+)\+g(?P<revision>[0-9a-f]{7,40})$"
)


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


def stable_version(value: str, source: str) -> str:
    if not VERSION_RE.fullmatch(value):
        raise SystemExit(f"{source} is not a release version: {value!r}")
    return value


def exact_release_tag() -> str | None:
    output = git_output(["tag", "--points-at", "HEAD", "--list", "v[0-9]*"])
    tags = sorted(set(output.splitlines())) if output else []
    for tag in tags:
        stable_version(tag, "release tag")
    if len(tags) > 1:
        raise SystemExit("conflicting release tags point at HEAD: " + ", ".join(tags))
    return tags[0] if tags else None


def latest_release_tag() -> str | None:
    latest = git_output(["describe", "--tags", "--abbrev=0", "--match", "v[0-9]*"])
    return stable_version(latest, "latest release tag") if latest else None


def release_baseline() -> str:
    current = os.environ.get("ARCH2_CURRENT_VERSION", "").strip()
    if current:
        current = stable_version(current, "ARCH2_CURRENT_VERSION")
    latest = latest_release_tag()
    if current and latest and current != latest:
        raise SystemExit(
            "ARCH2_CURRENT_VERSION conflicts with the latest release tag: "
            f"{current} != {latest}"
        )
    return current or latest or "v0.0.0"


def head_revision(*, short: bool = False) -> str:
    args = ["rev-parse", "--short=12", "HEAD"] if short else ["rev-parse", "HEAD"]
    revision = git_output(args)
    if not revision or not re.fullmatch(r"[0-9a-f]{7,40}", revision):
        raise SystemExit("cannot resolve a hexadecimal commit ID for HEAD")
    return revision


def release_tag_date(version: str) -> str:
    tagged_date = git_output(
        [
            "for-each-ref",
            f"refs/tags/{version}",
            "--format=%(creatordate:short)",
        ]
    )
    if not tagged_date:
        raise SystemExit(f"cannot resolve the release date for {version}")
    try:
        date.fromisoformat(tagged_date)
    except ValueError as exc:
        raise SystemExit(
            f"release tag date is malformed for {version}: {tagged_date!r}"
        ) from exc
    return tagged_date


def explicit_version() -> str | None:
    value = os.environ.get("ARCH2_VERSION", "").strip()
    if not value:
        return None

    if VERSION_RE.fullmatch(value):
        exact = exact_release_tag()
        if exact != value:
            raise SystemExit(
                "an explicit stable ARCH2_VERSION must match the release tag at HEAD; "
                "use --bump for a deliberate release candidate"
            )
        return value

    match = DEVELOPMENT_VERSION_RE.fullmatch(value)
    if not match:
        raise SystemExit(f"ARCH2_VERSION is malformed: {value!r}")
    revision = match.group("revision")
    if not head_revision().startswith(revision):
        raise SystemExit(
            "ARCH2_VERSION commit qualifier does not identify the current HEAD"
        )
    return value


def base_version(*, baseline: str | None = None) -> str:
    """Return a truthful identity for the current checkout.

    Stable versions identify exact tagged commits. Every ordinary post-tag build
    carries the current commit ID so it cannot impersonate the prior release.
    """

    explicit = explicit_version()
    if explicit:
        return explicit
    exact = exact_release_tag()
    if exact:
        return exact
    return f"{baseline or release_baseline()}+g{head_revision(short=True)}"


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


def resolve_version(bump: str) -> str:
    baseline = release_baseline()
    explicit = os.environ.get("ARCH2_VERSION", "").strip()
    if bump != "skip":
        if explicit:
            raise SystemExit("ARCH2_VERSION cannot be combined with a version bump")
        return bump_version(baseline, bump)
    return base_version(baseline=baseline)


def resolve_publish_date(version: str) -> str:
    explicit = os.environ.get("ARCH2_PUBLISH_DATE", "").strip()
    if explicit:
        try:
            date.fromisoformat(explicit)
        except ValueError as exc:
            raise SystemExit(f"ARCH2_PUBLISH_DATE is malformed: {explicit!r}") from exc
        return explicit

    if VERSION_RE.fullmatch(version) and exact_release_tag() == version:
        return release_tag_date(version)

    return datetime.now(timezone.utc).date().isoformat()


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

    version = resolve_version(args.bump)
    publish_date = resolve_publish_date(version)

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
