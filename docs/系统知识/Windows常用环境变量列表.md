---
status: reference
risk: low
applies_to:
  - Windows 10/11 命令提示符与 PowerShell
  - Windows 系统目录和用户路径定位
verified_on: 2026-08-21
# 本次收尾未重新核验外部事实，verified_on 保留上次核验日期
---

# Windows 常用环境变量列表

> **分类**：系统知识 · 系统机制
>
> **适用场景**：在命令提示符、批处理脚本或资源管理器地址栏中快速定位系统目录、引用用户路径、编写脚本时使用。
>
> 本文变量与取值已对照微软官方文档核实，其中一处常见误述已修正（见文末核查记录）。

---

## 一、核心系统变量

| 变量 | 路径示例 | 说明 |
| --- | --- | --- |
| `%ALLUSERSPROFILE%` | `C:\ProgramData` | 所有用户的共享配置目录 |
| `%APPDATA%` | `C:\Users\<用户名>\AppData\Roaming` | 当前用户的漫游应用程序数据 |
| `%CommonProgramFiles%` | `C:\Program Files\Common Files` | 64 位系统通用程序文件目录 |
| `%CommonProgramFiles(x86)%` | `C:\Program Files (x86)\Common Files` | 32 位程序通用文件目录（仅 64 位系统存在） |
| `%ComSpec%` | `C:\Windows\System32\cmd.exe` | 系统命令行解释器路径 |
| `%HOMEDRIVE%` | `C:` | 用户主目录所在驱动器盘符 |
| `%HOMEPATH%` | `\Users\<用户名>` | 用户主目录相对路径 |
| `%LOCALAPPDATA%` | `C:\Users\<用户名>\AppData\Local` | 当前用户本地应用数据（非漫游） |
| `%ProgramData%` | `C:\ProgramData` | 同 `%ALLUSERSPROFILE%`（Vista 起的新名称） |
| `%ProgramFiles%` | `C:\Program Files` | 64 位程序安装目录 |
| `%ProgramFiles(x86)%` | `C:\Program Files (x86)` | 32 位程序安装目录（仅 64 位系统存在） |
| `%PUBLIC%` | `C:\Users\Public` | 公共用户共享目录 |
| `%SystemDrive%` | `C:` | 系统根目录驱动器 |
| `%SystemRoot%` | `C:\Windows` | Windows 系统目录 |
| `%TEMP%` / `%TMP%` | `C:\Users\<用户名>\AppData\Local\Temp` | 当前用户临时文件目录 |
| `%USERDOMAIN%` | `<计算机名或域>` | 用户所属域 / 工作组名称 |
| `%USERNAME%` | `<用户名>` | 当前登录用户名 |
| `%USERPROFILE%` | `C:\Users\<用户名>` | 当前用户配置文件目录 |
| `%WINDIR%` | `C:\Windows` | 同 `%SystemRoot%`（Win9x 时代遗留别名） |

## 二、其他实用变量

| 变量 | 示例 / 取值 | 说明 |
| --- | --- | --- |
| `%CD%` | 当前目录 | 命令行当前工作目录（动态变化）※cmd 动态变量 |
| `%DATE%` / `%TIME%` | 当前日期 / 时间 | 命令行中动态生成 ※cmd 动态变量 |
| `%NUMBER_OF_PROCESSORS%` | 如 `16` | **逻辑处理器数量（含超线程）**，即任务管理器「逻辑处理器」数，不是物理核心数 |
| `%OS%` | `Windows_NT` | 操作系统类型标识（NT 内核恒为此值） |
| `%PATH%` | 多路径串 | 系统可执行文件搜索路径，**分号 `;` 分隔** |
| `%PROCESSOR_ARCHITECTURE%` | `AMD64` / `ARM64` / `x86` | 处理器架构类型 |
| `%RANDOM%` | `0～32767` | 命令行中每次引用生成新随机数 ※cmd 动态变量 |

> ※ **cmd 动态变量说明**：`%CD%`、`%DATE%`、`%TIME%`、`%RANDOM%` 由命令提示符实时合成，不写入环境块——**PowerShell 中不可用**（PowerShell 用 `Get-Location`、`Get-Date`、`Get-Random` 等替代）。

## 三、查看环境变量

1. **命令行查看全部**：命令提示符输入 `set`（可带前缀过滤，如 `set path`）；
2. **图形界面**：右键「此电脑」→ 属性 → **高级系统设置** → 「环境变量」按钮（或 `Win + R` → `sysdm.cpl` → 高级）。

## 四、使用示例

- **资源管理器地址栏**：输入 `%appdata%` 回车，直接打开当前用户的 AppData\Roaming 文件夹；
- **批处理脚本**：

  ```bat
  copy "D:\report.txt" "%USERPROFILE%\Documents"
  ```

- **命令行快速跳转**：

  ```bat
  cd %ProgramFiles%
  ```

## 五、提示与注意事项

1. 变量名**不区分大小写**（`%userprofile%` 与 `%USERPROFILE%` 等效）；
2. `%PATH%` 多路径用分号 `;` 分隔，末尾不要留多余分号；
3. 自定义 / 修改变量：
   - `set` 命令——仅**当前会话**有效，窗口关闭即失效；
   - `setx` 命令或图形界面——**永久写入**（setx 写入后需**新开**终端才生效，当前窗口读不到）；
4. 路径类变量（如 `%USERPROFILE%`）在资源管理器地址栏可用；值类变量（如 `%USERNAME%`、`%RANDOM%`）只在命令行 / 脚本中有意义。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| 各变量路径与含义（APPDATA/LOCALAPPDATA/ProgramFiles 系列/SystemRoot/TEMP/USERPROFILE 等） | ✅ 属实：与微软官方环境变量文档一致 |
| `%ALLUSERSPROFILE%` 与 `%ProgramData%` 同指向 `C:\ProgramData` | ✅ 属实：Vista 起二者等价，ProgramData 为新规范名 |
| `%ProgramFiles(x86)%`、`%CommonProgramFiles(x86)%` 仅 64 位系统存在 | ✅ 属实 |
| `%NUMBER_OF_PROCESSORS%` 为「CPU 物理核心数量」 | ❌ 修正：该变量返回**逻辑处理器数量（含超线程）**，与任务管理器「逻辑处理器」一致；原稿「物理核心」为常见误述 |
| `%CD%`/`%DATE%`/`%TIME%`/`%RANDOM%` 为 cmd 动态变量，PowerShell 不可用 | ✅ 属实：cmd 实时合成，不写入环境块 |
| `%RANDOM%` 取值 0～32767 | ✅ 属实 |
| `%OS%` 恒为 `Windows_NT` | ✅ 属实：NT 内核标识，不代表具体版本 |
| `set` 会话级 vs `setx` 永久（新终端生效） | ✅ 属实：二者作用域与生效时机差异为标准行为 |

**参考来源：**

- [Microsoft Learn — USMT 可识别的环境变量（官方变量对照表）](https://learn.microsoft.com/en-us/windows/deployment/usmt/usmt-recognized-environment-variables)
- [Microsoft Learn — set 命令](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/set_1)
- [Microsoft Learn — 环境变量（Win32 概述）](https://learn.microsoft.com/en-us/windows/win32/procthread/environment-variables)
