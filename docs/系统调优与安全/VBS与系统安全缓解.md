---
applies_to:
  - Windows 10
  - Windows 11
risk: high
tweak_module: [9, 10]
---

# VBS 与系统安全缓解

## VBS 是什么

Virtualization-Based Security（基于虚拟化的安全）利用硬件虚拟化能力隔离关键安全区域。

常见相关功能：

- Memory Integrity（HVCI）
- Credential Guard
- Device Guard
- Hypervisor

## 性能影响

VBS 是否影响性能取决于：

- CPU 架构
- Windows 版本
- 游戏和应用类型
- 驱动支持情况

部分场景可能出现性能下降或延迟变化，但并不是所有设备都会明显受到影响。

## 优化原则

关闭安全功能并不等于一定提升体验。

判断流程：

1. 确认是否需要虚拟化功能。
2. 测试实际游戏或工作负载。
3. 保留恢复方案。

## 与 tweakbyjie 的实际对应关系

`tweakbyjie.ps1` 将安全相关项目拆成三个不同入口，不能把它们都称为“关闭 VBS”：

| 编号 | 脚本入口 | 实际行为 | 恢复边界 |
| --- | --- | --- | --- |
| SECURITY-001 | 主菜单 `1` → 子项 `3`（CPU 安全缓解），应用为内层 `2` | 将 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride` 和 `FeatureSettingsOverrideMask` 写为 `3`，用于调整 Meltdown/Spectre 缓解 | 有 `security-mitigation-backup.json` 原值快照（机器绑定，备份失败阻止写入）；内层子项 `3` 可按存在状态和原值恢复。它不是 VBS/HVCI 开关 |
| SECURITY-002 | 主菜单 `10` → 子项 `1` | 将 5 个 Device Guard/VBS 相关注册表值设为 `0`，设置 `hypervisorlaunchtype off`、`isolatedcontext no`、`vsmlaunchtype off`，并禁用 Hyper-V 功能 | 子项 `1` 关闭前强制快照 `vbs-backup.json`（注册表 5 值 + BCD 3 值 + Windows 可选功能 3 项，机器绑定，备份失败阻止修改）；子项 `3` 按该快照恢复注册表/BCD/功能状态；子项 `2` 只删除脚本覆盖并尝试启用 Hyper-V，明确不是原状态精确回滚；UEFI 锁定不在快照范围内 |
| SECURITY-003 | 主菜单 `9` | 检查 BitLocker 后使用 `SecConfig.efi` 和一次性 BCD 引导项清除 Device Guard EFI 锁定 | 可清理临时 BCD 项，但没有 EFI 变量原始快照或精确恢复；重新启用通常需 Windows 安全设置和重启 |

### 实际注册表与验证边界

选项 10 管理的注册表值包括：

- `HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity\Enabled`
- `HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\EnableVirtualizationBasedSecurity`
- `HKLM\SYSTEM\CurrentControlSet\Control\LSA\LsaCfgFlags`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard\EnableVirtualizationBasedSecurity`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard\RequirePlatformSecurityFeatures`

选项 10 的 BCD 值会在状态查看中显示，关闭时对 BCD 有回读验证；注册表写入没有同等的专用回读。关闭子项执行前会强制生成/校验 `vbs-backup.json` 快照。`HypervisorPresent`、Windows 可选功能状态和 `msinfo32` 结果需要重启后再判断，不能只凭写入成功提示确认运行时状态。

### 风险与前置检查

关闭或覆盖这些安全功能可能影响 Memory Integrity、Credential Guard、BitLocker、WSL2、Docker、虚拟机和企业安全策略。执行前应确认确实不需要 Hyper-V/VBS，并保留 BitLocker 恢复密钥；Device Guard EFI 操作必须确认 BitLocker 保护状态并理解一次性引导流程。

## InSpectre：Spectre/Meltdown 缓解的图形化管理工具

[InSpectre](https://www.grc.com/inspectre.htm) 是 GRC（Gibson Research Corporation）发布的免费工具，可以查看和修改 Windows 的 Spectre/Meltdown CPU 安全缓解状态。

### 作用

- 显示当前系统 Spectre 和 Meltdown 缓解是否启用；
- 显示 CPU 和 Windows 对这些缓解的支持情况；
- 提供图形化开关，比手动修改注册表更直观。

### 与 `tweakbyjie` 选项 1→3 的关系

`tweakbyjie` 的 CPU 安全缓解子项通过写入 `FeatureSettingsOverride=3` 和 `FeatureSettingsOverrideMask=3` 调整缓解状态。InSpectre 修改的是同类底层配置，但两者不应同时使用：

- 同时修改可能产生冲突或覆盖；
- 先用一个工具修改并重启，再检查另一个工具的显示；
- 不要假设两者报告的值始终一致。

### 风险

- 关闭 Spectre/Meltdown 缓解会降低系统安全性，增加侧信道攻击风险；
- 个人游戏设备可能接受此取舍，但不应在公司、生产或高安全需求设备上关闭；
- 某些 Windows 更新可能自动恢复缓解或产生兼容问题；
- 部分杀毒软件将 InSpectre 识别为 PUAT（潜在有害应用），因为它能修改安全设置；
- 修改后必须重启才生效。

### 恢复

- 使用 InSpectre 界面重新打开缓解并重启；
- 或使用 `tweakbyjie` 选项 1→3 子项 3 按快照恢复原始值；
- 也可以通过 Windows 更新或系统还原恢复默认缓解状态。

### 参考

- [GRC InSpectre 官方页面](https://www.grc.com/inspectre.htm)
- Microsoft 官方 Spectre/Meltdown FAQ（support.microsoft.com 35f20c88）已被微软下架，可经 Internet Archive 检索原文；缓解状态查询以 `Get-SpeculationControlSettings` 为准。

## 用注册表在两个模式间切换（社区做法与边界）

除脚本入口外，社区流行一种"手搓一键开关"的做法：把 `DeviceGuard` 相关键值导出成 `.reg`，需要时双击导入切换状态。做法本身可行，但有两个必须澄清的边界。

### 涉及的键值

```text
HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard
├─ EnableVirtualizationBasedSecurity   (REG_DWORD)  1 = 启用 VBS，0 = 关闭
└─ Scenarios\HypervisorEnforcedCodeIntegrity
   └─ Enabled                          (REG_DWORD)  1 = 启用 HVCI，0 = 关闭
```

操作方式：右键 `DeviceGuard` 项 → 导出为 `xxx.reg`；用记事本把两处 `dword:00000001` 改成 `dword:00000000` 另存为另一个文件，即得到一对"开/关"脚本。系统被精简、缺少上述子项时，需按 `DeviceGuard` → `Scenarios` → `HypervisorEnforcedCodeIntegrity` 的层级手工新建。

### 边界一：改完必须重启，不能"双击即生效"

`.reg` 导入只是写了注册表值。VBS 与 HVCI 运行在 **VTL1（虚拟信任级别 1）**，其加载与卸载发生在系统引导阶段，由 hypervisor 建立隔离环境时完成。**运行中的系统无法通过写注册表即时改变已加载的 VTL1 环境**：

- 从关到开：需重启，下次引导时才建立 VBS/HVCI 环境；
- 从开到关：同样需重启，否则 hypervisor 与 HVCI 仍在运行。

声称"双击 .reg 后不用重启就已切换"的说法与机制不符。判断实际状态应看重启后的 `msinfo32`（"基于虚拟化的安全性"一行）或安全中心的"内核隔离"页，而不是注册表数值。脚本的正规做法是本库 VBS 专题给出的路径：写值 + BCD + 重启后回读验证。

### 边界二：HVCI 开启对驱动签名有硬性要求

开启 HVCI 会强制所有内核驱动满足兼容性与签名要求。若系统里有老旧或不兼容的驱动（部分外设驱动、超频/降压工具驱动、老显卡驱动），开启后**可能直接无法引导或反复蓝屏**。开启前应确认驱动来源，并准备系统还原点。此外 VBS/HVCI 依赖 CPU 硬件虚拟化（Intel VT-x / AMD-V）与 UEFI 安全启动，BIOS 未开启虚拟化时仅改注册表不会生效。

### 与反作弊的关系

部分竞技游戏的反作弊对 VBS/HVCI 状态有明确要求（例如 Riot Vanguard 在 Windows 11 上的要求与部分国服游戏的要求方向相反），跨服游玩时可能需要切换状态。若按上面的方式在两套状态间反复导入 `.reg`：

- **必须重启后才真正切换**，因此"同一台机器上两个服来回切"实际是"每次都要重启"；
- 不要在游戏运行期间导入 `.reg` 期望即时改变环境——那既不会生效，也不会被反作弊识别为"已切换"，只会在下次重启后突然改变环境；
- 任何绕过或伪造安全环境状态的操作都有账号封禁风险，本库不提供此类指引。

## 与 tweakbyjie 的关系

`tweakbyjie` 中涉及 VBS、Hyper-V、Device Guard 的功能属于高级配置，应独立测试。这类修改影响系统安全模型，不应与普通游戏优化混合执行。项目编号、源码行号、验证和恢复状态见 `youshouldknow/项目导航/tweakbyjie-optimization-mapping.md`。

## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-29 重核：对照 HEAD b905950 的 `Modules/Registry.ps1`、`Modules/Backup.SecurityMitigation.ps1`、`Modules/Virtualization.ps1`、`Modules/Backup.Vbs.ps1` 逐条复核）。

| 声明 | 核查结果 |
| --- | --- |
| SECURITY-001 写入 FeatureSettingsOverride/Mask=3，有 security-mitigation-backup.json 快照且子项可恢复 | ✅ 属实（2026-08-29 重核修正入口编号）：现为 `Modules/Registry.ps1` 主菜单 `1` → 子项 `3`（内层 `2` 应用、内层 `3` 按 `Restore-SecurityMitigationBackup` 恢复）+ `Modules/Backup.SecurityMitigation.ps1`；原文档写“子项 2/子项 3”为旧编号，正文已修正 |
| SECURITY-002 将 5 个 Device Guard/VBS 注册表值设为 0，BCD 设 hypervisorlaunchtype off / isolatedcontext no / vsmlaunchtype off 并禁用 Hyper-V | ✅ 属实：`Modules/Backup.Vbs.ps1` 的 vbsRegistryValues（5 值）与 `Modules/Virtualization.ps1` 的 Invoke-VbsModule 一致（2026-08-29 重核） |
| SECURITY-002 的 BCD 有回读验证、注册表无专用回读 | ✅ 属实：`Verify-BcdValue` 存在，`Set-RegDword` 写入后无对应 Verify（2026-08-29 重核） |
| SECURITY-002 注册表和可选功能没有统一原值快照 | ❌ 勘误（2026-08-29 重核）：子项 `1` 关闭前强制 `Ensure-VbsBackup`，`vbs-backup.json` 保存注册表 5 值 + BCD 3 值 + 可选功能 3 项（机器绑定）；子项 `3` 按快照恢复；仅 UEFI 锁定和子项 `2` 的删除式路径不属于快照恢复。正文已修正 |
| SECURITY-003 先检查 BitLocker 再用 SecConfig.efi + 一次性 BCD 清除 EFI 锁定 | ✅ 属实：Invoke-DeviceGuardModule 含 BitLocker 预检查与拒绝逻辑（2026-08-29 重核） |
| InSpectre 为 GRC 发布的 Spectre/Meltdown 图形化管理工具 | ✅ 属实：GRC 官方页面存在（该站对 CI 网络有连接重置，浏览器可访问）（2026-08-29 重核：维持原判，属外部事实，未重新在线验证） |
| 部分杀毒软件将 InSpectre 识别为 PUAT | ⚠️ 依赖社区反馈，未逐一验证杀软厂商官方声明（2026-08-29 重核：维持原判） |
| VBS/HVCI 的注册表切换路径为 `DeviceGuard\EnableVirtualizationBasedSecurity` 与 `DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity\Enabled` | ✅ 属实：`Modules/Backup.Vbs.ps1` 的 `vbsRegistryValues` 已包含这两个值（另含 LSA 与策略值），与社区 `.reg` 做法的键值一致 |
| 写注册表后可即时切换 VBS/HVCI，无需重启 | ❌ 错误说法：VBS/HVCI 运行于 VTL1，加载与卸载在系统引导阶段完成；本库要求重启后以 `msinfo32` / 安全中心 / `HypervisorPresent` 复核，而非仅看注册表数值 |
| 开启 HVCI 可能因不兼容驱动导致无法引导或蓝屏 | ✅ 属实：HVCI 强制内核驱动满足兼容性与签名要求，微软与社区文档均提示需在部署前验证驱动 |
| 跨服反作弊对 VBS/HVCI 的要求可能方向相反 | ⚠️ 部分核实：Riot Vanguard 在 Windows 11 上要求 VBS/HVCI 为社区广泛记录的现象；具体到"国服要求关闭"仅为视频口述，本库未取得官方公告佐证，正文已按"不提供绕过指引"处理 |
