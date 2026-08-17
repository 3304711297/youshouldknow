# Windows 审核模式（Audit Mode）与 OOBE

## 一、什么是审核模式

Windows 的 **Audit Mode（审核模式）** 是微软提供给系统部署、OEM 和系统定制使用的模式。

它允许在 Windows 首次进入正常 OOBE（Out-of-Box Experience，开箱体验）之前进入桌面，对系统进行配置，例如：

- 安装驱动；
- 安装应用程序；
- 运行脚本；
- 修改系统配置；
- 制作和维护 Windows 参考镜像。

微软官方明确说明，Audit Mode 可以绕过正常 OOBE，让用户更快进入桌面进行系统定制。citeturn0search0turn0search4

## 二、最推荐的进入方法：Ctrl + Shift + F3

在 Windows OOBE 界面按：

```text
Ctrl + Shift + F3
```

Windows 会自动重新启动，并进入 Audit Mode。

进入后通常会看到 **System Preparation Tool（Sysprep）** 窗口，这就是审核模式的明显特征。微软官方文档明确提供了这种进入方法。citeturn0search1turn0search6

### 注意

`Ctrl + Shift + F3` 并不是把 OOBE 的所有处理步骤都永久删除；微软说明，某些 OOBE 脚本和配置仍可能按照实际安装情况被处理。citeturn0search1

## 三、Audit Mode 中的 Administrator

进入 Audit Mode 时，Windows 会自动使用内置的 **Administrator** 账户登录。

因此，通常**不需要手动通过 `lusrmgr.msc` 启用 Administrator**。

微软官方文档明确指出，在 Audit Mode 中，内置 Administrator 会自动启用，并用于自动登录；不需要额外通过应答文件手动启用该账户。citeturn0search13

因此，不建议把下面这种操作当作进入审核模式的必要步骤：

```text
Win + R
↓
lusrmgr.msc
↓
用户
↓
Administrator
↓
取消“账户已禁用”
```

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

它本身并不是一个“修改注册表后永久关闭 OOBE 联网要求”的功能。

如果目标只是**在首次安装阶段避免进入普通 OOBE 流程，并进入桌面完成系统定制**，优先使用微软官方的 Audit Mode 方法，而不是修改 Windows Setup 内部状态。

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
3. 微软官方 Audit Mode 文档并没有把“修改这些 Setup 状态值”作为进入 Audit Mode 或跳过联网的标准方法；
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

安装完成后，Windows 可以按照应答文件配置自动进入审核模式。citeturn0search1turn0search8

这种方法比手工修改 Setup 注册表状态更加符合 Windows 官方部署机制。

## 七、完成系统定制后如何退出 Audit Mode

如果已经完成系统定制，需要让系统最终进入正常的 OOBE，可以使用 Sysprep。

例如：

```cmd
C:\Windows\System32\Sysprep\sysprep.exe /oobe /shutdown
```

微软官方说明，在完成 Audit Mode 中的系统配置后，需要将系统重新配置为 OOBE，才能作为最终用户首次启动时的正常开箱体验。citeturn0search1turn0search4

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

## 十、官方资料

- [Microsoft Learn：Audit mode overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/audit-mode-overview?view=windows-11)
- [Microsoft Learn：Boot Windows to Audit Mode or OOBE](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/boot-windows-to-audit-mode-or-oobe?view=windows-11)
- [Microsoft Learn：Sysprep Process Overview](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/sysprep-process-overview?view=windows-11)
- [Microsoft Learn：auditUser](https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/audituser?view=windows-11)
