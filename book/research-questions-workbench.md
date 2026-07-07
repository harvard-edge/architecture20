# Architecture 2.0 Research Questions Workbench

Generated: July 7, 2026

Purpose: collect candidate open research question titles for review before editing
the chapter source files. Chapter files were not modified. Each slot below was
handled by a separate read-only agent that read the relevant chapter and
generated alternatives only for that slot.

Latest working set: use **Sequential Chapter Fit Audit** as the current
chapter-by-chapter recommendation. Earlier synthesis sections are retained as
provenance for how the set evolved.

## Synthesis After User Feedback And Iterative Editorial Review

This synthesis layer reflects the follow-up discussion and an iterative
read-only `agy` / Gemini 3.1 Pro editorial conversation. The conversation used
three explicit lenses: a senior architecture-field historian, a textbook editor,
and a modern architecture/MLSys program-chair perspective. It does not replace
the candidate lists below. It records the current best direction before any
chapter-source rewrite.

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

### CFP And Venue-Evolution Notes

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

### Chapter 1: Field Wave And Review Norms

1. **What separates an architecture contribution from an AI-assistance contribution?**
2. **How should architecture venues and reviewer norms evolve for AI-assisted design loops?**
3. **When do rejected alternatives and negative data become creditable architecture contributions?**
4. **What shared tasks, standard baselines, and review incentives make loop-level architecture progress comparable?**

Roundtable logic: Chapter 1 should frame the new wave. It should help students,
authors, reviewers, and senior architects understand why AI-assisted design is
not merely a tooling trend, and why the community must deliberately evolve its
review norms instead of absorbing the shift accidentally.

### Chapter 2: Pressure Diagnosis And AI Entry Points

1. **When does the classical loop need AI assistance because generation outruns trusted feedback?**
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
3. **Which physical, power, and data-movement pressures signal that AI should help triage evidence?**
4. **When does software and workload drift make architecture evidence too brittle to maintain manually?**
5. **Where should AI assist when multiobjective tradeoffs exceed the loop's feedback budget?**

Roundtable logic: Chapter 2 should teach when and where AI belongs. It should
not yet teach the full mechanics of proxy trust, method roles, or evidence
ledgers. It diagnoses the pressure points that make those later mechanisms
necessary.

### Chapter 3: Ontology And Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**
2. **Which claim fields make workload characterization and benchmark scope reviewable?**
3. **How can design-space exclusions become auditable architecture evidence?**
4. **What can a claim commit to before its loop is executable?**

Roundtable logic: Chapter 3 should translate traditional architecture review
practice into explicit ontology. Workloads, baselines, objectives, constraints,
design-space boundaries, evidence, exclusions, and commitments become fields a
reviewer can inspect.

### Chapter 4: Representations And World Models

1. **What are the operational semantics of an auditable architecture proposal?**
2. **Where is an architecture world model calibrated, and when does a candidate leave support?**
3. **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**
4. **How can architecture representations discover novelty without forgetting negative evidence?**

Roundtable logic: Chapter 4 should ask what the loop can know. The historian
lens liked treating costly samples and prior failures as part of architecture's
quantitative record; the textbook lens kept the chapter on representation
rather than method control.

### Chapter 5: Environments And Tool Contracts

1. **What should an architecture environment contract expose before a generative loop can act?**
2. **Can agents infer environment contracts from legacy tool exhaust?**
3. **How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?**
4. **How can architecture environments stay valid as workloads, tools, software stacks, and failure records drift?**

Roundtable logic: Chapter 5 should ask where the loop acts. Legacy tools become
AI-callable environments only when action boundaries, observations, invalid
actions, feedback costs, security boundaries, and maintenance obligations are
explicit.

### Chapter 6: Method Roles And Feedback Allocation

1. **What contract language can bound the authority of generators, predictors, and optimizers before they become decision makers?**
2. **How should architecture loops allocate scarce feedback budgets across competing method roles?**
3. **How can optimizers learn from heterogeneous negative traces without elevating the fidelity of proxy evidence?**
4. **How can design loops balance novelty-seeking generation with evidence-seeking Pareto optimization?**

Roundtable logic: Chapter 6 should put actors into the loop without making them
authorities. It is about roles, permissions, feedback allocation, and useful
exploration, not yet about final trust.

### Chapter 7: Evidence And Trust

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

### Chapter 10: Ownership And Community Infrastructure

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

#### Chapter 1: Field Wave And Review Norms

1. **What separates an architecture contribution from an AI-assistance contribution?**
2. **How should architecture review and artifact norms evolve for AI-assisted design loops?**
3. **When do rejected alternatives and negative evidence become creditable architecture contributions?**
4. **What shared tasks, baselines, and artifact-review incentives make loop-level architecture progress comparable?**

Fit note: This chapter should stay high. The current chapter text supports a
field agenda around loop-level contribution, rejected alternatives, evidence,
and reviewability. If the final wording explicitly names conferences or CFP
evolution, the chapter should add a short lead-in so that venue evolution is
not only introduced in the questions.

#### Chapter 2: Pressure Diagnosis And AI Entry Points

1. **When does the classical loop need AI assistance because generation outruns trusted feedback?**
2. **At which system levels should AI interact when specialization and chiplets expand the design space?**
3. **Which physical, power, and data-movement pressures should force evidence triage before expensive validation?**
4. **When does software and workload drift make architecture evidence too brittle to maintain manually?**
5. **Where do multiobjective tradeoffs first exceed the classical loop's feedback budget?**

Fit note: This is the strongest fit. The set teaches when and where AI belongs
under pressure from the scissors gap, specialization, chiplets, software drift,
physical constraints, and scarce trusted feedback. It should not yet teach the
full mechanics of schemas, ledgers, or trust machinery.

#### Chapter 3: Ontology And Reviewable Claims

1. **What minimum claim schema makes AI-assisted architecture work reviewable while preserving architectural judgment?**
2. **Which claim fields make workload scope, baselines, and benchmark assumptions reviewable?**
3. **How can design-space exclusions and rejected alternatives become auditable architecture evidence?**
4. **What commitment boundary can a design-loop card state before the loop is executable?**

Fit note: The chapter is about making the claim and loop inspectable. Workload
characterization fits here when phrased as claim fields, not yet as the full
benchmark-maintenance problem that Chapter 9 develops.

#### Chapter 4: Representations And World Models

1. **What operational semantics make an architecture proposal auditable?**
2. **Where is an architecture world model calibrated, and when does a candidate leave support?**
3. **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**
4. **How can architecture representations support novelty while preserving negative evidence?**

Fit note: This chapter owns what the loop can know. The novelty question is a
fit only when it stays representation-centered: novelty under provenance,
coverage, transfer limits, and negative traces, not method behavior.

#### Chapter 5: Environments And Tool Contracts

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

#### Chapter 6: Method Roles And Feedback Allocation

1. **What role contracts keep AI methods from silently becoming decision makers?**
2. **How should loops allocate scarce feedback across generation, prediction, critique, and optimization?**
3. **How can optimizers learn from heterogeneous negative traces while preserving fidelity labels?**
4. **Can bounded rejection suites test hardware-aware generative models before their outputs are trusted?**
5. **How should methods trade off novelty, uncertainty reduction, and Pareto improvement?**

Fit note: This chapter owns method roles, not final trust. Adding the bounded
rejection-suite question preserves a strong in-source idea tied directly to the
hardware-awareness ladder, while keeping authority framed as role boundary
rather than governance.

#### Chapter 7: Evidence And Trust

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

#### Chapter 10: Ownership And Community Infrastructure

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

### Ch1-Q4: Shared Tasks, Norms, And Incentives

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

### Ch2-Q2: Specialization, Chiplets, And Verification Capacity

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

## Chapter 3: Architectural Claims And Design Loops

Chapter role: introduce the ontology as an architecture-native review object
grounded in workload characterization, benchmarks, baselines, design spaces,
objectives, constraints, evidence, rejected alternatives, and human commitment.

### Ch3-Q1: Workload And Benchmark Claim Fields

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

## Chapter 4: Representations And World Models

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

### Ch4-Q3: Sample Cost, Fidelity, Provenance, And Coverage

Candidate titles:

1. How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?
2. Can sample metadata bound generalization in AI-driven architecture design?
3. When does an architecture sample justify transferring a design-space lesson?
4. What makes expensive architecture feedback reusable evidence rather than isolated measurement?
5. How should design loops price evidence across fidelity, coverage, and risk?
6. Can architecture agents learn when scarce samples stop transferring?

Recommended title: **How should costly architecture samples encode fidelity, provenance, coverage, and transfer limits?**

Rationale: This keeps sample cost inside the representation problem.

### Ch4-Q4: Novelty And Negative Evidence

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

### Ch5-Q3: Security And Isolation

Candidate titles:

1. Can AI-callable architecture environments enforce least-privilege contracts over tools, workloads, and proprietary state?
2. How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?
3. What security contract should govern AI agents that act through architecture toolchains?
4. Can environment harnesses expose enough design state while keeping proprietary state isolated?
5. How can architecture loops prove that tool calls are confined, auditable, and reversible before commitment?
6. What isolation boundary lets generative methods use industrial tool flows without leaking data or mutating trusted state?

Recommended title: **How should architecture environments isolate model actions from proprietary workloads, tool state, and irreversible side effects?**

Rationale: This keeps security inside the environment-contract framing.

### Ch5-Q4: Environment Drift And Maintenance

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

### Ch6-Q4: Novelty And Pareto Evidence

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

## Chapter 7: Feedback, Evidence, And Trust

Chapter role: bind feedback to evidence, evidence to claims, and claims to
trustworthy rejection and commitment boundaries.

### Ch7-Q1: Evidence Ledgers And Authorized Commitment

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

### Ch8-Q1: Prompt To Rejectable Loop Turn

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

### Ch8-Q4: Receipts, Under-Evidenced Leads, And Stale Rejections

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

### Ch9-Q1: Workload And Objective Transfer

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

### Ch9-Q2: Evidence And Escalation Transfer

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

### Ch10-Q3: Tacit Constraints And Ownership

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

### Ch10-Q4: Publication Standards And Infrastructure Incentives

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
