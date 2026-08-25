# tweakbyjie 全量逐项执行参考


> 已与 `tweakbyjie` 模块化结构同步：`Modules/Menu.ps1` 只负责菜单调度，执行逻辑位于各业务模块（`Registry/Bcd/Defender/Mpo/Nvme/Power/Service/Virtualization.ps1`）与 `Modules/Common.ps1`（通用写入/验证）、`Modules/Backup.*.ps1`（备份闭环）；正文表格中的 `:NNN` 为模块化前单文件源码的历史行号快照（见文末边界说明），现行定位以 `Modules/文件.ps1` 和函数名为准。详见 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md`。

> **用途**：把 `tweakbyjie/tweakbyjie.ps1` 当前实际执行项转换为可核对的参考手册。
>
> **源码基线**：`tweakbyjie.ps1` 当前 `main` 分支源码；行号随源码变化，更新脚本后必须重新核对。
>
> **重要边界**：本文描述脚本实际行为，不等于推荐所有用户执行。配置层写入成功不等于运行时收益，也不等于拥有精确恢复能力。

## 统一字段

每个项目按以下字段核对：

- **入口**：主菜单/子菜单；
- **源码**：执行、验证、备份和恢复位置；
- **目标对象**：注册表、BCD、服务、电源计划、可选功能、EFI 文件、任务或 Appx；
- **原始状态**：脚本是否保存存在性、类型、值、运行状态和依赖；
- **目标状态**：具体值、类型、单位和编码；
- **验证**：配置层回读、运行时验证、是否需要重启；
- **恢复**：入口、备份文件、精确程度和限制；
- **风险**：兼容性、依赖功能和不可逆边界。

## 总览状态

| 分类 | 编号范围 | 当前执行闭环 |
|---|---|---|
| CPU/核心系统 | CPU-001 至 CPU-005、CORE-001 至 CORE-016 | 多数写入；仅少数回读；普通项通常无原值快照 |
| GPU/显示 | GPU-001 至 GPU-002 | HAGS 有回读无快照；MPO 有四值快照和恢复 |
| Memory/Storage | MEMORY-001/002、STORAGE-001 至 004 | Prefetch/压缩/TRIM 回读但无完整原值恢复；NVMe 有专用快照 |
| Security | SECURITY-001 至 003 | CPU 缓解有快照；VBS/EFI 非精确回滚 |
| Service | SERVICE-001/002 | Part 6 有 37 项快照；Part 5 策略值有快照（`5→2` 恢复），服务/任务/Appx 无精确回滚 |
| Boot | BOOT-001 至 006 | BCD-001/002 有快照；测试模式/EFI/VBS 部分不可精确恢复 |
| Power | POWER-001 | `power-backup.pow` 恢复最初电源计划 |
| NVMe | STORAGE-004 | `nvme-backup.json`，失败可回滚；运行时验证由 `Modules/Backup.Nvme.ps1` 的 `Test-NativeNvme*` 提供 |
| Registry deletion | REGISTRY-001 | Part 5/独立 Defender 删除高风险、部分不可逆 |

## 一、CPU-001：Win32PrioritySeparation

- **入口**：主菜单 `1` → 核心游戏优化 `1`。
- **源码**：写入 `Modules/Registry.ps1` + `Modules/Common.ps1/Set-RegDword`；验证 `Verify-RegDword`（Modules/Common.ps1）；写入函数 `Set-RegDword`（`Modules/Common.ps1`）；无专用备份/恢复函数。
- **目标对象**：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl`。
- **值**：`Win32PrioritySeparation`，`REG_DWORD`，目标 `38 Dec = 0x26`。
- **传统位解释**：`32/16` 表示短/长量子，`8/4` 表示固定/可变量子，`2/1/0` 表示高/中/无前台提升。`38=32+4+2`；`24=16+8+0` 仅是后台参考值，不是脚本模式。
- **原始状态**：当前脚本不保存存在性、类型和值；修改前需手工读取。
- **验证**：`Verify-RegDword` 回读 `38`，只证明配置层；需要重启并做 FPS、1% Low、帧时间、输入延迟、后台任务 A/B。
- **恢复**：手工写回原类型和值；原本不存在则删除新增值。不能把 `0x26` 或 `0x18` 当通用恢复值。
- **风险**：前台响应、后台任务份额和不同 Windows 版本行为可能变化，不保证性能收益。

## 二、CPU-002 至 CPU-005：MMCSS 与 Games

### CPU-002 `Multimedia\SystemProfile`

- **入口/源码**：主菜单 `1→1`；`Modules/Registry.ps1`（`Invoke-RegistryModule`）。
- **目标对象**：`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile`。
- **实际子项**：`SystemResponsiveness=10`、`NetworkThrottlingIndex=0xFFFFFFFF`，以及 `Tasks\Games` 七项；它们应分别核对，不应把路径当成单一值。
- **验证/恢复**：除 CPU-001/HAGS 外没有统一回读；无统一原值备份；必须人工记录每个值的存在性、类型和值。

### CPU-003 `SystemResponsiveness`

- `REG_DWORD=10`，源码 `:794`。
- 影响 MMCSS 后台资源分配策略，不是固定 CPU 百分比。
- 当前无专用回读、备份和恢复；需手工恢复原值并结合后台编译/同步/游戏 A/B。

### CPU-004 `NetworkThrottlingIndex`

- `REG_DWORD=0xFFFFFFFF`，源码 `:793`。
- 目标是尝试关闭/绕过多媒体网络节流，不等于提升带宽或保证低延迟。
- 当前无专用回读、备份和恢复；需记录原值并测试 RTT、抖动、丢包和 CPU 占用。

### CPU-005 `Tasks\Games`

路径：`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games`。

| 值名 | 类型 | 脚本目标 | 当前验证/恢复 |
|---|---|---:|---|
| `Affinity` | DWORD | `0` | 无逐项回读；无快照 |
| `Background Only` | SZ | `False` | 无逐项回读；无快照 |
| `Clock Rate` | DWORD | `10000` | MMCSS 参数，不是 GPU 硬件时钟；无回读 |
| `GPU Priority` | DWORD | `8` | Games 任务类别参数，不是显卡超频；无回读 |
| `Priority` | DWORD | `6` | 无回读；无快照 |
| `Scheduling Category` | SZ | `High` | 无回读；无快照 |
| `SFIO Priority` | SZ | `High` | 无回读；无快照 |

## 三、CORE-001 至 CORE-013：核心菜单 1

共同入口：主菜单 `1` → 核心游戏优化 `1` 或 `2`。除明确列出的项目外，普通 `Set-Reg*` 写入没有统一原值备份。

### CORE-001 至 CORE-010：核心游戏子项

| 编号 | 路径/对象 | 值/命令 | 类型/目标 | 源码 | 验证/恢复 |
|---|---|---|---|---|---|
| CORE-001 | `HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR` | `AppCaptureEnabled` | DWORD `0` | `:754` | 无专用回读/快照 |
| CORE-002 | `HKCU\System\GameConfigStore` | `GameDVR_Enabled` | DWORD `0` | `:755` | 无专用回读/快照 |
| CORE-003 | Windows Runtime PresenceServer | `ActivationType` | DWORD `0` | `:757-786` | `reg QUERY` 验证；SYSTEM 计划任务重试；无原值快照 |
| CORE-004 | `HKCU\Software\Microsoft\GameBar` | `UseNexusForGameBarEnabled` | DWORD `0` | `:791` | 无专用回读/快照 |
| CORE-005 | SystemProfile | `NetworkThrottlingIndex` | DWORD `0xFFFFFFFF` | `:793` | 见 CPU-004 |
| CORE-006 | SystemProfile | `SystemResponsiveness` | DWORD `10` | `:794` | 见 CPU-003 |
| CORE-007 | PriorityControl | `Win32PrioritySeparation` | DWORD `38/0x26` | `:796` | `Verify-RegDword:813`；无快照 |
| CORE-008 | GraphicsDrivers | `HwSchMode` | DWORD `2` | `:798` | `Verify-RegDword:814`；无快照，需重启 |
| CORE-009 | Tasks\Games | 七个值 | DWORD/SZ，见 CPU-005 | `:800-807` | 无逐项回读/快照 |
| CORE-010 | `HKCU\Software\Microsoft\GameBar` | `AutoGameModeEnabled`、`AllowAutoGameMode` | DWORD `0` | `:809-810` | 实际是关闭自动 Game Mode；无回读/快照 |

### CORE-011 至 CORE-013：系统行为子项

| 编号 | 路径/对象 | 值/命令 | 类型/目标 | 源码 | 验证/恢复 |
|---|---|---|---|---|---|
| CORE-011 | Search | `BingSearchEnabled`、`AllowSearchToUseLocation`、`CortanaConsent` | DWORD `0` | `:818-820` | 无回读/快照 |
| CORE-012 | PrefetchParameters | `EnablePrefetcher` | DWORD `0` | `:822` | `Verify-RegDword:858`；无原值快照 |
| CORE-013 | FileSystem | `NtfsDisable8dot3NameCreation` | DWORD `1` | `:824` | 无专门回读/快照，需卷级验证 |

### CORE-014 至 CORE-016：系统命令与视觉效果

| 编号 | 对象 | 目标 | 源码 | 验证/恢复 |
|---|---|---|---|---|
| CORE-014 | MMAgent | `Disable-MMAgent -mc` | `:825-828` | `Get-MMAgent` 验证 `MemoryCompression=False`（`:859`）；无原状态快照，手动 `Enable-MMAgent -mc` 恢复 |
| CORE-015 | NTFS | `fsutil behavior set DisableDeleteNotify 0` | `:829-835` | 全局 `DisableDeleteNotify=0`（`:860`）；不等于逐卷验证，无原策略恢复 |
| CORE-016 | HKCU 视觉效果 | `VisualFXSetting`、FontSmoothing、UserPreferencesMask、Transparency、Animation 等 15 项 | `:839-853` | 无逐项回读/快照；可能影响用户体验和辅助功能 |

## 四、SECURITY-001：CPU 安全缓解

- **入口**：主菜单 `1→3`。
- **对象**：`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management`。
- **值**：`FeatureSettingsOverride=3`、`FeatureSettingsOverrideMask=3`，均 DWORD。
- **源码**：备份 `:395-410`；写入/验证 `:862-883`；恢复 `:412-426`。
- **备份**：`security-mitigation-backup.json`，记录固定路径、值名、存在性和 DWORD 原值；已有快照不覆盖。
- **验证**：逐项 `Verify-RegDword`，仅配置层，不等于所有 CPU/固件缓解运行时均关闭。
- **恢复**：子项 `3` 按快照写回或删除原本不存在的值。
- **风险**：降低 Meltdown/Spectre 侧信道缓解，不应作为普通游戏优化默认执行。

### SECURITY-002 VBS/HVCI/Credential Guard/Hyper-V

- **入口**：主菜单 `10` 子项 `1`。
- **对象**：写入 5 个 Device Guard 相关注册表值为 `0`，BCD 设置 `hypervisorlaunchtype off`、`isolatedcontext no`、`vsmlaunchtype off`，并禁用 Hyper-V。
- **验证**：BCD 值有 `Verify-BcdValue` 回读；注册表无专门回读；运行状态需重启后用 `msinfo32` 等检查。
- **恢复**：子项 `2` 删除脚本覆盖并尝试启用 Hyper-V，明确不是原始状态精确回滚，未保存原始注册表/功能状态。详见 BOOT-006。

### SECURITY-003 Device Guard EFI 锁定清除

- **入口**：主菜单 `9`。
- **对象**：检查 BitLocker，复制/调用 `SecConfig.efi`，创建一次性 BCD 引导项清除 EFI 变量。
- **验证**：重启后用 `msinfo32` 等人工检查；有临时 BCD 清理。
- **恢复**：无 EFI 变量原始快照或精确恢复；清理子项只能删除临时引导项，EFI 状态重新启用需系统安全设置手工处理。详见 BOOT-005。

## 五、MEMORY/STORAGE

### MEMORY-001 / MEMORY-002

- `EnablePrefetcher=0`：`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters`，源码 `:822`，回读 `:858`，无原值快照。
- `Disable-MMAgent -mc`：源码 `:827`，回读 `:859`，手动 `Enable-MMAgent -mc` 恢复，无原状态快照。
- **MEMORY-003** 页面文件：当前脚本没有自动修改、验证、备份或恢复，不计为执行项。

### STORAGE-001 / STORAGE-002

- NTFS 8.3：`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisable8dot3NameCreation=1`，源码 `:824`；无专门回读/恢复。
- TRIM：`fsutil behavior set DisableDeleteNotify 0`，源码 `:832`；全局查询验证 `:704-706`，不代表每卷结果；无原策略快照。

### STORAGE-005

写入缓存策略：当前脚本没有实际写入项，不计为执行覆盖；仅知识文档提及检查方法。

### STORAGE-003 BITS

`BITS` 在主菜单 `6→1` 被设为 `Manual`，源码 `:1338-1393`；与 37 项服务一起保存 `service-backup.json`，逐项验证 `StartMode`，`6→2` 恢复启动类型但不强制恢复运行状态。

### STORAGE-004 Native NVMe

- 前置：Windows build、NVMe 设备和 ViVeTool，源码 `:1534-1699`。
- 实际启用：ViVeTool Feature `60786016`、`48433719`（`:1627-1639`）；SafeBoot 两项默认值 `Storage Disks`（`:1643-1656`）。
- 旧 Override：只读查看和备份，不再自动写入/删除；不要按旧文档声称写入三个 Override。
- 备份：`nvme-backup.json` Version 3，含 Feature、SafeBoot 和旧 Override 原始状态；支持失败回滚。
- 运行时验证：`Test-NativeNvmeConfigured`/`Test-NativeNvmeEffective` 由 `Modules/Backup.Nvme.ps1` 提供，CI 在 Pester 下覆盖定义与返回结构；仍不等价于重启后的硬件行为验证。

## 六、GPU-001 / GPU-002

- HAGS：`HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\HwSchMode=2`，源码 `:798`，回读 `:814`，无专用快照，需重启和实际游戏测试。
- MPO：四个 DWORD：`DisableMPO=1`、`DisableOverlays=1`、`OverlayTestMode=5`、`OverlayMinFPS=0`，源码 `:1933-2063`；`mpo-backup.json` Version 1 保存存在性、类型和值；子项 `11→4` 精确恢复；无备份时只能删除受管值恢复系统默认；验证主要依赖只读状态、dxdiag 和应用实测。

## 七、BOOT

### BOOT-001 / BOOT-002 高级 BCD

- **入口**：主菜单 `2`。
- **计时器目标**：`useplatformclock=no`、`useplatformtick=no`、`disabledynamictick=yes`、`tscsyncpolicy=Enhanced`。
- **安全目标**：`nx=AlwaysOff`、`tpmbootentropy=ForceDisable`、`nointegritychecks=Yes`。
- **源码**：应用 `:902-918`，验证 `Verify-BcdValue（Modules/Common.ps1）`。
- **备份/恢复**：`bcd-backup.json` 保存 `{current}` 下七项存在性和值；子项 `2/4` 按快照写回或删除。
- **风险**：高级计时和安全项可能影响启动、安全和兼容性，不是普通性能开关。

### BOOT-003 / BOOT-004 测试模式

- 开启 `testsigning on`、`debug on`、`dbgsettings local`、`nointegritychecks on`，源码 `:923-945`；无独立快照和完整回读。
- 关闭只删除 `testsigning`、`debug`，保留 `nointegritychecks`，源码 `:947-972`；不是原状态精确恢复，删除不存在值可能报告失败。

### BOOT-005 / BOOT-006

- Device Guard EFI：主菜单 `9`，检查 BitLocker、复制 `SecConfig.efi`、创建一次性 BCD；无 EFI 文件/原 bootsequence 快照，清理临时项不是精确恢复。
- VBS/Hyper-V：主菜单 `10` 子项 1 实际使用 `bcdedit /set hypervisorlaunchtype off`、`isolatedcontext no`、`vsmlaunchtype off`（`:1926`），不是 `deletevalue`；子项 2 才删除覆盖并尝试启用 Hyper-V，菜单明确不是原状态精确回滚。

## 八、SERVICE

### SERVICE-001 Part 6

- Group A 21 项、Group B 9 项设为 Disabled；Xbox、Bluetooth、Embedded、BITS 7 项设为 Manual；源码 `:1302-1420`。
- 备份 `service-backup.json` 保存 37 项 Name/StartMode/State，已有快照不覆盖。
- `Verify-ServiceStartupType` 回读 StartMode；`6→2` 恢复启动类型，不强制恢复运行状态。

### SERVICE-002 Part 5

- 实现位于 `Modules/Defender.ps1`（Invoke-DefenderModule）；约 95 个策略值统一定义在 `Modules/Backup.Defender.ps1` 的 `$script:defenderPolicyValues`。
- 首次应用前自动快照全部策略值与 4 个自启动项的原始状态到 `defender-policy-backup.json`（Version 1，含结构校验，已有快照不覆盖）；备份失败会阻止修改。
- 子选项 `5 → 2` 按快照恢复注册表值（按快照记录的原始类型写回）；服务停用、计划任务删除与 SecHealthUI 移除不在快照范围内，仍属高风险、部分不可逆操作。

## 九、POWER-001

主菜单 `7` 使用 `ultimate-performance.pow`：`powercfg /export` 保存当前计划到 `power-backup.pow`，再 `/import` 和 `/setactive` 应用；子项 2 导入备份恢复。文件内置设置不是注册表逐项值；备份只保留最初快照，需手动用 `powercfg /getactivescheme` 验证当前计划。

## 十、REGISTRY 高风险边界

- Part 1 的普通注册表项大多由 `Set-RegDword/Set-RegString/Set-RegBinary` 写入，没有原值快照；只有 ActivationType、Win32Priority、HAGS 等有限回读。
- Part 5 的 Defender/SmartScreen/Security Center 约 95 个策略值已有快照与恢复入口（`5 → 2`）但无逐项回读，并与服务、任务和 Appx 删除相互影响。
- `defender-removal.ps1` 删除大量 Defender 注册、组件和文件，没有完整备份，脚本本身不可逆；不应归类为普通优化。

## 文档状态

- 本参考按当前 `tweakbyjie.ps1` 源码核对；源码行号变化后必须重新校对。
- “脚本执行”不等于“可恢复”；“配置层回读”不等于“运行时有效”；“知识说明”不等于“脚本支持”。
## 事实核查记录

核验机制：由 tweakbyjie 仓库 Coverage 自动审计持续校验，映射、执行参考、覆盖检查三份资料每一份都必须与 manifest 全部 44 项完全一致（缺少清单内编号与出现清单外编号均判失败）；正文 `Modules/文件.ps1` 引用由审计器校验文件存在与函数定义。2026-08-25 对照 tweakbyjie main（commit `cd95802`）校准：页首定位说明改为“Menu 仅调度、执行在各业务模块”，CPU-002 源码定位修正为 `Modules/Registry.ps1`。⚠️ 已知边界：正文表格中的 `:NNN` 为模块化前单文件源码的基线行号快照，仅作历史对照，不对应现行 Modules/ 结构；现行定位以 `Modules/函数名` 为准。
