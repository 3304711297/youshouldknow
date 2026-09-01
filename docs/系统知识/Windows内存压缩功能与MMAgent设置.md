---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: [1]
---

# Windows 内存压缩功能与 MMAgent 设置

> **分类**：系统知识 · 内存管理
>
> **适用场景**：了解 Windows 内存压缩（Memory Compression）的原理与代价，判断自己的机器是否适合关闭它；以及 MMAgent 全家设置（程序预加载 / 预运行 / 页合并等）的含义与调优思路。
>
> 本文命令与参数已对照微软官方文档核实，经验建议部分为社区共识，核查记录见文末。

---

## 一、内存压缩是什么，为什么要考虑关闭

**内存压缩**（Windows 10 起默认开启）是把本要换出到磁盘（页面文件）的内存数据**压缩后仍存放在物理内存**中，用 CPU 算力换取更少的磁盘换页：

- **收益**：内存吃紧时减少读写页面文件，对机械硬盘 / 小内存机器明显更流畅；
- **代价**：压缩 / 解压持续消耗 **CPU 性能**，且读写都要经过一道压缩环节，增加延迟。

因此对 **CPU 性能有限**的机器，开启此功能可能得不偿失（负优化）。

## 二、什么条件下建议关闭

满足**任意一条**即可考虑关闭（经验建议，非官方规定）：

| 条件 | 理由 |
| --- | --- |
| ❶ CPU 性能较弱 | 压缩解压开销占比大，负优化更明显 |
| ❷ 内存容量 ≥ 20GB | 内存宽裕时极少触发换页，压缩的收益几乎用不上，只剩 CPU 开销 |
| ❸ 内存超频过 | 内存带宽 / 延迟已优化到位，换页惩罚相对更低，保留压缩不划算 |

> 反过来说：小内存 + 机械硬盘 + CPU 尚可的机器**不建议关闭**，内存压缩正是为这类配置设计的。

## 三、关闭教程

1. 打开 **PowerShell（管理员）**；
2. 查看当前状态（关注 `MemoryCompression` 一行为 True / False）：

   ```powershell
   Get-MMAgent
   ```

3. 关闭内存压缩（`-mc` 是 `MemoryCompression` 参数的缩写）：

   ```powershell
   Disable-MMAgent -mc
   ```

4. **重启电脑**生效（任务管理器中「系统压缩内存」的相关开销随之消失）。

恢复开启：`Enable-MMAgent -mc` 后重启。

### 与 tweakbyjie 的实际对应关系

`tweakbyjie.ps1` 在主菜单 `1` → 系统行为优化 `2` 中执行 `Disable-MMAgent -mc`，并在执行后用 `Get-MMAgent` 检查 `MemoryCompression=False`。该路径会提示需要重启，但当前脚本没有保存执行前的 Memory Compression 状态，也没有自动恢复入口；需要恢复时应手动执行上面的 `Enable-MMAgent -mc` 并重启。

脚本同时把传统注册表 `EnablePrefetcher` 写为 `0`，但没有同步修改 MMAgent 的 `ApplicationLaunchPrefetching`。两者是两套机制，不能把其中一个的验证结果当作另一个已经关闭。

## 四、MMAgent 其他设置详解

`Get-MMAgent` 输出中的每一项都可以单独开关（`Enable-MMAgent` / `Disable-MMAgent` 加对应参数）：

| 设置项 | 含义 | 调优建议 |
| --- | --- | --- |
| `ApplicationLaunchPrefetching` | 程序启动预读取：把程序文件按历史启动记录预加载进内存 | 通用场景建议保持开启；追求极致可控可用注册表细调（见下节） |
| `ApplicationPreLaunch` | 程序预运行：按使用习惯提前在后台预启动应用 | 按需关闭（不希望后台「偷跑」程序时） |
| `MaxOperationAPIFiles` | Operation API 维护的预读取文件数量上限（`Set-MMAgent -MaxOperationAPIFiles 数值`） | 内存越大可以开得越多 |
| `OperationAPI` | 操作 API：让预读取覆盖非系统程序 | 内存大就开，可让内存预读取任何程序 |
| `PageCombining` | 页合并：系统定期扫描并合并内容相同的内存页以节省内存 | 以节省 CPU 为先就关；内存紧张且 CPU 富余再开 |

## 五、注册表方式细调程序预读取

程序启动预读取也可以用注册表控制（传统逻辑预取器的开关），定位到：

```text
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters
```

修改 `EnablePrefetcher`（DWORD）：

| 数值 | 含义 |
| --- | --- |
| `0` | 完全关闭预读取（含启动和应用程序） |
| `1` | **仅启用应用程序预读取** |
| `2` | **仅启用启动预读取** |
| `3` | 两者都启用（**默认值**） |

> ⚠️ 注意：
> 1. 部分流传资料把 1 / 2 的含义写反——正确为 **1 = 仅应用程序、2 = 仅启动**（本文已核实）；
> 2. 该注册表值是传统预取器开关，与上节 MMAgent 的 `ApplicationLaunchPrefetching`（现代开关）是两套机制，现代系统上建议优先用 MMAgent 命令；
> 3. 对多数用户，保持默认值 `3` 是综合表现最好的选择；手动清空 `C:\Windows\Prefetch` 文件夹或随意调低此值反而会拖慢启动与程序加载，属于流传已久的优化误区。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| `Get-MMAgent` 查看状态、`Disable-MMAgent -mc` 关闭、需重启生效、`Enable-MMAgent -mc` 恢复 | ✅ 属实：MMAgent 模块官方文档（Microsoft Learn）确认全部参数；关闭后重启为社区与官方问答一致做法 |
| Windows 10 起内存压缩默认开启 | ✅ 属实 |
| 内存压缩以 CPU 开销换取减少磁盘换页 | ✅ 属实：机制如此，社区普遍确认（TechPowerUp 等讨论） |
| PageCombining = 合并相同内容的内存页以节省内存 | ✅ 属实：官方文档原文「内存管理器定期合并物理内存中的页面以减少物理内存占用」 |
| MaxOperationAPIFiles = Operation API 维护的预读取文件数 | ✅ 属实：官方文档（Enable-MMAgent 参数说明） |
| ApplicationLaunchPrefetching / ApplicationPreLaunch / OperationAPI 均为真实可开关项 | ✅ 属实：官方文档参数列表 |
| 关闭条件（CPU 弱 / 内存 ≥ 20GB / 内存超频） | 💡 经验建议：逻辑成立（内存宽裕或换页代价低时压缩收益趋零、只剩 CPU 开销），但阈值非官方标准，按实际体验取舍 |
| EnablePrefetcher 注册表 0/1/2/3 档位 | ✅ 已核实并修正：0 = 全关，1 = 仅应用程序，2 = 仅启动，3 = 两者（默认）——smallvoid、Ghacks 等权威记载一致；部分流传版本 1/2 写反 |
| 清空 Prefetch 文件夹 / 调低 EnablePrefetcher 提速 | ❌ 误区：Ghacks 等明确指出默认 3 综合最优，此类操作通常负优化 |

**参考来源：**

- [Microsoft Learn — Disable-MMAgent](https://learn.microsoft.com/en-us/powershell/module/mmagent/disable-mmagent?view=windowsserver2025-ps)
- [Microsoft Learn — Enable-MMAgent（含 MaxOperationAPIFiles、PageCombining 官方说明）](https://learn.microsoft.com/en-us/powershell/module/mmagent/enable-mmagent?view=windowsserver2025-ps)
- [Microsoft Learn — Get-MMAgent](https://learn.microsoft.com/en-us/powershell/module/mmagent/get-mmagent)
- [Super User — How to disable Windows 10 memory compression](https://superuser.com/questions/1000485/how-to-disable-windows-10-memory-compression)
- [NinjaOne — Enable or Disable Memory Compression in Windows 11](https://www.ninjaone.com/blog/enable-or-disable-memory-compression-in-windows-11/)
- [TechPowerUp — Memory Compression On or Off?](https://www.techpowerup.com/forums/threads/memory-compression-on-or-off.318537/)
- [smallvoid — Configure the logical prefetcher（EnablePrefetcher 档位）](https://smallvoid.com/article/winnt-logical-prefetcher.html)
- [Ghacks — EnablePrefetcher in PrefetchParameters](https://www.ghacks.net/2008/01/13/enableprefetcher-in-prefetchparameters/)
