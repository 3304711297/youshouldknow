---
applies_to:
  - Windows 10
  - Windows 11
  - EasyCLIProxyAPI
  - CLIProxyAPI
risk: low
status: stable
tweak_module: []
verified_on: 2026-09-07
---

# EasyCLIProxyAPI 便携版更新与单实例锁排障指南

> 本文目标：深入复盘 EasyCLIProxyAPI（官方核心 CLIProxyAPI）在 Windows 平台下的便携版就地更新机制、目录命名逻辑，以及启动阶段常见的本地代理握手超时、命名互斥体单实例锁碰撞与端口占用的底层根因与排错流程。
>
> 实测基准：EasyCLIProxyAPI v0.2.75 / 内核 v7.2.152+ / Windows 11 / 本地代理 127.0.0.1:3067 / 本地网关端口 18080。

---

## 一、 便携版更新与文件替换机制

EasyCLIProxyAPI 在 Windows 下通常以便携包（Portable）形式部署。在客户端内点击「检查更新」并执行升级时，系统采用**外挂辅助进程就地覆盖（In-Place Replacement）**机制，其生命周期如下：

### 1. 更新阶段划分
1. **下载与校验**：客户端将新版本压缩包下载至 `%LOCALAPPDATA%\Temp\EasyCLIProxyAPI-update-vX.Y.Z-PID-TIMESTAMP\` 临时工作目录。
2. **提取与暂存**：解压新版 GUI 应用程序 `EasyCLIProxyAPI.exe`、便携清单 `portable-app.json`、内核版本描述 `core-version.txt` 以及内核压缩包 `CLIProxyAPI_X.Y.Z_windows_amd64.zip` 到临时目录的 `staging/`。
3. **拉起更新助手并退出主程序**：主程序将当前自身的 exe 复制为 `EasyCLIProxyAPI-updater.exe`，以 `--portable-update-helper` 参数启动该辅助进程，主程序随后调用 `app.exit(0)` 退出以释放文件占用锁。
4. **备份旧版与原子替换**：辅助进程等待旧主进程完全退出后，将旧文件重命名为 `.update-backup`，并将新文件移动覆盖至应用目录。
5. **拉起新版验证与提交**：启动新版主程序并传入 `--portable-update-ack` 参数；新版若在 60 秒内启动就绪并生成确认信号，辅助进程便清理备份文件并退出；若超时则触发自动回滚。

### 2. 为什么安装目录名不会自动改变？
很多用户在升级后发现，父级文件夹名称仍然显示旧版本（例如 `D:\EasyCLIProxyAPI-v0.2.71-Windows-amd64`）：
* **原因**：便携式软件无法在自身运行时（或由子进程）重命名正在作为工作目录的父级文件夹；
* **本质**：版本更新的核心是二进制文件与内核包（`core-version.txt` 和 `portable-app.json` 已更新为最新版本）。父目录名属于静态路径，不影响软件实际版本与运行状态，无需手动强行重命名（否则会导致桌面快捷方式或配置路径失效）。

---

## 二、 启动报错三大根因与排查链路

更新后重新拉起程序时，若弹出系统报错或日志出现 Warning/Error，主要由以下三类时序与网络因素引发：

### 1. 本地代理握手瞬间拒绝（TLS Handshake / Connectex 403）
* **错误日志表象**（位于 `auth/logs/main.log`）：
  ```text
  [warn] failed to refresh antigravity version... dial tcp 127.0.0.1:3067: connectex: No connection could be made because the target machine actively refused it.
  [warn] credential refresh failed for antigravity (antigravity-xxx@gmail.com.json): dial tcp 127.0.0.1:3067: connectex: ... target machine actively refused it.
  ```
* **根因剖析**：
  在 `config.toml` 中配置了 `proxy-url = "http://127.0.0.1:3067"`。当 EasyCLIProxyAPI 重启初始化内核时，会毫秒级并发拉取 Google Antigravity Hub 版本清单并执行 OAuth 凭据刷新（Refresh Token）。如果此时系统本地代理客户端（如 Clash / v2ray / sing-box）恰好处于重启、TUN 切换或连接数激增状态，目标端口直接拒绝握手，导致启动探活直接抛出错误。
* **解决与处置**：
  检查本地代理端口（如 `3067`）是否保持正常监听。只要此前登录的 Access Token 尚未过期，内核具备保留旧有效凭据的容错机制（`retaining active credential as access token is unexpired`），网络恢复后将在下个周期自动重试。

### 2. 命名互斥体单实例锁碰撞（Instance Lock Conflict）
* **错误弹窗表象**：
  `"当前 EasyCLIProxyAPI 目录已经有一个软件实例在运行"`
* **机制与根因**：
  为了避免同一个数据目录下的 SQLite 数据库（`usage.db`）被并发读写损坏，客户端在启动初期通过 Win32 API 创建全局互斥体：
  `CreateMutexW(NULL, FALSE, "Local\\EasyCLIProxyAPI-instance-{path_sha256}")`
  若更新完成拉起新程序时，旧版主进程的某些后台线程（如 WebView2 渲染管道或托盘驻留）尚未完全释放句柄，导致操作系统仍持有互斥体，新进程触发 `ERROR_ALREADY_EXISTS` 从而直接退出。
* **解决步骤**：
  在任务管理器中彻底结束所有遗留的 `EasyCLIProxyAPI.exe` 进程，或在 PowerShell 中执行命令清理后重新拉起：
  ```powershell
  Get-Process -Name "EasyCLIProxyAPI" -ErrorAction SilentlyContinue | Stop-Process -Force
  ```

### 3. 端口占用与内核接管冲突（Port 18080 Already in Use）
* **错误弹窗表象**：
  `"端口 18080 已被其他程序占用，请更换端口后重试"`
* **机制与根因**：
  内核 `cli-proxy-api.exe` 是常驻运行的服务。EasyCLIProxyAPI 在启动时具备进程接管逻辑（`adopt_existing_core_processes`）。但如果在更新换代时，旧内核未能正确响应父进程退出信号，且其 PID 未被及时识别，新程序试图重新在 18080 端口启动子内核，就会发生 Socket 绑定碰撞。
* **排查方法**：
  执行命令查明占用 18080 端口的真实 PID：
  ```bash
  netstat -ano | grep 18080
  ```
  若占用者是孤儿 `cli-proxy-api.exe`，直接结束该进程后再通过 GUI 端点击「启动内核」即可平稳恢复。

---

## 三、 上游接口异常与冷却期机制

更新后如果请求特定模型返回 `500 Internal Server Error` 或 `503 Service Unavailable`：
1. **单账号配额冷却（Cooldown）**：
   若日志显示 `candidate(s) for model are in cooldown: [..., reason=quota, remaining=104h]`，代表该 Google 账号触发了官方速率限制（RPM/TPD），被网关隔离放入冷却池，期间网关将全量调度到备用账号。
2. **上游接口断连与 EOF**：
   Google `daily-cloudcode-pa.googleapis.com` 在特定网络环境下偶发返回 `streamGenerateContent: EOF` 或 TLS 握手超时。网关配置了 `request-retry: 2` 和双账号平级轮询池时，可有效平抑单次瞬时网络抖动。
