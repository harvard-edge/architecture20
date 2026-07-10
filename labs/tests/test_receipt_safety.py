from __future__ import annotations

import json
from pathlib import Path

import pytest

from arch2_labs.receipts import ReceiptMetadata, seal_receipt
from arch2_labs.scale_env import LABS_ROOT, _safe_replace_dir


def _seal(directory: Path, *, receipt_id: str = "receipt-test-id") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "payload.txt").write_text("owned payload\n")
    seal_receipt(
        directory,
        ReceiptMetadata(
            receipt_id=receipt_id,
            lab_id="safety_test",
            example="test_fixture",
            created_at="2026-07-10T00:00:00+00:00",
            status="awaiting_human_decision",
        ),
    )


@pytest.mark.parametrize(
    "protected",
    [
        Path("/"),
        Path.home(),
        LABS_ROOT,
        LABS_ROOT.parent,
        LABS_ROOT.parent.parent,
    ],
)
def test_safe_replace_refuses_protected_paths(protected: Path) -> None:
    with pytest.raises(ValueError, match="protected path"):
        _safe_replace_dir(protected)


def test_safe_replace_refuses_unrelated_directory(tmp_path: Path) -> None:
    unrelated = tmp_path / "unrelated"
    unrelated.mkdir()
    sentinel = unrelated / "keep-me.txt"
    sentinel.write_text("must survive\n")

    with pytest.raises(ValueError, match="not an Arch2 receipt"):
        _safe_replace_dir(unrelated)

    assert sentinel.read_text() == "must survive\n"


def test_safe_replace_refuses_output_symlink(tmp_path: Path) -> None:
    owned = tmp_path / "owned"
    _seal(owned)
    linked = tmp_path / "linked"
    linked.symlink_to(owned, target_is_directory=True)

    with pytest.raises(ValueError, match="symbolic link"):
        _safe_replace_dir(linked)

    assert owned.exists()
    assert linked.is_symlink()


def test_safe_replace_refuses_marker_symlink(tmp_path: Path) -> None:
    owned = tmp_path / "owned"
    _seal(owned)
    marker = owned / ".arch2-receipt.json"
    marker_copy = tmp_path / "marker.json"
    marker_copy.write_text(marker.read_text())
    marker.unlink()
    marker.symlink_to(marker_copy)

    with pytest.raises(ValueError, match="ownership marker.*symbolic link"):
        _safe_replace_dir(owned)

    assert owned.exists()


def test_safe_replace_refuses_marker_without_manifest(tmp_path: Path) -> None:
    directory = tmp_path / "marker-only"
    directory.mkdir()
    (directory / ".arch2-receipt.json").write_text(
        json.dumps(
            {
                "schema_version": "arch2-receipt-marker/v1",
                "owner": "arch2-labs",
                "receipt_id": "marker-only",
                "manifest": "manifest.yaml",
                "manifest_sha256": "0" * 64,
            }
        )
    )

    with pytest.raises(ValueError, match="manifest"):
        _safe_replace_dir(directory)

    assert directory.exists()


def test_safe_replace_refuses_mismatched_receipt_ids(tmp_path: Path) -> None:
    directory = tmp_path / "mismatched"
    _seal(directory)
    marker_path = directory / ".arch2-receipt.json"
    marker = json.loads(marker_path.read_text())
    marker["receipt_id"] = "different-id"
    marker_path.write_text(json.dumps(marker))

    with pytest.raises(ValueError, match="receipt ID"):
        _safe_replace_dir(directory)

    assert directory.exists()


def test_safe_replace_refuses_tampered_manifest(tmp_path: Path) -> None:
    directory = tmp_path / "tampered"
    _seal(directory)
    with (directory / "manifest.yaml").open("a") as manifest:
        manifest.write("tampered: true\n")

    with pytest.raises(ValueError, match="manifest hash"):
        _safe_replace_dir(directory)

    assert directory.exists()


def test_safe_replace_removes_sealed_arch2_receipt(tmp_path: Path) -> None:
    directory = tmp_path / "owned"
    _seal(directory)

    _safe_replace_dir(directory)

    assert not directory.exists()
