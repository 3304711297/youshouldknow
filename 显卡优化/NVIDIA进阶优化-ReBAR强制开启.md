# NVIDIA 进阶优化（一）：用 Profile Inspector 强制开启 ReBAR

> **分类**：显卡优化 · NVIDIA
>
> **适用场景**：RTX 30 系及更新显卡，想让未进 NVIDIA 白名单的游戏也用上 Resizable BAR（可调整大小 BAR），榨取额外性能。
>
> **需要工具**：[NVIDIA Profile Inspector](https://profileinspector.io/download/)（第三方免费绿色工具，解锁驱动里隐藏的配置项）。
>
> 本文已对照社区多方资料核实，其中一处流传说法经核实需纠正，核查记录见文末。

---

## 一、ReBAR 是什么，开不开

**Resizable BAR** 是一项 PCIe 特性：传统模式下 CPU 一次只能访问显卡显存中 256MB 的窗口，ReBAR 让 CPU 可以直接访问**全部显存**，减少数据搬运次数、提高 CPU 与 GPU 协同效率。部分游戏帧数可提升约 10%，最低帧流畅度改善更明显。

但 NVIDIA 驱动**默认只对白名单游戏启用** ReBAR，黑名单游戏强制禁用，其余大量游戏处于「没开」状态——这就是用 Profile Inspector 手动改的意义。

**收益与风险**（先看再动手）：

- 大部分现代游戏有性能提升；**部分网游 / 竞技游戏反而性能下降**；
- 建议的前提条件：**显存留有余量**、**CPU 为高端且占用率不高**，否则可能只有负提升；
- 逐游戏测试，改一个测一个，别无脑全局开。

## 二、第一步：BIOS 前置设置

ReBAR 生效的前提是 **UEFI 引导 + 关闭 CSM**。各主板开启路径：

| 主板 | 路径 |
| --- | --- |
| 华硕 | `Advanced` → `PCI Subsystem Settings` → `Re-Size BAR Support` = `Enabled`；同时 `Boot` → `CSM` = `Disabled` |
| 微星 | `Settings` → `高级` → `PCIe` → `PCIe 子系统设置` → `Above 4G memory` 与 `Re-Size BAR Support` = `允许` |
| 技嘉 | `设置` → `Re-Size BAR Support` = `启用` |
| 华擎 | `Advanced` → `PCI Subsystem` → `Above 4G Decoding` = `Enabled`，`Re-Size BAR Support` = `Auto/Enabled` |

> ⚠️ **纠正一个流传说法：开启 ReBAR 不需要关闭安全启动。**
> 正确要求是：**UEFI 引导 + CSM 关闭**。以华硕为例，Secure Boot 菜单中把 `OS Type` 设为 `Windows UEFI mode`（即安全启动保持正常开启的 Windows 模式）即可——部分教程把「设置为 Windows UEFI 模式」误传成了「关闭安全启动」。ReBAR 与安全启动不冲突。

## 三、第二步：Profile Inspector 强制开启

1. 运行 `nvidiaProfileInspector.exe`；
2. 顶部**先选中目标游戏的配置档（profile）**（按游戏名搜索；改全局配置档虽一劳永逸，但容易把不兼容的网游也一起开了，不建议）；
3. 在 **`5 - Common`** 分组中找到三项，改为：

   | 设置项 | 值 |
   | --- | --- |
   | `rBAR - Feature` | `Enabled` |
   | `rBAR - Options` | `0x00000001` |
   | `rBAR - SizeLimit` | `0x0000000040000000` |

4. 点右上角 **`Apply changes`** 应用，重启游戏生效。

## 四、验证与回退

- **验证**：NVIDIA 控制面板 → 左下角「系统信息」→ 查看 **Resizable BAR** 状态是否为「是」；游戏内对比修改前后的帧数与 1% low；
- **回退**：把对应游戏 profile 的三项 rBAR 设置改回默认值（或右键 profile → Restore to default），Apply 后重启游戏；
- 注意：**大版本驱动更新可能重置 profile 设置**，升级驱动后记得复查。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| ReBAR 原理：解锁 256MB 访问窗口，让 CPU 访问全部显存 | ✅ 属实：PCIe 特性，官方与媒体均如此描述 |
| NVIDIA 默认按白名单逐游戏启用 ReBAR，可用 Profile Inspector 强制改 | ✅ 属实：Reddit r/nvidia、XDA 等多方证实驱动白/黑名单机制及覆写方法 |
| 三项设置：rBAR-Feature=Enabled / rBAR-Options=0x00000001 / rBAR-SizeLimit=0x0000000040000000 | ✅ 属实：社区流传配方（Steam 指南、GitHub NvStrapsReBar 讨论）与主板厂商教程一致 |
| BIOS 前提：UEFI 引导 + CSM 关闭 + Above 4G Decoding / Re-Size BAR 开启 | ✅ 属实：各主板开启路径为通用做法（新平台通常默认开启） |
| 「必须关闭安全启动」 | ❌ 纠正：ReBAR 不要求关闭安全启动；参考教程原意为 Secure Boot 的 OS Type 设为「Windows UEFI 模式」（保持开启），两者不冲突 |
| 部分游戏（尤其网游）可能负优化；显存余量与 CPU 档次影响收益 | ✅ 属实（负优化案例有据可查）；具体前提条件为社区经验总结 |
| 驱动更新可能重置 profile | ✅ 属实：社区普遍反馈大版本驱动会还原部分 profile 项 |

**参考来源：**

- [Reddit r/nvidia — ReBAR options 各值含义](https://www.reddit.com/r/nvidia/comments/1ikqq6l/can_someone_enlighten_me_on_the_rebar_options/)
- [GitHub NvStrapsReBar — ReBAR settings 最佳取值讨论](https://github.com/terminatorul/NvStrapsReBar/discussions/70)
- [XDA — Nvidia's secretly disabling Resizable BAR in your games](https://www.xda-developers.com/nvidia-disabling-resizable-bar-in-games-even-though-bios-says-its-on/)
- [Wccftech — How to Enable Resizable BAR for Better Gaming](https://wccftech.com/how-to-enable-resizable-bar-for-better-gaming-performance-on-nvidia-gpus/)
- [DCS Forum — NVIDIA Resizable BAR (rBAR) enabling 详解](https://forum.dcs.world/topic/350443-nvidia-resizable-bar-rbar-are-you-enabling-it-right/)
- [NVIDIA Profile Inspector 下载](https://profileinspector.io/download/)
