---
name: acceptance-criteria-designer
description: Draft, refine, normalize, critique, and convert acceptance criteria from user stories, PRDs, requirements, use cases, business rules, tickets, or existing criteria. Use when Codex needs to turn product behavior into testable Gherkin, TDD-style, or sentence-based acceptance criteria, identify assumptions and coverage gaps, or return a JSON contract aligned to the bundled schemas.
license: MIT
metadata:
  author: jovd83
  version: "3.0.0"
  dispatcher-output-artifacts: acceptance_criteria, criteria_review, normalized_criteria_json
  dispatcher-risk: low
  dispatcher-writes-files: true
  dispatcher-input-artifacts: requirements, user_story, acceptance_criteria, product_constraints
  dispatcher-capabilities: acceptance-criteria-design, requirements-clarification, criteria-format-conversion
  dispatcher-stack-tags: analysis, testing, product
  dispatcher-accepted-intents: design_acceptance_criteria, review_acceptance_criteria, convert_acceptance_criteria
  dispatcher-category: analysis
---
# Acceptance Criteria Designer

Use this skill to turn feature intent into clear, testable, reviewable acceptance criteria without inventing unsupported behavior.

## Responsibilities

- Generate acceptance criteria from raw requirements.
- Tighten or critique existing acceptance criteria.
- Convert criteria between Gherkin, TDD-style, and sentence-based formats.
- Return a human-readable deliverable plus a schema-aligned JSON contract.
- Surface assumptions, uncovered gaps, and high-risk edge cases.

## Inputs

Accept any of the following:

- user stories, PRD excerpts, tickets, use cases, API notes, business rules, or policy text
- draft acceptance criteria that need review, normalization, or conversion
- optional preferred format, terminology, risk focus, or delivery constraints

If the request is too vague to produce reliable criteria, ask only for the smallest missing detail needed to avoid fabricating requirements.

## Format Selection

- Honor an explicitly requested format.
- Otherwise use:
  - `Gherkin` for user workflows, stateful interactions, or BDD-friendly feature behavior
  - `TDD-style` for business rules, API behavior, validations, calculations, and data constraints
  - `Sentence-style` for lightweight backlog refinement or quick stakeholder review
- If two formats are equally plausible and the choice would materially change the deliverable, ask one brief clarification. Otherwise choose the best fit and state it.

## Workflow

1. Read the source material and extract:
   - actor or system role
   - trigger or action
   - business rules and constraints
   - success outcomes
   - failure paths
   - permissions and roles
   - boundary values and state transitions
   - explicit non-functional expectations
2. Separate source facts from inference.
   - Keep explicit source behavior authoritative.
   - Put reasonable inferred details in `assumptions`.
   - Put unknown or unsupported items in `coverage_assessment.gaps` or ask a short clarification if the gap blocks a reliable answer.
3. Choose the working mode:
   - `generate` from raw source material
   - `refine` weak draft criteria
   - `review` existing criteria for gaps and quality issues
   - `convert` between supported formats
   - `schema` when the user asks for raw JSON schema contents
4. Draft atomic criteria.
   - Each criterion should cover one observable behavior or one tightly related condition and outcome pair.
   - Split compound requirements into multiple criteria.
   - Prefer externally observable behavior over implementation detail.
5. Add risk-based coverage where it is justified by the source or domain:
   - invalid input
   - boundary limits
   - unauthorized access
   - empty or missing data states
   - state transitions or idempotency
   - failure messaging or fallback behavior
6. Revise silently once or twice if obvious gaps remain.
   - Do not expose chain-of-thought, hidden scratch work, or private scoring loops.
7. Produce the final response in this order:
   - `Scope summary`
   - `Assumptions` if non-empty
   - `Acceptance criteria`
   - `JSON contract`
   - `Coverage summary`

## Output Rules

### Human-readable criteria

- `Gherkin`: render a Markdown table with `ID | Title | Given | When | Then`.
- `TDD-style`: render a Markdown table with `ID | Title | Setup | Action | Expected Outcome`.
- `Sentence-style`: render a Markdown list as `- [ID] [category] criterion`.

### JSON contract

Always emit a JSON code block after the human-readable criteria.
Use the matching schema from `assets/`:

- `assets/acceptance_criteria_gherkin.json`
- `assets/acceptance_criteria_tdd.json`
- `assets/acceptance_criteria_sentences.json`

Every contract must include:

- `schema_version`
- `format`
- `source_summary`
- `assumptions`
- `out_of_scope`
- `coverage_assessment`
- `acceptance_criteria`

### Coverage summary

Report a concise `Coverage Quality Score (CQS)` from 0-100 using the rubric in `references/criteria-authoring-guide.md`. Keep the score honest and explain major remaining gaps if the source was incomplete.

## Gotchas

- **Format Confusion**: Ensure the output format (Gherkin vs TDD vs Sentence) remains consistent throughout the entire response. Mixing them up causes downstream confusion.
- **JSON Schema Strictness**: The JSON contract must strictly adhere to the schemas in `assets/`. Missing mandatory fields like `coverage_assessment` or `schema_version` will cause contract validation failures.
- **Inference vs. Fact**: Avoid silently blurring the line between explicit source facts and inferred behavior, which happens often with vague source texts. Any inferred behavior must be explicitly logged in the `assumptions` array.
- **Over-Specification**: Avoid embedding UI-specific details (e.g., "click the blue submit button") in behavioral criteria unless explicitly present in the source text. Keep criteria focused on observable system behavior.

## Guardrails

- Do not invent business rules that conflict with or go beyond the source without labeling them as assumptions or follow-up gaps.
- Do not encode implementation details unless the source explicitly requires them.
- Do not merge unrelated behaviors into a single criterion.
- Do not treat suggested improvements as confirmed requirements.
- When reviewing existing criteria, preserve intent and call out defects before rewriting.
- If the user asks for a raw schema, print the requested schema file contents exactly and do not wrap it in commentary unless the user also asked for explanation.

## Memory Model

- Keep extracted behaviors, assumptions, and coverage notes in runtime memory for the current task only.
- Create project-local artifacts only when the user asks to persist criteria, traceability, or review output in the repository.
- Treat cross-project conventions as external shared memory; do not automatically promote local findings into shared memory.

## References

Read these only when they help:

- `references/criteria-authoring-guide.md` for format heuristics, quality rubric, edge-case checklist, and anti-patterns
- `references/output-contract.md` for field semantics, ID conventions, and response mapping
- `tests/fixtures/` for valid example inputs and JSON contracts
- `tests/forward/` for live forward-test prompts and runtime-facing smoke cases
- `scripts/validate_repo.py` to validate metadata, schemas, and example contracts locally
- `scripts/forward_test_harness.py` to exercise the skill through another agent runtime
