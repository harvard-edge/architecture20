# Architecture 2.0 Labs

These ten chapter-aligned activities teach the Architecture 2.0 design loop by
making learners predict, inspect evidence, reject unsupported claims, and state
an honest commitment boundary. The simulator-backed activities use SCALE-Sim,
but the learning objective is the reviewable loop and its records, not the
fastest simulator row.

The complete activity map, expected duration, and output of each lab are in
[`notebooks/README.md`](notebooks/README.md).

## Learner Setup

Use Python 3.10 or 3.11 on a laptop. The tested environment pins SCALE-Sim
3.0.0 and NumPy below version 2.

```bash
cd labs
python3.11 -m venv ../.venv
../.venv/bin/python -m pip install \
  -c constraints/py311-linux.txt \
  -e ".[dev,notebook]"
../.venv/bin/python -m pip check
```

For Python 3.10, use `constraints/py310-linux.txt` instead. The constraint files
record the tested Linux environments. Other operating systems use the same
declared package versions but may resolve platform-specific wheels differently.

Start with the first activity in edit mode so your responses remain available
during the session:

```bash
../.venv/bin/marimo edit notebooks/lab_01_prompt_to_card.py
```

Use `marimo run` for a read-only classroom deployment. Lab 06, the primary
simulator-backed activity, lives with its packaged example:

```bash
../.venv/bin/marimo edit examples/scale_proxy_mirage/lab.py
```

Every activity begins with retrieval and a submitted prediction. Evidence stays
hidden until the required response is complete. Later activities inspect or
produce cards, evidence ledgers, negative traces, environment records, and loop
receipts. The Chapter 8 activity is a separate real-tool exercise. It does not
replace the book's constructed lighthouse example, and its measured outcome is
allowed to differ.

## Receipt Workflow

The simulator runner deliberately stops after generating a Level 2 draft. A
learner must inspect the machine recommendation and evidence, supply an explicit
human decision, and then validate the completed receipt. The interactive Lab 06
and Lab 08 activities guide that process and provide the completed artifact for
review.

The command-line equivalent is useful for instructors and reproducibility jobs:

```bash
../.venv/bin/python -m arch2_labs.scale_env \
  --example scale_proxy_mirage \
  --out /tmp/arch2_proxy_mirage_receipt
# Inspect recommendation.json, evidence_ledger.json, and raw reports first.
../.venv/bin/python -m arch2_labs.decisions \
  /tmp/arch2_proxy_mirage_receipt \
  examples/scale_proxy_mirage/human_decision.example.yaml
../.venv/bin/python -m arch2_labs.validators \
  /tmp/arch2_proxy_mirage_receipt
```

`human_decision.example.yaml` is a named course-staff fixture for automated
reproduction. It is not the learner assignment and must not be presented as the
learner's judgment.

A complete receipt contains a hash-sealed manifest, canonical design-loop card,
environment contract, candidates, raw simulator provenance and output hashes,
an evidence ledger, negative traces, a noncommitting machine recommendation,
and separate human-owned decision records. Validation checks receipt integrity,
cross-record candidate identities, supported commitment levels, and the
separation between recommendation and decision.

## Verification

From `labs/`, run:

```bash
python -m pytest -q
marimo check --strict \
  examples/scale_proxy_mirage/lab.py \
  notebooks/lab_*.py
```

CI runs the suite under both supported Python versions, builds the wheel and
source distribution, and smoke-tests the installed wheel outside the checkout.

## Troubleshooting

- Run commands from `labs/` so the local package and example paths resolve.
- Confirm `python --version` reports 3.10 or 3.11.
- Run `python -m pip check` after installation.
- Treat a simulator crash as an environment failure to diagnose. It is not a
  candidate rejection unless a declared rule explicitly makes it disqualifying.
- Keep generated receipts outside the repository unless they are intentional,
  reviewed fixtures.
