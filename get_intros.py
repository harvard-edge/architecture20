import glob
import re

chapters = sorted(glob.glob("book/chapters/*/index.qmd"))
with open("intro_dump.txt", "w") as out:
    for ch in chapters:
        with open(ch, "r") as f:
            content = f.read()

        match = re.search(
            r"::: \{?\.callout-crux.*?:::.*?^\s*$(.*?)^## ",
            content,
            re.DOTALL | re.MULTILINE,
        )
        if match:
            intro_text = match.group(1).strip()
            # Only dump the text parts, strip code blocks out
            cleaned = re.sub(
                r"```.*?```", "[CODE BLOCK OMITTED]", intro_text, flags=re.DOTALL
            )
            out.write(f"=== {ch} ===\n")
            out.write(cleaned + "\n\n")
