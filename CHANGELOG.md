# Changelog

All notable changes to this repository are documented here.

The format follows Keep a Changelog.

## [3.0.0] - 2026-03-18

### Added

- MIT `LICENSE` for GitHub-ready open-source packaging.
- Author and version metadata in `SKILL.md`.
- Branded SVG icons plus brand color in `agents/openai.yaml`.
- `scripts/forward_test_harness.py` for live runtime-based forward testing.
- `tests/forward/` with runtime-facing smoke cases.

### Changed

- Renamed the skill from `acceptance-criteria-skill` to `acceptance-criteria-designer`.
- Updated docs, prompts, validator rules, and install examples to use the new name.
- Expanded repository validation to cover license, icons, and forward-test cases.

## [2.0.0] - 2026-03-18

### Added

- `agents/openai.yaml` with UI-facing skill metadata.
- `scripts/validate_repo.py` for local metadata, schema, and fixture validation.
- `tests/fixtures/` with realistic input documents and schema-compliant example contracts.
- `references/output-contract.md` to document response structure, field semantics, and ID conventions.

### Changed

- Rewrote `SKILL.md` around explicit modes, output order, guardrails, and memory boundaries.
- Upgraded all JSON schemas to use a richer contract envelope with coverage, assumptions, and scope metadata.
- Strengthened TDD-style outputs by requiring an explicit `action` field instead of only setup and outcome.
- Replaced vague guidance and hidden scoring-loop instructions with an auditable response contract.
- Reworked `README.md` into GitHub-ready documentation with responsibilities, layout, validation, and integration notes.

### Fixed

- Clarified when the skill should trigger and how it should select an output format.
- Removed ambiguity around inferred assumptions versus confirmed requirements.
- Added machine-checkable examples so the repo can demonstrate valid outputs instead of only describing them.

## [1.0.0] - 2026-03-17

### Added

- Initial creation of the Acceptance Criteria skill.
