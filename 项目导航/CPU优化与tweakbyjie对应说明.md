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
路径：HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl
值名：Win32PrioritySeparation
类型：REG_DWORD
脚本目标值：38（十进制）= 0x26
```

### Windows 原理

Windows 调度器根据线程优先级、前台/后台状态和量子时间等因素分配处理器时间。`Win32PrioritySeparation` 是系统级调度策略参数，会影响前台程序与后台程序的相对调度行为。它不是简单的“锁定某个程序使用 CPU”，实际效果还会受 Windows 版本、处理器、线程优先级和应用自身行为影响。

### 修改目的

脚本将该值设为十进制 `38`（十六进制 `0x26`），目标是调整前台交互应用和游戏线程的调度策略，优先关注响应性。这里必须区分十进制和十六进制表示，不能把 `38` 误读成十六进制 `0x38`。

### 默认行为与适用环境

Windows 默认值由系统版本、安装方式和现有策略决定，不能只根据一台电脑推断所有系统的默认值。适合在有明确测试基线、重视前台响应或游戏帧时间的环境中评估；不应默认适用于所有办公、服务器或后台任务场景。

### 潜在影响

前台响应可能改善，也可能没有可测收益。后台编译、压缩、同步、渲染或长时间计算任务的调度份额可能变化；不同系统版本和硬件的结果可能不同。应使用平均 FPS、1% Low、帧时间、输入延迟和后台任务完成时间进行前后对比，而不是只看主观感受。

### 验证方法

脚本在 `tweakbyjie.ps1:813` 使用 `Verify-RegDword` 回读并验证目标值 `38`。也可以只读检查：

```powershell
Get-ItemPropertyValue `
  'HKLM:\SYSTEM\CurrentControlSet\Control\PriorityControl' `
  'Win32PrioritySeparation'
```

### 恢复方式

执行前应先读取并记录原值；恢复时将该值写回原来的 `REG_DWORD`。当前脚本没有为 CPU-001 建立独立备份文件，也没有提供自动恢复入口，因此不要在未保存原值的情况下直接执行。

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
