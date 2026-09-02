---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# CPU 调频与电源管理机制

> **分类**：BIOS 与固件 · CPU 电源选项
>
> **一句话**：SpeedStep/Cool'n'Quiet 是"中层"调频（OS 按 P-state 档位调度），Speed Shift/CPPC 把决策权下放给 CPU 硬件（快一千倍），睿频是在功耗/温度/电流三墙下"能跑多高跑多高"，C-States 是空闲断电休眠——**这四组默认都开着就是最优，本篇可能是整个系列最不需要你修改的选项**。

## 第一层：Intel SpeedStep 与 AMD Cool'n'Quiet

- 原理是 **P-state 档位**：频率和电压被切成离散组合（P0 最高性能，最低档约 800MHz/0.6V，现代 CPU 有十几到几十档），操作系统毫秒级采样负载、在档位间切换。
- 华硕在 Advanced → CPU 配置；微星在 OC → CPU Features；华擎在 Advanced → CPU Configuration。
- **新 AMD 平台已没有 Cool'n'Quiet 选项**——被 CPPC 与 PBO 协同接管，正式退役。
- 验证：任务管理器/HWiNFO64 看频率是否随负载波动（空闲约 700MHz、满载拉满为正常）。
- **误区**：关 SpeedStep 不会提升性能，只会让 CPU 24 小时顶格跑、功耗翻倍；Windows"高性能电源计划"≠关闭 SpeedStep，只是抬高最低 P-state，功能还在跑。

## 第二层：Intel Speed Shift（HWP）与 AMD CPPC

- 把调速决策权从操作系统下放到 CPU 内部的功耗控制单元（PCU）：直接监测指令流水线、缓存命中率、分支预测，**十几微秒内完成切换**（80→5000MHz 级跳变），比 OS 采样调度快约一千倍。
- Intel 需 Win10 1709+ 由系统把决策委托给 CPU；大小核平台另有 Thread Director 硬件调度器（推荐 Win11）。
- AMD CPPC（协同处理器性能控制）Zen3 起默认接管；子选项 **CPPC 首选核心**标记体质最优核心、让单线程任务优先分配（默认开启；手动全核定频超频时可临时关）。
- **与 SpeedStep 是共存关系不是替代**：SpeedStep 搭框架，Speed Shift 做决策；开着反而待机功耗更低。
- 验证：HWiNFO64 看 Speed Shift/HWP 是否 Enabled；点鼠标瞬间频率拉满、松开快速回落即生效。

## 第三层：睿频加速 Turbo Boost / Precision Boost

- 标称最高睿频是理想条件下的瞬时值；CPU 每个瞬间都在问三个问题——温度多少、吃了多少功耗、拉了多少电流，共同决定当前睿频上限（"三座大山：功耗墙、温度墙、电流墙，谁先到谁说了算"）。
- Intel 选项叫 Turbo Boost Technology（Advanced → CPU 配置）；AMD 叫 Core Performance Boost（AMD Overclocking/OC 菜单）。
- **TVB（Thermal Velocity Boost，温度速度加速）**：低温红利——温度越低加成越多。新手最大误区：**TVB 不帮降温，反了——散热好把温度压下来 TVB 才生效**。AMD 没有独立低温开关，Precision Boost 本身整合了温度/电流动态调度。
- **MCE（Multi-Core Enhancement，多核增强）**：主板厂商绕过 Intel 全核降频限制，让全核同步跑到单核最高睿频——高端板默认开、入门板默认关；代价是功耗温度大幅飙升；**想自己设功耗墙必须先关 MCE**。
- 排查"频率上不去"三部曲：HWiNFO 看温度是否撞墙 → 看封装功耗是否卡在 PL（撞功耗墙）→ 都没到还上不去甚至重启，查主板 VRM 供电过热。

## 第四层：C-States 电源状态

- SpeedStep 管频率电压（CPU 还在跑），C-States 管**真正空闲时能关掉多少电路**：C0 活跃 → C1 暂停（纳秒级唤醒）→ C1E 降频降压 → C3 关 PLL → C6 切断核心供电（唤醒约 50~150 纳秒）→ C7+ 刷清共享缓存 → C8/C9/C10 连内存控制器、PCIe 也省电（微秒级唤醒）。
- **"关 C-States 游戏反而变卡"的真相在 Windows 调度器**：调度器靠 C-State 状态判断哪些核心空闲可停车；全关后失去参考、倾向把线程拆散到更多核心，缓存反复重载。
- 大小核（12~14 代）卡顿偏方：关 **Package C-state Limit（封装级 C-state）**，只让核心自己睡——封装级休眠会把 P 核与 E 核绑在一起断电，唤醒速度不一致导致线程在两类核之间疯狂睡醒切换。
- **C1 永远不要关**（最基本的空闲机制，关了待机功耗翻几倍、性能零提升）；音频制作等延迟敏感场景限制到 C3 以下即可，不必全关。
- 验证：HWiNFO64 看 C-State Residency（C6/C7 百分比在积累为正常）。

## 总结

| 层 | Intel | AMD | 建议 |
|---|---|---|---|
| 档位调频 | SpeedStep | Cool'n'Quiet（已退役） | 默认开 |
| 硬件自主调速 | Speed Shift (HWP) | CPPC | 默认开 |
| 睿频加速 | Turbo Boost / TVB | Precision Boost | 默认开，受三墙约束 |
| 空闲休眠 | C-States | C-States | 默认开；卡顿再关 Package C-state |

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」《电脑BIOS选项全科普》旧版合集第 15~18 集，经本地语音转录校对整理；唤醒延迟、毫秒数等口播数字以原视频画面为准：

- [EP15/SpeedStep & Cool'n'Quiet](https://www.bilibili.com/video/BV1sfKf6bEf9/)
- [EP16/Speed Shift & CPPC](https://www.bilibili.com/video/BV1rbTv6RE91/)
- [EP17/睿频加速](https://www.bilibili.com/video/BV1PSTL66EX7/)
- [EP18/C-States](https://www.bilibili.com/video/BV1QeT46JEoM/)
- 相关：[功耗墙、电流墙与 CEP 电流保护](./功耗墙电流墙与CEP电流保护.md)、[AMD PBO 与 Curve Optimizer](./AMD-PBO与CurveOptimizer.md)
