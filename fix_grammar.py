import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# Fix grammar from em-dash replacement
text = text.replace(
    "Can an environment wrapper automatically deploy multi-fidelity simulators. They could use fast",
    "Can an environment wrapper automatically deploy multi-fidelity simulators? They could use fast",
)

text = text.replace(
    'purely as "Environment Parsers." These models would ingest',
    'purely as "Environment Parsers"? These models would ingest',
)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(text)

print("Done")
