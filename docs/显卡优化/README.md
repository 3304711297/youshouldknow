# 显卡优化

NVIDIA / AMD 显卡驱动、控制面板、DLSS、ReBAR 与接口知识分类。

> 本目录提供可复现的显卡实际设置路径；是否值得修改、风险与游戏收益需结合 [系统调优与安全](../系统调优与安全/README.md) 的统一原则与 A/B 测试判断。

## 文章

### 驱动安装与精简
- [NVCleanstall 精简安装 NVIDIA 显卡驱动](./NVCleanstall精简安装NVIDIA显卡驱动.md) — TechPowerUp 官方源、组件取舍与事实核查

### 控制面板与应用设置
- [NVIDIA 进阶优化 - 控制面板设置](./NVIDIA进阶优化-控制面板设置.md) — 全局/程序设置的取舍与验证
- [NVIDIA 进阶优化 - App 设置与超频](./NVIDIA进阶优化-App设置与超频.md) — NVIDIA App 内的性能与超频路径

### DLSS / 帧生成与延迟
- [DLSS 帧生成、低延时模式与延迟的关系](./DLSS帧生成低延时模式与延迟的关系.md) — 超分/帧生成/Reflex、刷新率与多帧生成倍率对帧率与延迟的影响
- [NVIDIA 进阶优化 - DLSS 超分预设模型](./NVIDIA进阶优化-DLSS超分预设模型.md) — DLSS 预设、DLSSTweaks 与 Ultra Performance 比例示例

### 硬件能力与接口
- [NVIDIA 进阶优化 - ReBAR 强制开启](./NVIDIA进阶优化-ReBAR强制开启.md) — Resizable BAR 的开启条件与验证
- [DP / HDMI 协议与速率关系表](./DP-HDMI协议与速率关系表.md) — 接口带宽、分辨率与刷新率速查

## 建议阅读顺序

1. 先看 [NVCleanstall](./NVCleanstall精简安装NVIDIA显卡驱动.md) 确认驱动来源与组件取舍，避免精简过度；
2. 再按需查 [控制面板](./NVIDIA进阶优化-控制面板设置.md) / [App 设置](./NVIDIA进阶优化-App设置与超频.md)；
3. 关注帧率与延迟时，读 [DLSS 与延迟](./DLSS帧生成低延时模式与延迟的关系.md) 再决定是否开启帧生成；
4. 涉及接口与带宽上限时，查 [DP/HDMI 速率表](./DP-HDMI协议与速率关系表.md)。

## 与其他分类的边界

- `GPU与显示/`：图形管线、驱动模型与帧时间的原理总览；`显卡优化/` 负责可执行的驱动与面板设置。
- `CPU与延迟/`：调度/DPC/输入延迟；显卡设置不应替代 CPU 瓶颈的排查。
- `项目导航/GPU调度与显示管线.md`：HAGS/MPO 在 `tweakbyjie` 中的实际执行边界；本目录不重复脚本映射。
