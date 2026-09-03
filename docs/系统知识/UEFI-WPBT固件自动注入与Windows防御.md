---
status: stable
risk: low
applies_to:
  - Windows 10
  - Windows 11
verified_on: "2026-09-03"
tweak_module:
  - "2"
---

# UEFI WPBT 固件自动注入机制与 Windows 防御

## 1. 什么是 WPBT？

**WPBT（Windows Platform Binary Table，Windows 平台二进制表）** 是微软自 Windows 8 开始引入的一项 ACPI 固件规范。

它的设计初衷是允许主板或整机 OEM 厂商（如联想、华硕、微星、技嘉、华为等）在主板 UEFI 固件中固化一段原生 PE 二进制可执行文件。在每次 Windows 系统冷启动或全新安装后，Windows 会话管理器（`smss.exe`）会在早期启动阶段自动读取该 ACPI 表，将固件中的程序释放至磁盘（通常为 `C:\Windows\system32\wpbbin.exe`）并以最高系统权限（`SYSTEM`）在后台静默执行。

```text
┌─────────────────────────────────────────────────────────────┐
│                 主板 UEFI / BIOS 固件 (ACPI)                │
│             包含 WPBT 表与预固化的 PE 二进制程序            │
└──────────────────────────────┬──────────────────────────────┘
                               │ 开机引导 / Bootloader
                               ▼
┌─────────────────────────────────────────────────────────────┐
│         Windows 会话管理器 (smss.exe / sminit.c)             │
│        探测 ACPI WPBT -> 释放 C:\Windows\system32\wpbbin.exe│
└──────────────────────────────┬──────────────────────────────┘
                               │ 以 SYSTEM 权限静默执行
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 厂商服务全家桶（如 ASUS Armoury Crate / Lenovo LSE 注入）   │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 为什么需要防御与禁用 WPBT？

虽然厂商最初设计该机制是为了自动推送驱动与控制面板，但该机制带来了严重的安全隐患与系统膨胀问题：

1. **供应链安全与 Rootkit 风险**：
   - 固件中的二进制文件一旦存在漏洞（历史上联想 LSE 曾因 WPBT 包含缓冲区溢出与不安全文件覆盖漏洞被 CVE 披露），攻击者可在操作系统层面任意持久化执行恶意代码；
   - 即使重装正版纯净 Windows，固件也会在首次开机时强行再次“下毒”注入程序。
2. **强制捆绑与后台资源占用**：
   - 许多主板厂商通过 WPBT 强行在用户未授权的情况下下载数百兆的 OEM 软件全家桶（如 RGB 各种控制后台、遥测上报服务），增加 DPC 延迟并消耗后台 CPU/内存。
3. **固件更新滞后**：
   - 操作系统与驱动更新非常频繁，但主板 BIOS 很少更新。固件内打包的旧版分发器长期缺乏安全补丁。

---

## 3. 防御与彻底禁用方案

### 方案 A：操作系统级拦截（注册表策略）

微软在 Windows 会话管理器中预留了未公开的防御开关 `DisableWpbtExecution`：

- **注册表路径**：`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager`
- **键名**：`DisableWpbtExecution`
- **类型**：`REG_DWORD`
- **值**：`1`

当设置该值为 `1` 时，Windows 在启动阶段检测到该标志，将直接跳过对 ACPI WPBT 表的解析与执行，从源头杜绝 `wpbbin.exe` 的释放。

```powershell
# 管理员身份执行 PowerShell
New-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -Name 'DisableWpbtExecution' -PropertyType DWord -Value 1 -Force
```

> **注意**：`tweakbyjie` 的 **Part 1 -> 子项 2（系统行为优化）** 已自动集成该注册表项，并支持修改前完整快照与一键还原。

---

### 方案 B：主板 BIOS 固件层关闭（推荐同时配置）

现代主板普遍在 BIOS 设置中提供了关闭 OEM 自动分发软件的开关：

- **华硕 (ASUS)**：进入 BIOS -> `Advanced (高级)` -> `Tool (工具)` -> 找到 **`ASUS Armoury Crate`**，将其从 `Enabled` 修改为 **`Disabled`**。
- **微星 (MSI)**：进入 BIOS -> `Advanced` -> 找到 **`MSI Driver Utility Installer`**，将其设为 **`Disabled`**。
- **技嘉 (Gigabyte)**：进入 BIOS -> `Settings` -> `IO Ports` -> 找到 **`Gigabyte Utilities Downloader Configuration`**，将其设为 **`Disabled`**。
- **联想 (Lenovo)**：进入 BIOS -> `Security` -> 关闭 **`Lenovo Service Engine (LSE)`**。

---

## 4. 验证方式

1. **检查注册表项**：
   ```powershell
   Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager' -Name 'DisableWpbtExecution'
   ```
2. **排查系统目录**：
   检查 `C:\Windows\system32\wpbbin.exe` 是否存在。若已存在，说明此前曾触发过注入，可安全手动删除该残留文件。
3. **使用 NirSoft FirmwareTablesView 查看**：
   运行 `FirmwareTablesView` 查看当前主板是否包含名为 `WPBT` 的 ACPI 表。若包含且系统已启用 `DisableWpbtExecution`，则固件中的二进制代码将被 Windows 严格忽略。
