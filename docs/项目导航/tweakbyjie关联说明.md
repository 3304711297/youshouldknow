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
| `Backup.Mpo/Bcd/Service/SecurityMitigation/Nvme/Defender` | 备份闭环 | 各自的 `Test/Ensure/Restore` 三元组与写后回读校验 |
| `Registry.ps1` | Part 1 编排 | `Invoke-RegistryModule`（核心游戏/系统行为/CPU 缓解） |
| `Nvme.ps1` | Part 8 编排 | `Invoke-NvmeModule`（备份逻辑在 `Backup.Nvme.ps1`） |
| `Virtualization.ps1` | Part 9/10 编排 | `Invoke-DeviceGuardModule`/`Invoke-VbsModule` |
| `Defender.ps1` | Part 5 编排 | `Invoke-DefenderModule`（策略快照见 `Backup.Defender.ps1`） |
| `Menu.ps1` | 菜单调度与分发 | `Show-TweakMenu`（11 个 Part，支持 `-RunModules` 队列） |

本文档在描述执行位置时，已从“`tweakbyjie.ps1:行号`”改为“`Modules/函数名`”定位，避免行号漂移。建议按 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md` 查看最新模块清单，再对应到下方映射表与全量参考。

## 原则

优化不是简单地关闭越多功能越好，而是在性能、延迟、稳定性之间寻找适合当前设备的配置。

## 事实核查记录

核验基准：tweakbyjie 仓库 `main` 分支源码（2026-08-21，模块化收尾提交后）。

| 声明 | 核查结果 |
| --- | --- |
| tweakbyjie 采用 Loader + `Modules/` 模块化结构 | ✅ 属实：Loader 约 127 行，点源 16 个模块文件（由 Coverage Loader 契约自动校验） |
| 模块清单为 Common + 5 个 Backup.* + Menu | ❌ 勘误并已更新：现为 Common + 6 个 `Backup.*`（含 Defender）+ Bcd/Defender/Mpo/Nvme/Power/Registry/Service/Virtualization 八个执行模块 + Menu（共 16 个点源文件） |
| 执行位置采用 `Modules/函数名` 定位而非行号 | ✅ 属实：映射表与执行参考均已迁移；2026-08-25 校准后映射表中 Part N 级 `Modules/Menu.ps1` 引用已替换为实际业务模块 |
| `Menu.ps1` 含 11 个 Part | ✅ 属实：菜单选项 1–11 对应 11 个功能模块函数（由 Coverage 菜单契约自动校验） |
