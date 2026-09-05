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
- [AI 浏览器自动化的扩展禁用陷阱与数据恢复](./AI浏览器自动化扩展禁用陷阱与数据恢复.md) — chrome-devtools-mcp 默认 `--disable-extensions` 清空扩展注册表的事故链、防护参数、三类扩展 ID 与数据恢复原理、lockfile 占用排查
- [hermes-agent Windows 部署与本地模型桥接实战](./hermes-agent-Windows部署与本地模型桥接实战.md) — 安装器两段式失败根因（代理/目录契约）、custom provider 接本地 OpenAI 兼容桥、Electron 桌面端与中文界面、MCP 挂载
- [Google Antigravity 与 CloudCode PA 双配额池隔离陷阱与实时监控](./Google-Antigravity双配额池隔离陷阱与实时监控.md) — Google 云端配额桶隔离机制、daily-cloudcode-pa 专有通道实测比对、本地轻量微服务防抖架构
- [EasyCLIProxyAPI 本地网关架构与多智能体客户端适配](./EasyCLIProxyAPI本地网关架构与多智能体客户端适配.md) — 官方核心演进、Hermes 与 ZCode 双端接入 Gemini 3.8 实操配置、Gemini 生图 Skill（Nano Banana 2）、Windows 客户端 NTFS 目录联接与全流程避坑速查
- [Hermes-Agent 高阶指令全景与官方生态指南](./Hermes-Agent高阶指令全景与生态路线指南.md) — 目标导向/自动循环/后台任务等八大场景指令矩阵、Nous 官方文档与 FAQ 核心避坑、Tonbi Masterclass 视频课与 Wingtips 实战准则
- [Hermes×ZCode 双 Agent 跨端协同机制实战](./Hermes-ZCode双Agent跨端协同机制实战.md) — watch_zcode.py 守护 + 进程退出事件自动唤醒、db.sqlite 只读监听、握手文件反向等待、"开始盯"时序铁律与误报警示
- [WorkBuddy 积分端到端打通实录](./WorkBuddy积分端到端打通实录.md) — 哑管道问题定位、/api/usage_summary 端点契约（ZCode 施工）、token-stats 插件卡片升级与双端数据一致性验证方法论
- [Hermes 子代理模型路由机制](./Hermes子代理模型路由机制.md) — delegation 默认继承实证、官方文档优先级、Kanban per-task override 与"不固定模型，用户口头裁决"实践范式、思考型模型 max_tokens 假阳性
- [ZCode headless CLI 与 GUI 会话体系辨析](./ZCode-headless-CLI与GUI会话体系辨析.md) — project_id 落点差异实测、两套模型体系分离、18080 网关/Gemini 429 故障链与"GUI 手动建会话"实践规范

## 与其他分类的边界

- 本类收录 AI 工具链本身的使用与配置；由 AI 辅助完成的系统调优结论仍归入对应主题分类。
- 浏览器客户端的常规设置（非 AI 控制）不在此类，归 `软件技巧/`。
