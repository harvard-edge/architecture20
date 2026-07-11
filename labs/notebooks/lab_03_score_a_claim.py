import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    from textwrap import dedent

    import marimo as mo

    return dedent, json, mo


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            r"""
        # Lab 03 | Score a Claim | Chapter 3 (The Framework)

        **You can, after this lab:** audit an architecture claim for reviewability,
        locate missing loop fields, and record the strongest status its public record
        supports.

        > **Recap.** A reviewable architectural claim exposes its workload, any applicable
        > comparison baseline, evidence, rejection condition, and commitment boundary. Missing fields do not
        > make a result false. They make the claim underspecified and limit what a reviewer
        > can authorize from the record as stated.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "The claim with the largest reported speedup.": "wrong",
            "The claim whose record exposes its support and how it could be rejected.": "right",
            "The claim published in the strongest venue.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** Which claim is more reviewable?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(warmup.value != "right", mo.md("Locked. Match the recap to continue."))
    mo.md("Reviewability is a property of the exposed record. Now audit three claims.")
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked
    claims = {
        "Claim A": (
            "The 32x32 array advances to a next-fidelity study for the XRBench slice. "
            "SCALE-Sim cycles meet the 90,000-cycle deadline and the array fits the "
            "1,024-PE budget. A fuller workload missing the deadline or stronger power "
            "evidence exceeding the envelope would overturn this decision."
        ),
        "Claim B": "Our accelerator is 3x faster than the baseline.",
        "Claim C": "This design is optimal for mobile XR.",
    }
    mo.md(
        "## Three claims\n\n"
        + "\n".join(f"- **{name}.** *{text}*" for name, text in claims.items())
    )
    claims_ready = True
    return claims, claims_ready


@app.cell
def _(claims_ready, mo):
    assert claims_ready

    def _validate_prediction(value):
        if value is None or value.get("claim") is None:
            return "Select the claim you predict is most reviewable."
        if value.get("confidence") is None:
            return "Record your confidence before locking the prediction."
        if not str(value.get("reason", "")).strip():
            return "Give one reason for the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "claim": mo.ui.dropdown(
                options=["Claim A", "Claim B", "Claim C"],
                label="**Predict.** Which claim is most reviewable as stated?",
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
                placeholder="Which exposed or missing field drives your prediction?",
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
        mo.md("Submit a claim, confidence, and reason to reveal the audit."),
    )
    prediction_snapshot = dict(prediction_form.value)
    mo.md(f"Prediction locked at **{prediction_snapshot['confidence']}% confidence**.")
    return (prediction_snapshot,)


@app.cell
def _(claims, mo, prediction_snapshot):
    audit = {
        "Claim A": {
            "status": "reviewable for a next-fidelity-study commitment",
            "present": [
                "workload slice",
                "measured evidence",
                "hard constraints",
                "would-overturn condition",
            ],
            "missing_or_bounded": ["power evidence", "full-workload coverage"],
        },
        "Claim B": {
            "status": "not reviewable as stated",
            "present": ["comparative performance assertion"],
            "missing_or_bounded": [
                "identified baseline",
                "workload",
                "metric and protocol",
                "evidence",
                "rejection condition",
            ],
        },
        "Claim C": {
            "status": "not reviewable as stated",
            "present": ["broad optimality assertion"],
            "missing_or_bounded": [
                "bounded design space",
                "objective",
                "comparison set",
                "evidence",
                "would-overturn condition",
            ],
        },
    }
    picked_a = prediction_snapshot["claim"] == "Claim A"
    mo.md(
        f"""
        ### Audit reveal

        **Claim A is the most reviewable as stated.** It exposes a scoped workload,
        constraints, evidence, a bounded commitment, and conditions that would overturn
        the decision. {"Your prediction matched that record." if picked_a else "The reviewable claim is the one whose exposed fields let a reviewer limit or reject it."}

        **Claims B and C are not reviewable as stated.** They may become reviewable after
        their missing fields are supplied. This audit does not conclude that either claim
        is false, meaningless, or incapable of future support.

        | **Claim** | **Status** | **Missing or bounded fields** |
        | --- | --- | --- |
        | A | {audit['Claim A']['status']} | {', '.join(audit['Claim A']['missing_or_bounded'])} |
        | B | {audit['Claim B']['status']} | {', '.join(audit['Claim B']['missing_or_bounded'])} |
        | C | {audit['Claim C']['status']} | {', '.join(audit['Claim C']['missing_or_bounded'])} |
        """
    )
    audit_revealed = True
    return audit, audit_revealed


@app.cell
def _(audit_revealed, mo):
    assert audit_revealed

    def _validate_commitment(value):
        if value is None:
            return "Choose the status the current record supports."
        return None

    commitment_form = mo.ui.dropdown(
        options=[
            "Claim B is not reviewable as stated; request its baseline, workload, protocol, evidence, and rejection condition.",
            "Claim B is false because its record is incomplete.",
            "Claim B is ready for an implementation commitment.",
        ],
        label="**Commit.** What review status should Claim B receive?",
    ).form(
        submit_button_label="Record review status",
        clear_on_submit=False,
        validate=_validate_commitment,
    )
    commitment_form
    return (commitment_form,)


@app.cell
def _(commitment_form, mo):
    mo.stop(
        commitment_form.value is None,
        mo.md("Choose and submit a review status."),
    )
    mo.stop(
        not commitment_form.value.startswith("Claim B is not reviewable as stated"),
        mo.md(
            "That status overreaches the record. Missing support limits reviewability; "
            "it does not prove falsity or authorize implementation."
        ),
    )
    commitment_snapshot = commitment_form.value
    mo.md(
        "Review status recorded without turning missing evidence into a verdict of falsehood."
    )
    return (commitment_snapshot,)


@app.cell
def _(audit, claims, commitment_snapshot, json, mo, prediction_snapshot):
    audit_record = {
        "schema_version": "arch2-claim-audit/v0.1",
        "lab_id": "lab_03_score_a_claim",
        "prediction": prediction_snapshot,
        "claims": claims,
        "audit": audit,
        "review_commitment": commitment_snapshot,
        "limits": [
            "This record audits the supplied claim text, not the underlying project.",
            "Missing fields bound reviewability but do not prove a claim false.",
        ],
    }
    audit_bytes = (json.dumps(audit_record, indent=2, sort_keys=True) + "\n").encode()
    mo.vstack(
        [
            mo.md(
                "### Audit record\n\nThe record preserves the prediction, field audit, bounded status, and audit limits."
            ),
            mo.download(
                data=audit_bytes,
                filename="lab_03_claim_audit.json",
                mimetype="application/json",
                label="Download claim audit",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** What is the smallest new record that would make Claim B reviewable?",
        placeholder="Name one concrete baseline, workload, protocol, evidence item, or rejection condition.",
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
        mo.md("Submit the reflection to finish the activity."),
    )
    mo.md(
        "Activity complete. You audited the record without claiming more than it supports."
    )
    return


if __name__ == "__main__":
    app.run()
