# GPU 调度与显示管线

## HAGS（Hardware Accelerated GPU Scheduling）

HAGS 是 Windows 提供的一种 GPU 调度方式，将部分调度工作交给 GPU 硬件处理。

影响因素：

- GPU 架构
- 驱动版本
- 游戏引擎
- 延迟需求

不同硬件环境可能表现不同，因此需要实际测试。

## MPO（Multiplane Overlay）

MPO 是 Windows 显示合成机制，用于减少显示合成开销。

优点：

- 降低部分合成负担
- 提升部分场景效率

可能的问题：

- 黑屏
- 闪烁
- 帧时间异常

因此 tweakbyjie 中相关选项应保持独立管理。

## 与 tweakbyjie 关系

显示相关优化属于高级配置，应根据 GPU、驱动和游戏情况选择。
