from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

import yaml

from arch2_labs import __version__

MARKER_FILENAME = ".arch2-receipt.json"
MANIFEST_FILENAME = "manifest.yaml"
MARKER_SCHEMA_VERSION = "arch2-receipt-marker/v1"
RECEIPT_SCHEMA_VERSION = "arch2-loop-receipt/v0.2"
RECEIPT_OWNER = "arch2-labs"


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
