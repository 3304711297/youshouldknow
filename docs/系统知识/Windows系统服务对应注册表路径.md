---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: [6]
---

# Windows 系统服务对应注册表路径与键值说明

> **分类**：系统知识 · 注册表与服务
>
> **适用场景**：通过注册表定位、启停、禁用 Windows 系统服务；理解 `Services` 键下各数值的含义（Start / Type 等）。
>
> 本文已对照微软官方服务控制管理器（SCM）文档核实；原资料中一处键值描述已按标准修正、一处路径概念已澄清（见文末核查记录）。

---

## 一、机制说明：两类路径别混淆

**所有 Windows 服务都注册在同一个位置**：

```text
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\<服务名>
```

服务的启动类型、可执行文件、显示名等全部存放在各自服务名子键下。

另一类是**策略配置键**（如 `HKLM\SOFTWARE\Policies\...`）——它不是服务的注册位置，而是通过组策略 / 策略注册表控制某个功能的**行为开关**。例如下文 Windows Defender 的两种写法就分属两类。

## 二、常见服务注册键对照表

### 安全与更新类

| 服务名 | 服务 | 说明 |
| --- | --- | --- |
| `mpssvc` | Windows Defender 防火墙 | 服务本体注册键 |
| `WinDefend` | Microsoft Defender 防病毒 | ⚠️ 注意：Defender **服务本体**是这个键（第四类保护较难直接改） |
| `wuauserv` | Windows Update | 更新主服务 |
| `UsoSvc` | 更新会话编排器（Update Session Orchestrator） | 更新流程协调 |
| `WaaSMedicSvc` | Windows 更新 Medic | 自动修复更新组件，禁用 wuauserv 后它可能拉起，需一并处理 |
| `DoSvc` | 传递优化 | 更新的 P2P 分发，常改手动 |
| `BITS` | 后台智能传输服务 | wuauserv 依赖它下载更新 |

### 性能与体验类

| 服务名 | 服务 | 说明 |
| --- | --- | --- |
| `SysMain`（原 Superfetch） | 预取与内存管理 | 常见优化对象（改手动 / 禁用） |
| `WSearch` | Windows 搜索索引 | 建索引耗资源，不需要搜索可禁 |
| `Spooler` | 打印后台处理 | 不接打印机可禁用 |
| `DiagTrack` | 诊断跟踪（遥测） | 常禁 |
| `TrkWks` | 分布式链接跟踪客户端 | 常禁 |
| `RemoteRegistry` | 远程注册表 | 安全取向通常禁用 |
| `lfsvc` / `MapsBroker` | 地理位置 / 下载地图 | 常禁 |
| `Themes` | 主题 | 禁用会失去视觉主题效果 |
| `WlanSvc` | WLAN 自动配置 | **用 Wi-Fi 的机器勿动** |

### ⚠️ 系统关键服务（严禁修改）

`RpcSs`、`DcomLaunch`、`PlugPlay`、`Power`、`EventLog`、`Audiosrv` / `AudioEndpointBuilder`（音频）、`Dhcp` / `Dnscache`（网络）等——禁用会导致系统功能异常甚至无法启动。

## 三、键值说明（图片内容整理）

### Start 值（DWORD——服务的启动类型）

| 数值 | 含义 | 说明 |
| --- | --- | --- |
| `0` | Boot 启动 | 由启动加载器加载，内核关键，**严禁修改** |
| `1` | System 启动 | 由内核加载，系统关键，**严禁修改** |
| `2` | Automatic（自动） | 开机自动运行 |
| `3` | Manual（手动） | 按需启动（被依赖或调用时启动） |
| `4` | Disabled（禁用） | 服务完全禁用 |

### Type 值（服务 / 驱动类型）

| 数值 | 含义 |
| --- | --- |
| `1` | 内核驱动（Kernel Driver） |
| `2` | 文件系统驱动 |
| `4` | 适配器（网络组件类） |
| `8` | 文件系统识别器驱动 |
| `16`（0x10） | 独立进程服务（Own Process）——常规定义型服务 |
| `32`（0x20） | 共享进程服务（Share Process）——多服务共用一个 svchost |

### 其他常用值

| 值名 | 含义 |
| --- | --- |
| `ImagePath` | 服务的可执行文件路径 |
| `DisplayName` / `Description` | 显示名 / 描述 |
| `FailureActions` | 失败恢复操作（自动重启服务 / 重启计算机等） |
| `DependOnService` | 依赖的其他服务（改某个服务前先看它被谁依赖） |

> 💡 常见用法：把某服务 `Start` 改为 `4` 即禁用，改回 `3`（手动）或 `2`（自动）恢复。日常操作更推荐直接用 `services.msc` 图形界面改启动类型（本质就是改这个 Start 值），注册表方式适合脚本批量处理。

## 四、策略配置键示例：Windows Defender

```text
HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows Defender
```

这是通过**策略**层控制 Defender 行为的键（对应组策略「计算机配置 → 管理模板 → Windows 组件 → Windows Defender」），如新建 DWORD 值 `DisableAntiSpyware` = `1` 可策略级关闭 Defender——与上文 `Services\WinDefend` 的服务注册键是**两码事**，前者是行为开关、后者是服务注册信息。

## 五、操作提醒

1. **改前备份**：右键导出对应服务键为 `.reg` 文件，出问题双击导入恢复；
2. **看清依赖**：改 `Start` 前检查 `DependOnService` 与其他服务对本服务的依赖，避免连锁故障；
3. `Start=0/1` 的（驱动类）**永远不要动**；
4. 禁用后异常：进安全模式或用 `regedit`（也可 `sc config 服务名 start= demand` 命令行）改回 `3`。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| 所有服务注册于 `HKLM\SYSTEM\CurrentControlSet\Services\<服务名>` | ✅ 属实：服务控制管理器（SCM）标准机制 |
| `mpssvc` = 防火墙服务、`wuauserv` = Windows Update 服务 | ✅ 属实 |
| 「HKLM\SOFTWARE\Policies\Microsoft\Windows Defender 是 Defender 的服务注册路径」 | ⚠️ 澄清：该键是**策略配置键**（行为开关），Defender 服务本体注册于 `Services\WinDefend`，两者用途不同，文中已区分 |
| Start 值：0=Boot / 1=System / 2=自动 / 3=手动 / 4=禁用 | ✅ 属实：SCM 标准定义 |
| Type 值：1=内核驱动 / 2=文件系统驱动 / 4=适配器 / 8=识别器 / 16=独立进程 / 32=共享进程 | ✅ 属实（原资料 Type=4 描述含混，已按标准修正为「适配器」） |
| ImagePath / DisplayName / Description / FailureActions 含义 | ✅ 属实 |

**参考来源：**

- [Microsoft Learn — Service Control Manager（SCM 官方文档）](https://learn.microsoft.com/en-us/windows/win32/services/service-control-manager)
- [Microsoft Learn — Services（服务概述）](https://learn.microsoft.com/en-us/windows/win32/services/services)
- [Wikipedia — Windows service](https://en.wikipedia.org/wiki/Windows_service)
