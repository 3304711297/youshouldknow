---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# tweakbyjie 关联说明

`tweakbyjie` 是执行层项目，负责将经过验证的 Windows 优化方案自动化执行。

`youshouldknow` 是知识层项目，负责解释优化背后的原理、适用环境和注意事项。

## 两个项目关系

| 项目 | 定位 |
|---|---|
| tweakbyjie | 自动化执行工具 |
| youshouldknow | 原理说明与知识库 |

## 推荐阅读方式

1. 先在 `youshouldknow` 了解 Windows 底层机制。
2. 根据硬件和使用场景判断是否需要调整。
3. 再使用 `tweakbyjie` 执行对应优化。

## 优化分类

- CPU 调度与系统响应
- GPU 图形管线
- 内存管理
- SSD/NVMe 存储
- 网络通信
- 游戏相关优化
- 电源管理

## 与 tweakbyjie 模块化结构的对应

`tweakbyjie` 模块化已完成：`tweakbyjie.ps1` 为 Loader（含 `-RunModule` 非交互入口），全部功能拆至 `Modules/`：

| 模块 | 职责 | 说明 |
|---|---|---|
| `Common.ps1` | 通用注册表/BCD/验证/重启/电源计划去重 | `Set-Reg*`/`Invoke-BcdEdit`/`Verify-*`/`Invoke-PowerPlanDedupe` |
| `Backup.Mpo/Registry/Bcd/Service/SecurityMitigation/Nvme/Defender/Vbs/GameQos` | 备份闭环 | 各自的 `Test/Ensure/Restore` 三元组与写后回读校验 |
| `Registry.ps1` | Part 1 编排 | `Invoke-RegistryModule`（核心游戏/系统行为/CPU 缓解） |
| `Nvme.ps1` | Part 8 编排 | `Invoke-NvmeModule`（备份逻辑在 `Backup.Nvme.ps1`） |
| `Virtualization.ps1` | Part 9/10 编排 | `Invoke-DeviceGuardModule`/`Invoke-VbsModule` |
| `Defender.ps1` | Part 5 编排 | `Invoke-DefenderModule`（策略快照见 `Backup.Defender.ps1`） |
| `GameQos.ps1` | Part 12 编排 | `Invoke-GameQosModule`（竞技游戏 DSCP 46 QoS，备份在 `Backup.GameQos.ps1`） |
| `Adapters.ps1` | 适配层 | 网络适配器相关的辅助逻辑 |
| `Menu.ps1` | 菜单调度与分发 | `Show-TweakMenu`（菜单 0–12 共 12 项：1–12 对应 12 个功能模块，12 为 GameQos；支持 `-RunModule` 非交互队列） |

本文档在描述执行位置时，已从“`tweakbyjie.ps1:行号`”改为“`Modules/函数名`”定位，避免行号漂移。建议按 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md` 查看最新模块清单，再对应到下方映射表与全量参考。

## 原则

优化不是简单地关闭越多功能越好，而是在性能、延迟、稳定性之间寻找适合当前设备的配置。

## 事实核查记录

核验基准：tweakbyjie 仓库源码（2026-08-29 对照 `b905950` 首核；2026-09-12 重核：对照 HEAD `5fce57f` 逐项复核，GameQos（菜单 12）与 Adapters 纳入清单，基线随版本演进不再钉死）。

| 声明 | 核查结果 |
| --- | --- |
| tweakbyjie 采用 Loader + `Modules/` 模块化结构 | ✅ 属实（2026-09-12 对照 5fce57f 复核）：Loader 现为 180 行，点源 22 项（21 个 Modules/*.ps1 + 既有清单口径）；08-29 基线的“162 行、19 个文件”与 08-21 基线已随版本演进过时 |
| 模块清单构成 | ✅ 已更新（2026-09-12 对照 5fce57f 重核）：现为 Common + Adapters + 9 个 `Backup.*`（Mpo/Registry/Bcd/Service/SecurityMitigation/Nvme/Defender/Vbs/GameQos）+ Bcd/Defender/GameQos/Mpo/Nvme/Power/Registry/Service/Virtualization 九个执行模块 + Menu；08-29 基线缺 GameQos 项 |
| 执行位置采用 `Modules/函数名` 定位而非行号 | ✅ 属实：映射表与执行参考均已迁移；2026-08-25 校准后映射表中 Part N 级 `Modules/Menu.ps1` 引用已替换为实际业务模块 |
| `Menu.ps1` 菜单项数 | ✅ 属实（2026-09-12 对照 5fce57f 复核）：菜单选项 0–12，1–12 对应 12 个功能模块函数（原 11 个 + `Invoke-GameQosModule`）；Loader 支持 `-RunModule` 非交互队列（编号 0–12）。08-29 基线的“11 个 Part”已随 GameQos 引入过期 |
