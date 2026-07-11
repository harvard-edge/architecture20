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
        # Lab 08 · Run One Complete Loop Turn · Chapter 8

        **You can, after this lab:** run one bounded loop turn, inspect its evidence
        and rejections, make an explicit objective-based decision, and export a
        complete receipt that another reviewer can validate.

        > **Recap.** A tool may recommend a candidate, but it does not own the
        > commitment. The receipt must keep objective rankings, machine
        > recommendation, declared rejections, and the human decision separate. A
        > different gate-passing choice requires an explicit, justified override.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "The simulator finishes and returns its fastest candidate.": "simulator",
            "Evidence and rejections are recorded, then a human owns a bounded decision and the completed receipt validates.": "right",
            "Every objective ranking names the same candidate.": "ranking",
        },
        label="**Warm-up.** When is this loop turn complete?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(
        warmup.value != "right",
        mo.md(
            "*Choose the answer that includes evidence, decision ownership, and validation.*"
        ),
    )
    mo.md("The receipt is complete only after the human decision is recorded.")
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked

    def validate_prediction(value):
        if value is None or value.get("choice") is None:
            return "Predict how many candidates pass both declared gates."
        if value.get("confidence") is None:
            return "Record your confidence."
        if not str(value.get("reason", "")).strip():
            return "Name which candidates or gates drive the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "choice": mo.ui.dropdown(
                options={str(value): value for value in range(5)},
                label="**Predict.** How many of the 8×8, 16×16, 32×32, and 64×64 candidates pass a 1024-PE budget and a 90,000-cycle deadline?",
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
                placeholder="Which candidate fails which gate?",
                rows=2,
            ),
        }
    ).form(
        submit_button_label="Lock my prediction",
        clear_on_submit=False,
        validate=validate_prediction,
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
    mo.md(
        f"Prediction locked at **{prediction_snapshot['confidence']}% confidence**. "
        "The receipt draft remains ungenerated until you run the turn."
    )
    return (prediction_snapshot,)


@app.cell
def _(mo, prediction_snapshot):
    assert prediction_snapshot
    run_button = mo.ui.run_button(label="Run the four-candidate loop turn")
    run_button
    return (run_button,)


@app.cell
def _(Path, json, mo, prediction_snapshot, run_button, run_example, tempfile):
    assert prediction_snapshot
    mo.stop(not run_button.value, mo.md("*Run the loop turn to reveal its evidence.*"))

    receipt_dir = Path(tempfile.mkdtemp(prefix="arch2_lab08_")) / "receipt"
    summary = run_example("scale_proxy_mirage", receipt_dir, force=True)
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
    run_snapshot = {
        "draft_status": summary["status"],
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
    survivor_count = len(run_snapshot["accepted_ids"])
    prediction_hit = prediction_snapshot["choice"] == survivor_count
    rejection_rows = [
        {
            "candidate": trace["candidate_id"],
            "gate": trace["gate"],
            "observed": trace["observed"],
            "threshold": trace["threshold"],
        }
        for trace in negative_traces
    ]
    mo.vstack(
        [
            mo.md(
                f"""
                ### Reconcile the Prediction

                **{survivor_count} candidates passed both gates.** You predicted
                **{prediction_snapshot['choice']}** at
                **{prediction_snapshot['confidence']}% confidence**.
                {"Your count matched." if prediction_hit else "Your count did not match; inspect the gate records below."}

                Your submitted reason was: *{prediction_snapshot['reason']}*
                """
            ),
            mo.ui.table(rejection_rows, selection=None),
            mo.md(render_objective_summary(ledger)),
            mo.md(
                f"The draft records `{run_snapshot['machine_recommendation']}` as a "
                "machine recommendation. That recommendation is not yet a human decision."
            ),
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
            return "Complete the human decision."
        required = [
            value.get("objective"),
            value.get("choice"),
            str(value.get("human_owner", "")).strip(),
            str(value.get("rationale", "")).strip(),
            str(value.get("residual_risk", "")).strip(),
            str(value.get("would_overturn", "")).strip(),
        ]
        if not all(required):
            return "Complete every required decision field."
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
            "objective": mo.ui.dropdown(
                options={
                    "Minimize latency under declared gates": "latency_under_declared_gates",
                    "Minimize first-order energy under declared gates": "energy_under_declared_gates",
                    "Maximize area efficiency under declared gates": "area_efficiency_under_declared_gates",
                },
                label="**Commit.** Which objective governs the decision?",
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
                placeholder="Connect the candidate choice to the governing objective and evidence.",
                rows=2,
            ),
            "objective_override": mo.ui.checkbox(
                value=False,
                label="**Override the governing objective's top-ranked candidate**",
            ),
            "override_reason": mo.ui.text_area(
                label="**Override reason** (required only for an override)",
                placeholder="Name the architect-owned reason for choosing another gate passer.",
                rows=2,
            ),
            "residual_risk": mo.ui.text_area(
                label="**Residual risk** (required)",
                placeholder="What material uncertainty remains after this simulator turn?",
                rows=2,
            ),
            "would_overturn": mo.ui.text_area(
                label="**Would overturn** (required)",
                placeholder="What stronger evidence would change this decision?",
                rows=2,
            ),
        }
    ).form(
        submit_button_label="Record my human decision",
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
        mo.md("*Submit the human decision to complete the receipt.*"),
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
        "activity_id": "lab_08_run_the_loop",
        "prediction": prediction_snapshot,
        "run_summary": run_snapshot,
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
                        "arch2-lab08-receipt/"
                        + path.relative_to(receipt_dir).as_posix()
                    ),
                )
    mo.vstack(
        [
            mo.md(
                "### Complete, Validated Receipt\n\n"
                "The ZIP contains the hash-sealed replay receipt and its manifest-bound "
                "Lab 08 activity record. The receipt keeps the machine recommendation "
                "and human decision separate."
            ),
            mo.download(
                data=archive_buffer.getvalue(),
                filename="arch2-lab08-complete-turn.zip",
                mimetype="application/zip",
                label="Download validated Lab 08 receipt",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** What is the smallest evidence or objective change that could alter your decision?",
        placeholder="Name the change and explain whether it changes a ranking, a gate, or the commitment boundary.",
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
        "**Activity complete.** One honest turn produced evidence, declared rejections, "
        "an owned commitment, and a validated receipt."
    )
    return


if __name__ == "__main__":
    app.run()
