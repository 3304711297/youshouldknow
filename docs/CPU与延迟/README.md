---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# CPU 与延迟

面向游戏线程、系统调度、DPC/ISR、计时器、输入延迟和实验设置的知识分类。

## 主文

- [CPU 调度与游戏线程](./CPU调度与游戏线程.md)：线程、调度、DPC/ISR、计时器、帧时间和测试总览

## 专题

- [Intel 12 代移动标压 (HX) 降压黑屏排障与 Core/Cache 单轨联动机制实测](./Intel-12代移动标压HX降压黑屏排障与单轨联动机制实测.md) — 机械革命极光 X (i7-12800HX) ThrottleStop 极限降压实录、0x0000000A (IRQL=255 HIGH_LEVEL) 黑屏转储分析、Core/Cache 单轨供电绑定机制与 -180mV 稳态锁定
- [Windows 键鼠与 TCP 低延迟可选实验设置](./Windows键鼠与TCP低延迟可选实验设置.md)：高级实验，默认不进入主脚本

执行层参考位于[项目导航](../项目导航/README.md)，统一测试流程见[游戏性能验证流程](../项目导航/游戏性能验证流程.md)。
