# 排版与布局维护工具

本目录下的四个脚本用于维护站点的排版质量。它们**不是** CI 门禁的一部分
（`audit_layout.py` 需要浏览器），属于按需运行的诊断/修正工具。

## 工具速览

| 脚本 | 用途 | 依赖 | 会改文件？ |
| --- | --- | --- | --- |
| `audit_typography.py` | 源码级中文排版审计（6 类规则） | 无 | 否 |
| `audit_layout.py` | 渲染级布局审计（143 页 × 任意视口） | CDP 浏览器 + websocket-client | 否 |
| `fix_pangu.py` | 批量补 CJK↔拉丁 之间的盘古之白 | 无 | `--write` 才改 |
| `fix_fence_lang.py` | 给缺语言的代码围栏补标签 | 无 | `--write` 才改 |

两个 `fix_*` 脚本**默认 dry-run**，先看输出再决定是否 `--write`。

## 日常用法

```powershell
# 排版审计（改动中文正文后跑一次）
python tools/audit_typography.py docs

# 看某类问题的明细
python tools/audit_typography.py docs --verbose

# 修正盘古之白（先 dry-run 核对）
python tools/fix_pangu.py docs
python tools/fix_pangu.py docs --write

# 补代码围栏语言
python tools/fix_fence_lang.py docs
python tools/fix_fence_lang.py docs --write

# 布局审计（需先起 CDP 浏览器与本地站点）
python -m mkdocs build --strict -d <临时目录>
python -m http.server 8791 -d <临时目录>          # 另开一个终端
python tools/audit_layout.py <urls.txt> out.json 390
```

## 设计背景与坑

**为什么 `fix_pangu.py` 要保护这么多模式**：天真的 `re.sub(r'([\u4e00-\u9fff])([A-Za-z])', ...)`
会破坏版本号、文件扩展名、URL、单位（`5MB`）、路径（`C:\`）。脚本因此先划定
"不可改区间"（行内代码、URL、HTML、链接的 URL 段），再逐字符扫描插入空格；
链接的**锚文本属于可见正文**，需要修正，只有 `](url)` 部分保持不动。

**围栏必须用状态栈解析**：外层 ````markdown 内嵌 ```bash 时，内层的闭合符
会被"遇 ``` 就切换"的朴素写法误判为开启符，导致把后续正文吞进代码块。
`audit_typography.py` 与 `fix_fence_lang.py` 都用 `(字符, 长度)` 栈判定：
只有同字符、长度 >= 栈顶、且信息串为空才算闭合。

**审计器的假阳性教训**：早期版本报了 1681 处"缺空格"，实际 90% 是 markdown
语法噪声（`**粗体**` 标记、`1.` 列表序号）；T8"多余空格"的 758 处也全是
行内代码被剥离后留下的占位空格。**剥离语法时要用哨兵字符占位，不能用空格**
——否则制造出根本不存在的空格问题。报告数字前务必抽样人工核对。

**`overflow-wrap: anywhere` 是刻意的**：表格里的长参数串
（`useplatformclock/useplatformtick/…`）与正文里的注册表路径在窄屏会撑破容器。
`anywhere` 会计入 min-content 计算，因此能让不可断长串折行，避免横向滚动。
代价是折行点可能落在参数中间，属可接受的取舍。
