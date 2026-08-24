"""Validate the optional Front Matter used by selected documentation pages."""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_FIELDS = {"status", "risk", "applies_to", "verified_on"}
ALLOWED_STATUS = {"stable", "reference", "experimental"}
ALLOWED_RISK = {"low", "medium", "high"}


@dataclass
class CheckResult:
    files_checked: int
    files_with_front_matter: int
    errors: list[str]


def _error(path: str, line: int, message: str) -> str:
    return f"{path}:{line}: {message}"


def _front_matter_lines(text: str, path: str) -> tuple[str | None, int, list[str]]:
    lines = text.splitlines()
    if not lines:
        return None, 0, []
    if lines[0].lstrip("\ufeff") != "---":
        return None, 0, []
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), index + 1, []
    return None, 0, [_error(path, len(lines), "missing closing '---' for Front Matter")]


def _validate_value(data: dict[str, Any], path: str, start_line: int) -> list[str]:
    errors: list[str] = []
    for field in sorted(set(data) - ALLOWED_FIELDS):
        errors.append(_error(path, start_line, f"unknown field '{field}'"))

    missing = sorted(ALLOWED_FIELDS - set(data))
    for field in missing:
        errors.append(_error(path, start_line, f"missing required field '{field}'"))

    status = data.get("status")
    if status not in ALLOWED_STATUS:
        errors.append(
            _error(path, start_line, "status must be one of: experimental, reference, stable")
        )

    risk = data.get("risk")
    if risk not in ALLOWED_RISK:
        errors.append(_error(path, start_line, "risk must be one of: high, low, medium"))

    applies_to = data.get("applies_to")
    if (
        not isinstance(applies_to, list)
        or not applies_to
        or any(not isinstance(item, str) or not item.strip() for item in applies_to)
    ):
        errors.append(_error(path, start_line, "applies_to must be a non-empty list of strings"))

    verified_on = data.get("verified_on")
    if isinstance(verified_on, dt.date) and not isinstance(verified_on, dt.datetime):
        verified_text = verified_on.isoformat()
    elif isinstance(verified_on, str):
        verified_text = verified_on
    else:
        verified_text = ""
    try:
        parsed = dt.date.fromisoformat(verified_text)
    except ValueError:
        parsed = None
    if parsed is None or verified_text != parsed.isoformat():
        errors.append(_error(path, start_line, "verified_on must be a valid YYYY-MM-DD date"))

    return errors


def validate_text(text: str, path: str = "<text>") -> list[str]:
    """Return validation errors for one Markdown document."""
    front_matter, closing_line, errors = _front_matter_lines(text, path)
    if errors or front_matter is None:
        return errors
    try:
        data = yaml.load(front_matter, Loader=yaml.BaseLoader)
    except (ValueError, yaml.YAMLError) as exc:
        detail = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        return [_error(path, closing_line, f"invalid YAML: {detail}")]
    if not isinstance(data, dict):
        return [_error(path, 1, "Front Matter must be a YAML mapping")]
    return _validate_value(data, path, 1)


def check_tree(root: Path) -> CheckResult:
    """Validate all Markdown source files below ``root/docs``."""
    docs_dir = root / "docs"
    errors: list[str] = []
    files_checked = 0
    files_with_front_matter = 0
    for path in sorted(docs_dir.rglob("*.md")):
        files_checked += 1
        text = path.read_text(encoding="utf-8-sig")
        if text.startswith("---"):
            files_with_front_matter += 1
        relative = path.relative_to(root).as_posix()
        errors.extend(validate_text(text, relative))
    return CheckResult(files_checked, files_with_front_matter, errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    result = check_tree(args.root.resolve())
    if result.errors:
        for error in result.errors:
            print(error)
        return 1
    print(
        f"Front Matter check passed: {result.files_checked} Markdown files scanned; "
        f"{result.files_with_front_matter} contain Front Matter."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
