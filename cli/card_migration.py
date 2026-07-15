"""Deterministic, non-inventive migration support for design-loop cards."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


MIGRATION_DRAFT_VERSION = "arch2-design-loop-card-migration-draft/v1"
SOURCE_VERSION = "1.1"
TARGET_VERSION = "2.0"


def _missing(target: str, reason: str) -> dict[str, str]:
    return {"target": target, "reason": reason}


def migrate_v1_1_to_v2_draft(document: Mapping[str, Any]) -> dict[str, Any]:
    """Map only v1.1 content with a direct v2 meaning.

    The result is deliberately a migration draft, not a schema-valid v2 card.
    Missing claim status, evidence status, replay validation, and decision rights
    require author input and are listed explicitly.
    """
    if document.get("schema_version") != SOURCE_VERSION:
        raise ValueError("migration accepts only design-loop card schema version '1.1'")
    source = document.get("design_loop_card")
    if not isinstance(source, Mapping):
        raise ValueError("design_loop_card must be a mapping")

    mapped: dict[str, Any] = {}
    missing: list[dict[str, str]] = []
    legacy_unmapped: dict[str, Any] = {}

    for field in ("card_id", "design_space"):
        if field in source:
            mapped[field] = deepcopy(source[field])

    intent = source.get("intent")
    if isinstance(intent, Mapping):
        mapped_intent = {
            key: deepcopy(intent[key])
            for key in (
                "objective",
                "constraints",
                "non_goals",
                "risks",
                "deployment_assumptions",
            )
            if key in intent
        }
        mapped["intent"] = mapped_intent
        claim_boundary = intent.get("claim_boundary")
        if isinstance(claim_boundary, Mapping):
            partial_claim: dict[str, Any] = {}
            if claim_boundary.get("claim"):
                partial_claim["statement"] = deepcopy(claim_boundary["claim"])
            if claim_boundary.get("non_claim"):
                partial_claim["non_claims"] = [deepcopy(claim_boundary["non_claim"])]
            mapped["claims"] = [partial_claim]
            for field in (
                "claim_id",
                "claim_type",
                "baseline_or_comparator",
                "outcome",
                "scope",
                "status",
                "evidence_refs",
            ):
                missing.append(
                    _missing(
                        f"design_loop_card.claims[0].{field}",
                        "v1.1 claim_boundary does not encode this v2 claim meaning",
                    )
                )
        else:
            mapped["claims"] = []
            missing.append(
                _missing(
                    "design_loop_card.claims",
                    "v2 requires at least one typed architectural claim",
                )
            )

    task = source.get("task")
    if isinstance(task, str):
        mapped["task"] = {"kind": task}
        missing.append(
            _missing(
                "design_loop_card.task.description",
                "v1.1 records only a closed task label, not a task description",
            )
        )

    representation = source.get("representation")
    if isinstance(representation, Mapping):
        mapped_representation = {
            key: deepcopy(representation[key])
            for key in ("state_schema_id", "reads", "writes", "uncertainties")
            if key in representation
        }
        if "ir_level" in representation:
            mapped_representation["abstraction"] = deepcopy(representation["ir_level"])
        mapped["representation"] = mapped_representation

    if isinstance(source.get("environment"), Mapping):
        mapped["environment"] = deepcopy(source["environment"])

    method_role = source.get("method_role")
    if isinstance(method_role, Mapping):
        actor_map = method_role.get("actor_map")
        if isinstance(actor_map, list):
            mapped_roles = []
            for index, actor in enumerate(actor_map):
                if not isinstance(actor, Mapping):
                    continue
                partial_role = {
                    key: deepcopy(actor[key])
                    for key in ("actor_id", "reads", "writes")
                    if key in actor
                }
                partial_role["x-arch2-legacy"] = {
                    key: deepcopy(actor[key])
                    for key in ("role", "authority")
                    if key in actor
                }
                mapped_roles.append(partial_role)
                for field in ("actor_type", "roles", "limitations"):
                    missing.append(
                        _missing(
                            f"design_loop_card.method_roles[{index}].{field}",
                            "v1.1 actor records do not encode this v2 field",
                        )
                    )
            mapped["method_roles"] = mapped_roles
        if "roles" in method_role:
            legacy_unmapped["method_role.roles"] = deepcopy(method_role["roles"])

    feedback = source.get("feedback_budget")
    if isinstance(feedback, Mapping):
        mapped_feedback = {
            key: deepcopy(feedback[key])
            for key in ("evaluations", "latency", "fidelity")
            if key in feedback
        }
        if "cost" in feedback:
            mapped_feedback["compute_or_tool_cost"] = deepcopy(feedback["cost"])
        model_cost = feedback.get("model_side_cost")
        if isinstance(model_cost, Mapping):
            for key in ("model_calls", "energy_or_carbon", "human_review"):
                if key in model_cost:
                    mapped_feedback[key] = deepcopy(model_cost[key])
            if "gpu_hours" in model_cost:
                legacy_unmapped["feedback_budget.model_side_cost.gpu_hours"] = deepcopy(
                    model_cost["gpu_hours"]
                )
        mapped["feedback_budget"] = mapped_feedback

    source_evidence = source.get("evidence")
    mapped_records: list[dict[str, Any]] = []
    if isinstance(source_evidence, Mapping):
        records = source_evidence.get("records")
        if isinstance(records, list):
            for index, record in enumerate(records):
                if not isinstance(record, Mapping):
                    continue
                partial_record = {
                    key: deepcopy(record[key])
                    for key in ("evidence_id", "kind")
                    if key in record
                }
                legacy = {
                    key: deepcopy(record[key])
                    for key in ("workload_id", "seed", "provenance")
                    if key in record
                }
                if legacy:
                    partial_record["x-arch2-legacy"] = legacy
                mapped_records.append(partial_record)
                for field in (
                    "producer",
                    "status",
                    "tool",
                    "inputs",
                    "outputs",
                    "scope",
                    "limitations",
                    "integrity",
                ):
                    missing.append(
                        _missing(
                            f"design_loop_card.evidence.records[{index}].{field}",
                            "v1.1 evidence does not encode this v2 meaning without interpretation",
                        )
                    )
        for key in (
            "baseline_id",
            "resource_or_sustainability_boundary",
            "telemetry_packet",
            "integrity_manifest",
        ):
            if key in source_evidence:
                legacy_unmapped[f"evidence.{key}"] = deepcopy(source_evidence[key])
    mapped["evidence"] = {"records": mapped_records}

    source_traces = source.get("negative_traces")
    mapped_traces: list[dict[str, Any]] = []
    if isinstance(source_traces, list):
        for index, trace in enumerate(source_traces):
            if not isinstance(trace, Mapping):
                continue
            partial_trace = {
                key: deepcopy(trace[key])
                for key in ("candidate_id", "stage", "reason")
                if key in trace
            }
            if "gate" in trace:
                partial_trace["x-arch2-legacy"] = {"gate": deepcopy(trace["gate"])}
            mapped_traces.append(partial_trace)
            for field in ("record_id", "kind", "evidence_refs"):
                missing.append(
                    _missing(
                        f"design_loop_card.failed_or_rejected[{index}].{field}",
                        "v1.1 negative traces do not encode this v2 meaning",
                    )
                )
    mapped["failed_or_rejected"] = mapped_traces

    disclosure = source.get("disclosure_boundary")
    if isinstance(disclosure, Mapping):
        mapped["disclosure"] = deepcopy(disclosure)

    human_decision = source.get("human_decision")
    if isinstance(human_decision, Mapping):
        partial_decision: dict[str, Any] = {}
        if "owner" in human_decision:
            partial_decision["holder_id"] = deepcopy(human_decision["owner"])
        if "authorizes" in human_decision:
            partial_decision["action"] = deepcopy(human_decision["authorizes"])
        mapped["accountable_decision"] = partial_decision
        for field in (
            "status",
            "rationale",
            "claim_refs",
            "authorized_scope",
            "reopen_conditions",
        ):
            missing.append(
                _missing(
                    f"design_loop_card.accountable_decision.{field}",
                    "v1.1 human_decision does not encode this v2 meaning",
                )
            )

    for field in (
        "conformance_level",
        "rejection_authority",
        "commitment_boundary",
    ):
        if field in source:
            legacy_unmapped[field] = deepcopy(source[field])

    missing.extend(
        [
            _missing(
                "design_loop_card.profiles",
                "cumulative v1.1 levels cannot establish independent v2 profile status",
            ),
            _missing(
                "design_loop_card.profile_gaps",
                "an author must record gaps for every partial v2 profile",
            ),
            _missing(
                "design_loop_card.gates",
                "v1.1 gate prose lacks typed category, criterion, result, authority, waiver rule, and evidence links",
            ),
            _missing(
                "design_loop_card.decision_rights",
                "v1.1 does not separately assign propose, execute, reject, waive, recommend, and commit rights",
            ),
            _missing(
                "design_loop_card.replay",
                "v1.1 replay pointers do not establish commands, environment, inputs, outputs, expected status, and validated hashes",
            ),
        ]
    )

    extension_fields = {
        key: deepcopy(value)
        for key, value in source.items()
        if isinstance(key, str) and key.startswith("x-")
    }
    if extension_fields:
        mapped.update(extension_fields)

    return {
        "migration_draft_version": MIGRATION_DRAFT_VERSION,
        "source_schema_version": SOURCE_VERSION,
        "target_schema_version": TARGET_VERSION,
        "status": "requires_author_input",
        "mapped_design_loop_card": mapped,
        "missing_semantics": missing,
        "legacy_unmapped": legacy_unmapped,
        "instructions": (
            "Resolve every missing_semantics entry, then place the completed mapping "
            "under schema_version '2.0' and design_loop_card and validate it."
        ),
    }
