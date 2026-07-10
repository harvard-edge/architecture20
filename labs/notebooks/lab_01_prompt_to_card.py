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
        # Lab 01 · Prompt to Loop Card  ·  Chapter 1 (The Moonshot)

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
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        ## Worked example: the lighthouse prompt, carded

        > *Design a low-power 64-bit RISC-V compute subsystem for an XRBench-class mobile
        > XR workload under a 3 W TDP in a 3 nm-class process; return a design-space
        > report with evidence and rejected alternatives.*

        A good loop card fills every field so the claim is reviewable:

        | **Card field** | **Filled for the lighthouse prompt** |
        | --- | --- |
        | **Workload / scenario** | XRBench-class real-time mobile XR slice; latency + QoS target stated. |
        | **Legal action space** | Vector width, local memory, CPU/accelerator partition; ISA fixed. |
        | **Environment / tool path** | Analytic proxy → cycle simulator → (later) P&R; each with a cost. |
        | **Feedback budget** | Many proxy evals, few simulator runs, ~0 P&R runs this turn. |
        | **Evidence & rejection gate** | 3 W envelope, latency deadline, silicon budget; reject on any. |
        | **Commitment boundary** | Advance to a next-fidelity study only; no RTL/product claim. |
        | **Human decision owner** | The architect signs the commitment; the method proposes. |

        Notice the card exposes *how the answer could be wrong*, not just what it is.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    target = mo.ui.dropdown(
        options=[
            "Datacenter-scale: a scale-out TPU training topology for a 10T-param MoE model",
            "Sandbox: a 16x16 matmul systolic array integrated over a standard NoC",
        ],
        value="Sandbox: a 16x16 matmul systolic array integrated over a standard NoC",
        label="**Pick a prompt to card.**",
    )
    hardest = mo.ui.dropdown(
        options=[
            "Workload / scenario",
            "Legal action space",
            "Evidence & rejection gate",
            "Commitment boundary",
        ],
        label="**Predict.** Which field will be hardest to fill honestly for your prompt?",
    )
    why = mo.ui.text_area(
        placeholder="One sentence: why that field is the hard one here.",
        label="**Reason** (required)",
        rows=2,
    )
    lock = mo.ui.run_button(label="🔒 Lock my prediction")
    mo.vstack([target, hardest, why, lock])
    return hardest, lock, target, why


@app.cell
def _(lock, mo, why):
    mo.stop(
        not lock.value or not why.value.strip(),
        mo.md("*Predict the hardest field, give a reason, and lock to continue.*"),
    )
    mo.md("Prediction locked. Now fill the four load-bearing fields.")
    return


@app.cell
def _(mo):
    workload = mo.ui.text_area(
        label="**Workload / scenario**",
        rows=2,
        placeholder="Which slice, input distribution, QoS/latency target?",
    )
    actions = mo.ui.text_area(
        label="**Legal action space**",
        rows=2,
        placeholder="What may the method change; what is fixed or deferred?",
    )
    evidence = mo.ui.text_area(
        label="**Evidence & rejection gate**",
        rows=2,
        placeholder="What evidence is owed; what can reject a candidate?",
    )
    boundary = mo.ui.text_area(
        label="**Commitment boundary**",
        rows=2,
        placeholder="Strongest claim the evidence licenses; who owns it?",
    )
    mo.vstack([workload, actions, evidence, boundary])
    return actions, boundary, evidence, workload


@app.cell
def _(actions, boundary, evidence, hardest, mo, workload):
    fields = {
        "Workload / scenario": workload.value,
        "Legal action space": actions.value,
        "Evidence & rejection gate": evidence.value,
        "Commitment boundary": boundary.value,
    }
    empty = [name for name, text in fields.items() if not text.strip()]
    thin = [name for name, text in fields.items() if 0 < len(text.strip()) < 15]

    if empty:
        status = mo.md(
            f"🟡 **Card incomplete.** Still empty: {', '.join(f'`{e}`' for e in empty)}. "
            "A card with a blank field is a wish, not a claim."
        )
    else:
        note = f" Your prediction ({hardest.value}) " + (
            "matches a field you left thin, which is honest self-knowledge."
            if hardest.value in thin
            else "was one you actually filled well — did a different field turn out harder?"
        )
        status = mo.md(
            "✅ **Four-field bootstrap complete.** This exercise is a partial mapping, "
            "not a complete canonical design-loop card. The remaining canonical fields "
            "still need evidence, replay, rejection-authority, and ownership records."
            + (note if hardest.value else "")
        )
    status
    return


@app.cell
def _(mo):
    level = mo.ui.dropdown(
        options=[
            "Advance to a next-fidelity study only",
            "Advance straight to RTL",
            "Commit to product",
        ],
        label="**Commit.** Given only a carded prompt (no evidence yet), what may you commit to?",
    )
    level
    return (level,)


@app.cell
def _(boundary, level, mo):
    if level.value is None:
        _out = mo.md("*Choose a commitment level.*")
    elif level.value != "Advance to a next-fidelity study only":
        _out = mo.md(
            "🛑 **Overclaim.** A carded prompt with no evidence licenses only the "
            "decision to *study* it further. RTL or product needs the loop to run."
        )
    elif boundary.value.strip():
        _out = mo.md(
            "✅ **Consistent.** Your commitment matches the (still empty) evidence: study only."
        )
    else:
        _out = mo.md("🟡 Fill the commitment-boundary field first.")
    _out
    return


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        ### Reflect

        Which field would a *reviewer* attack first in your card? A strong first
        contribution in Architecture 2.0 is often a better loop record, not a better
        generator. In the next labs you will run the loop this card describes and watch
        the evidence and rejection fields do real work.
        """
        ).strip()
    )
    return


if __name__ == "__main__":
    app.run()
