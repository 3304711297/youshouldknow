"""从 docs/*.md 的 front matter `tweak_module` 字段生成 tweakbyjie 覆盖矩阵页。

产物：docs/项目导航/覆盖矩阵.md（模块 → 文章 双向矩阵 + 无联动文章清单）。
约定：
  - 页面纳入 mkdocs.yml nav（项目导航 分类），分类索引 README 同步链接；
  - 生成的页面自身也带三必填字段的 front matter；
  - CI 在构建前运行本脚本并以 `git diff --exit-code` 防漂移；本地改动后需重跑提交。

用法：python scripts/gen-matrix.py [--check]
  --check  仅校验已提交的矩阵页与 front matter 一致（不一致退出码 1），不写文件。
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = DOCS / "项目导航" / "覆盖矩阵.md"
MODULE_RANGE = range(1, 13)

_spec = importlib.util.spec_from_file_location("cfm", ROOT / "tools" / "check_front_matter.py")
_cfm = importlib.util.module_from_spec(_spec)
sys.modules["cfm"] = _cfm
_spec.loader.exec_module(_cfm)


def _collect() -> list[dict]:
    """读取全部内容页 front matter（跳过分类索引 README，它们只是导航）。"""
    entries = []
    # 以 posix 相对路径排序：Windows 的 Path 比较大小写不敏感，与 CI Linux 排序可能不同，
    # 会造成本地渲染与 CI 校验不一致（如 Above4G… 与 AMD-PBO… 的次序）
    for path in sorted(DOCS.rglob("*.md"), key=lambda p: p.relative_to(DOCS).as_posix()):
        rel = path.relative_to(DOCS).as_posix()
        if rel.endswith("/README.md") or rel == "README.md" or rel == "项目导航/覆盖矩阵.md":
            continue
        text = path.read_text(encoding="utf-8-sig")
        parsed = _parse(text, rel)
        if parsed is None:
            continue
        entries.append({
            "rel": rel,
            "title": _title(path, text),
            "applies_to": parsed.get("applies_to") or [],
            "risk": parsed.get("risk") or "",
            "modules": [str(m) for m in (parsed.get("tweak_module") or [])],
        })
    return entries


def _parse(text: str, source: str = "<unknown>") -> dict | None:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                import yaml
                data = yaml.safe_load("\n".join(lines[1:i]))
            except Exception as exc:
                # 降级跳过该文档，但绝不静默：必须留下警告，否则覆盖矩阵会悄悄缺页
                print(f"[警告] front matter YAML 解析失败，该文档已被排除出覆盖矩阵：{source}：{exc}", file=sys.stderr)
                return None
            return data if isinstance(data, dict) else None
    return None


def _title(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def _render(entries: list[dict]) -> str:
    by_module: dict[str, list[dict]] = {str(n): [] for n in MODULE_RANGE}
    unlinked = []
    for e in entries:
        if e["modules"]:
            for m in e["modules"]:
                by_module.setdefault(m, []).append(e)
        else:
            unlinked.append(e)

    lines: list[str] = []
    lines.append("---")
    lines.append("applies_to:")
    lines.append("  - Windows 10")
    lines.append("  - Windows 11")
    lines.append("risk: low")
    lines.append("tweak_module: []")
    lines.append("---")
    lines.append("")
    lines.append("# tweakbyjie 覆盖矩阵（模块 ↔ 文章）")
    lines.append("")
    lines.append("> 本页由 `scripts/gen-matrix.py` 从全部文章 front matter 的")
    lines.append("> `tweak_module` 字段自动生成；改动文章的 `tweak_module` 后重跑该脚本并提交。")
    lines.append("> 反向入口见 tweakbyjie 仓库 README 的菜单章节（各模块「详见」链接指向本库对应文章）。")
    lines.append(">")
    lines.append("> 边界说明：菜单 **0（退出 / Exit）不是模块**，不参与前置条件灰掉；预检（preflight）")
    lines.append("> 只对 1-11 号模块做可用性判断。各模块执行后的重启询问属于会话级收尾，同样不受预检影响，")
    lines.append("> 也从不自动重启（`-AcceptDefaults` 无人值守模式下维持默认\"不重启\"）。")
    lines.append("")
    lines.append("## 模块 → 文章（一对多）")
    lines.append("")
    lines.append("| tweakbyjie 菜单模块 | 关联文章 |")
    lines.append("| --- | --- |")
    for n in MODULE_RANGE:
        linked = by_module[str(n)]
        if linked:
            cells = "、".join(f"[{e['title']}](../{e['rel']})" for e in linked)
        else:
            cells = "—（暂无关联文章）"
        lines.append(f"| 模块 {n} | {cells} |")
    lines.append("")
    lines.append("## 文章 → 模块（反向）")
    lines.append("")
    lines.append("| 文章 | 风险 | 联动模块 |")
    lines.append("| --- | --- | --- |")
    for e in entries:
        if e["modules"]:
            mods = "、".join(f"`{m}`" for m in e["modules"])
            lines.append(f"| [{e['title']}](../{e['rel']}) | {e['risk']} | {mods} |")
    lines.append("")
    lines.append("## 无联动模块的知识文章")
    lines.append("")
    lines.append("以下文章不对应任何 tweakbyjie 菜单模块（纯知识/BIOS 层/外部工具/验机流程），")
    lines.append("列出以确认联动边界，避免误以为脚本覆盖：")
    lines.append("")
    for e in unlinked:
        lines.append(f"- [{e['title']}](../{e['rel']})")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="仅校验生成结果与已提交文件一致")
    args = parser.parse_args()

    entries = _collect()
    rendered = _render(entries)
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != rendered:
            print("覆盖矩阵页与 front matter 不一致，请运行 python scripts/gen-matrix.py 后提交。")
            return 1
        print("覆盖矩阵页校验一致。")
        return 0
    OUT.write_text(rendered, encoding="utf-8")
    print(f"已生成 {OUT.relative_to(ROOT).as_posix()}（{len(entries)} 篇文章参与统计）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
