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

`tweakbyjie` 已完成第一阶段模块化（`tweakbyjie.ps1` 为 Loader，功能拆至 `Modules/`）：

| 模块 | 职责 | 说明 |
|---|---|---|
| `Common.ps1` | 通用注册表/BCD/验证/重启 | `Set-Reg*`/`Invoke-BcdEdit`/`Verify-*` |
| `Backup.Mpo/Bcd/Service/SecurityMitigation/Nvme` | 备份闭环 | 各自的 `Test/Ensure/Restore` 三元组 |
| `Menu.ps1` | 菜单调度 | `Show-TweakMenu`（11 个 Part） |

本文档在描述执行位置时，已从“`tweakbyjie.ps1:行号`”改为“`Modules/函数名`”定位，避免行号漂移。建议按 `tweakbyjie/docs/design/CODE-REFACTOR-STATUS.md` 查看最新模块清单，再对应到下方映射表与全量参考。

## 原则

优化不是简单地关闭越多功能越好，而是在性能、延迟、稳定性之间寻找适合当前设备的配置。
