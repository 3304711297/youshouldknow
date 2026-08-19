# CPU 优化与 tweakbyjie 对应说明

## 对应范围

本章节逐项对应 `tweakbyjie/tweakbyjie.ps1` 当前“Part 1 → 核心游戏优化 → 子项 1”中的 CPU、MMCSS 多媒体调度和 Games 任务配置。脚本实际写入的路径、值名和目标值以当前源码为准。

> 重要边界：当前脚本对这些项目没有统一的修改前备份/恢复流程；除 CPU-001 外，当前执行路径也没有为这些项目提供完整的回读验证。因此，下面的“恢复方式”是人工恢复前提，不代表脚本已经自动提供恢复功能。

## CPU-001 Win32PrioritySeparation

### 执行位置

- 源码：`tweakbyjie.ps1:796`
- 入口：主菜单 `1` → 核心游戏优化 `1`
- 写入函数：`Set-RegDword`

### 注册表位置与目标值

```text
注册表 Hive：HKEY_LOCAL_MACHINE（HKLM）
子键：SYSTEM\CurrentControlSet\Control\PriorityControl
值名：Win32PrioritySeparation
类型：REG_DWORD（32 位无符号整数）
脚本目标值：38（十进制）= 0x26（十六进制）
```

### 字段卡

| 字段 | 当前事实 |
|---|---|
| 稳定编号 | `CPU-001` |
| 分类 | CPU 调度 / 前台与后台线程资源分配 |
| 脚本入口 | 主菜单 `1` → 核心游戏优化 `1` |
| 执行源码 | `tweakbyjie.ps1:796`，调用 `Set-RegDword` |
| 验证源码 | `tweakbyjie.ps1:813`，调用 `Verify-RegDword` |
| 配置对象 | `HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl` 下的单个 DWORD |
| 脚本行为 | 写入 `38`，成功后标记需要重启；不提供 CPU-001 专用快照 |
| 文档状态 | 已绑定当前源码；其他编码仅为参考，不属于脚本菜单 |

### Windows 原理

Windows 调度器根据线程优先级、前台/后台状态和量子时间等因素分配处理器时间。`Win32PrioritySeparation` 是系统级调度策略参数，会影响前台程序与后台程序的相对调度行为。它不是简单的“锁定某个程序使用 CPU”，实际效果还会受 Windows 版本、处理器、线程优先级和应用自身行为影响。

### 修改目的

脚本将该值设为十进制 `38`（十六进制 `0x26`），目标是调整前台交互应用和游戏线程的调度策略，优先关注响应性。这里必须区分十进制和十六进制表示，不能把 `38` 误读成十六进制 `0x38`。

### 默认值与目标值对照

`Win32PrioritySeparation` 的默认值不能从图片、旧教程或另一台电脑直接推断。必须在目标机修改前读取，并记录：

```powershell
$path = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'
Get-ItemProperty -Path $path -Name Win32PrioritySeparation |
  Select-Object Win32PrioritySeparation
```

| 状态 | 十进制 | 十六进制 | 含义 |
|---|---:|---:|---|
| 目标机修改前 | 以实际读取为准 | 以实际读取为准 | Windows 版本、策略和历史工具可能不同 |
| 当前脚本目标 | `38` | `0x26` | Short + Variable + High foreground boost（传统位字段解释） |
| 图片中的后台参考值 | `24` | `0x18` | Long + Fixed + No foreground boost（传统位字段解释） |

`24/0x18` 只是参考对照，不是当前脚本的后台服务模式，也不应因为名称“后台优化”就直接写入服务器、办公机或目标用户设备。

## Win32PrioritySeparation 位字段参考表

下面的表用于解释传统资料中常见的 `Win32PrioritySeparation` 编码。它是**参考解码表**，不是 Windows 所有版本的官方性能保证，也不是 `tweakbyjie` 的菜单选项。

常见的位组合可以按以下方式理解：

| 位值 | 含义 |
|---:|---|
| `32`（`0x20`） | Short Quantum；短量子 |
| `16`（`0x10`） | Long Quantum；长量子 |
| `8`（`0x08`） | Fixed Quantum；固定量子 |
| `4`（`0x04`） | Variable Quantum；可变量子 |
| `2`（`0x02`） | High foreground boost；前台高提升 |
| `1`（`0x01`） | Medium foreground boost；前台中等提升 |
| `0` | No foreground boost；无前台提升 |

每一项的基础值只取相应互斥组中的一个值：量子长度取 `32` 或 `16`，量子类型取 `8` 或 `4`，前台提升取 `2`、`1` 或 `0`。例如：

```text
32 + 4 + 2 = 38 Dec = 0x26
16 + 8 + 0 = 24 Dec = 0x18
```

### 常见组合

| 十进制 | 十六进制 | 量子长度 | 量子类型 | 前台提升 | 传统资料中的描述 |
|---:|---:|---|---|---|---|
| `42` | `0x2A` | Short | Fixed | High | 短、固定、前台高提升 |
| `41` | `0x29` | Short | Fixed | Medium | 短、固定、前台中等提升 |
| `40` | `0x28` | Short | Fixed | None | 短、固定、无前台提升 |
| `38` | `0x26` | Short | Variable | High | 短、可变、前台高提升 |
| `37` | `0x25` | Short | Variable | Medium | 短、可变、前台中等提升 |
| `36` | `0x24` | Short | Variable | None | 短、可变、无前台提升 |
| `26` | `0x1A` | Long | Fixed | High | 长、固定、前台高提升 |
| `25` | `0x19` | Long | Fixed | Medium | 长、固定、前台中等提升 |
| `24` | `0x18` | Long | Fixed | None | 长、固定、无前台提升 |
| `22` | `0x16` | Long | Variable | High | 长、可变、前台高提升 |
| `21` | `0x15` | Long | Variable | Medium | 长、可变、前台中等提升 |
| `20` | `0x14` | Long | Variable | None | 长、可变、无前台提升 |

### 如何读取目标值

只读读取注册表得到的是一个 DWORD。先确认输出是十进制还是十六进制，再按表格解码。以脚本当前值为例：

```text
38 Dec = 0x26
0x26 = 32 + 4 + 2
= Short Quantum + Variable Quantum + High foreground boost
```

这里的 `26` 是十六进制数字，不能把脚本的十进制 `38` 误写成十六进制 `0x38`。同理，图片中的 `24 Dec / 18 Hex` 是十进制 `24`、十六进制 `0x18` 的同一个值，不是两个不同配置。

### 参考值与脚本实际范围

传统资料常把 `38 Dec / 0x26` 描述为前台应用优化，把 `24 Dec / 0x18` 描述为后台服务优化。它们可以帮助理解位字段，但不能直接证明在当前 Windows 版本、硬件或游戏中一定更快。

`tweakbyjie` 当前只在 `tweakbyjie.ps1:796` 写入 `38 Dec / 0x26`，并在 `:813` 回读验证；脚本没有实现 `24/0x18` 或其他组合的切换，也没有新增“前台/后台模式”菜单。

> ⚠️ **可靠性边界**：量子长度、量子类型和 foreground boost 的传统位解释在资料中广泛流传，但实际调度效果会受到 Windows 版本、策略、处理器、线程优先级和应用行为影响。修改前请读取目标机原值、保存恢复信息，并用帧时间、输入延迟和后台任务完成时间进行 A/B 测试。不要仅凭表格或注册表目标值宣称性能提升。

### 潜在影响

前台响应可能改善，也可能没有可测收益。后台编译、压缩、同步、渲染或长时间计算任务的调度份额可能变化；不同系统版本和硬件的结果可能不同。该值不会锁定某个进程的 CPU，也不会绕过电源、温度、线程优先级或应用自身调度。

### 验证方法

#### 配置层验证

脚本在 `tweakbyjie.ps1:813` 使用 `Verify-RegDword` 回读并验证目标值 `38`。也可以只读检查：

```powershell
Get-ItemPropertyValue `
  'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' `
  'Win32PrioritySeparation'
```

这只能验证注册表配置层的目标值，不代表调度器在所有应用中产生了预期效果，也不代表性能一定提升。

#### 运行时 A/B 验证

在相同硬件、驱动、游戏版本、分辨率和电源模式下，对比修改前后：

- 平均 FPS 和 1% Low；
- 帧时间波动；
- 输入延迟；
- 后台编译、压缩或同步任务完成时间；
- 游戏切换、录制、睡眠/唤醒和长时间稳定性。

如果只观察一个游戏的一次平均 FPS，不能判断该值是否有效。建议先保留默认值作为基线，再测试目标值；不要同时修改 HAGS、MMCSS、Games 任务或电源计划，否则无法归因。

### 备份与恢复

当前脚本没有为 CPU-001 建立独立备份文件，也没有提供自动恢复入口。执行前应手工保存原始存在状态、注册表类型和值：

```powershell
$path = 'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl'
$key = Get-Item $path
$exists = $key.GetValueNames() -contains 'Win32PrioritySeparation'
if ($exists) {
  [pscustomobject]@{
    Exists = $true
    Kind = $key.GetValueKind('Win32PrioritySeparation').ToString()
    Value = $key.GetValue('Win32PrioritySeparation')
  }
} else {
  [pscustomobject]@{ Exists = $false; Kind = $null; Value = $null }
}
```

恢复时：

- 原值存在：按原类型和值写回；
- 原值不存在：删除实验新增的 `Win32PrioritySeparation`；
- 恢复后重新读取并重启，再进行同一组 A/B 测试。

不要把 `0x26`、`0x18` 或另一台电脑的值当作通用恢复值。

### 恢复方式

上面的手工快照和恢复规则是本条目的恢复前提。`tweakbyjie` 当前只负责写入/验证 `38`，不负责保存或恢复 CPU-001 的原始值。

## CPU-002 Multimedia SystemProfile

### 执行位置

- 源码：`tweakbyjie.ps1:793-794`
- 入口：主菜单 `1` → 核心游戏优化 `1`
- 写入函数：`Set-RegDword`

### 注册表位置与包含项目

```text
路径：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile
```

CPU-002 表示 `SystemProfile` 这一组多媒体调度配置；其中的两个独立值另列为 CPU-003 和 CPU-004：

- `SystemResponsiveness`：目标 `10`，见 CPU-003
- `NetworkThrottlingIndex`：目标 `0xFFFFFFFF`，见 CPU-004

### Windows 原理

`Multimedia\SystemProfile` 是 Windows Multimedia Class Scheduler Service（MMCSS）使用的系统级配置区域之一。它参与多媒体任务与普通后台任务之间的资源调度，不能理解为单独的 CPU 超频或显卡驱动开关。

### 修改目的

脚本通过调整该路径下的具体 DWORD，尝试改变游戏、音频和其他实时交互任务的调度环境。真正的效果取决于具体值、任务类别、Windows 版本和应用是否使用相应的调度机制。

### 默认行为与适用环境

Windows 会使用系统默认的 MMCSS 策略；默认值应在目标机器上实际读取确认。适合在游戏、音频、视频或实时交互场景中进行有基线的测试，不适合把整组参数无差别地视为所有用户的通用优化。

### 潜在影响

可能改变后台任务获得的处理器时间、网络线程调度或多媒体任务的稳定性。错误或不适配的值可能导致后台任务延迟、应用兼容性问题，且不一定带来帧率收益。

### 验证与恢复

当前脚本没有对 `SystemProfile` 下所有写入值进行统一回读，也没有自动备份这组配置。验证时应分别读取 CPU-003、CPU-004 和 CPU-005 中列出的具体值；恢复时必须将执行前记录的每个原值逐项写回。

## CPU-003 SystemResponsiveness

### 执行位置

- 源码：`tweakbyjie.ps1:794`
- 入口：主菜单 `1` → 核心游戏优化 `1`
- 写入函数：`Set-RegDword`

### 注册表位置与目标值

```text
路径：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile
值名：SystemResponsiveness
类型：REG_DWORD
脚本目标值：10（十进制）
```

### Windows 原理

该值参与 MMCSS 对系统响应性和后台任务资源分配的策略判断。它影响的是调度策略的一部分，不是对所有进程设置固定 CPU 占用比例，也不是直接保证游戏获得某个百分比的处理器时间。

### 修改目的

脚本将目标值设为 `10`，意图在多媒体或游戏前台运行时调整后台任务资源分配，使交互任务保持更高的响应性。

### 默认行为与适用环境

默认值由 Windows 版本和系统策略决定，应在修改前读取。只有在游戏、音视频或实时交互场景中完成前后测试后，才适合评估该调整；办公、多任务、编译和后台服务负载较重的用户需要谨慎。

### 潜在影响

后台任务可能获得不同的调度份额，表现为同步、下载、编译、压缩或后台渲染速度变化。对游戏帧率和延迟的收益并不保证，必须结合实际帧时间、1% Low、输入延迟和后台任务影响判断。

### 验证方法

当前脚本写入后没有调用专门的 `Verify-RegDword` 验证该值。可只读检查：

```powershell
Get-ItemPropertyValue `
  'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' `
  'SystemResponsiveness'
```

### 恢复方式

修改前读取并保存原始 `REG_DWORD`；恢复时写回原值。当前脚本没有自动备份或恢复 CPU-003。

## CPU-004 NetworkThrottlingIndex

### 执行位置

- 源码：`tweakbyjie.ps1:793`
- 入口：主菜单 `1` → 核心游戏优化 `1`
- 写入函数：`Set-RegDword`

### 注册表位置与目标值

```text
路径：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile
值名：NetworkThrottlingIndex
类型：REG_DWORD
脚本目标值：0xFFFFFFFF
```

### Windows 原理

该值位于 MMCSS 的网络节流相关配置中。脚本使用 `0xFFFFFFFF` 作为目标值，意图关闭或绕过 Windows 的网络节流限制。它不等同于提升带宽，也不能替代网卡驱动、路由器、运营商或应用协议层面的调优。

### 修改目的

在对网络延迟敏感的游戏或实时通信场景中，尝试减少系统网络节流对多媒体任务的影响。

### 默认行为与适用环境

Windows 默认行为应以目标系统当前值和版本实现为准。适用性需要通过稳定的网络延迟、抖动、丢包和 CPU 占用测试评估；普通办公、下载或带宽受限环境不应仅凭“关闭节流”就预期收益。

### 潜在影响

可能改变网络线程与多媒体任务的调度方式，增加高负载下的 CPU 调度压力；也可能没有可测的网络延迟改善。网络稳定性、吞吐量和游戏服务器路径仍是主要因素。

### 验证方法

当前脚本没有对该值进行回读验证。可只读检查并确认类型和值：

```powershell
Get-ItemProperty `
  'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile' `
  -Name 'NetworkThrottlingIndex' |
  Select-Object NetworkThrottlingIndex
```

### 恢复方式

修改前记录原始 `REG_DWORD`，恢复时写回原值。当前脚本没有自动备份或恢复 CPU-004；不要把 `0xFFFFFFFF` 当作所有系统的默认值。

## CPU-005 Tasks\\Games

### 执行位置

- 路径定义：`tweakbyjie.ps1:800`
- 写入位置：`tweakbyjie.ps1:801-807`
- 入口：主菜单 `1` → 核心游戏优化 `1`

### 注册表位置与目标值

```text
路径：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games
```

| 值名 | 类型 | 脚本目标值 |
| --- | --- | --- |
| `Affinity` | `REG_DWORD` | `0` |
| `Background Only` | `REG_SZ` | `False` |
| `Clock Rate` | `REG_DWORD` | `10000` |
| `GPU Priority` | `REG_DWORD` | `8` |
| `Priority` | `REG_DWORD` | `6` |
| `Scheduling Category` | `REG_SZ` | `High` |
| `SFIO Priority` | `REG_SZ` | `High` |

### Windows 原理

`Tasks\Games` 是 MMCSS 的游戏任务类别配置。相关值用于描述该类别任务的调度、优先级、I/O 和后台属性。它不是显卡硬件时钟控制项；特别是 `Clock Rate=10000` 不能解释成“把 GPU 时钟设置为最高”。

### 修改目的

脚本为游戏任务类别设置一组偏向前台和高优先级处理的目标属性，意图改善游戏线程、I/O 和多媒体任务的调度环境。

### 默认行为与适用环境

默认配置由 Windows 和系统版本提供，目标系统可能已经被 OEM、驱动或其他工具调整。适合在明确以游戏为主、并能进行重复测试的系统上评估；不应假定所有使用 MMCSS 的音视频或后台任务都适合使用同一组值。

### 潜在影响

高优先级任务可能挤占后台任务的处理器或 I/O 资源，导致同步、更新、录制、编译或其他多任务行为改变。对平均 FPS、1% Low 和输入延迟的影响必须实测；兼容性也可能因 Windows 版本和应用实现不同而变化。

### 验证方法

当前脚本没有对 `Tasks\Games` 下的七个值进行回读验证。可通过只读命令查看实际值：

```powershell
Get-ItemProperty `
  'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile\Tasks\Games'
```

应逐项核对值名、类型和目标值，而不是只确认注册表路径存在。

### 恢复方式

修改前必须记录该路径下七个值的原始存在状态、类型和值；恢复时按记录逐项写回，原本不存在的值应删除。当前脚本没有为 CPU-005 提供自动备份、删除缺失值或恢复入口。

## CPU 类核对结论

- CPU-001 至 CPU-005 均已与 `tweakbyjie.ps1` 当前源码逐项对应。
- `Multimedia SystemProfile` 是配置路径/类别；`SystemResponsiveness`、`NetworkThrottlingIndex` 和 `Tasks\Games` 是其中的独立执行项目，不能合并后遗漏。
- 当前脚本的写入成功提示不等于所有值都已回读验证；CPU-001 之外的这些项目仍存在验证和备份恢复缺口。
- 实际是否改善性能，应使用可重复的游戏和系统负载测试验证，不能仅凭注册表目标值判断。
