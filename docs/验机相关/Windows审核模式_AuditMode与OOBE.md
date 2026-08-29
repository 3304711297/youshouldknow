# Windows 审核模式（Audit Mode）与 OOBE

> **分类**：验机相关 · Windows 安装与初始化
>
> **适用场景**：Windows 安装、验机、系统部署与首次启动阶段的系统配置。

## 一、什么是审核模式

Windows 的 **Audit Mode（审核模式）** 是微软提供给系统部署、OEM 和系统定制使用的模式。

它允许在 Windows 首次进入正常 OOBE（Out-of-Box Experience，开箱体验）之前进入桌面，对系统进行配置，例如：

- 安装驱动；
- 安装应用程序；
- 运行脚本；
- 修改系统配置；
- 制作和维护 Windows 参考镜像。

微软官方明确说明，Audit Mode 可以在正常 OOBE 完成前进入桌面进行系统定制。

## 二、最推荐的进入方法：Ctrl + Shift + F3

在 Windows OOBE 界面按：

```text
Ctrl + Shift + F3
```

Windows 会自动重新启动，并进入 Audit Mode。

进入后通常会看到 **System Preparation Tool（Sysprep）** 窗口，这是审核模式的明显特征。

### 注意

`Ctrl + Shift + F3` 并不是把 OOBE 的所有处理步骤永久删除；它的作用是让系统在最终用户正常 OOBE 之前进入审核环境。

## 三、Audit Mode 中的 Administrator

进入 Audit Mode 时，Windows 会自动使用内置的 **Administrator** 账户登录。

因此，通常**不需要手动通过 `lusrmgr.msc` 启用 Administrator**。

如果已经正常进入 Audit Mode，Windows 会自行处理这个账户的状态。

## 四、审核模式与“跳过联网”要区分

Audit Mode 的核心作用是：

```text
OOBE
 ↓
进入 Audit Mode
 ↓
Administrator 自动登录
 ↓
进入桌面进行系统配置
```

它本身不是一个“修改注册表后永久关闭 OOBE 联网要求”的功能。

如果目标是在首次安装阶段进入桌面完成系统定制，优先使用微软官方的 Audit Mode 方法，而不是修改 Windows Setup 内部状态。

## 五、关于修改 HKLM\SYSTEM\Setup 的非官方方法

网上有一种方法会在审核模式或 OOBE 阶段打开注册表，然后修改：

```text
HKLM\SYSTEM\Setup
```

下面的一些 Setup 状态值，例如：

```text
SystemSetupInProgress
OOBEInProgress
CmdLine
SetupPhase
SetupSupported
SetupType
```

常见说法是把部分值改为 `0`，清空 `CmdLine`，然后注销或重新登录，以达到跳过某些 OOBE/联网流程的目的。

### 可靠性评价

**不建议把这种注册表修改作为标准教程或通用方案。**

原因是：

1. 这些值属于 Windows Setup/OOBE 的内部状态；
2. 不同 Windows 版本、安装方式和部署环境可能存在差异；
3. 微软官方 Audit Mode 文档没有把修改这些 Setup 状态值作为进入 Audit Mode 或跳过联网的标准方法；
4. 错误修改 Setup 状态可能导致 OOBE、Sysprep 或后续部署状态异常。

因此，如果资料中出现这套注册表技巧，应明确标记为：

> **非官方技巧：可能在特定 Windows 版本/场景下有效，但不保证通用，也不建议作为首选方法。**

## 六、如果需要自动进入 Audit Mode

对于 Windows 镜像部署，还可以通过 **Unattend（无人值守应答文件）**配置系统自动进入 Audit Mode。

微软提供的方式是使用：

```text
Microsoft-Windows-Deployment
└─ Reseal
   └─ Mode = audit
```

这种方式比手工修改 Setup 注册表状态更加符合 Windows 官方部署机制。

## 七、完成系统定制后如何退出 Audit Mode

如果已经完成系统定制，需要让系统最终进入正常的 OOBE，可以使用 Sysprep：

```cmd
C:\Windows\System32\Sysprep\sysprep.exe /oobe /shutdown
```

完成后再次启动，系统会进入正常 OOBE。

## 八、实用流程

### 普通手动进入审核模式

```text
Windows 安装
    ↓
OOBE
    ↓
Ctrl + Shift + F3
    ↓
系统自动重启
    ↓
Audit Mode
    ↓
Administrator 自动登录
    ↓
安装驱动 / 软件 / 修改系统 / 运行脚本
```

### 完成后恢复正常 OOBE

```text
Audit Mode
    ↓
完成系统定制
    ↓
Sysprep /oobe /shutdown
    ↓
再次启动
    ↓
正常 OOBE
```

## 九、关于“审核模式跳过联网”的结论

如果看到类似：

> “进入审核模式后，启用 Administrator，再修改 `HKLM\SYSTEM\Setup` 中多个值即可永久跳过联网。”

建议不要直接照搬。

更可靠的知识应该分成两层：

**官方方法：**

- 使用 `Ctrl + Shift + F3` 进入 Audit Mode；
- 使用 Unattend 配置自动进入 Audit Mode；
- 使用 Sysprep 在完成定制后返回 OOBE。

**非官方方法：**

- 修改 `HKLM\SYSTEM\Setup` 下的 OOBE/Setup 状态值；
- 可能用于特定版本或特殊场景；
- 不保证跨版本有效；
- 不建议作为首选方案。

### 核心结论

**Audit Mode 是微软正式支持的 Windows 部署模式；“修改 Setup 注册表状态来跳过联网/OOBE”则属于非官方技巧。两者不要混为一谈。**

## 十、与 Windows 激活的关系

还需要特别区分 **OOBE 联网要求** 与 **Windows 产品激活**：

- Audit Mode / OOBE：属于安装和首次初始化流程；
- Windows 激活：属于 Windows 许可证和授权状态验证。

“跳过 OOBE 联网”并不等于“激活 Windows”。完成系统安装后，仍应单独检查 Windows 的激活状态和许可证信息。

## 十一、官方资料

- [Microsoft Learn：Audit mode overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/audit-mode-overview?view=windows-11)
- [Microsoft Learn：Boot Windows to Audit Mode or OOBE](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/boot-windows-to-audit-mode-or-oobe?view=windows-11)
- [Microsoft Learn：Sysprep Process Overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-process-overview?view=windows-11)
- [Microsoft Learn：auditUser](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/audituser?view=windows-11)

## 事实核查记录

核验基准：Microsoft Learn《Audit mode Overview》（2026-08-29 重核：官方 audit-mode-overview 与 boot-windows-to-audit-mode-or-oobe 页面在线核验通过，正文各项声明与官方文档一致；官方仍注明"不应将审核模式用于测试验证场景"）。

| 声明 | 核查结果 |
| --- | --- |
| Audit Mode 允许在 OOBE 前进入桌面安装驱动/应用/运行脚本 | ✅ 属实：官方页面 Benefits 一节原文一致 |
| 进入 Audit Mode 后以内置 Administrator 账户自动登录，无需 lusrmgr.msc 手动启用 | ✅ 属实：官方"Audit mode account"一节原文一致 |
| 审核模式可绕过 OOBE（Bypass OOBE） | ✅ 属实：官方 Benefits 一节原文 |
| Ctrl+Shift+F3 进入审核模式、Sysprep /oobe 返回 OOBE、Unattend Reseal Mode=audit | ✅ 属实：官方 Boot to Audit mode / Sysprep / Unattend 文档记载（组合键详见官方 Boot to Audit mode or OOBE 页） |
| 修改 HKLM\SYSTEM\Setup 状态值跳过联网属非官方技巧 | ✅ 判断合理：官方文档未记载此方法，正文已按非官方标注 |
| 补充边界 | ⚠️ 官方注明审核模式账户在 auditUser 阶段后即被禁用、不应用于测试验证场景——本文未展开，读者可查阅原页 Notes |
