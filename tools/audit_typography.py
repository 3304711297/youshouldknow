"""ysk 中文排版规范审计（源码级，严格版）。

设计原则：只报**确认无误**的问题，宁可漏报不可误报——每条规则都排除
markdown 语法噪声（强调标记、列表序号、代码、链接、标题编号）。

检测项：
  T1 CJK↔拉丁之间缺少盘古之白（已剥离 **强调**/`代码`/[链接](url)/<html>）
  T2 中文语境误用半角逗号/分号/冒号（排除行首序号、小数、时间、英文缩写）
  T3 标题层级跳跃（h2→h4 等）
  T4 代码围栏缺语言标识
  T5 连续空行（>1，纯整洁性问题）
  T8 全角空格误用 / 中文之间出现 ≥3 个半角空格
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CJK = r"\u4e00-\u9fff\u3400-\u4dbf"
# 拉丁/数字类（不含 markdown 语法字符 * _ ` ~ | 与空白）
LATIN = r"A-Za-z0-9"
# 允许作为边界的中英间分隔符（这些不需要空格）
NO_SPACE_AFTER = r"[\s\u3000]"

FENCE_RE = re.compile(r"^\s*(```|~~~)")
FM_DELIM = re.compile(r"^---\s*$")

INLINE_CODE_RE = re.compile(r"`[^`]+`")
BOLD_RE = re.compile(r"\*{1,3}([^*\n]+)\*{1,3}")
UND_RE = re.compile(r"(?<![A-Za-z0-9_])_{1,3}([^_\n]+)_{1,3}(?![A-Za-z0-9_])")
LINK_RE = re.compile(r"!?\[([^\]]*)\]\([^)]*\)")
AUTO_RE = re.compile(r"<https?://[^>]*>")
URL_RE = re.compile(r"https?://\S+")
HTML_RE = re.compile(r"<[^>]+>")
IMG_RE = re.compile(r"!\[[^\]]*\]\([^)]*\)")


def strip_syntax(line: str) -> str:
    """剥离 markdown 语法，保留可读文字；链接保留锚文本。"""
    # 用不可能出现在正文的哨兵字符占位，避免剥离后产生伪空格
    SENT = "\uE000"
    s = IMG_RE.sub(" ", line)
    s = INLINE_CODE_RE.sub(SENT, s)           # 行内代码 → 哨兵（等同"非空格紧邻字符"）
    s = LINK_RE.sub(lambda m: SENT + m.group(1), s)  # 链接 → 锚文本
    s = AUTO_RE.sub(" ", s)
    s = URL_RE.sub(" ", s)
    s = HTML_RE.sub(" ", s)
    s = BOLD_RE.sub(lambda m: m.group(1), s)
    s = UND_RE.sub(lambda m: m.group(1), s)
    return s


def audit_file(path: Path) -> dict:
    raw_text = path.read_text(encoding="utf-8")
    lines = raw_text.splitlines()
    res: dict[str, list] = defaultdict(list)

    in_fence = False
    in_fm = False
    fence_no_lang = 0
    headings: list[tuple[int, int, str]] = []
    prev_blank = 0
    # 围栏状态栈：正确区分"真开启"与"嵌套中的内层围栏"，
    # 避免把外层 4 反引号里的内层 ```bash 误判为缺语言的独立围栏。
    fence_stack: list[tuple[str, int]] = []

    for idx, line in enumerate(lines, 1):
        line = line.rstrip("\n")

        # YAML front matter（仅文件首块）
        if idx == 1 and FM_DELIM.match(line):
            in_fm = True
            continue
        if in_fm:
            if FM_DELIM.match(line):
                in_fm = False
            continue

        # 代码围栏（状态栈解析）
        fm_match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if fm_match:
            fence, info = fm_match.group(1), fm_match.group(2).strip()
            ch, ln_len = fence[0], len(fence)
            prev_blank = 0                     # 围栏边界重置，避免跨块误判
            if fence_stack:
                top_ch, top_len = fence_stack[-1]
                if ch == top_ch and ln_len >= top_len and not info:
                    fence_stack.pop()          # 闭合
                    in_fence = bool(fence_stack)
                    continue
            else:
                if not info:
                    fence_no_lang += 1
            fence_stack.append((ch, ln_len))   # 开启
            in_fence = True
            continue
        if in_fence:
            prev_blank = 0
            continue

        # 表格行、引用行、列表标记行单独处理
        is_table_row = line.lstrip().startswith("|")
        m_head = re.match(r"^(#{1,6})\s+\S", line)
        if m_head:
            headings.append((len(m_head.group(1)), idx, line.strip()[:60]))

        # 连续空行（注意：围栏边界必须重置计数，否则会跨代码块误判）
        if not line.strip():
            prev_blank += 1
            if prev_blank >= 2:
                res["T5"].append((idx, "连续空行"))
            continue
        prev_blank = 0

        # 列表序号行首（"1. xxx" / "- xxx"）——序号点不算标点问题
        m_list = re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line)
        list_prefix_end = m_list.end() if m_list else 0

        prose = strip_syntax(line)
        if not prose.strip():
            continue

        # ---------- T1 盘古之白 ----------
        # 只在正文（非表格分隔行、非纯符号行）检测
        if not re.match(r"^\s*[-|:=\s]+$", prose):
            body = prose[list_prefix_end:] if list_prefix_end and list_prefix_end < len(prose) else prose
            # CJK 后紧跟拉丁/数字
            for mm in re.finditer(rf"([{CJK}])([{LATIN}])", body):
                res["T1"].append((idx, "CJK→拉丁: 「…" + body[max(0, mm.start() - 10):mm.end() + 10] + "…」"))
            # 拉丁/数字后紧跟 CJK（排除百分号/单位等常见无空格搭配）
            for mm in re.finditer(rf"([{LATIN}])([{CJK}])", body):
                seg = body[max(0, mm.start() - 10):mm.end() + 10]
                res["T1"].append((idx, "拉丁→CJK: 「…" + seg + "…」"))

        # ---------- T2 中文语境半角标点 ----------
        # 半角逗号/分号紧邻 CJK（排除列表序号位置）
        for mm in re.finditer(rf"[{CJK}]([,;])(?![0-9])", prose):
            if list_prefix_end and mm.start() < list_prefix_end:
                continue
            res["T2"].append((idx, "半角 " + mm.group(1) + ": 「…" + prose[max(0, mm.start() - 10):mm.end() + 12] + "…」"))
        # 半角冒号紧邻 CJK
        for mm in re.finditer(rf"[{CJK}](:)(?![/\d])", prose):
            if list_prefix_end and mm.start() < list_prefix_end:
                continue
            seg = prose[max(0, mm.start() - 12):mm.end() + 12]
            if re.search(r"\d\s*:\s*\d", seg):     # 时间/比例
                continue
            if re.search(r"[A-Za-z]\s*:\s*", seg):  # URL scheme / 英文键值
                continue
            res["T2"].append((idx, "半角冒号: 「…" + seg + "…」"))
        # 中文句末半角句点（排除版本号/文件名）
        for mm in re.finditer(rf"([{CJK}])\.(?=\s|$|[{CJK}])", prose):
            seg = prose[max(0, mm.start() - 12):mm.end() + 12]
            if re.search(r"[A-Za-z0-9]\.[A-Za-z0-9]", seg):
                continue
            res["T2"].append((idx, "半角句点: 「…" + seg + "…」"))

        # ---------- T8 全角空格 / 中文间多空格 ----------
        if "\u3000" in prose and not is_table_row:
            res["T8"].append((idx, "含全角空格 U+3000"))
        # 只统计真正的连续空格（哨兵占位符不参与）
        for mm in re.finditer(rf"[{CJK}]( {{3,}})[{CJK}]", prose):
            res["T8"].append((idx, "中文间 ≥3 空格: 「" + prose[mm.start():mm.end()] + "」"))

    # ---------- T3 标题层级跳跃 ----------
    prev = None
    for lv, ln, txt in headings:
        if prev is not None and lv > prev + 1:
            res["T3"].append((ln, "h%d → h%d: %s" % (prev, lv, txt)))
        prev = lv

    if fence_no_lang:
        res["T4"].append((0, "%d 个代码围栏缺语言标识" % fence_no_lang))

    return res


LABELS = {
    "T1": "CJK↔拉丁缺盘古之白",
    "T2": "中文语境半角标点",
    "T3": "标题层级跳跃",
    "T4": "代码围栏缺语言标识",
    "T5": "连续空行",
    "T8": "全角空格/多余空格",
}


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    verbose = "--verbose" in sys.argv
    top_n = 8
    files = sorted(root.rglob("*.md"))
    totals: Counter = Counter()
    per_file: dict[Path, dict] = {}
    for p in files:
        r = audit_file(p)
        if r:
            per_file[p] = r
            for k, v in r.items():
                totals[k] += len(v)

    print("扫描 %d 个 markdown 文件\n" % len(files))
    for k in sorted(LABELS):
        print("  %s %s: %d" % (k, LABELS[k], totals.get(k, 0)))

    print("\n--- 问题最集中的文件 ---")
    for k in sorted(LABELS):
        if not totals.get(k):
            continue
        ranked = sorted(((len(v.get(k, [])), f) for f, v in per_file.items()), reverse=True)[:top_n]
        print("\n%s %s (共 %d):" % (k, LABELS[k], totals[k]))
        for n, f in ranked:
            if n:
                print("    %4d  %s" % (n, f.name))

    if verbose:
        print("\n--- 明细 ---")
        shown = 0
        for f, r in per_file.items():
            for k in sorted(r):
                for ln, msg in r[k][:4]:
                    print("  [%s] %s:%d %s" % (k, f.name, ln, msg[:120]))
                    shown += 1
                    if shown >= 120:
                        return


if __name__ == "__main__":
    main()
