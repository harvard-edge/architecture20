from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / ".github" / "scripts"


class SubmissionContractTests(unittest.TestCase):
    def test_tool_submission_starts_unverified_without_date(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "registry"
            registry.mkdir()
            body = """### Tool name
Contract Test Tool
### Repository or website URL
https://example.com/tool
### Artifact type
Tool
### Primary category
Simulation
### Short description
A test simulator entry.
### Why does this belong in Architecture 2.0?
It supplies executable feedback.
"""
            environment = os.environ.copy()
            environment.update(
                {
                    "ISSUE_BODY": body,
                    "ARCH2_TOOL_REGISTRY": str(registry),
                    "ARCH2_TOOL_INDEX": str(root / "tools.yml"),
                }
            )
            subprocess.run(
                [sys.executable, str(SCRIPTS / "add_tool_from_issue.py")],
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            entry = yaml.safe_load((registry / "contract-test-tool.yml").read_text())
            self.assertEqual(entry["artifact_availability"], "unverified")
            self.assertNotIn("last_verified", entry)

    def test_workshop_submission_is_proposed_with_iso_dates(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "workshops"
            registry.mkdir()
            body = """### Workshop or venue name
Contract Test Workshop
### Website URL
https://example.com/workshop
### Venue or host
ExampleConf
### Date or year
September 2099
### Event start date
2099-09-10
### Event end date
2099-09-11
### Primary topic
Architecture 2.0
### Short description
A contract test workshop.
"""
            environment = os.environ.copy()
            environment.update(
                {
                    "ISSUE_BODY": body,
                    "ARCH2_WORKSHOP_REGISTRY": str(registry),
                    "ARCH2_WORKSHOP_INDEX": str(root / "workshops.yml"),
                }
            )
            subprocess.run(
                [sys.executable, str(SCRIPTS / "add_workshop_from_issue.py")],
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            entry = yaml.safe_load(
                (registry / "contract-test-workshop.yml").read_text()
            )
            self.assertEqual(entry["status"], "proposed")
            self.assertEqual(str(entry["event_start"]), "2099-09-10")
            self.assertEqual(str(entry["event_end"]), "2099-09-11")
            self.assertNotIn("last_verified", entry)

    def test_workshop_form_requires_machine_readable_dates(self) -> None:
        form = yaml.safe_load(
            (ROOT / ".github" / "ISSUE_TEMPLATE" / "submit_workshop.yml").read_text()
        )
        fields = {item.get("id"): item for item in form["body"] if item.get("id")}
        for field_id in ("event_start", "event_end"):
            self.assertIn(field_id, fields)
            self.assertTrue(fields[field_id]["validations"]["required"])
            self.assertEqual(
                fields[field_id]["attributes"]["placeholder"], "2026-06-27"
            )

    def test_workshop_submission_rejects_invalid_date_order(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "workshops"
            registry.mkdir()
            body = """### Workshop or venue name
Invalid Date Workshop
### Website URL
https://example.com/invalid
### Venue or host
ExampleConf
### Date or year
September 2099
### Event start date
2099-09-12
### Event end date
2099-09-11
### Primary topic
Architecture 2.0
### Short description
An invalid contract test workshop.
"""
            environment = os.environ.copy()
            environment.update(
                {
                    "ISSUE_BODY": body,
                    "ARCH2_WORKSHOP_REGISTRY": str(registry),
                    "ARCH2_WORKSHOP_INDEX": str(root / "workshops.yml"),
                }
            )
            completed = subprocess.run(
                [sys.executable, str(SCRIPTS / "add_workshop_from_issue.py")],
                cwd=ROOT,
                env=environment,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn("end date must not be before", completed.stdout)
            self.assertEqual(list(registry.glob("*.yml")), [])

    def test_tool_form_discloses_unverified_default(self) -> None:
        form = yaml.safe_load(
            (ROOT / ".github" / "ISSUE_TEMPLATE" / "submit_tool.yml").read_text()
        )
        introduction = form["body"][0]["attributes"]["value"]
        self.assertIn("unverified", introduction)

    def test_generated_pull_requests_target_dev(self) -> None:
        workflow_dir = ROOT / ".github" / "workflows"
        for name in ("tool", "workshop", "resource"):
            workflow = yaml.safe_load(
                (workflow_dir / f"process-{name}-submission.yml").read_text()
            )
            steps = workflow["jobs"]["create_pr_from_issue"]["steps"]
            checkout = next(
                step for step in steps if step["name"] == "Check out repository"
            )
            create_pr = next(
                step for step in steps if step["name"] == "Create pull request"
            )
            self.assertEqual(checkout["with"]["ref"], "dev")
            self.assertFalse(checkout["with"]["persist-credentials"])
            self.assertEqual(create_pr["with"]["base"], "dev")


if __name__ == "__main__":
    unittest.main()
