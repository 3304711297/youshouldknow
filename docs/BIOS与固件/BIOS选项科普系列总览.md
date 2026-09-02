---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# BIOS 选项科普系列总览

> **分类**：BIOS 与固件 · 系列导航
>
> **来源说明**：本系列文章整理自 B 站 UP 主 [所盼皆欣然](https://space.bilibili.com/589200735) 的两个视频合集——旧版《[主板BIOS选项科普](https://space.bilibili.com/589200735/channel/collectiondetail?sid=8222417)》（27 集）与重制版《[电脑BIOS/UEFI选项内容全科普](https://space.bilibili.com/589200735/channel/collectiondetail?sid=8897657)》（14 集），全部经本地语音转录后按硬件领域知识校对术语整理而成。每篇文章底部均附对应视频出处链接。

## 系列覆盖的两个合集

| 合集 | 集数 | 特点 |
|---|---|---|
| [主板BIOS选项科普（旧版）](https://space.bilibili.com/589200735/channel/collectiondetail?sid=8222417) | 27 集 | 覆盖面最全：从 BIOS 入门一路讲到 CPU 倍频、外频、核心电压与防掉压 |
| [电脑BIOS/UEFI选项内容全科普（重制版）](https://space.bilibili.com/589200735/channel/collectiondetail?sid=8897657) | 14 集 | 对旧版部分主题重制更新：补充 UEFI 时代细节（Boot Override、Secure Boot 密钥管理、VMD 等） |

两个合集主题有重叠，本文整理时**以重制版为主线、旧版补全重制版未覆盖的主题**（如快速启动、Above 4G、ReBAR、PBO、电压与防掉压等），出处均逐篇标注。

## 阅读地图

### 第一步：入门三篇（装机必看）

1. [BIOS 入门：进入、退出与模式切换](./BIOS入门进入退出与模式切换.md)——进 BIOS、EZ/高级模式、保存与放弃更改；
2. [BIOS 恢复默认设置的三种方法](./BIOS恢复默认设置的三种方法.md)——Load Optimized / Load Setup Defaults / Clear CMOS 的层级与坑；
3. [启动顺序与 Boot Override](./启动顺序与BootOverride.md)——装系统 U 盘启动的正确姿势。

### 第二步：装系统前后必改项

4. [UEFI、Legacy 与 CSM 兼容支持模块](./UEFI-Legacy-CSM与分区表.md)——启动模式与分区表配对；
5. [Secure Boot 安全启动与密钥管理](./SecureBoot安全启动与密钥管理.md)；
6. [TPM/PTT/fTPM 与清除风险](./TPM-PTT-fTPM与清除风险.md)；
7. [快速启动 Fast Boot](./FastBoot快速启动.md)。

### 第三步：性能优化项

8. [XMP/EXPO 内存认证档科普](../内存超频/XMP-EXPO内存认证档科普.md)（内存超频分类）；
9. [DDR5 内存训练与 MCR/PD](./DDR5内存训练与MCR-PD.md)；
10. [Above 4G 解码与 Resizable BAR](./Above4G解码与ResizableBAR.md)；
11. [风扇调速 PWM/DC 与风扇曲线](./风扇调速PWM-DC与风扇曲线.md)；
12. [显示输出优先级与核显调用](./显示输出优先级与核显调用.md)；
13. [SATA 模式与 Intel VMD](./SATA模式与Intel-VMD.md)；
14. [M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)；
15. [厂商软件自动安装开关](./厂商软件自动安装开关.md)。

### 第四步：CPU 自动优化与超频进阶

16. [CPU 调频与电源管理机制](./CPU调频与电源管理机制.md)——SpeedStep/Speed Shift/CPPC、睿频与 C-States；
17. [AMD PBO 与 Curve Optimizer](./AMD-PBO与CurveOptimizer.md)；
18. [功耗墙、电流墙与 CEP 电流保护](./功耗墙电流墙与CEP电流保护.md)；
19. [CPU 倍频与外频超频基础](./CPU倍频与外频超频基础.md)；
20. [CPU 电压与 LLC 防掉压](./CPU电压与LLC防掉压.md)。

## 系列理念：超频的三条路线

旧版合集开篇的杂谈篇（《超频值得吗》，BV1g67P6VEA2）给出三条路线，供选择后续阅读深度：

| 路线 | 做法 | 收益与风险 |
|---|---|---|
| 保持默认，只开 XMP | 仅启用内存认证档 | 约 95% 性能，零风险，对应第三步第 8 篇 |
| 自动优化 | PBO + Curve Optimizer 降压 + 调功耗墙 | 风险极低、收益中等，对应第四步第 17~18 篇 |
| 手动超频 | 自定倍频、电压、防掉压 | 收益最高、风险最高，对应第四步第 19~20 篇 |

杂谈篇的核心观点：厂商睿频已吃掉单核极限约 95% 的空间，但全核重载频率仍留有保守余量；超频是否值得没有标准答案，若调试本身不是乐趣，4 小时反复调参换来全核 100MHz 不如拿去打游戏。

## 与其他分类的边界

- `内存超频/`：XMP/EXPO 认证档科普与手动时序参数作业；
- `CPU与延迟/`：Windows 侧的调度与延迟优化（BIOS 侧 CPU 选项在本分类）；
- 本分类其余既有文章：固件刷写、镜像编辑与 OEM 个案风险说明。

## 出处与核查说明

- 系列出处：[所盼皆欣然的 B 站空间](https://space.bilibili.com/589200735)，两个合集链接见上文表格；
- 整理方式：本地 Whisper 语音转录 + 术语校对；AI 语音与转录存在失真，文中标注"待核"的数字与菜单路径建议对照原视频画面核实；
- 本系列为科普整理，不构成对任何主板的操作保证；涉及清 CMOS、TPM、Secure Boot 的操作务必先阅读对应文章的风险章节。
