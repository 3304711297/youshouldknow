# 存储与 NVMe 原理

## 一、NVMe 与传统存储接口

NVMe 是针对 PCIe 固态硬盘设计的协议，相比传统 SATA AHCI，具有更低的协议开销和更高的并发能力。

## 二、Windows 存储栈

性能不仅取决于 SSD 本身，还受到：

- 主板 PCIe 通道与带宽分配
- 固件与驱动版本
- 文件系统（NTFS）与簇/短文件名行为
- 电源策略与链路节能（NVMe/PCIe 节能状态）
- 队列管理与后台任务（如索引、更新、BITS）

共同影响。

## 三、优化原则

存储优化应该关注：

- 保持 TRIM 正常工作
- 确认写入缓存策略与断电保护取舍
- 避免无意义的后台占用与频繁小文件操作
- 根据硬件（TLC/QLC、是否带 DRAM 缓存、散热）与工作负载调整

## 四、实操验证：TRIM 与写入缓存怎么查

### TRIM

```powershell
# 全局查询（脚本当前验证点）
fsutil behavior query DisableDeleteNotify

# 逐卷视角（更贴近实际，脚本当前未做逐卷验证）
fsutil behavior query DisableDeleteNotify C:
```

`DisableDeleteNotify=0` 表示系统允许向盘发送 TRIM；但是否对每块盘真正生效，还需结合盘固件、驱动与文件系统。脚本 `fsutil behavior set DisableDeleteNotify 0` 的验证仅覆盖全局，不代表每卷已核验，也没有按原策略自动恢复。

### 写入缓存策略

- 图形路径：设备管理器 → 磁盘驱动器 → 选中盘 → 属性 → 策略 → “启用设备上的写入缓存” / “关闭 Windows 写入高速缓存缓冲区刷新”。
- 取舍：启用可提升突发写入与小文件性能，但异常断电时丢失风险更高；带断电保护的企业/高端盘与普通消费盘策略不同。
- 当前 `tweakbyjie` 没有直接修改写入缓存的执行项，本文属于知识/检查范围，不计为脚本覆盖。

## 五、与 tweakbyjie 的实际对应关系

当前脚本中的存储相关执行项并不等于“写入缓存优化”，应按项目区分：

| 项目 | 脚本入口与实际行为 | 验证/恢复边界 |
| --- | --- | --- |
| NTFS 8.3 | 主菜单 `1` → 系统行为 `2`，写入 `HKLM\SYSTEM\CurrentControlSet\Control\FileSystem\NtfsDisable8dot3NameCreation=1` | 当前没有专门回读、原值备份或恢复入口 |
| TRIM | 主菜单 `1` → 系统行为 `2`，执行 `fsutil behavior set DisableDeleteNotify 0` | 脚本查询全局 `DisableDeleteNotify=0`；未做每卷独立验证，也没有按原策略自动恢复 |
| BITS | 主菜单 `6` 服务优化，把 BITS 启动类型设为 `Manual` | 与目标服务一起保存 `service-backup.json`，可通过 `6 → 2` 恢复原启动类型；不恢复原运行状态 |
| Native NVMe Driver | 主菜单 `8`，按版本和硬件条件管理 NVMe Feature/SafeBoot/驱动配置 | 有 NVMe 专用快照、失败回滚和重启后驱动状态检查；这不是写入缓存设置 |
| 写入缓存 | 当前脚本未发现实际写入、验证或恢复命令 | 仅属于知识/检查范围，不计为脚本执行项 |

脚本没有直接修改 SSD/NVMe 写入缓存策略，也没有对虚拟内存或页面文件执行设置。具体编号与脚本边界见 [全量逐项执行参考](../项目导航/tweakbyjie全量执行参考.md) 与 [优化项目映射](../项目导航/tweakbyjie-optimization-mapping.md)。

## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-21）。

| 声明 | 核查结果 |
| --- | --- |
| NTFS 8.3 写入 NtfsDisable8dot3NameCreation=1，无回读/备份/恢复 | ✅ 属实：STORAGE-001 与 Registry.ps1 一致 |
| TRIM 执行 fsutil set DisableDeleteNotify 0，仅全局查询验证、无逐卷核验与原策略恢复 | ✅ 属实：STORAGE-002 与源码一致 |
| BITS 经 Part 6 设为 Manual，有 service-backup.json 可恢复启动类型 | ✅ 属实：STORAGE-003 与 Backup.Service.ps1 一致 |
| Native NVMe（主菜单 8）有专用快照、失败回滚与状态检查 | ✅ 属实：STORAGE-004 与 Backup.Nvme.ps1 一致 |
| 写入缓存策略无脚本执行项 | ✅ 属实：STORAGE-005 不计为执行覆盖 |
| fsutil 逐卷查询（DisableDeleteNotify C:）语法 | ✅ 属实：fsutil 支持按卷参数（微软文档行为） |
