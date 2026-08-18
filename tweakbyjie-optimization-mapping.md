# tweakbyjie 优化项目映射

## 目的

建立知识说明与实际优化之间的对应关系。

结构：

知识原理 → 优化项目 → 执行位置 → 验证方式 → 恢复方式

## CPU

- 原理：CPU调度、线程管理
- 对应项目：PriorityControl、Multimedia SystemProfile
- 验证：检查当前系统配置

## GPU

- 原理：图形管线、WDDM、GPU调度
- 对应项目：HAGS、MPO相关配置
- 验证：检查Graphics相关配置

## 内存

- 原理：Windows内存管理
- 对应项目：Memory Compression、Prefetch相关配置
- 验证：检查系统当前状态

## 存储

- 原理：SSD/NVMe、TRIM、文件系统
- 对应项目：存储相关优化
- 验证：检查存储状态

## 原则

所有优化项目必须具备：

1. 修改原因
2. 适用环境
3. 风险说明
4. 恢复方式
