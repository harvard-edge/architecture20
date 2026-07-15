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

    labs_root = Path(__file__).resolve().parents[1]
    if str(labs_root) not in sys.path:
        sys.path.insert(0, str(labs_root))

    from arch2_labs.schemas import Candidate
    from arch2_labs.scale_env import example_dir, run_scalesim

    return Candidate, Path, dedent, example_dir, json, mo, run_scalesim, tempfile


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            """
        # Lab 07 · Earned Trust: Test the Environment's Blind Spot · Chapter 7

        **You can, after this lab:** expose one limitation in a simulator result,
        apply an orthogonal analytic feasibility check, and state exactly what that
        check does and does not license.

        > **Recap.** Trust belongs to a scoped commitment, not to a tool in the
        > abstract. A check earns authority only for failures it can actually expose.
        > Shared inputs or calculations must also be disclosed, because a second
        > calculation is not automatically independent evidence.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "A simulator is trusted once repeated runs agree.": "repeat",
            "A scoped commitment needs a rejection check matched to a failure the primary result may miss.": "right",
            "Any calculation outside the simulator is independent evidence.": "outside",
        },
        label="**Warm-up.** What can make a simulator-backed commitment more trustworthy?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(
        warmup.value != "right",
        mo.md("*Choose the answer that matches the scoped trust claim to continue.*"),
    )
    mo.md(
        "The check must match a declared blind spot. Now predict the tool's response."
    )
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked

    def validate_prediction(value):
        if value is None or value.get("choice") is None:
            return "Choose what you expect the cycle count to do."
        if value.get("confidence") is None:
            return "Record your confidence."
        if not str(value.get("reason", "")).strip():
            return "Give one reason for the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "choice": mo.ui.radio(
                options={
                    "Cycles rise sharply because the constrained interface stalls the array.": "cycles_rise",
                    "Cycles remain nearly unchanged because this configuration does not model the bandwidth stall.": "cycles_hold",
                },
                label="**Predict.** What happens when each declared DRAM channel falls from 64 to 1 word per cycle?",
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
                placeholder="Which modeled or unmodeled mechanism controls your prediction?",
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
        "The evidence remains hidden until you run both configurations."
    )
    return (prediction_snapshot,)


@app.cell
def _(mo, prediction_snapshot):
    assert prediction_snapshot
    run_button = mo.ui.run_button(
        label="Run SCALE-Sim 3.0.0 at 64 and 1 word/cycle per channel"
    )
    run_button
    return (run_button,)


@app.cell
def _(
    Candidate,
    Path,
    example_dir,
    mo,
    prediction_snapshot,
    run_button,
    run_scalesim,
    tempfile,
):
    assert prediction_snapshot
    mo.stop(
        not run_button.value, mo.md("*Run both configurations to reveal the evidence.*")
    )

    example = example_dir("scale_proxy_mirage")
    topology = example / "workloads" / "xr_slice_gemm.csv"
    layout = example / "layouts" / "default_layout.csv"

    def run_bandwidth(per_channel_bandwidth):
        candidate = Candidate(
            candidate_id=f"redteam_64x64_bw{per_channel_bandwidth}",
            label="64x64 bandwidth probe",
            source="lab07",
            array_rows=64,
            array_cols=64,
            dataflow="ws",
            sram_kb=128,
            dram_bandwidth_words_per_cycle=per_channel_bandwidth,
            clock_mhz=800,
            area_budget_pes=10**9,
            deadline_cycles=10**9,
            min_layer_util_pct=0.0,
        )
        record = run_scalesim(
            candidate,
            topology,
            layout,
            Path(tempfile.mkdtemp(prefix="arch2_lab07_")),
        )
        if record["status"] != "ok":
            raise RuntimeError("SCALE-Sim did not complete the bandwidth probe")
        return record

    reference_record = run_bandwidth(64)
    constrained_record = run_bandwidth(1)
    reference_metrics = reference_record["metrics"]
    constrained_metrics = constrained_record["metrics"]

    channel_count = 3
    declared_per_channel = 1.0
    declared_aggregate = channel_count * declared_per_channel
    required_aggregate = (
        constrained_metrics["dram_accesses"] / constrained_metrics["total_cycles"]
    )
    shortfall_ratio = required_aggregate / declared_aggregate
    analytic_check_failed = required_aggregate > declared_aggregate
    cycle_change_pct = (
        100.0
        * (constrained_metrics["total_cycles"] - reference_metrics["total_cycles"])
        / reference_metrics["total_cycles"]
    )

    probe_result = {
        "tool": "SCALE-Sim 3.0.0",
        "reference": {
            "per_channel_words_per_cycle": 64,
            "cycles": reference_metrics["total_cycles"],
            "stall_cycles": reference_metrics["stall_cycles"],
        },
        "constrained": {
            "per_channel_words_per_cycle": 1,
            "channel_count": channel_count,
            "declared_aggregate_words_per_cycle": declared_aggregate,
            "cycles": constrained_metrics["total_cycles"],
            "stall_cycles": constrained_metrics["stall_cycles"],
            "aggregate_dram_accesses": constrained_metrics["dram_accesses"],
        },
        "cycle_change_pct": cycle_change_pct,
        "analytic_check": {
            "required_average_aggregate_words_per_cycle": required_aggregate,
            "declared_aggregate_words_per_cycle": declared_aggregate,
            "shortfall_ratio": shortfall_ratio,
            "failed": analytic_check_failed,
            "dependence": "Uses SCALE-Sim traffic and cycle outputs; orthogonal calculation, not independent evidence.",
        },
    }
    return (probe_result,)


@app.cell
def _(mo, prediction_snapshot, probe_result):
    held = abs(probe_result["cycle_change_pct"]) < 1.0
    expected_hold = prediction_snapshot["choice"] == "cycles_hold"
    check = probe_result["analytic_check"]
    mo.md(
        f"""
        ### Evidence and Reconciliation

        | **Configuration** | **Declared bandwidth** | **Cycles** | **Stall cycles** |
        | --- | --- | --- | --- |
        | Reference | 64 words/cycle on each of 3 channels | {probe_result['reference']['cycles']} | {probe_result['reference']['stall_cycles']} |
        | Constrained | 1 word/cycle on each of 3 channels | {probe_result['constrained']['cycles']} | {probe_result['constrained']['stall_cycles']} |

        The cycle count changed by **{probe_result['cycle_change_pct']:.2f}%**.
        {"Your submitted direction matched the run." if held == expected_hold else "Your submitted direction did not match the run."}
        You predicted at **{prediction_snapshot['confidence']}% confidence** and wrote:
        *{prediction_snapshot['reason']}*

        ### Orthogonal Analytic Feasibility Check

        The access counter aggregates IFMAP reads, filter reads, and OFMAP writes.
        Its average demand is **{check['required_average_aggregate_words_per_cycle']:.1f}
        aggregate words/cycle**. The constrained configuration declares three channels
        at 1 word/cycle each, or **{check['declared_aggregate_words_per_cycle']:.0f}
        aggregate words/cycle**. Average demand therefore exceeds declared aggregate
        capacity by about **{check['shortfall_ratio']:.1f}×**.

        This calculation exposes an inconsistency that the unchanged cycle count hides.
        It reuses the simulator's access and cycle outputs, so it is an **orthogonal
        analytic check, not independent evidence**. It can reject this bandwidth claim
        for a next-fidelity commitment. It cannot establish full-system feasibility or
        validate every SCALE-Sim assumption.
        """
    )
    evidence_revealed = True
    return (evidence_revealed,)


@app.cell
def _(evidence_revealed, mo):
    assert evidence_revealed

    def validate_commitment(value):
        if value is None or value.get("decision") is None:
            return "Choose a scoped commitment."
        if value["decision"] != "reject_bandwidth_claim":
            return "The evidence does not clear the bandwidth-1 configuration for advancement."
        if not str(value.get("human_owner", "")).strip():
            return "Name the owner of the decision."
        if not str(value.get("rationale", "")).strip():
            return "Explain why the scoped check supports the commitment."
        if not str(value.get("would_overturn", "")).strip():
            return "State what evidence would overturn the rejection."
        return None

    commitment_form = mo.ui.dictionary(
        {
            "decision": mo.ui.dropdown(
                options={
                    "Reject the bandwidth-1 configuration from this next-fidelity commitment; require a stronger memory-system study.": "reject_bandwidth_claim",
                    "Advance the bandwidth-1 configuration directly to RTL.": "advance_to_rtl",
                    "Treat unchanged simulator cycles as proof of physical feasibility.": "trust_primary_result",
                },
                label="**Commit.** What does this evidence license?",
            ),
            "human_owner": mo.ui.text(
                label="**Decision owner** (required)",
                placeholder="Your name or review role",
            ),
            "rationale": mo.ui.text_area(
                label="**Rationale** (required)",
                placeholder="Connect the aggregate demand check to the bounded rejection.",
                rows=2,
            ),
            "would_overturn": mo.ui.text_area(
                label="**Would overturn** (required)",
                placeholder="Name stronger memory-system evidence that could clear this configuration.",
                rows=2,
            ),
        }
    ).form(
        submit_button_label="Record scoped commitment",
        clear_on_submit=False,
        validate=validate_commitment,
    )
    commitment_form
    return (commitment_form,)


@app.cell
def _(commitment_form, json, mo, prediction_snapshot, probe_result):
    mo.stop(
        commitment_form.value is None,
        mo.md("*Submit the scoped commitment to produce the chapter record.*"),
    )
    commitment_snapshot = dict(commitment_form.value)
    chapter_record = {
        "schema_version": "arch2-learning-record/v1",
        "activity_id": "lab_07_earned_trust",
        "prediction": prediction_snapshot,
        "evidence": probe_result,
        "human_commitment": commitment_snapshot,
        "scope": {
            "supports": "Reject the bandwidth-1 configuration from this next-fidelity commitment.",
            "does_not_support": "Independent validation, RTL readiness, or full-system feasibility.",
        },
    }
    record_text = json.dumps(chapter_record, indent=2, sort_keys=True) + "\n"
    mo.vstack(
        [
            mo.md(
                "### Auditable Chapter Record\n\n"
                "This JSON preserves the submitted prediction, tool observations, "
                "analytic check, dependence disclosure, and human commitment. It is a "
                "learning record, not a replayable run archive."
            ),
            mo.download(
                data=record_text.encode(),
                filename="arch2-lab07-earned-trust-record.json",
                mimetype="application/json",
                label="Download Lab 07 record",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** Which different evidence source could make the bandwidth judgment more independent?",
        placeholder="Name the source and the failure mode it could expose without reusing this calculation.",
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
        "**Activity complete.** You separated a primary result, a dependent analytic "
        "check, a scoped rejection, and the independent evidence still owed."
    )
    return


if __name__ == "__main__":
    app.run()
