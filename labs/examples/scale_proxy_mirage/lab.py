import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import sys
    import tempfile
    from pathlib import Path
    from textwrap import dedent

    import marimo as mo

    # Make arch2_labs importable when run from anywhere.
    LABS_ROOT = Path(__file__).resolve().parents[2]
    if str(LABS_ROOT) not in sys.path:
        sys.path.insert(0, str(LABS_ROOT))

    from arch2_labs.scale_env import run_example
    from arch2_labs.validators import validate_receipt

    return Path, dedent, json, mo, run_example, tempfile, validate_receipt


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
    # Lab: Proxy vs Evidence — the Cheap-Model Trap

    **You can, after this lab:** predict what a cheap proxy will say, run a real
    simulator, measure how far the proxy *overstated* the winner, name the
    mechanism behind the gap, and commit to a decision that states its governing
    objective.

    > **Architecture 2.0 recap.** A method's job inside the loop is a *role*:
    > generate, **predict**, optimize, critique. A cheap predictor (proxy) can
    > rank candidates fast, but its score is only a proxy. A loop is
    > *rejection-bound*: the scarce work is deciding which ranking to believe
    > before you commit.
    """
        ).strip()
    )
    return


@app.cell
def _(mo):
    retrieval = mo.ui.radio(
        options={
            "It is the final evidence; if it ranks a design first, ship it.": "wrong1",
            "It is a fast estimate whose ranking must be checked by stronger evidence before commitment.": "right",
            "It is only useful for energy, never for latency.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** What is a cheap proxy in an Architecture 2.0 loop?",
    )
    retrieval
    return (retrieval,)


@app.cell
def _(mo, retrieval):
    mo.stop(
        retrieval.value != "right",
        mo.md("🔒 *Pick the answer that matches the recap to continue.*"),
    )
    mo.md("✅ Right. A proxy ranks; it does not commit. Keep going.")
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
    ## The loop brief

    - **Claim.** One accelerator configuration is worth advancing to a stronger
      study for this XR-like GEMM slice.
    - **Design space.** A systolic array of 8×8, 16×16, 32×32, or 64×64 PEs.
    - **Cheap proxy.** total MACs ÷ PE count (nominal throughput). It ranks the
      **64×64** first and implies it is **16× faster** than the 16×16.
    - **Stronger evidence.** SCALE-Sim: real cycles, utilization, memory traffic.
    - **Commitment boundary.** Advance to a next-fidelity study only. No RTL,
      signoff, or product claim.
    """
        ).strip()
    )
    return


@app.cell
def _(mo):
    predicted = mo.ui.dropdown(
        options=[
            "About 16× (the proxy is right)",
            "About 10–13× (a little less)",
            "About 6–8× (much less than promised)",
            "Under 2× (the proxy is badly wrong)",
        ],
        label="**Predict.** The proxy says the 64×64 is 16× faster than the 16×16. What will SCALE-Sim measure?",
    )
    confidence = mo.ui.slider(
        start=0, stop=100, step=5, value=50, label="**Confidence** (%)"
    )
    reason = mo.ui.text_area(
        placeholder="One sentence: what mechanism might make the real speedup differ from 16×?",
        label="**Reason** (required)",
        rows=2,
    )
    lock = mo.ui.run_button(label="🔒 Lock my prediction")
    mo.vstack([predicted, confidence, reason, lock])
    return lock, predicted, reason


@app.cell
def _(lock, mo, reason):
    mo.stop(
        not lock.value or not reason.value.strip(),
        mo.md(
            "*Make a prediction, give a reason, and click **Lock** to reveal the evidence.*"
        ),
    )
    mo.md("Prediction locked. Now run the real simulator.")
    return


@app.cell
def _(mo):
    run = mo.ui.run_button(label="▶ Run SCALE-Sim on all four arrays")
    run
    return (run,)


@app.cell
def _(Path, json, mo, run, run_example, tempfile):
    mo.stop(not run.value, mo.md("*Click **Run** to execute the simulator.*"))

    _out = Path(tempfile.mkdtemp(prefix="arch2_proxy_")) / "receipt"
    summary = run_example("scale_proxy_mirage", _out, force=True)

    runs = [
        json.loads(l)
        for l in (_out / "runs.jsonl").read_text().splitlines()
        if l.strip()
    ]
    proxy_rows = {r["candidate_id"]: r for r in runs if r.get("stage") == "proxy"}
    sim_rows = {
        r["candidate_id"]: r
        for r in runs
        if r.get("stage") == "scalesim" and r.get("status") == "ok"
    }
    ledger = json.loads((_out / "evidence_ledger.json").read_text())
    receipt_dir = _out
    mo.md(f"Ran {len(sim_rows)} candidates. Receipt at `{receipt_dir}`.")
    return ledger, proxy_rows, receipt_dir, sim_rows


@app.cell
def _(mo, proxy_rows, sim_rows):
    def _fmt():
        order = ["proxy_hero_64x64", "throughput_32x32", "balanced_16x16", "tiny_8x8"]
        rows = []
        for cid in order:
            if cid not in sim_rows:
                continue
            m = sim_rows[cid]["metrics"]
            e = sim_rows[cid]["estimates"]
            rows.append(
                {
                    "candidate": cid,
                    "proxy_cycles": proxy_rows[cid]["proxy_cycles"],
                    "sim_cycles": m["total_cycles"],
                    "min_util_%": round(m["min_layer_util_pct"], 1),
                    "energy_uJ": e["energy"]["e_total_uj"],
                    "roofline": e["roofline"]["bound"],
                }
            )
        return rows

    big = next(r for r in _fmt() if r["candidate"] == "proxy_hero_64x64")
    small = next(r for r in _fmt() if r["candidate"] == "balanced_16x16")
    proxy_ratio = round(small["proxy_cycles"] / big["proxy_cycles"], 1)
    real_ratio = round(small["sim_cycles"] / big["sim_cycles"], 1)

    mo.vstack(
        [
            mo.md("### The evidence"),
            mo.ui.table(_fmt(), selection=None),
            mo.md(
                f"**Proxy promised {proxy_ratio}× speedup for the 64×64. "
                f"SCALE-Sim measured {real_ratio}×.** The proxy overstated by "
                f"~{round(proxy_ratio / real_ratio, 1)}×."
            ),
        ]
    )
    return (real_ratio,)


@app.cell
def _(mo, predicted, real_ratio):
    # Calibration feedback: score the mental model, not just the number.
    picked = predicted.value or ""
    close = "6–8×" in picked
    mo.md(
        f"""
        ### Reconcile the surprise

        You predicted **{picked or "—"}**; the truth is about **{real_ratio}×**.
        {"You had the right instinct." if close else "The realized speedup is far below the proxy's promise."}

        **Name the mechanism (self-explanation).** The proxy divides by PE *count*,
        which silently assumes every PE does useful work. A 64×64 array on a workload
        with a 32-row layer leaves most rows idle, so utilization collapses and the
        realized speedup is a fraction of the promised one. The roofline column shows
        the 64×64 is **memory-bound** here: its extra PEs cannot be fed, so they cannot
        pay off.
        """
    )
    return


@app.cell
def _(ledger, mo):
    obj = ledger["objective_rankings"]
    mo.md(
        f"""
        ### No single metric owns the commitment

        The 64×64 wins **latency** (`{obj['min_latency_us']['candidate_id']}`),
        **energy** (`{obj['min_energy_uj']['candidate_id']}`), and
        **EDP** (`{obj['min_edp']['candidate_id']}`). It loses only on the stated
        **silicon budget** (it needs 4096 PEs against a 1024-PE budget), so the loop's
        hard gates reject it on *cost* and the survivor is
        **`{obj['gate_survivor']}`** — the best design you can actually afford.

        The proxy was not simply wrong; it overstated the prize *and* was blind to the
        budget. Before you name a winner you must state which objective governs.
        """
    )
    return


@app.cell
def _(mo):
    objective = mo.ui.dropdown(
        options=[
            "Minimize latency (take the fastest that fits the budget)",
            "Minimize energy per inference",
            "Maximize area efficiency (TOPS/mm²)",
        ],
        label="**Commit.** Which objective governs this decision?",
    )
    level = mo.ui.dropdown(
        options=[
            "Advance to a next-fidelity study only",
            "Advance to RTL",
            "Ready for signoff / product",
        ],
        label="**Commitment level**",
    )
    rationale = mo.ui.text_area(
        placeholder="Optional: one line on what evidence would overturn this decision.",
        label="Rationale (optional)",
        rows=2,
    )
    mo.vstack([objective, level, rationale])
    return level, objective


@app.cell
def _(level, mo, objective, receipt_dir, validate_receipt):
    if objective.value is None or level.value is None:
        _out = mo.md("*Choose a governing objective and a commitment level to finish.*")
    elif level.value != "Advance to a next-fidelity study only":
        _out = mo.md(
            "🛑 **Overclaim.** Proxy-plus-one-simulator evidence does not license an "
            "RTL, signoff, or product commitment. Lower the commitment level to match "
            "the evidence."
        )
    else:
        errors = validate_receipt(receipt_dir)
        _out = mo.md(
            "✅ **Receipt valid.** Your loop turn is auditable: card, environment, "
            "evidence ledger, negative traces, and decision are all present, and the "
            f"decision cites the simulator, not the proxy.\n\nValidator: `{errors or 'ok'}`."
        )
    _out
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
    ### Reflect

    The workload had a 32-row layer. If every layer were 64 rows or larger, would
    the 64×64's utilization gap close, and would the proxy's overstatement shrink?
    What is the *smallest* change to the brief (workload, budget, or objective)
    that would flip the survivor?

    *SCALE-Sim v2 idealizes memory (it does not stall on bandwidth). This lab
    therefore teaches proxy overstatement and objective conflict, not memory
    stalls. A later lab red-teams that idealization directly.*
    """
        ).strip()
    )
    return


if __name__ == "__main__":
    app.run()
