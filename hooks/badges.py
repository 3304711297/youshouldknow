"""页面顶部徽章 + Material tags 注入（P2-13/P2-15，纯增量渲染层）。

- 徽章：由 page.meta 的 applies_to / risk / tweak_module 生成页顶
  Material admonition（abstract 样式，列表布局），联动模块带「覆盖矩阵」相对链接（P2-14）。
- tags：向模板上下文注入 `tags` 变量（Material 的 partials/tags.html 直接消费），
  内容为 applies_to + 风险等级；条目用 {"name": ...} 形式以匹配模板的 tag.name 访问。
- 分类索引页（is_index）与无 front matter 页面不做任何处理；任何异常静默跳过，
  绝不影响构建（--strict 下也不会因本 hook 失败）。

实现注意：mkdocs 1.6 进入 on_page_markdown 前已剥离 front matter，
meta 扩展的解析结果在 page.meta；material/tags 插件按 front matter 收集 tags（本库页面
FM 无 tags 键，插件不会注入同名上下文），因此这里注入的 context['tags'] 是唯一来源。
"""

from __future__ import annotations

import posixpath

RISK_META = {
    "low": ("🟢", "low"),
    "medium": ("🟡", "medium"),
    "high": ("🔴", "high"),
}
MATRIX_URL = "项目导航/覆盖矩阵/"


def _matrix_link(page) -> str | None:
    """覆盖矩阵页相对当前页的站内相对链接；解析失败返回 None（徽章退化为纯文本）。"""
    try:
        page_dir = posixpath.dirname(page.url.rstrip("/"))
        return posixpath.relpath(MATRIX_URL.rstrip("/"), start=page_dir or ".")
    except Exception:
        return None


def on_page_markdown(markdown: str, page, config, files):
    meta = getattr(page, "meta", None) or {}
    if not meta or getattr(page, "is_index", False):
        return markdown
    applies = meta.get("applies_to") or []
    risk = meta.get("risk")
    modules = meta.get("tweak_module") or []
    if not applies and not risk and not modules:
        return markdown

    items: list[str] = []
    if applies:
        items.append("- **适用范围**：" + "、".join(str(a) for a in applies))
    if risk in RISK_META:
        icon, label = RISK_META[risk]
        items.append(f"- **风险等级**：{icon} `{label}`")
    if modules:
        mod_text = "、".join(f"`{m}`" for m in modules)
        link = _matrix_link(page)
        if link:
            items.append(f"- **联动 tweakbyjie 模块**：{mod_text}（详见[覆盖矩阵]({link}/)）")
        else:
            items.append(f"- **联动 tweakbyjie 模块**：{mod_text}")

    badge = ['!!! abstract "适用范围 · 风险等级 · 联动模块"', ""] + [f"    {i}" for i in items]
    return "\n".join(badge) + "\n\n" + markdown


def on_page_context(context, page, config, nav):
    meta = getattr(page, "meta", None) or {}
    applies = meta.get("applies_to")
    risk = meta.get("risk")
    if applies and not getattr(page, "is_index", False):
        names = [str(a) for a in applies]
        if risk in RISK_META:
            names.append(f"风险：{RISK_META[risk][1]}")
        # partials/tags.html 迭代 tag.name / tag.url / tag.hidden，字典形式最稳
        context["tags"] = [{"name": n} for n in names]
    return context
