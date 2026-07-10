# The Proxy Mirage: A Systolic Accelerator Loop

This example is the first executable Architecture 2.0 lab seed. Students start
with a broad accelerator-design prompt, then narrow it into a bounded loop that
can reject its own cheap proxy.

## What Students See

The workload is a compact XR-like GEMM slice. A simple proxy estimates each
candidate as total MACs divided by PE count. That proxy ranks the `64x64` array
first. SCALE-Sim, a Python systolic-array simulator, then runs each candidate
against the same topology and layout files. The stronger evidence shows the
proxy winner is genuinely fast, but the loop rejects it because it exceeds the
declared 1024-PE mobile silicon budget. Utilization and roofline are kept as
diagnostics, not hidden hard gates.

The receipt makes the split between agent, environment, rejector, and human
owner concrete. The environment can reject candidates, but the final memo still
belongs to the human.

## Run

```bash
cd labs
../.venv/bin/python -m arch2_labs.scale_env \
  --example scale_proxy_mirage \
  --out /tmp/arch2_proxy_mirage_receipt \
  --decision-file examples/scale_proxy_mirage/human_decision.example.yaml \
  --force
../.venv/bin/python -m arch2_labs.validators /tmp/arch2_proxy_mirage_receipt
```

Inspect `recommendation.json`, `decision.yaml`, `decision.md`,
`negative_traces.jsonl`, and the per-candidate `runs/*/scalesim-results`
directories after the run. The checked-in decision is a course staff
reproducibility fixture. In the notebook, each learner supplies and persists
their own objective, candidate choice, rationale, residual risk, and overturn
condition.

Running without `--decision-file` produces a Level 2 evidence draft. It does not
create `decision.yaml` or `decision.md`, and the validator reports that a human
decision is still required. A valid completed receipt upgrades the canonical
card to Level 3 and keeps lab-only teaching state under `x-arch2-labs`.
