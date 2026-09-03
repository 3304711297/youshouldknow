---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# AI 工具

AI 编程助手、浏览器自动化、MCP（Model Context Protocol）工具链的使用与排错分类。

## 文章

- [让 AI 控制 Edge 浏览器：CDP 远程调试与 chrome-devtools-mcp 配置指南](./Edge浏览器CDP远程调试与AI接管指南.md) — edge://inspect 远程调试开关、autoConnect 配置、授权弹窗机制、中文扩展 locale 安装坑与解压版规避方案
- [ZCode 接入 Gemini 生图 Skill 与 Antigravity 桥接指南](./ZCode接入Gemini生图Skill与Antigravity桥接指南.md) — 基于 gemini-3.1-flash-image (Nano Banana 2) 的原生生图 Skill 制作、Antigravity 桥接解耦与排错实战
- [AI 浏览器自动化的扩展禁用陷阱与数据恢复](./AI浏览器自动化扩展禁用陷阱与数据恢复.md) — chrome-devtools-mcp 默认 `--disable-extensions` 清空扩展注册表的事故链、防护参数、三类扩展 ID 与数据恢复原理、lockfile 占用排查
- [hermes-agent Windows 部署与本地模型桥接实战](./hermes-agent-Windows部署与本地模型桥接实战.md) — 安装器两段式失败根因（代理/目录契约）、custom provider 接本地 OpenAI 兼容桥、Electron 桌面端与中文界面、MCP 挂载

## 与其他分类的边界

- 本类收录 AI 工具链本身的使用与配置；由 AI 辅助完成的系统调优结论仍归入对应主题分类。
- 浏览器客户端的常规设置（非 AI 控制）不在此类，归 `软件技巧/`。
