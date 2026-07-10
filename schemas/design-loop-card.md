# Design-Loop Card Contract

`design-loop-card.v1.schema.json` is the canonical machine contract for the
twelve-field Architecture 2.0 design-loop card. The document-level
`schema_version` and card-level `card_id` and `conformance_level` values are
metadata. They do not add ontology fields.

Version `1.0` follows the cumulative conformance levels in Appendix B.

| Level | Required content |
| --- | --- |
| 0 | Intent, task, and design space, with card metadata |
| 1 | Representation, environment, method role, feedback budget, evidence, and negative traces |
| 2 | Stable state, environment, evidence, workload, candidate, tool-version, and parameter-hash identifiers needed for replay |
| 3 | Independent rejection authority, commitment boundary, and human decision |

The optional research claim view belongs at `intent.claim_boundary`. A
namespaced experimental extension may use a top-level card key beginning with
`x-`, such as `x-example.org-review`. Consumers must not treat an extension as
one of the twelve canonical fields.

Patch releases may clarify descriptions, diagnostics, and examples without
changing accepted documents. A new field, enum value, required property, or
meaningful validation change requires a new schema version and compatibility
note. Validators reject unknown schema versions rather than guessing.

Validate a YAML or JSON card from the repository root.

```console
./arch2 validate card path/to/card.yaml
```
