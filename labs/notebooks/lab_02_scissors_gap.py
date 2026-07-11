import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import marimo as mo
    from textwrap import dedent

    return dedent, json, mo


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        # Lab 02 · Measure the Scissors Gap · Chapter 2

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
def _(dedent, mo, warmup_unlocked):
    assert warmup_unlocked
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
    brief_ready = True
    return (brief_ready,)


@app.cell
def _(brief_ready, mo):
    assert brief_ready

    def _validate_prediction(value):
        if value is None or value.get("prediction") is None:
            return "Select whether the mean-rate queue grows."
        if value.get("confidence") is None:
            return "Record your confidence before locking the prediction."
        if not str(value.get("reason", "")).strip():
            return "Give one reason for the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "prediction": mo.ui.radio(
                options={
                    "The mean-rate queue grows.": "grow",
                    "The mean-rate queue does not grow.": "stable",
                },
                label="**Predict.** Arrival becomes 100x the reference and trusted capacity becomes 3x. What happens?",
            ),
            "confidence": mo.ui.dropdown(
                options={
                    "Low (25%)": 25,
                    "Medium (50%)": 50,
                    "High (75%)": 75,
                    "Very high (100%)": 100,
                },
                label="**Confidence** (required)",
            ),
            "reason": mo.ui.text_area(
                label="**Reason** (required)",
                rows=2,
                placeholder="Why that direction?",
            ),
        }
    ).form(
        submit_button_label="Lock my prediction",
        clear_on_submit=False,
        validate=_validate_prediction,
    )
    prediction_form
    return (prediction_form,)


@app.cell
def _(mo, prediction_form):
    mo.stop(
        prediction_form.value is None,
        mo.md("*Submit a prediction, confidence, and reason to continue.*"),
    )
    prediction_snapshot = dict(prediction_form.value)
    prediction_locked = True
    mo.md(
        f"Prediction locked at **{prediction_snapshot['confidence']}% confidence**. "
        "Now move the blades yourself."
    )
    return prediction_locked, prediction_snapshot


@app.cell
def _(mo, prediction_locked, prediction_snapshot):
    assert prediction_locked and prediction_snapshot
    scenario_form = mo.ui.dictionary(
        {
            "proposal_multiplier": mo.ui.slider(
                0.1,
                1000.0,
                step=0.1,
                value=100.0,
                label="**Admitted proposal-arrival multiplier** (x reference)",
            ),
            "adjudication_multiplier": mo.ui.slider(
                0.1,
                1000.0,
                step=0.1,
                value=3.0,
                label="**Trusted-adjudication capacity multiplier** (x reference)",
            ),
            "evaluations_pct": mo.ui.slider(
                10,
                200,
                step=5,
                value=100,
                label="**Evaluations to fixed-quality target** (% of reference; lower is better)",
            ),
        }
    ).form(
        submit_button_label="Apply rates and reveal estimate",
        clear_on_submit=False,
    )
    scenario_form
    return (scenario_form,)


@app.cell
def _(mo, scenario_form):
    mo.stop(
        scenario_form.value is None,
        mo.md("*Set the rates and submit them to reveal the estimate.*"),
    )
    scenario_snapshot = dict(scenario_form.value)
    lambda0, mu0, evaluations0 = 100.0, 20.0, 100.0
    proposal_rate = lambda0 * float(scenario_snapshot["proposal_multiplier"])
    adjudication_capacity = mu0 * float(scenario_snapshot["adjudication_multiplier"])

    offered_load = proposal_rate / adjudication_capacity
    queue_growth = max(0.0, proposal_rate - adjudication_capacity)
    trusted_throughput = min(proposal_rate, adjudication_capacity)

    evaluations_to_target = (
        evaluations0 * float(scenario_snapshot["evaluations_pct"]) / 100.0
    )
    time_to_target = evaluations_to_target / trusted_throughput
    queue_added_by_target = queue_growth * time_to_target
    diagnosis_snapshot = {
        "reference": {
            "proposal_arrival_per_week": lambda0,
            "trusted_disposition_capacity_per_week": mu0,
            "evaluations_to_target": evaluations0,
        },
        "submitted_scenario": scenario_snapshot,
        "result": {
            "proposal_arrival_per_week": proposal_rate,
            "trusted_disposition_capacity_per_week": adjudication_capacity,
            "offered_load": offered_load,
            "mean_queue_growth_per_week": queue_growth,
            "trusted_throughput_per_week": trusted_throughput,
            "evaluations_to_target": evaluations_to_target,
            "time_to_target_weeks": time_to_target,
            "queue_added_by_target": queue_added_by_target,
        },
    }
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
    estimate_revealed = True
    return (
        adjudication_capacity,
        diagnosis_snapshot,
        estimate_revealed,
        evaluations_to_target,
        offered_load,
        proposal_rate,
        queue_growth,
    )


@app.cell
def _(
    adjudication_capacity,
    estimate_revealed,
    evaluations_to_target,
    mo,
    offered_load,
    prediction_snapshot,
    proposal_rate,
):
    assert estimate_revealed
    predicted = prediction_snapshot["prediction"]
    queue_grows = proposal_rate > adjudication_capacity
    got_it = (predicted == "grow" and queue_grows) or (
        predicted == "stable" and not queue_grows
    )
    mo.md(
        f"""
        ### Reconcile

        You predicted the queue would **{ {"grow": "grow", "stable": "not grow"}[predicted]}**
        at **{prediction_snapshot['confidence']}% confidence**. Your submitted reason was:
        *{prediction_snapshot['reason']}*

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
    reconciliation_complete = True
    return (reconciliation_complete,)


@app.cell
def _(mo, reconciliation_complete):
    assert reconciliation_complete

    def _validate_investment(value):
        if value is None:
            return "Choose the intervention you would fund."
        return None

    investment_form = mo.ui.dropdown(
        options=[
            "Raise trusted-adjudication capacity",
            "Control admitted proposal arrival",
            "Improve proposal quality to lower evaluations-to-target",
            "Raise admitted proposal arrival",
        ],
        label="**Commit.** Which intervention matches the bottleneck you measured?",
    ).form(
        submit_button_label="Record intervention",
        clear_on_submit=False,
        validate=_validate_investment,
    )
    investment_form
    return (investment_form,)


@app.cell
def _(adjudication_capacity, investment_form, mo, proposal_rate):
    mo.stop(
        investment_form.value is None,
        mo.md("*Choose and submit where to invest.*"),
    )
    investment_snapshot = investment_form.value
    if investment_snapshot == "Raise trusted-adjudication capacity":
        _out = mo.md(
            "Raising trusted capacity can stabilize the stage when `mu_adjudicate >= lambda_propose`. The added checks still need validation and an explicit scope."
        )
    elif investment_snapshot == "Control admitted proposal arrival":
        _out = mo.md(
            "Admission control can stabilize the stage when it brings `lambda_propose <= mu_adjudicate`. Validate the filter because dropping candidates can damage search quality."
        )
    elif (
        investment_snapshot == "Improve proposal quality to lower evaluations-to-target"
    ):
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
def _(
    diagnosis_snapshot,
    investment_form,
    investment_committed,
    json,
    mo,
    prediction_snapshot,
):
    assert investment_committed
    intervention_snapshot = investment_form.value
    assert intervention_snapshot is not None
    learning_record = {
        "schema_version": "arch2-learning-record/v1",
        "activity_id": "lab_02_scissors_gap",
        "chapter": 2,
        "prediction": prediction_snapshot,
        "diagnosis": diagnosis_snapshot,
        "human_intervention": intervention_snapshot,
        "scope": {
            "supports": "A constant mean-rate diagnosis for the submitted stage and interval assumptions.",
            "does_not_support": "A stochastic queue model, another stage's regime, or a general verdict on generator quality.",
        },
    }
    record_bytes = (
        json.dumps(learning_record, indent=2, sort_keys=True) + "\n"
    ).encode()
    mo.vstack(
        [
            mo.md(
                "### Learning record\n\n"
                "The JSON binds your submitted prediction, rate scenario, computed "
                "diagnosis, and chosen intervention."
            ),
            mo.download(
                data=record_bytes,
                filename="arch2-lab02-scissors-gap.json",
                mimetype="application/json",
                label="Download Lab 02 learning record",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, dedent, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** What rates and interval would you measure in your own design process?",
        placeholder="Name a comparable proposal unit, a trusted disposition, and an observation interval.",
        rows=3,
    ).form(
        submit_button_label="Record reflection",
        clear_on_submit=False,
        validate=lambda value: (
            None
            if value is not None and str(value).strip()
            else "Write one reflection."
        ),
    )
    mo.vstack(
        [
            mo.md(
                dedent(
                    """
                ### Reflect

                These rates are illustrative anchors, not measurements. Estimate
                comparable-unit proposal arrival, trusted disposition capacity,
                observed queue behavior, and evaluations to a fixed-quality target. If
                `lambda_propose <= mu_adjudicate` during a declared interval, this stage
                was not rejection-bound for that workload and protocol. That result
                rejects the local diagnosis; it does not falsify the book's broader
                framework or establish another stage's regime. Conversely,
                `lambda_propose > mu_adjudicate` diagnoses an adjudication bottleneck,
                not poor generator quality.
                """
                ).strip()
            ),
            reflection_form,
        ]
    )
    return (reflection_form,)


@app.cell
def _(mo, reflection_form):
    mo.stop(
        reflection_form.value is None,
        mo.md("*Submit the reflection to finish the activity.*"),
    )
    mo.md(
        "✅ **Activity complete.** The prediction, rate scenario, intervention, and reflection were submitted in order."
    )
    return


if __name__ == "__main__":
    app.run()
