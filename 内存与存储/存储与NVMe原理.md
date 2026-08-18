# 存储与 NVMe 原理

## NVMe 与传统存储接口

NVMe 是针对 PCIe 固态硬盘设计的协议，相比传统 SATA AHCI，具有更低的协议开销和更高的并发能力。

## Windows 存储栈

性能不仅取决于 SSD 本身，还受到：

- 主板 PCIe 通道
- 固件
- 驱动
- 文件系统
- 电源策略
- 队列管理

共同影响。

## 优化原则

存储优化应该关注：

- 保持 TRIM 正常工作
- 确认写入缓存策略
- 避免无意义的后台占用
- 根据硬件情况调整

## 与 tweakbyjie 的实际对应关系

当前脚本中的存储相关执行项并不等于“写入缓存优化”，应按项目区分：

| 项目 | 脚本入口与实际行为 | 验证/恢复边界 |
| --- | --- | --- |
| NTFS 8.3 | 主菜单 `1` → 系统行为 `2`，写入 `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisable8dot3NameCreation=1` | 当前没有专门回读、原值备份或恢复入口 |
| TRIM | 主菜单 `1` → 系统行为 `2`，执行 `fsutil behavior set DisableDeleteNotify 0` | 脚本查询全局 `DisableDeleteNotify=0`；未做每卷独立验证，也没有按原策略自动恢复 |
| BITS | 主菜单 `6` 服务优化，把 BITS 启动类型设为 `Manual` | 与目标服务一起保存 `service-backup.json`，可通过 `6 → 2` 恢复原启动类型；不恢复原运行状态 |
| Native NVMe Driver | 主菜单 `8`，按版本和硬件条件管理 NVMe Feature/SafeBoot/驱动配置 | 有 NVMe 专用快照、失败回滚和重启后驱动状态检查；这不是写入缓存设置 |
| 写入缓存 | 当前脚本未发现实际写入、验证或恢复命令 | 仅属于知识/检查范围，不计为脚本执行项 |

脚本没有直接修改 SSD/NVMe 写入缓存策略，也没有对虚拟内存或页面文件执行设置。具体源码行号和项目编号见 `youshouldknow/项目导航/tweakbyjie-optimization-mapping.md`。
