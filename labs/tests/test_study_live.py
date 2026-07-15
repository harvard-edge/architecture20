from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from arch2_labs.study import study_example_dir
from arch2_labs.study_live import LiveAdapterError, run_live_adapter


def test_live_adapter_fails_clearly_without_runtime(tmp_path: Path) -> None:
    with pytest.raises(LiveAdapterError, match="ARCH2_MODEL_COMMAND is not set"):
        run_live_adapter(study_example_dir(), tmp_path / "out", environ={})


def test_live_adapter_fails_clearly_without_model(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("arch2_labs.study_live.shutil.which", lambda value: value)
    with pytest.raises(LiveAdapterError, match="ARCH2_MODEL_ID is not set"):
        run_live_adapter(
            study_example_dir(),
            tmp_path / "out",
            environ={"ARCH2_MODEL_COMMAND": "fake-runtime"},
        )


def test_live_adapter_fails_clearly_without_required_credential(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("arch2_labs.study_live.shutil.which", lambda value: value)
    with pytest.raises(LiveAdapterError, match="required credential"):
        run_live_adapter(
            study_example_dir(),
            tmp_path / "out",
            environ={
                "ARCH2_MODEL_COMMAND": "fake-runtime",
                "ARCH2_MODEL_ID": "test-model",
                "ARCH2_MODEL_REQUIRED_CREDENTIAL": "TEST_API_KEY",
            },
        )


def test_live_adapter_validates_output_and_never_records_secret(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = study_example_dir()
    payload = (root / "recorded" / "model" / "original_response.json").read_text()
    monkeypatch.setattr("arch2_labs.study_live.shutil.which", lambda value: value)
    monkeypatch.setattr(
        "arch2_labs.study_live.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=["fake-runtime"], returncode=0, stdout=payload, stderr=""
        ),
    )
    secret = "do-not-record-this-value"
    out = tmp_path / "out"

    run_live_adapter(
        root,
        out,
        environ={
            "ARCH2_MODEL_COMMAND": "fake-runtime --json",
            "ARCH2_MODEL_ID": "test-model",
            "ARCH2_MODEL_PROVIDER": "test-provider",
            "ARCH2_MODEL_REQUIRED_CREDENTIAL": "TEST_API_KEY",
            "TEST_API_KEY": secret,
        },
    )

    combined = (out / "response.json").read_text() + (
        out / "provenance.json"
    ).read_text()
    assert secret not in combined
    provenance = json.loads((out / "provenance.json").read_text())
    assert provenance["credential_required"] is True
    assert provenance["credential_value_recorded"] is False


def test_live_adapter_rejects_invalid_response(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("arch2_labs.study_live.shutil.which", lambda value: value)
    monkeypatch.setattr(
        "arch2_labs.study_live.subprocess.run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=["fake-runtime"], returncode=0, stdout="{}", stderr=""
        ),
    )

    with pytest.raises(LiveAdapterError, match="failed validation"):
        run_live_adapter(
            study_example_dir(),
            tmp_path / "out",
            environ={
                "ARCH2_MODEL_COMMAND": "fake-runtime",
                "ARCH2_MODEL_ID": "test-model",
            },
        )
