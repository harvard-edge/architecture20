# Design-Loop Card Examples

The four level-progression cards follow one unchanged accelerator-array study.
Read them in order to see the same intent and design-space boundary gain
additional records. Each level is cumulative and validates as a complete card
on its own.

| **Level** | **What the example adds** |
| --- | --- |
| **0, context** | Intent, task, and legal, invalid, and deferred design choices. |
| **1, auditable card** | Representation, environment, actor map, feedback budget, evidence, and a failed-run or rejected-alternative entry. |
| **2, replay bindings present** | Stable IDs, a workload and seed, tool version, parameter digest, and replay source. |
| **3, independence and decision fields present** | Claimed independent rejection authority, a commitment boundary, and a named accountable owner. |

Conformance level, evidence fidelity, and commitment are separate judgments. A
Level 3 card can still contain proxy evidence, as this example does. A stronger
commitment needs stronger evidence; it does not follow from the presence
of more fields. Disclosure and method autonomy are separate review constraints
too.

Schema validation proves that the required structure is present. It does not
prove that the evidence is adequate, the replay succeeds, or reviewers agree
with the claim or commitment.

Validate each example from the repository root.

```console
./arch2 validate card examples/design-loop-cards/level-0-context.yaml
./arch2 validate card examples/design-loop-cards/level-1-auditable.yaml
./arch2 validate card examples/design-loop-cards/level-2-replayable.yaml
./arch2 validate card examples/design-loop-cards/level-3-independent.yaml
```

The Level 2 and Level 3 cards point to complete replay packets under
`evidence/`. These packets are small teaching artifacts. They use a declared
deterministic array estimator and a synthetic layer set, not SCALE-Sim or a
published benchmark.

Verify every synthetic packet from a repository clone with only Python 3.

```console
cd examples/design-loop-cards
python3 replay.py verify-all
```

Each packet also declares its own render and verify commands. The render command
recomputes the recorded results, while the verify command checks the result and
all integrity bindings. The card's `parameter_hash` is the SHA-256 digest of the
packet's exposed `canonical_parameter_payload`. The packet separately binds the
workload file and replay implementation by their byte-level SHA-256 digests.

The estimator tiles each matrix layer over the declared array. Each tile costs
`k + array_rows + array_columns - 2` cycles, which exposes pipeline fill and
drain overhead. Utilization is useful multiply-accumulates divided by available
processing-element cycles. The model does not estimate memory stalls, timing,
energy, area, or physical design. The cards keep those outcomes outside their
claim boundaries.

## Next Step

These synthetic packets teach schema progression, provenance, and replay in a
small deterministic setting. They do not replace empirical lab work with
tool-produced evidence. Continue with the
[simulator-backed Architecture 2.0 labs](https://github.com/harvard-edge/arch2/tree/main/labs)
to generate evidence, inspect raw outputs, preserve failed runs and rejected
alternatives, and submit a runnable receipt for review.

The fixture progression and the real labs serve different teaching roles.
Neither replaces Chapter 8's constructed lighthouse example, which remains the
worked synthesis of the complete design loop.
