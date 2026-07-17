import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# The current headers are:
# 1. ## The Origin Mismatch: Human Intuition vs. AI APIs
# 2. ## The Semantic Gap: From Unstructured Logs to Observations
# 3. ## Executing Intent: Orchestrating Complex Toolchains
# 4. ## Killing the Synchronous `env.step()`
# 5. ## The Economic Reality of EDA
# 6. ## The Attention Bottleneck and Data Distillation
# 7. ## Open Research Questions
# 8. ## Conclusion

# Let's extract the content of each section
sections = re.split(r"\n## ", text)

header = sections[0]
s_origin = None
s_semantic = None
s_executing = None
s_killing = None
s_economic = None
s_attention = None
s_open = None
s_conclusion = None

for sec in sections[1:]:
    if sec.startswith("The Origin Mismatch"):
        s_origin = sec
    elif sec.startswith("The Semantic Gap"):
        s_semantic = sec
    elif sec.startswith("Executing Intent"):
        s_executing = sec
    elif sec.startswith("Killing the Synchronous"):
        s_killing = sec
    elif sec.startswith("The Economic Reality"):
        s_economic = sec
    elif sec.startswith("The Attention Bottleneck"):
        s_attention = sec
    elif sec.startswith("Open Research Questions"):
        s_open = sec
    elif sec.startswith("Conclusion"):
        s_conclusion = sec

# Now let's inject transition sentences to smooth the flow.

# 1 -> 2 transition (Origin to Economic)
# End of s_origin: "...which states are invalid, and which runs can be repeated."
s_origin += "\n\nThis insufficiency of basic tool permissions is severely compounded by the harsh economic reality of the tools themselves."

# 2 -> 3 transition (Economic to Killing)
# End of s_economic: "...Architecture 2.0 must adopt similar best practices for tool execution, ensuring strict data provenance and reproducible environment snapshots."
s_economic += "\n\nHowever, ensuring data provenance and reproducibility is impossible if the agent expects instant feedback. The sheer cost and latency of EDA tools requires a fundamental shift in execution mechanics."

# 3 -> 4 transition (Killing to Semantic)
# End of s_killing: "...should be passed back to the AI as negative design feedback."
s_killing += "\n\nBut how exactly do we pass this feedback back safely, without corrupting the AI's world model? This brings us to the core interface design."

# 4 -> 5 transition (Semantic to Attention)
# End of s_semantic: "...Package observation_vector, status_flags, and exact tool hashes." (Algorithm block ends)
# Actually, the algorithm block ends it. Let's add text after the algorithm block.
s_semantic += "\n\nThe Return Path described above is the most critical juncture. But capturing the return safely is only the first step; we must also ensure the AI can comprehend it."

# 5 -> 6 transition (Attention to Executing)
# End of s_attention: "...reliable foundation upon which generative models and optimization algorithms can operate independently."
s_attention += "\n\nOnce a single robust environment can distill observations for a specific tool, the final challenge is scaling up. An architect rarely runs just one tool; they run a sequence."

# Reassemble in the new order:
# 1. Origin
# 2. Economic
# 3. Killing
# 4. Semantic
# 5. Attention
# 6. Executing
# 7. Open
# 8. Conclusion

new_text = (
    header
    + "\n## "
    + s_origin
    + "\n## "
    + s_economic
    + "\n## "
    + s_killing
    + "\n## "
    + s_semantic
    + "\n## "
    + s_attention
    + "\n## "
    + s_executing
    + "\n## "
    + s_open
    + "\n## "
    + s_conclusion
)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(new_text)

print("Done")
