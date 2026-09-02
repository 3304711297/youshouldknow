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
> **一句话**：Above 4G Decoding 是打开 64 位地址空间的大门，Resizable BAR（ReBAR，AMD 叫 SAM）是把显卡 256MB 的小门换成与显存一样大的大门——顺序不能反：先关 CSM、再开 Above 4G、最后开 ReBAR。

## Above 4G Decoding（4G 以上地址解码）

- **原理**：传统模式只支持 32 位寻址，BIOS 开机初始化默认把所有 PCIe 设备的地址窗口（BAR，基址寄存器）挤在 4G 以内，真正留给设备的不到 3G；大显存显卡的地址窗口可达 2GB 甚至更多，多卡/多设备时 4G 内根本不够分。开启后地址空间扩展到 64 位，"小仓库换大仓库"。
- **与 CSM 的联动**：CSM 强制传统模式初始化，传统模式天然限制在 4G 内——CSM 开启时该选项会隐藏/锁定/不生效，必须先关 CSM 用纯 UEFI。
- **品牌路径**：华硕在高级菜单 PCIe 相关设置；微星在 设置 → 高级 → PCIe 相关项；技嘉在 Settings → IO 端口；华擎在高级菜单 PCIe 配置。多数主板默认关闭，部分新板默认开启；有些主板需从 EZ 模式切到高级模式才能看到。

**判断四条**：64 位系统（Win10/11/Linux）直接开；显卡显存超过 4G 建议开；超过 3 张 PCIe 设备建议开避免地址冲突；32 位系统就关闭。

## Resizable BAR（ReBAR / SAM）

- **原理**：PCIe 规范默认每个 BAR 窗口最大 256MB（是地址窗口不是显存）。游戏时 CPU 频繁向显卡传送纹理、模型数据，超出窗口就要反复重映射，开销大；开 ReBAR 后用 64 位 BAR 把窗口拉到与显存一样大（16G 显存即 16G 窗口），CPU 可直接任意访问显存。
- **开启条件（六项全满足才生效）**：
  1. 64 位系统（Win10 1803+/Win11 或 Linux 5.10+）；
  2. CPU：AMD 锐龙 3000 系及以上；Intel 10 代及以上；
  3. 显卡：NVIDIA RTX 30 系起（早期批次可能需刷官方 VBIOS）、AMD RX 6000 系起（需 500 系芯片组）；
  4. 驱动：NVIDIA 465+、AMD 21.3.1+；
  5. CSM 关闭；
  6. 先开 Above 4G Decoding（多数主板开 Above 4G 后 ReBAR 选项自动出现）。
- **验证**：GPU-Z 高级面板拉到 Resizable BAR 一栏，系统支持/是否开启/CSM 关闭/UEFI+GPT/驱动支持全绿、BAR size 显示正常数值即生效。注意个别主板 CSM 开着仍显示 ReBAR 选项，点了也没用。

## 实测收益

- 分辨率越低收益越大：1080P 约 5~15%、1440P 约 3~10%、4K 多数小于 5%；
- 大纹理开放世界、CPU 参与度高的游戏收益大，显卡已满载的游戏收益有限；个别游戏可能掉帧，可在驱动面板按游戏单独关闭；
- 功耗增加不超过约 5%。

## 翻车恢复与风险

- 开启后黑屏：清 CMOS 恢复（拔电源线 → 长按电源键放电 → 拔 CMOS 电池或短接跳线），操作不损坏硬件；
- 显存识别不全：查 CSM 是否没关、显卡驱动是否最新、BIOS 是否太老；
- **给不支持的显卡用第三方工具魔改开启属高风险操作**，必须先备份原版 VBIOS，刷写绝不能断电。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」《电脑BIOS选项全科普》旧版合集第 07、08 集，经本地语音转录校对整理；实测数字（游戏帧率、功耗）为口播数据，标注待核处建议对照原视频：

- [电脑BIOS选项全科普EP07/Above 4G【暮里学姐】（旧版）](https://www.bilibili.com/video/BV1LFEt6QE4e/)
- [电脑BIOS选项全科普EP08/Resizable BAR【暮里学姐】（旧版）](https://www.bilibili.com/video/BV11tEu6SEKX/)
- 相关：[UEFI、Legacy 与 CSM 兼容支持模块](./UEFI-Legacy-CSM与分区表.md)、[M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)
