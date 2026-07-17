import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# 1. Explain Figure 1.1
text = text.replace(
    "As illustrated in @fig-environment-tool-interface, when confronted with the massive semantic gap",
    """As illustrated in @fig-environment-tool-interface, an architecture environment explicitly maps intent to actions and actions to observations. The wrapper acts as a protective boundary: it intercepts the high-level request, checks it against constraints via the read path, translates it into tool-specific commands along the action path, and distills the messy log outputs back into a clean semantic vector on the return path.

When confronted with this massive semantic gap""",
)

# 2. Change section title
text = text.replace(
    "## Executing Intent: Cloud and Bioinformatics Analogies",
    "## Executing Intent: Orchestrating Complex Toolchains",
)

# 3. Remove XR Lighthouse
text = text.replace(
    "Consider the **XR Lighthouse** example introduced in ?@sec-moonshot. The high-level system intent is to maximize XRBench throughput within a strict 3 W TDP thermal envelope.",
    "Consider an AI agent proposing a hardware change to a spatial accelerator. The high-level system intent might be to maximize inference throughput within a strict 3 W TDP thermal envelope.",
)

text = text.replace(
    "For the **XR Lighthouse** subsystem, adding a new Tensor Core accelerator unit requires explicit MLIR-to-RTL lowering and compiler IR transformations.",
    "For a complex System-on-Chip (SoC), adding a new Tensor Core accelerator unit requires explicit MLIR-to-RTL lowering and compiler IR transformations.",
)

text = text.replace(
    "If the AI is trying to solve routing congestion for the XR Lighthouse subsystem,",
    "If the AI is trying to solve routing congestion for a newly proposed SoC layout,",
)

# 4. Explain Figure 1.2
text = text.replace(
    "When a candidate design passes validation, it must be translated into actionable tool commands. As shown in @fig-chipyard-framework, how does one candidate architecture change become several legal tool actions without losing its connection to the system intent? We must look to adjacent domains that have solved this exact problem of decoupling *intent* from *messy execution mechanics*.",
    """When a candidate design passes validation, it must be translated into actionable tool commands. As shown in @fig-chipyard-framework, a single high-level hardware configuration might need to fan out to multiple distinct evaluation backends: an RTL simulator for functional correctness, a VLSI flow for power and area estimates, and an FPGA emulation path for full-stack software booting. The framework ensures that one candidate architecture change routes downward to become several legal tool actions without losing its connection to the system intent.

To manage this fan-out, we must look to adjacent domains that have solved this exact problem of decoupling *intent* from *messy execution mechanics*.""",
)

# 5. env.step() background
text = text.replace(
    "Asynchronous, Scarce, and Protected Tool Chains are critical. Because of the physical and economic constraints of real hardware design, the standard synchronous `env.step()` wrapper---which blocks execution until a scalar reward is returned---is fundamentally the wrong abstraction.",
    """In pedagogical AI tutorials, agents often interact with simulated games (like OpenAI Gym) using a synchronous `env.step()` function. The agent takes a discrete action, the simulation instantly steps forward in time, and the function returns the new state and a reward. However, because of the physical and economic constraints of real hardware design, this standard synchronous `env.step()` wrapper---which blocks execution until a scalar reward is returned---is fundamentally the wrong abstraction. A blocking synchronous call will inevitably time out or hang when a placement job takes 40 hours, or waits three days for an EDA license checkout.

Asynchronous, Scarce, and Protected Tool Chains are critical.""",
)

# 6. Footnotes
text = text.replace(
    "Slurm queue",
    "Slurm queue^[Slurm is a highly scalable cluster management and job scheduling system used extensively in supercomputing and server farms.]",
)
text = text.replace(
    "FlexLM license",
    "FlexLM license^[FlexLM is a widely used software license manager; many commercial EDA tools require checking out a network license token before they will execute, which can cause jobs to hang if tokens are exhausted.]",
)

# 7. Separate Attention section
text = text.replace(
    "A major issue is the attention bottleneck in LLM-Driven Architecture.",
    "## The Attention Bottleneck and Data Distillation\n\nA major issue is the attention bottleneck in LLM-Driven Architecture.",
)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(text)

print("Done")
