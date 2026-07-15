import marimo

__generated_with = "0.23.13"
app = marimo.App(width="medium")


@app.cell
def _():
    import json
    import shutil
    import sys
    import tempfile
    from pathlib import Path
    from textwrap import dedent

    import marimo as mo
    import yaml

    _source = Path(__file__).resolve()
    for _candidate_root in [_source.parent, *_source.parents]:
        if (_candidate_root / "arch2_labs").is_dir():
            if str(_candidate_root) not in sys.path:
                sys.path.insert(0, str(_candidate_root))
            break

    from arch2_labs.scale_env import run_example
    from arch2_labs.validators import validate_decision_draft

    return (
        Path,
        dedent,
        json,
        mo,
        run_example,
        shutil,
        tempfile,
        validate_decision_draft,
        yaml,
    )


@app.cell
def _(dedent, mo):
    mo.md(
        dedent(
            r"""
        # Lab 04 | Represent and Replay | Chapter 4

        **You can, after this lab:** distinguish evidence from replayability, inspect the
        bindings in a real draft run archive, and state exactly what an attempted replay would
        and would not establish.

        > **Recap.** Evidence can support a bounded claim even when a public replay packet
        > is unavailable. Replayability is a separate property. It requires runnable inputs,
        > configuration, environment and tool versions, commands, outputs, and integrity
        > bindings. A run archive can make an attempted replay possible; only an actual replay
        > result establishes that the packet ran in the declared environment.
        """
        ).strip()
    )
    return


@app.cell
def _(mo):
    warmup = mo.ui.radio(
        options={
            "A winning score and a screenshot.": "wrong",
            "Runnable inputs, configuration, command, environment versions, outputs, and integrity bindings.": "right",
            "A paper title and a timestamp.": "wrong2",
        },
        label="**Warm-up (unlocks the lab).** What must a packet bind before it supports an attempted replay?",
    )
    warmup
    return (warmup,)


@app.cell
def _(mo, warmup):
    mo.stop(warmup.value != "right", mo.md("Locked. Match the recap to continue."))
    mo.md(
        "A replay claim needs runnable bindings. Predict which bundle matters before inspecting one."
    )
    warmup_unlocked = True
    return (warmup_unlocked,)


@app.cell
def _(mo, warmup_unlocked):
    assert warmup_unlocked
    mo.md(
        r"""
        ## The task

        The lab will run the checked-in SCALE-Sim example and produce a schema 2.0
        draft run archive. Its replay profile is partial with verified bindings, while its
        decision remains pending. You will inspect the packet before deciding what it supports.
        """
    )
    brief_ready = True
    return (brief_ready,)


@app.cell
def _(brief_ready, mo):
    assert brief_ready

    def _validate_prediction(value):
        if value is None or value.get("binding") is None:
            return "Choose the bundle you predict is required."
        if value.get("confidence") is None:
            return "Record your confidence before locking the prediction."
        if not str(value.get("reason", "")).strip():
            return "Give one reason for the prediction."
        return None

    prediction_form = mo.ui.dictionary(
        {
            "binding": mo.ui.radio(
                options={
                    "Input files and hashes, configuration, command, tool/runtime versions, and raw outputs.": "runnable_bindings",
                    "The selected winner and its reported score.": "conclusion_only",
                    "A screenshot and wall-clock timestamp.": "presentation_only",
                },
                label="**Predict.** Which bundle must survive for another architect to attempt the same run?",
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
                placeholder="What would another machine need to reconstruct or verify?",
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
        mo.md("Submit a binding, confidence, and reason before running the study."),
    )
    prediction_snapshot = dict(prediction_form.value)
    mo.md(f"Prediction locked at **{prediction_snapshot['confidence']}% confidence**.")
    return (prediction_snapshot,)


@app.cell
def _(mo, prediction_snapshot):
    assert prediction_snapshot
    run_study = mo.ui.run_button(
        label="Run the study turn and build its draft run archive"
    )
    run_study
    return (run_study,)


@app.cell
def _(
    Path,
    json,
    mo,
    run_example,
    run_study,
    tempfile,
    validate_decision_draft,
    yaml,
):
    mo.stop(not run_study.value, mo.md("Run the turn to inspect its archive bindings."))
    run_dir = Path(tempfile.mkdtemp(prefix="arch2_replay_")) / "run"
    run_summary = run_example("scale_proxy_mirage", run_dir, force=True)
    draft_manifest = validate_decision_draft(run_dir)
    card = yaml.safe_load((run_dir / "card.yaml").read_text())
    run_records = [
        json.loads(line)
        for line in (run_dir / "runs.jsonl").read_text().splitlines()
        if line.strip()
    ]
    sim_record = next(
        record
        for record in run_records
        if record.get("stage") == "scalesim" and record.get("status") == "ok"
    )
    lab_card = card["design_loop_card"]
    raw_files = sim_record["outputs"]["raw_files"]
    binding_audit = {
        "archive_status": draft_manifest["status"],
        "runner_status": run_summary["status"],
        "card_profiles": lab_card["profiles"],
        "environment_id": lab_card["environment"]["environment_id"],
        "candidate_id": sim_record["candidate_id"],
        "tool": sim_record["tool"],
        "runtime": sim_record["runtime"],
        "command": sim_record["command"],
        "inputs": sim_record["inputs"],
        "raw_outputs": raw_files,
        "negative_trace_count": sum(
            1
            for line in (run_dir / "negative_traces.jsonl").read_text().splitlines()
            if line.strip()
        ),
        "replay_attempted": False,
    }
    mo.md(f"Draft run archive built at `{run_dir}`.")
    return binding_audit, run_dir


@app.cell
def _(binding_audit, mo, prediction_snapshot):
    predicted_bindings = prediction_snapshot["binding"] == "runnable_bindings"
    input_rows = "\n".join(
        f"- `{name}`: `{value}`"
        for name, value in binding_audit["inputs"].items()
        if name.endswith("_sha256")
    )
    mo.md(
        f"""
        ### Run-Archive Binding Audit

        | **Binding** | **Recorded value** |
        | --- | --- |
        | Draft status | `{binding_audit['archive_status']}` |
        | Complete card profiles | {', '.join(name for name, status in binding_audit['card_profiles'].items() if status == 'complete')} |
        | Environment | `{binding_audit['environment_id']}` |
        | Tool | `{binding_audit['tool']['name']} {binding_audit['tool']['version']}` |
        | Python runtime | `{binding_audit['runtime']['python']}` |
        | Candidate | `{binding_audit['candidate_id']}` |
        | Command | `{' '.join(str(part) for part in binding_audit['command'])}` |
        | Raw outputs with hashes | {len(binding_audit['raw_outputs'])} |
        | Failed / rejected records | {binding_audit['negative_trace_count']} |

        **Input integrity bindings**

        {input_rows}

        {"Your prediction identified the runnable bundle." if predicted_bindings else "A conclusion or screenshot cannot reconstruct the execution; the packet needs the runnable bundle shown above."}

        This run archive contains evidence and passes the draft audit. It also binds the
        material needed to attempt replay. It does **not** claim that replay has been
        attempted, that another environment will reproduce the result, or that the evidence
        authorizes a human commitment. Those are separate judgments.
        """
    )
    audit_revealed = True
    return (audit_revealed,)


@app.cell
def _(audit_revealed, mo):
    assert audit_revealed

    def _validate_commitment(value):
        if value is None:
            return "Choose the strongest status this packet supports."
        return None

    commitment_form = mo.ui.dropdown(
        options=[
            "Evidence-bearing v2 draft with verified replay bindings; replay is not attempted and the decision is pending.",
            "Independently reproduced result ready for implementation.",
            "No evidence exists because the run archive is not yet complete.",
        ],
        label="**Decide.** What status does the inspected packet support?",
    ).form(
        submit_button_label="Record packet status",
        clear_on_submit=False,
        validate=_validate_commitment,
    )
    commitment_form
    return (commitment_form,)


@app.cell
def _(commitment_form, mo):
    mo.stop(
        commitment_form.value is None,
        mo.md("Choose and submit the packet status."),
    )
    mo.stop(
        not commitment_form.value.startswith("Evidence-bearing v2 draft"),
        mo.md(
            "That status collapses evidence, replay, and commitment. The packet carries "
            "evidence and replay bindings, but no replay result or recorded decision."
        ),
    )
    packet_status = commitment_form.value
    mo.md("Packet status recorded with evidence, replay, and commitment kept separate.")
    return (packet_status,)


@app.cell
def _(binding_audit, json, mo, packet_status, prediction_snapshot, run_dir, shutil):
    audit_record = {
        "schema_version": "arch2-replay-binding-audit/v0.1",
        "lab_id": "lab_04_represent_and_replay",
        "prediction": prediction_snapshot,
        "binding_audit": binding_audit,
        "review_status": packet_status,
    }
    audit_bytes = (json.dumps(audit_record, indent=2, sort_keys=True) + "\n").encode()
    archive_path = run_dir.with_suffix(".zip")
    shutil.make_archive(str(archive_path.with_suffix("")), "zip", root_dir=run_dir)
    mo.vstack(
        [
            mo.md(
                "### Auditable Artifacts\n\nDownload either the binding audit or the sealed draft run archive it describes."
            ),
            mo.download(
                data=audit_bytes,
                filename="lab_04_replay_binding_audit.json",
                mimetype="application/json",
                label="Download binding audit",
            ),
            mo.download(
                data=lambda: archive_path.read_bytes(),
                filename="lab_04_draft_run_archive.zip",
                mimetype="application/zip",
                label="Download draft run archive",
            ),
        ]
    )
    artifact_ready = True
    return (artifact_ready,)


@app.cell
def _(artifact_ready, mo):
    assert artifact_ready
    reflection_form = mo.ui.text_area(
        label="**Reflect.** What additional result would you require before claiming independent reproduction?",
        placeholder="Name the actor, environment, replay protocol, and comparison you would require.",
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
        "Activity complete. The evidence, replay bindings, replay result, and commitment remained separate claims."
    )
    return


if __name__ == "__main__":
    app.run()
