---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# Windows 网络栈优化原则

> **定位**：网络主题主文，负责分层判断“该动哪一层”。
>
> 代理/TUN 的具体排障见 [Karing Windows TUN 与 Windows 网络转发设置](./Karing-Windows-TUN与Windows网络转发设置.md)，运营商频段与 APN 见 [四大运营商频段速率与 APN 设置速查](./四大运营商频段速率与APN设置速查.md)。

## 一、网络优化不是改越多越好

网络问题的层次不同，解法也不同：

- **输入链路延迟**（键鼠采样 → HID → 游戏主线程）不靠 TCP 参数解决；
- **帧时间与 DPC 延迟**（驱动/调度）不靠带宽优化解决；
- **服务器 RTT 与路由**（运营商/节点/跨网）不靠本机注册表解决。

先测量，再选层：不要把所有“优化”一次性写入，再用主观感受判断。

## 二、分层模型

```text
应用/游戏 ↔ Windows 网络栈 ↔ 网卡驱动/硬件 ↔ 链路/运营商 ↔ 代理/TUN（如有） ↔ 远端服务器
         TCP/IP 参数   缓冲/队列/中断   信号/频段/APN   分流规则   路由与负载
```

| 层次 | 关键对象 | 典型可选项 | 风险 |
|---|---|---|---|
| TCP/IP 参数 | Nagle、Delayed ACK、ECN、RWIN/窗口缩放、拥塞控制 | 注册表/ `netsh` | 改错导致重传、抖动或兼容性下降 |
| 网卡驱动 | 中断节流、RSS、电源管理、 offload | 驱动设置/设备管理器 | 影响稳定性与功耗 |
| 缓冲与队列 | 接收/发送缓冲、队列深度 | 驱动/系统默认值 | 过大增加排队延迟，过小丢包 |
| 后台服务 | 更新、云同步、遥测、后台下载 | 服务/任务管理器 | 关闭不当影响功能 |
| 代理/TUN | TUN/系统代理/Forwarding | Karing/Clash 配置 | 多 TUN 冲突、回环、CPU 飙升 |

## 三、低延迟 vs 高吞吐：关注点不同

| 目标 | 优先关注 | 典型指标 | 常见误区 |
|---|---|---|---|
| 低延迟（游戏/实时通信） | 数据包处理路径、队列等待、驱动 DPC、中断与调度 | RTT、抖动、丢包、1% Low 与输入延迟 | 只改带宽参数不测 RTT |
| 高吞吐（下载/备份/推流） | 带宽利用率、缓冲与并发、稳定性 | 峰值/均值吞吐、重传率 | 只压延迟参数不测吞吐 |

两者常互斥：为低延迟收紧缓冲可能降低峰值吞吐；为吞吐放大窗口可能增加排队延迟。按场景选目标，不要追求“全都要”。

## 四、关键参数的适用边界

> 以下为机制说明与适用判断，具体阈值取决于 Windows 版本、网卡与链路，必须实测。

- **Nagle / Delayed ACK**：合并小包以省带宽，实时交互可能增加等待；是否关闭取决于应用是否已做小包优化。
- **ECN**：拥塞显式通知，利于拥塞控制，但需链路与对端支持。
- **接收窗口与窗口缩放（RWIN）**：影响高带宽高延迟链路的吞吐；窗口过大在拥塞时增加排队。
- **拥塞控制算法**：不同算法在丢包/抖动下的表现不同，选型需结合链路特征与实测。
- **中断节流 / RSS / Offload**：网卡将数据包分发到多核与卸载计算，配置不当可能增加 DPC 或丢包。

不要把某篇教程的“固定值”当作所有机器的通用答案；改前记录原值，改后做前后对照。

### 4.1 `netsh int tcp` 常用开关的官方语义与风险

社区"网络优化第一期"类教程常见两条命令：`autotuninglevel=experimental` 与 `timestamps=enabled`。二者都是**合法参数**，但语义常被夸大：

| 命令 | 官方语义 | 实际影响与风险 |
| --- | --- | --- |
| `netsh int tcp set global autotuninglevel=experimental` | 接收窗口自动调优的**最高档**，"允许接收窗口增长以适应极端场景" | 官方文档把 `normal` 描述为"适应几乎所有场景"，`experimental` 是为**极端场景**准备的非默认档位。它不叫"最大化吞吐"，把窗口放到极端会放大排队延迟；在普通游戏/浏览场景下与 `normal` 的差异往往测不出来，却更容易在拥塞或对端窗口受限时出现抖动 |
| `netsh int tcp set global timestamps=enabled` | 在**出站**协商时间戳、在对端协商后**入站**启用 | 与 `allowed`（默认，仅在对端协商时入站启用）的差别在出站协商。它测量 RTT 更精确，代价是每个报文多若干字节头部开销，且在异常对端上可能引入兼容性问题 |
| `netsh int tcp set global rss=enabled` | 接收端缩放，把收包处理分散到多核 | 现代网卡与系统默认多已启用；单核尖峰问题优先查 RSS/VMQ 配置而非盲目重设 |
| `netsh int tcp set global rsc=disabled` | 关闭接收段合并 | 关闭后 CPU 每包处理开销上升，通常只在特定抓包/虚拟化场景需要 |

查看当前值：`netsh int tcp show global`；恢复默认：把参数设回 `default`（如 `netsh int tcp set global autotuninglevel=default`）或重启网络适配器。

> 判断原则：这类全局参数影响**所有** TCP 连接。若目标是游戏的低延迟，先确认游戏的网络层用的是 UDP 还是 TCP、瓶颈在 RTT 还是丢包——改全局参数通常不是最直接的杠杆。

### 4.2 更换 DNS 的取舍与正确测量方式

"精准选择地区 DNS"是社区常用手法，做法本身合理，但**推荐值要按自己的链路实测**，不能照抄：

```powershell
# 正确的测量方式：直接测解析耗时（每个服务器多测几次取平均/最小值）
1..5 | ForEach-Object {
  foreach ($s in '223.5.5.5','119.29.29.29','180.76.76.76','114.114.114.114') {
    $m = Measure-Command {
      Resolve-DnsName -Name 'www.example.com' -Server $s -Type A -DnsOnly -QuickTimeout -ErrorAction SilentlyContinue
    }
    "{0,-18} {1,7:N1} ms" -f $s, $m.TotalMilliseconds
  }
}
```

要点：

- **不要用 `ping` 代替 DNS 测试**。ICMP 常被运营商或目标网络限速/丢弃，本机实测中多个国内公共 DNS 的 `Test-Connection` 全部返回 0 ms（被拦或未计），而 `Resolve-DnsName` 给出的解析耗时差异明显（实测 `223.5.5.5` 平均约 27 ms，`114.114.114.114` 平均约 61 ms）——**ping 延迟低 ≠ 解析快**，二者是不同链路。
- 社区教程常推荐的 `114.114.114.114` 并非通用最优解，需按自己的运营商与地区实测。
- 加密 DNS（DoH/DoT）与 Fake-IP 分流的取舍见本文第九节。

### 4.3 网卡协议绑定的精简

在"网络连接 → 网卡属性"里取消勾选不用的协议/服务（如部分虚拟化协议、旧版隧道组件）可减少协议栈处理路径，属于**可逆、低风险**的操作：改前截图记录勾选状态，出问题勾回来即可。

但要注意：取消勾选必须逐个确认用途，尤其 `Internet 协议版本 4 (TCP/IPv4)` 是必需项；`客户端 Microsoft 网络`/`文件和打印机共享` 视是否使用局域网共享决定。IPv6 相关组件在下文另有说明，不建议整块关闭。

### 4.4 IPv6 隧道组件（Teredo / 6to4 / ISATAP）

Teredo、6to4、ISATAP 是 IPv6 过渡期的隧道技术，用于在纯 IPv4 网络上打通 IPv6。它们与"主 IPv6 协议栈"不是一回事：

| 组件 | 作用 | 常见默认状态（本机实测，Windows 11 26200） |
| --- | --- | --- |
| Teredo | 通过 NAT 穿透建立 IPv6 隧道 | `Type: disabled`、`State: offline` |
| 6to4 | 通过 IPv4 中继提供 IPv6 | `Service State: default` |
| ISATAP | 企业网内 ISATAP 路由隧道 | `State: default` |

社区网络优化常把三者的 `disabled` 命令当作"降低延迟"手段。机制上它们**只在特定过渡场景生效**，在现代网络环境下多数用户本就不走这些路径，关闭它们的收益通常是"减少极少数场景下的额外路径"，而非普遍降延迟；若所在网络确实依赖 IPv6（如教育网、部分运营商 IPv6 优先场景），错误处理可能让 IPv6 能力丢失。

```bat
:: 状态查询（只读）
netsh interface teredo show state
netsh interface 6to4 show state
netsh interface isatap show state

:: 若确需关闭（本机实测当前 Teredo 已为 disabled/offline）
netsh interface teredo set state disabled
netsh interface 6to4 set state disabled
netsh interface isatap set state disabled

:: 恢复
netsh interface teredo set state default
netsh interface 6to4 set state default
netsh interface isatap set state default
```

> ⚠️ 不要与"关闭 IPv6 协议本身"混为一谈。关闭 IPv6 栈会影响依赖它的功能（部分游戏 P2P、Xbox 网络、Windows 更新分发），属于另一类取舍，不在本文推荐范围。

## 五、网卡驱动侧的检查

1. 驱动版本与来源（OEM/芯片厂商/Windows Update 的差异）；
2. 设备管理器 → 网卡属性 → 高级：中断节流、RSS、节能/唤醒、流控等；
3. 电源管理：`允许计算机关闭此设备以节约电源` 与 `唤醒` 的取舍；
4. 有线/无线/热点 的差异：热点场景关注 [Karing 专题](./Karing-Windows-TUN与Windows网络转发设置.md) 的 Forwarding 回环。

## 六、测试方法

修改前后固定：游戏/服务器/分辨率/驱动/电源计划/后台程序/网络接入方式。

至少对比：

- **RTT / 抖动 / 丢包**（`ping` / `tracert` / 游戏内网络面板）；
- **吞吐**（下载/上传均值与峰值、重传率）；
- **帧时间与 1% Low**（网络参数不应以牺牲帧稳定为代价）；
- **CPU 占用与 DPC**（网络驱动异常会反映为 DPC 尖峰）。

单次跑分或单服务器样本不能作为结论；不要同时改 CPU 调度、电源与网络参数。

## 七、与 tweakbyjie 的关系

在传输层参数上，`tweakbyjie` 坚持克制原则，**不包含盲改 TCP/IP 协议栈（如 TcpAckFrequency/TCPNoDelay 等易产生负优化的脆弱参数）的项**；此类网络栈调优属于知识与实测方法，不计为自动化执行覆盖。

但在系统行为与网络安全防御层，`tweakbyjie` 在 **Part 1 核心优化（子项 2 系统行为优化）** 中收录了 `EnableActiveProbing` 优化项（关闭 NCSI 主动网络探测），以防御运营商 DNS 劫持触发的流氓自动弹窗并减少后台网络探针遥测，同时支持快照完整恢复。

涉及代理/TUN/Forwarding 的排障，按 [Karing 专题](./Karing-Windows-TUN与Windows网络转发设置.md) 的“入站方式 vs 出站规则”与 Forwarding 检查步骤执行。

## 八、风险与恢复

- 改前记录：Hive/路径/值名/类型/原值/是否存在、驱动版本、备份点；
- 改后验证：配置层回读 + 运行时 A/B（RTT/抖动/吞吐）+ 重启/睡眠/唤醒稳定性；
- 恢复：逐项写回原值，原本不存在的值应删除；不要用另一台机器的值当通用恢复值。
- 任何影响系统更新、后台同步或安全的功能性服务，关闭前确认依赖与可恢复路径。

## 九、运营商 DNS 劫持与 Windows NCSI 探测机制防御

### 1. 典型案例与异常表象（2026-07-21 中国移动事件）

在 2026 年 7 月 21 日，我国部分地区（如西南节点）的中国移动网络用户遭遇大面积异常：**设备开机或连网瞬间，系统自动拉起浏览器并强制跳转到网络赌博、博彩等非法网页**。

多数用户误以为电脑感染了木马病毒或流氓软件，但实际根因是：**非法组织对运营商递归 Local DNS 实施投毒劫持，将微软官方网络检测域名解析定向篡改，进而巧妙利用了 Windows 自身的连网认证机制**。

### 2. 底层机理：NCSI 主动探针与 Captive Portal 的“武器化”

Windows 系统的网络位置感知服务（`NlaSvc`）内置了 **NCSI（Network Connectivity Status Indicator，网络连接状态指示器）**。每当网卡连接网络或 IP 发生变动时，系统会发起主动探测（Active Probing）：

1. **域名解析**：系统向本地配置的 DNS 请求解析 `www.msftconnecttest.com`；
2. **HTTP 探针**：向 `http://www.msftconnecttest.com/connecttest.txt` 发起轻量 GET 请求，预期收到内容为 `Microsoft Connect Test` 且状态码为 `200 OK` 的应答；
3. **状态判定与 Captive Portal 唤醒**：
   - 若收到预期应答，系统判定网络具备完整 Internet 访问权限；
   - 若收到 **HTTP 302/307 重定向** 或返回非预期网页，Windows 会判定当前处于机场、酒店、咖啡馆等**公共 Wi-Fi 的 Web 强制门户认证（Captive Portal）**环境；
   - 此时，Windows 底层会自动唤起系统默认浏览器访问该重定向地址，方便用户输入账号密码完成连网认证。

**黑产利用链路**：黑客篡改了运营商 Local DNS 中 `msftconnecttest.com` 等域名的解析，返回恶意站点的 IP 并附带 302 重定向。Windows 的 NCSI 探针请求被劫持后，误以为是认证热点，遂**忠实地执行了“帮用户拉起浏览器打开网页”的系统行为**，形成了无毒却全屏弹非法页面的破坏效果。

### 3. 三层防御体系（从标到本）

针对该机制漏洞，可从系统触发层、域名解析层和传输虚拟化层建立三道防线：

| 防御层级 | 实施方案 | 防护效果 | 代价与副作用 |
| :--- | :--- | :--- | :--- |
| **第一层：系统级阻断（治标）** | 修改注册表将 `EnableActiveProbing` 设为 `0` | 彻底切断 Windows 发起主动探针与自动调起浏览器的触发链路，连网零骚扰 | 在需要 Web 认证的公共 Wi-Fi 下不会自动弹登录窗（需手动打开浏览器输入 `1.1.1.1`）；任务栏网络图标小概率偶发感叹号/地球标（实际网络通畅） |
| **第二层：网络层换源（局部缓解）** | 路由器/本机更换为公共 DNS（如 `114.114.114.114`、`223.5.5.5`） | 绕开运营商被污染的递归节点，恢复正常域名解析 | 若运营商部署了基于 UDP 53 端口的**旁路镜像或透明劫持**，明文 DNS 请求依然会被强行篡改 |
| **第三层：加密与分流（治本）** | 启用 **DoH / DoT 加密 DNS**，或配置 **TUN 模式 Fake-IP 分流** | DNS 请求经 TLS 加密传输或在本地虚构 IP，彻底消除运营商明文劫持的土壤 | 依赖本地代理客户端（如 Karing、sing-box）的持续运行 |

#### 系统级注册表操作指南

- **注册表路径**：`HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\NlaSvc\Parameters\Internet`
- **目标值名**：`EnableActiveProbing`
- **类型**：`REG_DWORD`
- **取值说明**：
  - `1`：开启主动探测（Windows 默认值）；
  - `0`：禁用主动探测（阻断自动弹窗与探针遥测，`tweakbyjie` Part 1 已内置）。

## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-29 重核 HEAD b905950；2026-09-07 补充 NCSI 防御机制核实）。

| 声明 | 核查结果 |
| --- | --- |
| tweakbyjie 没有脆弱 TCP/IP 协议栈的自动注册表/驱动修改项 | ✅ 属实（对全源码检索确认无 TcpAckFrequency/TCPNoDelay 等写入；Part 1 收录的 EnableActiveProbing 属于 NlaSvc 系统行为优化项，不属于传输层 TCP/IP 栈参数） |
| Nagle/Delayed ACK/ECN/RWIN/拥塞控制的机制描述 | ✅ 属实（通读确认与 TCP/IP 通行技术资料一致，机制类内容无时效变化，正文已声明阈值需实测） |
| 低延迟与高吞吐的取舍关系 | ✅ 属实（通读确认，缓冲/窗口参数的两难为通行结论） |
| Windows NCSI EnableActiveProbing 与 Captive Portal 弹窗触发机制 | ✅ 属实（经微软官方文档及 2026-07-21 运营商 DNS 劫持事件交叉验证，NCSI 收到重定向后拉起系统浏览器的逻辑确为系统原生设计） |
| `autotuninglevel=experimental` 的官方定义为"允许接收窗口增长以适应极端场景"，非"最大化性能" | ✅ 属实：微软 netsh interface 官方文档参数表原文列举五档并给出各自定义，`normal` 为"适应几乎所有场景" |
| `timestamps=enabled` 使出站也协商时间戳，默认值为 `allowed`（仅入站按对端协商启用） | ✅ 属实：微软官方文档对 `timestamps` 三档（disabled/enabled/allowed）的说明 |
| `netsh int tcp set global` 支持以 `default` 恢复各项默认值 | ✅ 属实：官方参数表每项均含 `default` 选项 |
| DNS 延迟应直接测解析耗时而非用 ping 判断 | ✅ 属实（2026-09-13 本机实测）：`Resolve-DnsName` 五轮均值 `223.5.5.5`≈26.6 ms、`180.76.76.76`≈35.8 ms、`114.114.114.114`≈61.0 ms；同一批地址 `Test-Connection` 全部返回 0 ms（ICMP 被拦或未计入），证明两类测量不可互替 |
| Teredo/6to4/ISATAP 为 IPv6 过渡隧道组件，与主 IPv6 协议栈不同；本机 Teredo 已为 disabled/offline | ✅ 属实（2026-09-13 本机实测）：`netsh interface teredo show state` 输出 `Type: disabled`、`State: offline`；6to4/ISATAP 均为 `default` |
| 关闭 IPv6 隧道组件与关闭 IPv6 协议栈是两件事，后者会影响依赖 IPv6 的功能 | ✅ 属实：三者仅为过渡隧道技术，主协议栈独立配置 |

