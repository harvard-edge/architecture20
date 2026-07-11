from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path, PurePosixPath
from typing import Any

import yaml

from arch2_labs import __version__

MARKER_FILENAME = ".arch2-receipt.json"
MANIFEST_FILENAME = "manifest.yaml"
MARKER_SCHEMA_VERSION = "arch2-receipt-marker/v1"
RECEIPT_SCHEMA_VERSION = "arch2-loop-receipt/v0.2"
RECEIPT_OWNER = "arch2-labs"
ACTIVITY_RECORD_FILENAME = "activity_record.json"
ACTIVITY_RECORD_SCHEMA_VERSION = "arch2-activity-record/v1"


@dataclass(frozen=True)
class ReceiptMetadata:
    receipt_id: str
    lab_id: str
    example: str
    created_at: str
    status: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _package_version(distribution: str) -> str:
    try:
        return version(distribution)
    except PackageNotFoundError:
        return "not-installed"


def runtime_versions() -> dict[str, Any]:
    return {
        "python": {
            "version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "executable": sys.executable,
        },
        "platform": platform.platform(),
        "tools": {
            "arch2-labs": __version__,
            "numpy": _package_version("numpy"),
            "PyYAML": _package_version("PyYAML"),
            "SCALE-Sim": _package_version("scalesim"),
        },
    }


def _payload_files(receipt_dir: Path) -> list[Path]:
    excluded = {MARKER_FILENAME, MANIFEST_FILENAME}
    files: list[Path] = []
    for path in receipt_dir.rglob("*"):
        if path.name in excluded and path.parent == receipt_dir:
            continue
        if path.is_symlink():
            raise ValueError(f"receipt payload contains a symbolic link: {path}")
        if path.is_file():
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(receipt_dir).as_posix())


def seal_receipt(receipt_dir: Path, metadata: ReceiptMetadata) -> dict[str, Any]:
    """Write a complete payload manifest and a matching ownership marker."""
    receipt_dir = receipt_dir.resolve()
    if not receipt_dir.is_dir():
        raise ValueError(f"receipt directory does not exist: {receipt_dir}")
    if metadata.status not in {"awaiting_human_decision", "complete"}:
        raise ValueError(f"unsupported receipt status: {metadata.status}")

    manifest_path = receipt_dir / MANIFEST_FILENAME
    marker_path = receipt_dir / MARKER_FILENAME
    if manifest_path.is_symlink() or marker_path.is_symlink():
        raise ValueError("receipt metadata files must not be symbolic links")
    manifest_path.unlink(missing_ok=True)
    marker_path.unlink(missing_ok=True)

    files = [
        {
            "path": path.relative_to(receipt_dir).as_posix(),
            "sha256": sha256_file(path),
            "size_bytes": path.stat().st_size,
        }
        for path in _payload_files(receipt_dir)
    ]
    manifest: dict[str, Any] = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "receipt_id": metadata.receipt_id,
        "lab_id": metadata.lab_id,
        "example": metadata.example,
        "created_at": metadata.created_at,
        "status": metadata.status,
        "generator": {"name": RECEIPT_OWNER, "version": __version__},
        "runtime": runtime_versions(),
        "files": files,
    }
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False))

    marker = {
        "schema_version": MARKER_SCHEMA_VERSION,
        "owner": RECEIPT_OWNER,
        "receipt_id": metadata.receipt_id,
        "manifest": MANIFEST_FILENAME,
        "manifest_sha256": sha256_file(manifest_path),
    }
    marker_path.write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n")
    return manifest


def verify_receipt_ownership(receipt_dir: Path) -> dict[str, Any]:
    """Verify the marker/manifest pair used to authorize replacement."""
    if receipt_dir.is_symlink():
        raise ValueError(f"refusing to replace a symbolic link: {receipt_dir}")
    if not receipt_dir.is_dir():
        raise ValueError(f"replacement target is not a directory: {receipt_dir}")

    marker_path = receipt_dir / MARKER_FILENAME
    if marker_path.is_symlink():
        raise ValueError("Arch2 receipt ownership marker is a symbolic link")
    if not marker_path.is_file():
        raise ValueError(f"target is not an Arch2 receipt: missing {MARKER_FILENAME}")
    try:
        marker = json.loads(marker_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError("Arch2 receipt ownership marker is malformed") from exc

    if marker.get("schema_version") != MARKER_SCHEMA_VERSION:
        raise ValueError("Arch2 receipt ownership marker has an unsupported schema")
    if marker.get("owner") != RECEIPT_OWNER:
        raise ValueError("target is not owned by arch2-labs")
    if marker.get("manifest") != MANIFEST_FILENAME:
        raise ValueError("Arch2 receipt ownership marker names an invalid manifest")

    manifest_path = receipt_dir / MANIFEST_FILENAME
    if manifest_path.is_symlink():
        raise ValueError("Arch2 receipt manifest is a symbolic link")
    if not manifest_path.is_file():
        raise ValueError(f"Arch2 receipt manifest is missing: {MANIFEST_FILENAME}")
    if marker.get("manifest_sha256") != sha256_file(manifest_path):
        raise ValueError("Arch2 receipt manifest hash does not match its marker")
    try:
        manifest = yaml.safe_load(manifest_path.read_text())
    except yaml.YAMLError as exc:
        raise ValueError("Arch2 receipt manifest is malformed") from exc
    if not isinstance(manifest, dict):
        raise ValueError("Arch2 receipt manifest is malformed")
    if manifest.get("schema_version") != RECEIPT_SCHEMA_VERSION:
        raise ValueError("Arch2 receipt manifest has an unsupported schema")
    if not marker.get("receipt_id") or marker["receipt_id"] != manifest.get(
        "receipt_id"
    ):
        raise ValueError("Arch2 receipt ID does not match between marker and manifest")
    return manifest


def manifest_payload_errors(receipt_dir: Path, manifest: dict[str, Any]) -> list[str]:
    """Check that a manifest exactly describes an unchanged regular-file payload."""
    receipt_dir = receipt_dir.resolve()
    entries = manifest.get("files")
    if not isinstance(entries, list):
        return ["manifest files must be a list"]

    errors: list[str] = []
    declared: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"manifest file entry {index} must be an object")
            continue
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative:
            errors.append(f"manifest file entry {index} has no path")
            continue
        pure = PurePosixPath(relative)
        if pure.is_absolute() or ".." in pure.parts:
            errors.append(f"manifest contains unsafe payload path: {relative}")
            continue
        path = receipt_dir.joinpath(*pure.parts)
        try:
            path.resolve().relative_to(receipt_dir)
        except ValueError:
            errors.append(f"manifest contains unsafe payload path: {relative}")
            continue
        if relative in declared:
            errors.append(f"manifest declares payload more than once: {relative}")
            continue
        declared.add(relative)
        if path.is_symlink():
            errors.append(f"manifest payload is a symbolic link: {relative}")
            continue
        if not path.is_file():
            errors.append(f"manifest payload is missing: {relative}")
            continue
        if entry.get("sha256") != sha256_file(path):
            errors.append(f"manifest payload {relative} sha256 mismatch")
        if entry.get("size_bytes") != path.stat().st_size:
            errors.append(f"manifest payload {relative} size mismatch")

    actual: set[str] = set()
    for path in receipt_dir.rglob("*"):
        relative = path.relative_to(receipt_dir).as_posix()
        if path.is_symlink():
            errors.append(f"receipt contains a symbolic link: {relative}")
        elif path.is_file() and relative not in {MARKER_FILENAME, MANIFEST_FILENAME}:
            actual.add(relative)
    for relative in sorted(actual - declared):
        errors.append(f"payload file is not declared in manifest: {relative}")
    for relative in sorted(declared - actual):
        errors.append(f"manifest payload is not a regular file: {relative}")
    return errors


def verify_receipt_integrity(
    receipt_dir: Path, *, expected_status: str | None = None
) -> dict[str, Any]:
    """Verify ownership, status, and every payload byte before a state transition."""
    manifest = verify_receipt_ownership(receipt_dir)
    errors = manifest_payload_errors(receipt_dir, manifest)
    if expected_status is not None and manifest.get("status") != expected_status:
        errors.append(
            "receipt status must be "
            f"{expected_status}, got {manifest.get('status') or '<missing>'}"
        )
    if errors:
        raise ValueError("; ".join(errors))
    return manifest


def attach_activity_record(
    receipt_dir: Path, record: Mapping[str, Any]
) -> dict[str, Any]:
    """Add one activity record to a complete receipt and reseal its manifest."""
    manifest = verify_receipt_integrity(receipt_dir, expected_status="complete")
    if record.get("schema_version") != ACTIVITY_RECORD_SCHEMA_VERSION:
        raise ValueError("activity record has an unsupported schema")
    activity_id = record.get("activity_id")
    if not isinstance(activity_id, str) or not activity_id.strip():
        raise ValueError("activity record must name a nonempty activity_id")
    if "embedded_receipt" in record:
        raise ValueError("embedded_receipt is reserved for receipt metadata")

    record_path = receipt_dir / ACTIVITY_RECORD_FILENAME
    if record_path.is_symlink() or record_path.exists():
        raise ValueError("receipt already contains an activity record")

    payload = dict(record)
    payload["activity_id"] = activity_id.strip()
    payload["embedded_receipt"] = {
        "receipt_id": manifest["receipt_id"],
        "lab_id": manifest["lab_id"],
        "example": manifest["example"],
    }
    record_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    seal_receipt(
        receipt_dir,
        ReceiptMetadata(
            receipt_id=manifest["receipt_id"],
            lab_id=manifest["lab_id"],
            example=manifest["example"],
            created_at=manifest["created_at"],
            status=manifest["status"],
        ),
    )
    verify_receipt_integrity(receipt_dir, expected_status="complete")
    return payload
