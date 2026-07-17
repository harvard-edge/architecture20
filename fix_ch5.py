import re

with open(
    "/Users/VJ/GitHub/Arch2/book/chapters/05-architecture-environments-tool-interfaces/index.qmd",
    "r",
) as f:
    lines = f.read().split("\n")

# Find sections
idx_abstract_end = next(i for i, l in enumerate(lines) if l.strip() == "```" and i > 12)
idx_5_1 = next(i for i, l in enumerate(lines) if l.startswith("## The Origin Mismatch"))
idx_5_4 = next(
    i
    for i, l in enumerate(lines)
    if l.startswith("## Killing the Synchronous `env.step()`")
)

intro = lines[: idx_abstract_end + 1]
intro_rest = lines[idx_abstract_end + 1 : idx_5_1]

# Insert Crux
crux = [
    "",
    "::: {.callout-crux}",
    "How do we bridge the semantic gap between an AI's abstract intent and the messy, stateful reality of computer architecture tools to create a reliable design environment?",
    ":::",
]
new_intro = intro + crux + intro_rest

# Process 5.1 to 5.3
# Remove ### headers
middle_section = lines[idx_5_1:idx_5_4]
new_middle = []
for line in middle_section:
    if line.startswith("### "):
        continue

    # Replace the callout with a native listing
    if line.startswith(
        '::: {.callout-note title="Algorithm Listing: The Architecture Environment Interface"}'
    ):
        new_middle.append(
            '```{#lst-environment-interface .pseudo lst-cap="The Architecture Environment Interface"}'
        )
        continue
    if (
        line.strip() == ":::"
        and len(new_middle) > 0
        and "lst-environment-interface" in new_middle[-10:]
    ):
        # Found the end of the listing
        new_middle.append("```")
        continue

    # We need to add images. We can add F6-environment-tool-interface.svg in 5.2, right after its header.
    new_middle.append(line)

    if line.startswith("## The Semantic Gap: From Unstructured Logs to Observations"):
        new_middle.append(
            '\n![**The Architecture Environment Interface.** An architecture environment connects a system intent to legal actions and translates raw tool outputs into semantic observations. The wrapper checks the request, calls the tool, and parses the result, while the harness records the run and its provenance.](images/F6-environment-tool-interface.svg){#fig-environment-tool-interface fig-alt="A diagram showing how an architecture environment connects an architecture question and workload, an action schema, and declared constraints and metric definitions to a wrapper and harness."}\n'
        )

    if line.startswith("## Executing Intent: Cloud and Bioinformatics Analogies"):
        new_middle.append(
            '\n![**The Chipyard Framework.** A single configuration routes downward to three backend evaluation paths: RTL simulation, VLSI flow, and FPGA emulation. This fan-out ensures one configuration reaches every evaluation path consistently.](images/F6b-chipyard-framework.svg){#fig-chipyard-framework fig-alt="A flow diagram of the Chipyard SoC-generation framework inside one bounding panel."}\n'
        )

rest_of_chapter = lines[idx_5_4:]

# Also we need to fix the reference to the algorithmic interface.
new_middle = "\n".join(new_middle)
new_middle = new_middle.replace(
    "we can formalize this interaction as a standard algorithmic interface, drawing inspiration",
    "we can formalize this interaction as a standard algorithmic interface (@lst-environment-interface), drawing inspiration",
)

# And fix the 'Algorithm Listing' text inside the code block since we changed the boundary
# Original:
# ::: {.callout-note title="Algorithm Listing: The Architecture Environment Interface"}
# **Input:** `action_request` (e.g., target L2 cache size, routing effort)
# **Output:** `observation_vector`, `status_flags`, `provenance_metadata`
# 1. **Validate Action (Read/Action Path):**
# ...
# :::
# We already replaced the opening with ```{#lst-environment-interface ...} and closing with ```.
# We should remove markdown formatting like **Input:** and just make it pseudo-code, but Quarto's .pseudo might support markdown.
# Actually, keeping the markdown inside is fine. Let's just strip the bold and list markers so it looks like code?
# Wait, Quarto's `lst-` just wraps code blocks. Let's leave the content as is, it's just text inside a code block now. Wait, if it's inside ```, markdown rendering is off. So **Input:** will literally render as asterisks.
new_middle = new_middle.replace("**Input:**", "Input:")
new_middle = new_middle.replace("**Output:**", "Output:")
new_middle = new_middle.replace(
    "**Validate Action (Read/Action Path):**", "Validate Action (Read/Action Path):"
)
new_middle = new_middle.replace(
    "**Translate to Tool Commands:**", "Translate to Tool Commands:"
)
new_middle = new_middle.replace(
    "**Asynchronous Execution (Return Path):**", "Asynchronous Execution (Return Path):"
)
new_middle = new_middle.replace("**Data Distillation:**", "Data Distillation:")
new_middle = new_middle.replace("**Return State:**", "Return State:")
new_middle = new_middle.replace("*Check if*", "Check if")
new_middle = new_middle.replace("*If invalid:*", "If invalid:")
new_middle = new_middle.replace("*Lower*", "Lower")
new_middle = new_middle.replace("*Submit*", "Submit")
new_middle = new_middle.replace("*Handle*", "Handle")
new_middle = new_middle.replace(
    "*If infrastructure fails:*", "If infrastructure fails:"
)
new_middle = new_middle.replace("*Parse*", "Parse")
new_middle = new_middle.replace("*Extract*", "Extract")
new_middle = new_middle.replace("*Package*", "Package")


final_content = (
    "\n".join(new_intro) + "\n" + new_middle + "\n" + "\n".join(rest_of_chapter)
)

with open(
    "/Users/VJ/GitHub/Arch2-ch5-rewrite/book/chapters/05-architecture-environments-tool-interfaces/index.qmd",
    "w",
) as f:
    f.write(final_content)
