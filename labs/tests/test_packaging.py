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
        "design-loop-card.v2.schema.json",
    ):
        canonical = labs_root.parent / "schemas" / name
        packaged = labs_root / "arch2_labs" / "resources" / name

        assert packaged.read_bytes() == canonical.read_bytes()


def test_installed_wheel_finds_activities_fixtures_and_card_schema(
    tmp_path: Path,
) -> None:
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

package_root = Path(arch2_labs.__file__).parent
example = example_dir("scale_proxy_mirage")
spec = load_candidates(example / "configs" / "candidates.yaml", example)
card = yaml.safe_load((example / "starter_receipt" / "card.yaml").read_text())
activities = [
    package_root / "notebooks/lab_01_prompt_to_card.py",
    package_root / "notebooks/lab_02_scissors_gap.py",
    package_root / "notebooks/lab_03_score_a_claim.py",
    package_root / "notebooks/lab_04_represent_and_replay.py",
    package_root / "notebooks/lab_05_environment_contract.py",
    package_root / "examples/scale_proxy_mirage/lab.py",
    package_root / "notebooks/lab_07_earned_trust.py",
    package_root / "notebooks/lab_08_run_the_loop.py",
    package_root / "notebooks/lab_09_same_loop_different_costs.py",
    package_root / "notebooks/lab_10_own_the_commitment.py",
]
fixture = json.loads(
    (package_root / "fixtures/alphachip_public_record_card.json").read_text()
)
print(json.dumps({
    "module": arch2_labs.__file__,
    "example": str(example),
    "activity_count": len(activities),
    "missing_activities": [str(path) for path in activities if not path.is_file()],
    "fixture_field_count": len(fixture["card_fields"]),
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
    assert result["activity_count"] == 10
    assert result["missing_activities"] == []
    assert result["fixture_field_count"] == 12
    assert result["candidate_count"] == 4
    assert result["schema_title"] == "Architecture 2.0 Design-Loop Card"
    assert result["schema_version"] == "2.0"
    assert result["card_errors"] == []
