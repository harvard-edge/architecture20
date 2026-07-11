# Architecture 2.0 Chapter Activities

The sequence follows the book from the moonshot prompt to architect-owned
commitment. Each activity teaches one additional part of the loop and can also
run independently from its chapter recap.

## Activity Map

| **Lab** | **Chapter and activity** | **Form** | **Typical time** | **Learner artifact** |
| --- | --- | --- | ---: | --- |
| [01](lab_01_prompt_to_card.py) | Ch1, Prompt to Card | reasoning | 20 min | Four-field context sketch with an explicit commitment limit |
| [02](lab_02_scissors_gap.py) | Ch2, Scissors Gap | data | 20 min | Queue and disposition diagnosis with an intervention choice |
| [03](lab_03_score_a_claim.py) | Ch3, Score a Claim | audit | 20 min | Claim-review record naming missing evidence and rejection conditions |
| [04](lab_04_represent_and_replay.py) | Ch4, Represent and Replay | simulator audit | 25 min | Replayability audit of a generated draft receipt |
| [05](lab_05_environment_contract.py) | Ch5, Environment Contract | simulator | 25 min | Legal or refused action plus a provenance-bearing environment record |
| [06](../examples/scale_proxy_mirage/lab.py) | Ch6, Proxy Versus Evidence | simulator anchor | 45 min | Completed and validated runnable receipt with an accountable decision |
| [07](lab_07_earned_trust.py) | Ch7, Earned Trust | simulator red team | 30 min | Orthogonal feasibility check for an environment blind spot |
| [08](lab_08_run_the_loop.py) | Ch8, Run the Loop | simulator capstone | 45 min | Completed receipt and self-assessed commitment decision |
| [09](lab_09_same_loop_different_costs.py) | Ch9, Same Loop at Different Costs | feedback-budget exercise | 25 min | Budget-allocation receipt audit and cheap-first gate decision |
| [10](lab_10_own_the_commitment.py) | Ch10, Own the Commitment | public-record audit | 30 min | Shareable Architecture 2.0 claim audit with a bounded conclusion |

The full sequence takes about four and three-quarters hours. Labs 01, 06, and 08
form a coherent two-hour introduction when time is limited.

## Learning Contract

Every activity follows the same progression:

1. Retrieve the chapter's key distinction.
2. Submit a prediction with confidence and a reason.
3. Run or audit externally inspectable evidence.
4. Reconcile the prediction with the result.
5. State a bounded rejection, escalation, or commitment.
6. Inspect or download the chapter-appropriate record.
7. Transfer the lesson to another architecture problem.

Hard gates are declared constraints such as a silicon budget or deadline.
Utilization, roofline position, and similar signals remain diagnostics unless a
separate validated rule grants them rejection authority. A tool failure remains
an environment failure unless the declared contract says otherwise.

## Running Activities

From `labs/`:

```bash
../.venv/bin/marimo edit notebooks/lab_03_score_a_claim.py
../.venv/bin/marimo run notebooks/lab_03_score_a_claim.py
```

Use edit mode for self-paced work and run mode for a read-only classroom app.
The simulator-backed activities can take longer on the first run while Python
loads SCALE-Sim.
