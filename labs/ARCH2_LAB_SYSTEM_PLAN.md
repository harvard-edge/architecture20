# Architecture 2.0 Lab System Plan

Status: planning artifact for the `feat/arch2-labs-plan` worktree.

This plan sketches an Architecture 2.0 lab system that borrows the strongest
MLSysBook lab patterns while preserving the core Architecture 2.0 thesis. The
unit of learning is not a generated artifact. The unit of learning is a
reviewable design loop that leaves a loop receipt.

## Core Teaching Claim

Architecture 2.0 labs should teach students to work from prompt to loop, not
prompt to chip.

The recurring student experience should be:

1. Read a compact Architecture 2.0 chapter recap.
2. Translate a broad prompt into a bounded loop contract.
3. Predict which candidate or resource constraint will bind.
4. Let an agent or search policy propose bounded actions.
5. Run a real or realistic architecture environment.
6. Inspect evidence and rejected alternatives.
7. Decide what the evidence supports and where it stops.
8. Save a loop receipt that another student or reviewer can audit.

The recurring intellectual pattern should be:

1. Name the architectural claim.
2. Bound the task and design space.
3. State what the agent may read and write.
4. State what the environment can reject.
5. Separate cheap proxy feedback from stronger evidence.
6. Preserve negative traces.
7. Assign the final commitment to a human owner.

The lab should make the human-agent split concrete. The agent can generate,
predict, search, critique, repair, call tools, or organize evidence. The human
owns the loop contract, evidence standard, rejection authority, and commitment
boundary.

## MLSysBook Patterns to Reuse

MLSysBook labs provide a useful implementation grammar. The reusable patterns
are:

| Pattern | MLSysBook Form | Architecture 2.0 Adaptation |
| --- | --- | --- |
| Predict first | Structured prediction locks before reveal. | Students predict which claim, candidate, or rejection gate will fail. |
| Interactive instruments | Marimo controls, charts, and tables. | Students manipulate action-space knobs and see evidence change. |
| Local-first state | Browser-local Design Ledger plus report export. | Browser-local Loop Receipt plus Markdown and JSON export. |
| Stable lab rhythm | Learning objectives, recap, scenario, parts, synthesis, report. | Learning objectives, Architecture 2.0 recap, loop brief, role contract, evidence, rejection, decision, receipt. |
| Track plans | A companion `.track-plan.md` records teaching intent. | A companion `.loop-plan.md` records claim, action schema, evidence, negative traces, and human decision. |
| Helper package | `mlsysbook_labs` owns UI, schemas, reports, and state. | `arch2_labs` should own schemas, receipt validation, UI shell, and shared plotting. |
| Engine boundary | MLSysIM owns formulas and typed results. | SCALE-Sim or another tool owns simulator feedback; `arch2_labs` owns loop records and interpretation. |
| Static tests | Tests enforce lab structure, reports, and browser readiness. | Tests should enforce receipt fields, action schemas, rejection gates, and no overclaiming. |
| Tutorial design | Backward design, aha moments, pair work, setup checks. | Tutorial starts from a prompt, then makes students experience proxy failure and commitment boundaries. |

The key change is vocabulary. MLSysBook asks students to produce a design
ledger and report. Architecture 2.0 should ask students to produce a loop
receipt and decision record.

## Recommended First Full Lab

The first flagship lab should be:

**The Proxy Mirage: A Systolic Accelerator Loop**

The lab uses a lightweight DNN accelerator design-space loop around SCALE-Sim.
SCALE-Sim is a good first tool because it is Python-based, models systolic-array
accelerators, accepts architecture configuration and workload topology files,
and emits inspectable CSV reports for compute, bandwidth, access, and timing.

The lab should not start with an LLM. It should first teach the loop mechanics
with a deterministic agent or simple search policy. An optional later part can
swap in an LLM as a generator or critic.

### Student Scenario

The student receives a broad prompt:

> Design a lightweight accelerator path for an XR-like real-time inference
> slice under a latency and bandwidth budget. Return a design-space report with
> evidence and rejected alternatives.

The lab immediately converts that prompt into a bounded loop:

| Loop Field | First-Lab Instance |
| --- | --- |
| Claim | A selected accelerator configuration is worth advancing to a stronger study for this workload slice. |
| Workload | A small XR-like inference topology represented as GEMM or convolution layers. |
| Baseline | A simple reference candidate and the cheap proxy ranking. |
| Legal actions | Array rows, array columns, dataflow, SRAM sizes, and DRAM bandwidth assumption. |
| Invalid actions | Unsupported dimensions, impossible SRAM budgets, missing topology, or bandwidth outside the declared envelope. |
| Cheap proxy | MACs divided by nominal PE count, with simple SRAM and bandwidth checks. |
| Stronger feedback | SCALE-Sim reports for cycles, stalls, utilization, bandwidth, accesses, and optional time estimate. |
| Rejection authority | Deadline miss, poor utilization, bandwidth pressure, invalid config, missing provenance, or stronger feedback overturning proxy rank. |
| Commitment boundary | Advance to next-fidelity study only. No RTL, physical design, power signoff, or product claim. |
| Human decision | Student names the survivor, rejected candidates, residual risk, and evidence that would overturn the decision. |

### Intended Aha Moment

The cheap proxy should make a larger or seemingly faster array look best. The
SCALE-Sim run should reveal that the proxy ignored utilization, memory stalls,
or bandwidth pressure, so a different candidate survives.

The exact winner is less important than the reversal:

```text
 Proxy rank: largest array wins.
 SCALE-Sim evidence: largest array has poor utilization or memory pressure.
 Rejection: proxy winner does not earn the commitment.
 Decision: a smaller or differently mapped candidate advances only to the next study.
```

This is the Architecture 2.0 lesson in executable form. The loop does not trust
the agent or proxy. It records what evidence supported the survivor and what
rejected the alternatives.

## Lab Modality

Use marimo as the primary student surface. Use a plain Python package underneath
for repeatable command-line and CI runs.

| Layer | Recommended Tool | Role |
| --- | --- | --- |
| Student lab | Marimo | Interactive prediction, controls, evidence views, and receipt export. |
| Simulator | SCALE-Sim | Real tool feedback for systolic-array DSE. |
| Shared code | `arch2_labs` Python package | Schemas, runners, receipt builder, validation, plotting helpers. |
| Records | YAML and JSONL | Design-loop card, environment contract, candidates, runs, evidence, negative traces. |
| Validation | `pytest` plus receipt validator | Check lab structure and report completeness. |
| Book integration | Quarto page or appendix pointer | Narrative framing, not the live execution surface. |
| Tutorial kit | Slides, handout, cheatsheet, starter receipts | Venue-ready delivery for ISCA, MICRO, IISWC, and classes. |

The marimo notebook is the classroom. The loop receipt is the assignment
artifact. The command-line runner is the reproducibility path.

## Proposed Repository Layout

Start small. Avoid building a full course platform before the first loop works.

```text
labs/
  README.md
  ARCH2_LAB_SYSTEM_PLAN.md
  pyproject.toml
  requirements.txt
  arch2_labs/
    __init__.py
    schemas.py
    receipt.py
    validators.py
    scale_env.py
    agents.py
    plots.py
    ui.py
  examples/
    scale_proxy_mirage/
      lab.py
      scale_proxy_mirage.loop-plan.md
      README.md
      configs/
        base.cfg
        candidates.yaml
      workloads/
        xr_slice_gemm.csv
      starter_receipt/
        card.yaml
        environment.yaml
      solution_receipt/
        card.yaml
        environment.yaml
        candidates.jsonl
        runs.jsonl
        evidence_ledger.json
        negative_traces.jsonl
        decision.md
  tests/
    test_receipt_schema.py
    test_scale_env_smoke.py
    test_lab_static.py
    test_report_contract.py
  tutorial/
    DESIGN.md
    prerequisites.md
    exercises.md
    cheatsheet.md
    slides/
```

The first implementation should support two equivalent runs:

```bash
marimo run labs/examples/scale_proxy_mirage/lab.py
python -m arch2_labs.scale_env --example scale_proxy_mirage --out receipt/
python -m arch2_labs.decisions receipt/ human_decision.yaml
python -m arch2_labs.validators receipt/
```

The command-line path exists for CI and instructors. The marimo path exists for
learning.

## Lab Structure

Each Arch2 lab should use a stable structure derived from MLSysBook, but with
Architecture 2.0 labels.

| Order | Student-Facing Section | Purpose |
| ---: | --- | --- |
| 1 | Learning Objectives | State what the student can do after the lab. |
| 2 | Architecture 2.0 Recap | Bridge the relevant book concepts into the lab. |
| 3 | Loop Brief | State the claim, workload, baseline, design space, and commitment boundary. |
| 4 | Role Contract | State what the agent/searcher, environment, rejector, and human owner do. |
| 5 | Part A - Prompt to Loop | Convert the broad prompt into a design-loop card. |
| 6 | Part B - Proxy Prediction | Predict the proxy winner and likely blind spot. |
| 7 | Part C - Environment Feedback | Run SCALE-Sim and inspect evidence. |
| 8 | Part D - Rejection Gate | Reject invalid or unsupported candidates and preserve negative traces. |
| 9 | Part E - Agent Role Swap | Optional comparison of random, heuristic, and LLM-generated candidates. |
| 10 | Synthesis | Name the survivor, rejected alternatives, and residual risk. |
| 11 | Download Loop Receipt | Export Markdown and JSON artifacts locally. |

Every part should contain:

1. What you need to know.
2. Scenario slice.
3. Prediction.
4. Try it.
5. Evidence.
6. Rejection gate.
7. Source trace.
8. Reflection.
9. Checkpoint or decision.

The source trace is important for Arch2. It should show config paths, topology
paths, tool version, command, seed, and output file hashes where practical.

## Loop Receipt Contract

The receipt is the durable student artifact. It should be small enough to inspect
in class and structured enough to validate automatically.

Required files:

| File | Contents |
| --- | --- |
| `.arch2-receipt.json` | Ownership marker bound to the manifest ID and hash. |
| `manifest.yaml` | Receipt status, runtime/tool versions, and hashes for every payload file. |
| `card.yaml` | The design-loop card fields. |
| `environment.yaml` | Legal actions, observations, invalid states, cost, provenance, and rejection authority. |
| `candidates.jsonl` | One record per proposed candidate, including source and action values. |
| `runs.jsonl` | One record per proxy or SCALE-Sim run, including command, status, outputs, and cost. |
| `evidence_ledger.json` | Evidence stages, fidelity, support, limits, and next evidence required. |
| `negative_traces.jsonl` | Rejected candidates with stage, gate, and reason. |
| `recommendation.json` | Machine recommendation with no human-decision or commitment authority. |
| `decision.yaml` | Explicit human owner, objective, candidate choice, rationale, commitment, residual risk, and would-overturn evidence. |
| `decision.md` | Human-readable rendering of `decision.yaml`. |

The validator should fail if:

- no candidate is rejected;
- the final decision lacks a commitment boundary;
- the proxy result is treated as final evidence;
- a SCALE-Sim run has no provenance;
- the environment contract lacks legal actions or invalid-action semantics;
- the receipt omits negative traces;
- a manifest or declared raw-output hash does not match;
- an ID does not resolve across candidates, runs, evidence, recommendation, and decision;
- a machine recommendation is represented as a human decision;
- the commitment level exceeds the evidence-supported next-fidelity study;
- `decision.md` makes an implementation, RTL, or tapeout claim.

## Candidate Tools Beyond the First Lab

The first lab should use SCALE-Sim. Later labs can expand the tool stack.

| Tool | Best Lab Use | Why Not First |
| --- | --- | --- |
| SCALE-Sim | Lightweight accelerator DSE with real simulator reports. | Best first choice. |
| Timeloop and Accelergy | Mapping, energy, and dataflow studies. | Docker and dependencies add setup risk. |
| ArchGym | Standardized method comparison across search algorithms. | Better after students understand loop contracts. |
| Verilator | Generator-critic RTL repair loops. | Too RTL-focused for the first architecture-loop lab. |
| gem5 | Higher-fidelity architecture simulation and workload execution. | Setup and runtime are heavier for a first tutorial. |
| MLPerf-style harness | Benchmark governance and evidence-disclosure labs. | Better for later IISWC-style workload and benchmark modules. |

## Lab Sequence

A useful Arch2 lab sequence should be short, coherent, and conference-ready.

| Lab | Title | Primary Lesson | Tool |
| --- | --- | --- | --- |
| 0 | Prompt to Loop Card | A prompt is not a loop until claim, actions, evidence, rejection, and commitment are explicit. | No simulator required. |
| 1 | The Proxy Mirage | Cheap proxy feedback can rank candidates but cannot own the claim. | SCALE-Sim. |
| 2 | The Environment Contract | A tool becomes an environment when legal actions, observations, invalid states, and provenance are explicit. | SCALE-Sim wrapper. |
| 3 | Agent as Generator | An agent can propose candidates only inside an action schema. | Optional LLM, fallback heuristic. |
| 4 | Agent as Critic | An agent may be more useful finding missing evidence and overclaims than generating designs. | Receipt validator plus optional LLM. |
| 5 | Negative Trace Reuse | A rejected candidate is architecture data with scope and reuse limits. | Receipt repository. |
| 6 | Higher-Fidelity Escalation | Commitment level rises only when evidence rises. | Timeloop, Verilator, or gem5 extension. |

The first three labs are enough for a half-day tutorial. Labs 0 through 5 are
enough for a full-day tutorial or a two-week course module.

## Conference Tutorial Shape

The conference tutorial should feel like a design review workshop, not a tool
demo.

### Half-Day Format

| Time | Activity | Format | Output |
| --- | --- | --- | --- |
| 0:00-0:15 | Hook: prompt-to-loop, not prompt-to-chip | Lecture plus poll | Shared misconception surfaced. |
| 0:15-0:40 | Lab 0: fill the loop card | Pair work | Draft `card.yaml`. |
| 0:40-1:20 | Lab 1: proxy prediction and SCALE-Sim reveal | Marimo lab | Candidate evidence and negative trace. |
| 1:20-1:35 | Break and setup recovery | Support | Everyone has a receipt directory. |
| 1:35-2:10 | Lab 2: environment contract and rejection gates | Pair work | `environment.yaml` plus validator pass. |
| 2:10-2:45 | Lab 3: agent role swap | Demo plus optional hands-on | Generated or heuristic candidates compared. |
| 2:45-3:20 | Synthesis: human commitment boundary | Group critique | `decision.md`. |
| 3:20-3:30 | Transfer to attendee projects | Individual reflection | One loop they can build next. |

### Full-Day Format

Morning should build the loop. Afternoon should vary the agent role and the
commitment level.

| Module | Theme | Main Aha Moment |
| --- | --- | --- |
| 1 | Prompt to loop | The prompt hides workload, action, evidence, and ownership obligations. |
| 2 | Proxy to evidence | The proxy winner can fail once the environment returns stronger feedback. |
| 3 | Rejection gates | A useful loop is rejection-bound, not generation-bound. |
| 4 | Agent role discipline | The same agent is safe or unsafe depending on role and authority. |
| 5 | Negative traces | Failures are reusable only with fidelity labels and scope limits. |
| 6 | Capstone design review | A human decision is defensible only when it states what would overturn it. |

### Venue Emphasis

| Venue | Emphasis |
| --- | --- |
| ISCA | Architecture-loop contracts, proxy mismatch, accelerator DSE, and commitment boundaries. |
| MICRO | Microarchitecture action schemas, simulator evidence, invalid actions, and escalation to RTL or timing evidence. |
| IISWC | Workload slice definition, benchmark coverage, evidence provenance, drift, and workload-aware rejection. |
| ASPLOS | Cross-layer agent roles, software path evidence, and co-design failures. |
| MLSys | Method role discipline, agent evaluation, and evidence ledgers for ML-for-systems claims. |

## Design Principles

1. Make one failure visible before showing one success.
2. Keep every first-run lab laptop-only and CPU-only.
3. Use structured predictions, never free-text guesses, before evidence.
4. Limit visible knobs to three primary controls at a time.
5. Let students inspect the exact command, config, topology, and output files.
6. Treat simulator output as feedback until provenance and authority make it evidence.
7. Make the final answer a bounded decision, not a winner row.
8. Provide both marimo interaction and command-line reproducibility.
9. Require a validator so instructors can grade receipts at scale.
10. Keep LLM use optional in the first release so the lab works offline.

## Implementation Work Packages

### Phase 0: Contract

Deliverables:

- `labs/README.md`.
- `labs/ARCH2_LAB_SYSTEM_PLAN.md`.
- First `scale_proxy_mirage.loop-plan.md`.
- Decision on naming: "Loop Receipt" as the durable artifact.

Exit criteria:

- The first lab has learning objectives, loop fields, action schema, evidence
  plan, rejection gates, and receipt schema before code is written.

### Phase 1: Receipt and Schema Package

Deliverables:

- `arch2_labs.schemas` dataclasses or pydantic models.
- `arch2_labs.receipt` builder.
- `arch2_labs.validators` CLI.
- Starter `card.yaml` and `environment.yaml`.

Exit criteria:

- A hand-written receipt validates.
- Incomplete receipts fail with actionable messages.

### Phase 2: SCALE-Sim Environment Wrapper

Deliverables:

- Minimal SCALE-Sim install instructions.
- A tiny topology file that runs quickly.
- Candidate config generator.
- Parser for SCALE-Sim CSV reports.
- A deterministic smoke run.

Exit criteria:

- `python -m arch2_labs.scale_env --example scale_proxy_mirage --out receipt/`
  creates a hash-sealed Level 2 draft on a clean laptop environment.
- `python -m arch2_labs.decisions receipt/ human_decision.yaml` verifies the
  Level 2 draft and attaches one immutable human decision after evidence review.

### Phase 3: Marimo Lab

Deliverables:

- `lab.py` with structured prediction, controls, evidence charts, source trace,
  rejection view, reflection card, and receipt export.
- Local-first receipt state.
- Table fallbacks for charts.

Exit criteria:

- A student can complete the lab without editing code.
- A student can download the receipt.
- The receipt passes the validator.

### Phase 4: Agent Role Options

Deliverables:

- Heuristic candidate generator.
- Random baseline generator.
- Optional LLM generator or critic with offline fallback.
- Role contract panel naming what each method can and cannot do.

Exit criteria:

- Students can swap method roles without changing the environment contract.
- The lab shows that better generation does not remove rejection authority.

### Phase 5: Tutorial Kit

Deliverables:

- `tutorial/DESIGN.md` using backward design.
- `tutorial/prerequisites.md`.
- `tutorial/exercises.md`.
- `tutorial/cheatsheet.md`.
- Slides for half-day and full-day delivery.
- Instructor quickstart and troubleshooting guide.

Exit criteria:

- The tutorial can survive installation failures through a browser or prebuilt
  fallback.
- Every exercise has a checkable output.
- The capstone can be critiqued from receipts, not screenshots.

## Testing Contract

Required tests:

- Every lab imports as a valid marimo app.
- Every lab has a setup cell with browser/local dependency handling.
- Every visible knob maps to the declared action schema.
- Every lab has at least one structured prediction.
- Every lab has at least one visible rejection state.
- Every lab can generate a complete loop receipt.
- Every receipt includes card, environment, candidates, runs, evidence,
  negative traces, and decision.
- Every run record includes command, status, tool version or package version,
  inputs, outputs, and elapsed time.
- Every decision includes strongest supported claim and would-overturn evidence.
- No first-release lab requires network access after setup.
- No lab claims implementation readiness from proxy or SCALE-Sim-only evidence.

Optional browser tests:

- Marimo opens.
- Prediction controls render.
- Report download appears only after required fields are complete.
- Source trace accordion renders and remains readable.

## Operational Risks

| Risk | Why It Matters | Mitigation |
| --- | --- | --- |
| Install friction | Conference tutorials lose momentum when 10 percent of the room cannot run setup. | Preflight script, browser/WASM option if feasible, cached environment, and printed fallback results. |
| SCALE-Sim schema drift | Parser can break if CSV names change. | Pin version, test against committed fixture outputs, and include a schema adapter. |
| Runs take too long | Students need quick feedback. | Use a tiny topology and a small candidate set. Keep deep sweeps optional. |
| Overclaiming | Students may treat simulator output as final architecture evidence. | Validator rejects implementation claims and forces commitment boundary. |
| LLM dependency | API keys and network access will fail in classrooms. | Make LLM role optional. Always provide deterministic generator and critic. |
| Vendor or hardware accuracy | ISCA and MICRO audiences will challenge numbers. | Keep first lab about loop shape, not vendor claims. Source every external hardware number. |
| Too much UI | Widgets can distract from the loop. | Limit to prediction, three primary knobs, evidence, rejection, and receipt. |
| No autograding | Instructors need scalable assessment. | Validate receipts and expose rubric fields. |

## Course and Tutorial Assessment

A good student receipt should show:

- The claim is bounded.
- The action schema is explicit.
- The proxy winner and stronger-evidence survivor are distinguishable.
- At least one candidate is rejected for a stated reason.
- The negative trace is preserved.
- The human decision is not delegated to the agent.
- The commitment boundary is honest.
- The student can name what evidence would overturn the decision.

Suggested grading dimensions:

| Dimension | Good Answer Shows |
| --- | --- |
| Loop framing | Converts prompt into claim, task, design space, and commitment boundary. |
| Agent role discipline | Names what the agent can read, write, and decide. |
| Evidence quality | Separates proxy feedback from stronger tool evidence. |
| Rejection | Uses explicit gates and preserves negative traces. |
| Source trace | Records tool, version, inputs, outputs, and assumptions. |
| Decision quality | States a defensible, bounded human decision. |
| Residual risk | Names what would overturn the result. |

## Immediate Next Steps

1. Create the `labs/README.md` and first lab `.loop-plan.md`.
2. Prototype the receipt schema and validator before the UI.
3. Install and smoke-test SCALE-Sim with one tiny topology.
4. Commit a fixture SCALE-Sim output so tests do not require full simulator runs.
5. Build the marimo lab around the working command-line path.
6. Add the optional agent role only after the receipt validates.
7. Package the half-day tutorial around the same lab.

The first milestone should be a boring but complete loop receipt. Once that
exists, the interactive lab, agent variants, and tutorial can grow around a
stable artifact instead of a demo script.
