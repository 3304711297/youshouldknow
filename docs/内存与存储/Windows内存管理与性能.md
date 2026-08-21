# Windows 内存管理与性能

> **定位**：内存主题主入口，负责给出“该不该动”的判断框架。
>
> 详细机制见：
>
> - [Windows 内存压缩功能与 MMAgent 设置](../系统知识/Windows内存压缩功能与MMAgent设置.md) — 压缩、MMAgent 与 Prefetch
> - [Windows 虚拟内存设置指南](../系统知识/Windows虚拟内存设置指南.md) — 页面文件、提交容量与崩溃转储
>
> 执行层的实际目标、验证与恢复限制见 [全量逐项执行参考](../项目导航/tweakbyjie全量执行参考.md)；硬件超频见 [DDR5 内存超频](../内存超频/DDR5-内存超频时序参数公式速查.md)。

## 一、三个机制一句话

- **Memory Compression（内存压缩）**：用 CPU 压缩不活跃内存页，减少磁盘分页，但增加 CPU 开销；`MMAgent` 控制其开关。
- **Prefetch / SysMain**：根据历史加载行为预取程序与系统组件，改善启动与常用程序响应；`EnablePrefetcher` 与 `SysMain` 服务配合。
- **页面文件（Pagefile）**：磁盘上的虚拟内存后备，影响提交容量、崩溃转储与极端内存压力下的稳定性。

三者都不是“关闭即优化”；是否调整取决于内存容量、CPU 余量、存储类型与多任务压力，必须可回滚地测试。

## 二、适用判断

| 场景 | 倾向 | 说明 |
|---|---|---|
| 内存充足（≥32GB）且以游戏为主 | 保留压缩与 Prefetch，按需评估页面文件 | 压缩可减少卡顿时的磁盘抖动，Prefetch 利于启动 |
| 内存吃紧（≤16GB）且多任务/大型项目 | 优先加内存，再评估压缩与页面文件 | 关闭压缩可能把压力转回磁盘，体感不一定更好 |
| CPU 本就高负载（编译/转码/后台任务重） | 谨慎动压缩 | 压缩以 CPU 换内存，CPU 瓶颈时收益为负 |
| 已使用高速 NVMe 且追求启动一致性 | 保留 Prefetch 观察，再决定 | 关闭后首次启动与常用程序加载可能变慢 |
| 需要完整内存转储或极端提交容量 | 保留系统托管页面文件 | 自定义过小可能导致提交失败或转储不完整 |

不要把某篇教程的“固定值”当作所有机器的通用答案；先记录原值与基线，再单变量对照。

## 三、怎么看当前状态

```powershell
# 内存压缩与 MMAgent
Get-MMAgent

# Prefetch 配置
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters' -Name EnablePrefetcher

# 页面文件与提交
Get-CimInstance Win32_PageFileUsage | Format-List *
Get-CimInstance Win32_ComputerSystem | Select-Object AutomaticManagedPagefile
```

资源监视器 / 任务管理器 / 性能监视器可观察压缩、分页与提交的实时行为；配置层“写入成功”不等于运行时收益。

## 四、与 tweakbyjie 的关系

- `EnablePrefetcher=0`（`tweakbyjie` 主菜单 `1 → 2`）与 `Disable-MMAgent -mc` 有回读但无原值快照；恢复需手工写回或 `Enable-MMAgent -mc`。
- 页面文件当前不在脚本自动化范围内，知识文档的 GUI/系统托管原则不计为脚本覆盖。
- 具体编号、路径、类型与恢复边界见 [全量执行参考](../项目导航/tweakbyjie全量执行参考.md)。

## 五、风险与恢复

- 改前记录：注册表 Hive/路径/值名/类型/原值/是否存在、`Get-MMAgent` 原状态、页面文件托管状态与大小；
- 改后验证：配置回读 + 重启 + 启动/加载/游戏/多任务的 A/B 对照 + 睡眠/唤醒稳定性；
- 恢复：按记录逐项写回，原本不存在的值应删除；不要用另一台机器的值当通用恢复值。

## 事实核查记录

核验基准：tweakbyjie 仓库 main 分支源码（2026-08-21）。

| 声明 | 核查结果 |
| --- | --- |
| EnablePrefetcher=0（主菜单 1→2）与 Disable-MMAgent -mc 有回读但无原值快照 | ✅ 属实：Verify-RegDword/Get-MMAgent 回读，无专用快照文件 |
| 页面文件不在脚本自动化范围内 | ✅ 属实：源码无 pagefile 相关执行项（MEMORY-003） |
| 恢复方式（手工写回 / Enable-MMAgent -mc） | ✅ 属实：与执行参考 MEMORY-001/002 一致 |
