import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# 1. Update Learning Objectives
text = re.sub(
    r"::: \{\.callout-learning-objectives\}.*?:::",
    """::: {.callout-learning-objectives}
After this chapter you can turn an ad-hoc tool path into a documented environment interface. Specifically, you can:

- **Explain** the semantic gap between human intuition-driven EDA tools and deterministic AI APIs;
- **Translate** high-level architectural intent into a concrete set of legal tool actions;
- **Formulate** standard algorithmic interfaces for asynchronous, scarce, and protected execution mechanics;
- **Distinguish** infrastructure failures from true architectural constraint violations to prevent negative training reinforcement;
- **Evaluate** the economic reality of EDA tools, balancing fidelity against simulation cost.
:::""",
    text,
    flags=re.DOTALL,
)

# 2. Add history of tools and Semantic Gap definition to 5.1
text = text.replace(
    "The fundamental friction in AI-assisted hardware design stems from an origin mismatch.",
    """The journey from early hardware design to modern Electronic Design Automation (EDA) is fundamentally a story of human-in-the-loop scaling. For decades, architecture tools---like CACTI for memory modeling [@MuralimanoharEtAl2009CACTI], DRAMSys for memory controllers [@WeisEtAl2021DRAMSys], or gem5 for full-system simulation [@BinkertEtAl2011gem5]---were painstakingly engineered to support human intuition. They assume an architect sitting at a workstation, interacting through Graphical User Interfaces (GUIs), interpreting color-coded waveforms, and entering commands into an interactive shell.

This legacy created what we call the **semantic gap**: the massive gulf between the high-level semantic intent of a design ("increase the cache size to improve hit rate") and the low-level, unstructured, and messy mechanics of the tool itself (editing a specific line in a `.cfg` file, running a brittle bash script, and parsing a 10,000-line unstructured log file to extract one metric).

The fundamental friction in AI-assisted hardware design stems from this origin mismatch.""",
)

# 3. Transition before XR Lighthouse
text = text.replace(
    "Consider the **XR Lighthouse** example introduced in @sec-moonshot.",
    """Before executing a change, we must ask: where does a candidate change actually come from? For Chapters 1 through 3, we discussed the components of the design loop---the generator, the world model, the verifier. A candidate change is born from the generator acting on the world model's representation, but it remains a pure hypothesis until it executes. By the end of Chapter 10, we will have touched on every layer required to build this end-to-end system. In this chapter, however, we focus strictly on the environment that translates that hypothetical change into physical truth.

Consider the **XR Lighthouse** example introduced in @sec-moonshot.""",
)

# 4. Clarify Hallucination
text = text.replace(
    "Without this data, an AI is just a stochastic hallucination engine.",
    "Without this data, a generative AI is just a stochastic hallucination engine, while an optimization AI will ruthlessly exploit any flaws in an ungrounded reward function.",
)

# 5. Make the algorithm look like a LaTeX algorithm
old_algo = """```{#lst-environment-interface .pseudo lst-cap="The Architecture Environment Interface"}
Input: `action_request` (e.g., target L2 cache size, routing effort)
Output: `observation_vector`, `status_flags`, `provenance_metadata`

1. Validate Action (Read/Action Path):
   * Check if `action_request` violates fundamental fixed constraints (e.g., exceeds global area budget).
   * If invalid: Return `INVALID_ACTION` immediately. Do not invoke tools.
2. Translate to Tool Commands:
   * Lower `action_request` into tool-specific configurations (e.g., CACTI `.cfg` files, gem5 command line arguments).
3. Asynchronous Execution (Return Path):
   * Submit job to cluster/queue.
   * Handle timeouts, missing FlexLM licenses, or cluster preemption.
   * If infrastructure fails: Return `TOOL_CRASH`. Do not penalize the architecture candidate.
4. Data Distillation:
   * Parse the 10,000-line tool stdout and gigabyte trace files.
   * Extract the key performance indicators (KPIs) into a dense `observation_vector` (e.g., `[latency_ns, power_w, area_mm2]`).
5. Return State:
    * Package the `observation_vector`, `status_flags` (e.g., `TIMING_MET`, `ROUTING_FAILED`), and exact tool hashes for reproducibility.
```"""

new_algo = r"""::: {.content-visible when-format="pdf"}
```{=latex}
\begin{algorithm}[H]
\caption{The Architecture Environment Interface}\label{lst-environment-interface}
\begin{algorithmic}[1]
\Require \texttt{action\_request} (e.g., target L2 cache size, routing effort)
\Ensure \texttt{observation\_vector}, \texttt{status\_flags}, \texttt{provenance\_metadata}
\State \textbf{Validate Action (Read/Action Path):}
\If{\texttt{action\_request} violates fixed constraints}
    \State \Return \texttt{INVALID\_ACTION} immediately. Do not invoke tools.
\EndIf
\State \textbf{Translate to Tool Commands:}
\State Lower \texttt{action\_request} into tool-specific configurations.
\State \textbf{Asynchronous Execution (Return Path):}
\State Submit job to cluster/queue.
\If{infrastructure fails (timeout, missing license)}
    \State \Return \texttt{TOOL\_CRASH}. Do not penalize the architecture candidate.
\EndIf
\State \textbf{Data Distillation:}
\State Parse the tool stdout and trace files.
\State Extract KPIs into \texttt{observation\_vector}.
\State \textbf{Return State:}
\State Package \texttt{observation\_vector}, \texttt{status\_flags}, and exact tool hashes.
\end{algorithmic}
\end{algorithm}
```
:::

::: {.content-visible when-format="html"}
::: {#lst-environment-interface .algorithm lst-cap="The Architecture Environment Interface"}
**Require:** `action_request`
**Ensure:** `observation_vector`, `status_flags`, `provenance_metadata`

1. **Validate Action (Read/Action Path):**
   - If `action_request` violates fixed constraints:
     - **return** `INVALID_ACTION` immediately. Do not invoke tools.
2. **Translate to Tool Commands:**
   - Lower `action_request` into tool-specific configurations (e.g., CACTI `.cfg`).
3. **Asynchronous Execution (Return Path):**
   - Submit job to cluster/queue.
   - If infrastructure fails:
     - **return** `TOOL_CRASH`. Do not penalize candidate.
4. **Data Distillation:**
   - Parse tool stdout and trace files.
   - Extract KPIs into `observation_vector`.
5. **Return State:**
   - Package `observation_vector`, `status_flags`, and exact tool hashes.
:::
:::"""

text = text.replace(old_algo, new_algo)

# 6. Add transitions for executing intent
text = text.replace(
    "As shown in @fig-chipyard-framework, how does one candidate architecture change become several legal tool actions without losing its connection to the system intent?",
    "When a candidate design passes validation, it must be translated into actionable tool commands. As shown in @fig-chipyard-framework, how does one candidate architecture change become several legal tool actions without losing its connection to the system intent?",
)

# 7. Flatten 5.4 and 5.5 subsections
text = text.replace(
    "### Asynchronous, Scarce, and Protected Tool Chains\n\nBecause of the physical",
    "Asynchronous, Scarce, and Protected Tool Chains are critical. Because of the physical",
)
text = text.replace(
    "### Distinguishing Tool Failures from Design Failures\n\nA critical requirement",
    "Furthermore, distinguishing Tool Failures from Design Failures is necessary. A critical requirement",
)

text = text.replace(
    "### Different Tools Return Different Things\n\nModern AI research",
    "First, we must acknowledge that different tools return different things. Modern AI research",
)
text = text.replace(
    "### Variable Execution Latency and Cost\n\nThe second economic reality",
    "Second, variable execution latency and cost must be accommodated. The second economic reality",
)
text = text.replace(
    "### Unstructured Formats and the Parser Bottleneck\n\nThird, extracting meaning",
    "Third, we must overcome unstructured formats and the parser bottleneck. Extracting meaning",
)
text = text.replace(
    "### Determinism vs. Reproducibility\n\nFinally, architecture environments",
    "Finally, the environment must balance determinism versus reproducibility. Architecture environments",
)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(text)

print("Done")
