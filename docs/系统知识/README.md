---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# 系统知识

Windows 系统机制、电源管理、排障工具与常用命令的知识分类。

> 本目录侧重“怎么查、怎么配、怎么排障”的系统知识；涉及是否值得优化、风险等级与备份恢复的统一判断，见 [系统调优与安全](../系统调优与安全/README.md)。

## 文章

### 系统机制与命令速查
- [Windows 常用命令列表](./Windows常用命令列表.md) — Win+R / 命令行 / MSC / CPL 速查与事实核查
- [Windows 常用环境变量列表](./Windows常用环境变量列表.md) — `%APPDATA%` / `%SystemRoot%` 等变量与 `set` / `setx` 区别
- [Windows 系统服务对应注册表路径](./Windows系统服务对应注册表路径.md) — 服务与注册表 `Services\` 的对应关系
- [Windows 目录联接 Junction 与符号链接辨析](./Windows目录联接Junction与符号链接辨析.md) — 三种链接对照、删除语义实测与多应用共享数据目录实战

### 电源与睡眠管理
- [电源计划创建与优化指南](./电源计划创建与优化指南.md) — `powercfg`、Power Settings Explorer 与组策略锁定（主文）
- [Windows 睡眠、休眠与混合睡眠详解](./Windows-睡眠-休眠与混合睡眠详解.md) — 睡眠/休眠/混合睡眠原理与唤醒排障
- [Windows 虚拟内存设置指南](./Windows虚拟内存设置指南.md) — 页面文件、提交容量与崩溃转储
- [Windows 内存压缩功能与 MMAgent 设置](./Windows内存压缩功能与MMAgent设置.md) — Memory Compression / MMAgent / Prefetch 机制

### 启动与驱动
- [Windows 启动配置与 tweakbyjie 对应说明](./Windows启动配置与tweakbyjie对应说明.md) — BCD / 测试模式 / Device Guard 启动项与脚本边界
- [UEFI WPBT 固件自动注入机制与 Windows 防御](./UEFI-WPBT固件自动注入与Windows防御.md) — ACPI WPBT 表、厂商后台静默下发原理与 DisableWpbtExecution 注册表防御
- [Windows 新驱动程序策略与关闭方法](./Windows新驱动程序策略与关闭方法.md) — 驱动更新策略与适用场景
- [安装系统时跳过硬件和 TPM 检测](./安装系统时跳过硬件和TPM检测.md) — 安装阶段的硬件检查与兼容处理

### 排障与系统调整
- [用事件查看器排查黑屏蓝屏绿屏崩溃](./用事件查看器排查黑屏蓝屏绿屏崩溃.md) — `eventvwr` / Bug Check / WHEA 排障路径
- [Defender 删除脚本风险与恢复边界](./Defender删除脚本风险与恢复边界.md) — 高风险专题，`defender-removal.ps1` 的不可逆边界
- [删除此电脑中多余软件快捷方式图标](./删除此电脑中多余软件快捷方式图标.md) — 命名空间与清理方法
- [禁用 Windows 通知中心与操作中心](./禁用Windows通知中心与操作中心.md) — 通知/操作中心的关闭与恢复
- [调整 Windows 滚动条宽度与高度](./调整Windows滚动条宽度与高度.md) — 滚动条尺寸的注册表与界面调整

## 建议阅读顺序

1. 先看 [电源计划创建与优化指南](./电源计划创建与优化指南.md) 建立 AC/DC 与 `powercfg` 基础；
2. 再按需查 [常用命令](./Windows常用命令列表.md) / [环境变量](./Windows常用环境变量列表.md) / [服务注册表路径](./Windows系统服务对应注册表路径.md)；
3. 遇到睡眠/唤醒/崩溃问题时，查 [睡眠详解](./Windows-睡眠-休眠与混合睡眠详解.md) 与 [事件查看器](./用事件查看器排查黑屏蓝屏绿屏崩溃.md)；
4. 涉及内存/虚拟内存/启动/BCD 的修改，先读对应专题再决定是否执行。

## 与其他分类的边界

- `系统调优与安全/`：优化原则、风险等级、服务/VBS 的调优判断；`系统知识/` 负责机制与排障本身。
- `CPU与延迟/`、`GPU与显示/`、`内存与存储/`：更聚焦调度/图形/存储原理；`系统知识/` 提供通用的命令与电源排障工具。
- `验机相关/`：OOBE / Audit Mode / 激活与装机流程；`系统知识/` 处理装好系统后的日常设置与排障。

执行层参考见 [项目导航](../项目导航/README.md)，电源 `ultimate-performance.pow` 的来源与校验见 `tweakbyjie/docs/POWER-PLAN-SOURCE.md`。
