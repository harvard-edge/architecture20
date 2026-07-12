# Architecture 2.0 Research Questions Workbench

Generated July 7, 2026

This workbench collects candidate open research questions and editorial notes for
review before editing the chapter source files. It preserves the working set and
synthesis trail so the chapter questions can be reviewed without rebuilding the
book.

The latest working set is **Compression and Operationalization Pass**. The latest
feedback synthesis is **Expanded Draft Review Feedback**. Earlier synthesis
sections are retained as provenance for how the set evolved.

## Compression and Operationalization Pass

This pass keeps the U shape and the expanded draft's chapter style, but tightens
the questions after the review round. It cuts repeated scaffolding, clarifies
the local job of recurring concepts, and makes each technical question point to a
testable artifact, setting, metric, or failure mode.

### Chapter 1. Field Wave and Review Norms

These open research questions set the field-level agenda for the rest of the
book. They ask what the architecture community should count, review, reward, and
compare when progress shifts from a generated artifact to the loop that
produced, tested, rejected, and justified it.

1. **When is AI-assisted design work an architecture contribution?**
AI-assisted work becomes architectural when it changes what can be credibly
designed, compared, rejected, or committed under architectural constraints. The
research object is a contribution rubric for loop-level architecture work, with
examples that separate method novelty from architectural state, evidence,
rejection, and human commitment. A serious study would test reviewer agreement
on borderline papers and show where the rubric changes review outcomes. This
question follows from the shift from artifact design to loop design in
@sec-from-architecture-10-to-architecture-20 and from the boundary setting near
the end of the chapter.

2. **How should venues review AI-assisted design-loop claims?**
Architecture review already knows how to inspect artifacts, baselines, and
quantitative tradeoffs. AI-assisted loops add represented state, permitted
actions, rejected alternatives, and commitment boundaries to the review object.
A review protocol, artifact rubric, or shadow-review study could test whether
reviewers identify unsupported commitments earlier and request evidence that
would have clarified contested cases such as the AlphaChip comparison. The
moonshot framing in @sec-moonshot makes this a community problem, not a matter
of individual paper style.

3. **When do rejected alternatives count as architecture evidence?**
Rejected candidates can define a design-space boundary, expose invalid
assumptions, and prevent later loops from rediscovering the same weak path. A
reporting standard for rejected alternatives should record what was tried, what
evidence rejected it, what claim the rejection supports, and when the rejection
expires. The evaluation should ask whether independent reviewers can reconstruct
the design-space boundary and whether later teams avoid repeated invalid regions
without treating weak evidence as final truth. This question builds on
@sec-why-the-prompt-spans-the-stack and
@sec-efficiency-claims-need-rejectable-loops.

4. **What shared artifacts make loop-level progress comparable?**
If AI-assisted architecture remains a collection of isolated showcases, the
field will struggle to compare loops. A shared task family, baseline loop
report, workload packet, and rejection protocol would let groups produce
contrastable reports without pretending every architecture problem has one fixed
benchmark. The evaluation is reviewer agreement and cross-team comparability
under the same task, workload, metric, and rejection record. The lighthouse
decomposition in @tbl-moonshot-decomposition and the MLPerf discussion in
@sec-efficiency-claims-need-rejectable-loops provide the working model.

5. **What should an architecture moonshot leave behind?**
A field-shaping moonshot should leave more than one impressive design. It should
leave tasks, instruments, baselines, evidence standards, trained reviewers, and
maintained artifacts that make later work easier to trust. A research program
could evaluate past architecture and AI-infrastructure examples by asking which
artifacts survived the flagship result and which ones enabled follow-on work,
negative results, or fair rejection. This is the field-level lesson of the
moonshot examples and the AlphaChip war story in @sec-moonshot.

### Chapter 2. Pressure Diagnosis and AI Entry Points

The strain on classical design loops points to a narrower research agenda than
generic AI-for-architecture. The immediate questions are how to measure strain,
where bounded AI should enter, and which pressure signals should trigger triage
before expensive evidence or human commitment is spent.

1. **What measurements reveal a strained architecture loop?**
A loop becomes strained when candidate volume, feedback cost, validation burden,
software drift, and human review latency grow faster than the team's ability to
reject and revise. A strained-loop profile should predict concrete failures such
as wasted high-fidelity runs, missed invalid candidates, delayed decisions, or
stale evidence. Useful measurements include invalid-action rates, feedback
latency and cost, verification staffing, high-fidelity sample budgets, and
decision turnaround. The profile should explain the scissors gap in
@fig-scissors-gap and the cost pressure in @fig-leading-node-design-cost better
than candidate count alone.

2. **Where should AI enter specialized and chiplet design loops?**
Specialization and chiplets expand the loop across workload selection, software
paths, microarchitecture, integration, packaging, validation, and physical
feasibility. AI should enter where the bottleneck is measurable, not wherever a
model can produce more candidates. A strong study would compare entry points
under the same validation budget and report invalid candidates avoided, missed
software obligations, high-fidelity checks saved, and lost tradeoff quality. The
expanding design spaces in @tbl-design-loop-scale-anchors and the discipline in
"AI Helps Only When the Loop Is Designed" provide concrete testbeds.

3. **Which physical signals should triage expensive validation?**
Physical reality becomes an architecture concern when data movement, timing
margin, congestion, power density, thermal behavior, or closure risk can overturn
an early architectural win. A useful triage suite would compare early signals
against later synthesis, floorplan, placement, routing, STA, DRC or LVS, EM/IR,
and power outcomes. The evaluation should report false accepts, false rejects,
inconclusive runs, and engineering effort saved. The goal is earlier routing
toward rejection, revision, or stronger evidence, not signoff-quality prediction.
The pressure comes from @sec-physical-constraints-move-into-architecture,
@fig-waterbed-effect, and @fig-data-movement-energy-scale.

4. **When does workload drift expire architecture evidence?**
Architecture evidence can age out when models, compilers, kernels, runtimes,
precision formats, traces, or deployment scenarios move faster than the hardware
decision they support. A validity-horizon study should define drift tests such
as rank reversal, confidence degradation, support exit, baseline invalidation,
or objective-vector change. Historical workload or software changes can show
when an earlier ranking, constraint, or efficiency claim should be maintained,
weakened, or withdrawn. This question builds on
@sec-software-changes-faster-than-silicon and the workload-growth pressure shown
in @fig-ai-compute-growth.

5. **When do multiobjective tradeoffs overwhelm manual evaluation?**
Modern architecture choices mix performance, energy, power, area, cost, carbon,
verification burden, simulator hours, tool availability, and human review.
Manual evaluation breaks down when the team can no longer inspect the trade
space before evidence expires or high-value candidates are pruned. A
feedback-priced exploration study should compare manual triage, AI-assisted
triage, and bounded exhaustive baselines. The key metrics are lost Pareto
candidates, invalid survivors, feedback spent, review effort, and commitment
mistakes. The question connects @tbl-ai-assumptions-architecture-violations to
@sec-feedback-and-verification-become-the-bottleneck.

### Chapter 3. Ontology and Reviewable Claims

The ontology in this chapter turns AI-assisted architecture work into a
reviewable claim and loop record. The research agenda is to make that record
lighter, more precise, and easier to check before later chapters add richer
representations, environments, methods, and trust machinery.

1. **What minimum claim packet makes AI-assisted architecture work reviewable?**
A generated artifact becomes architecture work only when it is attached to the
claim fields that let someone else inspect what is being asserted. A minimal
claim packet should expose workload, baseline, design space, objective,
constraints, evidence, rejection authority, commitment boundary, and decision
owner, drawing on @tbl-architectural-claim-schema and the design-loop card in
@sec-appendix-b-design-loop-card. The evaluation should use real or synthetic
papers and ask whether independent reviewers can reconstruct the claim, identify
missing fields, compare packets, and distinguish artifact plausibility from
architectural commitment.

2. **What workload and baseline records make a claim credible?**
Workload and baseline names are not enough. The workload record should describe
input classes, traces or phases, software stack, deployment mix, sampling
policy, exclusions, and version window. The baseline record should describe
implementation, tuning effort, tool versions, known weaknesses, and why it is
the right comparison. A credible packet should let reviewers decide whether the
comparison is fair, whether another baseline would change the result, and
whether the workload scope matches the commitment boundary in
@tbl-architectural-claim-schema and @fig-design-loop.

3. **How can holdout benchmarks expose loop overfitting?**
An AI-assisted loop can overfit to a benchmark when task framing, search choices,
or evaluation rules are tuned after seeing failures. A benchmark packet should
separate what the loop can see during search from what reviewers or evaluators
hold out, including workload slices, baseline variants, design-space regions,
tool versions, and failure modes. The test is false confidence. A loop that
looks strong on visible cases should still face held-out cases that preserve the
same architectural claim structure. The framework checklist in
@tbl-compact-framework-checklist provides the alignment target.

4. **How can rejected alternatives become auditable design-space evidence?**
A surviving candidate is hard to interpret when rejected candidates disappear.
The design space in Chapter 3 contains legal choices and invalid regions, so a
rejection record can state which boundary was tested, which objective or
constraint failed, which baseline or candidate was weakened, and what evidence
would reopen the decision. The evaluation should ask whether reviewers can
reconstruct why the reported candidate survived and whether future loops avoid
known failures without treating local exclusions as universal laws. The relevant
anchors are @tbl-architectural-claim-schema and @fig-design-loop.

5. **What can a design-loop card catch before execution?**
Some defects should be visible before the loop calls a simulator, compiler,
benchmark harness, or model. A static card checker could catch missing workload
scope, ambiguous baselines, illegal action fields, mismatched objective units,
impossible constraints, missing rejection conditions, or overstrong commitments.
The evaluation should seed historical and synthetic claim cards with review
blocking defects, then measure what the checker catches without replacing
architectural judgment. Relevant targets include @fig-design-loop-card-example and
@tbl-compact-framework-checklist.

### Chapter 4. Representations and World Models

The gap between public architecture knowledge and actionable loop state is
significant. The questions here focus on representations, not yet on full tool
environments or governance. Each one asks what data structure, learning problem,
or benchmark would make architecture state more replayable, calibrated, and
useful inside an AI-assisted loop.

1. **What semantics make architecture proposals replayable and rejectable?**
Architecture proposals sit between human intent and tool-facing action, but they
often remain informal narratives rather than replayable boundary objects. A
proposal representation should record task intent, mutable and immutable design
fields, candidate identity, assumptions, evidence pointers, and rejection
reasons. The evaluation should ask whether reviewers can replay a proposal,
compare it with rejected alternatives, detect missing provenance, and reject
unsupported claims without relying on private author memory. The boundary-object
discussion in @sec-architecture-descriptions-as-boundary-objects supplies the
actionable representation test.

2. **What should costly architecture samples record?**
A sample in this chapter is a feedback event, not a labeled row. Its cost
changes what an optimizer should do next. A sample receipt should record setup
cost, tool cost, human triage, fidelity, provenance, coverage, opportunity cost,
and commitment level, following @sec-sample-cost-is-architecture-data and
@tbl-sample-cost-regimes. The evaluation should test whether later loops can
reuse samples to choose cheaper next evaluations, avoid known failures, separate
tool failure from design failure, and preserve the evidence meaning of
high-cost feedback.

3. **When is an architecture world model outside calibrated support?**
A world model is useful only where its predictions, uncertainty estimates, and
invalid-move warnings still mean what the loop thinks they mean. A calibrated
support map should state which workload slices, design parameters, tool
versions, and fidelity levels support a prediction or rejection warning. The
evaluation should report false accepts, false escalations, uncertainty coverage,
and evidence cost under shifted workloads or stronger-fidelity checks. Success
means lower commitment risk at the same feedback budget, or lower feedback cost
at the same risk, as motivated by @sec-toward-architecture-world-models and
@tbl-xr-world-model-sketch.

4. **What coverage record tells reviewers when a result generalizes?**
A result may be replayable and still fail to generalize if its samples cover
only one workload phase, trace slice, architecture class, or evidence regime. A
coverage record should attach workload-space, design-space, and fidelity-space
coverage to each sample and negative trace. The evaluation should ask whether
reviewers and downstream optimizers can predict when a design-space lesson
transfers, weakens, or should be withheld from a new claim. Held-out workload
slices, shifted traces, and uncovered candidate regions provide the test cases.
This connects @sec-sample-cost-is-architecture-data with
@sec-provenance-coverage-and-negative-traces.

5. **How should representations preserve negative traces?**
Rejected candidates, failed runs, invalid configurations, and human rejections
define much of the usable design boundary, but they are easy to lose or flatten
into generic failure labels. A representation task suite should preserve
candidate context, failure reason, fidelity level, coverage boundary, and
decision owner. The evaluation should measure repeated failures avoided, transfer
to nearby design spaces, preservation of local failure context, and resistance
to overgeneralizing one rejected candidate into a false universal rule.
@tbl-negative-traces and @sec-provenance-coverage-and-negative-traces define the
evidence such representations need to preserve.

### Chapter 5. Environments and Tool Contracts

The concepts in this chapter make tool interfaces into research objects. The
open questions here ask how architecture environments should expose legal
action, preserve tool evidence, reject invalid candidates, reuse failures across
flows, and remain valid after the tool world changes.

1. **What must an architecture environment contract expose before a loop can act?**
A generative loop cannot safely treat a simulator, compiler, runtime, EDA flow,
or telemetry path as a callable function until the environment names what the
loop may change, what it may observe, what feedback costs, and what outcomes are
admissible under the contract. A minimal environment contract should define
actions, observations, costs, invalid-action outcomes, provenance, and local
rejection paths. A second optimizer or reviewer should be able to run the same
harness, replay the same actions, recover the same invalid-action outcomes, and
distinguish comparable feedback from private wrapper behavior. The fields in
@tbl-environment-contract and @tbl-architecture-interface-boundaries define the
contract surface.

2. **How can legacy tool traces suggest environment contracts?**
Legacy tools expose fragments of a contract through scripts, warnings, logs,
timeouts, reports, waived errors, and version-specific behavior. A credible
system should infer candidate contract fields from tool traces and then require
expert validation plus conformance tests. The evaluation should use held-out tool
runs to measure whether the inferred contract predicts legal actions,
recoverable failures, blocking warnings, and report fields that support the
environment claim. The strongest result would reduce expert wrapper effort
without pretending logs alone are a contract.

3. **How should environments classify invalid actions and rejection paths?**
Invalid actions are structured evidence about the boundary between the
architecture problem and the tool world. The outcome taxonomy should distinguish
malformed input, unsupported knob, infeasible constraint, tool crash, timeout,
inconclusive run, waived violation, physical violation, proxy insufficiency, and
escalation required. An environment API should report those outcomes in a form
that a loop can replay and a reviewer can inspect. The evaluation should use
generated candidate streams that intentionally hit boundary cases and report
classification consistency, false passes, false rejects, and reviewer effort.
A relevant target is "Building Environments for New Subfields" and
@pri-tools-environments.

4. **How can negative evidence transfer across simulated and physical tool flows?**
A late physical rejection can sometimes teach an earlier simulator-backed
environment what not to spend samples on, but that lesson is dangerous if it
loses context. A portable failure receipt should preserve node or PDK, corners,
constraints, libraries, macros or IP, floorplan context, tool versions, seeds,
waivers, workload, and power intent when those fields matter. The evaluation
should ask whether receipts improve early rejection in proxy or simulation
environments without discarding valid candidates under held-out workloads,
changed constraints, or different technology assumptions. @tbl-eda-stage-contract
and @tbl-feedback-latency-fidelity give the local evidence ladder.

5. **How do architecture environments stay valid as tools and workloads drift?**
An environment contract can be correct on the day it is built and misleading
after workload revisions, compiler changes, simulator updates, deprecated knobs,
new failure modes, or changed rejection thresholds. An environment-validity
monitor should flag stale action, observation, provenance, or rejection fields
and trigger the smallest recertification run needed before the loop acts again.
The evaluation should use versioned environment histories with known semantic
changes and measure whether the monitor preserves, weakens, or invalidates the
environment's supported claims. The scope is local operating discipline from
@sec-archops-operating-discipline and @tbl-archops-operating-discipline, not the
Chapter 10 problem of community infrastructure.

### Chapter 6. Method Roles and Feedback Allocation

The discipline of assigning AI methods to specific loop roles exposes a method
agenda, not a leaderboard agenda. At this point in the book, the unsettled
questions concern how methods remain bounded, how scarce feedback is spent, and
how a loop changes roles without turning method output into architect-owned
commitment.

1. **What role contracts keep AI methods from becoming decision makers?**
The method-role view in @fig-method-role-map, @tbl-method-role-discipline, and
@tbl-method-object-discipline asks each participant to act on a named object
through a named interface. A role contract should state what each generator,
predictor, optimizer, critic, repair method, verifier, explainer, or coordinator
may read, write, propose, reject, or escalate. The evaluation should include
multi-participant traces with deliberate authority violations, such as a
predictor promoting a ranking into a decision. Useful metrics include violation
detection, false alarms, logging cost, and preservation of the architect-owned
boundary in @sec-choosing-a-method-under-constraints.

2. **How should loops spend scarce feedback across method roles?**
Sample efficiency in @sec-sample-efficiency-under-expensive-feedback treats
feedback as scarce, but a loop must decide which role should receive the next
unit of feedback. It may need more generation, cheaper prediction, targeted
optimization, critique, or repair. A role-aware scheduler should be evaluated on
bounded design-space exploration tasks, with static pipelines and existing DSE
methods as baselines. The metrics are high-fidelity runs avoided, invalid-action
rate, repeated failures avoided, lost tradeoff quality, and whether the final loop record
explains why feedback was spent where it was. The regimes in
@tbl-sample-efficiency-regimes and the constraints in
@tbl-method-selection-matrix provide the setup.

3. **How can optimizers use negative traces without losing fidelity labels?**
Failed simulations, invalid candidates, timeouts, rejected configurations, and
proxy mismatches are information about the boundary of the design space. They
become dangerous training data when their evidence strength is flattened. A
fidelity-labeled negative-trace schema should preserve reason, scope, fidelity,
and reopening condition. The evaluation should compare search policies that
preserve fidelity labels against policies that collapse all failures into one
negative class. The metrics are sample efficiency, false pruning of valid
regions, repeated invalid-action avoidance, rejection-strength calibration, and
cases where cheap negative evidence still requires escalation.

4. **What bounded rejection suites test hardware-aware generators?**
The hardware-awareness ladder in @fig-hardware-awareness-ladder and the tests in
@tbl-hardware-awareness-assessment and @tbl-hardware-awareness-tests make
hardware awareness observable. A bounded rejection suite should test a named
environment and artifact class, such as kernels, simulator configurations, RTL
fragments, constraints, or design-loop cards. The suite should include invalid
candidates, near misses, valid but weak candidates, and valid candidates that
stress portability, numerical tolerance, constraint handling, and provenance.
The metrics are false passes, false rejects, replayability, coverage of the
claimed hardware-awareness level, and the strongest method role the suite
supports before stronger feedback is required.

5. **When should a loop hand off between method roles?**
This is an intra-loop question, distinct from Chapter 9's cross-stack posture
changes. A generator may be useful early, a predictor may dominate while
uncertainty is narrow, a critic may become central when workload coverage is
missing, and repair may be the right role after a tool rejects a malformed
artifact. A handoff policy should route loop state among generation, prediction,
optimization, critique, and repair based on uncertainty, failure reason,
feedback cost, and expected architectural value. The evaluation should compare
adaptive handoffs against fixed role orderings under the evidence gap in
@fig-evidence-gap while checking that the policy obeys role contracts.

### Chapter 7. Evidence and Trust

The mechanisms in this chapter make trust reviewable, but they leave several
research artifacts unfinished. The questions here ask how evidence stays bound
to claims, how proxy wins are challenged before commitment, and how rejection
authority remains independent when the evidence path is under pressure.

1. **How should evidence ledgers limit commitment?**
Fidelity ladders and evidence ledgers record what a loop has seen, while
commitment levels determine how far a claim may travel. The open problem is
preventing weak evidence from authorizing a stronger claim than it supports. A
claim-bound ledger should record feedback rung, provenance, uncertainty,
rejected alternatives, waivers, and the highest supported commitment level for
each candidate. The evaluation should include replay tests, omission tests,
downgrade behavior when evidence is missing, and false-authorization rates on
mixed proxy, simulation, synthesis, and human-review packets. The chapter
anchors are @sec-fidelity-ladders-and-evidence-ledgers and
@sec-commitment-levels-and-reversibility.

2. **What benchmarks expose proxy exploitation before commitment?**
Proxy mismatch and metric gaming become more dangerous when a generator can
search until it finds a candidate that wins the proxy and fails the architecture
objective. A proxy-exploitation benchmark should include adversarial candidate
families, calibrated support regions, hidden higher-fidelity checks, and known
failure modes such as power leakage, timing pressure, workload drift, or
unpriced interface cost. The metrics are proxy false-pass rates, escalation
precision and recall, budget overhead, and how often the loop rejects or
escalates a misleading winner before it crosses the commitment boundary. The
proxy-mismatch discussion in @sec-proxy-mismatch-metric-gaming-and-calibration
defines the failure mode.

3. **How can rejection authorities be tested for independence?**
Verification authorities add trust only when they can fail independently of the
method that produced the candidate. A rejector-dependency model should record
shared model family, training data, objective, tool path, evidence source, task
instructions, and human instructions. The evaluation should inject shared blind
spots, correlated tool failures, and cases where multiple apparent reviewers
agree for the same wrong reason. The result should predict when consensus is
repetition and when a rejection authority can actually block an unsupported
claim. A relevant anchor is @tbl-verification-authorities.

4. **How should loops stress-test compromised evidence sources?**
Ordinary proxy mismatch is not the same as corrupted or adversarial evidence. A
loop also needs to survive stale baselines, poisoned traces, tampered logs,
selective reporting, simulator drift, and missing negative evidence. An
adversarial evidence harness should inject those faults into a normal
architecture loop and measure false commitment rate, time to detection,
escalation cost, and whether the loop downgrades the claim or demands
independent evidence. This extends the evidence-dispute logic in
@sec-evidence-disputes-and-the-trust-checklist.

5. **How can confidential evidence remain auditable?**
Private evidence can support a claim only if the review mode is explicit. Public
summaries, confidential artifact review, and privileged reproduction provide
different evidence regimes. A confidential evidence capsule should record data
class, access rule, redaction boundary, local replay receipt, claim scope, and
the public proxy that would be insufficient. The evaluation should test whether
an authorized reviewer can confirm fidelity, provenance, missing-evidence risk,
and rejection authority without exposing protected material. It should also
measure leakage risk and cases where redaction hides evidence that should have
forced escalation. A relevant anchor is @tbl-trust-checklist.

### Chapter 8. Executing One Loop

The lighthouse loop shows one bounded turn, not a general recipe. The research
questions here ask what artifacts would make that same discipline repeatable
when high-level intent becomes a legal turn, a proxy win faces stronger
evidence, and a recorded rejection remains useful without pretending to be final
forever.

1. **How can architectural intent become one bounded loop turn?**
The chapter lowers a broad XR subsystem request into one XRBench-class slice,
three legal candidate organizations, and two declared gates in
@tbl-active-lighthouse-slice. The research problem is formal bounds extraction,
not text parsing. An intent-to-turn method should produce workload scope, legal
actions, candidate records, excluded evidence, rejection gates, and a commitment
boundary. The evaluation should ask whether independent architects reconstruct
the same task boundary, detect invalid actions, and replay the turn without
granting the AI authority beyond the slice shown in @fig-loop-beat.

2. **What signals should trigger escalation in one loop turn?**
Round One uses a cheap proxy only to rank candidates, then Round Two escalates
because that proxy has no final rejection authority. A loop-turn escalation
policy should read proxy uncertainty, coverage, sensitivity to data movement,
interface assumptions, and constraint proximity. The evaluation should compare
the policy against static escalation in the lighthouse setting, measuring false
commitments, false rejections, evidence cost, and whether the loop still stops
at the honest commitment level recorded in @tbl-worked-loop-ledger.

3. **How can proxy workloads expose data-movement mirages?**
The proxy mirage in @fig-proxy-mirage is a research generalization, not only a
toy reversal. A proxy-audit workload suite should use paired kernels and traces
that separate compute, locality, interface traffic, DMA behavior, and shared
memory effects for accelerator, vector, and SoC-block candidates. The evaluation
should show that the suite predicts ranking reversals before scarce simulation
is spent, bounds the proxy claims that remain valid, and catches the
data-movement failure explained in Round Three.

4. **What receipt metadata makes rejected candidates reusable?**
The loop receipt in @tbl-loop-replay-receipt preserves more than the winner. A
negative-trace receipt should include workload slice, coverage labels, tool
versions, constants, fidelity level, rejection gate, failure mechanism,
sensitivity notes, and next evidence required. The evaluation should ask whether
the metadata prevents duplicate rediscovery, lets another architect reconstruct
the rejection in @tbl-worked-loop-card, and distinguishes a dead end from a
candidate rejected only under one bounded assumption set.

5. **When should a recorded rejection be reopened?**
A negative trace is useful because it prevents repeated failure, but it becomes
harmful if it permanently excludes a candidate whose workload, software stack,
process node, interface, or evidence tool has changed. A reopening policy should
use receipt fields to decide which assumption expired and which original failure
mode must be rechecked. The evaluation should show that reopened candidates
clear a changed-assumption test before reentering search and that the loop does
not convert stale rejection records into permanent bans or automatic revivals.

### Chapter 9. Cross-Stack Loop Patterns

The loop patterns outlined in this chapter define operating regimes across the
stack. The questions here ask what can move safely between regimes, what must be
recalibrated, and when a local result stops being architecture evidence.

1. **What transfers safely across loop patterns?**
A loop card is useful only if some fields can travel between regimes without
smuggling in false authority. Workload packets, baseline assumptions, objective
vectors, rejection gates, and negative traces may transfer from a fast software
loop into DSE, co-design, deployment, or high-commitment RTL work, but their
authority changes with feedback cost and rollback risk. A transfer contract
should state which fields are portable, which fields must be weakened, and which
fields require fresh evidence. The evaluation should replay multi-stage design
studies and measure invalid transfers, stale baselines, and objective drift
against @tbl-loop-patterns and @tbl-loop-pattern-decision.

2. **What error bounds make cheap cross-layer rejectors usable?**
The rejection-bound view in @sec-the-rejection-bound depends on cheap,
independent rejection, yet a rejector that passes the wrong candidate only moves
risk to a later and more expensive stage. Cross-layer rejectors such as
interface-cost models, compiler legality checks, power screens, replay
harnesses, or deployment guards need calibration against stronger evidence. A
rejector-calibration suite should report false passes and false rejects by
commitment level, layer boundary, and workload slice. The result should state
the maximum claim each rejector can clear before escalation is required.

3. **When should loops change posture across stack regimes?**
This chapter-level question is distinct from Chapter 6's intra-loop method
handoffs. A loop may need to move from surrogate prediction to constrained
optimization, from generator-critic repair to simulation, or from exploration to
deployment guardrails as feedback latency and rollback cost rise. The evaluation
should test whether posture changes improve loop cost, rejection quality, and
final candidate quality across @fig-loop-pattern-spectrum while respecting the
autonomy rule in @pri-change-autonomy.

4. **How can loops detect single-layer wins that fail system objectives?**
Many cross-stack failures occur when one layer improves its local metric while
the system objective gets worse. A kernel speedup can lose to interface cost, an
accelerator win can disappear in the compiler path, and a compute optimization
can raise memory traffic, power, or tail latency. A system-objective rejection
suite should seed candidates that look strong in one layer and fail after data
movement, software reachability, network contention, or power constraints are
measured. The evidence should require end-to-end objective vectors and negative
traces, grounded in @fig-logca-breakeven, @fig-codegen-narrow-waist, and
@fig-hardware-software-coevolution.

5. **How should loops track evidence half-life across co-evolving stacks?**
Evidence half-life is the period over which an architecture claim remains
defensible as workloads, compilers, runtimes, hardware targets, tool versions,
and deployment conditions change. An evidence-validity ledger should attach
dependency edges, version ranges, refresh triggers, and invalidation rules to
each claim. The evaluation should replay historical stack changes and ask
whether the ledger flags stale evidence before an optimizer composes it into a
new cross-layer claim. Relevant anchors include @tbl-workload-characterization-20
and @fig-hardware-software-coevolution.

### Chapter 10. Ownership and Community Infrastructure

Building shared infrastructure and navigating the transition to AI-assisted
architecture leaves several unsettled research directions. At the end of the
book, the questions return to ownership. The technical challenge is to make
redacted evidence, shared failures, physical and integration knowledge, human
stop authority, and maintained standards durable enough for community-scale
practice.

1. **How can redacted loop ledgers be audited without revealing design state?**
The problem is not to make private architecture work fully reproducible in
public. It is to make the public record strong enough for reviewers to audit
what the loop claimed, what it observed, what it rejected, and who accepted the
commitment. A redacted ledger should expose projected proxies, ownership
records, evidence stages, and redaction boundaries, extending
@lst-redacted-trace and @tbl-public-evidence-ledger. The evaluation should ask
whether reviewers can detect missing workload scope, missing
action-observation context, unsupported escalation, or hidden decision ownership
without seeing proprietary design state.

2. **How can negative traces become shared infrastructure?**
Architecture practice loses field knowledge when failed candidates, invalid
configurations, stale benchmarks, misleading proxy wins, and rejected fixes
disappear into private notebooks or tool logs. A shared negative-trace corpus
should preserve rejection reason, fidelity level, scope, authority, redaction
boundary, and reopening condition. The evaluation should ask whether new loops
avoid known failure modes, reopen old rejections only when new evidence
justifies it, and preserve the original rejection authority. The long-horizon
challenge table and public evidence ledger, @tbl-long-horizon-challenges and
@tbl-public-evidence-ledger, define the infrastructure setting.

3. **How can tacit physical and integration constraints become loop state?**
The relevant tacit knowledge is not general intuition. It is the physical and
integration knowledge that keeps architecture work honest, including packaging
limits, compiler assumptions, integration risks, workload exclusions, waivers,
and product-specific failure experience. A capture workflow should turn those
constraints into reviewable environment contracts, hidden-state lists, evidence
gates, and rejection rules. The evaluation should ask whether the loop makes
fewer invalid actions, whether reviewers can trace each constraint to a human
source or decision owner, and whether the representation preserves human
override. Relevant anchors include @fig-tacit-extraction-bridge and
@tbl-architect-owned-artifacts.

4. **How can human stop authority survive long-horizon multi-agent loops?**
As loops become asynchronous, distributed across tools, and maintained across
personnel changes, the ability to halt a claim can decay even when the record
looks complete. A commitment ledger should record ownership transfer, expiration
conditions, revalidation triggers, waiver history, and human stop authority. The
evaluation should ask whether a later reviewer can identify who owns a stale
claim, which evidence still supports it, which event forces re-approval, and who
can stop the loop before a higher commitment is made. Relevant anchors include the
Ownership Test, @fig-architect-owned-boundary, and @pri-human-accountable.

5. **What makes Architecture 2.0 infrastructure durable?**
Loop cards, evidence ledgers, environment contracts, and negative-trace corpora
will not become field infrastructure unless the community rewards maintenance,
retirement, and reuse as much as first publication. A durability standard should
define acceptance criteria, versioning expectations, stale-record retirement,
owner transfer, maintenance obligations, and minimum evidence packets. The
evaluation should measure whether a maintained artifact still supports
independent review after tools, workloads, models, and owners change, and
whether artifact committees can distinguish durable infrastructure from a
one-time demonstration. Relevant anchors include @tbl-role-agenda,
@tbl-minimum-credible-loop-packet, and @tbl-architecture-20-design-principles.

### Remaining Setup Notes

These are not chapter edits. They are the setup points that should be handled
before this pass is copied into chapter source files.

- Chapter 1 needs a compact bridge from rejected alternatives to scholarly
  credit and a sentence connecting venue review to CFPs or artifact review.
- Chapter 2 should name the strained-loop measurement bundle and define the
  operational threshold for manual evaluation breakdown.
- Chapter 3 should introduce workload characterization as distribution,
  benchmark construction, holdout evaluation, provenance, and overfit defense.
- Chapter 4 should define calibrated support and coverage boundary before the
  open questions.
- Chapter 5 should introduce the invalid-action outcome taxonomy and give one
  physical-flow example that transfers into an earlier proxy constraint.
- Chapter 6 should define fidelity-labeled negative traces and show one
  intra-loop handoff example.
- Chapter 7 should separate proxy mismatch from compromised evidence and name
  the evidence regimes for confidential review.
- Chapter 8 should frame intent-to-turn as formal bounds extraction and name the
  receipt fields that govern reopening.
- Chapter 9 should set up evidence half-life and provide one bad-transfer
  example across loop patterns.
- Chapter 10 should sharpen the maintenance-incentive thread for shared
  infrastructure.

## Expanded Draft Review Feedback

This review round sent the full Expanded Draft Pass through several distinct
editorial lenses. The consensus review was positive, with remaining yellow flags
around compression, operationalization, and fit to chapter-level context.

The consensus is that the U shape works and that the expanded draft is a real
improvement over the current chapter questions. The draft is not yet ready to
copy into the chapters. It needs a compression and operationalization pass that
keeps the strong research agenda while reducing repeated scaffolding, tightening
vocabulary, and making the most technical questions more falsifiable.

### Strong Consensus

- The whole-book arc is working. Chapter 1 starts as a field and review agenda,
  Chapters 2-9 descend into technical machinery, Chapter 8 is the bottom of the
  U, and Chapter 10 returns to ownership and infrastructure.
- The strongest technical paper seeds are in the middle chapters. Reviewers
  repeatedly highlighted physical-signal triage, workload drift, benchmark
  construction and holdout evaluation, calibrated world-model support, legacy
  tool traces, scarce-feedback allocation, proxy-exploitation benchmarks,
  proxy-workload mirages, and cheap cross-layer rejectors.
- The negative-evidence thread is important. It should remain, but each chapter
  needs a distinct role for it.
- The workload-characterization thread is now visible. It should be made more
  operational through distribution, holdout, proxy, drift, calibration, and
  evidence-expiry language.
- The broad Chapter 1 and Chapter 10 questions are useful as field-agenda
  questions, even if not every one is meant to seed an ISCA-style technical
  paper.

### Main Revision Themes

- Compress the draft before integration. Several paragraphs use repeated
  scaffolding such as "A plausible artifact," "A strong contribution," and "The
  evidence standard." The chapter version should sound authored, not templated.
- Give each recurring concept one local job. Negative traces, drift, proxy
  escalation, ledgers, and rejection authority recur across chapters. Keep them,
  but differentiate their role by chapter.
- Operationalize key terms. Reviewers asked for clearer thresholds or tests for
  strained, safe, valid, independent, calibrated, expired, and auditable.
- Make workload distributions explicit. Workload characterization should name
  input classes, traces or phases, software stack, deployment mix, sampling
  policy, exclusions, and version window.
- Separate evaluation objects. Proxy workload, proxy metric, surrogate model,
  cheap rejector, and low-fidelity tool run should not collapse into one generic
  proxy concept.
- Tighten EDA and physical-flow language. Physical signals should map to
  recognizable stages and metrics such as synthesis, floorplan, placement,
  routing, STA, DRC or LVS, EM/IR, power, thermal, ECO churn, WNS/TNS,
  congestion, waiver count, and timing-closure iterations.
- Use verification language carefully. The draft should distinguish
  architectural validation, RTL simulation, formal checking, equivalence
  checking, CDC/RDC, lint, emulation, regression coverage, and signoff checks.
- Scope "legal action" as environment-legal or admissible under a contract, not
  as hardware-legal in a formal sense.
- Make confidential and redacted evidence auditable, not fully verified, unless
  the chapter provides an authorized-review or privileged-reproduction mode.

### Questions to Tighten

- Chapter 1. The contribution and venue-review questions are important, but
  they should be framed as field review norms. The moonshot question reads too
  essay-like unless it names a concrete residue such as tasks, instruments,
  baselines, or maintained artifacts.
- Chapter 2. The strained-loop question needs to say what the measurements
  predict. The AI-entry question needs one bottleneck or one flow, not the whole
  stack at once. The multiobjective question needs an operational threshold.
- Chapter 3. Workload and baseline characterization is right, but the title is
  stiff. The benchmark and holdout question is strong, but "loop overfit" needs
  setup and the expansion should not include meta prose about what Chapter 3
  does or does not need.
- Chapter 4. Calibrated support and coverage boundaries need clearer terms. The
  negative-trace question should be narrowed to representation semantics so it
  does not duplicate Chapters 3, 6, 8, and 10.
- Chapter 5. Legacy trace mining should become candidate contract inference
  plus expert validation, not automatic contract recovery. Invalid-action
  outcomes need a status lattice that includes malformed input, unsupported
  knob, infeasible constraint, tool crash, timeout, inconclusive run, waived
  violation, physical violation, proxy insufficiency, and escalation required.
- Chapter 6. Feedback spending and role reassignment overlap. Chapter 6 should
  focus on intra-loop handoffs among generation, prediction, critique, and
  repair, while Chapter 9 handles cross-stack posture changes.
- Chapter 7. Proxy exploitation, compromised evidence, and confidential audit are
  strong, but the chapter should distinguish ordinary proxy mismatch from
  corrupted or adversarial evidence. Confidential evidence should be separated
  from Chapter 10 redacted public ledgers.
- Chapter 8. Intent-to-turn should sound like formal bounds extraction and
  turn construction, not prompt handling. Proxy escalation should stay grounded
  in the worked lighthouse loop.
- Chapter 9. Cross-pattern transfer is important but broad. The draft should
  name what transfers, what loses authority, and what requires fresh evidence.
  Evidence half-life needs one setup sentence.
- Chapter 10. Tacit knowledge should be scoped toward tacit physical and
  integration constraints rather than general expert intuition. Infrastructure
  durability should name measurable artifact decay, maintenance failure, owner
  transfer, expiration, and stale-record retirement.

### Recommended Next Pass

The next pass should be a **compression and operationalization pass** on the
workbench only. It should not edit chapter source files yet.

- Keep the Expanded Draft Pass as the source.
- Tighten the noun-stacked titles.
- Cut repeated template scaffolding from the expansion paragraphs.
- Add one concrete artifact, testbed, metric, or failure mode where reviewers
  flagged vagueness.
- Add lightweight internal tags for each question such as field agenda,
  architecture method, workload or benchmark, tool contract or EDA, ML method,
  evidence or trust, and community infrastructure.
- Preserve Chapter 1 and Chapter 10 as high-level agenda chapters instead of
  forcing every question to behave like a middle-chapter benchmark paper.

## Expanded Draft Pass

This pass drafts the full open-research-question sections in the style currently
used by the chapters. Chapter source files were not modified. Each chapter keeps
a short framing paragraph, numbered bold question titles, and one expansion
paragraph that names a research artifact, an evaluation standard, and the local
chapter material that supports the question.

### Chapter 1. Field Wave and Review Norms

These open research questions set the field-level agenda for the rest of the
book. They ask what the architecture community should count, review, reward, and
compare when the unit of progress shifts from a generated artifact to the design
loop that produced, tested, rejected, and justified it.

1. **What makes AI-assisted architecture work an architecture contribution?**
AI-assisted work becomes architectural when it changes what can be credibly
designed, compared, rejected, or committed under architectural constraints, not
merely when it uses an AI method to produce a plausible artifact. A useful
research agenda would define a contribution rubric for loop-level architecture
work, separating method novelty from architectural state, evidence, rejection,
and human commitment. The evidence standard should include retrospective review
of existing papers, reviewer agreement on borderline cases, and worked examples
showing that the rubric distinguishes an architecture claim from a tool
demonstration. This question builds on the shift from artifact design to loop
design in @sec-from-architecture-10-to-architecture-20 and from the boundary
setting near the end of the chapter.

2. **How should venues review AI-assisted design-loop claims?**
Architecture review has strong norms for artifacts, measurements, baselines, and
quantitative tradeoffs, but AI-assisted design loops also ask reviewers to judge
represented state, permitted actions, rejected alternatives, and commitment
boundaries. A plausible research artifact would be a review checklist,
artifact-evaluation rubric, or shadow-review protocol for AI-assisted
architecture papers. Its evaluation should test whether reviewers reach more
consistent judgments, identify unsupported commitments earlier, and request
evidence that would have clarified contested cases such as the AlphaChip
comparison. The moonshot framing in @sec-moonshot makes this a community problem
rather than a matter of individual paper style.

3. **When do rejected alternatives count as architecture evidence?**
Rejected candidates are not only failures. They can define the boundary of a
design space, expose invalid assumptions, and prevent later loops from
rediscovering the same weak path. A strong research contribution would define a
reporting standard for rejected alternatives, including what was tried, what
evidence rejected it, what claim the rejection supports, and when that rejection
should no longer be trusted. The evaluation should show that independent
reviewers can use the record to understand the design-space boundary and that
later teams can avoid repeated invalid regions without treating weak evidence as
final truth. This question builds on @sec-why-the-prompt-spans-the-stack
and @sec-efficiency-claims-need-rejectable-loops.

4. **What shared artifacts make loop-level progress comparable?**
If AI-assisted architecture remains a collection of isolated showcases, the
field will struggle to tell whether one loop is better than another. A plausible
agenda would build shared lighthouse-style tasks, baseline loop reports,
workload packets, and artifact-review incentives that make loop claims
comparable without pretending every architecture problem has one fixed
benchmark. The evidence standard should require independent groups to produce
contrastable reports under the same task, workload, metric, and rejection
protocol, while also recording where claims can only be reviewed rather than
directly compared. The lighthouse decomposition in @tbl-moonshot-decomposition
and the MLPerf discussion in @sec-efficiency-claims-need-rejectable-loops
provide the working model.

5. **What should a field-shaping architecture moonshot leave behind?**
A useful architecture moonshot should not be judged only by one impressive
generated design. It should leave behind tasks, instruments, baselines, evidence
standards, trained reviewers, and reusable artifacts that make future work
easier to trust. A research program around this question would define criteria
for moonshot readiness and moonshot residue, then apply them to architecture
examples such as Mead-Conway, RISC, MLPerf-style benchmarking, and AI-assisted
design claims. The evaluation should ask whether the resulting infrastructure
supports independent reproduction, fair rejection, negative results, and
follow-on work after the flagship result fades. This is the field-level lesson
of the moonshot examples and the AlphaChip war story in @sec-moonshot.

### Chapter 2. Pressure Diagnosis and AI Entry Points

The strain on classical design loops points to a narrower research agenda than
generic AI-for-architecture. The immediate questions are how to measure when a
loop is strained, where bounded AI should enter, and which pressure signals
should trigger triage before expensive evidence or human commitment is spent.

1. **What measurements reveal a strained architecture loop?**
A classical loop becomes strained when candidate volume, feedback cost,
validation burden, software drift, and human review latency grow faster than the
team's ability to reject and revise. A useful research artifact would be a
strained-loop profile that records candidate counts, invalid-action rates,
feedback latency and cost, verification staffing, high-fidelity sample budgets,
and decision turnaround for one architecture study. The evidence standard should
be predictive. The profile should identify whether a loop is representation
bound, action bound, feedback bound, rejection bound, or commitment bound in
cases like those in @tbl-loop-bottleneck-diagnostic, and it should explain the
widening region shown in @fig-scissors-gap and @fig-leading-node-design-cost
better than candidate count alone.

2. **Where should AI enter a specialization and chiplet loop?**
Specialization and chiplets expand the loop across workload selection, software
paths, microarchitecture, integration, packaging, validation, and physical
feasibility. Adding AI everywhere would only widen the scissors gap unless the
entry point matches the bottleneck. A plausible artifact is an AI-entry map for
a specialized accelerator or chiplet exploration, marking where assistance
should summarize workload evidence, rank candidate regions, predict cheap costs,
check software reachability, or synthesize tool feedback. The evaluation should
compare loop variants under the same validation budget and report whether AI
reduces invalid candidates, wasted high-fidelity checks, and missed software
obligations in settings like the design-space anchors in
@tbl-design-loop-scale-anchors.

3. **Which physical signals should triage expensive validation?**
Physical reality becomes an architecture concern when data movement, power
density, thermal behavior, timing margin, interconnect cost, and tool-closure
risk can overturn an early architectural win. A concrete agenda would build an
early-physical triage suite that exposes these signals before expensive
simulation, synthesis, or physical-design work is spent. The evaluation should
compare cheap physical signals against later tool outcomes, measuring false
accepts, false rejects, and engineering effort saved. The goal is not
signoff-quality prediction, but earlier routing of candidates toward rejection,
revision, or stronger evidence, following the pressure described in
@sec-physical-constraints-move-into-architecture, @fig-waterbed-effect, and
@fig-data-movement-energy-scale.

4. **When does workload drift expire architecture evidence?**
Architecture evidence can age out when models, compilers, kernels, runtimes,
precision formats, traces, or deployment scenarios move faster than the hardware
decision they support. A plausible artifact is a validity-horizon protocol that
packages an architecture result with versioned workload snapshots, software
assumptions, drift monitors, and re-evaluation triggers. The evidence standard
should be retrospective and operational. Replay historical workload or software
changes and show when an earlier ranking, constraint, or efficiency claim should
have been maintained, weakened, or withdrawn. This question builds on
@sec-software-changes-faster-than-silicon and the workload-growth pressure shown
in @fig-ai-compute-growth.

5. **When do multiobjective tradeoffs overwhelm manual evaluation?**
Modern architecture choices mix performance, energy, power, area, cost, carbon,
verification burden, simulator hours, tool availability, and human review.
Manual evaluation fails when these objectives and feedback costs interact faster
than the team can inspect the trade space. A useful research artifact would be a
feedback-priced multiobjective exploration protocol that treats scarce feedback
as part of the optimization problem rather than as an invisible resource. The
evaluation should compare manual triage, AI-assisted triage, and exhaustive or
high-fidelity baselines on bounded slices, reporting lost Pareto candidates,
invalid survivors, feedback spent, and review effort. The question connects the
generic-AI mismatch in @tbl-ai-assumptions-architecture-violations to the
bottleneck in @sec-feedback-and-verification-become-the-bottleneck.

### Chapter 3. Ontology and Reviewable Claims

The ontology in this chapter turns AI-assisted architecture work into a
reviewable claim and loop record. The research agenda is to make that record
lighter, more precise, and easier to check before later chapters add richer
representations, environments, methods, and trust machinery.

1. **What minimum claim schema makes AI-assisted architecture work reviewable?**
A generated artifact becomes architecture work only when it is attached to the
claim fields that let someone else inspect what is being asserted. A plausible
research artifact is a minimal claim-packet schema derived from
@tbl-architectural-claim-schema and the twelve-field design-loop card in
@sec-appendix-b-design-loop-card, with typed fields for workload, baseline,
design space, objective vector, constraints, evidence, rejection authority,
commitment boundary, and decision owner. The evaluation standard should be
reviewer usability rather than schema elegance. Given AI-assisted architecture
papers or internal design reports, independent reviewers should be able to
reconstruct the asserted claim, identify missing fields, compare competing
packets, and distinguish artifact plausibility from architectural commitment.

2. **What workload and baseline characterization makes a claim credible?**
The claim schema is weakest when $W$ and $B$ are labels rather than
characterized objects. For workload, the research problem is to record
distribution, input classes, phase behavior, software stack, version, sampling
policy, and excluded cases. For baseline, it is to record implementation,
tuning effort, tool versions, known weaknesses, and why it is the right
comparison. A strong artifact would be a workload-baseline packet for
Architecture 2.0 claims, linked to the workload and baseline rows of
@tbl-architectural-claim-schema and to the loop state in @fig-design-loop. Its
evidence standard should be replay and disagreement. Reviewers should be able to
inspect enough of the packet to decide whether the comparison is fair, whether
another reasonable baseline would change the result, and whether the workload
scope matches the commitment boundary.

3. **How can benchmark construction and holdout evaluation limit loop overfit?**
An AI-assisted loop can overfit to the benchmark as easily as to a design
objective, especially when task framing, search choices, and evaluation rules are
tuned after seeing failures. Chapter 3 does not need a full environment theory
to ask for a benchmark-construction artifact. A serious agenda would define
benchmark packets with training-visible tasks, sealed holdout workload slices,
baseline variants, invalid candidates, and metadata that records which parts of
the packet were exposed to the loop before a claim was made. The framework
checklist in @tbl-compact-framework-checklist provides the alignment target. The
evaluation should test whether the packet exposes when the claim generalizes,
when it narrows, and when the result is only a benchmark-specific artifact.

4. **How can rejected alternatives become auditable design-space evidence?**
A surviving candidate is hard to interpret when the rejected candidates
disappear. The design space in Chapter 3 is a set of legal choices and invalid
regions, so a rejection record can be more than a failed run. It can state which
boundary was tested, which objective or constraint failed, which baseline or
candidate was weakened, and what evidence would reopen the decision. A plausible
research artifact is a design-space exclusion ledger aligned with the
design-space row of @tbl-architectural-claim-schema and the negative-trace
return path in @fig-design-loop. The evidence standard should test whether
reviewers can reconstruct why the reported candidate survived and whether
future loops avoid repeating known failures without treating local exclusions as
universal laws.

5. **What parts of a design-loop card can be checked before execution?**
Some failures should be visible before the loop calls a simulator, compiler,
benchmark harness, or model. A pre-execution checker could validate that the
card has named workload scope, baseline, legal design actions, objective units,
hard constraints, required evidence, rejection conditions, and the maximum
commitment the current evidence can support, as in
@fig-design-loop-card-example and @tbl-compact-framework-checklist. The artifact
would be a static claim-card linter, not a simulator wrapper or authority
mechanism. Its evaluation should use historical and synthetic claim cards with
seeded omissions, mismatched units, ambiguous baselines, impossible constraints,
and overstrong commitments. Success means the checker catches review-blocking
defects early while leaving architectural judgment, evidence weighing, and later
execution to the human reviewer and subsequent machinery.

### Chapter 4. Representations and World Models

The gap between public architecture knowledge and actionable loop state is
significant. The questions here focus on representations, not yet on full tool
environments or governance. Each one asks what data structure, learning problem,
or benchmark would make architecture state more replayable, calibrated, and
useful inside an AI-assisted loop.

1. **What semantics make architecture proposals replayable and rejectable?**
Architecture proposals sit between human intent and tool-facing action, but
today they often remain informal narratives rather than replayable boundary
objects. A plausible research artifact is an architecture proposal IR that
records task intent, mutable and immutable design fields, candidate identity,
assumptions, evidence pointers, and rejection reasons, building on
@sec-architecture-descriptions-as-boundary-objects and the actionable
representation test. The evidence standard should show that independent
reviewers can replay a proposal, compare it with rejected alternatives, detect
missing provenance, and reject unsupported claims without relying on private
author memory.

2. **What should costly architecture samples record?**
A sample in this chapter is a feedback event, not a labeled row, and its cost
changes what an optimizer should do next. A concrete agenda is a sample receipt
schema for architecture feedback that records setup cost, tool cost, human
triage, fidelity, provenance, coverage, opportunity cost, and commitment level,
following @sec-sample-cost-is-architecture-data and @tbl-sample-cost-regimes.
The evaluation should test whether later loops can reuse the samples to choose
cheaper next evaluations, avoid repeating known failures, separate tool failure
from design failure, and preserve the evidence meaning of high-cost feedback
across candidate comparisons.

3. **When has an architecture world model left calibrated support?**
World models are useful only inside the regime where their predictions,
invalid-action rules, and uncertainty estimates still mean what the loop thinks
they mean. A strong research artifact would be a calibrated-support map for
architecture world models that marks which workload slices, design parameters,
tool versions, and fidelity levels support a prediction, extending the
uncertainty and escalation discipline in @sec-toward-architecture-world-models
and @tbl-xr-world-model-sketch. The evidence standard should report false
accepts, false escalations, and evidence cost under shifted workloads or
stronger-fidelity checks, with success measured by lower commitment risk at the
same feedback budget or lower feedback cost at the same risk.

4. **What coverage record bounds architectural generalization?**
A result may be replayable and still fail to generalize if its samples cover
only one workload phase, trace slice, architecture class, or evidence regime. A
plausible artifact is a coverage ledger that attaches design-space,
workload-space, and fidelity-space coverage claims to each sample and negative
trace, connecting @sec-sample-cost-is-architecture-data with
@sec-provenance-coverage-and-negative-traces. The evaluation should ask whether
reviewers and downstream optimizers can predict when a design-space lesson
transfers, when it weakens, and when it should be withheld from a new claim,
using held-out workload slices, shifted traces, and candidate regions not
represented in the original evidence.

5. **How should representations learn from negative traces?**
Rejected candidates, failed runs, invalid configurations, and human rejections
define much of the usable design boundary, but they are easy to lose or flatten
into generic failure labels. A paper-quality agenda would build a negative-trace
representation task suite that preserves candidate context, failure reason,
fidelity level, coverage boundary, and decision owner, grounded in
@tbl-negative-traces and @sec-provenance-coverage-and-negative-traces. The
evaluation should measure avoided repeated failures, transfer to nearby design
spaces, preservation of local failure context, and resistance to overgeneralizing
one rejected candidate into a false universal rule.

### Chapter 5. Environments and Tool Contracts

The concepts in this chapter make tool interfaces into research objects. The
open questions here ask how architecture environments should expose legal
action, preserve tool evidence, reject invalid candidates, reuse failures across
flows, and remain valid after the tool world changes.

1. **What must an architecture environment contract expose before a loop can act?**
A generative loop cannot safely treat a simulator, compiler, runtime, EDA flow,
or telemetry path as a callable function until the environment names what the
loop may change, what it may observe, what feedback costs, and what can reject
the action. A strong research artifact would be a minimal environment-contract
schema with a conformance suite for architecture tools, grounded in the fields
of @tbl-environment-contract and the interface boundaries of
@tbl-architecture-interface-boundaries. The evidence standard should be
practical. A second optimizer or reviewer should be able to enter the same
harness, replay the same actions, recover the same invalid-action outcomes, and
distinguish comparable feedback from private wrapper behavior across environment
instances from @tbl-environment-instances.

2. **How can legacy tool traces become environment contracts?**
Many architecture tools already expose contract fragments, but they do so
through scripts, warnings, logs, timeouts, report tables, waived errors, and
version-specific behavior rather than through clean APIs. A plausible agenda is
a trace-to-contract system that mines legacy tool exhaust and proposes action
fields, read-only constraints, observation fields, invalid-action labels,
feedback costs, and rejection authorities for human review. The evaluation
should test the inferred contract on held-out tool runs, measuring whether it
predicts which actions are legal, which failures are recoverable, which warnings
should block escalation, and which report fields support the environment claim.
The strongest evidence would show that an expert can correct the inferred
contract faster than writing a wrapper from scratch, while still preserving the
semantics described in "Interfaces Are Action Boundaries" and "The Architecture
Environment Abstraction."

3. **How should environments define invalid actions and rejection paths?**
Invalid actions are not just failed runs. They are structured evidence about the
boundary between the architecture problem and the tool world, including
malformed configurations, unsupported ISA or memory-model states, compiler
failures, nonsynthesizable RTL, timeouts, stale workloads, and actions that
require human approval before stronger feedback is spent. A useful artifact
would be an invalid-action taxonomy and rejection-path API for architecture
environments, with machine-readable outcomes that separate schema illegality,
tool failure, physical infeasibility, proxy insufficiency, and
escalation-required states. The evidence standard should include generated
candidate streams that intentionally hit boundary cases, then measure
classification consistency, replayability, false-pass rates, false-reject rates,
and reviewer effort. A relevant target is the recipe in "Building Environments
for New Subfields" and the principle in @pri-tools-environments.

4. **How can negative evidence transfer across simulated and physical tool flows?**
A late physical rejection can sometimes teach an earlier simulator-backed
environment what not to spend samples on, but that lesson is dangerous if it
loses context. Routing congestion, timing failure, IR-drop pressure, or
design-rule violations are not universal laws. They are failures under
particular workloads, process assumptions, constraints, and tool versions. A
credible research artifact would be a portable failure receipt that links a
high-fidelity rejection back to the earlier action fields that caused it, while
preserving the fidelity level and context needed to avoid overgeneralization.
The evaluation should ask whether those receipts improve early rejection in
proxy or simulation environments without discarding valid candidates, using
held-out workloads, changed constraints, or different technology assumptions.
@tbl-eda-stage-contract and @tbl-feedback-latency-fidelity give the local
evidence ladder for that test.

5. **How do architecture environments stay valid as tools and workloads drift?**
An environment contract can be correct on the day it is built and misleading
after workload revisions, compiler changes, simulator updates, deprecated knobs,
new failure modes, or changed rejection thresholds. A strong systems artifact
would be an environment-validity monitor that treats these changes as contract
events, flags which action, observation, provenance, or rejection fields are
stale, and triggers the smallest recertification run needed before the loop acts
again. The evidence standard should use versioned environment histories with
known semantic changes and measure whether the monitor correctly preserves,
weakens, or invalidates the environment's supported claims. The scope is local
operating discipline for the harness, as developed in
@sec-archops-operating-discipline and @tbl-archops-operating-discipline, not the
Chapter 10 problem of community infrastructure.

### Chapter 6. Method Roles and Feedback Allocation

The discipline of assigning AI methods to specific loop roles exposes a method
agenda, not a leaderboard agenda. At this point in the book, the unsettled
questions concern how methods remain bounded, how scarce feedback is spent, and
how the loop adapts when uncertainty changes without turning method output into
architect-owned commitment.

1. **What role contracts keep AI methods from becoming decision makers?**
The method-role view in @fig-method-role-map, @tbl-method-role-discipline, and
@tbl-method-object-discipline asks each participant to act on a named object
through a named interface, but it does not yet provide a rigorous enforcement
mechanism. A strong research artifact would be a role-contract language plus a
runtime monitor that states what each generator, predictor, optimizer, critic,
repair method, verifier, explainer, or coordinator may read, write, propose,
reject, or escalate. The evidence standard should include multi-participant loop
traces that contain deliberate authority violations, such as a predictor
silently promoting a ranking into a design decision or a coordinator hiding
delegation. Evaluation should measure violation detection, false alarms, logging
cost, and whether the contract preserves the architect-owned boundary described
in @sec-choosing-a-method-under-constraints.

2. **How should loops spend scarce feedback across method roles?**
Sample efficiency in @sec-sample-efficiency-under-expensive-feedback treats
feedback as the scarce resource, but a real loop must decide whether the next
unit of feedback should generate more candidates, predict a cheaper estimate,
optimize the next sample, critique a weak claim, or repair a malformed artifact.
A plausible agenda is a role-aware feedback scheduler that treats method
invocation as an acquisition decision over roles, fidelities, and expected
decision value. The evaluation should compare static pipelines against adaptive
role-allocation policies on bounded design-space exploration tasks, using the
regimes in @tbl-sample-efficiency-regimes and the method constraints in
@tbl-method-selection-matrix. The evidence standard should report decision value
per scarce sample, high-fidelity runs avoided, rejected-space coverage,
invalid-action rate, and whether the final loop record explains why feedback was
spent where it was.

3. **How can optimizers learn from negative traces without losing fidelity labels?**
The chapter argues that failed simulations, invalid candidates, timeouts,
rejected configurations, and proxy mismatches are information about the boundary
of the design space, but those failures are dangerous training data if their
evidence strength is flattened. A strong contribution would define a
fidelity-labeled negative-trace schema and acquisition policies that can use
proxy failures, tool warnings, synthesis timeouts, expert rejections, and rare
high-fidelity failures without treating them as equivalent. The evaluation
should use a design-space search benchmark with known cheap and expensive
feedback levels, then compare policies that preserve fidelity labels against
policies that collapse all failures into one negative class. The evidence
standard should report sample efficiency, false pruning of valid regions,
repeated invalid-action avoidance, calibration of rejection strength, and the
conditions under which a cheap negative trace must still be escalated.

4. **What bounded rejection suites test hardware-aware generators?**
The hardware-awareness ladder in @fig-hardware-awareness-ladder and the tests in
@tbl-hardware-awareness-assessment and @tbl-hardware-awareness-tests make
hardware awareness observable, but generators still need bounded tests that can
falsify unsupported hardware claims before they receive broader loop roles. A
useful artifact would be a rejection suite for a named environment and artifact
class, such as kernels, simulator configurations, RTL fragments, constraints, or
design-loop cards. The suite should contain invalid candidates, near misses,
valid but weak candidates, and valid candidates that stress portability,
numerical tolerance, constraint handling, and provenance. Evaluation should
report false-pass and false-reject rates, replayability, coverage of the claimed
hardware-awareness level, and the strongest method role the suite supports
before stronger feedback is required. The result should remain a method-role
test, not a Chapter 7 trust authorization mechanism.

5. **How should loops reassign method roles as uncertainty changes?**
The decision matrix in @sec-choosing-a-method-under-constraints is mostly
static, but real loops change shape as evidence arrives. A generator may be
useful early, a predictor may dominate while calibrated uncertainty is narrow, a
critic may become central when workload coverage is missing, and repair may be
the right role after a tool rejects a malformed artifact. A plausible artifact
is a role-reassignment policy that routes loop state among generation,
prediction, optimization, critique, and repair based on uncertainty, failure
reason, feedback cost, and expected decision value. The evaluation should
compare adaptive role reassignment against fixed role orderings under the
evidence gap shown in @fig-evidence-gap. The evidence standard should report
whether reassignment improves decision value under a fixed budget, reduces
unnecessary generation or high-fidelity runs, preserves negative traces, and
obeys the role contracts rather than quietly expanding method authority.

### Chapter 7. Evidence and Trust

The mechanisms in this chapter make trust reviewable, but they leave several
research artifacts unfinished. The questions here ask how evidence can stay
bound to claims, how proxy wins can be challenged before commitment, and how
rejection authority can remain independent when the evidence path itself is
under pressure.

1. **How should multi-fidelity evidence ledgers bind claims to commitment levels?**
Fidelity ladders and evidence ledgers
(@sec-fidelity-ladders-and-evidence-ledgers) record what a loop has seen, while
commitment levels and reversibility (@sec-commitment-levels-and-reversibility)
determine how far a claim may travel. The open problem is preventing weak
evidence from authorizing a stronger claim than it supports. A plausible
artifact is a claim-bound ledger schema and checker that records feedback rung,
provenance, uncertainty, rejected alternatives, waivers, and the highest
supported commitment level for each candidate. The evidence standard should
include replay tests, tamper and omission tests, downgrade behavior when
evidence is missing, and false-authorization rates on mixed proxy, simulation,
synthesis, and human-review packets.

2. **What benchmarks expose proxy exploitation before commitment?**
Proxy mismatch and metric gaming
(@sec-proxy-mismatch-metric-gaming-and-calibration) become more dangerous when a
generator can search until it finds a candidate that wins the proxy and fails
the architecture objective. The research artifact should be a proxy-exploitation
benchmark suite with adversarial candidate families, calibrated support regions,
hidden higher-fidelity checks, and known failure modes such as power leakage,
timing pressure, workload drift, or unpriced interface cost. A credible
evaluation would report proxy false-pass rates, escalation precision and recall,
budget overhead, and how often the loop rejects or escalates a misleading winner
before it crosses the commitment boundary.

3. **How can rejection authorities be tested for independence?**
The verification authorities in @tbl-verification-authorities add trust only
when they can fail independently of the method that produced the candidate. A
serious research agenda would build a rejector-dependency model that records
shared model families, training data, objectives, tool paths, evidence sources,
task instructions, and human instructions, then turns that model into an independence test
for AI-assisted verification. The evidence standard should include injected
shared blind spots, correlated-tool failures, and cases where multiple apparent
reviewers agree for the same wrong reason. The result should predict when
consensus is merely repetition and when a rejection authority can actually block
an unsupported claim.

4. **How should loops stress-test compromised evidence sources?**
Evidence disputes (@sec-evidence-disputes-and-the-trust-checklist) assume that
provenance, baselines, logs, simulators, and private reports can be inspected,
but a loop also needs to survive cases where those sources are stale, poisoned,
tampered with, or selectively reported. A useful artifact would be an adversarial
evidence harness that injects compromised baselines, simulator drift, missing
negative traces, altered tool logs, deceptive summaries, and hidden security
failures into an otherwise normal architecture loop. The evaluation should
measure false commitment rate, time to detection, escalation cost, and whether
the loop downgrades the claim, demands independent evidence, or rejects the
candidate instead of treating corrupted evidence as support.

5. **How can confidential evidence remain auditable?**
The confidentiality boundary check and the confidentiality row of
@tbl-trust-checklist require private evidence to be reviewable without forcing
disclosure of proprietary RTL, workloads, tool logs, traces, or process
assumptions. The research artifact should be a confidential evidence capsule
that records data class, access rule, redaction boundary, local replay receipt,
claim scope, and the public proxy that would be insufficient. The evidence
standard should test whether an authorized reviewer can confirm fidelity,
provenance, missing-evidence risk, and rejection authority without seeing
protected material, while also measuring leakage risk and the rate at which
redaction hides evidence that should have forced escalation.

### Chapter 8. Executing One Loop

The lighthouse loop shows one bounded turn, not a general recipe. The research
questions here ask what artifacts would make that same discipline repeatable
when a broad intent must become a legal turn, a proxy win must face stronger
evidence, and a recorded rejection must remain useful without pretending to be
final forever.

1. **How can architectural intent become one rejectable loop turn?**
The chapter lowers a broad XR subsystem request into one XRBench-class slice,
three legal candidate organizations, and two declared gates in
@tbl-active-lighthouse-slice. A concrete research artifact would be an
intent-to-turn schema that converts architectural intent into workload scope,
legal actions, candidate records, excluded evidence, rejection gates, and a
commitment boundary. The evaluation should test whether independent architects
can reconstruct the same task boundary, detect invalid actions, and replay the
loop turn from the resulting card without granting the AI authority beyond the
slice shown in @fig-loop-beat.

2. **What signals should trigger escalation beyond a proxy?**
Round One uses a cheap proxy only to rank candidates, then Round Two escalates
all three because that proxy has no final rejection authority. A strong research
agenda would define escalation policies that read proxy uncertainty, model
coverage, sensitivity to data movement, interface assumptions, and constraint
proximity, then decide when scarce stronger evidence is required. The evidence
standard should compare those policies against static escalation, measuring
false commitments, false rejections, evidence cost, and whether the loop still
stops at the honest commitment level recorded in @tbl-worked-loop-ledger.

3. **How can proxy workloads expose data-movement mirages?**
The worked proxy mirage in @fig-proxy-mirage turns on a specific failure mode,
where arithmetic looks cheap until interface traffic is charged. A plausible
artifact would be a proxy-audit workload suite with paired kernels and traces
that separate compute, locality, interface traffic, DMA behavior, and
shared-memory effects for accelerator, vector, and SoC-block candidates. The
evaluation should show that the suite predicts ranking reversals before scarce
simulation is spent, bounds the proxy claims that remain valid, and catches the
kind of data-movement failure explained in Round Three.

4. **What receipt metadata makes rejected candidates reusable?**
The loop receipt in @tbl-loop-replay-receipt preserves more than the winner. It
records inputs, task framing, candidate IDs, proxy and simulation runs, evidence,
failures, and decisions. A concrete research artifact would be a negative-trace
receipt schema for rejected architecture candidates, including workload slice,
coverage labels, tool versions, constants, fidelity level, rejection gate,
failure mechanism, sensitivity notes, and next evidence required. The evaluation
should ask whether the metadata prevents duplicate rediscovery, lets another
architect reconstruct the rejection in @tbl-worked-loop-card, and distinguishes
a real dead end from a candidate that was rejected only under one bounded
assumption set.

5. **When should a recorded rejection be reopened?**
A negative trace is useful because it prevents the loop from repeating a known
failure, but it becomes harmful if it permanently excludes a candidate whose
workload, software stack, process node, interface, or evidence tool has changed.
A strong paper would define a reopening policy for recorded rejections, perhaps
as a validity model over the receipt fields that expired or changed since the
original loop turn. The evidence standard should show that reopened candidates
clear a changed assumption test before reentering search, that the original
failure mode is explicitly rechecked, and that the loop does not convert stale
rejection records into either permanent bans or automatic revivals.

### Chapter 9. Cross-Stack Loop Patterns

The loop patterns outlined in this chapter define operating regimes across the
stack. The questions here ask what can move safely between regimes, what must be
recalibrated, and when a local result stops being architecture evidence.

1. **What transfers safely across loop patterns?**
A loop card is useful only if some of its fields can travel from one regime to
another without smuggling in false assumptions. Workload packets, baseline
assumptions, objective vectors, rejection gates, and negative traces may
transfer from a fast software loop into DSE, co-design, deployment, or
high-commitment RTL work, but their authority changes with feedback cost and
rollback risk (@tbl-loop-patterns; @tbl-loop-pattern-decision). A strong
research artifact would be a cross-pattern transfer contract that states which
fields are portable, which fields must be weakened, and which fields require
fresh evidence before reuse. The evaluation should replay multi-stage design
studies and measure whether the contract catches invalid transfers, stale
baselines, and objective drift better than ad hoc handoff notes.

2. **What error bounds make cheap cross-layer rejectors usable?**
The rejection-bound view in @sec-the-rejection-bound depends on cheap,
independent rejection, yet a rejector that passes the wrong candidate only moves
risk to a later and more expensive stage. The open problem is to calibrate
cross-layer rejectors such as interface-cost models, compiler legality checks,
power screens, replay harnesses, or deployment guards against the stronger
evidence they claim to approximate. A plausible artifact is a
rejector-calibration suite that reports false-pass and false-reject rates by
commitment level, layer boundary, and workload slice. The evidence standard
should compare cheap dispositions against higher-fidelity tools or deployed
measurements, then state the maximum claim each rejector is allowed to clear
before escalation is required.

3. **When should loops change method posture across feedback regimes?**
This chapter separates surrogate prediction, constrained optimization, and
generator-critic repair, but real loops may move among those postures as proxy
mismatch, feedback latency, and rollback cost change. The research challenge is
to make posture changes explicit loop actions rather than informal engineering
judgment. A useful agenda would build a posture controller that shifts a method
from exploration to critique, from proxy screening to simulation, or from
generation to repair when measured evidence quality falls below a declared
threshold. The evaluation should test whether the controller improves loop cost,
rejection quality, and final candidate quality across the spectrum in
@fig-loop-pattern-spectrum while respecting the autonomy rule in
@pri-change-autonomy.

4. **How can loops detect single-layer wins that fail system objectives?**
Many of the chapter's failure modes occur when one layer improves its local
metric while the system objective gets worse. A kernel speedup can lose to
interface cost, an accelerator win can disappear in the compiler path, and a
compute optimization can raise memory traffic, power, or tail latency. A
concrete research artifact would be a system-objective rejection suite for
co-design loops, seeded with candidates that look strong in one layer and fail
after data movement, software reachability, network contention, or power
constraints are measured. The evidence standard should require end-to-end
objective vectors and negative traces, with examples grounded in the
LogCA-style interface cliff (@fig-logca-breakeven), the code-generation waist
(@fig-codegen-narrow-waist), and hardware/software co-evolution
(@fig-hardware-software-coevolution).

5. **How should loops track evidence half-life across co-evolving stacks?**
Evidence half-life is the period over which an architecture claim remains
defensible as workloads, compilers, runtimes, hardware targets, tool versions,
and deployment conditions change. The chapter has examples of drift in workload
packets, co-evolving hardware/software paths, and fleet-facing evidence, but the
field lacks a mechanism for weakening claims as their dependencies move
(@tbl-workload-characterization-20; @fig-hardware-software-coevolution). A
strong artifact would be an evidence-validity ledger that attaches dependency
edges, version ranges, refresh triggers, and invalidation rules to each claim.
The evaluation should replay historical stack changes and ask whether the ledger
flags stale evidence before an optimizer composes it into a new cross-layer
claim.

### Chapter 10. Ownership and Community Infrastructure

Building shared infrastructure and navigating the transition to AI-assisted
architecture leaves several unsettled research directions. At the end of the
book, the questions return to ownership. The technical challenge is to make
redacted evidence, shared failures, tacit knowledge, human stop authority, and
maintained standards durable enough for community-scale practice.

1. **How can redacted loop ledgers be audited without exposing proprietary design state?**
The problem is not to make private architecture work fully reproducible in
public. It is to make the public record strong enough that reviewers can audit
what the loop claimed, what it observed, what it rejected, and who accepted the
commitment. A plausible research artifact is a redacted loop-ledger format with
an accompanying audit protocol for projected proxies, ownership records,
evidence stages, and redaction boundaries, extending the pattern in
@lst-redacted-trace and @tbl-public-evidence-ledger. The evidence standard
should be whether an independent reviewer can detect missing workload scope,
missing action-observation context, unsupported escalation, or hidden decision
ownership without seeing the proprietary design state itself.

2. **How can negative traces become shared, reviewable infrastructure?**
Architecture practice loses field knowledge when failed candidates, invalid
configurations, stale benchmarks, misleading proxy wins, and rejected fixes
disappear into private notebooks or tool logs. A plausible agenda is a
negative-trace corpus and reuse protocol that treats rejected alternatives as
evidence-bearing records rather than opaque training data, aligned with the
negative-trace row in @tbl-long-horizon-challenges and the public evidence
fields in @tbl-public-evidence-ledger. The evaluation should ask whether new
loops can use those records to avoid known failure modes, reopen old rejections
only when new evidence justifies it, and preserve the original rejection
authority, fidelity level, and redaction boundary.

3. **How can tacit architectural knowledge become explicit loop state without erasing human ownership?**
Many of the constraints that keep architecture work honest live in expert
judgment before they live in schemas, including packaging limits, compiler
assumptions, integration risks, workload exclusions, and product-specific
failure experience. A plausible research artifact is a tacit-constraint capture
workflow that turns expert knowledge into reviewable environment contracts,
hidden-state lists, evidence gates, and rejection rules, building on
@fig-tacit-extraction-bridge and @tbl-architect-owned-artifacts. The evidence
standard should be whether an automated loop that receives this state makes
fewer invalid actions, whether reviewers can trace each codified constraint to a
named human source or decision owner, and whether the representation preserves
room for human override when the context changes.

4. **How can human stop authority survive long-horizon, multi-agent design loops?**
As architecture loops become asynchronous, distributed across tools, and
maintained across personnel changes, the ability to halt a claim can decay even
when the record looks complete. A plausible research artifact is a commitment
ledger that records ownership transfer, expiration conditions, revalidation
triggers, waiver history, and human stop authority for multi-agent loops,
connecting the Ownership Test, @fig-architect-owned-boundary, and
@pri-human-accountable. The evaluation should ask whether a later reviewer can
identify who currently owns a stale claim, which evidence still supports it,
which event should force re-approval, and which person or review body can stop
the loop before a higher commitment is made.

5. **What standards, incentives, and maintenance obligations make Architecture 2.0 infrastructure durable?**
Loop cards, evidence ledgers, environment contracts, and negative-trace corpora
will not become field infrastructure unless the community rewards maintenance,
retirement, and reuse as much as first publication. A plausible agenda is an
artifact-evaluation standard for Architecture 2.0 infrastructure that defines
acceptance criteria, versioning expectations, stale-record retirement, owner
transfer, and minimum evidence packets, extending @tbl-role-agenda,
@tbl-minimum-credible-loop-packet, and @tbl-architecture-20-design-principles.
The evidence standard should be whether a maintained artifact continues to
support independent review after tool versions, workloads, models, and owners
change, and whether venues or artifact committees can distinguish durable
infrastructure from a one-time demonstration.

### Setup Notes For Expanded Draft

These are not chapter edits. They are the places where the expanded drafts would
benefit from small setup additions before they are copied into the chapter
source files.

- Chapter 1 would benefit from one bridge from negative evidence as useful loop
  state to negative evidence as scholarly credit, plus one sentence connecting
  Architecture 2.0 to CFPs or artifact review.
- Chapter 2 should name the strained-loop measurement bundle before the open
  questions and briefly list AI entry points without turning them into Chapter 6
  method roles.
- Chapter 3 should define workload characterization as distribution, benchmark
  construction, holdout evaluation, provenance, and overfit defense. It should
  also separate static claim-card checks from executable-environment checks.
- Chapter 4 should define calibrated support, coverage boundary, and the axes of
  workload-space, design-space, and fidelity-space coverage.
- Chapter 5 should add one concrete example of a physical-flow failure becoming
  an earlier proxy constraint, and one example of logs becoming contract fields.
- Chapter 6 should introduce "fidelity-labeled negative trace" and include one
  example where a loop shifts from generation to prediction, critique, or repair
  as uncertainty changes.
- Chapter 7 should distinguish ordinary proxy mismatch from compromised
  evidence and name shared model family, objective, tool path, training data, and
  evidence source as independence risks.
- Chapter 8 should frame the proxy mirage as a research generalization and name
  the receipt fields that control whether a recorded rejection can be reopened.
- Chapter 9 should add one setup sentence for evidence half-life, one concrete
  failure example for bad cross-pattern transfer, and a mention of objective
  vectors in the co-design discussion.
- Chapter 10 should sharpen incentives for maintaining shared loop
  infrastructure after publication, including owner transfer, expiration, and
  stale-record retirement.

## Chapter-Grounded Greenlight Pass

Chapter reviewers read the full chapter files, the preface arc, and the U-shape
candidate. No reviewer returned a red verdict. The consensus was
green on the whole-book structure and yellow on final wording because several
questions exposed small setup gaps in the chapters. This pass therefore treats
the U shape as accepted and regenerates the questions from chapter content, with
grounding notes for later integration.

### Current Grounded Candidate

#### Chapter 1. Field Wave and Review Norms

1. **What makes AI-assisted architecture work an architecture contribution?**
   Grounding. "Ask What AI Can Do for Architecture," "From Architecture 1.0 to
   Architecture 2.0," and "Boundaries of the Argument."
2. **How should venues review AI-assisted design-loop claims?**
   Grounding. "The Architecture Moonshot," the AlphaChip comparison, "Ask What
   AI Can Do for Architecture," and the preface's venue guidance.
3. **When do rejected alternatives count as architecture evidence?**
   Grounding. "From Architecture 1.0 to Architecture 2.0," "Why the Prompt
   Spans the Stack," and "Efficiency Claims Need Rejectable Loops."
4. **What shared artifacts make loop-level progress comparable?**
   Grounding. "The Architecture Moonshot," the lighthouse prompt decomposition,
   the AlphaChip comparison problem, and the MLPerf discussion.
5. **What should a field-shaping architecture moonshot leave behind?**
   Grounding. "The Architecture Moonshot," especially the Apollo, Human Genome
   Project, DARPA Grand Challenge, AlphaFold, Mead-Conway, RISC, and AlphaChip
   framing.

#### Chapter 2. Pressure Diagnosis and AI Entry Points

1. **What measurements reveal a strained architecture loop?**
   Grounding. The scissors-gap framing, "Classical Loops Already Use Feedback,"
   "Engineering Cost Creates the Scissors Gap," and "Feedback and Verification
   Become the Bottleneck."
2. **Where should AI enter a specialization and chiplet loop?**
   Grounding. "Architecture Levers Add State," "Specialization and Chiplets
   Expand Search," "Specialized Hardware Needs a Software Loop," and "AI Helps
   Only When the Loop Is Designed."
3. **Which physical signals should triage expensive validation?**
   Grounding. "Physical Constraints Move Into Architecture," the waterbed and
   data-movement examples, and "Engineering Cost Creates the Scissors Gap."
4. **When does workload drift expire architecture evidence?**
   Grounding. "Software Changes Faster Than Silicon," the workload-packet
   discussion, and the benchmark-governance material.
5. **When do multiobjective tradeoffs overwhelm manual evaluation?**
   Grounding. "Architecture Levers Add State," "Specialization and Chiplets
   Expand Search," "Engineering Cost Creates the Scissors Gap," and
   "Architecture Violates Generic AI Assumptions."

#### Chapter 3. Ontology and Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable?**
   Grounding. "The Architectural Claim Is the Unit of Review," "The Compact
   Framework," and "The Design-Loop Card."
2. **What workload and baseline characterization makes a claim credible?**
   Grounding. "The Architectural Claim Is the Unit of Review," "The Design Loop
   Is the Unit of Analysis," "Intent Defines the Task," and "Feedback Becomes
   Evidence."
3. **How can benchmark construction and holdout evaluation limit loop overfit?**
   Grounding. "Representations and World Models," "Tools Become Environments,"
   "Feedback Becomes Evidence," and "The Design-Loop Card."
4. **How can rejected alternatives become auditable design-space evidence?**
   Grounding. "Design Spaces Make Claims Meaningful," "The Compact Framework,"
   "Feedback Becomes Evidence," and "The Design-Loop Card."
5. **What parts of a design-loop card can be checked before execution?**
   Grounding. "The Design Loop Is the Unit of Analysis," "The Compact
   Framework," "Autonomy Is Earned, Not Declared," and "The Design-Loop Card."

#### Chapter 4. Representations and World Models

1. **What semantics make architecture proposals replayable and rejectable?**
   Grounding. "Architecture Descriptions as Boundary Objects," "Unstructured
   Design Data and Its Cost," and "When a Representation Becomes Actionable."
2. **What should costly architecture samples record?**
   Grounding. "Sample Cost Is Architecture Data," "QuArch as a Stress Test,"
   and "Provenance, Coverage, and Negative Traces."
3. **When has an architecture world model left calibrated support?**
   Grounding. "Toward Architecture World Models" and "Sample Cost Is
   Architecture Data."
4. **What coverage record bounds architectural generalization?**
   Grounding. "Sample Cost Is Architecture Data," "Toward Architecture World
   Models," and "Provenance, Coverage, and Negative Traces."
5. **How should representations learn from negative traces?**
   Grounding. "Provenance, Coverage, and Negative Traces" and "When a
   Representation Becomes Actionable."

#### Chapter 5. Environments and Tool Contracts

1. **What must an architecture environment contract expose before a loop can act?**
   Grounding. "The Architecture Environment Abstraction" and
   `@tbl-environment-contract`.
2. **How can legacy tool traces become environment contracts?**
   Grounding. "Interfaces Are Action Boundaries," the EDA handoff discussion,
   "The Architecture Environment Abstraction," and "ArchGym as a Worked
   Example."
3. **How should environments define invalid actions and rejection paths?**
   Grounding. "Interfaces Are Action Boundaries," `@tbl-environment-contract`,
   and "Building Environments for New Subfields."
4. **How can negative evidence transfer across simulated and physical tool flows?**
   Grounding. "Feedback Latency and Fidelity," "Proxy Gaming and the Simulator
   Case," `@tbl-eda-stage-contract`, and "Building Environments for New
   Subfields."
5. **How do architecture environments stay valid as tools and workloads drift?**
   Grounding. "Environment Validity and Operating Discipline" and
   `@tbl-archops-operating-discipline`.

#### Chapter 6. Method Roles and Feedback Allocation

1. **What role contracts keep AI methods from becoming decision makers?**
   Grounding. "Match the Method to the Architecture Task," the method-role
   tables, "Choosing a Method Under Constraints," and the multi-participant
   role-contract discussion.
2. **How should loops spend scarce feedback across method roles?**
   Grounding. "Sample Efficiency Under Expensive Feedback," "Choosing a Method
   Under Constraints," and the lighthouse method-selection callout.
3. **How can optimizers learn from negative traces without losing fidelity labels?**
   Grounding. "Sample Efficiency Under Expensive Feedback," the negative-trace
   discussion, the fidelity ladder, and the sample-value heuristic.
4. **What bounded rejection suites test hardware-aware generators?**
   Grounding. "Hardware Awareness as Staged Capability," the hardware-awareness
   assessment and reviewer-test tables, and the generation section on proposing
   candidates and artifacts.
5. **How should loops reassign method roles as uncertainty changes?**
   Grounding. "Sample Efficiency Under Expensive Feedback," "Critique, Repair,
   and Explanation," "Choosing a Method Under Constraints," and the coordination
   role material.

#### Chapter 7. Evidence and Trust

1. **How should multi-fidelity evidence ledgers bind claims to commitment levels?**
   Grounding. "Feedback Budget Ledger and Feedback Economics," "Fidelity
   Ladders and Evidence Ledgers," and "Commitment Levels and Reversibility."
2. **What benchmarks expose proxy exploitation before commitment?**
   Grounding. "Proxy Mismatch, Metric Gaming, and Calibration," the AlphaChip
   proxy dispute callout, "Rejection Authority," and "Evidence Disputes and the
   Trust Checklist."
3. **How can rejection authorities be tested for independence?**
   Grounding. The verification-authorities table, "Rejection Authority," the
   AI-assisted verification discussion, and the trust checklist.
4. **How should loops stress-test compromised evidence sources?**
   Grounding. "Evidence Disputes and the Trust Checklist," "Proxy Mismatch,
   Metric Gaming, and Calibration," "Security, IP, and Confidentiality
   Boundaries," and "Rejection Authority."
5. **How can confidential evidence remain auditable?**
   Grounding. "Security, IP, and Confidentiality Boundaries," the trust
   checklist confidentiality row, and the evidence-dispute material on private
   evidence.

#### Chapter 8. Executing One Loop

1. **How can architectural intent become one rejectable loop turn?**
   Grounding. The opening crux, the active lighthouse slice table, and Round
   One's bounded candidate schema.
2. **What signals should trigger escalation beyond a proxy?**
   Grounding. Round One's escalation gate, Round Two's simulation-stage
   estimate, and the worked-loop ledger.
3. **How can proxy workloads expose data-movement mirages?**
   Grounding. Round Two, the proxy-mirage figure, and Round Three's
   interface-cost explanation.
4. **What receipt metadata makes rejected candidates reusable?**
   Grounding. Round Four, the worked-loop card, the replay receipt table, and
   the evidence packet paragraph.
5. **When should a recorded rejection be reopened?**
   Grounding. The worked-loop card, the replay receipt table, and the
   carry-forward discussion around rejected candidates.

#### Chapter 9. Cross-Stack Loop Patterns

1. **What transfers safely across loop patterns?**
   Grounding. "A Template for Reading the Cases," "Workload Characterization and
   Benchmark Construction," and "What Transfers Across Loops."
2. **What error bounds make cheap cross-layer rejectors usable?**
   Grounding. "The Loop Is Rejection-Bound," "Architecture Loops," "Co-Design
   Loops," and "High-Commitment Loops."
3. **When should loops change method posture across feedback regimes?**
   Grounding. "AI-Assisted Loop Postures," "Fast Software Loops,"
   "High-Commitment Loops," and "What Transfers Across Loops."
4. **How can loops detect single-layer wins that fail system objectives?**
   Grounding. "Domain-Specific Architecture and Code Generation" and
   "Co-Design Loops."
5. **How should loops track evidence half-life across co-evolving stacks?**
   Grounding. "Workload Characterization and Benchmark Construction,"
   "Co-Design Loops," "Deployment-Facing Loops," and "What Transfers Across
   Loops."

#### Chapter 10. Ownership and Community Infrastructure

1. **How can redacted loop ledgers be audited?**
   Grounding. "Community Infrastructure for Architecture 2.0," the redacted
   negative-trace example, the public evidence ledger table, "From Capability to
   Standard," and "Loop Invariants as Review Checks."
2. **How can negative traces become shared infrastructure?**
   Grounding. "Community Infrastructure for Architecture 2.0," "Long-Horizon
   Challenge Tasks," the negative-trace corpus row, and the final carry-forward.
3. **How can tacit knowledge become loop state?**
   Grounding. "Extracting and Codifying Tacit Knowledge," "Nondelegable
   Architectural Responsibilities," "The Architect Owns the Loop," and the
   strongest-objections discussion.
4. **How can human stop authority survive multi-agent loops?**
   Grounding. "Nondelegable Architectural Responsibilities," the Multi-Agent
   Authority Gate, the Ownership Test, "Beyond the Current Loop," and "The
   Architect's Standing Obligation."
5. **What makes Architecture 2.0 infrastructure durable?**
   Grounding. "Community Infrastructure for Architecture 2.0," "From Capability
   to Standard," "Long-Horizon Challenge Tasks," "Loop Invariants as Review
   Checks," and the final carry-forward.

### Setup Notes After Full-Chapter Review

These are not chapter edits. They are the places where the grounded questions
show that the chapter prose may need clearer support before final integration.

- Chapter 1 needs a short bridge from negative evidence as useful loop state to
  negative evidence as scholarly credit. A compact venue or CFP example would
  also support the review-norm question.
- Chapter 2 needs a clearer measurement bundle for strained loops. Candidate
  count, feedback cost, verification staffing, design cost, and drift all appear,
  but they are not yet named as a diagnostic bundle.
- Chapter 3 should make workload characterization explicit as distribution,
  benchmark construction, holdout evaluation, provenance, and overfit defense.
  It should also distinguish claim-packet checks from executable-environment
  checks.
- Chapter 4 should define calibrated support and coverage boundaries more
  explicitly. The latest questions avoid "novelty" because that term is not yet
  set up in the chapter.
- Chapter 5 should explain what makes a negative trace portable rather than
  local to one flow. One concrete example of logs becoming contract fields would
  help.
- Chapter 6 should separate feedback spending from runtime role reassignment.
  One short example of a loop shifting from generation to prediction, critique,
  or repair would support the last question.
- Chapter 7 should distinguish ordinary proxy mismatch from a compromised
  evidence source. The independence test could name shared model family,
  objective, tool path, training data, or evidence source.
- Chapter 8 should make proxy workloads a research generalization of the worked
  proxy mirage. It should also name the receipt fields that determine when a
  recorded rejection can be reopened.
- Chapter 9 should make cross-pattern transfer more operational. A transfer rule
  or failure example would support the workload, baseline, and objective-vector
  question. Evidence half-life also needs one explicit setup sentence.
- Chapter 10 should frame redacted ledgers as auditable rather than fully
  verified. The infrastructure question needs clearer incentives, maintenance
  obligations, owner transfer, expiration, and stale-record retirement.

## U-Shape Iteration Pass

This pass treats the questions as a whole-book research agenda. The bar is that
each question should fit its chapter, preserve progressive disclosure, and be
concrete enough to seed a serious paper or artifact in a top architecture,
systems, EDA, or ML systems venue. The sequence should read as a U shape.
Chapter 1 starts high at the field and review level, Chapters 2-9 descend into
the technical machinery, and Chapter 10 returns to ownership and community
infrastructure.

The venue bar is intentionally broad. It includes ISCA, MICRO, HPCA, ASPLOS,
MLSys, NeurIPS, ICML, ICLR, OSDI, SOSP, NSDI, PLDI, CGO, DAC, ICCAD, and
comparable venues when the contribution fits their scope.

### Current Landing Candidate

#### Chapter 1. Field Wave and Review Norms

1. **What separates an architecture contribution from an AI-assistance contribution?**
2. **How should architecture, systems, and ML systems venues evolve their calls, review criteria, and artifacts for AI-assisted design-loop work?**
3. **When do rejected alternatives and negative evidence become creditable architecture contributions?**
4. **What shared tasks, baselines, and artifact-review norms make loop-level architecture progress comparable?**

#### Chapter 2. Pressure Diagnosis and AI Entry Points

1. **What measurements reveal when a classical architecture loop is strained enough to justify AI assistance?**
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
3. **Which physical, power, and data-movement pressures should force evidence triage before expensive validation?**
4. **When does software and workload drift make architecture evidence expire faster than manual maintenance can track?**
5. **At what scale do multiobjective tradeoffs overwhelm the classical human-driven evaluation loop?**

#### Chapter 3. Ontology and Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**
2. **What must a reviewable architecture claim expose about workload distributions, hold-out evaluations, baselines, and benchmark assumptions?**
3. **How can design-space exclusions and rejected alternatives become auditable architecture evidence?**
4. **Which parts of a design-loop card can be checked before the loop is executable?**

#### Chapter 4. Representations and World Models

1. **What operational semantics make architecture proposals replayable and rejectable?**
2. **Where is an architecture world model calibrated, and when does a candidate leave support?**
3. **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**
4. **How can architecture representations support novelty while preserving negative evidence?**

#### Chapter 5. Environments and Tool Contracts

1. **What must an architecture environment contract expose before a generative loop can act?**
2. **How can legacy tool traces reveal environment contracts?**
3. **How should environments bound model actions, invalid states, and irreversible tool effects?**
4. **How can environments transfer negative evidence across physical and simulated tool flows?**
5. **How can architecture environments remain valid as workloads, tools, software stacks, and failure records drift?**

#### Chapter 6. Method Roles and Feedback Allocation

1. **What role contracts keep AI methods from silently becoming decision makers?**
2. **How should loops allocate scarce feedback across generation, prediction, critique, and optimization?**
3. **How can optimizers learn from heterogeneous negative traces while preserving fidelity labels?**
4. **What bounded rejection suites can test hardware-aware generative models before they receive broader loop roles?**
5. **How should loops reallocate generation, prediction, critique, and repair roles as feedback costs and uncertainty change?**

#### Chapter 7. Evidence and Trust

1. **How can multi-fidelity evidence ledgers bind architectural claims to their authorized commitment level?**
2. **What evaluation artifacts expose adversarial proxy exploitation before an architectural commitment is made?**
3. **How can rejection authorities be tested for independence from the methods that generated the candidates?**
4. **How can rejection authority remain effective when simulators or evidence sources are compromised?**

#### Chapter 8. Executing One Loop

1. **How can high-level architectural intent be lowered into a legal, rejectable, replayable loop turn?**
2. **What signals should govern escalation from proxy feedback to stronger evidence?**
3. **How can proxy workloads expose interface-cost and data-movement mirages before scarce simulation is spent?**
4. **What receipt metadata makes rejected candidates reusable when future evidence changes?**

#### Chapter 9. Cross-Stack Loop Patterns

1. **How can workload assumptions, baseline assumptions, and objective vectors transfer safely across loop patterns?**
2. **What error bounds make cheap cross-layer rejectors safe before stronger evidence is required?**
3. **How should method posture change across loop patterns as feedback gets more expensive and commitments become harder to reverse?**
4. **How can co-design loops expose single-layer AI wins that violate cross-layer system objectives?**
5. **How should loops track the half-life of architectural evidence across a co-evolving hardware-software stack?**

#### Chapter 10. Ownership and Community Infrastructure

1. **How can redacted loop ledgers verify design claims without exposing proprietary design state?**
2. **How can the community turn rejected alternatives and negative traces into shared, reviewable infrastructure?**
3. **How can tacit architectural knowledge become explicit loop state without erasing human ownership?**
4. **How do we preserve human stop authority and accountability in long-horizon, multi-agent design loops?**
5. **What artifact-evaluation standards, incentives, and maintenance obligations make Architecture 2.0 infrastructure durable?**

### U-Shape Assessment

The current set lands the intended shape. Chapter 1 is a field-level agenda
about contribution boundaries, review, negative evidence, and comparability.
Chapter 2 turns that agenda into a diagnostic for when AI assistance is
justified. Chapters 3-8 descend through the loop machinery by moving from
claims to representations, environments, method roles, evidence, and one
executed turn.
Chapter 9 widens back out across stack patterns while staying technical.
Chapter 10 returns high and asks what the architect and the community must own.

### Chapter-Support Notes For Later

These are not chapter edits now. They are places where the questions reveal
material that may need clearer setup before final integration.

- Chapter 1 may need a short history or CFP-style example if we ask venues to
  evolve calls and review criteria.
- Chapter 2 should clearly distinguish when AI assistance is justified from
  where in the stack it should interact.
- Chapter 3 should make clear what can be checked before execution and what
  remains judgment if we keep the design-loop-card question.
- Chapter 3 should connect the ontology to familiar workload characterization
  practice so the claim fields do not read as bureaucratic overhead.
- Chapter 4 may need a sharper account of support, coverage, and calibration if
  we keep asking when a candidate leaves the world model's support.
- Chapter 5 may need a clearer bridge from environment contracts to transfer
  across mismatched tool flows if we keep the negative-evidence-transfer
  question.
- Chapter 6 should keep bounded rejection suites method-role focused so they do
  not collapse into Chapter 7 trust machinery.
- Chapter 7 should make independence of rejection authority more visible before
  asking how it survives compromised simulators or evidence sources.
- Chapter 8 should introduce the proxy-audit benchmark as the research
  generalization of the proxy mirage, not as something the toy loop already
  solves.
- Chapter 9 should better prepare cross-pattern transfer and evidence half-life
  if those become the chapter's highest-level research agenda.
- Chapter 10 should make infrastructure incentives and maintenance obligations
  explicit if we keep the final standards question.

## Synthesis After User Feedback and Iterative Editorial Review

This synthesis layer reflects the follow-up discussion and iterative editorial
review. The review used three explicit lenses, a senior architecture-field
historian, a textbook editor, and a modern architecture/MLSys program-chair
perspective. It does not replace the candidate lists below. It records the
current best direction before any chapter-source rewrite.

### High-Low-High Arc

- **Chapter 1:** Stay high and field-shaping. The questions should help the
  community distinguish architecture contributions from AI-tooling demos,
  evolve reviewer and venue norms, credit rejected alternatives, and create
  comparable loop-level tasks.
- **Chapter 2:** Move from field agenda to pressure diagnosis. The questions
  should teach when and where AI becomes necessary because generation outruns
  trusted feedback, specialization exceeds verification capacity, physical
  constraints force escalation, drift makes evidence brittle, and multiobjective
  tradeoffs exceed classical feedback budgets.
- **Chapters 3-9:** Descend into the technical machinery: claim ontology,
  representations, environments, method roles, evidence/trust, one worked loop,
  and cross-stack transfer.
- **Chapter 10:** Return high. The questions should ask what the architect and
  the community own: redacted audit, shared evidence, tacit knowledge,
  publication incentives, and human stop authority.

### Current Chapter 1 Synthesis Titles

1. **What separates an architecture contribution from an AI-assistance contribution?**
   This is the central review problem: communities need to know whether a paper
   advances computer architecture, AI tooling, or the architecture loop that
   makes AI assistance architecturally meaningful.
2. **How should architecture venues and reviewer norms evolve for AI-assisted design loops?**
   This explicitly includes CFPs and review criteria, but frames them as field
   evolution rather than committee politics. Architecture conferences have
   expanded before, for example around compilers, hardware/software interfaces,
   systems, and accelerator interfaces, and this question asks whether
   AI-assisted design should be shepherded deliberately rather than absorbed ad
   hoc.
3. **When do rejected alternatives become creditable architecture evidence and useful negative data?**
   Rejected alternatives matter as review evidence, as architecture knowledge,
   and as future negative data for training, evaluating, and calibrating
   Architecture 2.0 models.
4. **What shared tasks, baselines, publication norms, and incentives make loop-level architecture progress comparable?**
   The point is to reward reusable loop evidence, maintained baselines, negative
   results, and shared infrastructure, not only isolated generated artifacts.

### Current Chapter 2 Synthesis Titles

1. **When does the classical loop need AI assistance because generation outruns trusted feedback?**
   This keeps the scissors gap central and asks students to identify the point
   where more candidates stop helping unless the loop also gains trusted
   evaluation, rejection, or triage capacity.
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
   This frames specialization and chiplets as a placement problem for AI
   assistance: workload, compiler, runtime, microarchitecture, integration,
   physical design, and validation do not all need the same kind of interaction.
3. **Which physical, power, and data-movement pressures signal that AI should help triage evidence?**
   The goal is not merely pruning. It is to recognize when physical pressure
   forces the loop to change evidence level, tool fidelity, or human review
   before expensive validation is spent.
4. **When does software and workload drift make architecture evidence too brittle to maintain manually?**
   This keeps the validity-horizon idea but asks when AI assistance becomes
   necessary to track, weaken, refresh, or withdraw claims as workloads and
   software stacks move.
5. **Where should AI assist when multiobjective tradeoffs exceed the loop's feedback budget?**
   This asks where AI belongs when performance, energy, power, carbon, cost,
   verification burden, simulator hours, EDA licenses, and human review cannot
   all be explored by a classical loop.

### Editorial Roundtable Takeaways

- The historian lens argued that AI-assisted design should be framed as the next
  wave in architecture's quantitative methodology, not as an outsider tool to
  fence off. The useful analogy is not "AI demos enter architecture," but
  "architecture absorbs a new method when that method becomes central to
  architectural evidence."
- The textbook-editor lens warned that Chapter 1 cannot become only a
  program-committee memo. The reader first needs the paradigm shift: from
  reviewing only an artifact to reviewing the loop, its evidence, its rejected
  alternatives, and its commitment boundary.
- The PC-chair lens insisted that the contribution boundary is practical, not
  philosophical. Reviewers need to know what evidence distinguishes an
  architecture contribution from an AI-tooling contribution, and what reporting
  norms make negative results and loop artifacts reviewable.
- The consensus is that Chapter 2 should teach "when and where," not just
  "how to prune." The deeper mechanics of method roles, proxy trust, evidence
  ledgers, and rejection authority should descend into Chapters 6-8.

### CFP and Venue-Evolution Notes

These are prompts for a possible Chapter 1 paragraph or footnote, not finished
claims. They support the idea that conference scope evolves through CFPs,
review norms, artifact expectations, and topic lists.

- MICRO CFP language has explicitly included microarchitecture, compilers,
  hardware/software interfaces, and systems, showing that compiler and
  HW/SW-interface work can become central to a microarchitecture venue.
  Sources to mine: [MICRO 2020 CFP](https://microarch.org/micro53/submit/papers.php),
  [MICRO 2026 CFP](https://www.microarch.org/micro59/submit/papers.php).
- ISCA CFP topic lists include architectural support for programming languages
  or software development and architectural support for accelerator interfaces,
  which is useful precedent for architecture venues absorbing adjacent
  methodology when it becomes architecturally consequential.
  Source to mine: [ISCA 2023 CFP](https://www.iscaconf.org/isca2023/submit/papers.php).
- ASPLOS is structurally cross-disciplinary across architecture, programming
  languages, and operating systems, which offers a different model: build the
  intersection into the venue identity rather than treating it as scope drift.
  Source to mine: [ASPLOS 2027 CFP](https://www.asplos-conference.org/asplos2027/cfp/).
- HPCA topic lists already include chiplets/3D/interposers, sustainability,
  security/privacy, and evaluation/measurement, suggesting that architecture
  venues regularly update scope as the bottlenecks and evidence standards move.
  Source to mine: [HPCA 2025 CFP](https://hpca-conf.org/2025/call-for-papers/).

## All-Chapter Roundtable Synthesis

This section applies the same simulated roundtable method to every chapter. It
records the title-level structure before the later sequential chapter read. The
architecture-history, textbook-editor, and PC-chair lenses debated each chapter
range and a final whole-book convergence pass checked the sequence. The newer
**Sequential Chapter Fit Audit** below supersedes this section as the current
working recommendation.

### Chapter 1: Field Wave and Review Norms

1. **What separates an architecture contribution from an AI-assistance contribution?**
2. **How should architecture venues and reviewer norms evolve for AI-assisted design loops?**
3. **When do rejected alternatives and negative data become creditable architecture contributions?**
4. **What shared tasks, standard baselines, and review incentives make loop-level architecture progress comparable?**

Roundtable logic: Chapter 1 should frame the new wave. It should help students,
authors, reviewers, and senior architects understand why AI-assisted design is
not merely a tooling trend, and why the community must deliberately evolve its
review norms instead of absorbing the shift accidentally.

### Chapter 2: Pressure Diagnosis and AI Entry Points

1. **When does the classical loop need AI assistance because generation outruns trusted feedback?**
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
3. **Which physical, power, and data-movement pressures signal that AI should help triage evidence?**
4. **When does software and workload drift make architecture evidence too brittle to maintain manually?**
5. **Where should AI assist when multiobjective tradeoffs exceed the loop's feedback budget?**

Roundtable logic: Chapter 2 should teach when and where AI belongs. It should
not yet teach the full mechanics of proxy trust, method roles, or evidence
ledgers. It diagnoses the pressure points that make those later mechanisms
necessary.

### Chapter 3: Ontology and Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**
2. **Which claim fields make workload characterization and benchmark scope reviewable?**
3. **How can design-space exclusions become auditable architecture evidence?**
4. **What can a claim commit to before its loop is executable?**

Roundtable logic: Chapter 3 should translate traditional architecture review
practice into explicit ontology. Workloads, baselines, objectives, constraints,
design-space boundaries, evidence, exclusions, and commitments become fields a
reviewer can inspect.

### Chapter 4: Representations and World Models

1. **What are the operational semantics of an auditable architecture proposal?**
2. **Where is an architecture world model calibrated, and when does a candidate leave support?**
3. **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**
4. **How can architecture representations discover novelty without forgetting negative evidence?**

Roundtable logic: Chapter 4 should ask what the loop can know. The historian
lens liked treating costly samples and prior failures as part of architecture's
quantitative record; the textbook lens kept the chapter on representation
rather than method control.

### Chapter 5: Environments and Tool Contracts

1. **What should an architecture environment contract expose before a generative loop can act?**
2. **Can agents infer environment contracts from legacy tool exhaust?**
3. **How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?**
4. **How can architecture environments stay valid as workloads, tools, software stacks, and failure records drift?**

Roundtable logic: Chapter 5 should ask where the loop acts. Legacy tools become
AI-callable environments only when action boundaries, observations, invalid
actions, feedback costs, security boundaries, and maintenance obligations are
explicit.

### Chapter 6: Method Roles and Feedback Allocation

1. **What contract language can bound the authority of generators, predictors, and optimizers before they become decision makers?**
2. **How should architecture loops allocate scarce feedback budgets across competing method roles?**
3. **How can optimizers learn from heterogeneous negative traces without elevating the fidelity of proxy evidence?**
4. **How can design loops balance novelty-seeking generation with evidence-seeking Pareto optimization?**

Roundtable logic: Chapter 6 should put actors into the loop without making them
authorities. It is about roles, permissions, feedback allocation, and useful
exploration, not yet about final trust.

### Chapter 7: Evidence and Trust

1. **How can multi-fidelity evidence ledgers bind architectural claims to their authorized commitment level?**
2. **What evaluation artifacts can expose adversarial proxy exploitation before an architectural commitment is made?**
3. **How can rejection authorities prove their independence from the methods that generated the candidates?**
4. **Can rejection authority survive and recover when underlying simulators or evidence sources are compromised?**

Roundtable logic: Chapter 7 should ask why the reader should believe the loop.
It owns evidence authority, proxy gaming, independent rejection, and adversarial
trust. It should not become a worked example or a community-governance chapter.

### Chapter 8: Executing One Loop

1. **What schema turns a broad architecture prompt into a legal, rejectable, and reproducible loop turn?**
2. **Which empirical signals should trigger a loop to escalate from cheap proxy feedback to scarce high-fidelity simulation?**
3. **How can proxy-audit steps expose evaluation mirages before scarce simulation hours are spent?**
4. **What receipt metadata makes a rejected architecture candidate reusable as a future under-evidenced lead?**

Roundtable logic: Chapter 8 should be a bounded worked example. It should show
one loop turn becoming legal, rejectable, escalated, and receipted, without
turning into field-wide infrastructure.

### Chapter 9: Cross-Stack Loop Patterns

1. **How can workload packets and baseline assumptions transfer safely across loops with different feedback costs?**
2. **What error bounds make cross-layer proxies safe to use as independent rejection authorities?**
3. **How should AI method autonomy scale with the rising cost of rollback down the stack?**
4. **How can co-design loops expose single-layer AI wins that violate cross-layer system objectives?**
5. **Can we track the half-life of architectural evidence across a co-evolving hardware-software stack?**

Roundtable logic: Chapter 9 should synthesize across the stack. The key is not a
single proxy or loop turn, but how evidence, assumptions, rollback cost,
autonomy, and system objectives transfer across workload, software, compiler,
runtime, hardware, RTL, and physical-design loops.

### Chapter 10: Ownership and Community Infrastructure

1. **How can redacted loop ledgers verify proprietary design claims without exposing physical IP?**
2. **How can the community turn rejected alternatives and negative traces into shared, reviewable infrastructure?**
3. **How can tacit architectural knowledge become explicit loop state without erasing human ownership?**
4. **How do we preserve human stop authority and accountability in long-horizon, multi-agent design loops?**
5. **What publication and artifact-evaluation incentives will fund the maintenance of Architecture 2.0 infrastructure?**

Roundtable logic: Chapter 10 returns high. The technical mechanisms developed in
the middle chapters become questions of community infrastructure, redaction,
tacit knowledge, durable human authority, and incentive design.

### Whole-Book Sequence Rationale

The sequence works as a U-shaped arc. Chapter 1 names the field wave and the
review problem; Chapter 2 explains the pressure points that make AI assistance
necessary. Chapters 3-9 then descend into the machinery of claims,
representations, environments, methods, evidence, execution, and cross-stack
transfer. Chapter 10 rises back to the field level and asks who owns the
resulting infrastructure, evidence, accountability, and maintenance burden.

## Sequential Chapter Fit Audit

This pass reread each chapter in order and checked the synthesis questions
against the actual chapter role, progressive disclosure, and set-level
cohesion. The main conclusion is that the sequence is working, but several
titles should be tightened so each chapter owns a distinct research agenda
rather than repeating later evidence, trust, or governance machinery too early.
The number of questions should follow the agenda; four is not a requirement.

### Revised Cohesive Title-Level Set

These titles are the current best fit after the sequential read.

#### Chapter 1: Field Wave and Review Norms

1. **What separates an architecture contribution from an AI-assistance contribution?**
2. **How should architecture review and artifact norms evolve for AI-assisted design loops?**
3. **When do rejected alternatives and negative evidence become creditable architecture contributions?**
4. **What shared tasks, baselines, and artifact-review incentives make loop-level architecture progress comparable?**

Fit note: This chapter should stay high. The current chapter text supports a
field agenda around loop-level contribution, rejected alternatives, evidence,
and reviewability. If the final wording explicitly names conferences or CFP
evolution, the chapter should add a short lead-in so that venue evolution is
not only introduced in the questions.

#### Chapter 2: Pressure Diagnosis and AI Entry Points

1. **When does the classical loop need AI assistance because generation outruns trusted feedback?**
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
3. **Which physical, power, and data-movement pressures should force evidence triage before expensive validation?**
4. **When does software and workload drift make architecture evidence too brittle to maintain manually?**
5. **Where do multiobjective tradeoffs first exceed the classical loop's feedback budget?**

Fit note: This is the strongest fit. The set teaches when and where AI belongs
under pressure from the scissors gap, specialization, chiplets, software drift,
physical constraints, and scarce trusted feedback. It should not yet teach the
full mechanics of schemas, ledgers, or trust machinery.

#### Chapter 3: Ontology and Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**
2. **Which claim fields make workload scope, baselines, and benchmark assumptions reviewable?**
3. **How can design-space exclusions and rejected alternatives become auditable architecture evidence?**
4. **What commitment boundary can a design-loop card state before the loop is executable?**

Fit note: The chapter is about making the claim and loop inspectable. Workload
characterization fits here when phrased as claim fields, not yet as the full
benchmark-maintenance problem that Chapter 9 develops.

#### Chapter 4: Representations and World Models

1. **What operational semantics make an architecture proposal auditable?**
2. **Where is an architecture world model calibrated, and when does a candidate leave support?**
3. **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**
4. **How can architecture representations support novelty while preserving negative evidence?**

Fit note: This chapter owns what the loop can know. The novelty question is a
fit only when it stays representation-centered: novelty under provenance,
coverage, transfer limits, and negative traces, not method behavior.

#### Chapter 5: Environments and Tool Contracts

1. **What should an architecture environment contract expose before a generative loop can act?**
2. **Can legacy tool traces reveal environment contracts?**
3. **How should environments bound model actions, invalid states, and irreversible tool side effects?**
4. **How can environments transfer negative evidence across physical and simulated tool flows?**
5. **How can architecture environments stay valid as workloads, tools, software stacks, and failure records drift?**

Fit note: This chapter needed the most adjustment. Security and IP language is
only lightly grounded here and belongs more naturally in Chapters 7 and 10
unless Chapter 5 is expanded. The more chapter-native agenda is environment
contracts, legacy tool exhaust, invalid-action semantics, negative evidence
transfer across tool flows, and environment drift.

#### Chapter 6: Method Roles and Feedback Allocation

1. **What role contracts keep AI methods from silently becoming decision makers?**
2. **How should loops allocate scarce feedback across generation, prediction, critique, and optimization?**
3. **How can optimizers learn from heterogeneous negative traces while preserving fidelity labels?**
4. **Can bounded rejection suites test hardware-aware generative models before their outputs are trusted?**
5. **How should methods trade off novelty, uncertainty reduction, and Pareto improvement?**

Fit note: This chapter owns method roles, not final trust. Adding the bounded
rejection-suite question preserves a strong in-source idea tied directly to the
hardware-awareness ladder, while keeping authority framed as role boundary
rather than governance.

#### Chapter 7: Evidence and Trust

1. **How can multi-fidelity evidence ledgers bind architectural claims to their authorized commitment level?**
2. **What evaluation artifacts can expose adversarial proxy exploitation before an architectural commitment is made?**
3. **How can rejection authorities be tested for independence from the methods that generated the candidates?**
4. **Can rejection authority remain effective when simulators or evidence sources are compromised?**

Fit note: This chapter cleanly owns trust: evidence ledgers, fidelity ladders,
commitment levels, proxy exploitation, independent rejection, security, and
confidentiality. The wording avoids overclaiming with words like "prove" or
"recover."

#### Chapter 8: Executing One Loop

1. **How can a broad architecture prompt be sliced into a legal, rejectable, replayable loop turn?**
2. **What signals should govern escalation from proxy feedback to stronger evidence?**
3. **What proxy-audit benchmark can expose interface-tax or data-movement mirages before scarce simulation is spent?**
4. **What receipt metadata makes a rejected architecture candidate reusable as a future under-evidenced lead?**

Fit note: This chapter is a worked turn, so the questions should be concrete:
slice the prompt, escalate evidence, expose the proxy mirage, and preserve the
receipt. Redacted cross-organization audit belongs later in Chapter 10.

#### Chapter 9: Cross-Stack Loop Patterns

1. **How can workload packets, baseline assumptions, and objective vectors transfer safely across loop patterns?**
2. **What error bounds make cheap cross-layer rejectors safe before stronger evidence is required?**
3. **How should method posture change across loop patterns as feedback cost and rollback risk rise?**
4. **How can co-design loops expose single-layer AI wins that violate cross-layer system objectives?**
5. **Can we track the half-life of architectural evidence across a co-evolving hardware-software stack?**

Fit note: This set is cohesive and serious. The terminology should use the
chapter's own language: method posture and cheap rejection authorities, not
generic autonomy or cross-layer proxies.

#### Chapter 10: Ownership and Community Infrastructure

1. **How can redacted loop ledgers verify design claims without exposing proprietary design state?**
2. **How can the community turn rejected alternatives and negative traces into shared, reviewable infrastructure?**
3. **How can tacit architectural knowledge become explicit loop state without erasing human ownership?**
4. **How do we preserve human stop authority and accountability in long-horizon, multi-agent design loops?**
5. **What publication, artifact-evaluation, and maintenance incentives sustain Architecture 2.0 infrastructure?**

Fit note: The final chapter should rise back to ownership and field
infrastructure. It should not repeat Chapter 7 trust mechanics except at the
community scale: redaction, shared negative traces, tacit knowledge, human stop
authority, and incentives.

### Whole-Book Cohesion Assessment

The chapter arc now reads coherently:

1. Chapter 1 frames the field wave and review problem.
2. Chapter 2 diagnoses when AI assistance is needed.
3. Chapter 3 defines the reviewable claim and loop ontology.
4. Chapter 4 asks what state the loop can know.
5. Chapter 5 asks where the loop can act.
6. Chapter 6 assigns method roles under feedback budgets.
7. Chapter 7 asks when evidence is trustworthy.
8. Chapter 8 runs one bounded turn and records its receipt.
9. Chapter 9 compares loop patterns across the stack.
10. Chapter 10 returns to human ownership and community infrastructure.

The main edits to preserve this arc are title-level, not structural. Chapter 1
should stay broad; Chapter 2 should stay diagnostic; Chapter 5 should stop
short of security/IP governance; Chapter 6 should avoid becoming a trust
chapter; Chapter 8 should avoid field-level redaction; and Chapter 10 should
carry the incentive and infrastructure agenda.

## Chapter 1: The Architecture 2.0 Moonshot

Chapter role: broad field agenda. These should read as questions for the field,
reviewers, venues, and research community, not as detailed paper abstracts.

### Ch1-Q1: Contribution Versus Demo

Candidate titles:

1. What makes an Architecture 2.0 result a contribution rather than a demo?
2. When does an AI-generated architecture become a research claim?
3. What separates loop-level architecture research from generated artifacts?
4. What evidence turns an AI architecture demo into a field contribution?
5. What should count as a contribution in AI-assisted architecture?
6. How should architects judge whether an AI-generated design advances the field?

Recommended title: **What makes an Architecture 2.0 result a contribution rather than a demo?**

Rationale: This keeps the question broad enough for a field agenda while testing
the distinction between artifact generation and governed, rejectable design
loops.

### Ch1-Q2: Review Norms

Candidate titles:

1. How should architecture venues judge AI-assisted design claims?
2. What should peer review ask of AI-assisted architecture work?
3. How can reviewers evaluate architecture work whose contribution is a loop?
4. What makes an AI-assisted architecture result conference-worthy?
5. How should the field review AI-assisted claims beyond artifact quality?
6. What evidence should reviewers expect from AI-assisted architecture?

Recommended title: **How should architecture venues judge AI-assisted design claims?**

Rationale: This names the actors who shape norms while staying at the field
agenda level.

### Ch1-Q3: Rejected Alternatives As Contribution

Candidate titles:

1. When do rejected alternatives become part of the architecture contribution?
2. How should architecture research credit what a design loop rules out?
3. When is a failed design path useful evidence rather than wasted work?
4. How should the field value negative results from AI-assisted design loops?
5. What makes rejection a first-class research output in architecture?
6. How can failed candidates strengthen an architecture claim?

Recommended title: **When do rejected alternatives become part of the architecture contribution?**

Rationale: This keeps the opening chapter broad while preserving the shift from
rewarding only winners to valuing the loop that bounds and rejects them.

### Ch1-Q4: Shared Tasks, Norms, and Incentives

Candidate titles:

1. What shared tasks make loop-level architecture progress comparable?
2. How should conferences evaluate AI-assisted architecture loops?
3. What publication norms make architecture loop claims reproducible?
4. How can the field reward comparable progress in AI-assisted design loops?
5. What community infrastructure turns architecture loop showcases into shared evidence?
6. What shared tasks, publication norms, and incentives make loop-level architecture progress comparable?

Recommended title: **What shared tasks, publication norms, and incentives make loop-level architecture progress comparable?**

Rationale: This stays at the conference and community level while naming shared
tasks, publication norms, and incentives.

## Chapter 2: Why Classical Architecture Loops Strain

Chapter role: diagnose why classical loops strain and ask how AI should be read
under scarce feedback, specialization, chiplets, physical constraints, software
drift, and multiobjective cost.

### Ch2-Q1: Feedback Bound

Candidate titles:

1. Where does the classical loop become feedback bound?
2. When does generation outrun trusted rejection?
3. What makes the scissors gap visible?
4. How much feedback can a classical architecture loop afford?
5. When do more candidates stop helping?
6. Where does trusted feedback become the limiting resource?

Recommended title: **Where does the classical loop become feedback bound?**

Rationale: This keeps the chapter diagnostic and avoids Chapter 3-style schema
language.

### Ch2-Q2: Specialization, Chiplets, and Verification Capacity

Candidate titles:

1. How can heterogeneous chiplet search stay inside verification capacity?
2. What loop state makes specialized chiplet designs reviewable?
3. How can AI explore specialization without widening the scissors gap?
4. Which rejection gates make heterogeneous architecture search safe?
5. How should chiplet design spaces be pruned before high-fidelity checks?
6. Can specialization scale without overwhelming trusted feedback?

Recommended title: **How can heterogeneous chiplet search stay inside verification capacity?**

Rationale: This captures the pressure point where specialization and chiplets
multiply design actions while trusted rejection stays scarce.

### Ch2-Q3: Early Physical Rejection

Candidate titles:

1. What physical signals should reject AI-generated architectures early?
2. Which early physical constraints predict expensive architecture failure?
3. How should cheap physical proxies be calibrated against high-cost evidence?
4. Which data-movement, thermal, timing, and power signals deserve rejection authority?
5. When should physical feasibility stop an architecture candidate?
6. What early-rejection gates keep AI search inside physical reality?

Recommended title: **What physical signals should reject AI-generated architectures early?**

Rationale: This foregrounds physical evidence and rejection authority without
narrowing to one constraint class too early.

### Ch2-Q4: Evidence Validity Under Drift

Candidate titles:

1. How should architecture evidence age under software and workload drift?
2. When does drift invalidate an architectural claim?
3. How long can architecture evidence support a silicon commitment?
4. How should design loops track the expiration of workload evidence?
5. What validity horizon should architecture claims carry?
6. How can versioned software stacks keep architecture evidence current?

Recommended title: **How should architecture evidence age under software and workload drift?**

Rationale: This keeps the focus on evidence rather than generic workload change.

### Ch2-Q5: Multiobjective Feedback Pricing

Candidate titles:

1. How should scarce feedback be priced across performance, energy, carbon, and verification risk?
2. What budget model should govern simulator hours, EDA licenses, and human review?
3. How can architecture loops allocate evidence across power, cost, carbon, and performance?
4. When should an AI-assisted loop spend stronger feedback on a multiobjective claim?
5. How can feedback cost become a first-class objective in architecture search?
6. What is the exchange rate between cheaper proxies, expensive tools, and human judgment?

Recommended title: **How should scarce feedback be priced across performance, energy, carbon, and verification risk?**

Rationale: This treats feedback as the limiting resource and links it to
multiobjective architecture tradeoffs.

## Chapter 3: Reviewable Architecture Studies

Chapter role: introduce the ontology as an architecture-native review object
grounded in workload characterization, benchmarks, baselines, design spaces,
objectives, constraints, evidence, rejected alternatives, and human commitment.

### Ch3-Q1: Workload and Benchmark Claim Fields

Candidate titles:

1. Which claim fields make workload characterization reviewable?
2. How should architecture papers bound workload, baseline, objective, and design-space claims?
3. What minimum claim packet lets reviewers judge benchmark scope and baseline validity?
4. Can workload characterization become a structured review object for architecture claims?
5. Which workload, baseline, objective, and constraint fields define a reviewable design boundary?
6. How can benchmark scope and design-space boundaries be stated as architecture claim fields?

Recommended title: **Which claim fields make workload characterization and benchmark scope reviewable?**

Rationale: This keeps Chapter 3 centered on ontology and review, not later
environment or trust mechanics.

### Ch3-Q2: Minimum Claim Schema

Candidate titles:

1. What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?
2. Which claim fields are necessary for reviewing AI-assisted architecture work?
3. How much structure does an architectural claim need before AI can act inside it?
4. What is the smallest reviewable claim packet for AI-assisted architecture?
5. Which parts of architectural judgment can be represented without being automated away?
6. Can a lightweight claim schema separate AI output from architectural commitment?

Recommended title: **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**

Rationale: This fits the ontology chapter while preserving the distinction
between auditability and delegated commitment.

### Ch3-Q3: Design-Space Exclusions

Candidate titles:

1. How should rejected alternatives be recorded as architecture evidence?
2. What makes a failed baseline a reviewable design-space boundary?
3. How can design-space exclusions become auditable evidence?
4. What evidence should survive when an architecture loop says no?
5. How should failed comparisons bound a reviewable design space?
6. When do rejected candidates strengthen an architectural claim?

Recommended title: **How can design-space exclusions become auditable architecture evidence?**

Rationale: This keeps negative evidence at the ontology level, as reviewable
boundary information rather than later learning machinery.

### Ch3-Q4: Pre-Executable Commitment Boundary

Candidate titles:

1. What can a claim commit to before its loop is executable?
2. What commitment boundary can a non-executable claim state?
3. How much architectural commitment can early evidence carry?
4. Where should a design-loop card stop short of commitment?
5. What remains uncommitted before environments and gates exist?
6. How should claims name their pre-executable commitment boundary?

Recommended title: **What can a claim commit to before its loop is executable?**

Rationale: This stays at the Chapter 3 ontology level and avoids later formal
environment, gate, and governance mechanics.

## Chapter 4: Representations and World Models

Chapter role: define what architecture state must be represented before loops,
tools, and methods can act.

### Ch4-Q1: Auditable Proposal Semantics

Candidate titles:

1. What are the operational semantics of an auditable architecture proposal?
2. What makes an architecture proposal executable, replayable, and rejectable?
3. How should architecture proposals encode intent, evidence, and rejection?
4. Can architecture proposals become formal boundary objects for design loops?
5. What semantics make automated architecture proposals actionable and auditable?
6. How can proposal languages bind design intent to tool-checked evidence?

Recommended title: **What are the operational semantics of an auditable architecture proposal?**

Rationale: This keeps the contribution centered on semantics rather than a
particular language or benchmark.

### Ch4-Q2: World-Model Support Boundaries

Candidate titles:

1. Where is an architecture world model calibrated, and when does a candidate leave support?
2. Can architecture world models learn their own support boundaries?
3. How should world models mark calibration, coverage, and support loss?
4. Can calibration-boundary models route architecture candidates to stronger evidence?
5. What state must a world model cover before an optimizer may trust it?
6. When should a world model escalate rather than accept an architecture candidate?

Recommended title: **Where is an architecture world model calibrated, and when does a candidate leave support?**

Rationale: This names calibration and support directly while staying focused on
world-model scope.

### Ch4-Q3: Sample Cost, Fidelity, Provenance, and Coverage

Candidate titles:

1. How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?
2. Can sample metadata bound generalization in AI-driven architecture design?
3. When does an architecture sample justify transferring a design-space lesson?
4. What makes expensive architecture feedback reusable evidence rather than isolated measurement?
5. How should design loops price evidence across fidelity, coverage, and risk?
6. Can architecture agents learn when scarce samples stop transferring?

Recommended title: **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**

Rationale: This keeps sample cost inside the representation problem.

### Ch4-Q4: Novelty and Negative Evidence

Candidate titles:

1. How can architecture representations discover novelty without forgetting negative evidence?
2. What representations let design agents find new candidates within auditable evidence boundaries?
3. How can negative traces become a substrate for novel architecture design?
4. Can representation learning distinguish reusable failures from local dead ends?
5. What evidence schemas let novelty transfer without overgeneralizing failure?
6. How should architecture loops represent novelty, failure context, and transfer limits?

Recommended title: **How can architecture representations discover novelty without forgetting negative evidence?**

Rationale: This adds a positive discovery agenda while keeping negative traces
visible as representation state.

## Chapter 5: Tools As Architecture Environments

Chapter role: make tools environment-like through contracts over actions,
observations, invalid states, feedback, fidelity, security, and maintenance.

### Ch5-Q1: Inferring Environment Contracts

Candidate titles:

1. Can legacy tool traces reveal formal environment contracts?
2. Can agents infer environment contracts from legacy tool exhaust?
3. How can simulator, compiler, EDA, and runtime logs become environment contracts?
4. Can unstructured tool exhaust define legal actions and rejection rules?
5. How do we recover action schemas from legacy architecture toolchains?
6. Can tool failure traces become auditable environment contracts?

Recommended title: **Can agents infer environment contracts from legacy tool exhaust?**

Rationale: This directly matches the chapter's claim that tools become
environments when actions, observations, costs, provenance, and rejection
authority are explicit.

### Ch5-Q2: Exposed Environment Contract Fields

Candidate titles:

1. Can architecture environments expose enough contract structure for safe automated action?
2. How should tool environments encode legal actions, invalid states, and rejection authority?
3. What makes an action and feedback contract complete enough for architecture loops?
4. Can feedback cost and fidelity become first-class fields in architecture environment APIs?
5. How can environment contracts prevent hidden tool limits from becoming hidden loop state?
6. What should an architecture environment contract expose before a generative loop can act?

Recommended title: **What should an architecture environment contract expose before a generative loop can act?**

Rationale: This is broad enough to cover legal actions, invalid-action
semantics, observations, feedback cost, fidelity, and rejection authority.

### Ch5-Q3: Security and Isolation

Candidate titles:

1. Can AI-callable architecture environments enforce least-privilege contracts over tools, workloads, and proprietary state?
2. How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?
3. What security contract should govern AI agents that act through architecture toolchains?
4. Can environment harnesses expose enough design state while keeping proprietary state isolated?
5. How can architecture loops prove that tool calls are confined, auditable, and reversible before commitment?
6. What isolation boundary lets generative methods use industrial tool flows without leaking data or mutating trusted state?

Recommended title: **How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?**

Rationale: This keeps security inside the environment-contract framing.

### Ch5-Q4: Environment Drift and Maintenance

Candidate titles:

1. How can architecture environments stay valid as workloads, tools, software stacks, and failure records drift?
2. What operating discipline keeps architecture environments trustworthy after the first paper?
3. Can ArchOps monitors recertify architectural claims as their evidence decays?
4. How should environment contracts evolve when workloads and toolchains change?
5. Can negative traces keep stale architecture environments from misleading design loops?
6. What makes an AI-assisted architecture environment maintainable over time?

Recommended title: **How can architecture environments stay valid as workloads, tools, software stacks, and failure records drift?**

Rationale: This stays tied to environment validity rather than generic
infrastructure automation.

## Chapter 6: Method Roles: Generate, Predict, Optimize

Chapter role: assign and adapt method roles under bounded feedback budgets.

### Ch6-Q1: Method-Role Contracts

Candidate titles:

1. How can AI method-role contracts define what each role may read, write, and decide?
2. What contract language can bound the authority of generators, predictors, optimizers, and critics?
3. How should architecture loops enforce read, write, and decision boundaries for AI method roles?
4. Can role contracts prevent AI methods from silently becoming decision makers?
5. What audit model can expose authority creep across AI method roles?
6. How can shared loop state make method-role permissions enforceable and reviewable?

Recommended title: **What contract language can bound the authority of generators, predictors, optimizers, and critics?**

Rationale: This foregrounds authority boundaries while staying in the chapter's
method-role vocabulary.

### Ch6-Q2: Feedback Allocation Across Roles

Candidate titles:

1. How should architecture loops allocate scarce feedback across method roles?
2. What policies decide when to generate, predict, optimize, critique, or repair?
3. Can meta-controllers spend feedback where method roles have the highest decision value?
4. How should scarce high-fidelity checks be split between creating candidates and rejecting weak claims?
5. What feedback-allocation rules maximize architectural learning across method roles?
6. How can loops reallocate effort among generation, prediction, optimization, critique, and repair?

Recommended title: **How should architecture loops allocate scarce feedback across method roles?**

Rationale: This treats method choice as a role-and-budget decision.

### Ch6-Q3: Fidelity-Labeled Negative Traces

Candidate titles:

1. How can optimizers learn from heterogeneous negative traces while preserving fidelity boundaries?
2. What acquisition policies can use failed runs without flattening evidence fidelity?
3. How should active-learning loops turn negative traces into decision-relevant evidence?
4. Can optimizer policies learn from loop residue without promoting weak rejection signals?
5. How can sample-efficient search use proxy failures, tool errors, and rare high-fidelity rejections together?
6. What fidelity-aware learning rules make negative traces useful without overstating what they prove?

Recommended title: **How can optimizers learn from heterogeneous negative traces while preserving fidelity boundaries?**

Rationale: This makes negative traces useful to methods without allowing weak
evidence to masquerade as high-fidelity rejection.

### Ch6-Q4: Novelty and Pareto Evidence

Candidate titles:

1. How can AI-assisted architecture loops balance novelty-seeking exploration with evidence-seeking Pareto optimization?
2. What acquisition policies can discover novel architectures without weakening multiobjective evidence standards?
3. How should optimizers trade off Pareto improvement, uncertainty reduction, and architectural novelty?
4. Can multiobjective architecture search learn when to explore surprising regions and when to consolidate evidence?
5. How can design loops reward positive discovery while preserving Pareto-frontier accountability?
6. What method adaptations make novelty useful rather than distracting in evidence-constrained architecture optimization?

Recommended title: **How can AI-assisted architecture loops balance novelty-seeking exploration with evidence-seeking Pareto optimization?**

Rationale: This adds positive discovery while preserving the chapter's
evidence-constrained discipline.

## Chapter 7: Feedback, Evidence, and Trust

Chapter role: bind feedback to evidence, evidence to claims, and claims to
trustworthy rejection and commitment boundaries.

### Ch7-Q1: Evidence Ledgers and Authorized Commitment

Candidate titles:

1. How should multi-fidelity evidence ledgers cap architectural claims?
2. Can evidence ledgers bind claims to their authorized commitment level?
3. What prevents proxy evidence from becoming signoff-grade commitment?
4. How can claim-bound evidence packets make escalation auditable?
5. What checks keep multi-fidelity evidence from overauthorizing a design claim?
6. Can tamper-evident ledgers enforce the highest defensible claim?

Recommended title: **Can evidence ledgers bind claims to their authorized commitment level?**

Rationale: This ties evidence, claims, and commitment boundaries into one trust
problem.

### Ch7-Q2: Proxy Exploitation Before Commitment

Candidate titles:

1. Can adversarial proxy wins be detected before commitment?
2. How can loops detect proxy exploitation before architectural commitment?
3. When should proxy wins trigger escalation rather than commitment?
4. Can surrogate uncertainty expose adversarial proxy wins?
5. How should calibration gates catch misleading proxy wins?
6. Can AI-assisted loops reject proxy wins before they harden into architecture?

Recommended title: **Can adversarial proxy wins be detected before commitment?**

Rationale: This keeps the proxy mismatch question tied to commitment rather
than score improvement.

### Ch7-Q3: Independent Rejection Authority

Candidate titles:

1. How can rejection authorities be tested for shared blind spots?
2. When are multiple AI-assisted checks truly independent?
3. How should loops measure independence between generators and rejectors?
4. Can correlated verification tools provide real rejection authority?
5. What stress tests expose shared failure modes among rejection authorities?
6. How can evidence sources prove independence before commitment?

Recommended title: **How can rejection authorities be tested for shared blind spots?**

Rationale: Trust depends on whether the rejector can fail independently from
the system that produced the claim.

### Ch7-Q4: Compromised Evidence Sources

Candidate titles:

1. Can rejection authority survive compromised evidence sources?
2. How should trust mechanisms defend against poisoned baselines and deceptive proxies?
3. Can evidence ledgers detect tampering before trust becomes commitment?
4. How can AI-assisted loops verify tools that may themselves be compromised?
5. What security gates catch side channels hidden behind proxy wins?
6. How should architecture loops defend trust machinery against adversarial evidence?

Recommended title: **Can rejection authority survive compromised evidence sources?**

Rationale: This distinguishes compromised evidence from shared-blind-spot
independence.

## Chapter 8: Running The Lighthouse Loop

Chapter role: generalize from one bounded loop turn without jumping to community
infrastructure.

### Ch8-Q1: Prompt to Rejectable Loop Turn

Candidate titles:

1. How can broad architecture prompts become legal, rejectable loop turns?
2. What makes an AI-assisted architecture turn bounded enough to reject?
3. How should prompt slices define legal actions and rejection gates?
4. Can AI loops compile lighthouse-scale prompts into auditable task slices?
5. How should architecture loops record the boundary between prompt and turn?
6. What schema turns a one-shot architecture prompt into a reviewable loop?

Recommended title: **How can broad architecture prompts become legal, rejectable loop turns?**

Rationale: This matches the chapter's move from the lighthouse prompt to one
XRBench-class slice with legal candidates and declared gates.

### Ch8-Q2: Escalation From Proxy Feedback

Candidate titles:

1. What signals should trigger escalation from proxy feedback to stronger evidence?
2. When is a proxy ranking too risky to trust?
3. How should loops decide when cheap feedback has done enough?
4. Can proxy uncertainty govern scarce simulation budgets?
5. When should a loop spend high-fidelity evidence?
6. How can proxy blind spots be detected before commitment?

Recommended title: **What signals should trigger escalation from proxy feedback to stronger evidence?**

Rationale: This frames escalation as an evidence-control decision.

### Ch8-Q3: Proxy-Audit Benchmarks

Candidate titles:

1. Can proxy-audit benchmarks expose interface-tax mirages before scarce simulation is spent?
2. How can analytical proxies be stress-tested for hidden data-movement costs?
3. Can benchmarked proxy audits predict when cheap architecture screens are misleading?
4. What benchmark signals reveal analytical blind spots before high-fidelity simulation?
5. Can data-movement mirages be detected from proxy receipts alone?
6. How should proxy-audit suites measure false confidence in low-fidelity screens?

Recommended title: **Can proxy-audit benchmarks expose interface-tax mirages before scarce simulation is spent?**

Rationale: This names the worked proxy mirage and a concrete research artifact.

### Ch8-Q4: Receipts, Under-Evidenced Leads, and Stale Rejections

Candidate titles:

1. What receipt lets a loop reopen stale rejections safely?
2. How can loop receipts preserve under-evidenced discoveries?
3. When should negative traces become candidates again?
4. Can receipt metadata distinguish dead ends from under-evidenced leads?
5. How should AI-assisted loops expire or revive past rejections?
6. What evidence makes a rejected architecture worth reconsidering?

Recommended title: **Can receipt metadata distinguish dead ends from under-evidenced leads?**

Rationale: This treats the receipt as the mechanism that carries decisions
forward.

## Chapter 9: Loop Patterns Across The Stack

Chapter role: cross-stack transfer of loop contracts, evidence, rejectors,
postures, and evidence validity.

### Ch9-Q1: Workload and Objective Transfer

Candidate titles:

1. How can workload packets, baselines, objective vectors, and task assumptions transfer safely across AI-assisted architecture loops?
2. What schema lets design-loop assumptions travel from compiler/runtime feedback to RTL and physical evidence without losing validity?
3. How can cross-layer loop packets preserve baselines and objectives as claims move from DSE to co-design and fleet deployment?
4. Can architecture loops expose when transferred baselines, objectives, and workload assumptions have become stale or incompatible?
5. What makes a workload packet reusable across DSE, co-design, fleet, compiler/runtime, RTL, and physical-design loops?
6. How should evidence ledgers carry objective vectors and task assumptions across feedback regimes with different rejection authorities?

Recommended title: **How can workload packets, baselines, objective vectors, and task assumptions transfer safely across AI-assisted architecture loops?**

Rationale: This preserves the loop contract as claims move across regimes with
different feedback costs and rejection authorities.

### Ch9-Q2: Evidence and Escalation Transfer

Candidate titles:

1. Can evidence and escalation contracts transfer across loop patterns without weakening the commitments they govern?
2. What makes rejection evidence admissible when it moves from one loop pattern to another?
3. How should AI-assisted architecture loops carry escalation boundaries across the stack?
4. Can negative traces and rejection gates remain valid as evidence crosses feedback regimes?
5. What contract lets software-loop evidence support hardware-loop commitments?
6. How can cross-stack loops preserve evidence meaning while feedback cost and rollback risk change?

Recommended title: **Can evidence and escalation contracts transfer across loop patterns without weakening the commitments they govern?**

Rationale: This asks what must remain true when evidence moves between loop
regimes.

### Ch9-Q3: Cheap Rejector Bounds

Candidate titles:

1. How far can cheap rejectors carry an AI-assisted design loop?
2. What error bounds make cheap rejectors safe across stack layers?
3. Can false-pass and false-reject rates define commitment boundaries?
4. How should cheap rejectors be calibrated before higher-commitment use?
5. What is the maximum safe commitment for a cheap rejection authority?
6. Can cross-layer rejectors be certified against high-fidelity evidence?

Recommended title: **What error bounds make cheap rejectors safe across stack layers?**

Rationale: This combines cheap rejectors, error bounds, and the commitment level
those bounds can justify.

### Ch9-Q4: Method Posture Adaptation

Candidate titles:

1. When should an architecture loop change its method posture?
2. How should method posture adapt when proxies, rollback, and escalation costs shift?
3. Can loop posture be chosen from feedback cost and commitment risk?
4. When does proxy mismatch force a loop from exploration to critique?
5. How can architecture loops price posture changes across feedback and rollback regimes?
6. What evidence should trigger a shift from generation to repair, critique, or escalation?

Recommended title: **How should method posture adapt when proxies, rollback, and escalation costs shift?**

Rationale: This keeps the focus on loop contracts, evidence cost, reversibility,
and escalation burden rather than generic agent control.

### Ch9-Q5: Evidence Half-Life Across The Stack

Candidate titles:

1. Can we track the half-life of architectural evidence across a co-evolving stack?
2. How can AI-assisted architecture loops know when cross-layer evidence has expired?
3. Can evidence ledgers assign validity windows as workloads, compilers, runtimes, hardware, deployments, RTL, and physical flows drift?
4. What mechanisms can propagate evidence invalidation across workload, software, hardware, and silicon-facing toolchains?
5. Can cross-stack provenance detect when a once-valid architecture claim has gone stale?
6. How should AI-assisted design loops refresh evidence as stack assumptions co-evolve?

Recommended title: **Can we track the half-life of architectural evidence across a co-evolving stack?**

Rationale: This names the useful lifetime of evidence as the measurable object.

## Chapter 10: What The Architect Owns

Chapter role: ownership, redacted audit, shared infrastructure, tacit knowledge,
publication incentives, and human stop authority.

### Ch10-Q1: Redacted Loop Integrity

Candidate titles:

1. How can redacted loop records be audited across competitive ecosystems?
2. How can redacted loop integrity be verified without exposing proprietary design state?
3. What audit protocol can make private architecture loops publicly accountable?
4. How can federated architecture ecosystems verify evidence under redaction?
5. Can reviewers detect missing evidence in redacted competitive design loops?
6. How can public evidence ledgers certify private architecture loop claims?

Recommended title: **How can redacted loop integrity be verified without exposing proprietary design state?**

Rationale: This centers auditability, redaction, and accountability rather than
privacy technology alone.

### Ch10-Q2: Reviewable Community Negative Traces

Candidate titles:

1. How can negative traces become reviewable evidence rather than opaque training data?
2. How can architecture models learn from failures the community can inspect?
3. How should redacted design failures become reusable community evidence?
4. What makes a rejected design path credible as shared evidence?
5. How can failure traces support learning without hiding accountability?
6. How can redacted negative traces make architecture claims more reviewable?

Recommended title: **How can negative traces become reviewable evidence rather than opaque training data?**

Rationale: This shifts the emphasis from model training to community review.

### Ch10-Q3: Tacit Constraints and Ownership

Candidate titles:

1. How can tacit architectural constraints become reviewable loop state without erasing human ownership?
2. How can AI-assisted architecture loops codify expert constraints while preserving human stop authority?
3. What representations make tacit architectural knowledge machine-usable and still architect-owned?
4. How can design environments surface unwritten constraints before automated action crosses a commitment boundary?
5. How can tacit constraints become evidence gates without turning judgment into unreviewable automation?
6. How can teams preserve accountable ownership when expert intuition becomes machine-readable loop state?

Recommended title: **How can tacit architectural constraints become reviewable loop state without erasing human ownership?**

Rationale: This keeps codification tied to reviewability and accountable
ownership.

### Ch10-Q4: Publication Standards and Infrastructure Incentives

Candidate titles:

1. What publication standards make evidence-gated Architecture 2.0 infrastructure worth maintaining?
2. How should artifact review evaluate AI-mediated architecture claims?
3. How can venues reward reusable evidence infrastructure rather than isolated demos?
4. What evidence gates should papers expose before reviewers trust an Architecture 2.0 claim?
5. How can publication norms turn loop infrastructure into a shared field asset?
6. What should artifact committees require from evidence-bearing architecture loops?

Recommended title: **What publication standards make evidence-gated Architecture 2.0 infrastructure worth maintaining?**

Rationale: This links venues, evidence gates, and maintenance incentives.

### Ch10-Q5: Human Stop Authority

Candidate titles:

1. How can human stop authority survive ownership transfer in asynchronous multi-agent design loops?
2. How should asynchronous architecture loops preserve a human veto when claims and owners drift?
3. How can commitment ledgers keep stale claims rejectable after ownership transfer?
4. What mechanisms keep a named human able to halt drifting multi-agent design loops?
5. How can stop authority be revalidated when workload claims, tool state, and owners change?
6. How do we make human rejection authority durable across long-horizon multi-agent architecture work?

Recommended title: **How can human stop authority survive ownership transfer in asynchronous multi-agent design loops?**

Rationale: This emphasizes enforceable halt rights as claims, agents, evidence,
and owners change over time.
