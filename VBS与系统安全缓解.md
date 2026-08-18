# VBS 与系统安全缓解

## VBS 是什么

Virtualization-Based Security（基于虚拟化的安全）利用硬件虚拟化能力隔离关键安全区域。

常见相关功能：

- Memory Integrity（HVCI）
- Credential Guard
- Device Guard
- Hypervisor

## 性能影响

VBS 是否影响性能取决于：

- CPU 架构
- Windows 版本
- 游戏和应用类型
- 驱动支持情况

部分场景可能出现性能下降或延迟变化，但并不是所有设备都会明显受到影响。

## 优化原则

关闭安全功能并不等于一定提升体验。

判断流程：

1. 确认是否需要虚拟化功能。
2. 测试实际游戏或工作负载。
3. 保留恢复方案。

## 与 tweakbyjie 的关系

`tweakbyjie` 中涉及 VBS、Hyper-V、Device Guard 的功能属于高级配置，应独立测试。

这类修改影响系统安全模型，不应与普通游戏优化混合执行。
