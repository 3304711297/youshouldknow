"""为缺语言标识的代码围栏补上语言标签（状态感知，正确处理嵌套）。

问题背景：ASCII 流程图/日志片段常用裸 ``` 围栏，导致 MkDocs 不给语法高亮，
复制按钮样式也降级。但简单的"遇到 ``` 就切换状态"会被**嵌套围栏**骗到
（外层 ````markdown 内含内层 ```bash 时，内层闭合符会被误判为开启符）。

本脚本用状态栈正确解析：
  · 开启：栈空，或栈顶围栏字符不同 / 更短
  · 闭合：与栈顶同字符、长度 >= 栈顶、且信息串为空
只为**真正的开启围栏**且缺语言者补标签，默认补 'text'（ASCII 图表）。

用法:
  python tools/fix_fence_lang.py docs            # dry-run
  python tools/fix_fence_lang.py docs --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})(.*)$")
FM_DELIM = re.compile(r"^---\s*$")
DEFAULT_LANG = "text"

# 依据围栏内容特征推断更精确的语言。
# 顺序很重要：先判断**确定性高**的特征（JSON 必须有引号包围的键），
# 再退回通用类型；ASCII 图表/日志片段一律归为 text。
HINTS = [
    # 真 JSON：整段以 { 或 [ 开头且含 "key": 结构
    (re.compile(r'^\s*[\{\[][\s\S]*"\s*[\w-]+\s*"\s*:'), "json"),
    # PowerShell 命令
    (re.compile(r"(?m)^\s*(?:PS [A-Z]:[\\/]|Get-[A-Z]\w+|Set-[A-Z]\w+|New-[A-Z]\w+|Invoke-[A-Z]\w+)"), "powershell"),
    # Shell 命令
    (re.compile(r"(?m)^\s*(?:sudo |apt-get |systemctl |#!/bin/(?:ba)?sh)"), "bash"),
]


def guess_lang(body: list[str]) -> str:
    """从围栏内容推断语言；识别不了就用 text（ASCII 图表/日志最安全）。"""
    sample = "\n".join(body[:12])
    for pat, lang in HINTS:
        if pat.search(sample):
            return lang
    return DEFAULT_LANG


def process(path: Path, write: bool, show: int) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    changes: list[str] = []
    out: list[str] = []
    stack: list[tuple[str, int]] = []   # (char, length)
    in_fm = False

    for idx, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")

        if idx == 1 and FM_DELIM.match(line):
            in_fm = True
            out.append(raw)
            continue
        if in_fm:
            if FM_DELIM.match(line):
                in_fm = False
            out.append(raw)
            continue

        m = FENCE.match(line)
        if not m:
            out.append(raw)
            continue

        indent, fence, rest = m.group(1), m.group(2), m.group(3)
        char, length = fence[0], len(fence)
        info = rest.strip()

        if stack:
            top_char, top_len = stack[-1]
            if char == top_char and length >= top_len and not info:
                stack.pop()
                out.append(raw)
                continue

        if not info:
            # 真正的开启围栏且缺语言 → 收集主体后推断
            body: list[str] = []
            for j in range(idx, min(idx + 12, len(lines))):
                nxt = lines[j].rstrip("\n")
                nm = FENCE.match(nxt)
                if nm and nm.group(2)[0] == char and len(nm.group(2)) >= length and not nm.group(3).strip():
                    break
                body.append(nxt)
            lang = guess_lang(body)
            new_line = f"{indent}{fence}{lang}"
            changes.append(f"  L{idx}: ``` → ```{lang}   (上文: {lines[idx-2].strip()[:52] if idx >= 2 else ''})")
            out.append(new_line + "\n")
        else:
            out.append(raw)

        stack.append((char, length))

    if write and changes:
        path.write_text("".join(out), encoding="utf-8")
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--show", type=int, default=10)
    args = ap.parse_args()

    root = Path(args.target)
    files = sorted(root.rglob("*.md")) if root.is_dir() else [root]
    total = 0
    for p in files:
        ch = process(p, args.write, args.show)
        if ch:
            total += len(ch)
            print(f"\n{p.name}  ({len(ch)} 处)")
            for c in ch[: args.show]:
                print(c)
    print(f"\n合计 {total} 处 · {'已写入' if args.write else 'dry-run'}")


if __name__ == "__main__":
    main()
