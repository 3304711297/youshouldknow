# Windows 启动配置与 tweakbyjie 对应说明

## 对应范围

> 已与 `tweakbyjie` 模块化结构同步：`Modules/Menu.ps1` 只负责菜单调度，BCD/测试模式执行逻辑位于 `Modules/Bcd.ps1`，通用写入/验证在 `Modules/Common.ps1`，备份闭环在 `Modules/Backup.*.ps1`；此处不再使用 `tweakbyjie.ps1:行号` 定位，以 `Modules/文件.ps1` 和函数名为准。详见 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md`。


本页对应 `tweakbyjie/tweakbyjie.ps1` 的 BCD、测试模式和 Device Guard 启动项操作。启动配置会影响系统能否正常启动、驱动完整性和安全边界，不能与普通游戏优化混合执行。

## BOOT-001 高级 BCD 计时器配置

### 执行入口与目标

主菜单 `2. 高级 BCD / 计时器与启动安全`，源码 `Modules/Bcd.ps1`（`Invoke-BcdAdvancedModule`）+ `Modules/Backup.Bcd.ps1`/`Modules/Common.ps1`：

```text
useplatformclock    = No
useplatformtick     = No
disabledynamictick   = Yes
tscsyncpolicy       = Enhanced
```

这些值通过 `bcdedit` 写入当前启动项，意图测试平台时钟、动态 tick 和 TSC 同步策略对计时与延迟的影响。它们不是所有硬件的通用性能优化。

### 适用环境与风险

只适合有明确计时、帧时间或音频同步问题并能准备恢复介质的测试环境。错误的 BCD 计时器设置可能导致计时异常、功耗变化、兼容性问题或没有任何收益。

### 验证与恢复

应用后脚本使用 `Verify-BcdValue` 回读目标值。修改前会在 `bcd-backup.json` 中保存 `Present/Value` 快照；恢复依赖有效的完整备份，按原值写回或删除原本不存在的项。该备份还被安全 BCD 项共用，文件损坏或缺失时脚本拒绝声称已恢复。

### HPET 辨析：不建议直接禁用 HPET 设备

HPET（High Precision Event Timer，高精度事件定时器）是主板上的硬件计时器。社区常见的"禁用 HPET"做法（BIOS 里关闭或设备管理器停用设备）并不适合作为通用优化：部分系统组件与传统应用仍依赖它做时间基准，直接禁用设备可能造成计时漂移、音频爆音或兼容性问题。

更稳妥的思路不是动设备，而是通过 BCD 调整操作系统对计时器的**调用策略**——这正是 BOOT-001 四个值的作用：

- `useplatformclock no`：禁止操作系统强制优先调用 HPET；
- `useplatformtick no`：禁止强制使用主板计时器（相对 TSC 的纳秒级精度慢得多）;
- `disabledynamictick yes`：关闭动态 tick 频率调节，使计时稳定平滑（该机制原本是节能特性）；
- `tscsyncpolicy Enhanced`：增强 TSC 同步策略。

恢复时把 `/set xxx yes|no` 写法换成 `bcdedit /deletevalue <值名>` 后重启即可。延伸参考：B站文章[《【Win优化】Bcdedit 参数与高精度计时器 HPET》](https://b23.tv/cOH0RxB)。注意：以上均为调用策略层面的调整，HPET 设备本身不在 tweakbyjie 的执行范围内。

## BOOT-002 高级启动安全 BCD 配置

### 执行入口与目标

同为主菜单 `2`，源码 `Modules/Bcd.ps1`（`Invoke-BcdAdvancedModule` 启动安全子项）+ `Modules/Backup.Bcd.ps1`/`Modules/Common.ps1`：

```text
nx               = AlwaysOff
tpmbootentropy    = ForceDisable
nointegritychecks = Yes
```

这些值会削弱或绕过部分启动安全/完整性检查，只能在明确理解驱动签名、TPM 和系统安全影响时测试。`nointegritychecks` 与测试模式相关，不应作为普通游戏优化使用。

### 验证与恢复

脚本对 BCD 目标值进行回读验证，并与 BOOT-001 共用 `bcd-backup.json`。恢复必须按备份恢复原始存在状态；没有有效备份时不能把“删除当前值”描述成恢复原配置。

## BOOT-003 开启测试模式

### 执行入口与目标

主菜单 `3. 开启测试模式`，源码 `Modules/Bcd.ps1`（`Invoke-TestModeEnableModule`）：

```text
bcdedit /set testsigning on
bcdedit /debug on
bcdedit /dbgsettings local
bcdedit /set nointegritychecks on
```

该入口用于测试驱动或调试环境，不是性能优化。它没有独立的原始 BCD 快照，也没有完整的自动回读闭环。

### 影响与恢复

测试签名、内核调试和完整性检查改变系统安全模型，可能显示桌面水印并允许不适合日常使用的驱动环境。主菜单 `4` 可以删除 `testsigning` 和 `debug`，但脚本明确保留 `nointegritychecks`；它不是原状态精确恢复。若需关闭保留项，应按当前系统需求手动检查 BCD。

> ⚠️ **反作弊风险**：`/debug on` 开启的内核调试模式会被主流反作弊系统（EAC、BattlEye 等）识别为调试环境，可能导致游戏拒绝运行甚至账号封禁；⚠️ 该结论来自社区共识而非反作弊厂商官方声明。调试用途结束后应及时用主菜单 `4` 或 `bcdedit /deletevalue debug` 关闭。

## BOOT-004 关闭测试模式

### 执行入口与目标

主菜单 `4. 关闭测试模式`，源码 `Modules/Bcd.ps1`（`Invoke-TestModeDisableModule`）。当前脚本删除：

```text
bcdedit /deletevalue testsigning
bcdedit /deletevalue debug
```

并明确保留 `nointegritychecks`。该模块没有独立备份，也没有完整回读；删除不存在的值可能产生失败提示。源码中的用户提示已修正为：重新开启测试模式应使用主菜单选项 `3`。

## BOOT-005 Device Guard EFI 锁定清除

### 执行入口与目标

主菜单 `9. 清除 Device Guard EFI 锁定`，源码 `Modules/Virtualization.ps1`。流程包括：

1. 检查 BitLocker 保护状态和管理员权限；
2. 查找并挂载 EFI 分区，复制 `SecConfig.efi`；
3. 创建一次性 BCD `DebugTool` 引导项；
4. 设置 `DISABLE-LSA-ISO` 等 `loadoptions`，通过重启清除 Device Guard EFI 变量；
5. 重启后按系统提示确认，并用 `msinfo32` 等方式核查。

### 风险、验证与恢复

该流程涉及 EFI 变量、BitLocker 和一次性启动顺序。脚本会清理临时 BCD 项和盘符，但没有保存原始 EFI 变量、原始 `bootsequence` 或精确恢复 `SecConfig.efi` 文件；清理临时项不等于恢复 Device Guard 原状态。执行前必须保留 BitLocker 恢复密钥，确认确实需要清除 EFI 锁定，并准备离线恢复方案。

## BOOT-006 VBS/HVCI/Hyper-V 的启动部分

主菜单 `10` 除注册表和 Windows 可选功能外，还处理：

```text
hypervisorlaunchtype = Off
vsmlaunchtype        = Off
isolatedcontext      = No
```

关闭子项对这些 BCD 值有回读验证；恢复子项删除脚本覆盖并尝试启用 Hyper-V，但没有保存原始 BCD、可选功能或策略状态，因此不是精确回滚。运行时是否仍有 Hypervisor 必须重启后检查。

## 已知但脚本未采纳的 BCD 项（仅知识记录）

以下 BCD 用法在社区资料中流传，`tweakbyjie` 当前**明确不采纳**（无对应菜单项、无编号、无备份闭环），此处仅作知识记录；使用需自行承担验证与恢复责任。

| 命令 | 作用与边界 |
| --- | --- |
| `bcdedit /set loadoptions DISABLE_INTEGRITY_CHECKS` | 经加载选项关闭驱动签名强制（内核加载未签名驱动的常见手法之一）。脚本不采纳：与测试模式/完整性检查项职责重叠且风险更高 |
| `bcdedit /set loadoptions DISABLE_INTEGRITY_CHECKS,DISABLE-LSA-ISO,DISABLE-VBS` | 三合一组合：在关闭签名强制之外同时关闭 LSA 隔离与 VBS 加载。脚本仅在 BOOT-005 的 EFI 清除流程中设置过 `DISABLE-LSA-ISO` 单值，组合形式不采纳 |
| `bcdedit /set nx OptIn` | DEP 的 OptIn 档位（仅为 Windows 组件和服务启用 DEP，兼容性更好）。脚本只用 `nx AlwaysOff`（BOOT-002），恢复走快照删除还原系统默认，不写 OptIn |
| `bcdedit /set bootux disabled` | 禁用 Windows 启动动画（转圈界面），缩短开机画面时间。恢复：`bcdedit /deletevalue bootux` |

以上均不计入 tweakbyjie 执行覆盖（无 BOOT 编号、无快照），效果与副作用随 Windows 版本差异较大。

## 重要边界

- `bcd-backup.json`、`service-backup.json` 等备份文件只有在实际运行模块后才会生成；仓库中存在脚本定义不等于本地已有用户备份。
- BCD 回读只证明当前配置层值，不证明系统启动后所有安全或计时行为符合预期。
- 任何测试模式、`nointegritychecks`、VBS/HVCI 或 EFI 操作都应独立测试并保留恢复介质。
## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-21）。

| 声明 | 核查结果 |
| --- | --- |
| 高级 BCD 管理 7 个值（useplatformclock/useplatformtick/disabledynamictick/tscsyncpolicy/nx/tpmbootentropy/nointegritychecks） | ✅ 属实：bcdManagedValues 定义一致 |
| BCD 修改前备份 bcd-backup.json，恢复按快照写回或删除，无备份时拒绝声称恢复 | ✅ 属实：Backup.Bcd.ps1（含写后回读校验） |
| 测试模式开启写入 testsigning/debug/dbgsettings/nointegritychecks；关闭仅删除 testsigning/debug、保留 nointegritychecks | ✅ 属实：Part 3/4 行为一致 |
| 测试模式与 EFI/VBS 操作无精确原始状态回滚 | ✅ 属实：文档边界与源码行为一致 |
| `bootux disabled` 可禁用启动动画；`loadoptions` 三合一组合可关闭签名强制/LSA 隔离/VBS 加载；`nx OptIn` 为仅 Windows 组件档位 | ⚠️ 社区资料记载，按知识记录收录；除 `DISABLE-LSA-ISO` 单值（BOOT-005）外脚本均不采纳 |
| `/debug on` 会被主流反作弊识别，可能导致游戏拒跑或封号 | ⚠️ 社区共识（EAC/BattlEye 用户报告），无反作弊厂商官方声明 |
| 直接禁用 HPET 设备不适合，应改用 BCD 计时器调用策略调整 | ✅ 判断合理：BOOT-001 即为此类调整；设备禁用的副作用已有社区案例 |
