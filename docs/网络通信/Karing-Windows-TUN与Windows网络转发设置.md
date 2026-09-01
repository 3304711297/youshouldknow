---
applies_to:
  - Windows 10
  - Windows 11
  - Karing 客户端
risk: medium
tweak_module: []
---

# Karing Windows TUN、系统代理与 Windows 网络转发

## 一、适用场景

本文适用于 Windows 电脑使用 **Karing**，尤其是以下场景：

- Karing 使用 TUN 模式接管系统流量；
- 同时开启 Windows 系统代理；
- Windows 电脑通过手机热点上网；
- 希望减少 TUN 与 Windows 路由转发之间产生的路由回环问题。

> 本文针对“电脑作为普通终端使用”的情况。若 Windows 本身承担路由器、网关、网络共享或特殊虚拟网络转发功能，请不要直接照搬关闭转发的设置。

## 二、系统代理与 TUN 不是一回事

Karing 中的 **系统代理** 和 **TUN** 都属于代理软件的入站方式，但作用不同。

### 系统代理

Windows 系统代理主要影响遵循 Windows 系统代理设置的程序。

优点：

- 配置简单；
- 对支持系统代理的浏览器和应用非常方便；
- 不需要虚拟网卡。

缺点：

- 不遵循系统代理的软件不会自动经过代理；
- 某些游戏、后台程序及特殊网络程序可能不会使用系统代理。

### TUN

TUN 会通过虚拟网卡接管系统网络流量，使大量不支持系统代理的软件也能够进入 Karing 的流量处理链路。

因此，**系统代理 + TUN 可以同时开启**，两者并不代表同一层面的功能。

Karing 官方也明确说明：系统代理和 TUN 是两种不同的代理入站方式；系统代理依赖应用适配，而 TUN 通过虚拟网卡重定向系统中的大量网络请求。

## 三、规则模式与 TUN/系统代理的关系

需要特别区分：

- **系统代理 / TUN**：决定流量如何进入 Karing；
- **规则 / 全局**：决定进入 Karing 后，流量如何选择直连或代理出站。

因此，对于日常使用，一般推荐：

```text
系统代理：开启
TUN：开启
模式：规则
```

规则模式可以按照 Karing 的分流规则，让不同目标分别走直连或代理，而不是把所有流量强制通过同一个节点。

## 四、Windows 网络转发是什么

Windows 网卡的 **Forwarding（数据包转发）** 与 Karing TUN 完全不是同一个功能。

简单理解：

```text
普通电脑：
网络 → Windows → 应用

开启 Forwarding 后：
网络接口 A → Windows → 网络接口 B
```

开启 Forwarding 后，Windows 可以承担类似“路由器”的数据包转发角色。

如果普通电脑并不需要充当路由器或网关，通常没有必要主动开启网卡 Forwarding。

## 五、为什么 Karing TUN 要关注 Windows Forwarding

Karing 官方 FAQ 指出，在 Windows 开启 TUN 后，如果 `karingservice.exe` 出现异常高 CPU 或内存占用，其中一个可能原因就是 **Windows 数据转发开启导致路由回环**。

因此，对于不需要让 Windows 充当路由器的普通终端，可以检查并关闭不必要的 Forwarding。

## 六、检查 Windows 是否开启网络转发

使用 **管理员 PowerShell** 执行：

```powershell
Get-NetIPInterface | Where-Object {$_.Forwarding -eq 'Enabled'}
```

如果没有输出，通常表示没有发现 Forwarding 状态为 Enabled 的网络接口。

如果出现类似结果：

```text
ifIndex InterfaceAlias  AddressFamily Forwarding
------- -------------- ------------- ----------
12      Wi-Fi          IPv4          Enabled
```

说明对应网络接口开启了数据包转发。

也可以使用更直观的格式查看：

```powershell
Get-NetIPInterface |
Where-Object {$_.Forwarding -eq 'Enabled'} |
Format-Table ifIndex,InterfaceAlias,AddressFamily,Forwarding
```

## 七、关闭指定网卡的网络转发

假设需要关闭的网卡名称是 `Wi-Fi`：

```powershell
Set-NetIPInterface -ifAlias "Wi-Fi" -Forwarding Disabled
```

如果接口名称是 `Ethernet`：

```powershell
Set-NetIPInterface -ifAlias "Ethernet" -Forwarding Disabled
```

执行后重新检查：

```powershell
Get-NetIPInterface | Where-Object {$_.Forwarding -eq 'Enabled'}
```

## 八、关闭所有当前已启用的接口转发

如果确认这台 Windows 电脑不需要承担路由器、网关或网络共享等职责，可以使用下面的管理员 PowerShell 命令关闭当前所有已启用的 Forwarding：

```powershell
Get-NetIPInterface |
Where-Object {$_.Forwarding -eq 'Enabled'} |
ForEach-Object {
    Set-NetIPInterface -ifIndex $_.ifIndex -AddressFamily $_.AddressFamily -Forwarding Disabled
}
```

然后再次验证：

```powershell
Get-NetIPInterface | Where-Object {$_.Forwarding -eq 'Enabled'}
```

没有输出，即表示没有发现仍处于 Enabled 状态的接口。

## 九、通过手机热点上网的电脑是否需要 Windows Forwarding

如果网络结构只是：

```text
手机
  ↓
手机热点
  ↓
Windows 电脑
  ↓
Karing
  ↓
Internet
```

Windows 电脑只是热点的客户端，并不承担路由器职责，那么通常**不需要为了正常上网而开启 Windows 网卡 Forwarding**。

关闭 Forwarding 一般不会影响：

- Windows 通过手机热点正常上网；
- 浏览器；
- Steam；
- Discord；
- 普通游戏网络连接；
- Karing TUN；
- Karing 系统代理；
- 普通 Wi-Fi 网络连接。

### 注意

“电脑连接手机热点”和“Windows 开启移动热点给其他设备共享网络”是两种不同场景。

如果 Windows 还需要作为网络共享设备、软路由或网关，让其他设备通过这台电脑访问网络，则不能简单认为 Forwarding 可以关闭，应根据实际网络拓扑重新配置。

## 十、关闭 Forwarding 后手机热点暂时断网的处理

在部分 Windows + 手机热点环境中，修改网卡 Forwarding 后，网络接口或热点连接可能不会立即重新初始化。此时可能出现：

- Forwarding 已经关闭；
- 手机热点仍显示连接；
- 但普通网页暂时无法打开；
- Karing 也可能暂时无法正常建立网络连接。

如果确认只是刚刚修改了 Forwarding 后出现这种情况，可以先**断开手机热点，再重新连接手机热点**。

重新连接会让 Windows 重新初始化当前 Wi-Fi 网络接口、IP 配置和路由状态。实际排查时，如果重新连接热点后网页恢复正常，通常无需因为这一次短暂断网而重新开启 Forwarding。

推荐排查顺序：

1. 先确认手机热点本身仍然正常；
2. 断开 Windows 与手机热点的连接；
3. 重新连接手机热点；
4. 测试普通网页是否恢复；
5. 再测试 Karing；
6. 如果仍然无法联网，再检查 IP、默认网关、DNS、Karing TUN 和 Forwarding 状态。

> **经验提示：** 修改 Forwarding 后出现的短暂断网，不一定意味着 Forwarding 必须保持 Enabled。先重新连接热点是成本最低、最值得尝试的恢复方法。

## 十一、推荐的 Karing Windows 配置

对于普通 Windows 终端，并且电脑通过手机热点上网，可以优先考虑：

| 项目 | 推荐设置 |
| --- | --- |
| Karing 连接 | 开启 |
| Windows 系统代理 | 开启 |
| Karing TUN | 开启 |
| Karing 出站模式 | 规则 |
| Windows 网卡 Forwarding | 关闭（不需要路由转发时） |
| 其他代理软件 TUN | 关闭，避免多个 TUN 冲突 |

整体流量关系可以理解为：

```text
                    ┌─ 遵循系统代理的程序 ─┐
                    │                       ↓
手机热点 → Windows → Karing → 分流规则 → 直连/代理
                    │                       ↑
                    └─ TUN 接管的其他程序 ──┘
```

## 十二、遇到 Karing TUN 异常时的排查顺序

如果开启 TUN 后出现 `karingservice.exe` CPU/内存异常、网络异常或疑似回环，可以按下面顺序检查：

1. 确认没有同时运行其他 Clash、sing-box、v2rayN 等 TUN/VPN 软件；
2. 检查 Windows 是否启用了网卡 Forwarding；
3. 如果不需要路由转发，关闭 Forwarding；
4. 如果刚修改 Forwarding 后手机热点暂时断网，先断开并重新连接热点；
5. 检查 Karing TUN 的自动路由设置；
6. 如果 Windows 自己开启了移动热点并进行网络共享，检查是否因此产生额外的路由关系；
7. 重新启动 Karing，再观察 `karingservice.exe` 的 CPU 和内存占用。

## 十三、什么时候不要关闭 Forwarding

以下情况不要在不了解网络拓扑的情况下直接关闭：

- Windows 作为软路由；
- Windows 作为局域网网关；
- 需要让其他设备通过 Windows 转发网络；
- 某些虚拟化、容器或网络实验环境依赖 IP 转发；
- 使用特殊 VPN、桥接或路由方案。

## 十四、官方资料

- [Karing 官方 FAQ](https://karing.app/faq)
- [Karing 官方设置说明](https://karing.app/app-manual/settings)
- [Karing 官方快速使用教程](https://karing.app/quickstart)
- [Karing 官方 GitHub FAQ 文档](https://github.com/KaringX/karing-docu/blob/main/docs/faq.md)

> 核心结论：**Karing TUN 和 Windows Forwarding 是两个不同的功能。普通 Windows 电脑通过手机热点上网、使用 Karing TUN 时，如果不需要让 Windows 承担路由器/网关职责，可以关闭不必要的网卡 Forwarding；系统代理和 TUN 则可以同时开启。如果修改 Forwarding 后手机热点暂时断网，可以先重新连接热点，让网络接口重新初始化。**

## 事实核查记录

核验基准：Windows 网络机制与 Karing 官方文档（上次 2026-08-21；2026-08-29 重核）。

| 声明 | 核查结果 |
| --- | --- |
| 系统代理与 TUN 是两种不同入站方式 | ✅ 属实（2026-08-29 重核：Karing 官方 FAQ“系统代理和TUN的区别是什么”一节原文确认，两者均为入站方式、与规则/全局无关） |
| Windows Forwarding（IP 路由转发）影响热点共享与 TUN 场景 | ✅ 属实（2026-08-29 重核：FAQ“karingservice.exe内存及CPU占用超高”条目仍列“开启 Windows 数据转发导致路由回环”为原因，并给出相同的查询/禁用命令；`Get-NetIPInterface`/`Set-NetIPInterface` 为 Windows 机制，可复现） |
| Karing 客户端的具体行为与规则模式说明 | ⚠️（2026-08-29 重核：最新版本 v1.2.24.2707，2026-08-28 发布，GitHub 预发布渠道活跃；官方文档确认 TUN 为自带独立虚拟网卡实现，Windows 端需管理员权限并自动安装驱动。正文“自带 TUN 不等于依赖系统 NDIS 枚举器，可禁用 Forwarding 但无法确认时不要盲禁”的结论仍成立。行为细节仍随上游版本变化，karing.app/faq 已复核；GitHub 仓库内 faq.md 页面当日网络超时未能直接打开，以 karing.app/faq 为准） |
