# Recorded AI-Assisted SCALE-Sim Study

This example supplies the empirical study in Chapter 8. It records one model
interaction, compares it with a deterministic conventional heuristic at the
same domain-tool budget, evaluates every candidate with SCALE-Sim 3.0.0, tests
the proposed mechanism, and stops at an evidence-bounded recommendation.

The example is deliberately narrow. It does not establish that a model is
generally better at architecture search, that the three-layer GEMM slice
represents a complete XR application, or that any candidate is ready for RTL,
physical design, or product use.

## Frozen protocol

The preregistration in
[`context/pre_registration.yaml`](context/pre_registration.yaml) was frozen
before the model call or any study simulation. It declares:

- the three-layer XR-like GEMM slice and its transposed mechanism probe;
- the legal array dimensions, 1,024-PE budget, and 32x32 baseline;
- three model candidates and three conventional candidates, with four
  SCALE-Sim evaluations per arm after inserting the baseline;
- a deterministic aggregate-aspect-ratio heuristic fixed before the call;
- the local decision score, `cycles / (average utilization / 100)`;
- a 1 percent support margin; and
- a shared four-run mirrored/transposed mechanism test outside both arm
  budgets.

The exact model prompt, response schema, complete recorded response, and
public-safe provenance are in `context/` and `recorded/model/`. The recorded
call produced a valid response without repair. The runtime did not report a
currency cost, seed, temperature, or provider revision, so those values are
recorded as unavailable rather than inferred.

## Recorded outcome

All values below are computed by SCALE-Sim for the frozen inputs. They are not
measurements from silicon.

| Arm | Shape | Total cycles | Average layer utilization | Local score | Disposition |
| --- | ---: | ---: | ---: | ---: | --- |
| Model | 32x32 baseline | 13,917 | 41.196% | 33,782.40 | Tied best |
| Model | 16x64 | 13,917 | 41.196% | 33,782.40 | Tied best |
| Model | 8x128 | 19,405 | 29.704% | 65,327.45 | Dominated |
| Model | 32x16 | 25,277 | 45.438% | 55,629.61 | Dominated |
| Conventional | 32x32 baseline | 13,917 | 41.196% | 33,782.40 | Tied best |
| Conventional | 16x64 | 13,917 | 41.196% | 33,782.40 | Tied best |
| Conventional | 8x128 | 19,405 | 29.704% | 65,327.45 | Dominated |
| Conventional | 64x16 | 17,757 | 32.294% | 54,985.25 | Dominated |

The architecture-outcome claim is null at the preregistered margin because no
nonbaseline candidate improves on 32x32 by at least 1 percent. The
AI-contribution claim is a tie because both arms return the same best score at
the same four-run budget.

The model predicted that 16x64 would beat 64x16 on the original workload and
that the winner would reverse after transposing M and N. The first prediction
held by 38.56 percent on the local score. The transposed result did not reverse:
16x64 still won, by 7.57 percent. The proposed orientation mechanism is
therefore falsified under its own recorded criterion.

The machine-readable result in
[`recorded/reference/study_results.json`](recorded/reference/study_results.json)
retains the 32x32 baseline. The book-study decision remains a
separate record and may authorize no more than the evidence supports.

## Deterministic replay

From `labs/` in the documented Python 3.11 environment:

```bash
../.venv/bin/python -m arch2_labs.study validate-model
../.venv/bin/python -m arch2_labs.study verify-reference \
  --reference examples/ai_systolic_array_study/recorded/reference
../.venv/bin/python -m arch2_labs.study replay \
  --reference examples/ai_systolic_array_study/recorded/reference
```

Replay uses no network access or model credential. It reruns all twelve
SCALE-Sim evaluations and compares every stable input, raw summary report,
parsed result, and hash with the recorded reference.

SCALE-Sim also emits large per-layer access traces. Those deterministic
intermediates are regenerated during replay but are not archived. The fixture
retains each exact input plus `COMPUTE_REPORT.csv`, `BANDWIDTH_REPORT.csv`,
`DETAILED_ACCESS_REPORT.csv`, and `RUN_CONFIG.csv`, which support the reported
metrics and keep the reference compact.

## Optional live proposal

The live adapter is not part of deterministic replay and never overwrites the
recorded result. It accepts any local or remote command that reads the frozen
prompt from standard input and emits one schema-valid JSON object on standard
output.

```bash
export ARCH2_MODEL_COMMAND='your-model-command --json'
export ARCH2_MODEL_ID='exact-model-identifier'
export ARCH2_MODEL_PROVIDER='provider-or-local-runtime'
../.venv/bin/python -m arch2_labs.study_live --out /tmp/arch2-live-proposal
```

For a runtime that needs a credential, set
`ARCH2_MODEL_REQUIRED_CREDENTIAL` to the *name* of its credential environment
variable. The adapter verifies that the variable exists but never records its
value. Missing runtime, model identity, credential, invalid JSON, invalid
geometry, and schema failures stop safely without modifying the recorded
reference.
