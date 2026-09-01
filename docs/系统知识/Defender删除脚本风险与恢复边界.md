---
applies_to:
  - Windows 10
  - Windows 11
risk: high
tweak_module: [5]
---

# defender-removal.ps1 风险与恢复边界

## 文档范围

本文专门说明 `tweakbyjie/defender-removal.ps1`。它与 `tweakbyjie.ps1` 的 Part 5“关闭安全中心”不是同一个入口：前者是独立的高风险删除脚本，后者主要是停用服务、写入策略并可选删除部分组件。

## 脚本行为

`defender-removal.ps1` 不只是把服务改为 Disabled。根据当前源码，它会在管理员权限检查后，尝试删除 Defender 相关服务注册、WinRT/Svchost 注册、CLSID/App/Shell/Autologger 等注册表键和值，并删除相关实体文件（`C:\ProgramData\Microsoft\Windows Defender` 目录连同隔离区数据一并删除）。受 TrustedInstaller 保护而删除失败的键不会被自动以 SYSTEM 重试：脚本只报告 `[FAIL]`，并提示借助 NSudo/PowerRun 等提权工具手动重试（源码头部中文注释仍写有“再以 SYSTEM 批量重试”，与英文注释和实际实现矛盾，以实现为准）。脚本只在删除前查询对象是否存在（不存在则跳过），删除后没有回读检查，也没有把完整原始系统状态保存成可恢复备份。

这类操作可能影响：

- Microsoft Defender 实时防护、篡改防护和安全中心；
- SmartScreen、通知、计划任务和安全策略；
- Windows 更新、系统组件修复、应用启动和依赖 Defender 的功能；
- SFC/DISM 能否修复组件，以及后续 Windows 版本升级。

## 与 Part 5 的区别

| 项目 | Part 5（`tweakbyjie.ps1`） | `defender-removal.ps1` |
| --- | --- | --- |
| 主要动作 | 停止/禁用服务、写入安全策略，可选删除任务/启动项/SecHealthUI | 删除大量服务注册、系统注册表对象和实体文件 |
| 备份 | 没有完整统一备份/自动恢复 | 没有原始状态备份 |
| 验证 | 有限的查询/状态输出，缺少完整回读闭环 | 删除前存在性查询（不存在即跳过），无删除后回读 |
| 恢复 | 需要手工检查、系统修复或重新安装相关组件 | 脚本本身不可逆，不能声称可恢复 |

## 恢复边界

脚本没有提供“撤销”命令，也没有保存被删除键、值、服务注册和文件的完整快照。删除完成后，恢复不能依赖重新运行脚本或简单地把服务启动类型改回 Automatic。可能需要：

1. 使用系统还原点或完整系统镜像回滚；
2. 使用 Windows 安装介质、DISM/SFC 和官方组件修复流程；
3. 在组件无法修复时重新安装 Windows；
4. 重新配置 Defender、SmartScreen、计划任务和企业安全策略。

这些恢复路径是否可用取决于删除范围、Windows 版本和系统备份情况。执行前应确认有可启动的恢复介质和必要的 BitLocker 恢复密钥。

## 使用结论

- 该脚本不应被归类为普通游戏性能优化。
- 不应在没有完整系统备份、恢复介质和明确授权的机器上运行。
- 本项目当前只记录其行为和风险，不建议为了补齐优化数量而修改或扩展该脚本。
- 在 `tweakbyjie → youshouldknow` 映射中，它属于 Registry/Security 高风险独立项目，状态应保持“有执行项但不可逆、说明需谨慎”，不能标记为具备完整恢复闭环。

## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-29 重核：对照 HEAD b905950 的 `defender-removal.ps1`（342 行）逐条复核，并确认 DryRun 默认、-Execute 显式执行与无备份路径仍成立）。

| 声明 | 核查结果 |
| --- | --- |
| defender-removal.ps1 删除 Defender 服务注册、WinRT/Svchost、CLSID/App/Shell/Autologger 键值与实体文件 | ✅ 属实：342 行源码含上述对象的大量删除项（2026-08-29 重核） |
| 受保护对象以管理员尝试后按 SYSTEM 批量重试 | ❌ 勘误（2026-08-29 重核）：当前实现不自动以 SYSTEM 重试；TrustedInstaller 保护键删除失败仅报 `[FAIL]`，提示借助 NSudo/PowerRun 提权后手动重试。源码头部中文注释与实现矛盾，已按实现修正正文 |
| 无原始状态备份、无撤销命令、脚本不可逆 | ✅ 属实：全文无 backup/restore 路径（2026-08-29 重核） |
| 默认 DryRun，需显式 -Execute 才会修改系统 | ✅ 属实：不带 `-Execute` 时仅打印 DryRun 清单即退出（2026-08-29 重核补充） |
| 与 Part 5 是不同入口，Part 5 的 Defender 策略值有快照而删除脚本没有 | ✅ 属实：defender-policy-backup.json 仅覆盖 Part 5（2026-08-29 重核） |
