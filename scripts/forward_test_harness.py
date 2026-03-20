#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validate_repo import validate_common_contract, validate_criteria_items


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_DIR = ROOT / "tests" / "forward"
DEFAULT_ARTIFACTS_DIR = DEFAULT_CASES_DIR / "artifacts"
SKILL_NAME = "acceptance-criteria-designer"


@dataclass
class ForwardCase:
    id: str
    format: str
    instruction: str
    input_file: Path
    required_substrings: list[str]
    source_text: str


def load_case(path: Path) -> ForwardCase:
    with path.open("r", encoding="utf-8") as handle:
        raw = json.load(handle)

    input_file = ROOT / raw["input_file"]
    source_text = input_file.read_text(encoding="utf-8")

    return ForwardCase(
        id=raw["id"],
        format=raw["format"],
        instruction=raw["instruction"],
        input_file=input_file,
        required_substrings=raw["required_substrings"],
        source_text=source_text,
    )


def build_prompt(case: ForwardCase) -> str:
    instruction = case.instruction.format(
        skill_root=str(ROOT),
        skill_name=SKILL_NAME,
    )
    return (
        f"{instruction}\n\n"
        f"Source document ({case.input_file.name}):\n"
        "```text\n"
        f"{case.source_text.rstrip()}\n"
        "```"
    )


def extract_json_contract(response: str) -> dict[str, Any]:
    blocks: list[str] = []
    fenced_blocks = response.split("```")
    for index in range(1, len(fenced_blocks), 2):
        candidate = fenced_blocks[index].strip()
        if candidate.startswith("json"):
            candidate = candidate[4:].strip()
        blocks.append(candidate)

    for block in reversed(blocks):
        try:
            parsed = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise ValueError("No JSON object code block was found in the runtime response.")


def evaluate_response(case: ForwardCase, response: str) -> list[str]:
    errors: list[str] = []

    for needle in case.required_substrings:
        if needle not in response:
            errors.append(f"Missing expected substring: {needle}")

    try:
        contract = extract_json_contract(response)
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    pseudo_path = Path(f"{case.id}.{case.format}.json")
    validate_common_contract(contract, case.format, pseudo_path, errors)
    validate_criteria_items(contract, case.format, pseudo_path, errors)
    return errors


def run_case(
    case: ForwardCase,
    runner: str,
    artifacts_dir: Path,
    timeout_seconds: int,
    dry_run: bool,
) -> bool:
    case_dir = artifacts_dir / case.id
    case_dir.mkdir(parents=True, exist_ok=True)

    prompt_file = case_dir / "prompt.md"
    output_file = case_dir / "response.md"
    stdout_file = case_dir / "stdout.txt"
    stderr_file = case_dir / "stderr.txt"
    command_file = case_dir / "command.txt"

    prompt = build_prompt(case)
    prompt_file.write_text(prompt, encoding="utf-8")

    command = runner.format(
        prompt_file=str(prompt_file),
        output_file=str(output_file),
        skill_root=str(ROOT),
        skill_name=SKILL_NAME,
        case_id=case.id,
    )
    command_file.write_text(command, encoding="utf-8")

    if dry_run:
        print(f"[DRY-RUN] {case.id}")
        print(f"  Prompt:   {prompt_file}")
        print(f"  Command:  {command}")
        return True

    completed = subprocess.run(
        command,
        cwd=ROOT,
        shell=True,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    stdout_file.write_text(completed.stdout or "", encoding="utf-8")
    stderr_file.write_text(completed.stderr or "", encoding="utf-8")

    response_text = ""
    if output_file.exists():
        response_text = output_file.read_text(encoding="utf-8")
    elif completed.stdout:
        response_text = completed.stdout
        output_file.write_text(response_text, encoding="utf-8")

    if completed.returncode != 0:
        print(f"[FAIL] {case.id}: runtime exited with code {completed.returncode}")
        return False

    if not response_text.strip():
        print(f"[FAIL] {case.id}: runtime produced no response text")
        return False

    errors = evaluate_response(case, response_text)
    if errors:
        print(f"[FAIL] {case.id}")
        for error in errors:
            print(f"  - {error}")
        return False

    print(f"[OK] {case.id}")
    return True


def collect_cases(cases_dir: Path, selected_ids: set[str]) -> list[ForwardCase]:
    loaded_cases = [load_case(path) for path in sorted(cases_dir.glob("*.json"))]
    if selected_ids:
        loaded_cases = [case for case in loaded_cases if case.id in selected_ids]
    return loaded_cases


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run live forward tests for acceptance-criteria-designer through another agent runtime."
    )
    parser.add_argument(
        "--runner",
        help="Shell command template used to execute the external runtime. Supports {prompt_file}, {output_file}, {skill_root}, {skill_name}, and {case_id}.",
    )
    parser.add_argument(
        "--cases-dir",
        default=str(DEFAULT_CASES_DIR),
        help="Directory containing forward-test case definitions.",
    )
    parser.add_argument(
        "--artifacts-dir",
        default=str(DEFAULT_ARTIFACTS_DIR),
        help="Directory where prompts, commands, outputs, and logs are written.",
    )
    parser.add_argument(
        "--case",
        action="append",
        default=[],
        help="Run only the specified case id. Repeat for multiple cases.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=180,
        help="Timeout for each runtime invocation.",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop after the first failed forward-test case.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write prompts and commands without executing the external runtime.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if not args.runner and not args.dry_run:
        print("--runner is required unless --dry-run is used.", file=sys.stderr)
        return 2

    cases_dir = Path(args.cases_dir)
    artifacts_dir = Path(args.artifacts_dir)
    cases = collect_cases(cases_dir, set(args.case))

    if not cases:
        print("No forward-test cases matched the requested selection.", file=sys.stderr)
        return 2

    artifacts_dir.mkdir(parents=True, exist_ok=True)

    failures = 0
    for case in cases:
        success = run_case(
            case=case,
            runner=args.runner or "",
            artifacts_dir=artifacts_dir,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
        )
        if not success:
            failures += 1
            if args.stop_on_failure:
                break

    if failures:
        print(f"[SUMMARY] {failures} forward-test case(s) failed.")
        return 1

    print(f"[SUMMARY] {len(cases)} forward-test case(s) completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
