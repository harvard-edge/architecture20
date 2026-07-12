# Architecture 2.0 Labs

These ten chapter-aligned activities provide selected, deterministic practice
in AI-assisted computer architecture. Learners formulate bounded study records,
inspect alternatives, connect configurations to a real simulator, evaluate
evidence, explain selected results, and defend limited decisions. The design
loop is the execution and analysis mechanism used in the activities, not the
whole discipline or its intended outcome.

The current suite invokes no live AI model. Its runnable example records
`model_calls = 0` and uses fixed heuristic, human-seeded, and negative-control
candidates so that every learner can inspect the same evidence without an API
key or network dependency. This supports controlled practice with study
mechanics and review. It does not compare AI with a conventional method or
establish that AI improves architecture work. The simulator-backed activities
use SCALE-Sim, but the goal is architectural understanding and a supported
decision, not the fastest simulator row.

The complete activity map, expected duration, and output of each lab are in
[`notebooks/README.md`](notebooks/README.md).

These activities are formative rather than a complete summative assessment.
Lab 08 integrates a supplied task, candidate set, environment, evidence path,
and decision record. The transfer capstone defined in
[Chapter 10](../book/chapters/10-what-architect-owns/index.qmd) instead gives the
learner a new, tractable architecture problem and assesses all six capabilities
as one bounded study. The activity map shows which parts of that larger outcome
the current labs practice.

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
produce cards, supporting evidence records, failed-run and rejected-alternative
records, environment records, and runnable receipts.

The Chapter 8 activity is a separate real-tool exercise. It does not replace the
book's constructed lighthouse example, and its measured outcome is allowed to
differ.

## Receipt Workflow

For this course exercise, the simulator runner deliberately stops after
generating a Level 2 draft. A learner must inspect the machine recommendation
and evidence, supply an explicit accountable decision, and then validate the
completed Level 3 receipt. The interactive Lab 06 and Lab 08 activities guide
that process and provide the completed artifact for review. Requiring Level 3 is
the exercise's submission rule, not a claim that every low-consequence loop
needs independent review or a Level 3 card.

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

`human_decision.example.yaml` uses the released v1.1 compatibility key and is a named course-staff fixture for automated
reproduction. It is not the learner assignment and must not be presented as the
learner's judgment.

A complete course receipt contains a hash-sealed manifest, canonical design-loop card,
environment contract, candidates, raw simulator provenance and output hashes,
a supporting evidence record (stored as `evidence_ledger.json` for compatibility),
failed-run and rejected-alternative records, a noncommitting machine recommendation,
and a separate accountable decision record. Validation checks receipt integrity,
cross-record candidate identities, supported commitment levels, and the
separation between recommendation and decision.

## Instructor Judgment

The validator checks structural conformance, required fields, cross-record
identities, integrity bindings, supported commitment levels, and separation of
the machine recommendation from the accountable decision. A passing receipt is
inspectable. It is not proof that the architecture reasoning is correct or that
the learner has mastered the six capabilities.

After validation, assess the learner's record with the following judgment
rubric. Use the rows together rather than adding field-presence points.

| **Dimension** | **Weak** | **Adequate** | **Strong** |
| --- | --- | --- | --- |
| Study formulation | Repeats a prompt or leaves the baseline, constraints, or claim implicit. | Bounds the task, baseline, alternatives, constraints, claim, and commitment limit. | Also makes non-goals, assumptions, and evidence that would count against the claim precise. |
| Alternatives and implementation path | Accepts a supplied winner or reports a tool result without a traceable artifact. | Connects declared alternatives to checkable configurations, tool inputs, outputs, provenance, and rejected candidates. | Also justifies the method and tool path, preserves serious alternatives, and identifies where the implementation path could invalidate the study. |
| Evaluation and explanation | Reports a metric or repeats the notebook's explanation. | Matches evidence to workload, baseline, fidelity, and scope, then gives a plausible architecture mechanism. | Tests that mechanism with a sensitivity, intervention, ablation, or discriminating contrast, addresses counterevidence, and uses a matched no-AI comparison when claiming benefit from AI. |
| Decision and defense | Names a winner without ownership, tradeoffs, or limits. | Gives an evidence-bounded recommendation with rationale, owner, residual risk, and reversal condition. | Can answer an independent challenge, distinguish judgment from tool output, and revise the recommendation when assumptions or evidence change. |

The downloadable records capture the prediction, inspected evidence, and
bounded disposition appropriate to each activity. The final transfer reflection
is currently session-local and is not included in the downloaded artifact, so
instructors who grade it must collect it separately. The open-ended Chapter 10
capstone remains the assessment of independent transfer across all six
capabilities.

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
