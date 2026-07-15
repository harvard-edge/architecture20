# The Proxy Mirage: A Systolic Accelerator Loop

This example is the first executable Architecture 2.0 lab seed. Students start
with a broad accelerator-design prompt, then narrow it into a scoped study that
tests a cheap proxy against simulator evidence and a fixed silicon budget.

## What Students See

The workload is a compact XR-like GEMM slice. A simple proxy estimates each
candidate as total MACs divided by PE count. That proxy ranks the `64x64` array
first. SCALE-Sim, a Python systolic-array simulator, then runs each candidate
against the same topology and layout files. The stronger evidence shows the
proxy winner is genuinely fast, but the study excludes it because it exceeds the
declared 1024-PE mobile silicon budget. Utilization and roofline are kept as
diagnostics, not pass/fail rejection criteria.

The run archive separates the generator, simulator wrapper, rejection checks,
and decision owner. Automated checks can exclude candidates, but the final memo
still belongs to the declared owner.

## Run

```bash
cd labs
../.venv/bin/python -m arch2_labs.scale_env \
  --example scale_proxy_mirage \
  --out /tmp/arch2_proxy_mirage_run
# Inspect the evidence-bound draft before deciding.
../.venv/bin/python -m arch2_labs.decisions \
  /tmp/arch2_proxy_mirage_run \
  examples/scale_proxy_mirage/human_decision.example.yaml
../.venv/bin/python -m arch2_labs.validators /tmp/arch2_proxy_mirage_run
```

Inspect `recommendation.json`, `decision.yaml`, `decision.md`,
`negative_traces.jsonl`, and the per-candidate `runs/*/scalesim-results`
directories after the run. The checked-in decision is a course staff
reproducibility fixture. In the notebook, each learner supplies and persists
their own objective, candidate choice, rationale, residual risk, and overturn
condition.

The first command produces a schema 2.0 draft whose inspectability, disclosure,
and decision-right profiles are complete. Its replay profile is partial because
the original run's bindings are verified but a separate replay has not been
attempted. Its decision is still pending, so it does not create
`decision.yaml` or `decision.md`.
`arch2_labs.decisions` verifies every draft hash and record before writing the
separate decision and updating the card's `accountable_decision` status. It does
not claim independent review and will not revise a completed run archive. Lab-only
teaching state remains under `x-arch2-labs`.
