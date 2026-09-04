---
applies_to:
  - Windows 10/11
  - EasyCLIProxyAPI 使用者
  - Hermes Agent / ZCode / Claude Code / Codex 多智能体用户
risk: low
tweak_module: []
---

# EasyCLIProxyAPI 本地网关架构与多智能体客户端适配

> 本文目标：全面梳理本地大模型网关从非官方分叉（ZCode-Antigravity）向官方稳定核心（EasyCLIProxyAPI 7.2.149+）迁移的演进历程；详解 **Hermes Agent** 与 **ZCode** 双端接入使用 Gemini 3.8/3.7 Flash 的完整配置步骤、关键配置文件、避坑指南与常见故障速查表。
>
> 实测环境：Windows 11 / EasyCLIProxyAPI 0.2.71 (Core 7.2.149) / Hermes Agent / ZCode 客户端 / Google AI Pro 个人订阅。

## 一、 本地模型网关的架构演进

在日常使用多种 AI 编程助手（如 Hermes Agent、ZCode、Claude Code、Codex）时，很多开发者选择在本地搭建网关以统一承接 Google Antigravity、Kimi、Claude 等模型渠道。

```text
               ┌───────────────────────┐
               │     Hermes Agent      │ (OpenAI 兼容协议 / 18080)
               └───────────┬───────────┘
                           │
                           ▼
               ┌───────────────────────┐
┌─────────────►│    EasyCLIProxyAPI    │◄────────────┐
│              │ (官方核心 v7.2.149)   │             │
│              └───────────┬───────────┘             │
│                          │                         │
│ (Anthropic 协议 / 18080) │                         │
│                          ▼                         │
┌─────────────┐  ┌───────────────────┐ ┌─────────────┴──────────┐
│    ZCode    │  │ 本地代理 127.0.0.1 │ │ 其它 CLI 智能体 (Codex) │
└─────────────┘  └─────────┬─────────┘ └────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │ Google Antigravity 服务 │
              └─────────────────────────┘
```

### 1. 早期分叉分支的局限与风险
早期社区存在基于旧版本修改的中间派生版本（例如 ZCode-Antigravity 7.2.132-zcode）。在实际生产使用中，此类版本暴露出以下问题：
- **凭据丢失陷阱**：官方二进制在发布期通过 `-X ldflags` 注入了官方发布的 OAuth Client ID 与 Secret；若在本地直接裸 `go build` 编译，源码中的变量为空，会导致运行时抛出 `500 OAuth client is not configured`，随后标记为 `503 auth_unavailable`，造成大面积鉴权不可用；
- **私有接口依赖**：派生版本常会添加非官方标准接口（如 `/v0/management/api-call`），导致外部插件产生私有依赖，一旦版本升级就会彻底失效。

### 2. 迁移至官方核心的优势
随着上游官方核心演进至 `7.2.149`（EasyCLIProxyAPI 桌面控制台标配）：
- **原生多模型支持**：上游已原生集成 `gemini-3.8-flash`、`gemini-3.8-flash-high`、`gemini-3.7-flash` 等全系模型及思考推理链（Thinking Variant）；
- **官方内嵌安全凭据**：官方发行版自带合法 OAuth 认证身份，规避本地编译导致凭据丢失的风险；
- **双协议原生互通**：同时支持标准 OpenAI 格式（`/v1/chat/completions`）与 Anthropic Messages 格式（`/v1/messages`），Hermes Agent 与 ZCode 可共用同一个 `127.0.0.1:18080` 端口无缝并发调用。

## 二、 Windows 客户端探查陷阱与目录联接（Junction）

在 EasyCLIProxyAPI 桌面控制台的「智能体配置」中，有时会遇到一个典型问题：**本地明明确认已安装了 ZCode 等客户端，但界面却弹出黄色警告“只检测到配置文件，未检测到客户端”，且右下角启动按钮显示“无法启动”被禁用**。

### 1. 探查机制排查
反编译与特征码扫描显示，控制台在 Windows 上采用固定硬编码的规范路径来探测客户端可执行文件：
- `%LOCALAPPDATA%\Programs\<Agent>\<Agent>.exe`（用户级安装规范路径）
- `%ProgramFiles%\<Agent>\<Agent>.exe`（系统级 64 位标准安装路径）

若用户将客户端安装在非系统盘（例如 `D:\zcode\ZCode.exe`），控制台仅能在用户目录（`~/.zcode`）找到配置，却无法在默认路径找到程序实体，因而禁用启动逻辑。

### 2. 优雅解决方案：NTFS 目录联接（Junction）
无需搬迁文件或重装软件，只需以管理员权限在命令行中建立 NTFS 目录联接即可：

```cmd
:: 映射到用户本地应用规范路径
mklink /J "%LOCALAPPDATA%\Programs\ZCode" "D:\zcode"

:: 映射到系统 Program Files 规范路径
mklink /J "%ProgramFiles%\ZCode" "D:\zcode"
```

**原理解析**：
- `mklink /J` 是 Windows 文件系统底层的硬链接变种（Junction Point），不占额外磁盘空间，对所有应用程序 100% 透明；
- 建立联接后，控制台在标准路径即可瞬间探测到 `ZCode.exe`，版本信息立刻正常显示，“无法启动”按钮随之恢复为正常启动控制。

## 三、 Hermes Agent 接入使用 Gemini 配置实战

Hermes Agent 底层采用标准 OpenAI 兼容格式对接本地网关，主要通过配置文件 `~/.hermes/config.yaml` 管理。

### 1. 主模型与辅助模型配置
在 `config.yaml` 中配置默认主力模型与提供商：

```yaml
model:
  default: gemini-3.8-flash
  provider: cpa-gui
  base_url: http://127.0.0.1:18080/v1

auxiliary:
  vision:
    provider: cpa-gui
    model: gemini-3.8-flash

agent:
  reasoning_effort: ultra # 开启 Gemini 3.8 Flash Ultra 思考链
```

### 2. 自定义提供商注册 (`custom_providers`)
确保在 `custom_providers` 列表内注册统一且唯一的 `cpa-gui` 项：

```yaml
custom_providers:
  - name: cpa-gui
    base_url: http://127.0.0.1:18080/v1
    api_key: wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0 # 取自 EasyCLIProxyAPI 的 api-keys
    api_mode: chat_completions
    model: gemini-3.8-flash
    models_discovered: true
    models:
      gemini-3.8-flash: {}
      gemini-3.7-flash: {}
      gemini-3.6-flash: {}
      gemini-3.1-pro-low: {}
      gemini-web-search: {}
      claude-sonnet-4-6: {}
      claude-opus-4-6-thinking: {}
      gpt-oss-120b-medium: {}
```

### 3. 注意点与防坑准则
- **严禁重复定义提供商**：旧版配置常遗留 `Local (127.0.0.1:18080)`。若与 `cpa-gui` 同时存在，二者打向同一端口，会导致桌面 GUI 的模型下拉框内出现两套完全重合的模型列表。必须清理掉冗余项；
- **凭据池同步清理**：编辑 `config.yaml` 去除重复项后，需同步检查 `~/.hermes/auth.json` 中的 `credential_pool`，删除废弃条目；
- **浏览器沙箱强制隔离**：配置 `browser.use_real_profile: false`，避免 Agent 浏览器操作污染甚至清空日常 Edge/Chrome 的扩展注册表。

## 四、 ZCode 客户端接入使用 Gemini 配置实战

ZCode 客户端与 OpenAI 格式不同，其底层采用的是 **Anthropic Messages 协议（`/v1/messages`）**。EasyCLIProxyAPI 官方核心原生支持此格式转换。

### 1. 配置文件双层定位
ZCode 的配置分为两层，建议同步配置：
1. **全局默认配置**：`C:\Users\<用户名>\.zcode\v2\config.json`
2. **工作区定制配置**：`<项目根目录>\.zcode\v2\config.json`（若存在）

### 2. 提供商注入 (`zcode-antigravity-local`)
在 `config.json` 的 `provider` 字典中注入 Google 本地网关节点：

```json
{
  "provider": {
    "zcode-antigravity-local": {
      "name": "Google",
      "kind": "anthropic",
      "options": {
        "apiKey": "wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0",
        "baseURL": "http://127.0.0.1:18080",
        "apiKeyRequired": true
      },
      "enabled": true,
      "source": "custom",
      "x-zcode-antigravity-managed": 1,
      "models": {
        "gemini-3.8-flash": {
          "name": "Gemini 3.8 Flash",
          "limit": { "context": 1048576 },
          "modalities": {
            "input": ["text", "image", "audio", "video"],
            "output": ["text"]
          },
          "reasoning": {
            "enabled": true,
            "variants": ["low", "medium", "high"],
            "defaultVariant": "high"
          },
          "zcode": { "priority": 200 }
        },
        "gemini-3.7-flash": {
          "name": "Gemini 3.7 Flash",
          "limit": { "context": 1048576 },
          "modalities": {
            "input": ["text", "image", "audio", "video"],
            "output": ["text"]
          },
          "reasoning": {
            "enabled": true,
            "variants": ["low", "medium", "high"],
            "defaultVariant": "high"
          },
          "zcode": { "priority": 201 }
        },
        "gemini-3.1-pro-low": {
          "name": "Gemini 3.1 Pro (Low)",
          "limit": { "context": 1048576 },
          "modalities": {
            "input": ["text", "image", "audio", "video"],
            "output": ["text"]
          },
          "reasoning": { "enabled": true, "variants": ["low", "medium", "high"], "defaultVariant": "low" },
          "zcode": { "priority": 203 }
        },
        "gemini-web-search": {
          "name": "Gemini Web Search (Google)",
          "limit": { "context": 1048576 },
          "modalities": {
            "input": ["text", "image", "audio", "video"],
            "output": ["text"]
          },
          "zcode": { "priority": 204 }
        }
      }
    }
  }
}
```

### 3. 模型列表置顶展示
在 `~/.zcode/v2/model-provider-display-order.json` 中，将 `"zcode-antigravity-local"` 放置在 `providerIds` 数组的**首位**：

```json
{
  "providerIds": [
    "zcode-antigravity-local",
    "builtin:bigmodel",
    "builtin:zai"
  ]
}
```

这样启动 ZCode 后，顶部模型下拉框首项即为 Google 官方 Gemini 全系模型。

## 五、 全流程避坑与常见故障速查表（血泪经验汇编）

| 故障现象 | 触发时机 / 原因 | 避坑方案与解决对策 |
| :--- | :--- | :--- |
| **HTTP 500 后变 503 `auth_unavailable`** | 本地直接裸 `go build` 编译 CLIProxyAPI 二进制，丢失了官方发布期通过 `-X ldflags` 注入的 OAuth Client 凭据。 | **严禁用本地裸构建覆盖官方核心**。直接使用 EasyCLIProxyAPI 官方预编译的 `cpa-core\cli-proxy-api.exe`（7.2.149+）。 |
| **“只检测到配置文件，未检测到客户端”** | EasyCLIProxyAPI 控制台硬编码探查系统盘规范路径，而 ZCode 安装在 `D:\zcode`。 | 在 `%LOCALAPPDATA%\Programs\ZCode` 与 `%ProgramFiles%\ZCode` 建立 NTFS 目录联接（`mklink /J`）。 |
| **Hermes 模型下拉列表重复翻倍** | `config.yaml` 中同时保留了旧网关名称（`Local (127.0.0.1:18080)`）与新网关名称（`cpa-gui`）。 | 清理 `config.yaml` 与 `auth.json`，统一规范化为单实例 `cpa-gui`。 |
| **日常浏览器扩展和脚本全清空** | Hermes 开启了 `browser.use_real_profile: true`，自动化实例退出时把无扩展加载的内存状态写回了日常配置。 | 在 `config.yaml` 中明确设置 `browser.use_real_profile: false`，彻底沙箱化。 |
| **两端查看的 Google 配额完全不一致** | 通用 Google 生产端点 `cloudcode-pa` 与 Antigravity 专有端点 `daily-cloudcode-pa` 属于云端解耦配额池。 | 查询 Antigravity 实际调用消耗时，**必须指定 `daily-cloudcode-pa.googleapis.com` 端点**。 |
| **HTTP 403: IP banned due to too many failed attempts** | 前端微件使用普通 API Key 频繁轮询 `/v0/management/` 高权限管理接口，触发了防爆破 30 分钟 IP 熔断。 | 数据面与管理面隔离；获取配额改走本地轻量 Python 微服务，绝不高频撞击管理接口。 |
| **刷新配额点击无反应 / 误以为卡死** | 内存防抖缓存瞬间命中，且界面缺乏加载动画与完成时间戳。 | 后端增加 `?force=1` 穿透参数；前端配套 SVG 旋转 Spinner、`✓ 已刷新` 徽章变形与 Toast 弹窗反馈。 |
