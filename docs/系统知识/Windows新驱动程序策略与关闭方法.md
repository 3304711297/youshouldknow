---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# Windows 新驱动程序策略与关闭方法（2026 年 4 月起）

> **分类**：系统知识 · 驱动与安全
>
> **适用场景**：2026 年 4 月安全更新后，旧驱动（交叉签名驱动）被系统策略阻止加载，导致硬件失灵、蓝屏黑屏等疑难杂症时，确认原因并关闭该策略。
>
> 本文已对照微软官方支持文档逐项核实（官方页面即原帖评论区所附链接），核查记录见文末。

---

## 一、背景：什么是 Windows 驱动程序策略

微软在 **2026 年 4 月安全更新**中更换了驱动程序信任策略：此前受信任的旧驱动由已过期的**交叉签名程序**签署，此后默认不再被信任。官方公告：[Advancing Windows driver security: Removing trust for the cross-signed driver program](https://techcommunity.microsoft.com/blog/windows-itpro-blog/advancing-windows-driver-security-removing-trust-for-the-cross-signed-driver-pro/4504818)。

**Windows 驱动程序策略**是 Windows 内核中限制内核驱动加载的策略，激活时仅允许加载：

1. 通过 **Microsoft WHCP**（Windows 硬件兼容性计划）正确签名的驱动；
2. 策略内置允许列表上的可信旧驱动（广泛使用但未过 WHCP 认证的交叉签名驱动）。

其余驱动一律阻止。策略分两阶段工作：

| 阶段 | 行为 |
| --- | --- |
| **审核模式** | 违规驱动仅记录事件，仍允许加载；系统累计运行时间（约 250 小时）、启动会话等指标，评估设备是否适合强制 |
| **强制模式** | 满足条件后自动转入，违规驱动**直接阻止加载**，重启后依然生效 |

评估期内一旦加载了「将被阻止」的驱动，计时器归零、重新评估——所以一直在用旧驱动的机器会长期停留在审核模式。

## 二、怎么判断是不是它挡了你的驱动

**典型症状**：硬件设备无法运行、打印机 / 网卡 / GPU 等识别异常、依赖内核驱动的软件起不来。

**查事件日志确认**（管理员 PowerShell）：

```powershell
Get-WinEvent -LogName 'Microsoft-Windows-CodeIntegrity/Operational' |
  Where-Object { $_.Id -in 3076, 3077 } | Select-Object TimeCreated, Id, Message
```

- **事件 ID 3076**：驱动被审核策略记录（本应阻止，审核模式下仍放行）——对应审核策略 GUID `{784C4414-79F4-4C32-A6A5-F0FB42A51D0D}`；
- **事件 ID 3077**：驱动被强制策略**实际阻止**——对应强制策略 GUID `{8F9CB695-5D48-48D6-A329-7202B44607E3}`。

这两个 GUID 与策略文件名一一对应，也是下文删除操作的目标。

## 三、关闭方法

### 方法一：CiTool 命令（推荐，已装 2026 年 7 月或更高更新的设备）

2026 年 7 月更新后，微软放开了该策略的启动保护，**无需进 BIOS、无需 PE**：

1. 右键「开始」→ **终端(管理员)**；
2. 运行：

   ```powershell
   CiTool.exe --remove-policy "{8F9CB695-5D48-48D6-A329-7202B44607E3}"
   ```

3. **重启设备**。命令执行后策略在当前会话仍然生效，重启后彻底禁用。

### 方法二：关安全启动 + 删除策略文件（未装 2026 年 7 月更新的设备）

旧版本系统的策略有额外的启动保护，需按官方文档操作（即原帖给出的路线）：

1. 重启进 UEFI/BIOS，**暂时关闭安全启动**（通常在「安全性」或「启动」菜单）；
2. 进 PE（或在系统下用管理员终端），挂载 EFI 系统分区为 S: 盘：

   ```bat
   mountvol S: /S
   ```

3. 删除**强制策略**文件（EFI 分区与 Windows 两处）：

   ```powershell
   Remove-Item "S:\EFI\Microsoft\Boot\CiPolicies\Active\{8F9CB695-5D48-48D6-A329-7202B44607E3}.cip" -Force
   Remove-Item "$env:windir\System32\CodeIntegrity\CiPolicies\Active\{8F9CB695-5D48-48D6-A329-7202B44607E3}.cip" -Force
   ```

   > 若系统提示找不到某个文件，直接继续下一步即可。

4. 卸载 EFI 分区并重启，策略即被禁用：

   ```bat
   mountvol S: /d
   ```

5. 回 BIOS **重新开启安全启动**，恢复其保护。

**原帖补充的经验操作**（作者实践总结，非官方文档所载，一并处理可防策略恢复）：

- 删除前把涉及的 `.cip` 文件**备份到 U 盘**（不要备份到原系统所在磁盘）；
- 审核策略的同名文件（`{784C4414-...}.cip`）如存在也可一并删除；
- `Active` 以外的文件夹（如 `reverse` 文件夹）若有同名 `.cip` 文件也需删除，防止系统恢复策略；
- Windows 侧 `C:\Windows\Boot\EFI\CiPolicies\Active\` 下的同名副本也可一并清理。

## ⚠️ 风险提示

- 关闭驱动程序策略意味着**未经 WHCP 审查的旧驱动重新可以加载**，降低系统安全性——仅在旧驱动被挡、确实影响使用时操作；
- 优先考虑的正规路线：联系硬件厂商获取 WHCP 签名的新版驱动，或更新外设/软件版本；
- 删除策略文件后若出现问题，可用 U 盘中的备份恢复（把 `.cip` 复制回原路径后重启）。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| 微软 2026 年 4 月安全更新起不再默认信任交叉签名旧驱动 | ✅ 属实：微软官方公告（Tech Community）与官方支持文档明确记载 |
| 两个策略 GUID：审核 {784C4414-...}、强制 {8F9CB695-...} | ✅ 属实：官方文档原文一字不差 |
| 症状：硬件失灵 / 外设识别异常 / 内核驱动软件无法启动；事件 ID 3076（审核）/ 3077（阻止） | ✅ 属实：官方文档「如何知道驱动程序是否被阻止」章节 |
| 未装 2026-07 更新需关安全启动并手动删除强制策略文件（EFI 分区 + System32 两处） | ✅ 属实：官方文档「未安装 2026 年 7 月更新的设备」章节，与原帖路线一致 |
| 已装 2026-07 更新可用 `CiTool.exe --remove-policy` 一条命令关闭 | ✅ 属实：官方文档「具有 2026 年 7 月更新或更高版本更新的设备」章节（原帖发布时此方法尚未出现，属本文补充） |
| 审核模式约 250 小时评估、冲突归零重来；允许列表机制 | ✅ 属实：官方文档「工作原理」章节 |
| 备份勿放原系统盘、`reverse` 文件夹同名文件也需删除、`C:\Windows\Boot\EFI\...` 副本清理 | ⚠️ 原帖作者经验补充：方向合理（防止策略恢复/重新暂存），官方文档未记载，已按原意保留并标注 |
| 评论区所附微软链接 | ✅ 有效：即官方支持文档《Windows 驱动程序策略》，已收入参考来源 |

**参考来源：**

- 微软官方文档（原帖评论区链接）：《Windows 驱动程序策略》：<https://support.microsoft.com/zh-cn/windows/hardware/drivers/the-windows-driver-policy>
- 微软官方公告：Advancing Windows driver security — Removing trust for the cross-signed driver program：<https://techcommunity.microsoft.com/blog/windows-itpro-blog/advancing-windows-driver-security-removing-trust-for-the-cross-signed-driver-pro/4504818>
- 英文原版文档：The Windows Driver Policy：<https://support.microsoft.com/en-us/windows/hardware/drivers/the-windows-driver-policy>
