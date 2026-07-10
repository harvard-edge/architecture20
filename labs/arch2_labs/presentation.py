from __future__ import annotations

from typing import Any

OBJECTIVE_LABELS = {
    "latency_under_declared_gates": "Lowest latency",
    "energy_under_declared_gates": "Lowest first-order energy",
    "area_efficiency_under_declared_gates": "Highest area efficiency",
}


def render_objective_summary(ledger: dict[str, Any]) -> str:
    rankings = ledger.get("objective_rankings")
    if not isinstance(rankings, dict):
        raise ValueError("evidence ledger has no objective rankings")
    lines = []
    for objective, label in OBJECTIVE_LABELS.items():
        ranking = rankings.get(objective)
        if not isinstance(ranking, dict) or not ranking.get("candidate_id"):
            raise ValueError(f"evidence ledger is missing objective: {objective}")
        lines.append(
            f"- **{label}.** `{ranking['candidate_id']}` ({ranking['value']})."
        )
    return """### No Single Metric Owns the Commitment

Each ranking below considers only candidates that passed the declared gates.

{rankings}

The machine recommendation follows the gate-filtered latency objective. A human
may choose another gate passer only by recording an explicit, justified objective
override.
""".format(
        rankings="\n".join(lines)
    )


def render_receipt_validation(errors: list[str]) -> str:
    if errors:
        details = "\n".join(f"- `{error}`" for error in errors)
        return (
            "🛑 **Receipt invalid.** The decision was recorded, but the receipt "
            f"failed validation.\n\n{details}"
        )
    return (
        "✅ **Receipt valid.** Your explicit objective, candidate choice, rationale, "
        "and commitment are persisted separately from the machine recommendation."
    )
