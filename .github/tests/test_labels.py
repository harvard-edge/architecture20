from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "check_labels.py"
SPEC = importlib.util.spec_from_file_location("check_labels", SCRIPT)
assert SPEC and SPEC.loader
label_check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = label_check
SPEC.loader.exec_module(label_check)


class LabelCheckTests(unittest.TestCase):
    def make_root(self, manifest: str, form: str, workflow: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        (root / ".github" / "ISSUE_TEMPLATE").mkdir(parents=True)
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "labels.yml").write_text(manifest)
        (root / ".github" / "ISSUE_TEMPLATE" / "form.yml").write_text(form)
        (root / ".github" / "workflows" / "flow.yml").write_text(workflow)
        return root

    def test_declared_form_and_workflow_labels_pass(self) -> None:
        root = self.make_root(
            "- name: intake\n  color: '123abc'\n  description: Intake\n"
            "- name: review\n  color: 'abcdef'\n  description: Review\n",
            "name: Form\nlabels: [intake]\n",
            "jobs:\n  act:\n    steps:\n      - with:\n          labels: review\n",
        )
        self.assertEqual(label_check.check_labels(root), [])

    def test_undeclared_condition_label_fails(self) -> None:
        root = self.make_root(
            "- name: intake\n  color: '123abc'\n  description: Intake\n",
            "name: Form\nlabels: [intake]\n",
            "jobs:\n  act:\n    if: contains(github.event.issue.labels.*.name, 'missing')\n",
        )
        errors = label_check.check_labels(root)
        self.assertTrue(any("missing" in error for error in errors))

    def test_yaml_extension_is_checked(self) -> None:
        root = self.make_root(
            "- name: intake\n  color: '123abc'\n  description: Intake\n",
            "name: Form\nlabels: [intake]\n",
            "jobs: {}\n",
        )
        (root / ".github" / "workflows" / "extra.yaml").write_text(
            "jobs:\n  act:\n    steps:\n      - with:\n          labels: missing\n"
        )
        errors = label_check.check_labels(root)
        self.assertTrue(any("missing" in error for error in errors))

    def test_duplicate_and_invalid_manifest_entries_fail(self) -> None:
        root = self.make_root(
            "- name: intake\n  color: nope\n  description: ''\n"
            "- name: intake\n  color: '123abc'\n  description: Duplicate\n",
            "name: Form\nlabels: [intake]\n",
            "jobs: {}\n",
        )
        errors = label_check.check_labels(root)
        self.assertGreaterEqual(len(errors), 3)


if __name__ == "__main__":
    unittest.main()
