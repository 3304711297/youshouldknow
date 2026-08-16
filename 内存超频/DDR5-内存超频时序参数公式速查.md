# DDR5 内存超频时序参数公式速查

> **分类**：内存超频 · 时序调优
>
> **适用场景**：DDR5 内存（尤其海力士 A-die 颗粒）手动收紧时序时的起步参数计算。适用于 AM5 平台及支持内存时序调节的机械革命机型等。
>
> **原文出处**：机械革命优化/超频频道（QQ 频道，2025-03-06 发布，原文地址：<https://pd.qq.com/s/8gmjfcol0>）。本文经事实核查后重新整理排版，技术内容已对照 DDR5 领域公认规则及多家超频社区信源交叉验证。

---

## 背景说明

手动收紧内存时序（缩时序）是继频率之后进一步提升内存性能的手段。本文收录一组面向 DDR5 的时序**估算公式**，可根据目标频率快速推算各参数的起步值，再逐项压测调整。

> 📌 **说明**：原文标题为《内存参数公式及TM5报错提示》，其中「TM5 报错提示」部分位于原文配图中，文字内容未包含，故本文未收录。TM5（TestMem5）是社区常用的内存稳定性测试工具，配合 anta777 Extreme 等配置文件使用。
>
> 📌 公式中的「目标频率」指内存等效频率（MT/s），如 DDR5-6000 即取 6000。

## 时序公式速查表（以 DDR5-6000 为例）

| 参数 | 公式 / 规则 | 示例值 @6000 | 备注 |
| --- | --- | --- | --- |
| tCL | 第一时序，越低越好，**只能为偶数** | 30 | DDR5 架构特性，CAS 只有偶数档 |
| tRCD / tRP | tCL + 2～4 | 32～34 | 经验起步值 |
| tRAS | ≥ tCL + tRCD + 2～4 | ≥ 64～66 | 原文注：影响耐温 |
| tCWL | ≤ tCL，相差 0～2 | 28～30 | 写入延迟对齐 |
| tFAW | tRRD_S × 4 | 32 | 四激活窗口规则 |
| tREFI | 目标频率 × 3.5 | 21000 | 原文注：不影响帧率 |
| tRFC | 160 × 目标频率 / 2000 | 480 | 折合 160ns，A-die 公认甜点值 |
| tWR | 目标频率 / 400 × 4 | 60 | ⚠️ 原文作者自标「不确定」 |
| tRFCpb | 130 × 目标频率 / 2000 | 390 | 折合 130ns，逐 bank 刷新 |
| tRRD_L | ≈ 目标频率 / 400 | 15 | 越低越好 |
| tRRD_S | ≥ 8 | 8 | A-die 颗粒的物理下限就是 8 |
| tWTR_L | 目标频率 / 200 | 30（最低 30） | — |
| tWTR_S | tWTR_L / 4 | 8（最低 8） | — |

## 使用建议

1. 先定频率和 tCL，再按公式推算其余参数作为**保守起步值**；
2. 每收紧一项参数后运行 TM5（anta777 Extreme @ 3~5 cycles）、y-cruncher 或 MemTest86 压测验证稳定性，报错则回退该项；
3. 时序压得越紧，对内存颗粒体质、内存电压（VDD/VDDQ）和内存控制器（IMC）要求越高；笔记本平台散热与供电余量有限，建议小幅渐进；
4. 超频有风险：可能影响稳定性、硬件寿命及保修，数据请提前备份，后果自负。

---

## 事实核查记录

本文公式已对照 DDR5 领域公认规则与多家超频社区信源核实，结论：**核心结构性规则均属实，部分数值公式为社区经验估算（原文作者亦自行标注了不确定性），整体可靠、可作为起步参考**。

| 声明 | 核查结果 |
| --- | --- |
| tCL 只能为偶数 | ✅ 属实：DDR5 因 BL32 突发长度对齐，CAS Latency 只定义偶数档（DDR4 才有奇数 CL） |
| tRAS ≥ tCL + tRCD + 2~4 | ✅ 属实（经典保守规则）：为教科书式下限；现代社区实践认为实际约束为 tRAS ≥ tRCD(RD) + tRTP，可适当低于该公式 |
| tCWL ≤ tCL，相差 0~2 | ✅ 属实：主流调优指南公认规则 |
| tFAW = tRRD_S × 4 | ✅ 属实：JEDEC 规则——tFAW（Four Activate Window）窗口内最多 4 次激活，故下限 = 4 × tRRD_S |
| tRRD_S ≥ 8，A-die 最低就是 8 | ✅ 属实：海力士 A-die 公认甜点值，社区大量实测佐证 |
| tRFC ≈ 160ns（160 × 频率 / 2000） | ✅ 属实：16Gb A-die 在 ~1.4V 下普遍可达 160ns 或更低，为公认甜点值 |
| tRFCpb ≈ 130ns | ⚠️ 估算值：「逐 bank 刷新时序短于全 bank 刷新」的原则正确，具体数值随颗粒与容量不同 |
| tREFI = 频率 × 3.5（不影响帧率） | ⚠️ 估算值：「tREFI 对游戏帧率影响甚微」与 Hardware Unboxed 等实测结论一致；该公式结果属于温和放宽的调优区间 |
| tRCD/tRP = tCL + 2~4 | ⚠️ 经验起步范围：偏激进一侧，好体质 A-die 可达，普通颗粒可放宽 |
| tRRD_L ≈ 频率/400、tWTR_L = 频率/200、tWTR_S = tWTR_L/4 | ⚠️ 估算值：结果落在社区常见调优区间内，非硬性规则 |
| tWR = 频率/400 × 4 | ❓ 原文作者自标「不确定」，未找到独立佐证，建议按主板 AUTO 值保守处理 |

**参考来源：**

- [Reddit r/overclocking — AM5 DDR5 Tuning Cheat Sheet, observations and notes](https://www.reddit.com/r/overclocking/comments/1k3o7qe/am5_ddr5_tuning_cheat_sheet_observations_and_notes/)
- [overclock.net — AMD Hynix DDR5 Overclocking Guide](https://www.overclock.net/threads/amd-hynix-ddr5-overclocking-guide.1801842/)
- [TechPowerUp — SK Hynix A-Die Overclocking Thread (AM5)](https://www.techpowerup.com/forums/threads/sk-hynix-a-die-overclocking-thread-only-for-ryzen-am5-users.335298/)
- [LinusTechTips — Help me tune my DDR5 timings (Hynix A-Die)](https://linustechtips.com/topic/1491776-help-me-tune-my-ddr5-timings-hynix-a-die/)
- [SystemVerilog.io — Understanding DDR4 timing parameters（tFAW 规则原理）](https://www.systemverilog.io/design/understanding-ddr4-timing-parameters/)
- [StackExchange — Origin of tFAW (Four Activation Window)](https://cs.stackexchange.com/questions/32286/origin-of-tfaw-four-activation-window-in-dram-timing-constraint)
- [Reddit r/overclocking — RAM timing rules（tRAS 实际约束讨论）](https://www.reddit.com/r/overclocking/comments/tsuttu/ram_timing_rules/)
