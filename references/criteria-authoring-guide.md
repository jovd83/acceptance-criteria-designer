# Criteria Authoring Guide

## Table of Contents

- Format heuristics
- Extraction checklist
- Coverage Quality Score rubric
- Common anti-patterns
- Review checklist

## Format Heuristics

| Situation | Prefer | Why |
|---|---|---|
| User journeys, approvals, stateful UI flows | `Gherkin` | Makes context, trigger, and observable outcome explicit |
| APIs, validation rules, calculations, policies | `TDD-style` | Keeps setup, action, and assertion crisp for rule-oriented behavior |
| Backlog grooming, lightweight stakeholder review | `Sentence-style` | Optimizes readability when a full table would be unnecessary |

If the user names a format, honor it. If not, choose the format that best matches the behavior being described and say what you chose.

## Extraction Checklist

When reading source material, identify:

- actors, personas, or system roles
- actions, triggers, and state transitions
- explicit business rules and constraints
- permissions and authorization rules
- happy path outcomes
- failure paths and validation behavior
- boundary conditions such as limits, ranges, quotas, or time windows
- empty states, missing data behavior, and fallback behavior
- explicitly stated non-functional expectations

Keep explicit facts separate from assumptions. If you infer a reasonable detail, label it as an assumption instead of presenting it as confirmed behavior.

## Coverage Quality Score Rubric

Use an honest integer `CQS` from 0-100. The score is a quick quality signal, not a claim of mathematical certainty.

Score the draft across three dimensions:

- `Behavior coverage` (0-60): distinct testable behaviors from the source are represented.
- `Testability and precision` (0-25): criteria are atomic, observable, and unambiguous.
- `Risk and edge coverage` (0-15): negative paths, permissions, limits, or state transitions are covered when relevant.

Suggested score bands:

- `90-100`: strong coverage with only minor or clearly labeled gaps
- `75-89`: useful draft, but some edge cases or ambiguities remain
- `50-74`: partial coverage or weak precision
- `0-49`: source is too vague or the criteria are not yet reliable

If the source is incomplete, reduce the score instead of inventing missing product behavior.

## Common Anti-Patterns

| Anti-pattern | Why it is weak | Better move |
|---|---|---|
| Multiple behaviors in one criterion | Hard to test and easy to misunderstand | Split into separate criteria |
| Implementation detail disguised as behavior | Couples requirements to a solution choice | Describe externally observable behavior |
| Vague language such as "fast" or "user-friendly" | Not objectively testable | Replace with measurable or observable outcomes |
| Hidden assumptions | Looks authoritative but is not grounded in source | Move assumptions into `assumptions` |
| Missing trigger or action | Leaves test setup incomplete | State what action causes the outcome |
| Happy-path only coverage | Misses real risk | Add negative, boundary, or permission cases when justified |

## Review Checklist

Before finalizing, confirm that:

- each criterion is atomic
- each outcome is externally observable
- each format-specific field is populated with useful content
- assumptions are labeled and gaps are not hidden
- implementation detail is excluded unless explicitly required
- error paths or boundary conditions are included when the source warrants them
