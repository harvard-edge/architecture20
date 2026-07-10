"""Write values using the GitHub Actions environment-file protocol."""

from __future__ import annotations

import hashlib
import os
import re
from pathlib import Path

OUTPUT_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _delimiter(key: str, value: str) -> str:
    payload_lines = set(value.splitlines())
    nonce = 0
    while True:
        digest = hashlib.sha256(f"{key}\0{nonce}\0{value}".encode("utf-8")).hexdigest()
        delimiter = f"ARCH2_OUTPUT_{digest}"
        if delimiter not in payload_lines:
            return delimiter
        nonce += 1


def emit_outputs(**outputs: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return

    with Path(path).open("a", encoding="utf-8") as handle:
        for key, raw_value in outputs.items():
            if not OUTPUT_KEY_RE.fullmatch(key):
                raise ValueError(f"invalid GitHub output key: {key!r}")
            value = raw_value or ""
            if "\n" in value or "\r" in value:
                delimiter = _delimiter(key, value)
                handle.write(f"{key}<<{delimiter}\n{value}\n{delimiter}\n")
            else:
                handle.write(f"{key}={value}\n")
