---
applies_to:
  - Windows 10
  - Windows 11
  - USB/无线外设
risk: medium
tweak_module: []
---

# Windows 键鼠与 TCP 低延迟可选实验设置

> **定位**：高级实验设置，不是通用性能优化。
>
> **适用场景**：希望理解键鼠输入、文件夹视图和 TCP 小包行为的用户，并且能够记录原值、进行 A/B 测试和恢复。
>
> **重要边界**：本文中的设置不会自动加入 `tweakbyjie` 主脚本。输入延迟、游戏线程延迟、网络 RTT 和服务器响应不是同一层问题，修改注册表不能保证降低任何一种延迟。

## 一、先区分三种“延迟”

| 类型 | 主要路径 | 不能用什么替代 |
|---|---|---|
| 输入延迟 | 键盘/鼠标 → HID/驱动 → Windows 消息 → 游戏线程 → 渲染显示 | 不能用 TCP 参数解决 |
| 游戏线程/显示延迟 | CPU 调度、帧时间、GPU 队列、显示刷新 | 不能用键鼠队列值直接解决 |
| 网络延迟 | 应用 → TCP/UDP → 网卡 → 路由/服务器 | 不能用 `Win32PrioritySeparation` 直接解决 |

先测量问题在哪一层，再决定是否尝试设置。测试背景请先阅读[CPU 调度与游戏线程](./CPU调度与游戏线程.md)；正式测试流程见[游戏性能验证流程](../项目导航/游戏性能验证流程.md)。旧的计时器和延迟测试路径仍保留为兼容入口。

## 二、统一实验流程

任何注册表实验都应遵守：

1. 记录 Windows 版本、驱动版本、应用版本和当前设置；
2. 读取并保存目标值的存在状态、类型和值；
3. 每次只修改一组相关参数；
4. 重启或重新连接网络后进行相同场景 A/B 测试；
5. 记录输入延迟、RTT、抖动、丢包、重传、帧时间和稳定性；
6. 没有收益或出现异常时，立即写回原值；原本不存在的值应删除；
7. 不把“设置成功”当作“性能提升”。

## 三、键盘与鼠标设置

### 1. 控制面板设置

键盘重复延迟和重复速度属于用户体验偏好。控制面板中把重复延迟调短、重复速度调快，只会改变按键重复行为，不等于降低 USB/HID 扫描延迟，也不等于提高游戏轮询率。

注册表位置：

```text
HKEY_CURRENT_USER\Control Panel\Keyboard
```

常见值包括：

- `KeyboardDelay`：重复开始前的延迟；常见默认值为 `1`，`0` 通常表示更短延迟；
- `KeyboardSpeed`：重复速度；控制面板可用范围通常是 `0–31`，不建议采用来源不明的 `48`；
- `InitialKeyboardIndicators`：键盘指示灯初始状态，不是输入延迟开关。

修改后应测试文本输入、长按重复、游戏内按键和辅助功能。不要为了“最快”把超出控制面板范围的数值写入系统。

### 2. Keyboard Response 与辅助功能

以下路径与筛选键、粘滞键、重复键等辅助功能有关：

```text
HKEY_USERS\.DEFAULT\Control Panel\Accessibility\Keyboard Response
```

不建议把页面中的所有值批量改成 `0`。这样可能关闭或改变用户主动启用的辅助功能，且不同值承担的功能不同。只有在明确知道某个值的作用、记录原值并确认用户不需要该辅助功能时，才应单独调整。

### 3. 输入队列大小

常见路径：

```text
HKLM\SYSTEM\CurrentControlSet\Services\kbdclass\Parameters
HKLM\SYSTEM\CurrentControlSet\Services\mouclass\Parameters
```

相关值可能包括：

- `KeyboardDataQueueSize`；
- `MouseDataQueueSize`。

“数值越低越好”没有可靠的通用依据。队列过小可能造成输入事件丢失、突发输入处理异常或设备兼容性问题；即使某台机器测试通过，也不能把 `72`、`16` 或 `20` 当作通用答案。

因此本项目不推荐将这两个值加入主脚本，也不推荐普通用户为了游戏延迟主动修改它们。出现输入丢失时，应先检查 HID/芯片组驱动、USB 连接、设备轮询设置、应用和硬件。

## 四、FolderType：文件夹视图实验

可选命令：

```powershell
Set-ItemProperty `
  'HKCU:\Software\Classes\Local Settings\Software\Microsoft\Windows\Shell\Bags\AllFolders\Shell' `
  -Name FolderType `
  -Value NotSpecified `
  -Type String `
  -Force
```

该设置主要影响 Windows 文件夹模板/视图识别，可能减少文件夹类型自动变化带来的困扰。它不是键鼠低延迟、CPU 调度或网络优化，不应宣传为游戏性能提升。

修改前应导出相关注册表项或记录原值；如果文件夹视图异常，恢复原值或删除新增的 `FolderType`，然后重启 Explorer。使用前关闭重要文件操作，避免把界面体验问题误判成性能问题。

## 五、TCPNoDelay 与 TcpAckFrequency

### 1. 适用范围

这两个值常用于测试 TCP 小包发送和 ACK 行为，可能与 Nagle 算法及延迟确认有关。它们只影响特定 TCP 流量，不适用于所有游戏：许多游戏使用 UDP，或者网络延迟主要来自线路、服务器、Wi-Fi、路由和排队。

### 2. 网卡路径

常见路径：

```text
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces\{网卡 GUID}
```

应根据当前网卡实际存在的 `DhcpIPAddress` 或 `IPAddress` 判断接口，不能照抄别人电脑的 GUID。无线、网线、虚拟网卡和 VPN 可能对应不同接口。

常见实验值：

```text
TCPNoDelay       = 1
TcpAckFrequency  = 1
```

这不是全局“低延迟开关”，也不保证游戏 RTT 下降。关闭或改变 Nagle/ACK 行为可能增加小包数量、CPU/带宽开销，某些应用反而更差。

### 3. 测试方法

在修改前后保持以下条件尽量一致：

- 同一网卡、同一网络、同一服务器；
- 同一游戏或应用和同一时间段；
- 记录 RTT、抖动、丢包、TCP 重传和游戏内网络统计；
- 同时观察 CPU 占用、吞吐量和其他应用网络表现；
- 每组设置至少测试多次，避免把一次线路波动误认为效果。

如果应用主要使用 UDP，这两个值可能基本没有意义。不要只用测速网站的瞬时延迟作结论。

### 4. 恢复方法

修改前记录目标接口 GUID、值是否存在、注册表类型和值。实验结束后：

- 有原值：写回原类型和值；
- 原本不存在：删除新增值；
- 多个网卡：逐接口检查并恢复；
- 重启网络适配器或系统后，再确认应用行为。

不要批量遍历所有接口写入相同值，也不要在没有备份的情况下删除未知 TCP 参数。

## 六、不建议采纳为主脚本的项目

以下内容不应加入 `tweakbyjie` 的普通优化菜单：

- `KeyboardSpeed=48`；
- 把 `KeyboardDataQueueSize` 或 `MouseDataQueueSize` 调到“越低越好”；
- 批量清零 `Keyboard Response`；
- 无差别给所有网卡写入 `TCPNoDelay=1` / `TcpAckFrequency=1`；
- 用 `FolderType` 宣称提高游戏性能。

原因是它们缺少统一安全默认值，收益依硬件/应用/网络环境变化，且输入丢失、辅助功能异常或网络性能下降的恢复成本高于潜在收益。

## 七、与 tweakbyjie 的关系

当前 `tweakbyjie` 没有执行上述键鼠队列、FolderType 或 Nagle/TCP 参数。它已有的 CPU 调度、MMCSS、HAGS、Games 任务和搜索设置不能与这些实验项混为一谈。

如果未来要实现实验模块，至少需要：

- 只读检测当前状态；
- 结构化备份并记录不存在状态；
- 单项启用和独立恢复；
- 修改后回读验证；
- 明确显示风险和重启/网络重置要求；
- 默认不执行。

目前建议把本文作为知识参考，不修改主脚本。

## 事实核查记录

核验基准：Windows 设置/注册表机制（2026-08-29 重核：机制类内容稳定，无需实质变更；键鼠队列、FolderType 与 Nagle/TCP 实验项已对照 tweak 源码 HEAD b905950 复核，主脚本仍无对应执行项）。

| 声明 | 核查结果 |
| --- | --- |
| TCPNoDelay/TcpAckFrequency 位于各网卡接口的 Tcpip\Parameters\Interfaces 子键 | ✅ 属实：微软文档记载的接口级参数 |
| 关闭 Nagle/Delayed ACK 对游戏的实际收益 | ⚠️ 机制真实但收益依赖应用是否已做小包合并，社区结论不一，正文已要求实测 |
| Keyboard Response（辅助功能）与输入队列大小设置 | ✅ 属实：系统内置功能，路径可复现 |
| FolderType 文件夹视图实验 | ⚠️ 单机实验记录，效果未跨版本验证 |
| 本文整体定位为"可选实验、默认不进主脚本" | ✅ 与 tweakbyjie 源码一致：无对应执行项 |
