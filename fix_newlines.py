import re

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "r"
) as f:
    text = f.read()

# Add blank lines before headers that don't have them
text = re.sub(r"([^\n])\n(## )", r"\1\n\n\2", text)

with open(
    "book/chapters/05-architecture-environments-tool-interfaces/index.qmd", "w"
) as f:
    f.write(text)

print("Done")
