# CPU 优化与 tweakbyjie 对应说明

## 对应范围

本章节用于覆盖 tweakbyjie 中 CPU 类优化项目。

## CPU-001 Win32PrioritySeparation

### Windows 原理
Windows 使用线程调度器管理 CPU 时间分配。Win32PrioritySeparation 影响前台程序与后台程序的调度策略。

### 修改目的
针对交互响应和前台应用体验进行调整。

### 适用环境
游戏、实时交互应用等需要关注响应性的场景。

### 潜在影响
不同硬件和系统版本表现可能不同，不应脱离测试结果判断。

### 恢复方式
恢复修改前注册表值。

## CPU-002 Multimedia SystemProfile

### Windows 原理
SystemProfile 中的多媒体调度参数参与 Windows 对实时任务和后台任务的资源分配。

### 修改目的
优化多媒体和游戏场景下的调度行为。

### 潜在影响
可能影响后台任务资源分配。

## CPU-003 SystemResponsiveness

### Windows 原理
该参数用于控制系统对后台任务资源分配的策略。

### 注意
实际效果依赖系统版本、应用类型和硬件环境。

## CPU-004 NetworkThrottlingIndex

### Windows 原理
该参数涉及 Windows 多媒体调度环境中的网络节流行为。

### 注意
网络优化需要结合实际延迟测试验证。

## CPU-005 Tasks\\Games

### Windows 原理
Games 任务类别用于定义游戏相关任务的调度属性。

### 修改目的
为游戏场景提供专用调度配置。

---

状态：CPU 类覆盖文档建立。
