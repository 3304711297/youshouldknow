---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# UEFI、Legacy 与 CSM 兼容支持模块

> **分类**：BIOS 与固件 · 装机必改项
>
> **一句话**：UEFI（新接口）+ GPT 与 Legacy（老启动）+ MBR 是两对固定组合，CSM 是让新主板认老显卡/老设备的"翻译官"——新硬件装 Win10/11 要关掉它，它只是钥匙不是性能开关。

## 三兄弟与两对组合

| 项 | 内容 |
|---|---|
| UEFI | 现代固件接口：图形界面、鼠标支持、大硬盘、Secure Boot |
| Legacy | 老式启动：MBR 分区表，单盘上限 2.2TB、最多 4 个主分区 |
| CSM | 固件里的兼容模块：加载老显卡等设备的 Legacy Option ROM，充当"翻译官" |

分区表配对是铁律：**UEFI + GPT、Legacy + MBR，只有这两对组合能启动**；拆开交叉匹配开机就认不到盘。装系统时 U 盘在启动项里看不到，多半是 U 盘分区表与主板启动模式不匹配（"语言不通"），不是 U 盘坏了。

## CSM 的代价

- 开机自检变长（多花约 2~5 秒）；
- **与 Secure Boot 互斥**：开了 CSM，Secure Boot 选项会被禁用或直接消失——这是装 Win11 最常见的"安全启动不见了"原因；
- **Resizable BAR（可调显存地址窗口）失效**：传统模式只支持 32 位 BAR 寻址，显卡免费提速开不了；
- GPT 磁盘完整特性受限。

> 注意：CSM 本身不会让显卡核心性能变快或变慢，跑分无明显差异——网上"关 CSM 显卡白捡 10%"属于讹传，它只决定显存地址窗口能否用 ReBAR。

## 什么时候必须开 CSM

1. 老二手显卡没刷 UEFI GOP 固件：插上纯 UEFI 主板开机 VGA 灯常亮、黑屏——老卡只有 Legacy Option ROM，需要 CSM 兜底；
2. 装未打补丁的老系统（如 Win7），需要 MBR + Legacy 环境；
3. 要插老 PCIe 扩展卡（Legacy 驱动设备）。

新装系统 + 新显卡：直接把 CSM 设为 Disable，别犹豫。

## 关 CSM 后系统蓝屏怎么办

系统盘还是 MBR 分区表、关了 CSM 就没有"老翻译官"读老盘——不用重装，Windows 自带 **mbr2gpt** 命令把 MBR 转成 GPT，转换后再关 CSM 就完美运行。

**验证方法**：Win+R 输入 `msinfo32`，看"BIOS 模式"一栏——显示"UEFI"就是进了新接口时代（此时能开 Secure Boot 和 ReBAR）；显示"传统"说明还在用 Legacy。

## 品牌路径参考

华硕在启动（Boot）菜单；微星在 Settings → 高级 → Windows 操作系统配置；技嘉在 Boot 页；华擎在高级（Advanced）菜单。具体名称随型号版本变化，以说明书为准。

## 翻车恢复

改后黑屏/蓝屏：重启进 BIOS 改回，或按[恢复默认设置的三种方法](./BIOS恢复默认设置的三种方法.md)清 CMOS 回厂。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」对应集，经本地语音转录校对整理；数字与路径细节以原视频画面为准：

- [电脑BIOS选项全科普EP04/UEFI、Legacy与CSM兼容支持模块（重制版）](https://www.bilibili.com/video/BV12s8V6tEVm/)
- [电脑BIOS选项全科普EP06/CSM（旧版）](https://www.bilibili.com/video/BV1Tg7Q6uEDR/)
- 相关：[Above 4G 解码与 Resizable BAR](./Above4G解码与ResizableBAR.md)、[Secure Boot 安全启动与密钥管理](./SecureBoot安全启动与密钥管理.md)
