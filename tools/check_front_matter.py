"""Validate the optional Front Matter used by selected documentation pages."""

from __future__ import annotations

import argparse
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


ALLOWED_FIELDS = {"status", "risk", "applies_to", "verified_on", "tweak_module"}
REQUIRED_FIELDS = {"applies_to", "risk", "tweak_module"}
ALLOWED_STATUS = {"stable", "reference", "experimental"}
ALLOWED_RISK = {"low", "medium", "high"}
# tweakbyjie 主菜单模块编号（菜单 0 是退出，不是模块）
ALLOWED_TWEAK_MODULES = {str(n) for n in range(1, 13)}


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

    missing = sorted(REQUIRED_FIELDS - set(data))
    for field in missing:
        errors.append(_error(path, start_line, f"missing required field '{field}'"))

    status = data.get("status")
    if status is not None and status not in ALLOWED_STATUS:
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

    # tweak_module：数组，允许一对多；允许空数组（无对应 tweakbyjie 模块的纯知识页），
    # 但字段本身必须存在；条目必须是 1-11 的菜单模块编号
    tweak_module = data.get("tweak_module")
    if not isinstance(tweak_module, list):
        errors.append(_error(path, start_line, "tweak_module must be a list of module numbers (1-12)"))
    else:
        for item in tweak_module:
            if not isinstance(item, str) or item.strip() not in ALLOWED_TWEAK_MODULES:
                errors.append(
                    _error(path, start_line, f"tweak_module entries must be module numbers 1-12, got '{item}'")
                )
                break

    verified_on = data.get("verified_on")
    if verified_on is not None:
        # 可选字段：仅在提供时校验格式（YYYY-MM-DD）
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
    """Validate all Markdown source files below ``root/docs``.

    P2-13 契约：全部 docs/*.md 必须携带 Front Matter，且包含
    applies_to / risk / tweak_module 三个必填字段。
    """
    docs_dir = root / "docs"
    errors: list[str] = []
    files_checked = 0
    files_with_front_matter = 0
    for path in sorted(docs_dir.rglob("*.md")):
        files_checked += 1
        text = path.read_text(encoding="utf-8-sig")
        if text.startswith("---"):
            files_with_front_matter += 1
        else:
            errors.append(
                _error(path.relative_to(root).as_posix(), 1,
                       "missing Front Matter (applies_to / risk / tweak_module are required on every docs/*.md)")
            )
        relative = path.relative_to(root).as_posix()
        errors.extend(validate_text(text, relative))
    return CheckResult(files_checked, files_with_front_matter, errors)


def _nav_markdown_paths(mkdocs_path: Path) -> tuple[set[str], list[str]]:
    """Collect ``*.md`` targets referenced by mkdocs.yml nav (relative to docs/)."""
    try:
        data = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return set(), [f"mkdocs.yml: 无法解析（{exc}）"]
    nav = data.get("nav") if isinstance(data, dict) else None
    if not isinstance(nav, list):
        return set(), ["mkdocs.yml: nav 缺失或不是列表"]
    paths: set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, str):
            if node.endswith(".md"):
                paths.add(node)
        elif isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(nav)
    return paths, []


def check_nav_coverage(root: Path) -> list[str]:
    """mkdocs.yml nav 与 docs/ 磁盘文件必须一一对应（双向）。"""
    mkdocs_path = root / "mkdocs.yml"
    if not mkdocs_path.exists():
        return ["mkdocs.yml 不存在，无法校验导航覆盖"]
    nav_paths, errors = _nav_markdown_paths(mkdocs_path)
    docs_dir = root / "docs"
    on_disk = {p.relative_to(docs_dir).as_posix() for p in docs_dir.rglob("*.md")}
    for missing in sorted(on_disk - nav_paths):
        errors.append(f"docs/{missing}: 文件未收录进 mkdocs.yml nav")
    for extra in sorted(nav_paths - on_disk):
        errors.append(f"mkdocs.yml nav 指向不存在的文件: docs/{extra}")
    return errors


def check_index_coverage(root: Path) -> list[str]:
    """每个分类 README 必须链接同分类全部文章，且首页必须链接每个分类索引。"""
    docs_dir = root / "docs"
    errors: list[str] = []
    home = docs_dir / "README.md"
    if not home.exists():
        return ["docs/README.md 不存在，无法校验分类索引覆盖"]
    home_text = home.read_text(encoding="utf-8-sig")
    for category in sorted(p for p in docs_dir.iterdir() if p.is_dir()):
        if not any(category.glob("*.md")):
            continue  # 纯资源目录(stylesheets/、images/ 等)不是内容分类
        readme = category / "README.md"
        if not readme.exists():
            errors.append(f"docs/{category.name}: 分类目录缺少 README.md 索引")
            continue
        if f"{category.name}/README.md" not in home_text:
            errors.append(f"docs/README.md: 未链接分类索引 {category.name}/README.md")
        readme_text = readme.read_text(encoding="utf-8-sig")
        for article in sorted(category.glob("*.md")):
            if article.name == "README.md":
                continue
            if article.name not in readme_text:
                errors.append(
                    f"docs/{category.name}/README.md: 未链接同分类文章 {article.name}"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    args = parser.parse_args()
    root = args.root.resolve()
    result = check_tree(root)
    errors = list(result.errors)
    errors.extend(check_nav_coverage(root))
    errors.extend(check_index_coverage(root))
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        f"Docs check passed: {result.files_checked} Markdown files scanned; "
        f"{result.files_with_front_matter} contain Front Matter; "
        "nav and category indexes fully cover the tree."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
