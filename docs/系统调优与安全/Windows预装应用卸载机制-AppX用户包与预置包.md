---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
verified_on: "2026-11-04"
---

# Windows 预装应用卸载机制：用户包、预置包与「删了又回来」

> **一句话结论**：Windows 的预装应用有两层——**已安装到账户的用户包**和**为新账户准备的预置包**。只删前者，新建账户或部分系统更新后应用会重新出现；只删后者，现有账户里的应用仍在。批量「卸载全部预装应用」的脚本之所以经常「看起来成功、过一阵又回来」，多数是把这两层混为一谈。

## 一、两个不同的对象

微软把 `C:\Program Files\WindowsApps` 下的应用分两类：

| 类别 | 含义 | 查看命令 | 作用范围 |
| :--- | :--- | :--- | :--- |
| **已安装（Installed）** | 已经注册到某个用户账户的包 | `Get-AppxPackage` | 单个用户（`-AllUsers` 列出全部） |
| **预置（Provisioned）** | 系统镜像里预置、**每个新用户首次登录时安装**的包 | `Get-AppxProvisionedPackage -Online` | 机器级，面向未来账户 |

微软文档对预置包的描述很直接：`Get-AppxProvisionedPackage` 获取的是「在镜像中、**将为每个新用户安装**」的包；`Remove-AppxProvisionedPackage` 删除后「创建新用户账户时不再安装该包」，但**不会删除现有用户账户里已安装的包**。

这就是「删了又回来」的第一层原因：很多脚本只跑了 `Get-AppxPackage | Remove-AppxPackage`，删的是当前账户的注册，预置包纹丝不动。换个账户登录、或新建账户，Windows 按预置清单再装一遍。

## 二、「回来」的五种原因

| 现象 | 机制 | 是否可避免 |
| :--- | :--- | :--- |
| 新建账户后又出现 | 预置包仍在，首次登录按清单安装 | 删除预置包 |
| 其他现有账户仍有 | 只删了当前用户 | `-AllUsers` 或逐账户删除 |
| 删除命令报错/被拒 | 包被标记为不可移除（NonRemovable），或应用正在运行 | 前者是系统设计，不建议对抗；后者先关应用 |
| 功能更新后又出现 | 就地升级带来新的系统镜像，可能重新写入预置包 | ⚠️ 无官方「一次删除永久生效」承诺，升级后需复查 |
| 自己或商店重新装了 | 用户操作、应用依赖被重新拉起 | 行为层面，不是机制问题 |

其中「功能更新后回归」属于社区长期观察：微软没有承诺删除预置包会在所有升级路径上永久保持。把它当作「一次性清理 + 升级后复查」，比当作「永久免疫」更符合实际。

## 三、正确的操作顺序

以管理员身份打开 PowerShell（删除他人账户的包需要管理员权限，微软文档对 `Remove-AppxPackage -AllUsers` 明确要求 administrator）：

```powershell
# 1. 先确认包名：用户级与预置级分别看
Get-AppxPackage -AllUsers *BingWeather* |
    Select-Object Name, PackageFullName, NonRemovable
Get-AppxProvisionedPackage -Online |
    Where-Object DisplayName -like '*Weather*' |
    Select-Object DisplayName, PackageName

# 2. 删除已安装的用户包（所有账户）
Get-AppxPackage -AllUsers *BingWeather* |
    Remove-AppxPackage -AllUsers

# 3. 删除预置包（阻止新账户安装）
Get-AppxProvisionedPackage -Online |
    Where-Object DisplayName -like '*Weather*' |
    Remove-AppxProvisionedPackage -Online
```

三个容易踩的点：

1. **`-Package` 要的是 `PackageFullName`，不是显示名**。用 `Name` 或通配符筛选后管道传入最稳；如果目标是 bundle，微软文档提示要配合 `Get-AppxPackage -PackageTypeFilter` 指定 bundle。
2. **两步都要做**。只做第 2 步 = 新账户回归；只做第 3 步 = 当前账户的应用还在。顺序上先删用户包、再删预置包更直观，官方没有强制顺序。
3. **「命令没报错」不等于成功**。删完重新枚举一遍，用剩余计数作为证据；失败时到事件查看器的 `Microsoft-Windows-AppXDeploymentServer/Operational` 日志里找部署错误码。

## 四、哪些包不要碰

批量脚本最常见的破坏不是「删多了几个小游戏」，而是删到了**框架包和系统依赖**：

- **框架/运行时包**：`Microsoft.VCLibs.*`、`Microsoft.UI.Xaml.*`、`WindowsAppRuntime.*` 一类。它们本身没有界面，是其它应用的依赖；删掉后依赖它们的应用会启动失败、更新失败或行为异常。
- **商店与安装基础设施**：Microsoft Store、Desktop App Installer（`winget` 的载体）。删了会连带影响应用安装与更新链路。
- **Shell 与安全组件**：开始菜单/搜索宿主、安全中心 UI（`SecHealthUI`）一类。它们通常被系统标记为不可移除，硬删的代价远大于收益。

具体包名与用途见文末附录「Windows 11 常见预置包速查」，删除前先按 Name 对号，不要凭显示名猜。

先看系统自己怎么标记：

```powershell
# 官方 cmdlet：列出已安装且被配置为不可移除的包
Get-NonRemovableAppsPolicy -Online

# 备用：并非所有版本/语言镜像都注册了上面的 cmdlet（实测 Windows 11 26H2 会报“没有注册类”）
Get-AppxPackage | Where-Object NonRemovable -eq $true |
    Select-Object Name, PackageFullName
```

两条路径的结果可能不完全一致：`Get-NonRemovableAppsPolicy` 读的是策略配置，`NonRemovable` 属性读的是包自身的标记。被任一处标记的包，删除请求通常会被拒绝——这是 Windows 的显式设计，不建议用改权限、改策略的方式绕过。

## 五、工程对照：一个「可验证的批量卸载」长什么样

[Atom-Tool-Box](https://github.com/ProjectAtomOS/Atom-Tool-Box) v0.2.0 的 DEBLOAT 页面提供了一个可对照的实现样本（MIT 许可）。它做对的四件事，正好对应上面每一节：

1. **目录化白名单**：要删的包写在 `src/config/debloat.json` 里，而不是 `Get-AppxPackage | Remove-AppxPackage` 全量通配；框架包、Store、Desktop App Installer、Windows App Runtime 明确排除。
2. **先扫描再动手**：同时枚举 installed 与 provisioned，只允许选择「实际存在」的条目，并按应用显示两类计数。
3. **删后重扫验证**：删除完成后重新枚举，剩余数量作为失败证据；不把「命令返回 0」当成成功。
4. **保留已完成进度**：用原子进度文件记录每个应用的结果，助手进程超时不会把已完成项当作失败重来。

它同样明确写了两条边界：删除**不可撤销**（只能从商店或应用官网重装），以及**跳过系统标记为 protected 的包**而不强行删除。这两条边界比「一键全删」的口号更接近真实能力。

## 六、回滚与收益边界

- **回滚**：已删除的预装应用可以从 Microsoft Store、应用官网或 `winget` 重新安装；系统组件通常需要就地升级或重置才能恢复，具体依包而定。删之前建一个还原点，成本极低。
- **收益**：预装应用大多体积不大、平时也不常驻。清理的收益主要是减少后台活动、开始菜单推荐与首次登录安装项，**不是**可感知的性能提升。把它当「装机整洁」而不是「提速手段」。
- **受管设备**：域/Intune 管理的机器可能由策略重新部署应用，本地删除会与策略打架；这类设备不要用第三方批量卸载脚本。

## 七、与 tweakbyjie 的边界

tweakbyjie 当前**不执行 AppX 删除**：它把「批量卸载预装应用」视为超出固定优化范围的新功能面，脚本里没有对应模块。本文只解释机制与边界，不提供可直接照抄的「全量卸载清单」；需要清理时按第三节的两步法逐项做，并保留还原点。

## 附录：Windows 11 常见预置包速查

删除前先认包。下表按用途分组，包名取**包族名（`Name`）**——`PackageFullName` 还会附带版本、架构与发布者哈希（如 `_8wekyb3d8bbwe`），随更新变化，不适合作为判断依据。

「建议」一列只表达删除后的功能影响，不表达性能收益：

- **保留**：删了会破坏依赖或系统基础功能；
- **谨慎**：删了会缺失某项功能，且不一定能靠商店一键装回；
- **按需**：功能明确，用不到可以删；
- **可删**：独立内容应用，删除不影响系统。

### 框架与基础组件

| 包名（Name） | 实际应用 | 建议 |
| :--- | :--- | :--- |
| `Microsoft.VCLibs.140.00` | UWP 应用的 C++ 运行时 | 保留 |
| `Microsoft.UI.Xaml.2.4` | WinUI 2 框架 | 保留 |
| `Microsoft.WindowsAppRuntime.*` | Windows App SDK 运行时（较新版本出现） | 保留 |
| `Microsoft.DesktopAppInstaller` | 应用安装器，`winget` 的载体 | 保留 |
| `Microsoft.WindowsStore` | Microsoft Store | 保留 |
| `Microsoft.StorePurchaseApp` | Store 购买流程组件 | 保留 |
| `Microsoft.SecHealthUI` | Windows 安全中心界面 | 保留 |
| `MicrosoftWindows.Client.WebExperience` | 小组件（Widgets）平台 | 谨慎 |

### 系统工具与生产力

| 包名（Name） | 实际应用 | 建议 |
| :--- | :--- | :--- |
| `Microsoft.WindowsNotepad` | 记事本 | 按需 |
| `Microsoft.Paint` | 画图 | 按需 |
| `Microsoft.ScreenSketch` | 截图工具（Snipping Tool） | 按需 |
| `Microsoft.WindowsTerminal` | Windows 终端 | 按需 |
| `Microsoft.WindowsCalculator` | 计算器 | 按需 |
| `Microsoft.Windows.Photos` | 照片 | 按需 |
| `Microsoft.WindowsCamera` | 相机 | 按需 |
| `Microsoft.WindowsSoundRecorder` | 录音机 | 按需 |
| `Microsoft.MicrosoftStickyNotes` | 便笺 | 按需 |
| `Microsoft.WindowsAlarms` | 时钟（闹钟/计时器） | 按需 |
| `Microsoft.PowerAutomateDesktop` | Power Automate 桌面版 | 按需 |
| `Microsoft.Todos` | 微软待办 | 按需 |
| `microsoft.windowscommunicationsapps` | 邮件和日历（旧版） | 按需 |
| `Microsoft.People` | 人脉 | 按需 |
| `Microsoft.YourPhone` | 手机连接（Phone Link） | 按需 |
| `Microsoft.GetHelp` | 获取帮助 | 按需 |
| `Microsoft.Getstarted` | 入门/提示（Tips） | 可删 |
| `Microsoft.MicrosoftOfficeHub` | Office 集线器 | 可删 |
| `Microsoft.WindowsFeedbackHub` | 反馈中心 | 可删 |

### 内容、娱乐与 Xbox

| 包名（Name） | 实际应用 | 建议 |
| :--- | :--- | :--- |
| `Microsoft.BingNews` | 新闻 | 可删 |
| `Microsoft.BingWeather` | 天气 | 可删 |
| `Microsoft.WindowsMaps` | 地图 | 可删 |
| `Microsoft.MicrosoftSolitaireCollection` | 纸牌合集 | 可删 |
| `Microsoft.549981C3F5F10` | Cortana（小娜，微软已停止支持） | 可删 |
| `Microsoft.ZuneMusic` | 媒体播放器（Media Player） | 按需 |
| `Microsoft.ZuneVideo` | 电影和电视 | 按需 |
| `Microsoft.GamingApp` | Xbox 应用 | 按需 |
| `Microsoft.XboxIdentityProvider` | Xbox 登录组件 | 谨慎 |
| `Microsoft.Xbox.TCUI` | Xbox UI 组件 | 谨慎 |
| `Microsoft.XboxGameOverlay` | Xbox 游戏覆盖层 | 谨慎 |
| `Microsoft.XboxGamingOverlay` | Game Bar / 录屏覆盖层 | 谨慎 |
| `Microsoft.XboxSpeechToTextOverlay` | Xbox 语音转文字覆盖层 | 谨慎 |

### 媒体扩展

这几项是解码扩展，不是「预装娱乐应用」。删掉后对应格式可能无法预览或播放，且不一定能从商店装回。

| 包名（Name） | 实际应用 | 建议 |
| :--- | :--- | :--- |
| `Microsoft.HEIFImageExtension` | HEIF/HEIC 图像解码 | 保留 |
| `Microsoft.WebpImageExtension` | WebP 图像解码 | 保留 |
| `Microsoft.VP9VideoExtensions` | VP9 视频解码 | 保留 |
| `Microsoft.WebMediaExtensions` | 媒体格式扩展 | 保留 |

### 使用说明

1. **包族名对号，不看版本**：用 `Get-AppxPackage -AllUsers *<Name>*` 匹配；表里的名称是前缀，实际包名可能带版本后缀。
2. **清单不是全集**：不同 Windows 版本、地区与 SKU 的预置包不同（较新版本还会出现 Clipchamp、Family、QuickAssist、CrossDevice 等），以本机 `Get-AppxProvisionedPackage -Online` 的结果为准。
3. **「可删」不等于「该删」**：删除的收益是减少后台活动与推荐内容，不是性能提升；删之前建还原点。
4. **本表底稿是 2023-06 的一份第三方 Win11 清单**，其中若干描述笼统或已过时（例如把 `549981C3F5F10` 留空、把 `YourPhone` 说成「Windows 10 设备连接」）。本表按当前应用身份做了校正，仍建议结合本机枚举核对。

## 事实核查记录

| 声明 | 核查结果 |
| :--- | :--- |
| 预置包只影响新用户，不删除现有用户已安装的包 | ✅ 微软文档原文：`Remove-AppxProvisionedPackage` 删除后新账户不再安装，现有账户的包不会被移除 |
| `Remove-AppxPackage -AllUsers` 需要管理员权限 | ✅ 微软文档明确要求 administrator permissions |
| 存在「不可移除应用」策略，删除会被拒绝 | ✅ `Get-/Set-NonRemovableAppsPolicy` 为官方 cmdlet |
| 删除框架包会让依赖应用故障 | ✅ 机制成立：框架包是依赖项；具体表现依应用与版本 |
| 功能更新后应用一定回归 | ⚠️ 社区常见观察，微软无永久删除承诺；不同升级路径结果不一 |
| 清理预装应用能显著提升性能 | ❌ 无通用证据；收益主要是后台活动与推荐内容减少，需实测 |
| 附录的预装包清单可以跨版本照抄 | ❌ 包名与数量随版本、地区、SKU 变化；清单只作识别参考，删除前以本机枚举为准 |

## 参考

- [Overview of apps on Windows client devices（Installed 与 Provisioned 两类应用）](https://learn.microsoft.com/en-us/windows/application-management/overview-windows-apps)
- [Remove-AppxPackage（`-AllUsers` 作用域与管理员要求）](https://learn.microsoft.com/en-us/powershell/module/appx/remove-appxpackage?view=windowsserver2025-ps)
- [Remove-AppxProvisionedPackage（预置包语义）](https://learn.microsoft.com/en-us/powershell/module/dism/remove-appxprovisionedpackage?view=windowsserver2025-ps)
- [Get-AppxProvisionedPackage（为新用户安装的包）](https://learn.microsoft.com/en-us/powershell/module/dism/get-appxprovisionedpackage?view=windowsserver2025-ps)
- [Get-NonRemovableAppsPolicy（不可移除应用清单）](https://learn.microsoft.com/en-us/powershell/module/appx/get-nonremovableappspolicy?view=windowsserver2025-ps)
- [Windows 11 预安装的 Microsoft Appx 应用程序功能介绍（pc528，2023-06-27）](https://www.pc528.net/202306271417.html)——附录清单的底稿；该文对部分包的描述已过时或笼统，附录按当前应用身份做了校正。
- [Atom-Tool-Box v0.2.0（DEBLOAT 实现样本）](https://github.com/ProjectAtomOS/Atom-Tool-Box/releases/tag/v0.2.0)
