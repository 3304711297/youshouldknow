# 禁用 Windows 通知中心与操作中心

> **分类**：系统知识 · 系统设置
>
> **适用场景**：彻底关闭 Windows 通知中心（Win10 为操作中心），不弹任何应用通知、保持桌面干净；以及托盘图标显示的相关设置。
>
> 本文注册表值已对照微软官方策略文档核实，其中一处流传写法经核实为误用，已勘误，核查记录见文末。

---

## 一、正确方法：DisableNotificationCenter

新建文本文件，粘贴以下内容，保存为 `禁用通知中心.reg` 后双击导入，**注销或重启**生效：

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer]
"DisableNotificationCenter"=dword:00000001
```

- 对应组策略：**用户配置 → 管理模板 →「开始」菜单和任务栏 → 删除通知和操作中心**（启用）；
- **Win10**：整体移除操作中心——通知列表与快捷操作面板（Win + A）一并消失；
- **Win11**：禁用通知中心（时间轴角标与通知列表），不再弹出任何应用通知。

> 📌 官方将该策略定义为**用户级**（写入 HKCU）。部分优化脚本会同时向 `HKLM\SOFTWARE\Policies\Microsoft\Windows\Explorer` 写入同名值，实际起作用的是 HKCU 一处。

**恢复方法**：把上述值改为 `0`（或直接删除该值）后注销重启；用组策略的用户改回「未配置」再 `gpupdate /force` 即可。

**副作用提示**：禁用后**所有应用通知将无处显示**（包括系统更新提醒、安全中心警告等），请确认自己确实想要完全清净。若只是嫌弹窗烦，更温和的方案是：设置 → 系统 → 通知 中关闭个别应用的通知，或开启「勿扰 / 专注模式」。

## 二、勘误：NoAutoTrayNotify 并不能禁用通知中心

一些流传脚本把下面这段与 `DisableNotificationCenter` 并列，标为「禁用通知中心」：

```reg
[HKEY_CURRENT_USER\Software\Policies\Microsoft\Windows\Explorer]
"NoAutoTrayNotify"=dword:00000001
```

**经核实这是误用**，两个问题：

1. **作用不符**：`NoAutoTrayNotify` 是组策略「**关闭通知区域清理**」的注册表值——设为 1 的效果是系统不再收纳隐藏不活跃的托盘图标，即**所有托盘图标常驻显示**，与通知中心的开关无关；
2. **路径也不对**：该值的官方路径是 `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`（旧版资源管理器策略键），写在 `...\Policies\Microsoft\Windows\Explorer` 下不会产生预期效果。

**如果你的真实需求是「显示全部托盘图标」**，正确做法任选其一：

```reg
Windows Registry Editor Version 5.00

[HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer]
"NoAutoTrayNotify"=dword:00000001
```

或更简单：任务栏右键 → 任务栏设置 → 其他系统托盘图标 → 全部开启（图形界面等效操作）。

## 三、相关但不同的值（避免混淆）

| 注册表值 | 真实作用 |
| --- | --- |
| `DisableNotificationCenter`（用户策略键） | 禁用通知中心 / 操作中心 |
| `NoAutoTrayNotify`（旧版 Explorer 策略键） | 关闭通知区域清理，托盘图标全部常驻 |
| `NoTrayItemsDisplay`（同上旧版键） | 隐藏整个通知区域（托盘图标完全不显示，慎用） |

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| `HKCU\Software\Policies\Microsoft\Windows\Explorer\DisableNotificationCenter = 1` 禁用通知中心，注销/重启生效 | ✅ 属实：微软官方 ADMX_Taskbar 策略文档（用户级策略），社区多方实测确认，Win10 移除操作中心、Win11 禁用通知中心 |
| 对应组策略为「删除通知和操作中心」 | ✅ 属实：位于 用户配置 → 管理模板 →「开始」菜单和任务栏 |
| HKLM 同名值可实现机器级禁用 | ⚠️ 官方策略定义为用户级（HKCU）；HKLM 写法见于部分优化脚本，未见官方文档支持 |
| `NoAutoTrayNotify = 1` 可禁用通知中心 | ❌ 误用：该值是「关闭通知区域清理」策略——效果为托盘图标全部常驻显示；且其官方路径为 `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer`，与流传写法不同 |
| `NoTrayItemsDisplay` 隐藏整个通知区域 | ✅ 属实：旧版 Explorer 策略，社区与文档记载一致 |

**参考来源：**

- [Microsoft Learn — Policy CSP ADMX_Taskbar（DisableNotificationCenter 官方策略）](https://learn.microsoft.com/en-us/windows/client-management/mdm/policy-csp-admx-taskbar)
- [Atera — Enable/disable Notification Center in Windows 11](https://www.atera.com/blog/how-to-enable-or-disable-the-notification-center-in-windows-11/)
- [Spiceworks — GPP to turn off Action Center by default](https://community.spiceworks.com/t/gpp-to-turn-off-windows-10-action-center-by-default/633306)
- [TenForums — Notification Center 图标异常（删除 DisableNotificationCenter 恢复）](https://www.tenforums.com/installation-upgrade/152998-i-cannot-activate-notifications-center-icon.html)
- [ADMX 策略参考 — Turn off notification area cleanup（NoAutoTrayNotify）](https://gpedit.tplant.com.au/en-us/policy/StartMenu/NoAutoTrayNotify/)
- [Super User — Windows won't hide my notification area icons](https://superuser.com/questions/1363736/windows-wont-hide-my-notification-area-icons-even-though-i-set-them-to-hide)
- [Puget Systems — Disabling the notification area（NoTrayItemsDisplay）](https://www.pugetsystems.com/support/guides/disabling-notification-area/)
