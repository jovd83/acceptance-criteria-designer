# Output Contract

## Response Order

Use this order in the final answer:

1. `Scope summary`
2. `Assumptions` when non-empty
3. `Acceptance criteria`
4. `JSON contract`
5. `Coverage summary`

## Top-Level JSON Fields

Every JSON contract must contain these fields:

| Field | Purpose |
|---|---|
| `schema_version` | Contract version for downstream consumers |
| `format` | One of `gherkin`, `tdd`, or `sentences` |
| `source_summary` | Short plain-language summary of what the source describes |
| `assumptions` | Reasonable inferred details that were not explicit in the source |
| `out_of_scope` | Adjacent behavior intentionally excluded from the generated criteria |
| `coverage_assessment` | Summary of score, covered behaviors, and unresolved gaps |
| `acceptance_criteria` | Format-specific criteria items |

## Format-Specific Criteria Items

### Gherkin

Use:

- `id`
- `title`
- `given`
- `when`
- `then`

### TDD-style

Use:

- `id`
- `title`
- `setup`
- `action`
- `expected_outcome`

### Sentence-style

Use:

- `id`
- `category`
- `sentence`

Allowed `category` values:

- `functional`
- `validation`
- `permission`
- `error`
- `boundary`
- `state`
- `integration`
- `nfr`

## ID Conventions

- `AC-GHK-001` for Gherkin
- `AC-TDD-001` for TDD-style
- `AC-SNT-001` for sentence-style

Use three-digit, sequential numbering within a single response.

## Handling Ambiguity

- Put reasonable inference in `assumptions`.
- Put unresolved uncertainty in `coverage_assessment.gaps`.
- Use `out_of_scope` only for clearly adjacent behavior that the source does not ask you to define.
- If ambiguity blocks a reliable answer, ask a short clarification instead of fabricating precision.

## Multi-Format Requests

If the user requests more than one format:

- keep `source_summary`, `assumptions`, `out_of_scope`, and `coverage_assessment` semantically aligned across formats
- emit one human-readable section and one JSON code block per format
- do not let one format invent behaviors that the others omit
