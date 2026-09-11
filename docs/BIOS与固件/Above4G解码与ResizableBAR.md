---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# Above 4G 解码与 Resizable BAR

> **分类**：BIOS 与固件 · 性能优化项
>
> **一句话**：Above 4G Decoding 是打开 64 位地址空间的大门，Resizable BAR（ReBAR，AMD 叫 SAM）是把显卡 256MB 的小门换成与显存一样大的大门——顺序不能反：先关 CSM、再开 Above 4G、最后开 ReBAR。它本身不加速，只让设备能活、让 ReBAR 有地方站。

## Above 4G Decoding（4G 以上地址解码）

- **本质与核心机制**：
  - **不是解决内存容量识别**：不是早年 32 位操作系统认不全 >4GB 物理内存的古早问题；
  - **解决的是 MMIO 地址窗口耗尽**：主板和 CPU 需要给 PCIe 设备（显卡、声卡、RAID 卡等）分配一段物理内存地址映射（MMIO，Memory-Mapped I/O），供 CPU 发号施令。传统 32 位寻址下，所有设备的 BAR（基址寄存器）窗口被强行塞在 4GB 以下那段仅存不到 2~3GB 的“PCI 空洞”里。当插入第二块卡、计算卡、大显存显卡或开启 ReBAR 后，地址窗口根本不够分；
  - **设备管理器「代码 12」的精准归因**：设备出现黄叹号提示「代码 12：该设备找不到足够可用的资源」，**先别急着重装显卡驱动**。如果是因为多卡、专业计算卡或开启 ReBAR 导致，正是 MMIO 地址窗口挤爆的典型病症；开启 Above 4G 将设备门牌号搬迁到 4GB 以上的 64 位空间，即可瞬间解除资源冲突（若无大 BAR 设备的普通代码 12 才是传统 IRQ 或驱动残留冲突）。
- **与 CSM 的绝对互斥**：
  - CSM（兼容性支持模块）使用的是 16 位/32 位传统 Option ROM，根本不认 64 位 MMIO 寻址；
  - **开启硬性先决条件**：必须先彻底关闭 CSM（采用纯 UEFI 启动模式 + GPT 硬盘分区）。CSM 开启状态下强开 Above 4G 可能导致主板自检卡死或开机黑屏。
- **品牌路径**：
  - 华硕（ASUS）：高级（Advanced）→ PCIe 相关设置 / 系统代理（SA）配置；
  - 微星（MSI）：Settings → 高级 → PCIe 子系统设置；
  - 技嘉（GIGABYTE）：Settings → IO 端口；
  - 华擎（ASRock）：高级 → PCIe 设备配置。
  - *注*：多数新主板出厂默认开启；部分旧主板需从 EZ 简易模式按 F7 切入高级模式方可查看。
- **判断标准**：
  - 64 位系统（Win10/11/Linux）建议直接开启；
  - 显存超过 4GB、装载多张 PCIe 设备或计算卡必开；
  - 准备启用 Resizable BAR / SAM 的必须前置开启；
  - 纯 32 位系统或依赖 Legacy/CSM 引导的设备必须保持关闭。

## Resizable BAR（ReBAR / SAM）

- **原理**：PCIe 规范早期默认每个 BAR 窗口最大仅 256MB。游戏渲染时 CPU 频繁向显卡传输纹理与着色模型数据，超出 256MB 就必须分批切片、排队反复映射，CPU 调度开销大；开启 ReBAR 后依托 64 位 Above 4G 空间，把窗口拉大到与整块显存等大（例如 16GB 显存即 16GB 窗口），CPU 可以直接且并发寻址整块显存。
- **Above 4G 与 ReBAR 的上下层关系**：
  - **Above 4G 是底层地基**：它负责把地址门牌搬上楼，本身不增加游戏帧数，但它决定设备能否正常初始化存活；
  - **ReBAR 是上层应用**：负责把小门拆成大门，游戏帧率提升与调度优化全部源于 ReBAR。
- **开启条件（六项缺一不可）**：
  1. 64 位操作系统（Windows 10 1803+ / Windows 11 或 Linux 5.10+）；
  2. CPU 支持：AMD 锐龙 3000 系及以上（不含 3000G 等 APU）；Intel 10 代酷睿及以上；
  3. 主板芯片组与 BIOS：AMD 400/500/600 系；Intel 400/500/600/700 系（需更新支持 ReBAR 的 BIOS）；
  4. 显卡支持：NVIDIA RTX 30 系起（早期批次需刷官方支持 ReBAR 的 VBIOS）、AMD RX 6000 系起、Intel Arc 全系列；
  5. 引导模式：CSM 必须关闭，GPT 分区 + 纯 UEFI 启动；
  6. BIOS 设置顺位：先开启 Above 4G Decoding，随后将出现的 Resizable BAR 设为 Auto 或 Enabled。
- **验证机制**：
  - 打开 GPU-Z，切到「Advanced」标签页选择「Resizable BAR」下拉菜单：
    - 检查 GPU-Z 诊断清单中的 9 项参数（包括 GPU Hardware Support、Above 4G Decode Enabled、CSM Disabled 等）是否全部显示为「Yes」；
    - 若显示 Disabled，对照排查哪一项打红叉（最常见是 CSM 遗留开启或主板 BIOS 未刷最新）。

## 实测收益

- 分辨率越低，CPU 瓶颈越明显，收益越显著：1080P 提升约 5%~15%，1440P 约 3%~10%，4K 显卡负载打满时多在 3%~5% 以内；
- 开放世界、超大贴图流式加载（如《赛博朋克 2077》、《地平线》等）及 CPU 调度重负荷游戏收益最明显；极少数老旧引擎游戏可能存在反向掉帧（可在显卡驱动面板中按游戏单独配置开关 Profile）；
- 整机功耗增加通常不超过 3%~5%。

## 翻车恢复与风险红线

- **开后黑屏无法进系统**：通常为系统盘为 MBR 分区或显卡 VBIOS 过旧不认 UEFI GOP。执行清 CMOS 恢复（断电拔线 → 长按电源按键放电 → 短接 CLRTC 跳线或抠电池 5 分钟），即可回退默认设置开机；
- **排查代码 12 避免盲目重装**：先看设备是多卡还是大 BAR；若是，进 BIOS 确认 Above 4G 是否被误关；
- **严禁盲目魔改旧卡**：为未官方支持的老卡（如 GTX 10/20 系或早期 AMD 卡）使用第三方 UEFI 驱动补丁注入 ReBAR 属于高危破坏性操作，存在变砖风险。

## 出处与核查说明

本文综合整理自 B 站 UP 主「所盼皆欣然」《电脑 BIOS 选项全科普》系列视频，经本地语音转录与专业硬件工程逻辑校对：

- [电脑 BIOS 选项全科普 EP16/Above 4G Decoding【暮里学姐】（重制版，BV1SqbK6VEfW）](https://www.bilibili.com/video/BV1SqbK6VEfW/)
- [电脑 BIOS 选项全科普 EP08/Resizable BAR【暮里学姐】（旧版，BV11tEu6SEKX，待重制版 EP17）](https://www.bilibili.com/video/BV11tEu6SEKX/)
- [电脑 BIOS 选项全科普 EP07/Above 4G【暮里学姐】（旧版，BV1LFEt6QE4e，已由重制版 EP16 替代）](https://www.bilibili.com/video/BV1LFEt6QE4e/)
- 联动篇目：[UEFI、Legacy 与 CSM 兼容支持模块](./UEFI-Legacy-CSM与分区表.md)、[NVMe 识别全链路与故障排查](./NVMe识别全链路与故障排查.md)、[M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)
