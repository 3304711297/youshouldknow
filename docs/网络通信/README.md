---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# 网络通信

Windows 网络栈、代理/TUN 转发与运营商速查的知识分类。

> 本目录区分“系统网络栈优化”与“代理/TUN 的流量接管”；二者不在同一层，直接改注册表不能替代驱动与链路排查。

## 文章

### 主文
- [Windows 网络栈优化原则](./Windows网络栈优化原则.md) — 低延迟 vs 高吞吐的分层判断、参数与测试方法

### 专题
- [Windows 游戏网络 QoS 策略与 DSCP 原理](./Windows游戏网络QoS策略与DSCP原理.md) — 竞技游戏网络数据包 DSCP 46 加速标记与 TCP CUBIC 原理
- [Karing Windows TUN 与 Windows 网络转发设置](./Karing-Windows-TUN与Windows网络转发设置.md) — TUN/系统代理/Forwarding 的区别与热点场景排障

### 速查
- [四大运营商频段速率与 APN 设置速查](./四大运营商频段速率与APN设置速查.md) — 频段分配、APN 与套餐速率分档

## 建议阅读顺序

1. 先读主文 [Windows 网络栈优化原则](./Windows网络栈优化原则.md) 建立低延迟/高吞吐的判断框架；
2. 使用 Karing/Clash 等代理时，再读 [Karing TUN 专题](./Karing-Windows-TUN与Windows网络转发设置.md) 区分 TUN 与 Forwarding；
3. 需要核对手机频段或 APN 时，查 [运营商速查](./四大运营商频段速率与APN设置速查.md)。

## 与其他分类的边界

- `CPU与延迟/Windows键鼠与TCP低延迟可选实验设置.md`：键鼠/TCP 的可选实验与注册表边界；本目录负责网络栈的通用原则。
- `系统知识/`：`powercfg` / `eventvwr` 等系统排障工具；网络排障需结合驱动与链路，而非仅注册表。
- `项目导航/`：`tweakbyjie` 当前无网络自动项；不要把知识教程误记为脚本覆盖。
