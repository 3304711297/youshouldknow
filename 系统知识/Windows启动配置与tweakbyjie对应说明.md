# Windows 启动配置与 tweakbyjie 对应说明

## 对应范围

本页对应 `tweakbyjie/tweakbyjie.ps1` 的 BCD、测试模式和 Device Guard 启动项操作。启动配置会影响系统能否正常启动、驱动完整性和安全边界，不能与普通游戏优化混合执行。

## BOOT-001 高级 BCD 计时器配置

### 执行入口与目标

主菜单 `2. 高级 BCD / 计时器与启动安全`，源码 `tweakbyjie.ps1:902-918`：

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

## BOOT-002 高级启动安全 BCD 配置

### 执行入口与目标

同为主菜单 `2`，源码 `tweakbyjie.ps1:902-918`：

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

主菜单 `3. 开启测试模式`，源码 `tweakbyjie.ps1:923-948`：

```text
bcdedit /set testsigning on
bcdedit /debug on
bcdedit /dbgsettings local
bcdedit /set nointegritychecks on
```

该入口用于测试驱动或调试环境，不是性能优化。它没有独立的原始 BCD 快照，也没有完整的自动回读闭环。

### 影响与恢复

测试签名、内核调试和完整性检查改变系统安全模型，可能显示桌面水印并允许不适合日常使用的驱动环境。主菜单 `4` 可以删除 `testsigning` 和 `debug`，但脚本明确保留 `nointegritychecks`；它不是原状态精确恢复。若需关闭保留项，应按当前系统需求手动检查 BCD。

## BOOT-004 关闭测试模式

### 执行入口与目标

主菜单 `4. 关闭测试模式`，源码 `tweakbyjie.ps1:950-972`。当前脚本删除：

```text
bcdedit /deletevalue testsigning
bcdedit /deletevalue debug
```

并明确保留 `nointegritychecks`。该模块没有独立备份，也没有完整回读；删除不存在的值可能产生失败提示。源码中的用户提示已修正为：重新开启测试模式应使用主菜单选项 `3`。

## BOOT-005 Device Guard EFI 锁定清除

### 执行入口与目标

主菜单 `9. 清除 Device Guard EFI 锁定`，源码 `tweakbyjie.ps1:1700-1913`。流程包括：

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

## 重要边界

- `bcd-backup.json`、`service-backup.json` 等备份文件只有在实际运行模块后才会生成；仓库中存在脚本定义不等于本地已有用户备份。
- BCD 回读只证明当前配置层值，不证明系统启动后所有安全或计时行为符合预期。
- 任何测试模式、`nointegritychecks`、VBS/HVCI 或 EFI 操作都应独立测试并保留恢复介质。
