---
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
  - OpenAI 兼容本地推理桥
risk: low
tweak_module: []
---

# hermes-agent Windows 部署与本地模型桥接实战

> 本文目标：在 Windows 上把开源个人助理框架 [hermes-agent](https://github.com/NousResearch/hermes-agent)（Nous Research 出品，含 CLI / TUI / 消息网关 / Electron 桌面端）完整落地，并把它的主模型接到**本地已有的 OpenAI 兼容推理桥**上——与《ZCode 接入 Gemini 生图 Skill 与 Antigravity 桥接指南》中的桥接复用同一入口，一个桥喂多个 AI 客户端。
>
> 实测环境：Windows 11 / hermes-agent v0.21.0 / PowerShell 5.1 与 7 双版本 / Node 24 / 本地 OpenAI 兼容桥（127.0.0.1 本地端口）。安装、模型接入、GUI、中文界面、MCP 挂载均实机验证。

## 一、安装：官方一条命令，但有两个 Windows 专属坑

官方安装方式（PowerShell）：

```powershell
irm https://hermes-agent.nousresearch.com/install.ps1 | iex
```

安装器会自动准备 uv、托管版 Python 3.11、Git、Node.js、ripgrep、ffmpeg，并把代码以 git checkout 形式放到安装目录。首次安装失败基本都卡在下面两个坑上。

### 坑一：git 与 uv 不读 Windows 系统代理

安装器内部有两类下载通道，行为完全不同：

| 通道 | 代理行为 |
| --- | --- |
| PowerShell 的 `Invoke-WebRequest`（下载安装脚本、ZIP 回退包） | 走系统代理，正常 |
| 安装器调用的 `git clone`（GitHub 检出） | **不走系统代理**，只认 `http.proxy` 配置或环境变量 |
| uv 下载托管 Python | **不走系统代理**，只认环境变量 |

于是出现一个非常有迷惑性的现象：安装日志显示 ZIP 包下载成功（走系统代理的通道），紧接着 git 克隆却 `Connection was reset`，Python 运行时下载中断留下 `python.incomplete-<时间戳>` 残留目录。**解法是在运行安装器的同一个 shell 里先显式导出代理**：

```powershell
$env:HTTP_PROXY  = "http://127.0.0.1:<本地代理端口>"
$env:HTTPS_PROXY = "http://127.0.0.1:<本地代理端口>"
```

环境变量随进程继承，git 与 uv 都认。这条同样适用于后续的 `hermes update`。

### 坑二：失败的旧安装目录会被整体移走

安装器检测到安装目录存在但"不是有效 git 仓库"时，会把整个目录改名移开（`hermes-agent.broken-<时间戳>`）再重新克隆。如果你的托管 Python 运行时恰好装在这个目录里（`.hermes-runtime\python`），它会跟着旧目录一起消失——表现为上一次明明装好了 Python、下一次运行却报"Hermes-managed Python is unavailable"。手工补救：先用 uv 手动装回运行时，再重跑安装器：

```powershell
# 定向补装运行时（UV_PYTHON_INSTALL_DIR 指向安装目录内的运行时位置）
$env:UV_PYTHON_INSTALL_DIR = "<安装目录>\hermes-agent\.hermes-runtime\python"
uv python install 3.11
```

## 二、目录契约

Windows 原生安装的默认布局（`HERMES_HOME` 用户环境变量指向数据主目录）：

```text
%LOCALAPPDATA%\hermes\          ← HERMES_HOME（数据主目录）
├── hermes-agent\               ← 代码（git checkout，hermes update 在此更新）
│   ├── .hermes-runtime\python\ ← 托管 Python 3.11
│   └── apps\desktop\           ← Electron 桌面端源码与构建产物
├── bin\                        ← hermes.exe / uv.exe 等可执行入口
├── config.yaml                 ← 主配置（模型、浏览器、MCP 服务器）
├── .env                        ← 环境变量与密钥
├── skills\                     ← 技能（内置 + 本地自建共存）
├── memories\ sessions\ cron\   ← 数据目录
└── logs\gateway.log            ← 网关日志（见第六节）
```

用户主目录下的 `~\.hermes` 是另一套历史目录布局，重装前若两套并存，先确认 `HERMES_HOME` 实际指向哪套再迁移数据。

## 三、主模型接入本地 OpenAI 兼容桥

`config.yaml` 的 model 段支持 `provider: custom` 直连任意 OpenAI 兼容端点，且密钥可直接写在配置里：

```yaml
model:
  default: <模型名>
  provider: custom
  base_url: http://127.0.0.1:<桥接端口>/v1
  api_key: <桥接侧的访问密钥>
```

- 本地桥如果就是 Antigravity 桥接（`cli-proxy-api`），模型列表用 `GET /v1/models`（带 `Authorization: Bearer <key>`）查询，把 `default` 换成列表中任意模型即可切换；
- 改完用一次性模式冒烟：`hermes -z "你现在用的是什么模型？"`——只输出最终回答，适合脚本化验证；
- `hermes model` 可交互式切换默认模型；
- 日志中出现的 Nous/OpenRouter 辅助通道警告属正常：主模型走 custom 时，辅助小模型通道（摘要、记忆整理等）未配置密钥则不可用，不影响主对话。

## 四、桌面端 GUI 与中文界面

- **`hermes desktop`**：官方 Electron 桌面应用。首次运行会自动安装工作区依赖并打包（Electron 二进制下载同样需要第三节的环境变量代理），产物在 `hermes-agent\apps\desktop\release\win-unpacked\Hermes.exe`，可为其创建桌面快捷方式；`hermes update` 后重跑一次 `hermes desktop` 即可刷新构建。
- **`hermes dashboard`**：浏览器版管理页（配置、密钥、会话管理），不适合聊天。
- **`hermes serve`**：桌面端依赖的无头后端，日常无需单独操作。
- **中文界面**：桌面端设置 → 外观（Appearance）→ 语言（Language），内置简体中文/繁體中文/English/日本語/العربية/Русый 六种，选择持久化写入配置。中文包覆盖界面层；对话语言由模型决定，两者互不影响。

## 五、MCP 服务器挂载与共享记忆

`config.yaml` 的 `mcp_servers` 段可挂载任意 MCP 服务器，与 CLI/TUI/GUI 所有会话形态共用。Windows 下把 npx 类命令用 `cmd /c` 包装最稳：

```yaml
mcp_servers:
  chrome-devtools:
    command: cmd
    args:
      - /c
      - npx
      - -y
      - chrome-devtools-mcp@latest
      - --autoConnect
      - --ignore-default-chrome-arg=--disable-extensions
      - --user-data-dir=<浏览器用户数据目录>
    enabled: true
```

**`--ignore-default-chrome-arg=--disable-extensions` 必加**，原因与事故复盘见本站《AI 浏览器自动化的扩展禁用陷阱与数据恢复》。

本地自建技能（skill）的约定：在 `%LOCALAPPDATA%\hermes\skills\<技能名>\SKILL.md` 放置带 YAML frontmatter（`name` + `description`）的 Markdown 即被自动发现，无需注册；frontmatter 必须是无 BOM 的 UTF-8（BOM 会让解析静默失败）。配合常驻人格文件 `SOUL.md` 中的一段指针，可以让多个 AI 客户端共享同一套文件型记忆库（协议写在技能文件里，双方按约定读写）。

## 六、排障速查

| 现象 | 原因与处理 |
| --- | --- |
| 安装时 git clone / Python 下载被重置 | git/uv 不走系统代理，见第一节坑一 |
| 报 "Hermes-managed Python is unavailable" | 旧目录被整体移走带丢了运行时，见第一节坑二 |
| 网关"卡住不动"没有就绪日志 | 就绪日志写在 `logs\gateway.log` 文件里，**不进 stdout**，看文件别盯终端 |
| 怀疑网关状态陈旧 | 对比 `gateway_state.json` 里的 pid 与 `tasklist`，进程不存在即为陈旧状态 |
| 每次启动日志抛 `AttributeError: module 'asyncio' has no attribute 'start_unix_server'` | 上游 Windows 兼容 bug（shutdown_watchdog），非致命，等官方修复 |
| MCP 服务器拉不起来 | Windows 下 npx 类命令用 `cmd /c` 包装；MCP 的 stderr 在 `logs\mcp-stderr.log` |

## 七、参考链接

- [NousResearch/hermes-agent 仓库](https://github.com/NousResearch/hermes-agent)
- 本站《ZCode 接入 Gemini 生图 Skill 与 Antigravity 桥接指南》——本地 OpenAI 兼容桥的搭建与解耦
- 本站《AI 浏览器自动化的扩展禁用陷阱与数据恢复》——MCP 启动参数的防护细节
