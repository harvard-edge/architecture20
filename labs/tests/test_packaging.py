from __future__ import annotations

import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path


def test_packaged_card_schema_matches_canonical_source() -> None:
    labs_root = Path(__file__).resolve().parents[1]
    for name in (
        "design-loop-card.v1.schema.json",
        "design-loop-card.v1.1.schema.json",
    ):
        canonical = labs_root.parent / "schemas" / name
        packaged = labs_root / "arch2_labs" / "resources" / name

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
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(target)

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
from arch2_labs.validators import _card_errors, _card_schema
import yaml

example = example_dir("scale_proxy_mirage")
spec = load_candidates(example / "configs" / "candidates.yaml", example)
card = yaml.safe_load((example / "starter_receipt" / "card.yaml").read_text())
print(json.dumps({
    "module": arch2_labs.__file__,
    "example": str(example),
    "candidate_count": len(spec.candidates),
    "schema_title": _card_schema()["title"],
    "schema_version": _card_schema()["properties"]["schema_version"]["const"],
    "card_errors": _card_errors(card),
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
    assert result["schema_version"] == "1.1"
    assert result["card_errors"] == []
