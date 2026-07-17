import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# 1. Fix explanatory colons
text = text.replace(
    "The wrapper acts as a protective boundary: it intercepts the high-level request",
    "The wrapper acts as a protective boundary. It intercepts the high-level request",
)
text = text.replace(
    "a critical philosophical question arises: do we throw all the traditional simulation and EDA data overboard",
    "a critical philosophical question arises. Do we throw all the traditional simulation and EDA data overboard",
)

# 2. Fix em-dashes
text = text.replace(
    "intent---whether proposing a new cache hierarchy or adjusting a prefetcher---it must",
    "intent (whether proposing a new cache hierarchy or adjusting a prefetcher) it must",
)
text = text.replace(
    "tools---like CACTI for memory modeling [@MuralimanoharEtAl2009CACTI], DRAMSys for memory controllers [@WeisEtAl2021DRAMSys], or gem5 for full-system simulation [@BinkertEtAl2011gem5]---were",
    "tools such as CACTI for memory modeling [@MuralimanoharEtAl2009CACTI], DRAMSys for memory controllers [@WeisEtAl2021DRAMSys], or gem5 for full-system simulation [@BinkertEtAl2011gem5] were",
)
text = text.replace(
    "change---inserting a specialized Tensor Core accelerator block---is",
    "change of inserting a specialized Tensor Core accelerator block is",
)
text = text.replace(
    "physics---timing closure, thermal limits, memory bandwidth, and physical routing congestion.",
    "physics, including timing closure, thermal limits, memory bandwidth, and physical routing congestion.",
)
text = text.replace(
    'reconciliation"---the user declares', 'reconciliation." The user declares'
)
text = text.replace(
    "wrapper---which blocks execution until a scalar reward is returned---is fundamentally",
    "wrapper (which blocks execution until a scalar reward is returned) is fundamentally",
)
text = text.replace(
    "failures---such as failing to meet a timing constraint in synthesis, or causing a thermal violation in the system's 3 W envelope---should be",
    "failures, such as failing to meet a timing constraint in synthesis or causing a thermal violation in the system's 3 W envelope, should be",
)
text = text.replace(
    "output---often tens of thousands",
    "output. These logs often contain tens of thousands",
)
text = text.replace(
    "boundaries---from the compiler's intermediate representation to the final physical design signoff.",
    "boundaries, extending from the compiler's intermediate representation to the final physical design signoff.",
)
text = text.replace(
    'Parsers"---models that ingest', 'Parsers." These models would ingest'
)
text = text.replace(
    "simulators---using fast, cycle-approximate",
    "simulators. They could use fast, cycle-approximate",
)

# 3. Fix one-off sentences (merge them to form proper paragraphs with thesis statements)

text = text.replace(
    "Asynchronous, Scarce, and Protected Tool Chains are critical. A blocking synchronous call will inevitably time out or hang when a placement job takes 40 hours, or waits three days for an EDA license checkout.\n\nInstead, real tool chains require asynchronous, scarce, and protected execution mechanics. Long simulations,",
    "Because a blocking synchronous call will inevitably time out or hang when a placement job takes 40 hours or waits three days for an EDA license checkout, real tool chains require asynchronous, scarce, and protected execution mechanics. Long simulations,",
)

text = text.replace(
    "Furthermore, distinguishing Tool Failures from Design Failures is necessary. A critical requirement of this asynchronous system is explicitly distinguishing between an **infrastructure failure** and an **architectural constraint violation**.\n\nIf an AI proposes an SRAM configuration",
    "A critical requirement of this asynchronous system is explicitly distinguishing between an **infrastructure failure** and an **architectural constraint violation**. If an AI proposes an SRAM configuration",
)

text = text.replace(
    "To balance determinism versus reproducibility, we must consider costs, operational fidelity, nondeterminism, and integrity.\n\nTwo post-route attempts",
    "To balance determinism versus reproducibility, we must consider costs, operational fidelity, nondeterminism, and integrity. Two post-route attempts",
)

text = text.replace(
    "A major issue is the attention bottleneck in LLM-Driven Architecture.\n\nWhen interfacing Large Language Models (LLMs) with traditional architecture environments, a fundamental impedance mismatch occurs at the observation layer.",
    "When interfacing Large Language Models (LLMs) with traditional architecture environments, a fundamental impedance mismatch occurs at the observation layer.",
)

text = text.replace(
    "This highlights the need for distilling massive logs into semantic observations.\n\nA critical requirement of the Return Path is **Data Distillation**. Traditional architecture and EDA tools are excessively verbose.",
    "A critical requirement of the Return Path is **Data Distillation**, because traditional architecture and EDA tools are excessively verbose.",
)

text = text.replace(
    "Ultimately, we must build and maintain a robust architecture environment.\n\nBy demanding distinct read, action, and return paths, the environment guarantees that architectural intent survives across domain boundaries",
    "By demanding distinct read, action, and return paths, a robust architecture environment guarantees that architectural intent survives across domain boundaries",
)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(text)

print("Done")
