# Acceptance Criteria Designer

[![Validate Skills](https://github.com/jovd83/acceptance-criteria-designer/actions/workflows/ci.yml/badge.svg)](https://github.com/jovd83/acceptance-criteria-designer/actions/workflows/ci.yml)
[![version](https://img.shields.io/badge/version-3.0.0-blue)](CHANGELOG.md)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20Me%20a%20Coffee-ffdd00?style=flat&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jovd83)

Turn raw product intent into testable acceptance criteria and a machine-readable contract.

This repository packages an Agent Skill for drafting, refining, reviewing, and converting acceptance criteria from user stories, PRD excerpts, tickets, use cases, business rules, and existing requirement artifacts. The skill supports Gherkin, TDD-style, and sentence-based outputs and always pairs the human-readable result with a JSON contract that matches the bundled schemas.

## What This Skill Does

- Converts ambiguous requirements into explicit, testable acceptance criteria.
- Reviews weak or incomplete criteria and calls out gaps, assumptions, and edge cases.
- Converts criteria between Gherkin, TDD-style, and sentence-based representations.
- Emits schema-aligned JSON artifacts that downstream tools can validate or transform.

## Responsibilities and Boundaries

This skill is responsible for acceptance-criteria design and review.

It is not responsible for:

- writing full PRDs or product strategy documents
- generating full automation suites
- storing cross-project memory or global conventions
- acting as a requirements management system

When persistent memory is needed, keep it local to the project on request or delegate cross-project reuse to a separate shared-memory skill.

## Supported Formats

| Format | Best fit | Human-readable output | JSON item fields |
|---|---|---|---|
| `Gherkin` | user flows, stateful behavior, BDD-oriented review | `ID \| Title \| Given \| When \| Then` | `id`, `title`, `given`, `when`, `then` |
| `TDD-style` | API rules, validation logic, calculations, business constraints | `ID \| Title \| Setup \| Action \| Expected Outcome` | `id`, `title`, `setup`, `action`, `expected_outcome` |
| `Sentence-style` | backlog refinement, lightweight stakeholder review | Markdown list | `id`, `category`, `sentence` |

## Installation

If you publish this repository to GitHub, install it with the Agent Skills CLI:

```bash
npx skills add <owner>/acceptance-criteria-designer
```

Manual installation also works:

```bash
git clone <repo-url> ~/.agents/skills/acceptance-criteria-designer
```

Because the repository root is the skill root, place the entire folder directly in the agent's skills directory.

## Repository Layout

```text
LICENSE
SKILL.md
agents/
  openai.yaml
assets/
  acceptance-criteria-designer-small.svg
  acceptance-criteria-designer.svg
  acceptance_criteria_gherkin.json
  acceptance_criteria_tdd.json
  acceptance_criteria_sentences.json
references/
  criteria-authoring-guide.md
  output-contract.md
scripts/
  forward_test_harness.py
  validate_repo.py
tests/
  fixtures/
  forward/
```

## Validation

Run the structural validator before publishing or after making changes:

```bash
python scripts/validate_repo.py
```

The validator checks:

- core skill metadata
- UI metadata in `agents/openai.yaml`
- icon assets and MIT license presence
- schema structure in `assets/`
- example contracts in `tests/fixtures/`
- forward-test case definitions in `tests/forward/`

## Forward Testing

The live harness runs real prompts through another agent runtime and validates the returned JSON contract against this repo's schemas.

Use any runtime that can accept a prompt file and optionally write a response file:

```bash
python scripts/forward_test_harness.py --runner "your-agent-runtime --prompt-file {prompt_file} --output-file {output_file}"
```

Available placeholders in `--runner`:

- `{prompt_file}`
- `{output_file}`
- `{skill_root}`
- `{skill_name}`
- `{case_id}`

If your runtime prints to stdout instead of writing an output file, omit `{output_file}` and the harness will capture stdout.

## Memory Model

- Runtime memory: extracted behaviors, assumptions, and coverage notes for the current task only.
- Project-local persistence: optional and deliberate; create local artifacts only when the user asks.
- Shared memory: out of scope for this repository and best handled by a separate shared-memory capability.

## Optional Integrations

This repository intentionally keeps integrations lightweight. It can be paired with:

- a shared-memory skill for reusable cross-project conventions
- issue-tracker or test-management skills for exporting approved criteria elsewhere
- automation-focused skills that transform approved acceptance criteria into executable tests

Those integrations are optional and not bundled into this skill.

## Future Concepts

These are reasonable future additions, but they are not implemented in this repository today:

- requirement-diff workflows that compare criteria across revisions
- importers for tickets, PRDs, or backlog systems
- traceability exporters that map criteria to downstream test assets

## Contributing

Keep the skill lean and auditable:

- update `SKILL.md`, schemas, fixtures, and forward cases together when the output contract changes
- prefer explicit guardrails over vague prose
- run `python scripts/validate_repo.py` before opening a pull request
- use `python scripts/forward_test_harness.py --dry-run` to inspect generated prompts before live execution
