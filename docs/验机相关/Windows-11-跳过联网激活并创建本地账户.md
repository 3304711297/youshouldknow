---
applies_to:
  - Windows 11
risk: medium
tweak_module: []
---

# Windows 11 跳过联网激活并创建本地账户

> **分类**：验机相关 · 验机教程
>
> **适用场景**：新机开箱验机 / 重装系统后，在 Windows 11 OOBE（初始设置）阶段不想强制联网登录微软账户，希望直接创建本地账户。
>
> 本文技术内容已对照微软官方公告及多家科技媒体交叉验证。

---

## 背景

微软自 2025 年 3 月 28 日起，在以下版本中**移除了 `bypassnro.cmd` 脚本**：

- Dev 频道 Build **26200.5516**
- Beta 频道 Build **26120.3653**（24H2，经由 KB5053658）

微软官方给出的理由是「以增强 Windows 11 的安全性和用户体验」，即要求所有用户在初始化时保持联网并登录微软账户。此后在 OOBE 阶段用 `Shift+F10` 输入 `OOBE\BYPASSNRO` 会直接报错。

不过脚本虽然被移除，**注册表层面的 `BypassNRO` 开关目前仍然有效**，以下是几种可行的替代方案。

---

## 方案一：命令行添加注册表值（推荐）

1. 在 OOBE 阶段按 `Shift + F10` 调出命令提示符；
2. 输入以下命令（**不区分大小写**）：

   ```bat
   reg add HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE /v BypassNRO /t REG_DWORD /d 1 /f
   ```

3. 重启计算机：

   ```bat
   shutdown /r /t 0
   ```

4. 重启后回到 OOBE，联网页面会出现「我没有 Internet 连接」/「以后再说」选项，点击即可进入本地账户创建流程。

## 方案二：注册表编辑器图形界面操作

如果不习惯命令行，也可以：

1. 在 OOBE 阶段按 `Shift + F10`，输入 `regedit` 打开注册表编辑器；
2. 定位到：

   ```text
   HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE
   ```

3. 新建 **32 位 DWORD 值**，命名为 `BypassNRO`，数值数据设为 `1`（16 进制）；
4. 保存后关闭，执行 `shutdown /r /t 0` 重启。

## 方案三：调用隐藏的本地账户创建界面

旧命令 `start ms-cxh:localonly` 曾可直接跳过联网激活，但在 Build **26220.6772** / **26120.6772** 中已被移除。新的替代方法：

1. 在 OOBE 阶段按 `Shift + F10` 打开命令提示符；
2. 按 `Ctrl + Shift + J` 呼出脚本控制台；
3. 输入以下命令（**区分大小写**）：

   ```js
   WinJS.Application.restart('ms-cxh://LOCALONLY')
   ```

4. 系统会重启 Cloud Experience Host 并进入隐藏的本地账户创建界面。

---

## 备选思路（补充）

除上述方案外，社区常用的其他方法还包括：

- **Rufus 制作安装盘**：在写入镜像时勾选「移除 Microsoft 账户登录要求」，直接在安装介质层面禁用强制联网，稳定性最好；
- **拔网线 / 不连 Wi-Fi**：部分版本在无网络时会自动提供离线账户入口（新版本已逐步封堵）。

> ⚠️ **注意**：微软正在逐个版本封堵上述绕过方法，本文方案存在随时失效的可能。发布本文时（2026-08）注册表方案与 `WinJS.Application.restart` 方案均已通过多信源交叉验证属实，但使用前请留意你所安装的系统版本。

---

## 事实核查记录

本文关键技术声明已对照以下独立信源核实：

| 声明 | 核查结果 |
| --- | --- |
| 微软在 Build 26200.5516 / 26120.3653 中移除 bypassnro.cmd | ✅ 属实（微软官方公告 2025-03-28） |
| 注册表 `BypassNRO` 值仍被系统读取 | ✅ 属实（Bleeping Computer、ElevenForum 实测） |
| `start ms-cxh:localonly` 已在后续版本移除 | ✅ 属实（Winhance GitHub Issue #326） |
| `Ctrl+Shift+J` + `WinJS.Application.restart('ms-cxh://LOCALONLY')` 可用 | ✅ 属实（ElevenForum、Reddit 社区验证） |

**参考来源：**

- [Windows Insider Blog — Announcing Build 26200.5516 (Dev Channel)](https://blogs.windows.com/windows-insider/2025/03/28/announcing-windows-11-insider-preview-build-26200-5516-dev-channel/)
- [Tom's Hardware — Microsoft eliminates workaround that circumvents Microsoft account requirement](https://www.tomshardware.com/software/windows/microsoft-eliminates-workaround-that-circumvents-microsoft-account-requirement-during-windows-11-installation)
- [Bleeping Computer — Microsoft's killing script used to avoid Microsoft account in Windows 11](https://www.bleepingcomputer.com/news/microsoft/microsofts-killing-script-used-to-avoid-microsoft-account-in-windows-11/)
- [ElevenForum — KB5053658 Build 26120.3653 讨论帖](https://www.elevenforum.com/t/kb5053658-windows-11-insider-beta-build-26120-3653-24h2-march-28.34704/page-2)
- [ElevenForum — New Local Account Method 讨论帖](https://www.elevenforum.com/t/new-local-account-method-access-unused-setup-screen-s-mode-supported.29973/page-2)
