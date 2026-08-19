# Windows 内存管理与性能

> **定位**：Windows 内存管理主题主入口。
>
> 详细的 Memory Compression、MMAgent、Prefetch 和页面文件说明见：
>
> - [Windows 内存压缩功能与 MMAgent 设置](../系统知识/Windows内存压缩功能与MMAgent设置.md)
> - [Windows 虚拟内存设置指南](../系统知识/Windows虚拟内存设置指南.md)
>
> 本文保留主入口路径，用于说明主题边界：Windows 内存压缩用 CPU 压缩数据减少磁盘分页，Prefetch 通过历史加载行为改善程序启动；是否关闭这些功能取决于内存容量、CPU、存储设备和多任务场景，不能把关闭功能当作通用优化。

## 主题分层

- **机制专题**：内存压缩、MMAgent、Prefetch 和页面文件；
- **执行参考**：`tweakbyjie` 的实际目标、验证和恢复限制见[全量逐项执行参考](../项目导航/tweakbyjie全量执行参考.md)；
- **独立硬件专题**：DDR5/AM5 内存超频不属于本文范围。
