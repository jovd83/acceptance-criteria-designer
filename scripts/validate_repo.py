#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / "SKILL.md"
README_PATH = ROOT / "README.md"
LICENSE_PATH = ROOT / "LICENSE"
OPENAI_YAML_PATH = ROOT / "agents" / "openai.yaml"
FIXTURES_DIR = ROOT / "tests" / "fixtures"
FORWARD_CASES_DIR = ROOT / "tests" / "forward"

EXPECTED_FRONTMATTER_KEYS = {"name", "description", "license", "metadata"}
EXPECTED_TOP_LEVEL_FIELDS = {
    "schema_version",
    "format",
    "source_summary",
    "assumptions",
    "out_of_scope",
    "coverage_assessment",
    "acceptance_criteria",
}
EXPECTED_COVERAGE_FIELDS = {"score", "covered_behaviors", "gaps"}
EXPECTED_ITEM_FIELDS = {
    "gherkin": {"id", "title", "given", "when", "then"},
    "tdd": {"id", "title", "setup", "action", "expected_outcome"},
    "sentences": {"id", "category", "sentence"},
}
ID_PATTERNS = {
    "gherkin": re.compile(r"^AC-GHK-[0-9]{3}$"),
    "tdd": re.compile(r"^AC-TDD-[0-9]{3}$"),
    "sentences": re.compile(r"^AC-SNT-[0-9]{3}$"),
}
SCHEMA_PATHS = {
    "gherkin": ROOT / "assets" / "acceptance_criteria_gherkin.json",
    "tdd": ROOT / "assets" / "acceptance_criteria_tdd.json",
    "sentences": ROOT / "assets" / "acceptance_criteria_sentences.json",
}
ALLOWED_SENTENCE_CATEGORIES = {
    "functional",
    "validation",
    "permission",
    "error",
    "boundary",
    "state",
    "integration",
    "nfr",
}
README_HEADINGS = [
    "## What This Skill Does",
    "## Responsibilities and Boundaries",
    "## Supported Formats",
    "## Installation",
    "## Validation",
    "## Forward Testing",
    "## Memory Model",
    "## Optional Integrations",
    "## Future Concepts",
]
EXPECTED_ICON_FIELDS = {"icon_small", "icon_large"}


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if len(lines) < 3 or lines[0].strip() != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter.")

    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise ValueError("SKILL.md frontmatter is not closed with '---'.")

    data: dict[str, Any] = {}
    current_parent: str | None = None

    for line in lines[1:end_index]:
        if not line.strip():
            continue

        if line.startswith("  "):
            if current_parent != "metadata" or ":" not in line:
                raise ValueError(f"Invalid nested frontmatter line: {line!r}")
            key, raw_value = line.strip().split(":", 1)
            data.setdefault("metadata", {})[key.strip()] = raw_value.strip().strip('"')
            continue

        if ":" not in line:
            raise ValueError(f"Invalid frontmatter line: {line!r}")

        key, raw_value = line.split(":", 1)
        key = key.strip()
        raw_value = raw_value.strip()

        if raw_value:
            data[key] = raw_value.strip('"')
            current_parent = None
        else:
            data[key] = {}
            current_parent = key
    return data


def parse_openai_yaml(text: str) -> dict[str, str]:
    def extract(field: str) -> str:
        match = re.search(rf'^\s*{re.escape(field)}:\s*"(.+)"\s*$', text, re.MULTILINE)
        if not match:
            raise ValueError(f"Missing quoted field '{field}' in agents/openai.yaml.")
        return match.group(1)

    if not re.search(r"^interface:\s*$", text, re.MULTILINE):
        raise ValueError("agents/openai.yaml must contain an 'interface' block.")

    data = {
        "display_name": extract("display_name"),
        "short_description": extract("short_description"),
        "brand_color": extract("brand_color"),
        "default_prompt": extract("default_prompt"),
    }
    for field in EXPECTED_ICON_FIELDS:
        data[field] = extract(field)
    return data


def ensure_non_empty_string(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{label} must be a non-empty string.")


def ensure_string_list(value: Any, label: str, errors: list[str], *, min_items: int = 0) -> None:
    if not isinstance(value, list):
        errors.append(f"{label} must be an array.")
        return
    if len(value) < min_items:
        errors.append(f"{label} must contain at least {min_items} item(s).")
    for index, item in enumerate(value):
        ensure_non_empty_string(item, f"{label}[{index}]", errors)


def validate_skill_file(errors: list[str]) -> None:
    text = load_text(SKILL_PATH)
    try:
        metadata = parse_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        return

    if set(metadata) != EXPECTED_FRONTMATTER_KEYS:
        errors.append(
            "SKILL.md frontmatter must contain exactly name, description, license, and metadata."
        )

    if metadata.get("name") != "acceptance-criteria-designer":
        errors.append("SKILL.md name must be 'acceptance-criteria-designer'.")

    ensure_non_empty_string(metadata.get("description"), "SKILL.md description", errors)
    if metadata.get("license") != "MIT":
        errors.append("SKILL.md license must be 'MIT'.")

    nested_metadata = metadata.get("metadata")
    if not isinstance(nested_metadata, dict):
        errors.append("SKILL.md metadata block must contain author and version.")
        nested_metadata = {}

    ensure_non_empty_string(nested_metadata.get("author"), "SKILL.md metadata.author", errors)
    version = nested_metadata.get("version", "")
    if not re.match(r"^[0-9]+\.[0-9]+\.[0-9]+$", version):
        errors.append("SKILL.md metadata.version must use semantic versioning, for example 3.0.0.")

    for required_phrase in (
        "Gherkin",
        "TDD-style",
        "sentence-based acceptance criteria",
        "JSON contract",
    ):
        if required_phrase not in metadata.get("description", ""):
            errors.append(
                f"SKILL.md description should mention '{required_phrase}' to improve triggering."
            )

    for section in (
        "## Responsibilities",
        "## Format Selection",
        "## Workflow",
        "## Output Rules",
        "## Guardrails",
        "## Memory Model",
    ):
        if section not in text:
            errors.append(f"SKILL.md is missing required section '{section}'.")


def validate_readme(errors: list[str]) -> None:
    text = load_text(README_PATH)
    for heading in README_HEADINGS:
        if heading not in text:
            errors.append(f"README.md is missing heading '{heading}'.")

    if "acceptance-criteria-designer" not in text:
        errors.append("README.md should use the renamed skill identifier.")


def validate_license(errors: list[str]) -> None:
    text = load_text(LICENSE_PATH)
    if "MIT License" not in text:
        errors.append("LICENSE must contain the MIT License text.")
    if "Permission is hereby granted, free of charge" not in text:
        errors.append("LICENSE does not look like a complete MIT license.")


def validate_openai_yaml(errors: list[str]) -> None:
    try:
        data = parse_openai_yaml(load_text(OPENAI_YAML_PATH))
    except ValueError as exc:
        errors.append(str(exc))
        return

    ensure_non_empty_string(data["display_name"], "openai.display_name", errors)
    ensure_non_empty_string(data["short_description"], "openai.short_description", errors)
    ensure_non_empty_string(data["brand_color"], "openai.brand_color", errors)
    ensure_non_empty_string(data["default_prompt"], "openai.default_prompt", errors)

    if not (25 <= len(data["short_description"]) <= 64):
        errors.append("openai.short_description must be 25-64 characters long.")

    if "$acceptance-criteria-designer" not in data["default_prompt"]:
        errors.append("openai.default_prompt must mention '$acceptance-criteria-designer'.")

    if not re.match(r"^#[0-9A-Fa-f]{6}$", data["brand_color"]):
        errors.append("openai.brand_color must be a 6-digit hex color.")

    for field in EXPECTED_ICON_FIELDS:
        icon_path = ROOT / data[field].replace("./", "", 1)
        if not icon_path.exists():
            errors.append(f"Referenced {field} asset does not exist: {data[field]}")


def validate_schema_file(fmt: str, path: Path, errors: list[str]) -> None:
    try:
        schema = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc}")
        return

    properties = schema.get("properties")
    if not isinstance(properties, dict):
        errors.append(f"{path.name} must define a top-level properties object.")
        return

    required_fields = set(schema.get("required", []))
    if required_fields != EXPECTED_TOP_LEVEL_FIELDS:
        errors.append(f"{path.name} must require the full top-level contract envelope.")

    if properties.get("schema_version", {}).get("const") != "2.0.0":
        errors.append(f"{path.name} must lock schema_version to 2.0.0.")

    if properties.get("format", {}).get("const") != fmt:
        errors.append(f"{path.name} must lock format to '{fmt}'.")

    if "acceptance-criteria-designer" not in schema.get("description", ""):
        errors.append(f"{path.name} should describe the renamed skill.")

    coverage = properties.get("coverage_assessment", {})
    if set(coverage.get("required", [])) != EXPECTED_COVERAGE_FIELDS:
        errors.append(f"{path.name} must require score, covered_behaviors, and gaps.")

    items = properties.get("acceptance_criteria", {}).get("items", {})
    if set(items.get("required", [])) != EXPECTED_ITEM_FIELDS[fmt]:
        errors.append(f"{path.name} must require the correct item fields for '{fmt}'.")


def validate_schemas(errors: list[str]) -> None:
    for fmt, path in SCHEMA_PATHS.items():
        validate_schema_file(fmt, path, errors)


def validate_common_contract(data: Any, fmt: str, path: Path, errors: list[str]) -> None:
    if not isinstance(data, dict):
        errors.append(f"{path.name} must contain a JSON object.")
        return

    if set(data) != EXPECTED_TOP_LEVEL_FIELDS:
        errors.append(f"{path.name} must contain only the expected top-level fields.")

    if data.get("schema_version") != "2.0.0":
        errors.append(f"{path.name} must set schema_version to 2.0.0.")

    if data.get("format") != fmt:
        errors.append(f"{path.name} must set format to '{fmt}'.")

    ensure_non_empty_string(data.get("source_summary"), f"{path.name}.source_summary", errors)
    ensure_string_list(data.get("assumptions"), f"{path.name}.assumptions", errors)
    ensure_string_list(data.get("out_of_scope"), f"{path.name}.out_of_scope", errors)

    coverage = data.get("coverage_assessment")
    if not isinstance(coverage, dict):
        errors.append(f"{path.name}.coverage_assessment must be an object.")
    else:
        if set(coverage) != EXPECTED_COVERAGE_FIELDS:
            errors.append(
                f"{path.name}.coverage_assessment must contain score, covered_behaviors, and gaps only."
            )
        score = coverage.get("score")
        if not isinstance(score, int) or not (0 <= score <= 100):
            errors.append(f"{path.name}.coverage_assessment.score must be an integer from 0-100.")
        ensure_string_list(
            coverage.get("covered_behaviors"),
            f"{path.name}.coverage_assessment.covered_behaviors",
            errors,
            min_items=1,
        )
        ensure_string_list(
            coverage.get("gaps"),
            f"{path.name}.coverage_assessment.gaps",
            errors,
        )


def validate_criteria_items(data: dict[str, Any], fmt: str, path: Path, errors: list[str]) -> None:
    items = data.get("acceptance_criteria")
    if not isinstance(items, list) or not items:
        errors.append(f"{path.name}.acceptance_criteria must be a non-empty array.")
        return

    seen_ids: set[str] = set()
    required_fields = EXPECTED_ITEM_FIELDS[fmt]
    id_pattern = ID_PATTERNS[fmt]

    for index, item in enumerate(items):
        label = f"{path.name}.acceptance_criteria[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object.")
            continue

        if set(item) != required_fields:
            errors.append(f"{label} must contain only {sorted(required_fields)}.")
            continue

        item_id = item.get("id")
        if not isinstance(item_id, str) or not id_pattern.match(item_id):
            errors.append(f"{label}.id does not match the expected pattern for {fmt}.")
        elif item_id in seen_ids:
            errors.append(f"{path.name} contains duplicate criterion id '{item_id}'.")
        else:
            seen_ids.add(item_id)

        for field_name, value in item.items():
            if field_name == "id":
                continue
            ensure_non_empty_string(value, f"{label}.{field_name}", errors)

        if fmt == "sentences" and item.get("category") not in ALLOWED_SENTENCE_CATEGORIES:
            errors.append(f"{label}.category is not an allowed sentence category.")


def validate_fixture_file(path: Path, errors: list[str]) -> None:
    parts = path.name.split(".")
    if len(parts) < 3:
        errors.append(f"{path.name} should use '<name>.<format>.json' naming.")
        return

    fmt = parts[-2]
    if fmt not in SCHEMA_PATHS:
        errors.append(f"{path.name} uses unsupported format suffix '{fmt}'.")
        return

    input_name = ".".join(parts[:-2]) + ".input.md"
    if not (path.parent / input_name).exists():
        errors.append(f"{path.name} is missing its paired source file '{input_name}'.")

    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f"{path.name} is not valid JSON: {exc}")
        return

    validate_common_contract(data, fmt, path, errors)
    if isinstance(data, dict):
        validate_criteria_items(data, fmt, path, errors)


def validate_fixtures(errors: list[str]) -> None:
    fixture_files = sorted(FIXTURES_DIR.glob("*.json"))
    if not fixture_files:
        errors.append("tests/fixtures must contain at least one JSON contract example.")
        return

    for path in fixture_files:
        validate_fixture_file(path, errors)


def validate_forward_cases(errors: list[str]) -> None:
    case_files = sorted(FORWARD_CASES_DIR.glob("*.json"))
    if not case_files:
        errors.append("tests/forward must contain at least one forward-test case.")
        return

    for path in case_files:
        try:
            case = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name} is not valid JSON: {exc}")
            continue

        if not isinstance(case, dict):
            errors.append(f"{path.name} must contain a JSON object.")
            continue

        for field in ("id", "format", "input_file", "instruction", "required_substrings"):
            if field not in case:
                errors.append(f"{path.name} is missing required forward-test field '{field}'.")

        if case.get("format") not in SCHEMA_PATHS:
            errors.append(f"{path.name} uses unsupported forward-test format '{case.get('format')}'.")

        input_file = ROOT / str(case.get("input_file", ""))
        if not input_file.exists():
            errors.append(f"{path.name} references missing input file '{case.get('input_file')}'.")

        if "${skill_name}" not in str(case.get("instruction", "")):
            errors.append(f"{path.name} should reference the skill invocation via '${{skill_name}}'.")

        required_substrings = case.get("required_substrings")
        if not isinstance(required_substrings, list) or not required_substrings:
            errors.append(f"{path.name}.required_substrings must be a non-empty array.")
        else:
            for index, value in enumerate(required_substrings):
                ensure_non_empty_string(value, f"{path.name}.required_substrings[{index}]", errors)


def validate_root_name(errors: list[str]) -> None:
    if ROOT.name != "acceptance-criteria-designer":
        errors.append("Repository folder should be renamed to 'acceptance-criteria-designer'.")


def main() -> int:
    errors: list[str] = []

    validate_root_name(errors)
    validate_skill_file(errors)
    validate_readme(errors)
    validate_license(errors)
    validate_openai_yaml(errors)
    validate_schemas(errors)
    validate_fixtures(errors)
    validate_forward_cases(errors)

    if errors:
        print("[FAIL] Repository validation failed.")
        for error in errors:
            print(f"- {error}")
        return 1

    print("[OK] Repository validation passed.")
    print(f"Validated skill metadata, icons, schemas, fixtures, and forward cases in {ROOT}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
