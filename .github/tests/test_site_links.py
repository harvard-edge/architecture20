from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / ".github" / "scripts" / "check_site_links.py"
SPEC = importlib.util.spec_from_file_location("check_site_links", MODULE_PATH)
assert SPEC and SPEC.loader
check_site_links = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check_site_links)


class SiteLinkTests(unittest.TestCase):
    def test_root_relative_nested_and_fragment_links_pass(self) -> None:
        with TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "book" / "chapter").mkdir(parents=True)
            (site / "assets").mkdir()
            (site / "assets" / "figure.svg").write_text("<svg/>", encoding="utf-8")
            (site / "index.html").write_text(
                '<main id="main-content"><a href="/book/chapter/#result">Read</a></main>',
                encoding="utf-8",
            )
            (site / "book" / "chapter" / "index.html").write_text(
                '<section id="result"><img src="../../assets/figure.svg"></section>',
                encoding="utf-8",
            )

            self.assertEqual(check_site_links.findings(site), [])

    def test_missing_file_and_fragment_are_reported(self) -> None:
        with TemporaryDirectory() as directory:
            site = Path(directory)
            (site / "index.html").write_text(
                '<a href="missing.html">Missing</a><a href="#absent">Absent</a>',
                encoding="utf-8",
            )

            problems = check_site_links.findings(site)

            self.assertEqual(len(problems), 2)
            self.assertTrue(any("targets missing" in problem for problem in problems))
            self.assertTrue(any("missing fragment" in problem for problem in problems))


if __name__ == "__main__":
    unittest.main()
