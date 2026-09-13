---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# Windows 进程优先级持久化：IFEO PerfOptions

> **定位**：机制说明与取值辨析，非默认推荐项。
>
> **适用场景**：需要让某个程序每次启动都带指定 CPU / I/O 优先级（任务管理器里手动改优先级重启即失效），或需要长期压低某个后台进程的资源占用。

## 一、机制：它是什么

`Image File Execution Options`（IFEO）原本是调试器用的注册表机制：系统在创建进程时读取 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<程序名>.exe`，据此决定调试器挂接等行为。该键下的 `PerfOptions` 子键被系统额外用于指定**新进程启动时的性能偏好**，即优先级持久化。

完整路径：

```text
HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<程序名.exe>\PerfOptions
```

该子键默认不存在，需要手工新建。叶键名必须与可执行文件**同名且带 `.exe` 扩展名**。

## 二、可用键值与枚举

`PerfOptions` 下常见四个 `REG_DWORD` 值：

| 键名 | 含义 | 可选值 |
| --- | --- | --- |
| `CpuPriorityClass` | 进程优先级类 | `1`=Idle，`2`=Normal（默认），`3`=High，`4`=Real-time，`5`=Below Normal，`6`=Above Normal |
| `IoPriority` | I/O 优先级 | `0`=Very Low，`1`=Low，`2`=Normal（默认），`3`=High，`4`=Critical |
| `PagePriority` | 内存页优先级 | `0`=Very Low ～ `5`=Normal |
| `WorkingSetLimitInKB` | 工作集上限（KB） | 自定义数值 |

### 两个容易踩的边界

1. **IO 优先级经 IFEO 只能设到 Normal 及以下**。`IoPriority=3`（High）虽然枚举合法，但通过 IFEO 机制写入不会生效——High 只能由程序自身或 `System Informer` 一类工具在运行时设置；`4`（Critical）为系统保留（页文件请求使用）。想让某个进程拿到 High I/O，写 IFEO 是无效路径。
2. **优先级继承受限**。`CpuPriorityClass` 对子进程的继承**按设计只支持 Idle 与 Below Normal**；设为 High 等更高等级时，子进程不会继承该等级。

## 三、典型用法

### 3.1 让某个程序以高 CPU 优先级启动

```text
路径：HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\example.exe\PerfOptions
新建 REG_DWORD  CpuPriorityClass = 3   （十进制）
```

### 3.2 把某个后台程序压到最低

```text
路径：...\Image File Execution Options\example-bg.exe\PerfOptions
新建 REG_DWORD  CpuPriorityClass = 1   （十进制，Idle）
可选：IoPriority = 1（Low），PagePriority = 1
```

修改后**需要程序重新启动**才生效（IFEO 在进程创建时读取）。

### 3.3 回退

删除对应的 `<程序名.exe>` 整个子键即可恢复默认；单独删除 `PerfOptions` 也不会留下其他副作用。这个机制不写入启动项、不注册服务，回退成本很低。

## 四、它与"限制反作弊扫盘"不是一回事

社区流传不少"给反作弊进程建 IFEO 子键、把 `CpuPriorityClass` 降到 `1` 就能限制扫盘"的说法。从机制上说不过去：

- IFEO 只设置**用户态进程启动时刻的优先级类**，它改变的是调度权重，不是磁盘访问权限；
- 主流内核级反作弊（如 ACE、SGuard）的扫描与校验工作大量发生在**内核驱动（`.sys`）**中，不受用户态进程优先级约束；
- 若该进程被反作弊自身重新提升优先级或在其驱动侧做校验，用户态设置可能被覆盖。

降优先级本身是**合法且低风险**的系统功能，但把它当作"限制扫盘/提升帧率"的手段，缺少可验证的机制支撑；把它当作"对抗反作弊"的手段，则触及账号安全风险，本库不提供此类操作指引。相关辨析见[社区降延迟调机清单辨析](../系统调优与安全/社区降延迟调机清单辨析.md)。

## 五、风险与边界

| 项 | 说明 |
| --- | --- |
| 设置 `Real-time`（`4`） | 极高风险。实时优先级的用户态进程可能挤占系统服务与输入线程的 CPU 时间，导致桌面卡死甚至需要强制断电恢复。不要使用 |
| 对系统关键进程设置 | 与系统服务、计划任务、驱动交互的进程被提权后可能引发优先级反转或死锁 |
| 提权路径滥用 | IFEO 同样可被用于进程劫持（`Debugger` 值）。该键的写权限应只对管理员开放，异常条目应视为可疑 |
| 无回读验证 | 机制本身不提供状态查询入口，只能通过进程启动后的实际优先级（任务管理器 / `Get-Process -IncludeUserName` 等）确认 |

## 六、与 tweakbyjie 的关系

`tweakbyjie` 当前**没有**任何 IFEO / `PerfOptions` 相关执行项——这类设置需要逐程序指定，不具备"一键优化"的安全默认值，不适合放进统一菜单。本文作为机制参考，不修改主脚本。

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| `PerfOptions` 位于 `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\<程序名.exe>` 下，默认不存在 | ✅ 属实：IFEO 机制为微软公开机制（[Image File Execution Options](https://learn.microsoft.com/en-us/windows/win32/debug/image-file-execution-options)），`PerfOptions` 子键在 Windows Internals 中有记述，生产环境中很少见 |
| `CpuPriorityClass` 取值 1=Idle / 2=Normal / 3=High / 4=Realtime / 5=Below Normal / 6=Above Normal | ✅ 属实：多份社区技术文档与工具说明一致（[Aloneguid 实测记录](https://www.aloneguid.uk/posts/2020/12/proc-limit-image-file-exec/)、`gist` 笔记、Softdrive 支持文档） |
| `IoPriority` 取值 0=Very Low / 1=Low / 2=Normal / 3=High / 4=Critical；经 IFEO 只能设到 Normal 及以下 | ✅ 属实：`IoPriority` 的 High 需程序自身或 System Informer 一类工具设置，Critical 为系统保留（页文件请求）；社区文档明确标注 IFEO 机制下 High 不可用 |
| `CpuPriorityClass` 对子进程的继承按设计只限 Idle 与 Below Normal | ✅ 属实：对应 `SetPriorityClass` 文档中 `IDLE_PRIORITY_CLASS` / `BELOW_NORMAL_PRIORITY_CLASS` 的继承行为说明 |
| 修改后需重启目标程序才生效 | ✅ 属实：IFEO 在进程创建时读取，已运行进程不受影响 |
| 删除子键即可回退，无残留 | ✅ 属实：机制无服务/启动项等持久化载体 |
| 对腾讯 ACE / SGuard 类内核级反作弊降优先级可"限制扫盘" | ⚠️ 机制不成立：IFEO 只作用于 Ring 3 用户态进程优先级，内核驱动扫描不受其约束；且此类操作有账号安全风险，本库不作操作指引 |
| tweakbyjie 无 IFEO/PerfOptions 执行项 | ✅ 属实：`Modules/` 下各模块未见 `Image File Execution Options` 或 `PerfOptions` 写入 |

**参考链接：**

- [Microsoft Learn — Image File Execution Options](https://learn.microsoft.com/en-us/windows/win32/debug/image-file-execution-options)
- [Microsoft Learn — SetPriorityClass 函数](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-setpriorityclass)
- [PerfOptions 社区实测记录（CPU/I/O/Page 优先级枚举）](https://www.aloneguid.uk/posts/2020/12/proc-limit-image-file-exec/)
- [IFEO PerfOptions 键值笔记（继承与 I/O 边界）](https://gist.github.com/HelderMagalhaes/899766e74da8cd3923fd47c41c07b320)
