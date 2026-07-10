from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml

from arch2_labs.receipts import ReceiptMetadata, seal_receipt, verify_receipt_ownership

HUMAN_DECISION_SCHEMA_VERSION = "arch2-human-decision/v0.1"
SUPPORTED_COMMITMENT_LEVELS = {"next_fidelity_study"}
SUPPORTED_OBJECTIVES = {
    "latency_under_declared_gates",
    "energy_under_declared_gates",
    "area_efficiency_under_declared_gates",
}

OVERCLAIM_PATTERNS = {
    "advance to RTL": re.compile(
        r"\badvance(?:s|d|ing)?\s+(?:this\s+\w+\s+)?to\s+rtl\b", re.I
    ),
    "RTL-ready": re.compile(r"\b(?:rtl[- ]ready|ready\s+for\s+rtl)\b", re.I),
    "signoff-ready": re.compile(
        r"\b(?:sign[- ]?off[- ]ready|ready\s+for\s+sign[- ]?off)\b", re.I
    ),
    "tapeout-ready": re.compile(
        r"\b(?:tape[- ]?out[- ]ready|ready\s+for\s+tape[- ]?out)\b", re.I
    ),
    "product commitment": re.compile(
        r"\b(?:commit(?:s|ted|ting)?\s+(?:this\s+\w+\s+)?to\s+(?:the\s+)?product|product[- ]ready|ready\s+for\s+(?:the\s+)?product)\b",
        re.I,
    ),
}


@dataclass(frozen=True)
class HumanDecision:
    schema_version: str
    lab_id: str
    human_owner: str
    authored_at: str
    selected_candidate_id: str
    governing_objective: str
    commitment_level: str
    rationale: str
    residual_risk: str
    would_overturn: str


def decision_errors(data: Any) -> list[str]:
    if not isinstance(data, Mapping):
        return ["decision.yaml must contain a mapping"]
    errors: list[str] = []
    fields = [field.name for field in HumanDecision.__dataclass_fields__.values()]
    for field in fields:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"decision.yaml missing field: {field}")
    if (
        data.get("schema_version")
        and data.get("schema_version") != HUMAN_DECISION_SCHEMA_VERSION
    ):
        errors.append(
            f"unsupported human decision schema: {data.get('schema_version')}"
        )
    level = data.get("commitment_level")
    if level and level not in SUPPORTED_COMMITMENT_LEVELS:
        errors.append(f"unsupported commitment level: {level}")
    objective = data.get("governing_objective")
    if objective and objective not in SUPPORTED_OBJECTIVES:
        errors.append(f"unsupported governing objective: {objective}")
    for field in ("rationale", "residual_risk", "would_overturn"):
        value = data.get(field)
        if not isinstance(value, str):
            continue
        for label, pattern in OVERCLAIM_PATTERNS.items():
            if pattern.search(value):
                errors.append(f"decision.yaml appears to overclaim in {field}: {label}")
    return errors


def parse_human_decision(data: Mapping[str, Any]) -> HumanDecision:
    errors = decision_errors(data)
    if errors:
        raise ValueError("; ".join(errors))
    return HumanDecision(
        **{
            field: str(data[field]).strip()
            for field in HumanDecision.__dataclass_fields__
        }
    )


def load_human_decision(
    source: Path | Mapping[str, Any] | HumanDecision,
) -> HumanDecision:
    if isinstance(source, HumanDecision):
        return source
    if isinstance(source, Path):
        try:
            data = yaml.safe_load(source.read_text())
        except (OSError, yaml.YAMLError) as exc:
            raise ValueError(f"could not read human decision: {source}") from exc
        if not isinstance(data, Mapping):
            raise ValueError("human decision file must contain a mapping")
        return parse_human_decision(data)
    return parse_human_decision(source)


def render_decision(decision: HumanDecision) -> str:
    return f"""# Human Decision

Human owner: {decision.human_owner}

Authored at: {decision.authored_at}

Selected candidate: `{decision.selected_candidate_id}`

Governing objective: `{decision.governing_objective}`

## Rationale

{decision.rationale}

## Commitment Boundary

`{decision.commitment_level}`

This commitment advances only to a next-fidelity architecture study. It does
not establish implementation readiness, physical feasibility, or product
suitability.

## Residual Risk

{decision.residual_risk}

## Would Overturn This Decision

{decision.would_overturn}
"""


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def _record_decision_in_card(receipt_dir: Path, decision: HumanDecision) -> None:
    card_path = receipt_dir / "card.yaml"
    document = yaml.safe_load(card_path.read_text())
    card = document["design_loop_card"]
    card.update(
        {
            "conformance_level": 3,
            "rejection_authority": {
                "gates": [
                    "Reject candidates above the 1024-PE silicon budget.",
                    "Reject candidates above the 90000-cycle workload deadline.",
                ],
                "independent_of_producer": True,
                "independence_basis": "The fixed area and deadline gates execute independently of the machine recommendation and the human decision.",
            },
            "commitment_boundary": {
                "level": "experimental",
                "strongest_supported_claim": (
                    f"Advance {decision.selected_candidate_id} to one bounded "
                    "next-fidelity architecture study."
                ),
                "would_overturn": decision.would_overturn,
            },
            "human_decision": {
                "owner": decision.human_owner,
                "authorizes": (
                    f"{decision.selected_candidate_id} at "
                    f"{decision.commitment_level}; no broader commitment."
                ),
            },
        }
    )
    card["x-arch2-labs"].update(
        {
            "template_status": "human_decision_recorded",
            "learner_decision": {
                "authored_at": decision.authored_at,
                "selected_candidate_id": decision.selected_candidate_id,
                "governing_objective": decision.governing_objective,
                "rationale": decision.rationale,
                "residual_risk": decision.residual_risk,
            },
        }
    )
    card_path.write_text(yaml.safe_dump(document, sort_keys=False))


def record_human_decision(
    receipt_dir: Path,
    source: Path | Mapping[str, Any] | HumanDecision,
) -> HumanDecision:
    """Persist an explicit human decision and reseal an existing draft receipt."""
    receipt_dir = receipt_dir.absolute()
    manifest = verify_receipt_ownership(receipt_dir)
    decision = load_human_decision(source)
    if decision.lab_id != manifest.get("lab_id"):
        raise ValueError(
            "human decision lab_id does not match the receipt: "
            f"{decision.lab_id} != {manifest.get('lab_id')}"
        )

    candidates = _read_jsonl(receipt_dir / "candidates.jsonl")
    candidate_ids = {record.get("candidate_id") for record in candidates}
    if decision.selected_candidate_id not in candidate_ids:
        raise ValueError(
            "human decision selected_candidate_id is not a declared candidate: "
            f"{decision.selected_candidate_id}"
        )
    rejected_ids = {
        record.get("candidate_id")
        for record in _read_jsonl(receipt_dir / "negative_traces.jsonl")
    }
    if decision.selected_candidate_id in rejected_ids:
        raise ValueError(
            "human decision selects a candidate rejected by a declared gate: "
            f"{decision.selected_candidate_id}"
        )

    (receipt_dir / "decision.yaml").write_text(
        yaml.safe_dump(asdict(decision), sort_keys=False)
    )
    (receipt_dir / "decision.md").write_text(render_decision(decision))
    _record_decision_in_card(receipt_dir, decision)
    seal_receipt(
        receipt_dir,
        ReceiptMetadata(
            receipt_id=manifest["receipt_id"],
            lab_id=manifest["lab_id"],
            example=manifest["example"],
            created_at=manifest["created_at"],
            status="complete",
        ),
    )
    return decision
