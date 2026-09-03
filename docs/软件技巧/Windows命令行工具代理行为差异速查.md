---
applies_to:
  - Windows 10/11
  - PowerShell 5.1 / 7
  - Git Bash（MSYS2）
  - git / curl / npm / pip / uv / Node.js 使用者
risk: low
tweak_module: []
---

# Windows 命令行工具的代理行为差异速查

> 本文目标：解释"浏览器能上网、命令行却下载失败"这类故障的真正根因——**Windows 系统代理只对一部分命令行工具生效**——并给出各主流工具的代理判定表、典型误导性故障案例（尤其是"半成功"假象）与一分钟的判定流程。
>
> 实测环境：Windows 11 / 本地 HTTP 代理（127.0.0.1 回环端口）/ git 2.55 / Node 24 / Python 3.14 + uv / PowerShell 5.1 与 7 并存。表中每一行都经实机验证或对照官方文档核实。

## 一、核心认知：Windows 上有"两套代理"

1. **系统代理（WinINET/WinHTTP）**：设置 → 网络与 Internet → 代理里配置的那套，浏览器和部分微软系工具读它。
2. **环境变量代理**：`HTTP_PROXY` / `HTTPS_PROXY`（及小写形式），Unix 传统，绝大多数跨平台命令行工具**只认这一套**。

两边不互通。设置了系统代理的工具族不会惠及第二族，反之亦然——这就是"同一个终端里，一条命令成功、下一条命令连接重置"的根源。

## 二、主流工具代理行为速查表

| 工具 | 默认读系统代理？ | 读环境变量？ | 补充说明 |
| --- | --- | --- | --- |
| PowerShell 5.1 / 7 的 `Invoke-WebRequest` / `Invoke-RestMethod` | ✅ 是 | ❌ | 需要 `-Proxy` 参数或系统代理；PS7 基于 HttpClient，同走系统代理 |
| 浏览器 / Edge | ✅ 是 | ❌ | — |
| `git` | ❌ | ✅ `http_proxy`/`https_proxy` | 或 `git config --global http.proxy <地址>`（可按域名限定作用范围） |
| `curl`（含 Windows 内置版） | ❌ | ✅ `http_proxy`/`https_proxy`/`all_proxy` | 临时指定用 `-x <代理地址>` |
| `npm` | ❌ | ✅ | 另有 `.npmrc` 的 `proxy`/`https-proxy` 配置项 |
| `pip` | ❌ | ✅ | 亦有 `pip.ini` 配置 |
| `uv` | ❌ | ✅ `HTTP_PROXY`/`HTTPS_PROXY` | 与 pip 同风格 |
| `gh`（GitHub CLI） | ❌ | ✅ `HTTPS_PROXY` | — |
| Node.js 自带 `fetch`（undici） | ❌ | ❌ **两者都不读** | 必须显式用 undici 的 `ProxyAgent`，或改用子进程 curl |
| `winget` | ⚠️ 有代理设置项 | — | 新版支持 `settings` 中配置代理，行为随版本变化，用前单独核实 |

**判定口诀：PowerShell 系走系统代理，跨平台工具族走环境变量，Node fetch 谁都不走。**

## 三、典型误导性故障：安装器的"半成功"

混合型安装器（同一脚本内既用 PowerShell 下载、又调用 git/uv）在只配了系统代理的机器上会出现这样的日志序列：

```text
[OK] xxx.zip 下载成功                    ← PowerShell 通道，走了系统代理
fatal: unable to access 'https://github.com/...': Connection was reset   ← git 克隆失败
[!] 下载中断残留 xxx.incomplete-<时间戳>  ← uv 下载 Python 失败
[!] 回退到 ZIP 安装……
[X] 安装失败：托管 Python 不可用
```

ZIP 成功会造成"网络没问题"的错觉，真正的故障被推到后半段。**看到 `Connection was reset` + `incomplete` 残留的组合，先怀疑环境变量代理未设置**，而不是反复重试或换安装源。

修复：在启动安装器的同一 shell 会话里导出环境变量（子进程才会继承）：

```powershell
$env:HTTP_PROXY = "http://127.0.0.1:<本地代理端口>"
$env:HTTPS_PROXY = "http://127.0.0.1:<本地代理端口>"
```

Git Bash 下则是 `export HTTPS_PROXY=...`。注意**每次新开 shell 都要重设**，或写入 profile。

## 四、Git Bash（MSYS2）的两个额外坑

### 坑一：斜杠参数被路径改写吞掉

MSYS2 会对以 `/` 开头的参数做 POSIX→Windows 路径转换，导致部分 Windows 原生命令的开关被吞或被改写。实测案例：

```bash
reg add "HKCU\SOFTWARE\Policies\Microsoft\Edge" /v SomeValue /t REG_DWORD /d 1 /f
# 报错：无效语法 —— /v /t /d /f 被 MSYS 改写
```

解法（任选其一）：

```bash
# 方案 A：改用 PowerShell 执行注册表操作（推荐，完全绕开转换）
powershell -NoProfile -Command "Set-ItemProperty -Path 'HKCU:\SOFTWARE\Policies\Microsoft\Edge' -Name SomeValue -Value 1 -Type DWord"

# 方案 B：双斜杠阻止转换
reg add "HKCU\SOFTWARE\Policies\Microsoft\Edge" //v SomeValue //t REG_DWORD //d 1 //f
```

### 坑二：内联 PowerShell 的 `$` 变量被 bash 展开

在 Git Bash 里写 `powershell -Command "... $ws ..."`，`$ws` 会先被 bash 展开成空串。复杂 PowerShell 逻辑应写成临时 `.ps1` 文件再 `-File` 执行；临时脚本若含中文，必须是**带 BOM 的 UTF-8**（PS 5.1 会把无 BOM 的 UTF-8 按 ANSI 读，中文乱码甚至破坏语法），字符串内不要使用中文弯引号（PS 会把 `“ ”` 当字符串定界符，导致提前截断）。

## 五、一分钟判定流程

遇到"命令行下载/克隆失败"时按序执行：

1. **确认代理本身活着**：`curl -sI -x http://127.0.0.1:<端口> https://目标站` 返回 200 说明代理可用，问题在工具配置；
2. **分清工具属于哪一族**（对照第二节表格）；
3. **环境变量族**：当前 shell 里 `echo $HTTPS_PROXY`（PowerShell：`$env:HTTPS_PROXY`）为空即补上；
4. **设置后必须验证子进程真的继承了**：在同一会话内重跑失败命令，不要新开终端；
5. **仍失败**：区分"代理端口拒绝"（代理没起）与"Connection reset"（代理节点故障，先重试再换节点），不要在工具层面反复折腾。

## 六、事实核查与实测记录

- "git/uv/npm/curl 不读 Windows 系统代理、PowerShell IWR 读"：✅ 实测（本机系统代理 + 环境变量对照实验，安装器日志与手工命令双重验证）。
- "Node 内置 fetch（undici）不读代理环境变量"：✅ 实测（Node 24，外网请求直连失败、经 curl 子进程成功）。
- "MSYS2 路径转换吞掉 `reg add` 斜杠参数"：✅ 实测（报错"无效语法"，改 PowerShell 后成功）。
- "PS 5.1 无 BOM UTF-8 中文乱码、弯引号当定界符"：✅ 实测（同一带 BOM 文件在 5.1 与 7.6.5 对照解析，5.1 报错而 7 正常；弯引号截断行为两版本一致成立）。
- 工具版本迭代可能改变默认行为，使用时以 `--version` 对应的最新文档为准。

## 七、参考链接

- [Git 文档：git-config 的 http.proxy](https://git-scm.com/docs/git-config#Documentation/git-config.txt-httpproxy)
- [curl 官方手册：--proxy 与环境变量支持](https://curl.se/docs/manpage.html)
- [undici 官方文档：ProxyAgent 支持](https://undici.nodejs.org/#/docs/api/ProxyAgent)
- [Microsoft Learn：about_Invoke-WebRequest（PowerShell 7）](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/invoke-webrequest)
