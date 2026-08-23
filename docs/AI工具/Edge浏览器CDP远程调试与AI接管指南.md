# 让 AI 控制 Edge 浏览器：CDP 远程调试与 chrome-devtools-mcp 配置指南

> 本文目标：让 AI 编程助手（ZCode、Claude Code、Copilot 等）通过 chrome-devtools-mcp **接管你日常正在使用的 Microsoft Edge**——保留全部登录态、Cookie 和扩展，而不是另开一个干净的临时浏览器。
>
> 实测环境：Microsoft Edge Dev 153.0.4224.0 / Windows 11 / ZCode。文中所有行为均经实机验证；Edge 稳定版与 Dev 版在本文涉及的开关上表现一致，但 153 引入的扩展安装问题（见第八节）为 Dev 渠道已知情况。
>
> **安全前提**：此模式开启后，AI 能看到浏览器里的全部登录信息与 Cookie。只对你信任的 AI 客户端使用。

## 一、原理与架构

整体链路是四层：

```text
AI 助手 → chrome-devtools-mcp → CDP（Chrome DevTools Protocol）→ 你的 Edge
```

- **MCP**：给 AI 提供标准化工具接口（打开网页、点击、填表、截图、读控制台等）。
- **CDP**：Chromium 内核的调试协议，Edge 同样支持，AI 通过它直接驱动浏览器底层能力。
- **chrome-devtools-mcp**：ChromeDevTools 官方的 MCP 服务器，基于 Puppeteer。

关键认知：**目标是接管"正在使用的那个 Edge"（默认用户数据目录）**，而不是让 AI 另起一个全新 Profile——后者正是很多 AI 浏览器方案"账号全是初始状态"的原因。

## 二、为什么不能用传统命令行参数直接接管默认 Profile（重要前置认知）

传统做法是给浏览器加启动参数 `--remote-debugging-port=9222`。但从 **Chromium 136 起，使用默认用户数据目录时这类外部远程调试参数受到安全限制**，直接依赖该参数接管日常 Profile 已不再是推荐路径。

需要特别区分两件事：

- **浏览器策略不是无效的**：Edge 的 `RemoteDebuggingAllowed=1` 策略可以允许远程调试，但它不能用来绕过 Chromium 对默认用户数据目录的安全限制。
- **显式传 `--user-data-dir` 指向同一个默认目录**：同样不能把默认 Profile 简单伪装成普通的自动化 Profile 来规避安全限制。
- **junction/符号链接改路径伪装成非默认目录**：端口能通，但会触发 Profile 完整性保护，**曾导致全部扩展被注销清空**，强烈不建议。

对于本文目标——**在保留日常 Edge 登录态、Cookie 和扩展的前提下，让 MCP 接管已经运行的浏览器**——正确路径是微软官方提供的浏览器内远程调试开关（下一节）。

## 三、第一步：开启 edge://inspect 远程调试开关

1. 在 Edge 地址栏输入 `edge://inspect` 回车；
2. 点左侧 **Remote debugging（远程调试）**;
3. 勾选 **允许对此浏览器实例进行远程调试**。

该勾选**持久化保存**（写入 Local State 的 `remote_debugging` 键），重启浏览器后依然生效，无需重复操作。

开启后，正常启动的 Edge 会自动在本机监听一个调试端口（实测为 9222），并在用户数据目录根下写出 `DevToolsActivePort` 文件（内容两行：端口号 + WebSocket 路径）。这个文件就是下一步 autoConnect 的发现依据。

!!! note "顶部横幅"
    开启后窗口顶部会出现「Microsoft Edge 正由自动测试软件控制」横幅，属正常提示。**不要点其中的「在设置中关闭」**，否则会关闭远程调试。

## 四、第二步：配置 MCP 客户端

以 ZCode 的用户级配置（`~/.zcode/cli/config.json`）为例，其他客户端（Claude Code、Cursor 等）把同一段 `mcpServers` 放进各自配置文件即可：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "npx",
      "args": [
        "-y",
        "chrome-devtools-mcp@latest",
        "--autoConnect",
        "--user-data-dir=C:\\Users\\你的用户名\\AppData\\Local\\Microsoft\\Edge Dev\\User Data"
      ]
    }
  }
}
```

要点：

- **必须用 `--autoConnect` + `--user-data-dir` 组合**：它读取用户数据目录下的 `DevToolsActivePort` 文件拿到端口和 WebSocket 路径后**直连**。
- **不要用 `--browserUrl http://127.0.0.1:9222`**：Edge 的这套远程调试端点把 HTTP 发现接口（`/json/*`）全部锁死（返回空 404），只有 WebSocket 可用，而 browserUrl 模式依赖 HTTP 发现。
- `--user-data-dir` 按实际渠道填写：Stable 为 `...\Microsoft\Edge\User Data`，Beta 为 `...\Microsoft\Edge Beta\...`，Dev 为 `...\Microsoft\Edge Dev\User Data`。
- 改完配置需重启 MCP 客户端（如 ZCode）生效。

## 五、第三步：连接授权弹窗（每个浏览器会话一次）

Edge 重启后的**第一次**外部连接会弹出确认框：

> 是否允许远程调试？——某个外部应用希望完全控制此 Microsoft Edge 会话以对其进行调试……

点**允许**即可，本次浏览器会话内后续连接不再询问（隔较久的新连接可能再次弹出）。这是 Chromium 144+ 上游的安全设计，换任何 Chromium 系浏览器都一样。

**日常使用节奏**：Edge 照常从任务栏启动；每次新开浏览器后，AI 第一次操作时点一次「允许」，仅此而已。若 AI 的工具调用超时无响应，大概率就是这个弹窗在等点击——点掉后让它重试。

## 六、验证连接

```powershell
curl.exe --noproxy "*" http://127.0.0.1:9222/json/version
```

注意两点：

- 记得绕过本机代理（加 `--noproxy "*"` 或系统代理排除 127.0.0.1）；
- 该端点的 HTTP 接口返回空 404 属**正常现象**（见第四节），不代表失败。真正的判据是 `DevToolsActivePort` 文件存在 + MCP 工具能列出标签页。

## 七、常见症状与排错速查

| 症状 | 原因 | 处理 |
| --- | --- | --- |
| MCP 报 ECONNREFUSED 127.0.0.1:9222 | Edge 没在运行 | 启动 Edge 即可 |
| 工具调用 30 秒超时、页面无响应 | 「是否允许远程调试」弹窗在等待点击 | 到 Edge 里点「允许」，再让 AI 重试 |
| list_pages 返回空 | 连接刚建立但未就绪 | 稍候重试同一调用 |
| 商店装不上扩展、报 locale 错误 | 见第八节 | 按第八节规避 |
| 扩展列表出现「无法加载扩展」错误弹窗 | Edge 自带组件扩展的加载报错 | 重启浏览器通常自愈，无需处理 |

## 八、附带坑：中文扩展安装报 locale 错误（153 已知问题）

Edge Dev 153 会**拒绝 manifest 中下划线写法的 `default_locale`（如 `"zh_CN"`）**，导致一批中文扩展无法从商店安装，三种安装方式全被拦：

- 商店安装：「Default locale is defined but default data couldn't be loaded」
- Chrome Web Store 安装：「下载时出错: 包无效」
- 开发者模式加载解压目录：「已使用本地化，但未在清单中指定 default_locale」

受影响案例：BilibiliSponsorBlock（小电视空降助手）、青柠起始页、better-XiaoHeiHe 等。而 `default_locale` 为 `"en"` 但同样带 `zh_CN` 语言文件夹的扩展（脚本猫、KISS Translator 等）一切正常。

**规避方案**（对解压版扩展）：

1. 把 manifest 中 `"default_locale"` 改为 `"en"`；
2. 确保 `_locales/en/messages.json` 存在（直接复制 `_locales/zh_CN/messages.json` 即可）；
3. `edge://extensions` 开启开发者模式 → 加载解压缩的扩展 → 选中该文件夹。

中文界面不受影响：浏览器语言为 zh-CN 时仍优先读取 zh_CN 语言文件夹。已在 BilibiliSponsorBlock（[issue #316](https://github.com/hanydd/BilibiliSponsorBlock/issues/316)）与 better-XiaoHeiHe（[issue #13](https://github.com/k1m0206/better-XiaoHeiHe/issues/13)）仓库提交完整报告。

!!! warning "解压版扩展注意事项"
    加载后**不要移动或删除源文件夹**，否则扩展失效。建议在 manifest 中加入随机生成的 `"key"` 字段固定扩展 ID，之后移动文件夹 ID 不变、数据不丢。

## 九、备选方案对比（为什么不推荐）

| 方案 | 结论 |
| --- | --- |
| 换 Chromium 系浏览器（Thorium 等） | 授权弹窗是 Chromium 144+ 上游行为，换了照样有；且失去 Edge 账号同步 |
| MCP 自管专用 Profile（`--executablePath` 启动模式） | 零弹窗，但那是独立 Profile，不是你正在用的浏览器 |
| Playwright 直接驱动 | 默认开全新临时 Profile，登录态全无 |

如果核心诉求就是「AI 接管原封不动的日常 Edge」，本文方案是当前摩擦最小的形态。

## 十、参考链接

- [微软官方文档：Let agents inspect your site with Chrome DevTools MCP](https://learn.microsoft.com/en-us/microsoft-edge/web-platform/devtools-mcp-server)
- [Chrome 官方博客：Debug your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [chrome-devtools-mcp 仓库](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [授权弹窗持久化请求 issue #825](https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/825) / [#1794](https://github.com/ChromeDevTools/chrome-devtools-mcp/issues/1794)
