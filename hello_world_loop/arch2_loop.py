# Architecture 2.0: Hello World Loop
# A minimal, executable example of the agentic design loop pattern.

import os
import random


def state() -> dict:
    """S: State - Represents the current snapshot of the design and environment."""
    return {
        "architecture_knobs": {"L1_cache_size": 32, "L2_cache_size": 256},
        "performance_target": 1.5,  # target IPC
        "current_ipc": 1.1,
    }


def action(current_state: dict) -> dict:
    """A: Action - The LLM/Agent proposes a change to the design."""
    print(
        f"[Agent] Analyzing state. Current IPC: {current_state['current_ipc']}. Target: {current_state['performance_target']}"
    )

    # In a real system, this is where you call the LLM API to get the next action.
    # We simulate the agent deciding to increase cache sizes.
    proposed_knobs = {
        "L1_cache_size": current_state["architecture_knobs"]["L1_cache_size"] * 2,
        "L2_cache_size": current_state["architecture_knobs"]["L2_cache_size"] * 2,
    }
    print(f"[Agent] Proposing new knobs: {proposed_knobs}")
    return proposed_knobs


def reject(proposed_knobs: dict) -> tuple[bool, str]:
    """R: Rejection - The verification layer checks for illegal or unsafe actions."""
    if proposed_knobs["L1_cache_size"] > 128:
        return True, "L1 cache size exceeds physical area constraints (Max 128KB)."
    return False, "Proposal passed structural constraints."


def evidence(proposed_knobs: dict) -> float:
    """E: Evidence - The simulator evaluates the accepted action to provide feedback."""
    # In a real system, this invokes gem5, SST, or an ML Proxy.
    # Here we simulate an IPC improvement based on the cache sizes.
    simulated_ipc = min(2.0, 1.1 + (proposed_knobs["L1_cache_size"] / 256.0))
    print(f"[Simulator] Ran structural simulation. Resulting IPC: {simulated_ipc:.2f}")
    return simulated_ipc


def main():
    print("=== Architecture 2.0 Loop ===")

    # 1. State
    current_state = state()

    # 2. Action
    proposed_knobs = action(current_state)

    # 3. Reject
    is_rejected, reject_reason = reject(proposed_knobs)
    if is_rejected:
        print(f"[Guardrail] REJECTED: {reject_reason}")
        return
    print(f"[Guardrail] {reject_reason}")

    # 4. Evidence
    new_ipc = evidence(proposed_knobs)

    # Loop update
    current_state["architecture_knobs"] = proposed_knobs
    current_state["current_ipc"] = new_ipc

    print("\n=== Loop Complete ===")
    if current_state["current_ipc"] >= current_state["performance_target"]:
        print("Success! Target performance achieved.")
    else:
        print("Target not met. Loop would continue...")


if __name__ == "__main__":
    main()
