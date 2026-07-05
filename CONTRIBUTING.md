# Contributing to Architecture 2.0

Architecture 2.0 is built in the open as a community resource: a synthesis
lecture, a living tool registry, workshop tracking, and the shared datasets,
benchmarks, and practices that make AI-assisted architecture research
reproducible. Contributions of all sizes are welcome. Please also read our
[Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

### Add a tool to the registry

Built an open simulator, proxy model, verification harness, or agentic workflow?

1. Open the [Submit a tool](https://github.com/harvard-edge/arch2/issues/new?template=submit_tool.yml) template.
2. Fill in the name, URL, one primary category, and a short public summary.
   The summary is limited to 220 characters because it appears directly on the
   registry card.
3. Optionally add tags, authors, institutions, paper/preprint link,
   documentation link, artifact link, artifact status, and example loop so the
   card gives proper visibility to the work.
4. On submit, an automated check parses the form and opens a pull request adding
   one source file under `tools/registry/` and regenerating `tools/tools.yml`.
   A maintainer reviews it for fit and category, then merges. It appears on the
   site shortly after.

Categories are a fixed set (Simulation, Proxy Models, Agentic Workflows, Data
Representations, Verification, Benchmarks and Datasets, Physical Design) so the registry
filter stays coherent. Use tags for secondary labels. If none of the categories
fit, choose **Not sure / suggest a category** in the issue form and add the
suggested category. The generated pull request will be marked `Needs Triage`
until a maintainer maps it to the final category.

You can validate the registry locally with:

```bash
PYTHONPATH=.github/scripts python .github/scripts/validate_catalog.py
```

### Add a workshop or venue

Organizing a workshop, special session, or recurring venue relevant to
Architecture 2.0, ML for systems, agentic AI, or AI-assisted computer
architecture?

1. Open the [Submit a workshop](https://github.com/harvard-edge/arch2/issues/new?template=submit_workshop.yml) template.
2. Fill in the workshop name, website, venue or host, date, primary topic, and a
   short description.
3. Optionally add location, organizers, institutions, CFP/submission URL, and
   deadline so the card is useful to potential submitters.
4. The workflow opens a pull request adding one source file under
   `www/workshops/` and regenerating `www/workshops.yml`.

Validate the workshop registry locally with:

```bash
PYTHONPATH=.github/scripts python .github/scripts/validate_workshops.py
```

### Add a reading or resource

Submitting a paper, SIGARCH post, podcast, talk, dataset, or other reference
that helps readers orient around Architecture 2.0?

1. Open the [Submit a resource](https://github.com/harvard-edge/arch2/issues/new?template=submit_resource.yml) template.
2. Fill in the resource title, URL, type, primary topic, and short description.
3. Optionally add venue/source, date, authors, and DOI so the card is easy to
   cite and evaluate.
4. The workflow opens a pull request adding one source file under
   `www/readings/` and regenerating `www/readings.yml`.

Validate the reading list locally with:

```bash
PYTHONPATH=.github/scripts python .github/scripts/validate_readings.py
```

### Suggest a book correction

Found a typo, a broken cross-reference, an unclear passage, or a wrong citation?
Open an issue with the **Suggest a book correction** template, or, for a small
fix, open a pull request directly. Book source lives under `book/` as Quarto
Markdown (`.qmd`).

### Report a broken link

Use the **Report a broken link** template. A weekly job also scans for link rot
and files issues automatically.

## Building the site locally

The site is three Quarto projects (`www/`, `tools/`, `book/`) assembled into one:

```bash
# Landing page + registries only (fast, no LaTeX needed):
SKIP_BOOK=1 .github/scripts/build_site.sh
python3 -m http.server 8757 --directory _site   # then open http://localhost:8757/

# Or render a single project:
quarto render www
quarto render tools
```

Rendering the book requires the `arch2` CLI and a LaTeX toolchain; a full build is
`.github/scripts/build_site.sh`. Workflow-owned scripts live under `.github/scripts/`.

## Pull requests

- Keep changes focused and describe what and why.
- Site and registry PRs are checked automatically (registry schema + render).
- Be kind in review. We are all here to build the same thing.

## Branch and release flow

- `dev` is the integration branch. Every push to `dev` runs the pre-commit gate,
  registry validation, and fast site render.
- `main` is the release branch. Updating `main` runs the same pre-commit gate
  first, then performs the full site/book build and GitHub Pages publish.
- Do not promote `dev` to `main` until the `Validate site` workflow is green.
- Local pre-commit and GitHub preflight intentionally run the same hooks:

```bash
pre-commit run --all-files
```

## Contributor recognition

Accepted tools, resources, workshops, corrections, and artifact submissions are
community contributions. Maintainers can credit contributors in the README using
the [All Contributors](https://allcontributors.org/) convention after a PR is
merged.

Thank you for helping build Architecture 2.0.
