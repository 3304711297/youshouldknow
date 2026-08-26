# GPU 调度与显示管线

## 对应范围

> 已与 `tweakbyjie` 模块化结构同步：执行逻辑现位于 `Modules/Menu.ps1` 与 `Modules/Common.ps1`（通用写入/验证）、`Modules/Backup.*.ps1`（备份闭环）；此处不再使用 `tweakbyjie.ps1:行号` 定位，以 `Modules/函数名` 为准。详见 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md`。


本章节对应 `tweakbyjie/tweakbyjie.ps1` 当前源码中的两个 GPU/显示相关执行项目：

- GPU-001：核心游戏优化中的 HAGS
- GPU-002：Part 11 的 MPO 独立管理

脚本没有直接修改某个 DirectX 版本、游戏引擎或显卡硬件时钟寄存器；DirectX 在本文中作为图形管线和兼容性背景说明。

## GPU-001 HAGS（Hardware-Accelerated GPU Scheduling）

### Windows 原理

HAGS 是 Windows 提供的硬件加速 GPU 调度模式。启用后，部分 GPU 调度工作由更接近硬件的调度路径处理，实际收益和行为取决于 Windows 版本、WDDM、显卡架构、驱动版本、游戏引擎以及显示链路。它不是显卡超频，也不会保证所有应用降低延迟。

### tweakbyjie 执行位置

- 源码：`Modules/Registry.ps1`+ `Modules/Common.ps1/Set-RegDword`
- 入口：主菜单 `1` → 核心游戏优化 `1`
- 写入函数：`Set-RegDword`

```text
路径：HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers
值名：HwSchMode
类型：REG_DWORD
脚本目标值：2
```

`HwSchMode=2` 表示请求启用 HAGS；最终是否实际启用仍受硬件、驱动和系统支持情况影响。

### 修改目的

尝试启用 Windows 的硬件加速 GPU 调度，观察其对 GPU 队列、帧时间稳定性和端到端延迟的影响。

### 适用环境

适合在支持 HAGS 的 Windows 系统、显卡和驱动上进行有基线的 A/B 测试。对于旧硬件、驱动不支持、专业图形软件或依赖特定驱动调度行为的系统，应先确认兼容性，不要把 `HwSchMode=2` 当成普适优化。

### 潜在影响

可能改善部分游戏的帧时间或调度延迟，也可能无明显收益，甚至引入卡顿、驱动重置、录屏/覆盖层兼容性问题。平均 FPS 不能单独证明有效，应同时观察 1% Low、帧时间、输入延迟、GPU 利用率、录屏和多显示器行为。

### 验证方法

脚本在 `Modules/Common.ps1/Verify-RegDword` 使用 `Verify-RegDword` 回读 `HwSchMode=2`。这只证明注册表配置层写入成功，不等于驱动已经采用 HAGS 运行时路径。可进一步检查 Windows 图形设置、`dxdiag` 和实际游戏测试结果：

```powershell
Get-ItemPropertyValue `
  'HKLM:\SYSTEM\CurrentControlSet\Control\GraphicsDrivers' `
  'HwSchMode'
```

修改后通常需要重启，再进行相同场景、相同驱动和相同显示设置的对照测试。

### 恢复方式

修改前应读取并记录原始值及其是否存在。当前核心游戏优化路径没有为 `HwSchMode` 建立独立备份文件或自动恢复入口；恢复时应将原始 `REG_DWORD` 写回，原本不存在时删除该值。若要恢复系统默认，不能简单假定所有系统的默认值都是同一个数字。

## GPU-002 MPO（Multi-Plane Overlay）

### Windows 原理

MPO 是 Windows/DWM 的多平面叠加显示合成路径，可让视频或其他内容在独立硬件平面上合成，从而减少部分主合成负担。它的收益与行为取决于 Windows、显卡驱动、显示器、刷新率、VRR/HDR 设置和应用。

MPO 相关异常可能表现为闪屏、切屏黑屏、副屏冻结、Chromium 残影、视频卡顿或帧时间异常。下面的注册表值属于未公开的社区排障配置，不是微软或显卡厂商保证长期稳定的 API。

### tweakbyjie 执行位置

- 源码：`Modules/Mpo.ps1`（`Invoke-MpoModule`）+ `Modules/Backup.Mpo.ps1`
- 入口：主菜单 `11. MPO 设置管理`
- 修改前调用 `Ensure-MpoBackup`，首次保存脚本目录下的 `mpo-backup.json`
- 修改后需重启；`11 → 4` 用于恢复

脚本管理以下四个值：

| 注册表路径 | 值名 | 类型/目标值 | 作用或边界 |
| --- | --- | --- | --- |
| `HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers` | `DisableMPO` | `REG_DWORD 1` | 方案 A 的旧式 MPO 禁用尝试；部分新系统可能无效 |
| `HKLM\SOFTWARE\Microsoft\Windows\Dwm` | `OverlayTestMode` | `REG_DWORD 5` | 方案 A 的 DWM 层禁用尝试 |
| `HKLM\SYSTEM\CurrentControlSet\Control\GraphicsDrivers` | `DisableOverlays` | `REG_DWORD 1` | 方案 B 的更激进叠加层禁用尝试 |
| `HKLM\SOFTWARE\Microsoft\Windows\Dwm` | `OverlayMinFPS` | `REG_DWORD 0` | 方案 C：尝试避免低帧率时撤下 MPO |

### 修改目的与方案

脚本把四个值组织成互斥的排障方案，而不是默认把 MPO 视为必须关闭的优化：

- **方案 A（11 → 1）**：写入 `OverlayTestMode=5` 和 `DisableMPO=1`，清除方案 B/C 值。适合先排查多屏闪烁、切屏黑屏、Chromium 残影等 MPO 症状。
- **方案 B（11 → 2）**：写入 `DisableOverlays=1`，更激进；仅在方案 A 无效时测试，可能影响个别 DX12 游戏或其他叠加层。
- **方案 C（11 → 3）**：写入 `OverlayMinFPS=0`，不直接禁用 MPO，社区常用于排查 G-Sync/FreeSync 视频播放卡顿；不保证有效。
- **查看（11 → 0）**：只读显示四个值和 `dxdiag` 辅助检查方法。
- **还原（11 → 4）**：优先恢复首次修改前的备份状态。

### 适用环境

只应在出现与 MPO 可能相关的具体症状时，逐方案、可回滚地排障。没有闪屏、黑屏、视频卡顿或副屏问题时，不应为了追求性能而盲目禁用 MPO。方案选择还要考虑窗口化游戏 VRR、HDR、录屏、浏览器、Steam/Discord 覆盖层和 DX12 应用。

### 潜在影响

禁用 MPO 可能增加 DWM 合成负担、影响窗口化游戏 VRR、视频呈现、HDR 或覆盖层；方案 B 对部分 DX12 游戏风险更高。方案 C 通常比禁用方案保守，但实际效果和副作用仍依赖系统与驱动。MPO 选项不是直接提升 GPU 时钟或保证 FPS 的功能。

### 验证方法

注册表层面可通过 `11 → 0` 查看当前四个值。重启后可用 `dxdiag` 保存报告并搜索 `MPO` 作为辅助信号；不同 Windows 和驱动版本的输出格式可能不同，MPO 条目消失或 `MaxPlanes=0` 不能证明所有应用的运行时行为。最终需要结合浏览器/视频、多显示器、窗口化游戏、DX12、HDR、录屏及 Steam/Discord 等覆盖层进行实测。方案 C 不禁用 MPO，不能用“MaxPlanes 消失”判断方案 C 已生效。

### 恢复方式

首次执行方案 A/B/C 前，脚本会把四个受管理值的存在状态、类型和值保存到 `mpo-backup.json`，已有有效备份不会覆盖。执行 `11 → 4` 时按备份逐项写回；备份中原本不存在的值会被删除。没有备份时，脚本只能删除受管理值并恢复系统默认，不能恢复此前的自定义值。备份损坏或无法读取时，脚本会阻止新的 MPO 修改。

## DirectX 与图形管线边界

游戏画面通常经历：

```text
CPU 游戏逻辑 → DirectX → GPU 队列 → 显示合成 → 显示器刷新
```

DirectX、GPU 队列和 MPO/HAGS 之间存在运行时关系，但当前 `tweakbyjie.ps1` 没有直接修改 DirectX 版本、渲染 API、游戏引擎配置或 GPU 硬件时钟。平均 FPS 不能完全反映体验，应同时关注帧时间波动、1% Low、GPU 使用率、CPU 瓶颈、输入延迟和稳定性。

## GPU 类核对结论

- GPU-001 和 GPU-002 已与当前脚本的 HAGS、MPO 执行入口逐项对应。
- HAGS 是核心优化中的单个 `HwSchMode` 写入，当前有配置层回读，但没有独立自动备份/恢复。
- MPO 是独立排障模块，包含四个受管理值、互斥方案、备份、恢复和辅助验证；它不应与核心优化中的 HAGS 混为一项。
- 当前脚本没有直接执行 DirectX 优化项，因此 DirectX 相关内容属于知识背景，不计作遗漏的脚本执行项。
## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-21（本次未重新核验））。

| 声明 | 核查结果 |
| --- | --- |
| GPU-001 写入 HwSchMode=2，经 Verify-RegDword 回读，需重启 | ✅ 属实：Modules/Registry.ps1 + Common.ps1 |
| GPU-002 管理四个 MPO 值（DisableMPO/OverlayTestMode/DisableOverlays/OverlayMinFPS），方案 A/B/C 互斥 | ✅ 属实：与 Menu.ps1（Part 11）及 mpoManagedValues 定义一致 |
| MPO 首次修改前快照 mpo-backup.json，已有备份不覆盖，11→4 恢复，备份损坏时阻止修改 | ✅ 属实：Backup.Mpo.ps1 的 Ensure/Restore 逻辑一致（含写后回读校验） |
| HAGS 无独立自动备份/恢复 | ✅ 属实：核心路径仅写入+回读 |
| HAGS 执行位置标注为 Modules/Menu.ps1（Part 1） | ❌ 勘误并已更新：已随 Part 1 迁至 Modules/Registry.ps1 |
