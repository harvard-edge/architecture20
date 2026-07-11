# Design-Loop Card Contract

`design-loop-card.v1.1.schema.json` is the current canonical machine contract
for the twelve-field Architecture 2.0 design-loop card. The document-level
`schema_version` and card-level `card_id` and `conformance_level` values are
metadata. They do not add ontology fields.

Version `1.1` follows the cumulative conformance levels in Appendix B.

| Level | Required content |
| --- | --- |
| 0 | Nonempty intent boundaries and design-space choices, with card metadata and task |
| 1 | Nonempty representation, environment, actor map, feedback budget, evidence, and failed-run or rejected-alternative entries under `negative_traces`, with at least one evaluation |
| 2 | Stable state, environment, evidence, workload, and candidate IDs, a SHA-256 parameter digest, and a replay source URI; these are replay bindings, not proof that replay succeeds |
| 3 | Claimed independent rejection authority, commitment boundary, and accountable decision under `human_decision`; these fields do not prove independence or decision quality |

The optional claim and non-claim view belongs at `intent.claim_boundary`. A
namespaced experimental extension may use a top-level card key beginning with
`x-`, such as `x-example.org-review`. Consumers must not treat an extension as
one of the twelve canonical fields.

Version `1.1` tightens conformance after version `1.0` accepted structurally
present but empty Level 1 records and weak Level 2 provenance. Because that
change rejects some previously accepted documents, it is a new contract version
rather than an in-place edit. The CLI still dispatches `schema_version: "1.0"`
to `design-loop-card.v1.schema.json` for legacy records. New cards should emit
`schema_version: "1.1"`.

Future documentation-only corrections may clarify descriptions, diagnostics,
and examples without changing accepted documents. A new field, enum value,
required property, or meaningful validation change requires a new schema
version and compatibility note. Validators reject unknown schema versions
rather than guessing.

Validate a YAML or JSON card from the repository root.

```console
./arch2 validate card path/to/card.yaml
```
