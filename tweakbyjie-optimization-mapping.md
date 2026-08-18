# tweakbyjie 优化项目映射

## 目的

建立知识说明与实际优化之间的对应关系。逐项映射必须以 `tweakbyjie/tweakbyjie.ps1` 当前源码为准，不能只根据概念标题判断已经覆盖。

结构：

```text
知识原理 → 优化项目 → 执行位置 → 验证方式 → 恢复方式
```

## CPU 逐项映射

共同执行入口：`tweakbyjie.ps1` 主菜单 `1` → `Part 1` 核心游戏优化 → 子项 `1`。对应知识文档：[`CPU 优化与 tweakbyjie 对应说明`](./CPU优化与tweakbyjie对应说明.md)。

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| CPU-001 | `Win32PrioritySeparation` | `HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl\Win32PrioritySeparation` → `REG_DWORD 38`（十进制，`0x26`）；源码 `tweakbyjie.ps1:796` | 源码 `:813` 使用 `Verify-RegDword` 回读目标值 `38` | 修改前记录原始 DWORD，恢复原值；当前脚本未提供该项自动备份/恢复 |
| CPU-002 | `Multimedia SystemProfile` | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile`；源码 `:793-794` 写入该路径下的独立值 | 没有对该组配置进行统一回读 | 逐项记录并恢复原值；当前脚本未提供统一备份/恢复 |
| CPU-003 | `SystemResponsiveness` | `...\Multimedia\SystemProfile\SystemResponsiveness` → `REG_DWORD 10`；源码 `:794` | 当前源码没有调用 `Verify-RegDword` 验证该值 | 修改前记录原始 DWORD，恢复原值；当前脚本未提供自动备份/恢复 |
| CPU-004 | `NetworkThrottlingIndex` | `...\Multimedia\SystemProfile\NetworkThrottlingIndex` → `REG_DWORD 0xFFFFFFFF`；源码 `:793` | 当前源码没有对该值进行回读验证 | 修改前记录原始 DWORD，恢复原值；当前脚本未提供自动备份/恢复 |
| CPU-005 | `Tasks\Games` | `...\Multimedia\SystemProfile\Tasks\Games`；源码 `:800-807` 写入七个值：`Affinity=0`、`Background Only=False`、`Clock Rate=10000`、`GPU Priority=8`、`Priority=6`、`Scheduling Category=High`、`SFIO Priority=High` | 当前源码没有对七个值进行回读验证 | 修改前记录每个值的存在状态、类型和值；恢复时逐项写回，原本不存在的值应删除；当前脚本未提供自动备份/恢复 |

### CPU 映射说明

- `PriorityControl` 是注册表路径的一部分，CPU-001 的实际优化项目名称是 `Win32PrioritySeparation`，两者不能互相替代。
- `Multimedia SystemProfile` 是配置路径/类别，不应覆盖或代替其下的 CPU-003、CPU-004 和 CPU-005 独立项目。
- `Tasks\Games` 的 `Clock Rate` 属于 MMCSS 游戏任务类别配置，不是直接设置 GPU 硬件时钟。
- “知识说明已覆盖”与“脚本执行闭环已完成”是两个不同状态。本表记录了当前脚本确实缺少统一备份、恢复和部分回读验证的事实。

## GPU 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| GPU-001 | HAGS / `HwSchMode` | 主菜单 `1` → 核心游戏优化 `1`；`HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers\HwSchMode` → `REG_DWORD 2`；源码 `tweakbyjie.ps1:797-798` | 源码 `:814` 使用 `Verify-RegDword` 回读 `HwSchMode=2`；仍需重启和实际游戏测试 | 当前核心路径未提供独立自动备份/恢复；修改前记录原值，恢复时写回或删除原本不存在的值 |
| GPU-002 | MPO / Overlay | 主菜单 `11. MPO 设置管理`；管理 `DisableMPO`、`OverlayTestMode`、`DisableOverlays`、`OverlayMinFPS` 四个值；源码 `tweakbyjie.ps1:1933-2059` | `11 → 0` 只读查看注册表值；重启后用 `dxdiag` 作辅助判断，并结合浏览器、视频、多显示器、窗口化游戏、DX12、HDR、录屏和覆盖层实测 | 首次方案 A/B/C 前保存 `mpo-backup.json`；`11 → 4` 按原始存在状态、类型和值恢复；无备份时只能删除受管理值恢复系统默认 |

对应知识文档：[`GPU 调度与显示管线`](./GPU调度与显示管线.md)。

### GPU 映射说明

- HAGS 与 MPO 是两个独立项目：HAGS 修改 `HwSchMode`，MPO 通过 Part 11 管理四个社区排障值。
- 当前源码没有直接修改 DirectX 版本、游戏引擎或 GPU 硬件时钟的执行项；DirectX 相关内容属于图形管线背景说明，不应虚构为脚本覆盖项。
- `Tasks\\Games\Clock Rate` 属于 MMCSS 游戏任务类别配置，不是 GPU 硬件时钟设置。

## Memory 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| MEMORY-001 | `EnablePrefetcher` | 主菜单 `1` → 系统行为优化 `2`；`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters\EnablePrefetcher` → `REG_DWORD 0`；源码 `tweakbyjie.ps1:821-822` | 源码 `:858` 使用 `Verify-RegDword` 回读 `0`；需重启后结合应用启动测试 | 当前脚本未保存原值，也没有自动恢复入口；恢复前应记录原值/存在状态，恢复时写回或删除 |
| MEMORY-002 | Memory Compression | 主菜单 `1` → 系统行为优化 `2`；执行 `Disable-MMAgent -mc`；源码 `tweakbyjie.ps1:825-828` | 源码 `:859` 使用 `Verify-MemoryCompressionDisabled` / `Get-MMAgent` 检查关闭状态；需重启 | 当前脚本未保存原状态；手动恢复使用 `Enable-MMAgent -mc` 后重启 |
| MEMORY-003 | 虚拟内存 / 页面文件 | 当前 `tweakbyjie.ps1` 未发现 pagefile、分页文件或 `AutomaticManagedPagefile` 的执行项 | 知识文档提供 GUI 和系统托管原则，不属于脚本运行时验证 | 不存在脚本修改或脚本恢复项；不要把知识教程误记为自动化覆盖 |

对应知识文档：[`Windows内存压缩功能与MMAgent设置`](./系统知识/Windows内存压缩功能与MMAgent设置.md)、[`Windows虚拟内存设置指南`](./系统知识/Windows虚拟内存设置指南.md)。

### Memory 映射说明

- 脚本关闭的是传统 `EnablePrefetcher=0`，同时通过 `Disable-MMAgent -mc` 关闭 Memory Compression；两者是不同机制。
- 现有知识文档已说明多数用户通常应保留 Prefetch 默认行为，脚本的强制关闭应视为需要基线和回滚的场景，不代表普适收益。
- 当前脚本没有为 Memory-001/002 建立修改前快照；写入成功或回读成功不等于具备精确恢复能力。

## Storage 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| STORAGE-001 | NTFS 8.3 短文件名 | 主菜单 `1` → 系统行为优化 `2`；`HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisable8dot3NameCreation` → `REG_DWORD 1`；源码 `tweakbyjie.ps1:823-824` | 当前源码没有专门回读验证，也没有按卷核验 | 当前脚本没有原值备份或恢复入口；恢复需先记录原值/存在状态后写回或删除，并结合卷级状态检查 |
| STORAGE-002 | NTFS TRIM | 主菜单 `1` → 系统行为优化 `2`；执行 `fsutil.exe behavior set DisableDeleteNotify 0`；源码 `tweakbyjie.ps1:829-835` | 源码 `:860` 使用 `Verify-TrimEnabled` 查询全局 `DisableDeleteNotify=0`；不代表每个卷都已单独核验 | 脚本未备份原状态；恢复应根据修改前策略谨慎处理，不应无条件关闭 TRIM |
| STORAGE-003 | BITS 启动类型 | 主菜单 `6` 服务优化；`BITS` 在手动服务组中设为 `Manual`；源码 `tweakbyjie.ps1:1337-1405` | `Verify-ServiceStartupType` 验证 `Manual` | 服务优化前写入 `service-backup.json`，选项 `6 → 2` 按快照恢复原启动类型；当前恢复不保证恢复服务运行状态 |
| STORAGE-004 | Native NVMe Driver | 主菜单 `8`；按系统版本、NVMe 和 ViVeTool 条件管理 Feature/SafeBoot/驱动状态；源码 `tweakbyjie.ps1:1534-1687` | 重启后检查 `nvmedisk` 驱动状态；模块有失败回滚和状态检查 | 使用 NVMe 专用快照恢复 Feature、SafeBoot 和旧 Override；该模块不是写入缓存设置 |
| STORAGE-005 | 写入缓存策略 | 当前 `tweakbyjie.ps1` 未发现实际写入项 | 无脚本验证 | 仅有知识/检查文档提及，不计作脚本执行覆盖 |

对应知识文档：[`存储与NVMe原理`](./存储与NVMe原理.md)。该文档现已补充脚本入口、实际行为、验证和恢复边界；其中写入缓存仍明确标记为当前脚本未执行的知识/检查项。

## Security 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| SECURITY-001 | CPU 安全缓解覆盖 | 主菜单 `1` → CPU 安全缓解子项 `2`；`HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride=3`、`FeatureSettingsOverrideMask=3`；源码 `tweakbyjie.ps1:862-883` | 写入后分别用 `Verify-RegDword` 回读；专用备份快照保存存在性和原值 | `security-mitigation-backup.json` 记录原状态，子项 `3` 按快照恢复 |
| SECURITY-002 | VBS/HVCI/Credential Guard/Hyper-V 关闭 | 主菜单 `10` 子项 `1`；写入 5 个 Device Guard 相关注册表值为 `0`，设置 BCD `hypervisorlaunchtype off`、`isolatedcontext no`、`vsmlaunchtype off`，禁用 Hyper-V；源码 `tweakbyjie.ps1:1915-1931` | BCD 有 `Verify-BcdValue`；注册表没有专门回读；运行状态需重启后检查 | 子项 `2` 删除脚本覆盖并尝试启用 Hyper-V，但脚本明确不是原始状态精确回滚，未保存原始注册表/功能状态 |
| SECURITY-003 | Device Guard EFI 锁定清除 | 主菜单 `9`；检查 BitLocker，复制/调用 `SecConfig.efi`，创建一次性 BCD 引导项清除 EFI 变量；源码 `tweakbyjie.ps1:1700-1913` | 重启后用 `msinfo32` 等检查；有临时 BCD 清理 | 没有 EFI 变量原始快照或精确恢复；清理子项只能删除临时引导项，EFI 状态重新启用需系统安全设置手工处理 |

对应知识文档：[`VBS 与系统安全缓解`](./VBS与系统安全缓解.md)。该文档需要补充实际路径、选项入口、BitLocker 前置检查、重启后验证和“非精确回滚”边界。

## Service 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| SERVICE-001 | Part 6 服务启动类型 | 主菜单 `6 → 1`；Group A 21 个 + Group B 9 个设为 `Disabled`，Xbox/Bluetooth/Embedded/BITS 7 个设为 `Manual`；源码 `tweakbyjie.ps1:1302-1420` | `Verify-ServiceStartupType` 使用 `Win32_Service.StartMode` 逐项验证；不验证运行状态和依赖功能 | 修改前创建/校验 `service-backup.json`；`6 → 2` 恢复原启动类型，不强制恢复运行状态 |
| SERVICE-002 | Part 5 Defender/Security Center 服务与策略 | 主菜单 `5`；`WinDefend` 及额外 Defender 服务停止并禁用，同时写入 Defender/SmartScreen/Security Center 策略，额外分支还删除任务、启动项和 `SecHealthUI`；源码 `tweakbyjie.ps1:977-1300` | 该入口没有统一启动类型回读；策略和删除操作没有完整配置层验证 | 不使用 `service-backup.json`，没有统一自动恢复；属于高风险、可能不可逆的安全组件停用 |

对应知识文档：[`Windows服务优化原则`](./Windows服务优化原则.md)、[`Windows系统服务对应注册表路径`](./系统知识/Windows系统服务对应注册表路径.md)。

## Boot 逐项映射

| 编号 | tweakbyjie 实际项目 | 执行位置与目标 | 当前验证范围 | 恢复方式与状态 |
| --- | --- | --- | --- | --- |
| BOOT-001 | 高级 BCD 计时器 | 主菜单 `2`；`useplatformclock=no`、`useplatformtick=no`、`disabledynamictick=yes`、`tscsyncpolicy=Enhanced`；源码 `tweakbyjie.ps1:902-918` | `Verify-BcdValue` 回读 | 与 BOOT-002 共用 `bcd-backup.json`，按快照恢复原值或删除 |
| BOOT-002 | 启动安全 BCD | 主菜单 `2`；`nx=AlwaysOff`、`tpmbootentropy=ForceDisable`、`nointegritychecks=Yes` | `Verify-BcdValue` 回读 | 依赖有效 `bcd-backup.json`；无备份时拒绝声称恢复 |
| BOOT-003 | 开启测试模式 | 主菜单 `3`；开启 `testsigning`、`debug`、`dbgsettings local`、`nointegritychecks`；源码 `tweakbyjie.ps1:923-948` | 无完整自动回读 | 无独立快照；改变安全模型，需手工检查恢复 |
| BOOT-004 | 关闭测试模式 | 主菜单 `4`；删除 `testsigning`、`debug`，保留 `nointegritychecks`；源码 `tweakbyjie.ps1:950-972` | 无完整自动回读 | 无精确原状态恢复；删除不存在值可能报告失败 |
| BOOT-005 | Device Guard EFI 锁定清除 | 主菜单 `9`；BitLocker 检查、SecConfig.efi、一次性 BCD 引导项；源码 `tweakbyjie.ps1:1700-1913` | 重启后 `msinfo32` 等人工检查；清理临时 BCD | 无 EFI/bootsequence 原始快照；只能清理临时项，不是精确回滚 |
| BOOT-006 | VBS/Hyper-V 启动项 | 主菜单 `10`；`hypervisorlaunchtype`、`vsmlaunchtype`、`isolatedcontext`；源码 `tweakbyjie.ps1:1915-1931` | BCD 值有回读，运行状态需重启 | 删除覆盖并尝试启用 Hyper-V，不恢复原 BCD/功能状态 |

对应知识文档：[`Windows启动配置与 tweakbyjie 对应说明`](./系统知识/Windows启动配置与tweakbyjie对应说明.md)。

## Registry 逐项边界

当前脚本还存在大量独立注册表执行项，不能只用 CPU/GPU/Memory 分类概括：

- Part 1：GameDVR、GameBar、Search、视觉效果、ActivationType、Prefetch、NTFS、HAGS、MMCSS 等；其中只有少数项目有回读，核心多数没有原值备份。
- Part 5：Defender、SmartScreen、Security Center、CI/Smart App Control 等策略注册表值；没有统一原值备份、完整回读或自动恢复，且与服务/任务/Appx 删除操作相互影响。
- `defender-removal.ps1`：独立的高风险删除脚本，会删除 Defender 服务注册、WinRT/Svchost、CLSID/App/Shell/Autologger 等键和值及实体文件；只有前置查询和有限验证，没有备份，脚本本身明确不可逆。

对应原则文档：[`注册表优化原则`](./注册表优化原则.md)。这些项目后续应继续按稳定编号拆分；本阶段不把概念性注册表文章当作已完成的逐项执行覆盖。

## 原则

所有已经确认的优化项目必须具备：

1. 修改原因
2. 适用环境
3. 风险说明
4. 恢复方式
5. 实际执行位置与目标值
6. 可复核的验证方法
