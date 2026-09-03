---
applies_to:
  - Windows 10/11
  - Chrome/Edge（Chromium 内核浏览器）
  - chrome-devtools-mcp 与同类浏览器自动化 MCP 使用者
risk: medium
tweak_module: []
---

# AI 浏览器自动化的扩展禁用陷阱与数据恢复

> 本文目标：讲清浏览器自动化类 MCP（以 chrome-devtools-mcp 为例）一个极易踩中的默认行为——**MCP 亲自启动浏览器时会带 `--disable-extensions`**，特定时序下会把扩展注册表"清空"，表现为扩展和脚本管理器里的东西一夜之间全部消失；以及如何防护、如何在不丢数据的前提下完整恢复。
>
> 实测环境：Microsoft Edge Dev 154 / Windows 11 / chrome-devtools-mcp 1.7.0。文中故障链与恢复流程均为实机复现结论；参数行为对照 chrome-devtools-mcp 源码与 Puppeteer 默认参数表核实。

## 一、结论速览

| 场景 | 结果 |
| --- | --- |
| MCP 连接到**已运行**的浏览器（autoConnect 成功附着） | 不涉及启动参数，扩展不受影响 |
| MCP **亲自启动**浏览器（浏览器当时是关闭状态） | 默认带 `--disable-extensions`，该会话内扩展全部不可用 |
| 带参启动的会话退出时写回配置 | 可能将扩展注册表（Preferences 的 `extensions.settings`）清零 |
| 扩展数据目录（脚本、登录态、设置） | **全程不被删除**，恢复后原样回来 |

**防护一行解决**：给 MCP 启动参数加上

```text
--ignore-default-chrome-arg=--disable-extensions
```

## 二、事故链复盘

chrome-devtools-mcp 基于 Puppeteer，其默认启动参数表包含 `--disable-extensions`（源码中的默认参数列表可见该项；这是自动化场景的保守安全默认）。完整故障链有四个条件叠加：

1. **MCP 亲自启动浏览器**：autoConnect 模式下，若目标浏览器当时没有运行，MCP 会用它配置的 `--user-data-dir` 拉起一个新的浏览器实例——此时默认参数生效。
2. **指向真实配置目录**：为了保留登录态，`--user-data-dir` 指向日常使用的用户数据目录。
3. **会话中扩展被禁**：该实例内所有扩展不可用（`edge://extensions` 页面为空）。
4. **退出时写回**：浏览器进程退出时把内存中的配置状态写回磁盘的 `Preferences` 文件，`extensions.settings` 字段被清零。

之后用户正常打开浏览器，看到的就是"扩展和脚本全没了"。实际上：

- 商店扩展的程序包目录（`<User Data>/<Profile>/Extensions/<ID>/`）可能仅余系统组件；
- **所有扩展的数据目录完好无损**：`Local Extension Settings/<ID>/`、`Sync Extension Settings/<ID>/`、`IndexedDB/chrome-extension_<ID>_0.indexeddb.*`；
- 脚本管理器（如 ScriptCat）的全部脚本就存在上述数据目录里。

判定方法：用 Python 或文本编辑器查看 `<Profile>/Preferences` 的 `extensions.settings` 是否为空数组/空对象，同时确认数据目录仍在——**注册表被清、数据还在**，即本文场景，可完整恢复。

## 三、三类扩展 ID 与对应恢复方式

扩展数据目录以扩展 ID 命名，ID 能否对上决定数据是否自动接回。Chromium 系浏览器的扩展 ID 有三种来源：

| 安装方式 | ID 来源 | 恢复要点 |
| --- | --- | --- |
| 应用商店安装 | 商店签发的 CRX 公钥哈希，**同一商品 ID 恒定** | 从原商店重装，ID 必然一致，数据自动接回 |
| 打包安装（manifest 声明 `key` 字段） | 由 `key` 派生，**换机器换路径 ID 不变** | 任意路径重新加载即可 |
| 开发者模式加载解压目录 | **由绝对路径哈希派生** | **必须从原路径重新加载**，同路径=同 ID；路径变了 ID 就变 |

解压版扩展的"原路径重载"特性是恢复的关键：只要目录没有移动过，重新加载一次，数据目录立刻重新关联。

恢复操作：

1. 打开 `edge://extensions`（或 `chrome://extensions`），开启**开发人员模式**；
2. 商店扩展：从原商店页面重新安装；
3. 解压扩展：逐个「加载解压缩的扩展」指向原目录；
4. 打开扩展面板确认数据（脚本、设置）已回来。

若解压扩展的原目录已删除导致无法原路径重载，ID 会变化，此时需要**数据迁移**：关闭浏览器，把旧 ID 命名的数据目录（`Local Extension Settings`、`Sync Extension Settings`、`IndexedDB/chrome-extension_<旧ID>_*`、`Extension State` 中相关键）改名/复制为新 ID，再启动浏览器。

## 四、防护配置

chrome-devtools-mcp 官方提供了忽略单个默认参数的选项：

```text
--ignore-default-chrome-arg=--disable-extensions
```

常见客户端配置示例（Windows 下 MCP 命令用 `cmd /c npx` 包装最稳）：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "cmd",
      "args": [
        "/c", "npx", "-y", "chrome-devtools-mcp@latest",
        "--autoConnect",
        "--ignore-default-chrome-arg=--disable-extensions",
        "--user-data-dir=C:\\Users\\<用户名>\\AppData\\Local\\Microsoft\\Edge\\User Data"
      ]
    }
  }
}
```

建议所有会把 `--user-data-dir` 指向真实配置目录的自动化配置都加这一参数。另有一个整体开关 `--ignore-default-chrome-args`（复数）可忽略全部默认参数，粒度更粗、需自行补齐必要参数，一般用单项形式即可。

## 五、关联故障：浏览器点开没反应（lockfile 占用）

自动化测试中断（进程被强杀、会话异常退出）常留下两类残留，二者都会导致浏览器**点击图标后无窗口**：

1. **孤儿 MCP 进程**：会话结束后未退出的 npx/node 进程群，继续持有浏览器配置目录的句柄；
2. **无头 Chromium 残留**：自动化链路（Playwright 等）拉起的无头实例没有窗口、进程名可能与浏览器不同（如 `chrome.exe`），常规按浏览器进程名过滤会漏检。

它们占住用户数据目录根下的 `lockfile`，新启动的浏览器检测到锁被占用就静默退出。排查流程：

```powershell
# 1. 确认没有正常的浏览器进程
Get-Process msedge, chrome -ErrorAction SilentlyContinue

# 2. 用 Sysinternals handle 定位占用者（https://live.sysinternals.com/handle.exe）
handle.exe -nobanner "User Data\lockfile"

# 3. 终止占用进程后，删除陈旧锁文件与调试端口残留
Remove-Item "<User Data>\lockfile", "<User Data>\DevToolsActivePort" -Force
```

之后浏览器即可正常启动。注意 `DevToolsActivePort` 文件也是会话残留，一并删除无副作用。

## 六、与 CDP 调试端口封锁的关系

Chromium 136 起出于安全考虑，**对默认用户数据目录忽略 `--remote-debugging-port` / `--remote-debugging-pipe` 启动参数**——即使显式把 `--user-data-dir` 指向默认目录本身也一样。这意味着：

- 想通过 CDP 端口附着到"日常使用的原配置浏览器"这条路在新版 Chromium 上走不通；
- 实测 Edge Dev 154 上设置 `RemoteDebuggingAllowed`、`DevToolsRemoteDebuggingAllowed` 策略（HKCU/HKLM）均未能解锁该限制；
- chrome-devtools-mcp 的 `--autoConnect` 模式正是为此设计：通过浏览器内授权弹窗（每次浏览器会话确认一次）而非 TCP 调试端口建立连接。

本站《让 AI 控制 Edge 浏览器：CDP 远程调试与 chrome-devtools-mcp 配置指南》完整覆盖该方案的配置方法，本文不重复。

## 七、预防清单

- [ ] 浏览器自动化 MCP 指向真实配置目录时，必加 `--ignore-default-chrome-arg=--disable-extensions`
- [ ] 大改自动化配置前，先关闭浏览器并备份 `<Profile>/Preferences` 与数据目录
- [ ] 自动化测试结束后检查是否有残留的 node/chrome 无头进程再关机
- [ ] 定期确认脚本管理器（ScriptCat 等）有本地导出或云同步备份
- [ ] 解压版扩展的源目录路径保持稳定，移动前先记录当前 ID 对应的数据目录

## 八、参考链接

- [chrome-devtools-mcp 仓库与 CLI 选项](https://github.com/ChromeDevTools/chrome-devtools-mcp)
- [Chrome 官方博客：Changes to Remote Debugging Switches（136 起默认目录封锁）](https://developer.chrome.com/blog/remote-debugging-port)
- [微软 Edge 官方文档：DevTools Protocol](https://learn.microsoft.com/en-us/microsoft-edge/devtools/protocol/)
- 本站《让 AI 控制 Edge 浏览器：CDP 远程调试与 chrome-devtools-mcp 配置指南》——autoConnect 与授权弹窗机制
- 本站《hermes-agent Windows 部署与本地模型桥接实战》——另一类 MCP 客户端（Python 侧）的挂载示例
