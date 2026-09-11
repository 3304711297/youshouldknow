"""页面顶部元数据卡（唯一渲染入口）+ Material tags 注入。

设计决策（2026-09-11）：
  同一批 Front Matter 字段曾被三处消费——本 hook 的 abstract admonition、
  on_page_context 注入的 tags、overrides/main.html 的 .doc-meta 卡片——
  导致顶部堆叠 2~4 份近似信息（最高 517px）。现合并为**单一元数据卡**：
    · 卡片：status / risk / applies_to / verified_on / tweak_module
    · 信息按重要性排序，缺失字段自动省略，不产生空行
  旧的 admonition 与 tags 注入已移除；如需恢复，见 git 历史。

卡片实现委托给 overrides/main.html（模板层），本 hook 只负责：
  1. 注入模板需要的展示数据（含 tweak_module 的覆盖矩阵相对链接）；
  2. 不向 context 注入 tags（Material 的 partials/tags.html 不再有内容）。

任何异常静默跳过，绝不影响构建（--strict 下也不会因本 hook 失败）。
"""

from __future__ import annotations

import posixpath

RISK_META = {
    "low": ("🟢", "低风险"),
    "medium": ("🟡", "中风险"),
    "high": ("🔴", "高风险"),
}
STATUS_LABELS = {
    "stable": "稳定维护",
    "reference": "参考资料",
    "experimental": "实验性内容",
}
MATRIX_URL = "项目导航/覆盖矩阵.md"


def _matrix_link(page) -> str | None:
    """覆盖矩阵页相对当前页的站内相对链接；解析失败返回 None。"""
    try:
        if hasattr(page, "file") and hasattr(page.file, "src_uri"):
            page_dir = posixpath.dirname(page.file.src_uri)
        else:
            page_dir = posixpath.dirname(page.url.rstrip("/"))
        return posixpath.relpath(MATRIX_URL, start=page_dir or ".")
    except Exception:
        return None


def on_page_markdown(markdown: str, page, config, files):
    """正文不做任何注入——顶部信息统一由模板层的元数据卡承担。"""
    return markdown


def on_page_context(context, page, config, nav):
    """向模板暴露卡片所需的规范化展示数据（供 overrides/main.html 消费）。"""
    meta = getattr(page, "meta", None) or {}
    if not meta or getattr(page, "is_index", False):
        return context

    card: dict = {}

    status = meta.get("status")
    if status in STATUS_LABELS:
        card["status"] = {"key": status, "label": STATUS_LABELS[status]}

    risk = meta.get("risk")
    if risk in RISK_META:
        icon, label = RISK_META[risk]
        card["risk"] = {"key": risk, "icon": icon, "label": label}

    applies = meta.get("applies_to") or []
    if applies:
        card["applies_to"] = [str(a) for a in applies]

    verified = meta.get("verified_on")
    if verified:
        card["verified_on"] = str(verified)

    modules = meta.get("tweak_module") or []
    if modules:
        card["modules"] = [str(m) for m in modules]
        link = _matrix_link(page)
        if link:
            card["matrix_url"] = link

    if card:
        context["meta_card"] = card
    return context
