# Architecture 2.0 Labs

This directory contains the first runnable Architecture 2.0 lab prototype. The
student-facing idea is not "run a simulator and accept the fastest row." The
idea is to turn a broad prompt into a bounded design loop, run stronger evidence,
preserve rejected alternatives, and submit a loop receipt another person can
audit.

## Quick Start

Use Python 3.11. SCALE-Sim 3.0.0 currently runs cleanly here with `numpy<2`.

```bash
cd labs
python3.11 -m venv ../.venv
../.venv/bin/python -m pip install -r requirements.txt
../.venv/bin/python -m arch2_labs.scale_env \
  --example scale_proxy_mirage \
  --out /tmp/arch2_proxy_mirage_receipt \
  --force
../.venv/bin/python -m arch2_labs.validators /tmp/arch2_proxy_mirage_receipt
```

The runner emits `card.yaml`, `environment.yaml`, candidate records, SCALE-Sim
run provenance, negative traces, an evidence ledger, and a human-owned decision
memo.

To run the interactive notebooks:

```bash
cd labs
../.venv/bin/marimo run notebooks/lab_01_prompt_to_card.py
../.venv/bin/marimo run notebooks/lab_02_scissors_gap.py
../.venv/bin/marimo run examples/scale_proxy_mirage/lab.py
```

## First Example

`examples/scale_proxy_mirage` is a small systolic-array design loop for an
XR-like GEMM workload slice. The cheap proxy ranks candidates by `MACs / PEs`,
so the largest array looks best. SCALE-Sim then supplies stronger evidence. The
largest array is fastest and looks best on several first-order metrics, but it
violates the stated 1024-PE mobile silicon budget. The smallest array misses the
cycle deadline. The `32x32` candidate is the fastest candidate that survives the
declared hard gates.

This is intentionally lightweight enough for a classroom or tutorial session.
It is also real enough that students see actual simulator CSVs, command
provenance, and reviewable rejection records.
