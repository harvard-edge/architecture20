from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_release_consistency.py"
SPEC = importlib.util.spec_from_file_location("check_release_consistency", SCRIPT)
assert SPEC and SPEC.loader
release_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release_check
SPEC.loader.exec_module(release_check)


class ReleaseConsistencyTests(unittest.TestCase):
    def test_cff_matches_release(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CITATION.cff"
            path.write_text("version: 0.1.3\ndate-released: 2026-07-08\n")
            self.assertEqual(release_check.check_cff(path, "v0.1.3", "2026-07-08"), [])

    def test_cff_reports_version_and_date_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "CITATION.cff"
            path.write_text("version: 1.0.0\ndate-released: 2026-08-01\n")
            errors = release_check.check_cff(path, "v0.1.3", "2026-07-08")
            self.assertEqual(len(errors), 2)

    def test_html_release_marker_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.html"
            path.write_text(
                '<span id="arch2-release-metadata" hidden>v0.1.3+gabcdef1</span>'
            )
            self.assertEqual(
                release_check.rendered_html_version(path), "v0.1.3+gabcdef1"
            )

    def test_epub_searches_rendered_documents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.epub"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("EPUB/text/index.xhtml", "Preview v0.1.3+gabcdef1")
            self.assertTrue(
                release_check.rendered_epub_contains(path, "v0.1.3+gabcdef1")
            )

    def test_preview_versions_find_stale_and_expected_identities(self) -> None:
        self.assertEqual(
            release_check.preview_versions(
                "Preview v0.1.0 and Preview v0.1.3+gabcdef1"
            ),
            {"v0.1.0", "v0.1.3+gabcdef1"},
        )

    def test_hardcoded_fallback_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "book" / "_quarto.yml"
            path.parent.mkdir(parents=True)
            path.write_text('arch2-version: "Preview v0.1.0"\n')
            errors = release_check.hardcoded_preview_errors(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("version-neutral", errors[0])

    def test_epub_reports_every_preview_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.epub"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("EPUB/text/index.xhtml", "Preview v0.1.3+gabcdef1")
                archive.writestr("EPUB/images/cover.svg", "Preview v0.1.0")
            self.assertEqual(
                release_check.rendered_epub_preview_versions(path),
                {"v0.1.0", "v0.1.3+gabcdef1"},
            )


if __name__ == "__main__":
    unittest.main()
