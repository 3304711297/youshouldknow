---
applies_to:
  - Android 8.0+
  - Hermes Agent
  - 移动端远程控制
  - Flutter / Jetpack Compose
risk: low
status: reference
tweak_module: []
verified_on: 2026-09-07
---

# Hermes Agent Android 客户端选型与双端通信机制

> 本文目标：深入梳理社区两款主流开源 Android 客户端（`rusty4444/hermes-android` 与 `Hy4ri/hermes-mobile`）在架构协议、界面语言本地化及核心功能上的本质差异，并剖析 Hermes Agent 在局域网远程暴露时的安全门禁机制与双端（PC/手机）并发运行时会话隔离拓扑。
>
> 实测基准：Hermes Agent v0.21.0+ / Windows 11 / Android 14+ / 本地局域网 Wi-Fi。

---

## 一、 两款 Android 客户端架构横向评测

目前社区针对 Hermes Agent 的移动端控制主要有两款开源实现，二者在底层通信契约与产品定位上有着截然不同的取向：

| 核心特性 | rusty4444/hermes-android (v2.0.1) | Hy4ri/hermes-mobile (v1.22.1+) |
| :--- | :--- | :--- |
| **技术栈** | Flutter (Dart) + 原生平台插件 | 原生 Android (Kotlin + Jetpack Compose) |
| **主通信协议** | **Desktop Gateway JSON-RPC**（端口 8642） | **Dashboard REST + TUI WebSocket**（端口 9119） |
| **语言本地化 (i18n)** | ❌ 纯英文硬编码（暂未接入多语言框架） | ✅ **原生内置完整简体中文**（1000+词条，跟随系统或手动切换） |
| **Agent 交互保真度** | **极高（桌面对齐）**：原生展示工具调用流（Tool Activity）、思考链（Reasoning）、高危指令审批（Approval/Sudo）、反问澄清（Clarification）与子代理状态 | **中等**：侧重流式消息收发，细粒度工具事件与深度审批流相对简化 |
| **移动端专有特性** | **后台任务通知**（Turn Notification）与**断线恢复**（Turn Recovery），支持 Per-chat 模型与思考强度调节 | **系统级全功能控制台**：实时日志流过滤、环境变量编辑、Cron 管理、Kanban 看板、6 套暗黑主题 |
| **选型适用场景** | 移动端替代桌面操控、重度代码/工具执行、需审批交互与推理思考展示 | 移动端运维管理、看日志查配置、对**中文原生界面**有刚性需求的用户 |

---

## 二、 局域网服务暴露与安全门禁最佳实践

Hermes Agent 原生设计具备严格的网络安全边界，当试图在非本地回环地址（`0.0.0.0`）暴露端口供局域网手机连接时，将强制触发安全防御机制：

### 1. 安全门禁拦截机理
若直接执行 `hermes dashboard --host 0.0.0.0 --port 9119`，控制台将抛出：
```text
Refusing to bind dashboard to 0.0.0.0 — the auth gate engages on non-loopback binds,
but no auth providers are registered.
```
Hermes 在对全网卡开放绑定时，禁止无密码公开裸奔，必须配置身份认证提供商（Basic Auth 或 OAuth）。

### 2. 避免配置文件污染的环境变量注入法
官方常规做法是修改 `~/.hermes/config.yaml` 增加 `dashboard.basic_auth`，但这会导致配置文件缩进重排、引入版本漂移并影响多端同步基准。

**最优解**：将认证凭据安全注入到用户专属环境变量文件 `~/.hermes/.env` 中（Hermes 启动时自动优先加载）：
```ini
# Gateway API (针对 hermes-android)
API_SERVER_KEY=your_generated_hex_token_32bytes_or_more
API_SERVER_HOST=0.0.0.0
API_SERVER_PORT=8642

# Dashboard Basic Auth (针对 hermes-mobile)
HERMES_DASHBOARD_BASIC_AUTH_USERNAME=admin
HERMES_DASHBOARD_BASIC_AUTH_PASSWORD=your_secure_password
```
- 配置完成后，重启网关即可自动生效，既通过了启动时的非空与强度校验，又避免了改动主配置文件的副作用。

### 3. Windows 本地防火墙放行
在宿主机 Windows PowerShell 执行入站规则放行：
```powershell
New-NetFirewallRule -DisplayName "Hermes Gateway API LAN" -Direction Inbound -LocalPort 8642 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "Hermes Dashboard LAN" -Direction Inbound -LocalPort 9119 -Protocol TCP -Action Allow
```

---

## 三、 PC 桌面端与移动端双进程通信拓扑解析

许多用户在手机端连通并发消息后，常疑惑为何 **“电脑屏幕上的当前会话没有实时同步打字”**。这是由 Hermes 的多进程运行时架构所决定的：

```text
[ 用户操作 ]
    │
    ├─► PC 桌面客户端 (Hermes Desktop) ──► 专属私有进程 (127.0.0.1:<动态端口>；⚠️ 2026-09-12 核实：桌面端用 `hermes serve --port 0` 由 OS 分配临时端口，图中 4837 为某次实测快照值，非固定) ──┐
    │                                                                      ▼
    └─► 手机端 App (Mobile Client)     ──► 共享网关服务 (0.0.0.0:9119)   ──┼──► 统一数据库 (state.db)
                                                                           │
                                                                           ▼
                                                                  持久化会话与历史消息
```

1. **运行时内存与推送通道解耦**：
   - PC 桌面端启动时会拉起独立的私有托管进程（`serve --port 0`，动态端口），桌面的输入与响应流仅在该专属 WebSocket 通道内推送；
   - 手机端连接的是系统级常驻的 Gateway / Dashboard 端口，两者的运行时内存状态并不直接互联。
2. **底层数据真实一致性**：
   - 手机端发送的消息与生成的 Agent 回复，都会实时同步落盘写入 SQLite `state.db`。
   - 若手机新建了独立会话（例如 `20260907_xxxxxx`），PC 桌面端为了避免打断用户当前屏幕操作，不会主动强制切页；用户只需在 PC 客户端历史会话列表搜索该会话标题，点击即可无缝查看手机上的完整对话与执行过程。
