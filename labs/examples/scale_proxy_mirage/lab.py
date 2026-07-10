import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import sys
    import tempfile
    from datetime import datetime, timezone
    from pathlib import Path
    from textwrap import dedent

    import marimo as mo

    # Make arch2_labs importable when run from anywhere.
    LABS_ROOT = Path(__file__).resolve().parents[2]
    if str(LABS_ROOT) not in sys.path:
        sys.path.insert(0, str(LABS_ROOT))

    from arch2_labs.scale_env import run_example
    from arch2_labs.decisions import record_human_decision
    from arch2_labs.presentation import (
        render_objective_summary,
        render_receipt_validation,
    )
    from arch2_labs.validators import validate_receipt

    return (
        Path,
        datetime,
        dedent,
        json,
        mo,
        record_human_decision,
        render_objective_summary,
        render_receipt_validation,
        run_example,
        tempfile,
        timezone,
        validate_receipt,
    )


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

        **Name the measured mechanism (self-explanation).** The proxy divides by PE
        *count*, which silently assumes every PE does useful work. A 64×64 array on a
        workload with a 32-row layer leaves rows idle, so mapping and utilization make
        the measured speedup a fraction of the proxy's promise. The roofline label is a
        separate analytic warning derived from access counts and declared bandwidth.
        SCALE-Sim 3.0.0 does not model bandwidth stalls in this configuration, so the
        label is not evidence that memory stalls caused the measured cycle gap.
        """
    )
    return


@app.cell
def _(ledger, mo, render_objective_summary):
    mo.md(render_objective_summary(ledger))
    return


@app.cell
def _(ledger, mo):
    eligible = [
        outcome["candidate_id"]
        for outcome in ledger["candidate_outcomes"]
        if outcome["accepted"]
    ]
    objective = mo.ui.dropdown(
        options={
            "Minimize latency (take the fastest that fits the budget)": "latency_under_declared_gates",
            "Minimize energy per inference": "energy_under_declared_gates",
            "Maximize area efficiency (TOPS/mm²)": "area_efficiency_under_declared_gates",
        },
        label="**Commit.** Which objective governs this decision?",
    )
    choice = mo.ui.dropdown(
        options=eligible,
        label="**Human choice.** Which gate-passing candidate do you select?",
    )
    level = mo.ui.dropdown(
        options={
            "Advance to a next-fidelity study only": "next_fidelity_study",
            "Advance to RTL": "advance_to_rtl",
            "Ready for signoff / product": "ready_for_signoff",
        },
        label="**Commitment level**",
    )
    human_owner = mo.ui.text(
        placeholder="Your name or accountable review role",
        label="**Human decision owner** (required)",
    )
    rationale = mo.ui.text_area(
        placeholder="Why does this candidate fit the governing objective and evidence?",
        label="**Rationale** (required)",
        rows=2,
    )
    objective_override = mo.ui.checkbox(
        value=False,
        label="**Override objective winner**",
    )
    override_reason = mo.ui.text_area(
        placeholder="Why should another gate passer override the selected objective?",
        label="**Override reason** (required only for an override)",
        rows=2,
    )
    residual_risk = mo.ui.text_area(
        placeholder="What material uncertainty remains after this simulator run?",
        label="**Residual risk** (required)",
        rows=2,
    )
    would_overturn = mo.ui.text_area(
        placeholder="What new evidence would change your decision?",
        label="**Would overturn** (required)",
        rows=2,
    )
    submit = mo.ui.run_button(label="Record my human decision")
    mo.vstack(
        [
            objective,
            choice,
            level,
            human_owner,
            rationale,
            objective_override,
            override_reason,
            residual_risk,
            would_overturn,
            submit,
        ]
    )
    return (
        choice,
        human_owner,
        level,
        objective_override,
        objective,
        override_reason,
        rationale,
        residual_risk,
        submit,
        would_overturn,
    )


@app.cell
def _(
    choice,
    datetime,
    human_owner,
    level,
    ledger,
    mo,
    objective,
    objective_override,
    override_reason,
    rationale,
    receipt_dir,
    record_human_decision,
    render_receipt_validation,
    residual_risk,
    submit,
    timezone,
    validate_receipt,
    would_overturn,
):
    required = [
        objective.value,
        choice.value,
        level.value,
        human_owner.value.strip(),
        rationale.value.strip(),
        residual_risk.value.strip(),
        would_overturn.value.strip(),
    ]
    expected_candidate = (
        ledger["objective_rankings"].get(objective.value, {}).get("candidate_id")
        if objective.value
        else None
    )
    if not submit.value or not all(required):
        _out = mo.md(
            "*Complete every decision field and record your decision to finish.*"
        )
    elif level.value != "next_fidelity_study":
        _out = mo.md(
            "🛑 **Overclaim.** Proxy-plus-one-simulator evidence does not license an "
            "RTL, signoff, or product commitment. Lower the commitment level to match "
            "the evidence."
        )
    elif choice.value != expected_candidate and not objective_override.value:
        _out = mo.md(
            "🛑 **Objective mismatch.** Your candidate is not the gate-filtered winner "
            "for the selected objective. Choose that winner or record a justified override."
        )
    elif choice.value == expected_candidate and objective_override.value:
        _out = mo.md(
            "🛑 **Override not needed.** Your choice already matches the selected "
            "objective's gate-filtered winner."
        )
    elif objective_override.value and not override_reason.value.strip():
        _out = mo.md("🛑 **Override reason required.** Explain the human override.")
    else:
        try:
            record_human_decision(
                receipt_dir,
                {
                    "schema_version": "arch2-human-decision/v0.2",
                    "lab_id": "scale_proxy_mirage",
                    "human_owner": human_owner.value.strip(),
                    "authored_at": datetime.now(timezone.utc).isoformat(),
                    "selected_candidate_id": choice.value,
                    "governing_objective": objective.value,
                    "objective_override": objective_override.value,
                    "override_reason": override_reason.value.strip() or None,
                    "commitment_level": level.value,
                    "rationale": rationale.value.strip(),
                    "residual_risk": residual_risk.value.strip(),
                    "would_overturn": would_overturn.value.strip(),
                },
            )
            errors = validate_receipt(receipt_dir)
        except ValueError as exc:
            errors = [str(exc)]
        _out = mo.md(render_receipt_validation(errors))
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

    *SCALE-Sim 3.0.0 does not model bandwidth stalls in this configuration. This
    lab therefore teaches proxy overstatement through mapping/utilization and
    objective conflict. The roofline result is a separate analytic warning, not
    a causal explanation of the simulator's measured cycles.*
    """
        ).strip()
    )
    return


if __name__ == "__main__":
    app.run()
