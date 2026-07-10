# Design-Loop Card Examples

The Level 2 and Level 3 cards point to complete replay packets under
`evidence/`. These packets are small teaching artifacts. They use a declared
deterministic array estimator and a synthetic layer set, not SCALE-Sim or a
published benchmark.

Run every packet from a repository clone with only Python 3.

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
