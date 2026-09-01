---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# Windows 睡眠、休眠与混合睡眠详解

> **分类**：系统知识 · 电源管理
>
> **适用场景**：了解 Windows 睡眠 / 休眠 / 混合睡眠三种电源状态的原理与取舍，开启默认隐藏的休眠选项，以及笔记本电源按钮与合盖行为的推荐设置。
>
> 本文技术内容已对照微软官方文档（Microsoft Support / Microsoft Learn）交叉验证，核查记录见文末。

---

## 一、睡眠与休眠的区别

| 对比项 | 睡眠（Sleep） | 休眠（Hibernate） |
| --- | --- | --- |
| 恢复速度 | 快速恢复（秒级） | 较慢（慢于睡眠，快于冷开机） |
| 状态保存位置 | 内存 RAM（需持续少量供电） | 磁盘休眠文件（无需电量） |
| 功耗 | 低 | 近乎为零（几乎等于关机） |
| 断电后果 | 可能丢失数据（开启混合睡眠除外） | 不会丢失数据 |
| 适用场景 | 短时间离开 | 长时间离开（如过夜）且不想关闭程序 |

补充说明：

- 笔记本**默认合盖操作是「睡眠」**，可在控制面板或电源计划中更改；
- 担心睡眠状态持续耗电的笔记本（尤其长时间不插电时），休眠是更稳妥的选择；
- Windows 会在电量过低时自动保存工作并关机，因此睡眠中电池耗尽通常也有保护，但不应依赖该机制。

## 二、开启休眠设置项

部分系统默认隐藏休眠选项，可用以下任一方式开启（均需重启后生效）：

**方式一：管理员命令提示符（推荐）**

```bat
powercfg /hibernate on
```

> 关闭则为 `powercfg /hibernate off`。官方推荐使用该命令而非直接改注册表，因为命令会同时管理休眠文件 `hiberfil.sys`（禁用时删除、启用时重建）。

**方式二：注册表**

1. `Win + R` 输入 `regedit` 打开注册表编辑器；
2. 定位到：

   ```text
   HKLM\SYSTEM\CurrentControlSet\Control\Power
   ```

3. 找到 `HibernateEnabled`（DWORD），数值改为 `1`（十六进制），保存后重启。

> 两种方式等效——`powercfg /hibernate on` 本质上就是把该注册表值设为 1。

## 三、混合睡眠（谨慎开启）

**原理**：混合睡眠 = 睡眠 + 休眠的组合——既维持内存供电保持秒级唤醒，又同时把状态写入磁盘休眠文件。**即使断电，也不会丢失数据**（来电/开机后从休眠文件恢复）。

开启位置：**控制面板 → 电源选项 → 更改计划设置 → 更改高级电源设置 → 睡眠**：

- **允许混合睡眠**：启用；
- **在此时间后休眠**：睡眠状态下无操作多长时间后，自动转入休眠。

⚠️ **注意**：本文**不建议**开启混合睡眠——部分系统上的蓝屏代码 `DRIVER_POWER_STATE_FAILURE`（0x9F）与该功能开启后的电源状态转换有关。此外官方文档表明混合睡眠主要面向**台式机**设计，多数笔记本的电源计划中本就不提供该选项。

> 若你的系统已出现 0x9F 蓝屏：该蓝屏码表示驱动在电源状态转换（睡眠/休眠挂起与恢复）中处于无效状态或超时，除检查混合睡眠设置外，更常见的原因是某个设备驱动过旧或有缺陷，可先在设备管理器中更新驱动排查。

## 四、笔记本推荐电源设置

在「控制面板 → 电源选项 → 选择电源按钮的功能」中（建议同时**关闭快速启动**）：

| 操作 | 推荐设置 |
| --- | --- |
| 按电源按钮时 | 关机 |
| 按睡眠按钮时 | 睡眠 |
| 合上盖子时 | 休眠 |

这样兼顾三点：电源键直接完整关机；短离开用睡眠秒回；合盖（日常携带场景）用休眠，既不耗电又保留全部工作现场。

> 关于**快速启动**：它基于休眠机制（关机时把系统内核状态存入休眠文件），偶尔会带来驱动状态异常、双系统磁盘锁定、更新未完全生效等问题，故有维护需求的用户常选择关闭；此为使用习惯建议，非必改项。

---

## 事实核查记录

本文关键声明已对照微软官方文档核实：

| 声明 | 核查结果 |
| --- | --- |
| 睡眠：状态保存在内存、功耗极低、秒级恢复 | ✅ 属实（Microsoft Support：Sleep uses very little power, starts up faster, instantly back to where you left off） |
| 睡眠状态断电可能丢失数据 | ✅ 属实（官方混合睡眠说明反证：断电后需从休眠文件恢复工作；KB920730 亦警告混合睡眠开启时禁用休眠可能因断电丢数据） |
| 休眠：状态存入磁盘、功耗低于睡眠、恢复慢于睡眠、适合长时间离开 | ✅ 属实（Microsoft Support：Hibernate uses less power than sleep... though not as fast as sleep; designed for laptops / extended period） |
| 笔记本默认合盖/按电源键 = 睡眠 | ✅ 属实（Microsoft Support 原文直接确认） |
| `powercfg /hibernate on` 开启休眠 | ✅ 属实（Microsoft Learn 官方文档命令） |
| 注册表 `HKLM\SYSTEM\CurrentControlSet\Control\Power\HibernateEnabled` = 1 开启休眠 | ✅ 属实（该键即 powercfg 命令实际写入的值；社区文档广泛印证两种方式等效） |
| 混合睡眠 = 睡眠+休眠组合，断电不丢数据 | ✅ 属实（Microsoft Support：混合睡眠为睡眠与休眠的混合，断电后可从休眠文件恢复工作） |
| 混合睡眠主要面向台式机 | ✅ 属实（Microsoft Support：mainly for desktop PCs）——多数笔记本不提供该选项，为本文补充说明 |
| 蓝屏 DRIVER_POWER_STATE_FAILURE（0x9F）与混合睡眠开启有关 | ⚠️ 部分属实：0x9F 蓝屏码真实存在，微软官方调试文档确认其发生于电源状态转换（睡眠/休眠挂起与恢复）中驱动超时或状态无效；「由混合睡眠开启导致」属个案经验观察，实际取决于具体驱动，非必然因果 |
| 电源按钮 / 睡眠按钮 / 合盖动作可自定义 | ✅ 属实（控制面板电源选项标准功能） |
| 关闭快速启动 | 💡 属使用习惯建议：快速启动基于休眠机制，偶发驱动状态异常、双系统磁盘锁定等问题是社区常见关闭理由，非事实性声明 |

**参考来源：**

- [Microsoft Support — Shut down, sleep, or hibernate your PC](https://support.microsoft.com/en-us/windows/experience/power-battery/shut-down-sleep-or-hibernate-your-pc)
- [Microsoft Learn — Powercfg command-line options](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)
- [Microsoft Learn — How to disable and re-enable hibernation（KB920730）](https://learn.microsoft.com/en-us/troubleshoot/windows-client/setup-upgrade-and-drivers/disable-and-re-enable-hibernation)
- [Microsoft Learn — Bug Check 0x9F: DRIVER_POWER_STATE_FAILURE](https://learn.microsoft.com/en-us/windows-hardware/drivers/debugger/bug-check-0x9f--driver-power-state-failure)
