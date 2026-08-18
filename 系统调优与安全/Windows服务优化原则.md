# Windows 服务优化原则

## 基本原则

Windows 服务优化不是简单地关闭所有后台服务。

正确方式：

1. 判断服务用途
2. 判断使用场景
3. 评估性能收益与功能影响
4. 保留恢复能力

## 服务状态分类

### 保持默认

系统核心、安全、硬件相关服务。

### 可调整

根据设备用途决定，例如游戏主机、工作站。

### 谨慎调整

涉及更新、网络、账户、驱动管理的服务。

## 与 tweakbyjie 的实际对应关系

`tweakbyjie.ps1` 有两个不同的服务入口，备份能力不能混为一谈。

### SERVICE-001：Part 6 服务优化

主菜单 `6 → 1` 会把 37 个目标服务分成：

- Group A：21 个服务设为 `Disabled`；
- Group B：9 个按需服务设为 `Disabled`；
- Manual 组：`XboxGipSvc`、`XblAuthManager`、`XboxNetApiSvc`、`XblGameSave`、`bthserv`、`embeddedmode`、`BITS` 共 7 个设为 `Manual`。

脚本在修改前创建或校验 `service-backup.json`，保存每个目标服务的 `Name`、`StartMode` 和 `State`；修改后用 `Win32_Service.StartMode` 逐项验证。主菜单 `6 → 2` 按快照恢复启动类型，原本不存在的服务跳过。恢复只保证启动类型，不强制恢复服务当前运行状态，通常需要重启。

#### Part 6 逐项目标清单

以下清单对应源码当前的 37 条服务记录；服务不存在时脚本会跳过，但仍会在首次快照中记录其不存在状态。Group A 与 Group B 在一次执行中都会处理，不是二选一。

| 组别 | 服务名 | 目标启动类型 | 主要影响边界 |
| --- | --- | --- | --- |
| A | `DialogBlockingService` | Disabled | 系统对话框阻塞/交互相关功能可能受影响 |
| A | `TrkWks` | Disabled | 分布式链接跟踪、快捷方式/文件关联维护可能受影响 |
| A | `AppVClient` | Disabled | App-V 虚拟化应用无法按需运行 |
| A | `MsKeyboardFilter` | Disabled | 键盘筛选策略相关设备功能可能受影响 |
| A | `NetTcpPortSharing` | Disabled | 依赖 Net.TCP 端口共享的应用无法使用 |
| A | `CscService` | Disabled | 脱机文件/缓存同步功能可能受影响 |
| A | `ssh-agent` | Disabled | SSH 密钥代理功能不可用 |
| A | `RemoteRegistry` | Disabled | 远程注册表管理不可用 |
| A | `RemoteAccess` | Disabled | 远程访问/VPN 相关功能可能受影响 |
| A | `SensorDataService` | Disabled | 传感器数据服务不可用 |
| A | `SensrSvc` | Disabled | 传感器监视相关功能可能受影响 |
| A | `shpamsvc` | Disabled | 共享 PC 账户管理功能可能受影响 |
| A | `UevAgentService` | Disabled | UE-V 用户设置同步不可用 |
| A | `WalletService` | Disabled | 钱包/支付相关系统功能可能受影响 |
| A | `wisvc` | Disabled | Windows Insider 相关功能可能受影响 |
| A | `WSAIFabricSvc` | Disabled | Windows Subsystem for Android 相关组件可能受影响 |
| A | `dmwappushservice` | Disabled | 设备管理/遥测推送相关功能可能受影响 |
| A | `DusmSvc` | Disabled | 数据使用量监控不可用 |
| A | `tzautoupdate` | Disabled | 自动时区更新不可用 |
| A | `edgeupdate` | Disabled | Microsoft Edge 自动更新可能受影响 |
| A | `edgeupdatem` | Disabled | Microsoft Edge 更新维护任务可能受影响 |
| B | `DPS` | Disabled | 诊断策略服务不可用，故障排查能力下降 |
| B | `WdiServiceHost` | Disabled | 诊断服务主机不可用 |
| B | `WdiSystemHost` | Disabled | 系统诊断主机不可用 |
| B | `diagsvc` | Disabled | 诊断执行服务不可用 |
| B | `PhoneSvc` | Disabled | 电话/移动通信集成功能可能受影响 |
| B | `PcaSvc` | Disabled | 程序兼容性助手不可用 |
| B | `Spooler` | Disabled | 打印、打印队列和部分依赖打印后台处理的应用受影响 |
| B | `WSearch` | Disabled | Windows Search 索引和快速搜索受影响 |
| B | `SysMain` | Disabled | SysMain/预加载行为改变，启动和磁盘后台活动可能变化 |
| Manual | `XboxGipSvc` | Manual | Xbox 手柄/配件按需使用 |
| Manual | `XblAuthManager` | Manual | Xbox Live 身份验证按需启动 |
| Manual | `XboxNetApiSvc` | Manual | Xbox Live 网络功能按需启动 |
| Manual | `XblGameSave` | Manual | Xbox 云存档按需启动 |
| Manual | `bthserv` | Manual | 蓝牙耳机、手柄、键鼠按需启动 |
| Manual | `embeddedmode` | Manual | 嵌入模式和 Store 应用后台任务按需启动 |
| Manual | `BITS` | Manual | Windows 更新和后台传输按需启动 |

这些用途是功能边界提示，不代表在每台 Windows 版本上都完全相同；执行前应查看服务依赖和当前 `StartMode`，尤其不要仅凭“性能优化”字样禁用打印、搜索、诊断、更新、蓝牙或 Xbox 相关服务。

Group B 和 Manual 组尤其需要按场景评估：`Spooler` 影响打印，`WSearch` 影响索引搜索，`SysMain` 影响预读取，BITS 影响 Windows 更新和后台下载，蓝牙/Xbox 服务影响对应硬件和账户功能。A/B 分组不是自动安全保证，选择 `6 → 1` 时两组都会执行。

### SERVICE-002：Part 5 安全中心/Defender 停用

主菜单 `5` 会停止并禁用 `WinDefend`；选择额外分支时还会处理一组 Defender/Security Center 相关服务，并可能删除 Defender 计划任务、启动项和 `SecHealthUI`。该入口没有使用 `service-backup.json`，也没有统一的启动类型回读或自动原始状态恢复；相关策略注册表写入同样没有统一备份闭环。

这不是普通服务优化。它可能降低实时防护、篡改防护、SmartScreen、安全中心提示、更新和企业安全策略的有效性。除非明确理解安全影响并准备手工恢复/系统修复方案，否则不应执行。

## 与 tweakbyjie 的关系

服务优化模块应遵循：

- 修改前备份
- 修改后可恢复
- 明确说明影响
- 不追求无服务状态
- 区分 Part 6 的可回滚启动类型调整与 Part 5 的高风险安全组件停用

具体服务集合、源码入口、验证和恢复限制见 `youshouldknow/项目导航/tweakbyjie-optimization-mapping.md`。
