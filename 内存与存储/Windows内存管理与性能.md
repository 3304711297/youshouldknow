# Windows 内存管理与性能

## Memory Compression

Windows 内存压缩用于降低分页压力，通过 CPU 压缩数据来减少磁盘交换需求。

## 是否关闭

没有统一答案。

适合测试关闭的情况：

- CPU 性能较弱
- 内存容量充足
- 追求低延迟场景

保持开启的情况：

- 内存容量较小
- 多任务使用
- 笔记本移动场景

## Prefetch / Superfetch

Prefetch 主要用于改善程序启动速度，通过记录加载行为提前准备数据。

关闭后可能减少后台活动，但不一定提升所有设备性能。

SSD/NVMe 环境下需要结合实际测试判断。

## 与 tweakbyjie 关系

相关项目：

- Memory Compression 管理
- EnablePrefetcher 配置
- 存储优化模块

优化目标不是关闭所有功能，而是根据硬件和使用场景调整。
