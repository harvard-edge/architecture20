import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import io
    import json
    import sys
    import tempfile
    import zipfile
    from datetime import datetime, timezone
    from pathlib import Path
    from textwrap import dedent

    import marimo as mo

    labs_root = Path(__file__).resolve().parents[1]
    if str(labs_root) not in sys.path:
        sys.path.insert(0, str(labs_root))

    from arch2_labs.decisions import record_human_decision
    from arch2_labs.presentation import (
        render_objective_summary,
        render_receipt_validation,
    )
    from arch2_labs.receipts import attach_activity_record
    from arch2_labs.scale_env import run_example
    from arch2_labs.validators import validate_receipt

    return (
        Path,
        attach_activity_record,
        datetime,
        dedent,
        io,
        json,
        mo,
        record_human_decision,
        render_objective_summary,
        render_receipt_validation,
        run_example,
        tempfile,
        timezone,
        validate_receipt,
        zipfile,
    )


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        # Lab 09 · The Same Loop at Different Feedback Costs · Chapter 9

        **You can, after this lab:** allocate a small incremental evaluation budget,
        preserve a fixed comparison baseline, inspect where expensive runs were
        wasted, and complete a receipt without weakening its evidence invariants.

        > **Recap.** Expensive feedback changes the order of work. A declared
        > baseline remains mandatory for comparison, while cheap, validated gates can
        > screen incremental candidates before costly evaluation. A cheap filter is
        > useful only within its stated scope; it is not permission to discard
        > candidates silently.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "Spend the two-run budget on any two candidates and omit the baseline.": "omit",
            "Keep the baseline as a fixed calibration run, then allocate two incremental runs among the remaining candidates.": "right",
            "Run only the cheapest proxy and skip stronger evidence.": "proxy",
        },
        label="**Warm-up.** How should a two-run incremental budget treat the baseline?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(
        warmup.value != "right",
        mo.md("*Preserve the fixed baseline, then allocate the incremental budget.*"),
    )
    mo.md(
        "`balanced_16x16` is the required calibration run. Your budget controls two "
        "additional candidate runs."
    )
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked
    allocation_map = {
        "large_and_mid": ["proxy_hero_64x64", "throughput_32x32"],
        "large_and_tiny": ["proxy_hero_64x64", "tiny_8x8"],
        "mid_and_tiny": ["throughput_32x32", "tiny_8x8"],
    }

    def validate_prediction(value):
        if value is None or value.get("allocation") is None:
            return "Allocate both incremental runs."
        if value.get("choice") is None:
            return "Predict how many incremental candidates survive."
        if value.get("confidence") is None:
            return "Record your confidence."
        if not str(value.get("reason", "")).strip():
            return "Explain which cheap fact or stronger gate drives the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "allocation": mo.ui.dropdown(
                options={
                    "64×64 and 32×32": "large_and_mid",
                    "64×64 and 8×8": "large_and_tiny",
                    "32×32 and 8×8": "mid_and_tiny",
                },
                label="**Allocate.** Which two candidates receive the incremental simulator runs?",
            ),
            "choice": mo.ui.dropdown(
                options={"Neither survives": 0, "One survives": 1, "Both survive": 2},
                label="**Predict.** How many of those two incremental candidates pass both declared gates?",
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
                placeholder="Which known budget fact or simulator-dependent deadline matters?",
                rows=2,
            ),
        }
    ).form(
        submit_button_label="Lock allocation and prediction",
        clear_on_submit=False,
        validate=validate_prediction,
    )
    prediction_form
    return allocation_map, prediction_form


@app.cell
def _(mo, prediction_form):
    mo.stop(
        prediction_form.value is None,
        mo.md(
            "*Submit an allocation, prediction, confidence, and reason to continue.*"
        ),
    )
    prediction_snapshot = dict(prediction_form.value)
    mo.md(
        f"Allocation locked at **{prediction_snapshot['confidence']}% confidence**. "
        "The fixed baseline plus your two incremental candidates will now form one "
        "valid comparison packet."
    )
    return (prediction_snapshot,)


@app.cell
def _(mo, prediction_snapshot):
    assert prediction_snapshot
    run_button = mo.ui.run_button(label="Spend the two incremental simulator runs")
    run_button
    return (run_button,)


@app.cell
def _(
    Path,
    allocation_map,
    json,
    mo,
    prediction_snapshot,
    run_button,
    run_example,
    tempfile,
):
    assert prediction_snapshot
    mo.stop(not run_button.value, mo.md("*Run the selected comparison packet.*"))

    baseline_id = "balanced_16x16"
    incremental_ids = allocation_map[prediction_snapshot["allocation"]]
    selected_ids = {baseline_id, *incremental_ids}
    receipt_dir = Path(tempfile.mkdtemp(prefix="arch2_lab09_")) / "receipt"
    summary = run_example(
        "scale_proxy_mirage",
        receipt_dir,
        force=True,
        candidate_ids=selected_ids,
    )
    ledger = json.loads((receipt_dir / "evidence_ledger.json").read_text())
    negative_traces = [
        json.loads(line)
        for line in (receipt_dir / "negative_traces.jsonl").read_text().splitlines()
        if line.strip()
    ]
    accepted_ids = [
        outcome["candidate_id"]
        for outcome in ledger["candidate_outcomes"]
        if outcome["accepted"]
    ]
    incremental_survivors = [
        candidate_id for candidate_id in incremental_ids if candidate_id in accepted_ids
    ]
    run_snapshot = {
        "draft_status": summary["status"],
        "fixed_baseline": baseline_id,
        "incremental_candidates": incremental_ids,
        "incremental_survivors": incremental_survivors,
        "accepted_ids": accepted_ids,
        "rejected_ids": [trace["candidate_id"] for trace in negative_traces],
        "machine_recommendation": ledger["machine_recommendation"],
    }
    return ledger, negative_traces, receipt_dir, run_snapshot


@app.cell
def _(
    ledger,
    mo,
    negative_traces,
    prediction_snapshot,
    render_objective_summary,
    run_snapshot,
):
    actual_count = len(run_snapshot["incremental_survivors"])
    hit = prediction_snapshot["choice"] == actual_count
    rejection_rows = [
        {
            "candidate": trace["candidate_id"],
            "gate": trace["gate"],
            "observed": trace["observed"],
            "threshold": trace["threshold"],
        }
        for trace in negative_traces
    ]
    wasted = [
        candidate_id
        for candidate_id in run_snapshot["incremental_candidates"]
        if candidate_id in run_snapshot["rejected_ids"]
    ]
    cheap_screen_note = (
        "The 64×64 area violation was knowable before simulation. Its costly run could have been screened by the declared 1024-PE gate."
        if "proxy_hero_64x64" in wasted
        else "Your allocation did not spend a run on the already-known 64×64 area violation."
    )
    mo.vstack(
        [
            mo.md(
                f"""
                ### Reconcile the Budget

                The fixed baseline was `{run_snapshot['fixed_baseline']}`. Your two
                incremental runs were `{run_snapshot['incremental_candidates'][0]}` and
                `{run_snapshot['incremental_candidates'][1]}`. **{actual_count} of the two
                survived.** You predicted **{prediction_snapshot['choice']}** at
                **{prediction_snapshot['confidence']}% confidence**.
                {"Your prediction matched." if hit else "Your prediction did not match the declared gates."}

                Your submitted reason was: *{prediction_snapshot['reason']}*

                {cheap_screen_note}
                """
            ),
            mo.ui.table(rejection_rows, selection=None),
            mo.md(render_objective_summary(ledger)),
        ]
    )
    evidence_revealed = True
    return (evidence_revealed,)


@app.cell
def _(evidence_revealed, ledger, mo, run_snapshot):
    assert evidence_revealed
    eligible = run_snapshot["accepted_ids"]

    def validate_decision(value):
        if value is None:
            return "Complete the budget policy and human decision."
        required = [
            value.get("budget_policy"),
            value.get("objective"),
            value.get("choice"),
            str(value.get("human_owner", "")).strip(),
            str(value.get("rationale", "")).strip(),
            str(value.get("residual_risk", "")).strip(),
            str(value.get("would_overturn", "")).strip(),
        ]
        if not all(required):
            return "Complete every required field."
        if value["budget_policy"] != "baseline_then_screen":
            return (
                "Keep the fixed baseline and apply validated cheap gates before "
                "costly incremental runs."
            )
        expected = (
            ledger["objective_rankings"].get(value["objective"], {}).get("candidate_id")
        )
        if value["choice"] != expected and not value["objective_override"]:
            return "Record an explicit override when choosing another gate-passing candidate."
        if value["choice"] == expected and value["objective_override"]:
            return (
                "Do not mark an override when the choice matches the objective ranking."
            )
        if (
            value["objective_override"]
            and not str(value.get("override_reason", "")).strip()
        ):
            return "Explain the objective override."
        return None

    decision_form = mo.ui.dictionary(
        {
            "budget_policy": mo.ui.dropdown(
                options={
                    "Keep the fixed baseline, apply validated cheap gates before costly runs, and preserve every screened rejection.": "baseline_then_screen",
                    "Drop the baseline whenever feedback is expensive.": "drop_baseline",
                    "Trust the proxy and eliminate stronger evaluation.": "proxy_only",
                },
                label="**Commit.** Which feedback-budget policy will you carry forward?",
            ),
            "objective": mo.ui.dropdown(
                options={
                    "Minimize latency under declared gates": "latency_under_declared_gates",
                    "Minimize first-order energy under declared gates": "energy_under_declared_gates",
                    "Maximize area efficiency under declared gates": "area_efficiency_under_declared_gates",
                },
                label="**Governing objective**",
            ),
            "choice": mo.ui.dropdown(
                options=eligible,
                label="**Human choice.** Which gate-passing candidate advances?",
            ),
            "human_owner": mo.ui.text(
                label="**Human decision owner** (required)",
                placeholder="Your name or accountable review role",
            ),
            "rationale": mo.ui.text_area(
                label="**Rationale** (required)",
                placeholder="Explain the candidate choice and how the budget affected the evidence.",
                rows=2,
            ),
            "objective_override": mo.ui.checkbox(
                value=False,
                label="**Override the governing objective's top-ranked candidate**",
            ),
            "override_reason": mo.ui.text_area(
                label="**Override reason** (required only for an override)",
                placeholder="Why should another gate passer override the selected objective?",
                rows=2,
            ),
            "residual_risk": mo.ui.text_area(
                label="**Residual risk** (required)",
                placeholder="Which untested candidates or higher-fidelity effects still matter?",
                rows=2,
            ),
            "would_overturn": mo.ui.text_area(
                label="**Would overturn** (required)",
                placeholder="What new evidence or budget change would alter the decision?",
                rows=2,
            ),
        }
    ).form(
        submit_button_label="Record budget policy and human decision",
        clear_on_submit=False,
        validate=validate_decision,
    )
    decision_form
    return (decision_form,)


@app.cell
def _(
    datetime,
    decision_form,
    mo,
    receipt_dir,
    record_human_decision,
    render_receipt_validation,
    timezone,
    validate_receipt,
):
    mo.stop(
        decision_form.value is None,
        mo.md("*Submit the budget policy and human decision to complete the receipt.*"),
    )
    decision_snapshot = dict(decision_form.value)
    try:
        record_human_decision(
            receipt_dir,
            {
                "schema_version": "arch2-human-decision/v0.2",
                "lab_id": "scale_proxy_mirage",
                "human_owner": str(decision_snapshot["human_owner"]).strip(),
                "authored_at": datetime.now(timezone.utc).isoformat(),
                "selected_candidate_id": decision_snapshot["choice"],
                "governing_objective": decision_snapshot["objective"],
                "objective_override": decision_snapshot["objective_override"],
                "override_reason": str(
                    decision_snapshot.get("override_reason", "")
                ).strip()
                or None,
                "commitment_level": "next_fidelity_study",
                "rationale": str(decision_snapshot["rationale"]).strip(),
                "residual_risk": str(decision_snapshot["residual_risk"]).strip(),
                "would_overturn": str(decision_snapshot["would_overturn"]).strip(),
            },
        )
        receipt_errors = validate_receipt(receipt_dir)
    except ValueError as exc:
        receipt_errors = [str(exc)]
    mo.stop(receipt_errors, mo.md(render_receipt_validation(receipt_errors)))
    mo.md(render_receipt_validation([]))
    decision_complete = True
    return decision_complete, decision_snapshot


@app.cell
def _(
    attach_activity_record,
    decision_complete,
    decision_snapshot,
    io,
    json,
    mo,
    prediction_snapshot,
    receipt_dir,
    run_snapshot,
    validate_receipt,
    zipfile,
):
    assert decision_complete
    final_errors = validate_receipt(receipt_dir)
    mo.stop(final_errors, mo.md("*The completed receipt no longer validates.*"))

    learning_record = {
        "schema_version": "arch2-activity-record/v1",
        "activity_id": "lab_09_same_loop_different_costs",
        "prediction_and_allocation": prediction_snapshot,
        "run_summary": run_snapshot,
        "budget_policy": decision_snapshot["budget_policy"],
        "human_decision": decision_snapshot,
        "receipt_validation": "passed",
    }
    attach_activity_record(receipt_dir, learning_record)
    final_errors = validate_receipt(receipt_dir)
    mo.stop(final_errors, mo.md("*The activity-bound receipt does not validate.*"))

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(receipt_dir.rglob("*")):
            if path.is_file() and not path.is_symlink():
                archive.write(
                    path,
                    arcname=(
                        "arch2-lab09-receipt/"
                        + path.relative_to(receipt_dir).as_posix()
                    ),
                )
    mo.vstack(
        [
            mo.md(
                "### Complete Budgeted-Turn Receipt\n\n"
                "The ZIP preserves the fixed baseline, both incremental runs, declared "
                "rejections, objective rankings, human decision, and the manifest-bound "
                "Lab 09 activity record."
            ),
            mo.download(
                data=archive_buffer.getvalue(),
                filename="arch2-lab09-feedback-costs.zip",
                mimetype="application/zip",
                label="Download validated Lab 09 receipt",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** Which cheap gate in your own loop could move earlier without silently narrowing the search?",
        placeholder="Name the gate, its scope, and the evidence you would retain for screened candidates.",
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
    reflection_form
    return (reflection_form,)


@app.cell
def _(mo, reflection_form):
    mo.stop(
        reflection_form.value is None,
        mo.md("*Submit the reflection to finish the activity.*"),
    )
    mo.md(
        "**Activity complete.** You preserved a comparison baseline, allocated "
        "incremental feedback, recorded candidate rejections, committed to a "
        "cheap-first policy, and completed the receipt."
    )
    return


if __name__ == "__main__":
    app.run()
