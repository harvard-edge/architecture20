from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def test_packaged_card_schema_matches_canonical_source() -> None:
    labs_root = Path(__file__).resolve().parents[1]
    canonical = labs_root.parent / "schemas" / "design-loop-card.v1.schema.json"
    packaged = labs_root / "arch2_labs" / "resources" / canonical.name

    assert packaged.read_bytes() == canonical.read_bytes()


def test_installed_wheel_finds_examples_and_card_schema(tmp_path: Path) -> None:
    labs_root = Path(__file__).resolve().parents[1]
    dist_dir = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--outdir", str(dist_dir)],
        cwd=labs_root,
        check=True,
        capture_output=True,
        text=True,
    )
    wheel = next(dist_dir.glob("arch2_labs-*.whl"))
    target = tmp_path / "installed"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(target),
            str(wheel),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    outside = tmp_path / "outside-source"
    outside.mkdir()
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(target)
    script = """
import json
from pathlib import Path
import arch2_labs
from arch2_labs.scale_env import example_dir
from arch2_labs.schemas import load_candidates
from arch2_labs.validators import _card_schema

example = example_dir("scale_proxy_mirage")
spec = load_candidates(example / "configs" / "candidates.yaml", example)
print(json.dumps({
    "module": arch2_labs.__file__,
    "example": str(example),
    "candidate_count": len(spec.candidates),
    "schema_title": _card_schema()["title"],
}))
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=outside,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout)

    assert Path(result["module"]).is_relative_to(target)
    assert Path(result["example"]).is_relative_to(target)
    assert result["candidate_count"] == 4
    assert result["schema_title"] == "Architecture 2.0 Design-Loop Card"
