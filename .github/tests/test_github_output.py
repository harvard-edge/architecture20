from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).parents[1] / "scripts" / "github_output.py"
SPEC = importlib.util.spec_from_file_location("github_output", SCRIPT)
assert SPEC and SPEC.loader
github_output = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = github_output
SPEC.loader.exec_module(github_output)


class GitHubOutputTests(unittest.TestCase):
    def test_multiline_payload_cannot_terminate_its_output(self) -> None:
        payload = "invalid input\nEOF_reason\nsuccess=true"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                github_output.emit_outputs(reason=payload)

            lines = output.read_text(encoding="utf-8").splitlines()
            key, delimiter = lines[0].split("<<", 1)
            self.assertEqual(key, "reason")
            self.assertNotIn(delimiter, payload.splitlines())
            self.assertEqual(lines[-1], delimiter)
            self.assertEqual("\n".join(lines[1:-1]), payload)

    def test_single_line_output_uses_key_value_form(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                github_output.emit_outputs(success="true")
            self.assertEqual(output.read_text(encoding="utf-8"), "success=true\n")

    def test_invalid_output_key_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "github-output"
            with mock.patch.dict(os.environ, {"GITHUB_OUTPUT": str(output)}):
                with self.assertRaisesRegex(ValueError, "invalid GitHub output key"):
                    github_output.emit_outputs(**{"bad-key": "value"})


if __name__ == "__main__":
    unittest.main()
