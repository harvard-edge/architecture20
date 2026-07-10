# Architecture 2.0 Starter Labs — Suite Design (v0 draft for review)

Status: design draft in the `feat/arch2-labs-plan` worktree. Companion to
`ARCH2_LAB_SYSTEM_PLAN.md` (implementation grammar) and the working
`scale_proxy_mirage` example. This document decides *what the labs are*, *why*,
*how they map to the book*, and *how each is structured to teach for
internalization rather than skimming*.

## 0. v1 revisions (from the Codex + Gemini 3.1 Pro review round)

Both models reviewed the v0 draft below; where they conflict with v0, this section
wins. Points where Codex and Gemini independently agreed are treated as settled.

- **Spine is 5 labs, reordered so the proxy-overstatement lab is the anchor**
  (Codex): Lab 0 Prompt-to-Card (worked example first) → **Lab 1 Proxy vs
  Evidence (anchor)** → Lab 2 Environment Contract (introduced only *after* the
  learner is burned by the proxy) → Lab 3 Earned Trust (rejection, fidelity via
  injected noise, multi-objective, **red-team the environment**) → Lab 4 Capstone
  (two-turn loop, graded by a judgment rubric). Exercises E1–E3 unchanged; E3
  (AlphaChip card) is also the book's Chapter 8/10 demonstration.
- **Validator checks completeness, never the "right" winner** (both). Removed the
  check that required proxy winner ≠ survivor; it manufactured a mirage and
  implied a hidden canonical answer. *(Done in code.)*
- **Honest gates** (both, and our finding #1): utilization and roofline are
  diagnostics, never hard rejections. The hard gates are a stated silicon/area
  budget and the real-time deadline. *(Done in code: the 64×64 is now rejected on
  the 1024-PE mobile budget, not on utilization.)*
- **Prediction-lock captures confidence + reason and scores calibration, not
  correctness** (Codex). Self-explanation must name a mechanism (utilization,
  roofline, budget). *(Done in the Lab 1 notebook.)*
- **Structured commitment gates the receipt; free text is optional** (Gemini);
  the commitment level is checked against the evidence (no RTL/product claim on
  proxy+one-sim evidence). *(Done in the notebook.)*
- **Do not build an `arch2_labs.ui` cell-generator framework** (Gemini) — import
  helpers, keep marimo cells explicit. Replaces v0 build-order step 3.
- **Vary the challenge form** across labs (both): worked example → predict/reveal
  → build-the-contract → audit/red-team → transfer/capstone. Not five identical
  notebooks.
- **Retrieval-question unlock** replaces the passive recap (Gemini). **Worked
  example shown before the learner authors one** (both). *(Done in the notebook.)*
- **Drop-in via seed/state capsules** (both): each lab ships a pre-validated seed
  JSON; cumulative learners load their prior receipt. *(To build.)*
- **Two added dimensions v0 missed entirely:** (a) *adversarial / model-hacking*
  (Gemini) — a learner red-teams SCALE-Sim's idealized memory to make an
  unrealizable design score perfectly, proving why the human gate must be
  independent of the generator; this becomes Lab 3's spine and uses our finding
  #2. (b) *a judgment rubric* (Codex) — weak / adequate / excellent criteria for a
  rejection, a commitment, and a loop contract when there is no single right
  answer; it becomes a shared artifact and the capstone's grading basis.
- **Version estimate assumptions in every receipt + keep a frozen golden
  workload** (Codex). *(ESTIMATE_SOURCES already ships in the ledger; golden
  fixture to add.)*
- **MVP release = Labs 0, 1, 4** (card, proxy failure, capstone) as a coherent
  half-day tutorial.

Status: the honest engine and the runnable **Lab 1 (Proxy vs Evidence)** marimo
notebook exist and are validated (`examples/scale_proxy_mirage/lab.py`).

## 1. The single design bet

A learner should not leave a lab able to *describe* a design loop. They should
leave having *run one, been wrong about it, and reconciled the surprise*. Every
structural choice below serves that bet. The mechanism is a fixed rhythm:
**recap → predict (locked) → run a real tool → reconcile the surprise → reject →
decide → receipt.** The prediction lock and the reconcile step are the whole
point; a lab that lets you read the answer before committing a prediction
teaches nothing.

## 2. What the empirical build already told us (constraints, not aspirations)

We built and ran the first environment against real SCALE-Sim 3.0.0, then added
literature-grounded energy/roofline estimates. Three findings constrain the
whole suite. Design to them; do not design around them.

- **No rigged reversals.** The book's Chapter 8 typed a losing energy number by
  hand. When we compute energy from real DRAM access counts (Horowitz 45 nm,
  Accelergy-style), the *big* array is actually lowest-energy and fastest, so the
  hand-picked "accelerator loses on energy" reversal is directionally wrong for
  this workload. Labs must teach honest, tool-produced results, never a gate
  chosen to force a predetermined loser.
- **SCALE-Sim v2 has an idealized memory.** The big array never stalls even at
  DRAM bandwidth 2 words/cycle (measured). A clean "big array stalls and misses
  the deadline" story is *not honestly available* in this tool. State the tool's
  limits in the lab; do not pretend past them.
- **The honest lessons are better than a gotcha.** From real numbers:
  *proxy overstatement* (the MACs/PE proxy predicts the 64×64 is 16× faster;
  SCALE-Sim measures 7.5×, and utilization is the gap) and *multi-objective
  conflict* (the 64×64 wins latency and energy but at 14% utilization, so the
  winner depends on whether you are latency-bound or cost-bound). These are truer
  to the book than any single-gate rejection.

## 3. The suite: a spine of runnable labs + light chapter exercises

Ten full marimo labs is too many to build well and too long a sequence to
finish. The book's arc is a loop, so the labs are a loop: a **spine of six
runnable labs** that cumulatively build and run one loop on the shared
lighthouse prompt (low-power RISC-V mobile-XR subsystem), plus **three short
exercises** for the chapters whose lesson is analytical, not computational. That
is "a handful to generate," and it is a complete learning sequence.

The same lighthouse prompt threads all six labs. Each lab adds exactly one loop
element, so by the capstone the learner has assembled the whole loop, not six
disconnected demos.

| # | Lab (runnable unless noted) | Book chapter(s) | The one loop element it adds | The internalized lesson |
| --- | --- | --- | --- | --- |
| **0** | **Prompt to Loop Card** | Ch1–3 (moonshot, scissors, framework) | The loop contract | A prompt is not an architecture claim until task, actions, evidence, rejection, and commitment are named. |
| **1** | **Representing Loop State** *(light)* | Ch4 (data, world models) | Represented state + provenance | A result you cannot replay is not evidence; negative traces are architecture data. |
| **2** | **The Environment Contract** | Ch5 (environments, tool interfaces) | The environment (SCALE-Sim) | A tool becomes an environment only when legal actions, observations, invalid-action semantics, cost, and provenance are explicit. |
| **3** | **Proxy vs Evidence: the Cheap-Model Trap** | Ch6 (generation/prediction/optimization) | Method roles under a feedback budget | A cheap proxy does not just pick wrong winners; it *overstates* advantages by assuming realizability the tool later denies. |
| **4** | **When Has the Loop Earned Trust?** | Ch7 (feedback, verification, trust) | Fidelity ladder + rejection authority | No single metric owns the commitment; when latency and cost-efficiency disagree, the architect must state the governing objective before selecting a winner. |
| **5** | **Run the Whole Loop (Capstone)** | Ch8 (running the loop) | The full turn + receipt | A defensible decision states its commitment boundary and what evidence would overturn it. |
| E1 | *Exercise:* The Same Loop at Different Costs | Ch9 (patterns across the stack) | — | Method posture changes as feedback gets expensive and commitments get harder to reverse. |
| E2 | *Exercise:* Redact and Share a Negative Trace | Ch10 (what the architect owns) | — | Field infrastructure is an incentive problem; you can share a lesson without the IP. |
| E3 | *Exercise:* Audit AlphaChip with the Card | Ch10 + preface war story | — | Fill the design-loop card for a real, contested, public claim; the empty "replayable inputs" field is where the dispute lives. (Ties to the book's AlphaChip demonstration.) |

Labs 2–5 reuse the working `arch2_labs` engine (SCALE-Sim wrapper, estimates,
receipt, validator). Lab 0 and E1–E3 are no-simulator. E3 doubles as the
book's AlphaChip worked-card demonstration; building the lab and fixing the book
are the same task.

## 4. Anatomy of one lab (the marimo notebook contract)

Every runnable lab is one marimo notebook with the same eleven cells, so the
rhythm becomes muscle memory. marimo is the right surface because its reactive
cells let a knob change re-run the evidence live, and because a locked prediction
cell can gate the reveal.

1. **Learning objectives** — what you can *do* after, in verbs.
2. **Book recap** — the chapter concept in 3–4 sentences, using the book's exact
   vocabulary (loop contract, evidence ledger, commitment boundary…).
3. **Loop brief** — claim, workload slice, design space, commitment boundary.
4. **Predict (locked)** — a structured prediction (radio/dropdown, no free text)
   the learner must submit before any evidence renders. Example for Lab 3:
   "Which array wins on latency? On energy? Will the proxy winner survive the
   gate?" The reveal cells stay hidden until this is submitted.
5. **Knobs (≤3)** — array rows/cols, DRAM bandwidth, budget. Reactive.
6. **Run** — execute the real environment (SCALE-Sim), stream the real CSV
   evidence into charts and a table.
7. **Reconcile** — put prediction next to evidence and name the surprise
   explicitly ("you predicted the 64×64 would be 16× faster; it is 7.5× —
   where did the other 2× go?").
8. **Rejection gate** — apply the declared gates, show negative traces with
   observed-vs-threshold, and separate *diagnostics* (utilization, roofline)
   from *hard gates* (deadline, budget).
9. **Decide** — the learner writes the bounded commitment and the
   would-overturn evidence in their own words. Human-owned, never auto-filled.
10. **Receipt** — export card + environment + ledger + negative traces +
    decision; run the validator inline; download.
11. **Reflect** — one transfer question: what would you change, and what is the
    smallest evidence that would flip your decision?

The command-line path (`python -m arch2_labs.scale_env …`) stays as the CI and
instructor reproducibility route; the notebook is the classroom.

## 5. How each lab teaches for internalization (not high-level)

Five levers, applied in every lab:

- **Prediction lock before reveal.** Commitment creates stakes; a contradicted
  prediction is what converts to memory. This is the MLSysBook "predict-first"
  pattern and it is non-negotiable.
- **Manipulable knobs with live evidence.** The learner *makes* the utilization
  collapse by growing the array, rather than being told it collapses.
- **Reconcile the surprise.** The gap between predicted and measured is named and
  explained mechanistically (roofline: the big array is memory-bound, so its
  extra PEs cannot be fed → the missing 2×).
- **Read the real artifact.** The learner opens the actual SCALE-Sim CSV and the
  actual receipt JSON, not a polished summary. Evidence you can inspect is the
  lesson.
- **Write the decision.** Forcing the learner to author the commitment boundary
  and would-overturn evidence in prose is where the concept becomes theirs.

## 6. Honest-gate policy (so no lab is secretly rigged)

- **Hard gates** (can reject a commitment): deadline (real-time budget), area or
  dollar budget (silicon is the constraint). Both are defensible and stated up
  front, not reverse-fit between two candidates.
- **Diagnostics** (explain, never silently reject): utilization, roofline bound,
  stall fraction. They tell you *why*, and the lab surfaces when a diagnostic
  conflicts with a bottom-line metric.
- **Objective-dependent metrics** (the learner must choose): latency, energy,
  EDP, TOPS/W, TOPS/mm². The lab shows their rankings disagree and refuses to
  name a single winner until the learner declares the objective.
- Every external constant is sourced in-code (Horowitz ISSCC 2014, Accelergy,
  roofline) and labeled order-of-magnitude, mirroring the book's own evidence
  discipline.

## 7. Build order

1. Harden Lab 3 (the working example) to the honest framing above: utilization
   becomes a diagnostic, add a stated budget gate, keep the multi-objective
   table as the lesson. *(This is the current code; small changes.)*
2. Install marimo; build the Lab 3 notebook as the reference implementation of
   the eleven-cell contract.
3. Factor the shared marimo cells into `arch2_labs.ui` so Labs 0, 2, 4, 5 reuse
   them.
4. Build Lab 0 (no simulator) and Lab 5 (capstone) around the same engine.
5. Write E3 (AlphaChip card) — it is also the book's Chapter 8/10 demonstration.
6. Fill in Labs 1, 2, 4 and exercises E1–E2.
7. Wire the corrected Lab 3 numbers back into the book's Chapter 8.

## 8. Open questions for the Codex / Gemini review pass

- Is six runnable labs the right spine, or should Labs 1 and 2 merge (state +
  environment are close)?
- Is prediction-lock-gates-reveal too rigid for a self-paced reader vs a live
  tutorial? Should there be a "reveal anyway" escape that records that the
  learner skipped the prediction?
- Should the capstone (Lab 5) run a *second, contrasting* turn (a candidate that
  is correctly rejected) so the learner sees both a survive and a reject?
- Is SCALE-Sim the right single tool for the spine, or should Lab 4 escalate to a
  second fidelity (Timeloop/Accelergy) to make the "fidelity ladder" real rather
  than narrated — accepting the install cost?
- What is the minimum viable set for a first public release: all six, or Labs 0,
  3, 5 as a coherent half-day tutorial?
