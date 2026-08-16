# 排查阻止 Windows 自动进入睡眠的程序

> **分类**：系统知识 · 电源管理
>
> **适用场景**：电脑设置了自动睡眠但迟迟不入睡时，找出正在阻止睡眠的程序或设置；以及相关的「睡了又被莫名唤醒」问题的排查命令。
>
> 本文方法已对照微软官方文档（Microsoft Learn）与社区经验交叉验证，核查记录见文末。

---

## 先区分两类问题

| 现象 | 问题类型 | 关键工具 |
| --- | --- | --- |
| 到时间了不睡觉（屏幕关了主机还醒着 / 根本不睡） | **入睡被阻止** | `powercfg /requests` |
| 睡着了却自己醒过来 | **被唤醒** | `powercfg /lastwake`、事件查看器 |

## 方法一：powercfg /requests（核心方法）

1. 按 `Win + X`，选择「终端(管理员)」或「Windows PowerShell(管理员)」；
2. 输入：

   ```bat
   powercfg /requests
   ```

3. 输出按类别列出正在阻止睡眠的进程 / 驱动：

   | 类别 | 含义 |
   | --- | --- |
   | `DISPLAY` | 阻止关闭显示器的请求 |
   | `SYSTEM` | 阻止系统进入睡眠的请求 |
   | `AWAYMODE` | 「离开模式」请求（系统看似睡眠实则继续运行，常被视频/下载软件使用） |
   | `PERF` | 性能模式请求 |

4. 记下对应进程名（如某网盘、下载器、播放器），在软件设置里关闭其「阻止休眠 / 离开模式」选项，或退出该软件后再次运行命令确认列表已清空。

> 📌 该命令为微软官方文档记载的标准用途：枚举应用与驱动的电源请求（Power Requests 阻止计算机关闭显示器或进入低功耗睡眠）。需要管理员权限；若输出显示「无」却仍不睡眠，继续往下排查。

## 方法二：其他 powercfg 排查命令

```bat
powercfg /waketimers            :: 列出活动的唤醒定时器（计划任务定时唤醒系统）
powercfg /systemsleepdiagnostics :: 生成睡眠转换诊断报告（HTML，含阻止睡眠的组件）
powercfg /lastwake              :: 查看最近一次唤醒源
powercfg /devicequery wake_armed :: 列出被允许唤醒系统的设备
```

均需管理员权限。其中 `systemsleepdiagnostics` 生成的报告会直接指出睡眠转换被哪些组件阻止，适合疑难情况。

## 方法三：检查电源选项高级设置

`Win + R` → 输入 `control` → 电源选项 → 更改计划设置 → 更改高级电源设置：

1. **多媒体设置 → 当共享媒体时**：若为「阻止在空闲时进入睡眠」，则任何媒体共享（包括某些播放器后台状态）都会阻止入睡——改为「允许计算机进入离开模式」或「允许计算机睡眠」；
2. **睡眠 → 在此时间后睡眠**：确认为合理数值，且未被「从不」；
3. **睡眠 → 允许唤醒定时器**：与「睡不着」无关，但影响「睡了被定时任务弹醒」，可按需禁用。

## 方法四：事件查看器（用于唤醒问题）

按 `Win + X` → 事件查看器，依次展开：

```text
应用程序和服务日志 → Microsoft → Windows → Power-Troubleshooter → Operational
```

该日志中的事件 ID 1（「系统已从低电量状态返回」）包含**睡眠时间、唤醒时间、唤醒源（Wake Source）**三个关键字段，是定位「谁把我叫醒」的标准位置。若 Wake Source 显示 `Unknown`，回到方法二用 `lastwake` 和 `devicequery wake_armed` 继续缩小范围。

> ⚠️ 注意：Power-Troubleshooter 日志记录的是睡眠/唤醒转换事件，用于排查**意外唤醒**；排查「无法入睡」应以方法一的 `requests` 为准。

## 方法五：更新驱动程序与系统

- 显卡、网卡驱动过旧或异常是睡眠问题的常见诱因（如网卡驱动持续保持系统唤醒状态）；
- 及时安装 Windows 更新，部分睡眠问题随系统组件更新修复。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| `powercfg /requests` 列出阻止睡眠的程序，按 DISPLAY / SYSTEM / AWAYMODE 等类别显示 | ✅ 属实：微软官方 powercfg 文档——「枚举应用和驱动的电源请求；电源请求会阻止计算机自动关闭显示器或进入低功耗睡眠」 |
| `/waketimers`、`/lastwake`、`/systemsleepdiagnostics`、`/devicequery wake_armed` 的用途 | ✅ 属实：均见于微软官方 powercfg 文档 |
| 事件查看器 Power-Troubleshooter/Operational 日志可查「阻止睡眠的程序」 | ⚠️ 原文说法不准确：该日志记录睡眠/唤醒转换事件（事件 ID 1 含睡眠时间、唤醒时间、唤醒源），标准用途是排查**意外唤醒**；排查入睡受阻应使用 `powercfg /requests`（本文已按正确用途重述） |
| 电源选项中「允许混合睡眠」「允许唤醒定时器」与无法入睡相关 | ⚠️ 部分相关：混合睡眠不阻止入睡；唤醒定时器影响唤醒；真正常见的阻止项是「多媒体设置 → 当共享媒体时 → 阻止在空闲时进入睡眠」（本文已修正归类） |
| 更新显卡/网卡驱动与系统有助于解决睡眠问题 | ✅ 属实：网卡驱动保持系统唤醒是社区与厂商支持文档常见诱因 |

**参考来源：**

- [Microsoft Learn — Powercfg command-line options](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/powercfg-command-line-options)
- [Microsoft Learn — PC wakes from sleep on its own（官方问答）](https://learn.microsoft.com/en-us/answers/questions/2564917/pc-wakes-from-sleep-on-its-own-and-boots-after-shu)
- [Super User — Computer wakes by itself, wake source unknown](https://superuser.com/questions/751544/computer-wakes-by-itself-but-wake-source-is-unknown)
- [TenForums — Computer keeps waking up from sleep](https://www.tenforums.com/general-support/166602-computer-keeps-waking-up-sleep-hibernation.html)
- [Dell 社区 — ACPI Wake Alarm 定时唤醒案例](https://www.dell.com/community/en/conversations/inspiron/inspiron-15-5584-wakes-after-180-min-of-sleep-acpi-wake-alarm/647f855cf4ccf8a8de440ac9)
