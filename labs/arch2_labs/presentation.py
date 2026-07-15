from __future__ import annotations

from typing import Any

OBJECTIVE_LABELS = {
    "latency_under_declared_gates": "Lowest latency",
    "energy_under_declared_gates": "Lowest first-order energy",
    "area_efficiency_under_declared_gates": "Highest area efficiency",
}


def render_objective_summary(evidence: dict[str, Any]) -> str:
    rankings = evidence.get("objective_rankings")
    if not isinstance(rankings, dict):
        raise ValueError("supporting evidence record has no objective rankings")
    lines = []
    for objective, label in OBJECTIVE_LABELS.items():
        ranking = rankings.get(objective)
        if not isinstance(ranking, dict) or not ranking.get("candidate_id"):
            raise ValueError(
                f"supporting evidence record is missing objective: {objective}"
            )
        lines.append(
            f"- **{label}.** `{ranking['candidate_id']}` ({ranking['value']})."
        )
    return """### Candidate Rankings After the Rejection Checks

Each ranking below considers only candidates that passed the declared area and
deadline checks.

{rankings}

The program recommends the lowest-latency candidate in that set. A decision
owner may choose another candidate only after naming the governing objective and
explaining the change.
""".format(
        rankings="\n".join(lines)
    )


def render_receipt_validation(errors: list[str]) -> str:
    if errors:
        details = "\n".join(f"- `{error}`" for error in errors)
        return (
            "🛑 **Run archive invalid.** The decision could not be completed or the "
            f"resulting archive failed validation.\n\n{details}"
        )
    return (
        "✅ **Run archive valid.** Your objective, candidate choice, rationale, "
        "and authorized next step are stored separately from the machine recommendation."
    )
