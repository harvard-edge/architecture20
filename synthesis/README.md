# Architecture 2.0 Synthesis Lecture

This directory contains the Quarto source for **Architecture 2.0: Agentic
Design Loops for Computing System Synthesis**.

Architecture 2.0 treats the architecture design loop itself as the object of
design. The lecture focuses on represented intent, constraints, world models,
tools, feedback, evidence, rejection, and human architectural judgment.

## Local Build

Run commands from this directory:

```bash
./arch2 render
```

That builds both:

- `book/_build/index.html`
- `book/_build/Architecture-2.0.pdf`

Render one target when iterating:

```bash
./arch2 render --to html --no-layout
./arch2 render --to pdf
```

Serve the HTML preview locally:

```bash
python3 -m http.server 8766 --bind 127.0.0.1 --directory book/_build
```

Then open <http://127.0.0.1:8766/>.

## Quality Gates

Use the composed checks before publishing or committing:

```bash
./arch2 check precommit
./arch2 check standard
```

Lower-level checks are grouped by purpose:

```bash
./arch2 validate refs
./arch2 validate citations
./arch2 validate concepts
./arch2 validate disclosure
./arch2 validate svg assets/figures/src
./arch2 verify figures
./arch2 verify html
./arch2 layout scan
```

Install the local commit hook with:

```bash
pip install pre-commit
pre-commit install
```

## Repository Layout

```text
synthesis/
├── arch2                         # CLI wrapper
├── cli/                          # arch2 command implementation
├── book/                         # Quarto book source
│   ├── _quarto.yml
│   ├── index.qmd
│   ├── chapters/
│   ├── appendices/
│   ├── csl/
│   ├── scripts/
│   └── tex/
├── assets/figures/               # SVG sources and generated PDF figures
├── data/                         # checked-in receipts and small datasets
├── references/                   # bibliography and source notes
└── scripts/                      # corpus and analysis helpers
```

Generated build output is intentionally ignored under `book/_build/`.

## Review Loop

The `arch2 loop` commands create source-grounded review packets and triage
reports for manuscript improvement:

```bash
./arch2 loop packet --focus progressive-disclosure
./arch2 loop review --reviewer gemini --model gemini-3.1-pro-preview
./arch2 loop triage
./arch2 loop learn
```

Loop artifacts are local working files under `.arch2/reviews/loop/` and should
not be committed.
