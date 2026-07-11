from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml


REQUIRED_ENVIRONMENT_FIELDS = (
    "schema_version",
    "lab_id",
    "legal_actions",
    "observations",
    "invalid_actions",
    "provenance",
    "rejection_authority",
)


def load_environment_contract(path: Path) -> dict[str, Any]:
    """Load the canonical lab environment contract and check its review surface."""
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("environment contract must contain a mapping")
    missing = [
        field
        for field in REQUIRED_ENVIRONMENT_FIELDS
        if field not in data or data[field] is None
    ]
    if missing:
        raise ValueError(
            "environment contract is missing required fields: " + ", ".join(missing)
        )
    for field in ("schema_version", "lab_id"):
        if not isinstance(data[field], str) or not data[field].strip():
            raise ValueError(f"environment {field} must be a nonempty string")
    if not isinstance(data["legal_actions"], dict) or not data["legal_actions"]:
        raise ValueError("environment legal_actions must contain a nonempty mapping")
    for field, allowed in data["legal_actions"].items():
        if not isinstance(field, str) or not field.strip():
            raise ValueError("environment legal_actions contains an invalid field name")
        if not isinstance(allowed, list) or not allowed:
            raise ValueError(
                f"environment legal_actions.{field} must be a nonempty list"
            )

    observations = data["observations"]
    if not isinstance(observations, dict) or not observations:
        raise ValueError("environment observations must contain a nonempty mapping")
    for tool, fields in observations.items():
        if not isinstance(tool, str) or not tool.strip():
            raise ValueError("environment observations contains an invalid tool name")
        if (
            not isinstance(fields, list)
            or not fields
            or any(not isinstance(field, str) or not field.strip() for field in fields)
        ):
            raise ValueError(
                f"environment observations.{tool} must be a nonempty string list"
            )

    invalid_actions = data["invalid_actions"]
    if (
        not isinstance(invalid_actions, list)
        or not invalid_actions
        or any(
            not isinstance(reason, str) or not reason.strip()
            for reason in invalid_actions
        )
    ):
        raise ValueError("environment invalid_actions must be a nonempty string list")

    provenance = data["provenance"]
    if not isinstance(provenance, dict) or not provenance:
        raise ValueError("environment provenance must contain a nonempty mapping")
    if any(
        not isinstance(key, str)
        or not key.strip()
        or not isinstance(value, str)
        or not value.strip()
        for key, value in provenance.items()
    ):
        raise ValueError(
            "environment provenance keys and values must be nonempty strings"
        )

    authorities = data["rejection_authority"]
    if not isinstance(authorities, list) or not authorities:
        raise ValueError("environment rejection_authority must contain a nonempty list")
    gate_names: set[str] = set()
    for authority in authorities:
        if not isinstance(authority, dict):
            raise ValueError("environment rejection_authority entries must be mappings")
        gate = authority.get("gate")
        threshold = authority.get("threshold")
        if not isinstance(gate, str) or not gate.strip():
            raise ValueError("environment rejection_authority entry has no gate")
        if gate in gate_names:
            raise ValueError(f"environment rejection_authority repeats gate: {gate}")
        gate_names.add(gate)
        if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
            raise ValueError(f"environment gate {gate} has no numeric threshold")
    return data


def validate_action(
    contract: Mapping[str, Any], action: Mapping[str, Any]
) -> list[str]:
    """Return contract violations for one proposed environment action."""
    legal_actions = contract.get("legal_actions")
    if not isinstance(legal_actions, Mapping):
        raise ValueError("environment legal_actions must contain a mapping")

    violations: list[str] = []
    for field, allowed in legal_actions.items():
        if field not in action:
            violations.append(f"{field} is missing from the action")
            continue
        if not isinstance(allowed, list) or not allowed:
            raise ValueError(
                f"environment legal_actions.{field} must be a nonempty list"
            )
        if action[field] not in allowed:
            allowed_text = ", ".join(str(value) for value in allowed)
            violations.append(
                f"{field}={action[field]!r} is outside the declared set [{allowed_text}]"
            )

    undeclared = sorted(set(action) - set(legal_actions))
    for field in undeclared:
        violations.append(f"{field} is not a declared action field")
    return violations


def rejection_threshold(contract: Mapping[str, Any], gate: str) -> int | float:
    """Read a named hard-gate threshold from an environment contract."""
    authorities = contract.get("rejection_authority")
    if not isinstance(authorities, list):
        raise ValueError("environment rejection_authority must contain a list")
    for authority in authorities:
        if isinstance(authority, Mapping) and authority.get("gate") == gate:
            threshold = authority.get("threshold")
            if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
                raise ValueError(f"environment gate {gate} has no numeric threshold")
            return threshold
    raise ValueError(f"environment contract does not declare gate: {gate}")
