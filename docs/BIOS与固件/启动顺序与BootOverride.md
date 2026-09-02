---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# 启动顺序与 Boot Override

> **分类**：BIOS 与固件 · 装机必改项
>
> **一句话**：启动顺序（Boot Priority）是每次开机的默认路线，改了就一直生效；Boot Override 只让下一次从你选的盘启动，用完自动回原路线——好比默认走三路上班，临时绕一趟超市，回来不用刻意改回。

## 出厂默认顺序

硬盘或 Boot Manager 第一，U 盘插着随时排在后面，网络启动放最后。装机时用 Boot Override 临时从 U 盘启动最省事；想永久调整才去改 Boot Priority。

## UEFI 装完系统的铁律

第一启动项选 **Windows Boot Manager**，不是具体硬盘名。很多人装完系统把"硬盘名"排到 Windows Boot Manager 前面，甚至以为 Windows Boot Manager 是病毒——其实它是标准 UEFI 引导标签，必须放在第一，否则 BitLocker 和系统引导可能出问题（认错盘、开机报错、进错系统）。

## 常见症状对照

| 症状 | 多半原因 |
|---|---|
| 卡在 checking media 转半天圈 | 网络启动被排到了第一位 |
| U 盘在启动项里看不到 | U 盘不是 UEFI 模式（分区表/引导方式不匹配），不是 U 盘坏了 |
| 插着 U 盘但不从 U 盘启动 | 被永久顺序排后或被 Fast Boot 跳过，用 Boot Override 临时选 |

- BIOS 找系统的逻辑：按 1、2、3 逐个问，找到第一个能启动的就移交控制权，后面的盘不再看。
- CSM（兼容支持模块）开启时主板可能只认 Legacy 设备，UEFI 模式的 U 盘显示不出来——详见[UEFI、Legacy 与 CSM 兼容支持模块](./UEFI-Legacy-CSM与分区表.md)。

## Boot Override：一次性启动

完全独立于永久顺序，是它最大的优势：

- 四家主板在启动/退出页都有 Override 入口，路径各不相同但逻辑一致；
- **不开机进 BIOS 的热键**：华硕按 F8、微星按 F11、技嘉按 F12、华擎按 F11（笔记本别套台式机键位，查整机说明书）。

## 装系统正确流程

1. 进 BIOS（或开机热键）用 Boot Override 选择 U 盘（UEFI 系统选带 UEFI 标记的 U 盘项）；
2. 第一阶段复制完成后第一次重启时**立刻拔掉 U 盘**，否则又跳回安装界面死循环；
3. 装完进 BIOS 把 Windows Boot Manager 调到第一，F10 保存，确认没误改。

## 翻车恢复与冷知识

- 改错了回 BIOS 重调，或 Load Defaults 恢复；Override 只改一次，下次开机自动还原，多担心的都没必要；
- **每次断电后日期时间都变回出厂** = 纽扣电池没电，买一颗 CR2032 换上即可。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」两个合集对应集，经本地语音转录校对整理；品牌热键与菜单路径如与画面有出入以原视频为准：

- [电脑BIOS选项全科普EP03/启动顺序与boot override（重制版）](https://www.bilibili.com/video/BV1JKbe6MEom/)
- [电脑BIOS选项全科普EP02/启动选项（旧版）](https://www.bilibili.com/video/BV1KcVE6aEMd/)
