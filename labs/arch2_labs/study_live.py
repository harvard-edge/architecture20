from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from arch2_labs.receipts import sha256_file
from arch2_labs.study import model_payload_errors, study_example_dir


class LiveAdapterError(RuntimeError):
    pass


def _required_environment(environ: Mapping[str, str]) -> tuple[list[str], str, str]:
    command_text = environ.get("ARCH2_MODEL_COMMAND", "").strip()
    if not command_text:
        raise LiveAdapterError(
            "ARCH2_MODEL_COMMAND is not set; the optional live adapter did not run"
        )
    command = shlex.split(command_text)
    if not command or shutil.which(command[0]) is None:
        raise LiveAdapterError(
            "ARCH2_MODEL_COMMAND does not name an available executable"
        )
    model_id = environ.get("ARCH2_MODEL_ID", "").strip()
    if not model_id:
        raise LiveAdapterError(
            "ARCH2_MODEL_ID is not set; declare the exact live model identifier"
        )
    required_credential = environ.get("ARCH2_MODEL_REQUIRED_CREDENTIAL", "").strip()
    if required_credential and not environ.get(required_credential):
        raise LiveAdapterError(
            f"required credential environment variable is missing: {required_credential}"
        )
    return command, model_id, required_credential


def run_live_adapter(
    root: Path,
    output_root: Path,
    *,
    environ: Mapping[str, str] | None = None,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    environment = os.environ if environ is None else environ
    command, model_id, required_credential = _required_environment(environment)
    if output_root.exists():
        raise FileExistsError(f"live output already exists: {output_root}")

    prompt_path = root / "context" / "model_prompt.md"
    schema_path = root / "context" / "model_output.schema.json"
    prompt = prompt_path.read_text()
    schema = json.loads(schema_path.read_text())
    started = datetime.now(timezone.utc)
    monotonic_start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            env=dict(environment),
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise LiveAdapterError(
            f"live model runtime failed safely: {type(exc).__name__}"
        ) from exc
    completed = datetime.now(timezone.utc)
    if proc.returncode != 0:
        raise LiveAdapterError(
            f"live model runtime exited with status {proc.returncode}; no output was recorded"
        )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise LiveAdapterError(
            "live model output is not one complete JSON object"
        ) from exc
    errors = model_payload_errors(payload, schema)
    if errors:
        raise LiveAdapterError(
            "live model output failed validation: " + "; ".join(errors)
        )

    output_root.mkdir(parents=True)
    response_path = output_root / "response.json"
    response_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    provenance = {
        "schema_version": "arch2-live-model-provenance/v1",
        "model_id": model_id,
        "provider": environment.get("ARCH2_MODEL_PROVIDER", "not declared"),
        "runtime_executable": Path(command[0]).name,
        "runtime_argument_count": len(command) - 1,
        "started_at_utc": started.isoformat(),
        "completed_at_utc": completed.isoformat(),
        "wall_time_seconds": time.monotonic() - monotonic_start,
        "returncode": proc.returncode,
        "prompt_sha256": sha256_file(prompt_path),
        "schema_sha256": sha256_file(schema_path),
        "response_sha256": sha256_file(response_path),
        "stderr_recorded": False,
        "credential_required": bool(required_credential),
        "credential_name": required_credential or None,
        "credential_value_recorded": False,
        "note": "This optional output is not the recorded book result.",
    }
    (output_root / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n"
    )
    return provenance


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the optional provider-neutral live proposal adapter."
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=180)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        provenance = run_live_adapter(
            study_example_dir(), args.out, timeout_seconds=args.timeout
        )
    except (LiveAdapterError, FileExistsError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(provenance, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
