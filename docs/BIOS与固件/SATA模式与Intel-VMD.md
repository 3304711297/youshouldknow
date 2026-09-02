---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# SATA 模式与 Intel VMD

> **分类**：BIOS 与固件 · 装机必改项
>
> **一句话**：SATA 模式三个选项（IDE 已淘汰 / AHCI 是现代标准 / RAID 即 Intel RST）；11 代起 Intel 把 VMD（卷管理设备）叠在 RST 上，开启后走扩展槽的 NVMe 盘会被 RST 驱动"收编"——装系统前普通用户先关它，最省事。

## SATA 模式三个选项

| 选项 | 说明 |
|---|---|
| IDE | 上古兼容模式，为 Windows XP 时代保留，新主板已淘汰 |
| AHCI | 现代标准，Win10/11 原生支持；自带 NCQ 原生命令队列（硬盘自己调度寻道，像叫号系统）与热插拔 |
| RAID / Intel RST | 磁盘阵列方案，含硬盘状态监控与（老平台）傲腾加速；11 代起配合 VMD 使用 |

- 自装机：**AHCI 就是最优解，不用改**；品牌整机（戴尔/惠普/联想）常默认 RST/RST Premium，日常使用保持原厂模式即可，装 Linux 或老 PE 才需要切 AHCI。
- 单盘开 RAID 不会变快，只多一层驱动麻烦。
- **装完系统别来回切模式**：Windows 安装时按当前模式加载驱动，突然切换驱动对不上 → 蓝屏 **INACCESSIBLE_BOOT_DEVICE（0x7B）**。数据不会丢，只是系统暂时读不到盘。

### 模式切换蓝屏的救法

1. 最快：进 BIOS 改回原模式，进系统后再操作；
2. 安全模式切换法：在能进的系统里用 msconfig 设为安全模式启动 → 进 BIOS 切换 SATA 模式 → 系统在安全模式自动重认驱动 → 再关掉安全模式；
3. 全新安装。

## Intel VMD（Volume Management Device）

- **本质**：芯片组（南桥）内部的一层虚拟化壳，**不是硬盘模式**；开启时走扩展槽的 NVMe 盘被收编给 Intel RST 驱动管理。只管 NVMe 盘，SATA 口的盘归 AHCI/RST 管，普通 SATA 盘它管不着。
- **为什么装系统看不到盘**：Windows 安装盘自带的标准 stornvme 驱动只认标准 NVMe 控制器，不认 VMD 控制器——BIOS 里明明写着三星/西数/铠侠，安装界面磁盘列表却是空的。**不是盘坏了**。
- **三种状态**：Enabled（盘被接管）/ Disabled（还原原生标准驱动）/ RAID（组阵列用）。

### 操作建议

1. **普通用户装系统前先进 BIOS 把 VMD 设 Disabled**——安装盘直接认盘，零驱动最省事；
2. 真要组 RST 阵列：保持 Enabled，装系统时点"加载驱动"，选解压出的 RST/f6 驱动（不是 setupRST.exe 安装器）；
3. **装完系统后别直接关 VMD**——官方确认会蓝屏 0x7B（驱动对不上，设计如此）；想关先重装或走安全模式流程；
4. 商用整机可能锁死关不了，只能带 VMD 驱动装；Linux 新内核（5.x+）自带 VMD 驱动基本无感；
5. 关掉 VMD 性能几乎无差别（口播称 5% 以内），它只影响"谁来管盘"不影响速度。

### 通道共享注意

部分主板的高速 M.2 插槽与某些 SATA 口共用通道——M.2 插上后对应 SATA 口直接失效（线没松盘也不认）。凡涉及 SATA 口失踪，先翻主板说明书的通道共享表换口。详见[M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)。

## SATA 区其他选项

控制器总开关（关了所有 SATA 口失效，别动）、每个口的 Enable 状态（灰掉=口没启用）、Hot Plug 热插拔（常换 2.5 寸盘的口可以开，免得每次换盘重设）、NCQ 开关——不确定就保持默认。

## 排查口诀

先查物理（换线、换口、别的机器认不认），再查模式；默认 AHCI 别乱切；VMD 只影响扩展槽 NVMe；SATA 口失踪查线也查通道共享。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」对应集，经本地语音转录校对整理；路径与百分比细节以原视频画面为准：

- [电脑BIOS选项全科普EP12/SATA模式（重制版）](https://www.bilibili.com/video/BV1nHtP6QEeF/)
- [电脑BIOS选项全科普EP13/Intel VMD（重制版）](https://www.bilibili.com/video/BV1iW4U6NEqK/)
- [电脑BIOS选项全科普EP03/SATAmode【暮里学姐】（旧版）](https://www.bilibili.com/video/BV1H2VU6VExq/)
- 相关：[M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)
