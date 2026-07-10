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
../.venv/bin/python -m pip install \
  -r requirements.txt \
  -c constraints/py311-linux.txt
../.venv/bin/python -m arch2_labs.scale_env \
  --example scale_proxy_mirage \
  --out /tmp/arch2_proxy_mirage_receipt
# Inspect recommendation.json, evidence_ledger.json, and the raw reports first.
../.venv/bin/python -m arch2_labs.decisions \
  /tmp/arch2_proxy_mirage_receipt \
  examples/scale_proxy_mirage/human_decision.example.yaml
../.venv/bin/python -m arch2_labs.validators /tmp/arch2_proxy_mirage_receipt
```

The runner emits a hash-sealed manifest, canonical design-loop card, environment
contract, candidate records, SCALE-Sim run provenance and raw-output hashes,
negative traces, an evidence ledger, a noncommitting machine recommendation, and
an explicitly supplied human decision. The example decision is a named course
staff reproducibility fixture, not a decision fabricated by the runner.

The first command stops after evidence generation. The resulting Level 2 draft
records the machine recommendation but intentionally fails complete-receipt
validation until a human inspects it and runs `arch2_labs.decisions`. That command
refuses a tampered draft and refuses to replace an existing decision. Automated
reproducibility jobs may pass `--decision-file` to `arch2_labs.scale_env`, but the
two-phase path is the learner workflow. `--force` replaces only a directory with
a matching Arch2 ownership marker and manifest; it refuses unrelated paths and
symbolic links.

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

## Receipt Integrity

`manifest.yaml` hashes every payload file. Each successful simulator run also
declares the raw reports and their hashes in `runs.jsonl`. The validator checks
those hashes, candidate IDs across every record, tool and runtime versions, the
canonical card schema, supported commitment levels, and the separation between
`recommendation.json` and `decision.yaml`.
