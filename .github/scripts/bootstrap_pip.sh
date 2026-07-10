#!/usr/bin/env bash
set -euo pipefail

readonly PIP_VERSION="26.1.2"
python_bin="${1:-python}"

"$python_bin" -m pip install --disable-pip-version-check "pip==$PIP_VERSION"
