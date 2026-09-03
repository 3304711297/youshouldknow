---
status: stable
risk: low
applies_to:
  - Windows 10 (21H2+)
  - Windows 11 (22H2/23H2/24H2)
verified_on: "2026-09-03"
tweak_module:
  - "Part 12"
---

# Windows 游戏网络 QoS 策略与 DSCP 标记原理

## 1. 为什么需要游戏网络 QoS？

在家庭多设备或同电脑后台下载（如 Steam 更新、后台网页推流、语音开黑）的高负载网络环境下，实时竞技网游（CS2、Valorant、Apex Legends、COD、英雄联盟等）的 UDP/TCP 关键输入数据包经常面临**缓冲区膨胀（Bufferbloat）**与队列排队延迟，导致游戏内出现丢包、跳 Ping 和人物回拉。

通过 Windows 内置的 **QoS（Quality of Service，服务质量）策略**，可以告诉网卡驱动和家用路由器的 QoS 调度引擎：“优先转发此游戏进程的数据包”。

---

## 2. DSCP 46 (Expedited Forwarding) 核心原理

在 IPv4 数据包头部的 **ToS（Type of Service）/ DS（Differentiated Services）字段** 中，DSCP（差分服务代码点）使用高 6 位来定义数据包的优先级等级：

| 优先级分类 | DSCP 值 (十进制) | 二进制 TOS 标识 | 适用网络流量 | 路由器队列映射 (802.1p / WMM) |
| :--- | :---: | :---: | :--- | :--- |
| **Best Effort (默认)** | `0` | `000000` | 普通网页浏览、文件下载 | Best Effort (BE) / 低优先级 |
| **Assured Forwarding** | `10` / `18` / `26` | `001010` | 视频流媒体、常规通信 | Background / Video |
| **Voice / EF (加速转发)** | **`46`** | **`101110`** | **实时语音、低延迟竞技游戏** | **Voice (VO) / 最高优先级硬件队列** |

- **DSCP 46 (EF - Expedited Forwarding)**：这是 DiffServ 协议标准中除了网络控制流量外的最高民用服务级别。它要求本地网卡与路由器在出现排队时，优先将该流量送入高优先级硬件发射 FIFO 队列，实现极低抖动与最小传输延迟。
- **Throttle Rate = -1**：指示 Windows 网络调度器不对该进程的峰值输出速率进行任何软件层节流。

---

## 3. 注册表实现路径与结构

Windows 组策略在注册表中的映射位置为：
`HKLM\Software\Policies\Microsoft\Windows\QoS\<策略名称>`

每个游戏策略包含以下标准键值：

```ini
[HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows\QoS\CS2]
"Version"="1.0"
"Application Name"="cs2.exe"
"Protocol"="*"
"Local Port"="*"
"Local IP"="*"
"Local IP Prefix Length"="*"
"Remote Port"="*"
"Remote IP"="*"
"Remote IP Prefix Length"="*"
"DSCP Value"="46"
"Throttle Rate"="-1"
```

> 💡 **联动说明**：本优化项已在 `tweakbyjie` 的 **[Part 12 竞技游戏网络 QoS 策略管理]** 模块中完整实现，支持一键快照备份、主流竞技游戏自动识别写入与安全还原。

---

## 4. 现代 TCP 协议栈优化与常见误区辨析

在分析以 Kiwi-Tweaks 为代表的社区优化方案时，有两项关键网络参数必须严谨对待：

### ✅ 推荐优化：启用 TCP CUBIC 与 SACK
```cmd
netsh int tcp set supplemental Internet congestionprovider=cubic
netsh int tcp set global autotuninglevel=normal
```
- **CUBIC 拥塞控制算法**：相比旧版 Windows 默认的 Compound TCP，CUBIC 具备更好的带宽探测效率与丢包恢复能力，在高带宽、中长延迟网络下连接更平稳；
- **SACK（Selective Acknowledgment，选择性确认）**：允许接收方只请求重传丢失的数据段，而不是重传整个窗口，大幅减少重传开销。

### ❌ 严禁避坑：盲目关闭窗口自动调优（`autotuninglevel=disabled`）
- 部分陈旧优化文章建议将 `autotuninglevel` 设为 `disabled`。在 Windows 10/11 与千兆宽带普及的今天，一旦关闭该功能，TCP 接收窗口将被锁死在 64KB，导致宽带下载速率直接从 1000Mbps 暴跌至几 Mbps！因此**必须保持 `normal` 级别**。

---

## 5. 风险与边界总结

1. **反作弊安全性**：QoS 策略属于 Windows 组策略原生支持的无侵入网络标记，不修改游戏内存或二进制代码，与 Riot Vanguard、EasyAntiCheat、BattlEye、VAC 等完全兼容；
2. **路由器协同**：若家用路由器开启了基于 DSCP / 802.1p 的 QoS 队列调度，加速效果更明显；若路由器为无 QoS 功能的基础交换机，则依然在本地 Windows 网络输出队列中享有最高优先级。
