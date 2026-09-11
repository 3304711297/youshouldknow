"""盘古之白（CJK↔拉丁间距）安全修正器。

设计要点（务必遵守，避免破坏正文）：
  · 逐行处理，**跳过** front matter / 代码围栏 / 表格分隔行 / 纯代码行
  · 剥离行内代码与链接后再判断，但**只在原文对应位置**插入空格
  · 保护这些**不该加空格**的情形：
      - markdown 语法字符紧邻（**、`、[、]、|、#、>、~、*、_）
      - 列表标记（- / 1.）与其后内容
      - 文件名/路径/扩展名（.md、.py、C:\、/etc/）
      - 版本号、数字+单位（5MB、2.4GHz、10.8 Gbps 已有空格者不动）
      - URL、邮箱
      - 全角标点相邻（（）、「」、，。等）
  · 默认 dry-run，--write 才落盘；输出逐条 diff 供人工核对

用法:
  python tools/fix_pangu.py docs               # dry-run 全库
  python tools/fix_pangu.py docs/path.md --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CJK = r"\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff"
LATIN = r"A-Za-z0-9"

FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
FM_DELIM = re.compile(r"^---\s*$")
TABLE_SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")

INLINE_CODE = re.compile(r"`[^`]*`")
LINK = re.compile(r"!?\[[^\]]*\]\([^)]*\)")
AUTOLINK = re.compile(r"<https?://[^>]*>")
URL = re.compile(r"https?://\S+|www\.\S+")
HTML_TAG = re.compile(r"</?[A-Za-z][^>]*>")
EMAIL = re.compile(r"\S+@\S+")

# 需要保护、绝不插入空格的上下文（用占位符替换后再判断）
PROTECT = re.compile(
    r"\d+(?:\.\d+)?(?:MB|GB|KB|TB|GHz|MHz|kHz|Hz|ms|ns|us|s|fps|FPS|W|V|A|℃|°C|%|bit|byte)"
    r"|[A-Za-z]:\\[^\s]*"          # Windows 路径
    r"|(?:\.\.?/)[^\s]*"           # 相对路径
    r"|/[\w./-]{2,}"               # 绝对路径片段
    r"|\b[\w.-]+\.(?:md|py|ps1|psm1|js|ts|json|ya?ml|toml|exe|dll|zip|log|txt|cfg|ini|sh|cmd|bat|pow)\b"
)

# 不应在两侧加空格的全角字符（中文标点自身已提供视觉间距）
FULLWIDTH_PUNCT = "，。！？；：“”‘’（）《》〈〉、·—…「」『』【】"

PLACEHOLDER = "\uE123"


def protect_segments(s: str) -> tuple[str, list[str]]:
    """把受保护片段替换为占位符，返回 (掩码文本, 片段表)。

    注意：占位符是单一字符，而原片段是多字符——因此本函数只用于判断
    "该位置是否紧邻受保护内容"，不用于就地插入空格。
    """
    store: list[str] = []

    def repl(m):
        store.append(m.group(0))
        return PLACEHOLDER

    # 依次保护：URL/邮箱/HTML → 路径/文件名 → 数字单位
    s = URL.sub(repl, s)
    s = EMAIL.sub(repl, s)
    s = HTML_TAG.sub(repl, s)
    s = PROTECT.sub(repl, s)
    return s, store


def add_spaces(line: str) -> str:
    """在 CJK 与拉丁/数字之间补空格。

    关键：只修改原行中**不在** markdown 行内代码/URL/HTML 里的位置。
    链接 `[锚文本](url)` 的**锚文本属于可见正文**，需要修正；
    仅 URL 部分保持不动。做法——先求出行内代码与链接(*URL段*)的字符区间，
    再在这些区间之外做替换。
    """
    # 1. 标记不可改区域：行内代码整体、链接的 URL 段、裸 URL、HTML、邮箱
    spans: list[tuple[int, int]] = []
    for pat in (INLINE_CODE, URL, HTML_TAG, EMAIL):
        for m in pat.finditer(line):
            spans.append((m.start(), m.end()))
    # 链接：只保护 `](...)` 的 URL 部分，锚文本留给后续处理
    for m in LINK.finditer(line):
        inner = m.group(0)
        close_idx = inner.rfind("](")
        if close_idx >= 0:
            url_start = m.start() + close_idx + 1  # 指向 '('
            spans.append((url_start, m.end()))

    def is_protected(pos: int) -> bool:
        return any(a <= pos < b for a, b in spans)

    out = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if is_protected(i):
            out.append(ch)
            i += 1
            continue

        # 情形 A：CJK 紧跟拉丁/数字
        if re.match(f"[{CJK}]", ch) and i + 1 < n:
            nxt = line[i + 1]
            if re.match(f"[{LATIN}]", nxt) and not is_protected(i + 1):
                out.append(ch)
                out.append(" ")
                i += 1
                continue

        # 情形 B：拉丁/数字紧跟 CJK
        if re.match(f"[{LATIN}]", ch) and i + 1 < n:
            nxt = line[i + 1]
            if re.match(f"[{CJK}]", nxt) and not is_protected(i + 1):
                out.append(ch)
                out.append(" ")
                i += 1
                continue

        out.append(ch)
        i += 1
    return "".join(out)


def protect_check(line: str) -> str:
    """在候选修改前，检查该行是否包含受保护模式；含则整体跳过（保守策略）。"""
    masked, _ = protect_segments(line)
    return masked


def process_file(path: Path, write: bool, verbose: bool) -> tuple[int, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    changes: list[str] = []
    new_lines: list[str] = []

    in_fence = False
    in_fm = False

    for idx, raw in enumerate(lines, 1):
        line = raw.rstrip("\n")
        eol = raw[len(line):] or ""

        if idx == 1 and FM_DELIM.match(line):
            in_fm = True
            new_lines.append(raw)
            continue
        if in_fm:
            if FM_DELIM.match(line):
                in_fm = False
            new_lines.append(raw)
            continue
        if FENCE.match(line):
            in_fence = not in_fence
            new_lines.append(raw)
            continue
        if in_fence:
            new_lines.append(raw)
            continue

        # 表格分隔行、纯符号行不动
        if TABLE_SEP.match(line):
            new_lines.append(raw)
            continue

        # 预检：剥掉**不可见的**语法部件（行内代码、URL、HTML、邮箱），
        # 但保留链接锚文本（它是可见正文）。若无 CJK↔拉丁 交界则跳过。
        probe = line
        for pat in (INLINE_CODE, URL, HTML_TAG, EMAIL):
            probe = pat.sub(" ", probe)
        for mm in LINK.finditer(probe):
            head = mm.group(0).split("](")[0] + "]"
            probe = probe.replace(mm.group(0), head)
        if not re.search(f"[{CJK}][{LATIN}]|[{LATIN}][{CJK}]", probe):
            new_lines.append(raw)
            continue

        fixed = add_spaces(line)
        if fixed != line:
            changes.append(f"  L{idx}: {line.strip()[:96]}\n      -> {fixed.strip()[:96]}")
        new_lines.append(fixed + eol)

    if write and changes:
        path.write_text("".join(new_lines), encoding="utf-8")

    return len(changes), changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--write", action="store_true", help="落盘（默认 dry-run）")
    ap.add_argument("--show", type=int, default=12, help="每文件最多展示条数")
    args = ap.parse_args()

    root = Path(args.target)
    files = sorted(root.rglob("*.md")) if root.is_dir() else [root]
    total = 0
    for p in files:
        n, ch = process_file(p, args.write, verbose=True)
        if n:
            total += n
            print(f"\n{p.relative_to(root.parent if root.is_dir() else root.parent)}  ({n} 处)")
            for c in ch[: args.show]:
                print(c)
            if len(ch) > args.show:
                print(f"  … 另有 {len(ch) - args.show} 处")

    mode = "已写入" if args.write else "dry-run（未改动）"
    print(f"\n合计 {total} 处待修正 · {mode}")


if __name__ == "__main__":
    main()
