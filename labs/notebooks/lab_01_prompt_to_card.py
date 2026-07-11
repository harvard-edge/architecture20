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
        # Lab 01 · Prompt to Loop Card · Chapter 1 (The Moonshot)

        **You can, after this lab:** take a one-line design request and turn it into a
        *loop card* whose fields another architect could reject, rather than a wish.

        > **Recap.** A prompt is not an architecture claim. It becomes one only when the
        > loop names what it may change, what evidence it owes, what can reject it, and
        > who owns the commitment. "AI for architecture" means designing that loop, not
        > prompt-to-chip.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "A prompt is a claim as soon as a capable model answers it.": "wrong",
            "A prompt becomes a claim only once its loop names actions, evidence, rejection, and a commitment owner.": "right",
            "A prompt is a claim if it names a chip target.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** When does a prompt become an architecture claim?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(
        warmup.value != "right",
        mo.md("🔒 *Pick the answer that matches the recap to continue.*"),
    )
    mo.md("✅ A prompt becomes a claim only through its loop. Let's build one.")
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(dedent, mo, warmup_unlocked):
    assert warmup_unlocked
    mo.md(
        dedent(
            """
        ## Worked example: the lighthouse prompt, carded

        > *Design a low-power 64-bit RISC-V compute subsystem for an XRBench-class mobile
        > XR workload under a 3 W TDP in a 3 nm-class process; return a design-space
        > report with evidence and rejected alternatives.*

        A compact loop sketch makes the core obligations visible before the full
        twelve-field card is written:

        | **Sketch element** | **Filled for the lighthouse prompt** |
        | --- | --- |
        | **Workload / scenario** | XRBench-class real-time mobile XR slice; latency + QoS target stated. |
        | **Legal action space** | Vector width, local memory, CPU/accelerator partition; ISA fixed. |
        | **Environment / tool path** | Analytic proxy → cycle simulator → (later) P&R; each with a cost. |
        | **Feedback budget** | Many proxy evals, few simulator runs, ~0 P&R runs this turn. |
        | **Evidence & rejection gate** | 3 W envelope, latency deadline, silicon budget; reject on any. |
        | **Commitment boundary** | Advance to a next-fidelity study only; no RTL/product claim. |
        | **Accountable decision owner** | The architect signs the commitment; the method proposes. |

        Notice the card exposes *how the answer could be wrong*, not just what it is.
        """
        ).strip()
    )
    example_ready = True
    return (example_ready,)


@app.cell
def _(example_ready, mo):
    assert example_ready

    def _validate_prediction(value):
        if value is None or value.get("hardest") is None:
            return "Select the field you predict will be hardest."
        if value.get("confidence") is None:
            return "Record your confidence before locking the prediction."
        if not str(value.get("reason", "")).strip():
            return "Give one reason for the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "target": mo.ui.dropdown(
                options=[
                    "Datacenter-scale: a scale-out TPU training topology for a 10T-param MoE model",
                    "Sandbox: a 16x16 matmul systolic array integrated over a standard NoC",
                ],
                value="Sandbox: a 16x16 matmul systolic array integrated over a standard NoC",
                label="**Pick a prompt to card.**",
            ),
            "hardest": mo.ui.dropdown(
                options=[
                    "Workload / scenario",
                    "Legal action space",
                    "Evidence & rejection gate",
                    "Commitment boundary",
                ],
                label="**Predict.** Which field will be hardest to fill honestly?",
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
                placeholder="One sentence: why that field is the hard one here.",
                label="**Reason** (required)",
                rows=2,
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
        "Now fill the four load-bearing fields."
    )
    return prediction_locked, prediction_snapshot


@app.cell
def _(mo, prediction_locked, prediction_snapshot):
    assert prediction_locked and prediction_snapshot

    def _validate_card(value):
        if value is None:
            return "Complete the four fields."
        missing = [name for name, text in value.items() if not str(text).strip()]
        if missing:
            return "Complete every field before submitting the bootstrap card."
        return None

    card_form = mo.ui.dictionary(
        {
            "Workload / scenario": mo.ui.text_area(
                rows=2,
                placeholder="Which slice, input distribution, QoS/latency target?",
            ),
            "Legal action space": mo.ui.text_area(
                rows=2,
                placeholder="What may the method change; what is fixed or deferred?",
            ),
            "Evidence & rejection gate": mo.ui.text_area(
                rows=2,
                placeholder="What evidence is owed; what can reject a candidate?",
            ),
            "Commitment boundary": mo.ui.text_area(
                rows=2,
                placeholder="Strongest claim the evidence licenses; who owns it?",
            ),
        },
        label="**Build the four-field bootstrap card.**",
    ).form(
        submit_button_label="Submit bootstrap card",
        clear_on_submit=False,
        validate=_validate_card,
    )
    card_form
    return (card_form,)


@app.cell
def _(card_form, mo, prediction_snapshot):
    mo.stop(
        card_form.value is None,
        mo.md("*Complete and submit all four card fields.*"),
    )
    card_snapshot = dict(card_form.value)
    thin = [name for name, text in card_snapshot.items() if len(str(text).strip()) < 15]
    hardest = prediction_snapshot["hardest"]
    note = (
        "Your predicted hard field is still thin; that is useful evidence about the brief."
        if hardest in thin
        else "You filled your predicted hard field; check whether another field became the weak point."
    )
    mo.md(
        "✅ **Four-field bootstrap complete.** This exercise is a partial mapping, "
        "not a complete canonical design-loop card. Among the still-unwritten card "
        "fields are explicit intent and task, representation, environment, method "
        "role and actor map, feedback budget, evidence, failed runs and rejected "
        "alternatives, rejection authority, and accountable decision. Replay is not another card field; it "
        f"requires a separate runnable receipt. {note}"
    )
    card_ready = True
    return card_ready, card_snapshot


@app.cell
def _(card_ready, mo):
    assert card_ready

    def _validate_commitment(value):
        if value is None:
            return "Choose the strongest commitment the current state supports."
        return None

    commitment_form = mo.ui.dropdown(
        options=[
            "Advance to a next-fidelity study only",
            "Advance straight to RTL",
            "Commit to product",
        ],
        label="**Commit.** Given only a carded prompt (no evidence yet), what may you commit to?",
    ).form(
        submit_button_label="Record commitment",
        clear_on_submit=False,
        validate=_validate_commitment,
    )
    commitment_form
    return (commitment_form,)


@app.cell
def _(card_snapshot, commitment_form, mo):
    mo.stop(
        commitment_form.value is None,
        mo.md("*Choose and submit a commitment level.*"),
    )
    mo.stop(
        commitment_form.value != "Advance to a next-fidelity study only",
        mo.md(
            "🛑 **Overclaim.** A carded prompt with no evidence licenses only the "
            "decision to *study* it further. RTL or product needs the loop to run."
        ),
    )
    assert str(card_snapshot["Commitment boundary"]).strip()
    mo.md(
        "✅ **Consistent.** Your commitment matches the still-empty evidence: "
        "advance only to a next-fidelity study."
    )
    commitment_snapshot = commitment_form.value
    commitment_recorded = True
    return commitment_recorded, commitment_snapshot


@app.cell
def _(
    card_snapshot,
    commitment_recorded,
    commitment_snapshot,
    json,
    mo,
    prediction_snapshot,
):
    assert commitment_recorded
    learning_record = {
        "schema_version": "arch2-learning-record/v1",
        "activity_id": "lab_01_prompt_to_card",
        "chapter": 1,
        "prediction": prediction_snapshot,
        "bootstrap_card": card_snapshot,
        "human_commitment": commitment_snapshot,
        "scope": {
            "supports": "A partial four-field context sketch for a next-fidelity study.",
            "does_not_support": "Canonical card completion, replayability, RTL readiness, or product commitment.",
        },
    }
    record_bytes = (
        json.dumps(learning_record, indent=2, sort_keys=True) + "\n"
    ).encode()
    mo.vstack(
        [
            mo.md(
                "### Learning record\n\n"
                "The JSON binds your submitted prediction, four-field bootstrap card, "
                "and bounded human commitment. It does not claim canonical card "
                "completion or replayability."
            ),
            mo.download(
                data=record_bytes,
                filename="arch2-lab01-prompt-to-card.json",
                mimetype="application/json",
                label="Download Lab 01 learning record",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, dedent, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** Which field would a reviewer attack first, and why?",
        placeholder="Name the field and the missing precision or evidence.",
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

                A strong first contribution in Architecture 2.0 is often a better loop
                record, not a better generator. In the next labs you will run the loop
                this card describes and watch the evidence and rejection fields do real
                work.
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
        "✅ **Activity complete.** Your prediction, card, commitment, and reflection were submitted in order."
    )
    return


if __name__ == "__main__":
    app.run()
