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

## 事实核查记录

| 声明 | 核查结果 |
| :--- | :--- |
| 预置包只影响新用户，不删除现有用户已安装的包 | ✅ 微软文档原文：`Remove-AppxProvisionedPackage` 删除后新账户不再安装，现有账户的包不会被移除 |
| `Remove-AppxPackage -AllUsers` 需要管理员权限 | ✅ 微软文档明确要求 administrator permissions |
| 存在「不可移除应用」策略，删除会被拒绝 | ✅ `Get-/Set-NonRemovableAppsPolicy` 为官方 cmdlet |
| 删除框架包会让依赖应用故障 | ✅ 机制成立：框架包是依赖项；具体表现依应用与版本 |
| 功能更新后应用一定回归 | ⚠️ 社区常见观察，微软无永久删除承诺；不同升级路径结果不一 |
| 清理预装应用能显著提升性能 | ❌ 无通用证据；收益主要是后台活动与推荐内容减少，需实测 |

## 参考

- [Overview of apps on Windows client devices（Installed 与 Provisioned 两类应用）](https://learn.microsoft.com/en-us/windows/application-management/overview-windows-apps)
- [Remove-AppxPackage（`-AllUsers` 作用域与管理员要求）](https://learn.microsoft.com/en-us/powershell/module/appx/remove-appxpackage?view=windowsserver2025-ps)
- [Remove-AppxProvisionedPackage（预置包语义）](https://learn.microsoft.com/en-us/powershell/module/dism/remove-appxprovisionedpackage?view=windowsserver2025-ps)
- [Get-AppxProvisionedPackage（为新用户安装的包）](https://learn.microsoft.com/en-us/powershell/module/dism/get-appxprovisionedpackage?view=windowsserver2025-ps)
- [Get-NonRemovableAppsPolicy（不可移除应用清单）](https://learn.microsoft.com/en-us/powershell/module/appx/get-nonremovableappspolicy?view=windowsserver2025-ps)
- [Atom-Tool-Box v0.2.0（DEBLOAT 实现样本）](https://github.com/ProjectAtomOS/Atom-Tool-Box/releases/tag/v0.2.0)
