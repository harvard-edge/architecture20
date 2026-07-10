from __future__ import annotations

import importlib.util
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "release_metadata.py"
SPEC = importlib.util.spec_from_file_location("release_metadata", SCRIPT)
assert SPEC and SPEC.loader
release_metadata = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release_metadata
SPEC.loader.exec_module(release_metadata)


def git_values(*, exact: str | None = None, latest: str | None = "v0.1.3"):
    full = "abcdef1234567890abcdef1234567890abcdef12"

    def output(args: list[str]) -> str | None:
        if args[:3] == ["tag", "--points-at", "HEAD"]:
            return exact
        if args[:3] == ["describe", "--tags", "--abbrev=0"]:
            return latest
        if args == ["rev-parse", "HEAD"]:
            return full
        if args == ["rev-parse", "--short=12", "HEAD"]:
            return full[:12]
        if args == ["log", "-1", "--format=%cs", "v0.1.3^{}"]:
            return "2026-07-08"
        raise AssertionError(f"unexpected git call: {args}")

    return output


class ReleaseMetadataTests(unittest.TestCase):
    def resolve(self, bump: str = "skip", **env: str) -> str:
        with mock.patch.dict(os.environ, env, clear=True), mock.patch.object(
            release_metadata, "git_output", side_effect=git_values()
        ):
            return release_metadata.resolve_version(bump)

    def test_exact_tag_is_stable_release(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            release_metadata,
            "git_output",
            side_effect=git_values(exact="v0.1.3"),
        ):
            self.assertEqual(release_metadata.resolve_version("skip"), "v0.1.3")

    def test_post_tag_commit_is_commit_qualified(self) -> None:
        self.assertEqual(self.resolve(), "v0.1.3+gabcdef123456")

    def test_explicit_development_version_must_name_head(self) -> None:
        self.assertEqual(
            self.resolve(ARCH2_VERSION="v0.1.3+gabcdef1"),
            "v0.1.3+gabcdef1",
        )

    def test_explicit_stable_version_requires_matching_tag(self) -> None:
        with mock.patch.dict(
            os.environ, {"ARCH2_VERSION": "v0.1.3"}, clear=True
        ), mock.patch.object(
            release_metadata,
            "git_output",
            side_effect=git_values(exact="v0.1.3"),
        ):
            self.assertEqual(release_metadata.resolve_version("skip"), "v0.1.3")

    def test_patch_bump_uses_stable_baseline(self) -> None:
        self.assertEqual(
            self.resolve("patch", ARCH2_CURRENT_VERSION="v0.1.3"), "v0.1.4"
        )

    def test_exact_tag_uses_tagged_commit_date(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            release_metadata,
            "git_output",
            side_effect=git_values(exact="v0.1.3"),
        ):
            self.assertEqual(
                release_metadata.resolve_publish_date("v0.1.3"), "2026-07-08"
            )

    def test_malformed_explicit_publish_date_fails(self) -> None:
        with mock.patch.dict(
            os.environ, {"ARCH2_PUBLISH_DATE": "July someday"}, clear=True
        ), self.assertRaisesRegex(SystemExit, "malformed"):
            release_metadata.resolve_publish_date("v0.1.3+gabcdef1")

    def test_all_bump_modes(self) -> None:
        self.assertEqual(release_metadata.bump_version("v1.2.3", "major"), "v2.0.0")
        self.assertEqual(release_metadata.bump_version("v1.2.3", "minor"), "v1.3.0")
        self.assertEqual(release_metadata.bump_version("v1.2.3", "patch"), "v1.2.4")
        self.assertEqual(release_metadata.bump_version("v1.2.3", "skip"), "v1.2.3")

    def test_malformed_current_version_fails(self) -> None:
        with self.assertRaisesRegex(SystemExit, "not a release version"):
            self.resolve(ARCH2_CURRENT_VERSION="release-1")

    def test_current_version_conflict_fails(self) -> None:
        with self.assertRaisesRegex(SystemExit, "conflicts"):
            self.resolve(ARCH2_CURRENT_VERSION="v0.1.2")

    def test_explicit_version_and_bump_conflict(self) -> None:
        with self.assertRaisesRegex(SystemExit, "cannot be combined"):
            self.resolve("patch", ARCH2_VERSION="v0.1.3+gabcdef1")

    def test_multiple_exact_release_tags_fail(self) -> None:
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch.object(
            release_metadata,
            "git_output",
            side_effect=git_values(exact="v0.1.2\nv0.1.3"),
        ), self.assertRaisesRegex(SystemExit, "conflicting release tags"):
            release_metadata.resolve_version("skip")


if __name__ == "__main__":
    unittest.main()
