---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: [1]
verified_on: "2026-09-05"
---

# WPBT 固件注入机制与禁用

## WPBT 是什么

**Windows Platform Binary Table（WPBT）** 是 ACPI 固件表的一种：OEM/主板厂商可以把一个可执行程序（`.exe`）写进 UEFI 固件，Windows 在**每次启动的早期阶段**把它释放为 `wpbbin.exe` 并执行。设计初衷是合法的 OEM 场景（防盗追踪软件、厂商驱动预装、企业设备管理）。

问题在于这条链路的信任模型：**注入程序在操作系统安全体系建立之前运行**，且由固件而非 Windows 决定内容。安全研究的共识是——在没有配置 WDAC（Windows Defender Application Control）的家用设备上，用户对 WPBT 注入内容几乎没有可见性和控制手段，`wpbbin.exe` 也因此被持久化机制研究列为固件层驻留途径之一。

## 禁用原理与注册表实现

Windows 内核在解析 ACPI 表时检查 `Session Manager` 下的开关值，置 `1` 后本次及后续启动**不再执行** WPBT 提供的二进制：

```ini
[HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager]
"DisableWpbtExecution"=dword:00000001
```

- 该值写入后**重启生效**；删除该值即可恢复默认行为（固件下次启动仍可注入）；
- 这是微软官方在 DFCI（设备固件配置接口）之外提供给系统的 WPBT 执行总开关，Intune 管理的 DFCI 策略也能在固件层达到同样目的。

## 与 tweakbyjie 的实际对应关系

- 执行位置：主菜单 `1`（核心优化，系统行为组），写入上方注册表值；
- 来源：该调优项吸收自 [Atom-Tool-Box](https://github.com/ProjectAtomOS/Atom-Tool-Box) 的高价值安全项，是 tweakbyjie 上游看门机制跟踪的吸收来源之一；
- 备份与恢复：已纳入 Part 1 统一注册表快照（`registry-backup.json`，见 `Modules/Backup.Registry.ps1`），主菜单 `1→4` 可按快照恢复原值。

## 影响边界

1. **会失效的功能**：依赖 WPBT 的 OEM 防盗/追踪组件、部分厂商预装工具将不再随启动注入执行；
2. **不受影响的功能**：BIOS/UEFI 固件更新、BitLocker、Windows 更新与安全组件均不依赖 WPBT 执行路径；
3. **边界声明**：禁用 WPBT 只阻断"固件→Windows"这一条注入路径，不能替代固件升级与 Secure Boot；已驻留系统内的其他持久化机制与本设置无关。

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| `DisableWpbtExecution=1` 可阻止 WPBT 二进制执行 | ✅ 属实：与 persistence-info 对 `wpbbin.exe` 的持久化研究及社区工具 dropWPBT 的实现描述一致 |
| WPBT 由固件每次启动注入、先于系统安全体系 | ✅ 属实：微软 Firmware WEG 与 Intune DFCI 文档均按"每次启动由 OEM 提供可执行体"描述 |
| 禁用不影响 BIOS 更新 | ⚠️ 社区反馈支持（Acer 等论坛无固件更新故障报告），微软未给出官方承诺；保守做法是固件更新前临时恢复默认 |

## 参考

- [微软 Firmware Windows Engineering Guide（WPBT 所属 ACPI 表说明）](https://learn.microsoft.com/en-us/windows-hardware/drivers/bringup/firmware-weg)
- [微软 Intune DFCI 设置参考（WPBT 官方功能描述与固件层管理）](https://learn.microsoft.com/en-us/intune/device-configuration/templates/ref-dfci-settings-windows)
- [persistence-info：wpbbin.exe 持久化机制记录](https://persistence-info.github.io/Data/wpbbin.html)
- [Jamesits/dropWPBT：非破坏性移除 WPBT 的开源工具](https://github.com/Jamesits/dropWPBT)
