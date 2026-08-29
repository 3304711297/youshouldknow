---
status: reference
risk: medium
applies_to:
  - Windows 10/11 Win + R、命令提示符与 PowerShell
  - 系统管理工具和诊断命令速查
verified_on: 2026-08-29
# 2026-08-29 通读复核：未发现过时项，verified_on 更新为本次核验日期
---

# Windows 常用命令列表（Win + R 运行速查）

> **分类**：系统知识 · 命令速查
>
> **适用场景**：通过 `Win + R` 运行框、命令提示符或 PowerShell 快速打开系统管理工具。绝大多数为系统自带，无需安装。
>
> 本文已对照微软官方文档与社区资料核实；原资料中数条归档有误的命令已修正（见文末核查记录）。

---

## 一、系统管理与配置

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `cmd` | 打开命令提示符 | Win11 可用 `wt` 打开 Windows 终端 |
| `powershell` | 打开 Windows PowerShell | — |
| `gpedit.msc` | 本地组策略编辑器 | **专业版以上**可用 |
| `regedit` | 注册表编辑器 | — |
| `services.msc` | 服务管理器 | — |
| `devmgmt.msc` | 设备管理器 | — |
| `diskmgmt.msc` | 磁盘管理 | — |
| `compmgmt.msc` | 计算机管理（集成工具集） | — |
| `taskmgr` | 任务管理器 | — |
| `msconfig` | 系统配置实用程序（启动项管理） | — |
| `cleanmgr` | 磁盘清理 | — |
| `dxdiag` | DirectX 诊断工具 | — |
| `eventvwr` | 事件查看器 | 等效 `eventvwr.msc` |
| `fsmgmt.msc` | 共享文件夹管理器 | — |
| `gpupdate /force` | 强制刷新组策略 | 需参数，命令行执行 |
| `lusrmgr.msc` | 本地用户和组 | **专业版以上**；家庭版报「此管理单元不能用于该版本」，替代：`netplwiz` |
| `secpol.msc` | 本地安全策略 | **专业版以上**可用 |
| `sfc /scannow` | 扫描并修复系统文件 | 需**管理员**权限 |
| `sysdm.cpl` | 系统属性 | — |
| `systempropertiesadvanced` | 系统属性「高级」标签 | 同族还有 `systempropertiescomputername` 等 |
| `gpresult /r` | 查看组策略应用结果 | 需参数 |
| `resmon` | 资源监视器 | — |
| `perfmon.msc` | 性能监视器 | — |
| `msinfo32` | 系统信息 | 替代旧版 `winmsd` |

## 二、网络相关

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `ipconfig` | 显示 / 配置网络设置 | `/all` 看详情，`/flushdns` 清 DNS 缓存 |
| `ncpa.cpl` | 网络连接面板 | — |
| `netstat -ano` | 查看网络连接与端口状态 | 需参数；配合 PID 定位进程 |
| `ping` | 测试网络连通性 | — |
| `tracert` | 跟踪网络路径 | — |
| `netsh` | 网络配置命令行工具 | 功能极多（WLAN / 防火墙 / 网络 reset 等） |
| `firewall.cpl` | Windows 防火墙 | — |
| `inetcpl.cpl` | Internet 属性 | — |

## 三、用户与会话

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `logoff` | 注销当前用户 | — |
| `tscon` | 连接 / 切换会话 | 常用于 RDP 会话切回控制台 |
| `tskill` | 终止会话进程 | — |
| `quser` | 查看已登录用户列表 | — |
| `qwinsta` | 查看终端会话信息 | — |
| `runas /user:账户名 cmd` | 以其他身份运行程序 | `账户名` 需替换为**实际管理员账户**（如 `Administrator`） |

## 四、远程控制

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `mstsc` | 远程桌面连接 | — |

## 五、硬件与设备

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `hdwwiz.cpl` | 添加硬件向导 | — |
| `printmanagement.msc` | 打印管理 | **专业版以上**可用 |
| `joy.cpl` | 游戏控制器设置 | — |
| `main.cpl` | 鼠标属性 | — |
| `mmsys.cpl` | 声音设置 | — |
| `sndvol` | 音量控制面板 | — |
| `powercfg.cpl` | 电源选项 | 命令行 `powercfg` 功能更多 |

## 六、实用工具

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `notepad` | 记事本 | — |
| `calc` | 计算器 | — |
| `mspaint` | 画图 | — |
| `charmap` | 字符映射表 | — |
| `osk` | 屏幕键盘 | — |
| `magnify` | 放大镜 | — |
| `narrator` | 屏幕朗读（讲述人） | — |
| `snippingtool` | 截图工具 | Win10 起逐步并入新截图工具；快捷键 `Win + Shift + S` |
| `ms-settings:` | 打开 Windows 设置 | 可带子页直达，如 `ms-settings:display`（显示）、`ms-settings:windowsupdate`（更新） |
| `explorer` | 文件资源管理器 | — |
| `control` | 控制面板 | — |

## 七、文件与存储

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `diskpart` | 磁盘分区命令行工具 | 需**管理员**权限，操作有数据风险 |
| `dfrgui` | 优化驱动器（碎片整理） | SSD 上执行 TRIM |
| `shrpubw` | 创建共享文件夹向导 | — |

## 八、系统维护

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `rstrui` | 系统还原 | — |
| `verifier` | 驱动程序验证管理器 | ⚠️ 高级排障工具，开启不当可能蓝屏循环，普通用户勿动 |
| `msdt` | Microsoft 支持诊断工具 | ⚠️ **官方已宣布退役**：Win11 23H2+ 疑难解答转向「获取帮助」（Get Help） |

## 九、脚本与开发

| 命令 | 作用 | 备注 |
| --- | --- | --- |
| `wscript` | 运行 VBScript（窗口模式） | — |
| `cscript` | 命令行运行脚本 | — |
| `odbcad32` | ODBC 数据源管理器 | — |

## 十、过时 / 已移除（了解即可）

| 命令 | 状态 |
| --- | --- |
| `tsadmin` | 远程桌面服务管理器，**Win8 / Server 2012 起已移除**（服务器端并入 Server Manager） |
| `drwtsn32` | Dr. Watson 调试器，仅旧版 Windows 有效 |
| `sndrec32` | 旧版录音机，Win7 后失效 |
| `wuaucpl.cpl` | 旧版 Windows 更新设置，Win10/11 已过时（现为 `ms-settings:windowsupdate`） |
| `conf` | NetMeeting，已淘汰 |
| `dcpromo` | AD 域控制器安装向导，**Server 2012 起弃用**（改用服务器管理器 / PowerShell） |
| `clipbrd` | 剪贴板查看器，**Vista 起已移除**（XP 专属；现为 `Win + V`） |
| `winchat` | Windows 聊天，仅 NT/XP 时代有效 |
| `tourstart` | Windows 漫游，XP 专属，**Vista 起已移除** |
| `wmic` | WMI 命令行工具，**已弃用**（Win11 24H2 起逐步移除，改用 PowerShell CIM：`Get-CimInstance`） |

## 十一、第三方工具（需单独安装）

| 命令 | 作用 |
| --- | --- |
| `psexec` | Sysinternals 远程执行工具 |
| `psinfo` | Sysinternals 系统信息工具 |

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| 各 .msc / .cpl / exe 命令与打开目标对应关系 | ✅ 属实：与系统实际 Run 命令一致 |
| `gpedit.msc`、`secpol.msc`、`printmanagement.msc` 专业版以上可用 | ✅ 属实 |
| `lusrmgr.msc` 家庭版不可用（报「此管理单元不能用于该版本」） | ✅ 属实：家庭版替代方案 `netplwiz` / `net user` 已补充 |
| `tsadmin` 可打开远程桌面管理工具 | ❌ 修正：Win8 / Server 2012 起已移除，原稿归入「远程控制」不当，已移至「过时」节 |
| `clipbrd` 「Win10/11 中移除」、`tourstart`「Win10 后移除」 | ⚠️ 修正：两者实际均为 **Vista 起移除**（XP 专属功能） |
| `dcpromo`「Win10 后改用 Server Manager」 | ⚠️ 修正：服务器组件，**Server 2012 起弃用**，与 Win10 客户端无关 |
| `msdt` 逐步退役，新版转向「获取帮助」 | ✅ 属实：微软官方已发布退役公告（Win11 23H2+），已补充 |
| `wmic` Win11 22H2 后弃用 | ✅ 属实：官方弃用公告，24H2 起逐步移除；替代命令 `Get-CimInstance` 已补充 |
| `sfc /scannow`、`diskpart` 需管理员权限 | ✅ 属实 |
| `runas /user:admin` 中的 admin | ⚠️ 修正：需替换为实际存在的管理员账户名（如 `Administrator`） |

**参考来源：**

- [Microsoft Learn — Windows 命令行参考（命令 A-Z）](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)
- [Microsoft 支持 — MSDT 与疑难解答程序退役公告](https://support.microsoft.com/en-us/windows/experience/deprecation-of-microsoft-support-diagnostic-tool-msdt-and-msdt-troubleshooters)
- [Microsoft Learn — WMIC 弃用与 PowerShell CIM 替代](https://learn.microsoft.com/en-us/windows/win32/wmisdk/wmic)
- [TenForums — lusrmgr.msc 家庭版报错与替代](https://www.tenforums.com/user-accounts-family-safety/59861-lusrmgr-msc-snapin-may-not-used-edition-windows.html)
- [Lizardsystems — Terminal Services Manager（tsadmin 移除史）](https://lizardsystems.com/terminal-services-manager/articles/terminal-services-manager-tsadmin-windows-server/)
