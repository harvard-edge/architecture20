import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    from textwrap import dedent

    return dedent, mo


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        # Lab 02 · Measure the Scissors Gap  ·  Chapters 2 and 9

        **You can, after this lab:** compare the rate at which comparable proposals
        enter an adjudication stage with its trusted disposition capacity, estimate
        mean queue growth, and track evaluations to a fixed-quality target separately.

        > **Recap.** A stage becomes *rejection-bound* when admitted proposals arrive
        > faster than the loop can apply trusted dispositions. Faster raw generation
        > may raise that arrival rate. A better generator may instead reduce the
        > evaluations needed to reach a fixed-quality target, which is a different gain.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "Buy the fastest generator; more candidates is the goal.": "wrong",
            "Measure both rates, then lower admitted arrival or raise trusted disposition capacity; track evaluations to target separately.": "right",
            "Generation and rejection always scale together.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** If raw generation gets 100x cheaper, what should a team do next?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(warmup.value != "right", mo.md("🔒 *Match the recap to continue.*"))
    mo.md("✅ Right. Now put numbers on it.")
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        ## Arrival, service, and search effort

        Take illustrative anchors for one adjudication stage:

        - **Proposal arrival** `lambda_propose` = **100** comparable candidates admitted
          to the stage per week.
        - **Trusted disposition capacity** `mu_adjudicate` = **20** candidates settled
          per week through accept, reject, revise, waive, or escalate decisions.

        The ratio `rho = lambda_propose / mu_adjudicate` is **offered load**, not
        queue length. In this lab's constant mean-rate sketch, the queue grows only
        when `lambda_propose > mu_adjudicate`, at
        `max(0, lambda_propose - mu_adjudicate)` candidates per week. Actual queue
        length also depends on the initial backlog, elapsed time, arrival variability,
        and scheduling.

        **Evaluations-to-target** is a separate search-quality measure. A better
        generator can lower it without increasing adjudication capacity.
        """
        ).strip()
    )
    return


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked
    predict = mo.ui.radio(
        options={
            "The mean-rate queue grows.": "grow",
            "The mean-rate queue does not grow.": "stable",
        },
        label="**Predict.** Admitted arrival becomes 100x the reference and trusted disposition capacity becomes 3x. What happens?",
    )
    confidence = mo.ui.slider(0, 100, step=5, value=50, label="**Confidence** (%)")
    reason = mo.ui.text_area(
        label="**Reason** (required)", rows=2, placeholder="Why that direction?"
    )
    lock = mo.ui.run_button(label="🔒 Lock my prediction")
    mo.vstack([predict, confidence, reason, lock])
    return lock, predict, reason


@app.cell
def _(lock, mo, predict, reason):
    mo.stop(
        not lock.value or predict.value is None or not reason.value.strip(),
        mo.md("*Predict, give a reason, and lock.*"),
    )
    mo.md("Locked. Now move the blades yourself.")
    prediction_locked = True
    return (prediction_locked,)


@app.cell
def _(mo, prediction_locked):
    assert prediction_locked
    proposal_multiplier = mo.ui.slider(
        0.1,
        1000.0,
        step=0.1,
        value=100.0,
        label="**Admitted proposal-arrival multiplier** (x reference)",
    )
    adjudication_multiplier = mo.ui.slider(
        0.1,
        1000.0,
        step=0.1,
        value=3.0,
        label="**Trusted-adjudication capacity multiplier** (x reference)",
    )
    evaluations_pct = mo.ui.slider(
        10,
        200,
        step=5,
        value=100,
        label="**Evaluations to fixed-quality target** (% of reference; lower is better)",
    )
    mo.vstack([proposal_multiplier, adjudication_multiplier, evaluations_pct])
    return adjudication_multiplier, evaluations_pct, proposal_multiplier


@app.cell
def _(adjudication_multiplier, evaluations_pct, mo, proposal_multiplier):
    lambda0, mu0, evaluations0 = 100.0, 20.0, 100.0
    proposal_rate = lambda0 * proposal_multiplier.value
    adjudication_capacity = mu0 * adjudication_multiplier.value

    offered_load = proposal_rate / adjudication_capacity
    queue_growth = max(0.0, proposal_rate - adjudication_capacity)
    trusted_throughput = min(proposal_rate, adjudication_capacity)

    evaluations_to_target = evaluations0 * evaluations_pct.value / 100.0
    time_to_target = evaluations_to_target / trusted_throughput
    queue_added_by_target = queue_growth * time_to_target
    mo.md(
        f"""
        ### Constant mean-rate estimate

        | | **Arrival `lambda`** | **Capacity `mu`** | **Offered load `rho`** | **Mean queue growth** |
        | --- | --- | --- | --- | --- |
        | Reference | {lambda0:.0f}/wk | {mu0:.0f}/wk | {lambda0 / mu0:.1f} | {max(0.0, lambda0 - mu0):.0f}/wk |
        | Current controls | {proposal_rate:.0f}/wk | {adjudication_capacity:.0f}/wk | **{offered_load:.1f}** | **{queue_growth:.0f}/wk** |

        `rho` is offered load, not backlog. Under this constant-rate sketch, the
        queue adds about **{queue_growth:.0f} candidates per week**.

        Separately, the search uses **{evaluations_to_target:.0f} trusted evaluations**
        to reach the fixed-quality target. At **{trusted_throughput:.0f} trusted
        dispositions per week**, that is about **{time_to_target:.2f} weeks**, during
        which the mean-rate sketch adds about **{queue_added_by_target:.0f} queued
        candidates**. These are illustrative rates, not a finite steady-state queue.
        """
    )
    return (
        adjudication_capacity,
        evaluations_to_target,
        offered_load,
        proposal_rate,
        queue_growth,
    )


@app.cell
def _(
    adjudication_capacity,
    evaluations_to_target,
    mo,
    offered_load,
    predict,
    proposal_rate,
):
    queue_grows = proposal_rate > adjudication_capacity
    got_it = (predict.value == "grow" and queue_grows) or (
        predict.value == "stable" and not queue_grows
    )
    mo.md(
        f"""
        ### Reconcile

        You predicted the queue would **{ {"grow": "grow", "stable": "not grow"}.get(predict.value, "—")}**.
        The arithmetic says it **{"grows" if queue_grows else "does not grow"}** because
        arrival ({proposal_rate:.0f}/wk) {">" if queue_grows else "≤"} trusted disposition
        capacity ({adjudication_capacity:.0f}/wk).
        {"Your diagnosis matched the rates." if got_it else "The regime follows the absolute arrival and service rates, not a comparison of their multipliers."}

        **The mechanism.** `rho = {offered_load:.2f}` is offered load, not the number
        waiting. Lowering admitted arrival or raising trusted disposition capacity can
        stabilize this stage. Lowering the current **{evaluations_to_target:.0f}
        evaluations-to-target** can improve search efficiency without changing
        adjudication capacity.
        """
    )
    return


@app.cell
def _(mo, queue_growth):
    assert queue_growth >= 0
    invest = mo.ui.dropdown(
        options=[
            "Raise trusted-adjudication capacity",
            "Control admitted proposal arrival",
            "Improve proposal quality to lower evaluations-to-target",
            "Raise admitted proposal arrival",
        ],
        label="**Commit.** Which intervention matches the bottleneck you measured?",
    )
    invest
    return (invest,)


@app.cell
def _(adjudication_capacity, invest, mo, proposal_rate):
    mo.stop(invest.value is None, mo.md("*Choose where to invest.*"))
    if invest.value == "Raise trusted-adjudication capacity":
        _out = mo.md(
            "Raising trusted capacity can stabilize the stage when `mu_adjudicate >= lambda_propose`. The added checks still need validation and an explicit scope."
        )
    elif invest.value == "Control admitted proposal arrival":
        _out = mo.md(
            "Admission control can stabilize the stage when it brings `lambda_propose <= mu_adjudicate`. Validate the filter because dropping candidates can damage search quality."
        )
    elif invest.value == "Improve proposal quality to lower evaluations-to-target":
        _out = mo.md(
            "Better proposals can shorten time-to-target, but they do not raise `mu_adjudicate` or stop queue growth when admitted arrival still exceeds capacity."
        )
    else:
        _out = mo.md(
            f"Raising admitted arrival helps trusted throughput only while arrival remains below capacity. Here arrival is {proposal_rate:.0f}/wk and capacity is {adjudication_capacity:.0f}/wk, so more admitted proposals increase mean queue growth."
        )
    _out
    investment_committed = True
    return (investment_committed,)


@app.cell
def _(dedent, investment_committed, mo):
    assert investment_committed
    mo.md(
        dedent(
            """
        ### Reflect

        These rates are illustrative anchors, not measurements. Estimate comparable-unit
        proposal arrival, trusted disposition capacity, observed queue behavior, and
        evaluations to a fixed-quality target. If `lambda_propose <= mu_adjudicate`
        during a declared interval, this stage was not rejection-bound for that workload
        and protocol. That result rejects the local diagnosis; it does not falsify the
        book's broader framework or establish another stage's regime. Conversely,
        `lambda_propose > mu_adjudicate` diagnoses an adjudication bottleneck, not poor
        generator quality.
        """
        ).strip()
    )
    return


if __name__ == "__main__":
    app.run()
