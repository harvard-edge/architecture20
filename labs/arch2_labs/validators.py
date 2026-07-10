from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REQUIRED_FILES = [
    "card.yaml",
    "environment.yaml",
    "candidates.jsonl",
    "runs.jsonl",
    "evidence_ledger.json",
    "negative_traces.jsonl",
    "decision.md",
]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open() as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL row") from exc
    return rows


def validate_receipt(receipt_dir: Path) -> list[str]:
    errors: list[str] = []
    receipt_dir = receipt_dir.resolve()

    for name in REQUIRED_FILES:
        if not (receipt_dir / name).exists():
            errors.append(f"missing required file: {name}")
    if errors:
        return errors

    card = yaml.safe_load((receipt_dir / "card.yaml").read_text())
    environment = yaml.safe_load((receipt_dir / "environment.yaml").read_text())
    candidates = read_jsonl(receipt_dir / "candidates.jsonl")
    runs = read_jsonl(receipt_dir / "runs.jsonl")
    negative_traces = read_jsonl(receipt_dir / "negative_traces.jsonl")
    evidence = json.loads((receipt_dir / "evidence_ledger.json").read_text())
    decision = (receipt_dir / "decision.md").read_text()

    for field in [
        "schema_version",
        "lab_id",
        "claim",
        "commitment_boundary",
        "human_owner",
    ]:
        if not card.get(field):
            errors.append(f"card.yaml missing field: {field}")

    for field in [
        "legal_actions",
        "invalid_actions",
        "observations",
        "rejection_authority",
    ]:
        if not environment.get(field):
            errors.append(f"environment.yaml missing field: {field}")

    if not candidates:
        errors.append("candidates.jsonl has no candidates")
    if not any(run.get("stage") == "proxy" for run in runs):
        errors.append("runs.jsonl has no proxy stage")
    if not any(
        run.get("stage") == "scalesim" and run.get("status") == "ok" for run in runs
    ):
        errors.append("runs.jsonl has no successful SCALE-Sim stage")
    if not negative_traces:
        errors.append("negative_traces.jsonl is empty")

    stages = {stage.get("stage") for stage in evidence.get("stages", [])}
    if "proxy" not in stages:
        errors.append("evidence_ledger.json has no proxy evidence stage")
    if "scalesim" not in stages:
        errors.append("evidence_ledger.json has no SCALE-Sim evidence stage")
    if evidence.get("final_decision_source") != "scalesim":
        errors.append(
            "final decision must cite SCALE-Sim, not the proxy, as the decision source"
        )

    if "## Commitment Boundary" not in decision:
        errors.append("decision.md lacks a Commitment Boundary section")
    if "## Would Overturn This Decision" not in decision:
        errors.append("decision.md lacks a Would Overturn This Decision section")

    banned_claims = [
        "tapeout-ready",
        "ready for tapeout",
        "ready for rtl",
        "product-ready",
    ]
    lowered = decision.lower()
    for claim in banned_claims:
        if claim in lowered:
            errors.append(f"decision.md appears to overclaim: {claim}")

    # NOTE: the validator intentionally does NOT judge which candidate "should"
    # win, and does not require the proxy winner and the survivor to differ.
    # Forcing a mismatch would manufacture a mirage and teach that a hidden
    # canonical answer exists. The validator checks completeness, consistency,
    # and that the final decision cites stronger evidence than the proxy; the
    # architectural judgment is the learner's.

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an Architecture 2.0 loop receipt."
    )
    parser.add_argument("receipt_dir", type=Path)
    args = parser.parse_args(argv)
    errors = validate_receipt(args.receipt_dir)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"receipt ok: {args.receipt_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
