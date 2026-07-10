from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_action_pins.py"
SPEC = importlib.util.spec_from_file_location("check_action_pins", SCRIPT)
assert SPEC and SPEC.loader
action_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = action_check
SPEC.loader.exec_module(action_check)


class ActionPinTests(unittest.TestCase):
    def workflow(self, uses: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "workflow.yml"
        path.write_text(f"steps:\n  - uses: {uses}\n")
        return path

    def test_full_commit_with_version_comment_passes(self) -> None:
        path = self.workflow(
            "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4"
        )
        self.assertEqual(action_check.check_workflow(path), [])

    def test_mutable_tag_fails(self) -> None:
        path = self.workflow("actions/checkout@v4")
        errors = action_check.check_workflow(path)
        self.assertTrue(any("mutable" in error for error in errors))

    def test_missing_version_comment_fails(self) -> None:
        path = self.workflow(
            "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5"
        )
        errors = action_check.check_workflow(path)
        self.assertTrue(any("version comment" in error for error in errors))

    def test_local_action_passes_without_pin(self) -> None:
        self.assertEqual(
            action_check.check_workflow(self.workflow("./.github/actions/x")), []
        )


if __name__ == "__main__":
    unittest.main()
