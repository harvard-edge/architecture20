from __future__ import annotations

import re
import tomllib
import unittest
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
LABS = ROOT / "labs"
LOCKS = {
    "3.10.20": "constraints/py310-linux.txt",
    "3.11.15": "constraints/py311-linux.txt",
}
PIN_RE = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[^]]+\])?==[^;\s]+(?:\s*;.*)?$")


class DependencyContractTests(unittest.TestCase):
    def test_lab_build_backend_is_pinned_and_installed_for_ci(self) -> None:
        project = tomllib.loads((LABS / "pyproject.toml").read_text())
        self.assertEqual(project["build-system"]["requires"], ["hatchling==1.31.0"])
        self.assertIn(
            "hatchling==1.31.0",
            project["project"]["optional-dependencies"]["dev"],
        )

    def test_lab_locks_contain_only_exact_package_pins(self) -> None:
        for relative_path in LOCKS.values():
            path = LABS / relative_path
            self.assertTrue(path.is_file(), path)
            requirements = [
                line
                for line in path.read_text().splitlines()
                if line and not line.startswith((" ", "#"))
            ]
            self.assertTrue(requirements, path)
            for requirement in requirements:
                self.assertRegex(requirement, PIN_RE, f"{path}: {requirement}")
            for package in ("build", "hatchling", "marimo", "pytest", "scalesim"):
                self.assertTrue(
                    any(
                        line.lower().startswith(f"{package}==") for line in requirements
                    ),
                    f"{path} does not pin {package}",
                )

    def test_lab_ci_uses_version_matched_locks_end_to_end(self) -> None:
        workflow = yaml.safe_load(
            (ROOT / ".github" / "workflows" / "validate.yml").read_text()
        )
        job = workflow["jobs"]["labs"]
        matrix = job["strategy"]["matrix"]["include"]
        self.assertEqual(
            {entry["python-version"]: entry["constraints"] for entry in matrix},
            LOCKS,
        )

        setup = next(step for step in job["steps"] if step["name"] == "Set up Python")
        self.assertIn(
            "labs/${{ matrix.constraints }}", setup["with"]["cache-dependency-path"]
        )

        install = next(
            step
            for step in job["steps"]
            if step["name"] == "Install source and test dependencies"
        )["run"]
        self.assertIn('"hatchling==1.31.0"', install)
        self.assertIn("--no-build-isolation", install)
        self.assertIn('-c "${{ matrix.constraints }}"', install)
        self.assertNotIn(' -e ".[dev,notebook]"', install)
        self.assertIn("python -m pip check", install)

        build = next(
            step
            for step in job["steps"]
            if step["name"] == "Build distribution artifacts"
        )["run"]
        self.assertEqual(build, "python -m build --no-isolation")

        smoke = next(
            step
            for step in job["steps"]
            if step["name"] == "Smoke-test installed wheel outside the checkout"
        )["run"]
        self.assertIn('-c "$constraints" "$wheel"', smoke)
        self.assertIn('"$smoke_dir/venv/bin/python" -m pip check', smoke)


if __name__ == "__main__":
    unittest.main()
