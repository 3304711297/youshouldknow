---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# BIOS 与固件

这是 BIOS、UEFI、固件镜像和主板恢复相关的高风险知识分类。

> ⚠️ 本目录不提供一键刷写脚本、修改后的 BIOS 镜像或工具压缩包。固件操作可能导致无法启动、变砖、BitLocker 恢复或需要售后/编程器维修。

## 文章

### BIOS 选项科普系列（整理自 B 站 UP 主「所盼皆欣然」两个合集，逐篇附视频出处）

- [BIOS 选项科普系列总览](./BIOS选项科普系列总览.md) — 两个合集导读、阅读地图与超频三条路线
- [BIOS 入门：进入、退出与模式切换](./BIOS入门进入退出与模式切换.md)
- [BIOS 恢复默认设置的三种方法](./BIOS恢复默认设置的三种方法.md)
- [启动顺序与 Boot Override](./启动顺序与BootOverride.md)
- [UEFI、Legacy 与 CSM 兼容支持模块](./UEFI-Legacy-CSM与分区表.md)
- [Secure Boot 安全启动与密钥管理](./SecureBoot安全启动与密钥管理.md)
- [TPM/PTT/fTPM 与清除风险](./TPM-PTT-fTPM与清除风险.md)
- [快速启动 Fast Boot](./FastBoot快速启动.md)
- [Above 4G 解码与 Resizable BAR](./Above4G解码与ResizableBAR.md)
- [风扇调速 PWM/DC 与风扇曲线](./风扇调速PWM-DC与风扇曲线.md)
- [显示输出优先级与核显调用](./显示输出优先级与核显调用.md)
- [SATA 模式与 Intel VMD](./SATA模式与Intel-VMD.md)
- [M.2 通道分配与显卡 PCIe 降速](./M2通道分配与显卡PCIe降速.md)
- [NVMe 识别全链路与故障排查](./NVMe识别全链路与故障排查.md)
- [厂商软件自动安装开关](./厂商软件自动安装开关.md)
- [DDR5 内存训练与 MCR/PD](./DDR5内存训练与MCR-PD.md)
- [CPU 调频与电源管理机制](./CPU调频与电源管理机制.md)
- [AMD PBO 与 Curve Optimizer](./AMD-PBO与CurveOptimizer.md)
- [功耗墙、电流墙与 CEP 电流保护](./功耗墙电流墙与CEP电流保护.md)
- [CPU 倍频与外频超频基础](./CPU倍频与外频超频基础.md)
- [CPU 电压与 LLC 防掉压](./CPU电压与LLC防掉压.md)

### 工具与个案

- [BIOS 与 UEFI 固件刷写及开机 Logo 修改指南](./BIOS与UEFI固件刷写及开机Logo修改指南.md)
- [UEFI Editor 项目说明](./UEFI-Editor项目说明.md)
- [机械革命笔记本 BIOS 选项与超频降压风险说明](./机械革命笔记本BIOS选项与超频降压风险说明.md)

## 建议阅读顺序

1. 先确认机型、主板、BIOS 版本和恢复路径；
2. 阅读刷写风险、备份和失败处理；
3. 再了解 UEFI Editor 的能力与限制；
4. 不要因为工具能打开或保存镜像，就认为修改后的固件可以安全刷入。

## 与其他分类的边界

- `验机相关/`：装机、激活、OOBE 和硬件验收；
- `内存超频/`、`显卡优化/`：硬件调校和驱动设置；
- 本目录：直接涉及 BIOS/UEFI 固件、镜像编辑、固件变量或恢复流程的内容。
