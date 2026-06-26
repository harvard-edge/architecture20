# Architecture 2.0

Public materials for Architecture 2.0.

The current book and preview site live in `synthesis/`:

```bash
cd synthesis
./arch2 render
```

The intended public site is:

<https://arch2.mlsysbook.ai>

This repository is organized as an umbrella so future Architecture 2.0 material
can live beside the synthesis lecture without renaming the project.

## Layout

```text
arch2/
├── synthesis/     # Architecture 2.0 synthesis lecture and Quarto site
└── .github/       # GitHub Pages build workflow
```

## Local Preview

```bash
cd synthesis
./arch2 render --to html --no-layout
python3 -m http.server 8766 --bind 127.0.0.1 --directory book/_build
```

Then open <http://127.0.0.1:8766/>.

## Publishing

The GitHub Pages workflow renders the Quarto book from `synthesis/book/` and
publishes `synthesis/book/_build/`.

The workflow writes `arch2.mlsysbook.ai` as the Pages custom-domain `CNAME`.
DNS still needs a matching CNAME record at the DNS host for `mlsysbook.ai`.
