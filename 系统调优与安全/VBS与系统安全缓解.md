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
| SECURITY-001 | 主菜单 `1` → CPU 安全缓解子项 `2` | 将 `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride` 和 `FeatureSettingsOverrideMask` 写为 `3`，用于调整 Meltdown/Spectre 缓解 | 有 `security-mitigation-backup.json` 原值快照；子项 `3` 可按存在状态和原值恢复。它不是 VBS/HVCI 开关 |
| SECURITY-002 | 主菜单 `10` → 子项 `1` | 将 5 个 Device Guard/VBS 相关注册表值设为 `0`，设置 `hypervisorlaunchtype off`、`isolatedcontext no`、`vsmlaunchtype off`，并禁用 Hyper-V 功能 | 子项 `2` 只删除脚本覆盖并尝试启用 Hyper-V，明确不是原状态精确回滚；注册表和可选功能没有统一原值快照 |
| SECURITY-003 | 主菜单 `9` | 检查 BitLocker 后使用 `SecConfig.efi` 和一次性 BCD 引导项清除 Device Guard EFI 锁定 | 可清理临时 BCD 项，但没有 EFI 变量原始快照或精确恢复；重新启用通常需 Windows 安全设置和重启 |

### 实际注册表与验证边界

选项 10 管理的注册表值包括：

- `HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\Scenarios\HypervisorEnforcedCodeIntegrity\Enabled`
- `HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\EnableVirtualizationBasedSecurity`
- `HKLM\SYSTEM\CurrentControlSet\Control\LSA\LsaCfgFlags`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard\EnableVirtualizationBasedSecurity`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\DeviceGuard\RequirePlatformSecurityFeatures`

选项 10 的 BCD 值会在状态查看中显示，关闭时对 BCD 有回读验证；注册表写入没有同等的专用回读。`HypervisorPresent`、Windows 可选功能状态和 `msinfo32` 结果需要重启后再判断，不能只凭写入成功提示确认运行时状态。

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
- [Microsoft Spectre/Meltdown FAQ](https://support.microsoft.com/en-us/windows/protect-windows-devices-from-spectre-meltdown-35f20c88-a028-3bd9-29bf-3723e872a5e8)

## 与 tweakbyjie 的关系

`tweakbyjie` 中涉及 VBS、Hyper-V、Device Guard 的功能属于高级配置，应独立测试。这类修改影响系统安全模型，不应与普通游戏优化混合执行。项目编号、源码行号、验证和恢复状态见 `youshouldknow/项目导航/tweakbyjie-optimization-mapping.md`。
