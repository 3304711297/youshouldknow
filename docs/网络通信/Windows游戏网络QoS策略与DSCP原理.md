---
status: stable
risk: low
applies_to:
  - Windows 10 (21H2+)
  - Windows 11 (22H2/23H2/24H2)
verified_on: "2026-09-03"
tweak_module:
  - "12"
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

> 💡 **联动说明**：本优化项已在 `tweakbyjie` 的 **[Part 12 竞技游戏网络 QoS 策略管理]** 模块中完整实现，支持一键快照备份、主流竞技游戏（含 CS2、Valorant、Apex、Minecraft Java 版与基岩版等 13 款游戏）自动识别写入与安全还原。

---

## 4. 现代 TCP 协议栈优化与常见误区辨析

在分析以 Kiwi-Tweaks 及民间网络优化工具为代表的社区方案时，有两项关键网络参数必须严谨对待：

### ✅ 推荐优化：保持 TCP CUBIC 与 SACK（拒绝旧版 CTCP）
```cmd
netsh int tcp set supplemental Internet congestionprovider=cubic
netsh int tcp set global autotuninglevel=normal
```
- **CUBIC 拥塞控制算法（RFC 8312）**：Windows 10 1709+ 客户端默认已全面转向 CUBIC。部分陈旧优化器（如 ALit-NetworkOptimizer）仍强制改写为 Vista/Win7 时代的 Compound TCP (CTCP)。CUBIC 具备更好的带宽探测效率与丢包恢复能力，在高带宽、中长延迟网络下连接更平稳，切忌降级回退为 CTCP；
- **控制对象辨析（TCP vs UDP）**：绝大多数竞技网游（如 CS2、Valorant、Apex、Minecraft 基岩版）的核心游戏数据包走 **UDP** 协议，TCP 拥塞控制参数对其游戏实时交互毫秒级延迟**完全不生效**，属于典型的调优对象错位；
- **SACK（Selective Acknowledgment，选择性确认）**：允许接收方只请求重传丢失的数据段，而不是重传整个窗口，大幅减少重传开销。

### ❌ 严禁避坑：盲目关闭窗口自动调优（`autotuninglevel=disabled`）
- 部分陈旧优化文章建议将 `autotuninglevel` 设为 `disabled`。在 Windows 10/11 与千兆宽带普及的今天，一旦关闭该功能，TCP 接收窗口将被锁死在 64KB，导致宽带下载速率直接从 1000Mbps 暴跌至几 Mbps！因此**必须保持 `normal` 级别**。

---

## 5. 风险与边界总结

1. **反作弊安全性**：QoS 策略属于 Windows 组策略原生支持的无侵入网络标记，不修改游戏内存或二进制代码，与 Riot Vanguard、EasyAntiCheat、BattlEye、VAC 等完全兼容；
2. **端到端边界：QoS 标记 ≠ 绝对广域网提速**：
   - DSCP 46（EF）在 RFC 3246 中被定义为每跳行为（Per-Hop Behavior, PHB）。它的实际生效高度依赖本地网卡驱动、局域网交换机/家庭路由器（如 WMM 语音队列映射）；
   - 一旦数据包离开家庭网关进入公网，绝大多数电信运营商（ISP）会将出站流量的 DSCP 字段重写（Remark）或置零重置为 Best Effort。因此，DSCP 46 的核心价值在于**解决本机至局域网家庭网关之间的排队挤塞与缓冲区膨胀（Bufferbloat）**，绝不能宣传为“穿透全网的绝对优先权”；
3. **启动器与分类器作用域（以 Minecraft 为例）**：
   - **Java 版启动器兼容性**：第三方启动器（PCL2、HMCL）拉起自定义路径的 JRE 时，Windows QoS 策略通过文件名（`javaw.exe`）进行匹配即可跨路径命中，无需固化绝对路径；其副作用是所有名为 `javaw.exe` 的图形程序均会被同等标记；
   - **基岩版 UWP 进程隔离**：UWP 虽然运行在 AppContainer 沙箱内，但网络套接字仍正常受底层 NDIS QoS 策略监管；
   - **避免硬编码端口**：Minecraft 默认端口为 Java 25565 / 基岩版 19132，但大量私设服务器使用自定义端口。基于进程名（AppPathNameMatchCondition）的分类器比限制特定端口更具普适性与鲁棒性。
