---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# YouShouldKnow

Windows 系统、硬件、游戏性能与日常使用知识库。

这里的文章分为两类：一类帮助你理解 Windows 和硬件机制，另一类提供具体设置、测试和排障方法。涉及注册表、启动配置、安全功能或驱动的文章，请先阅读风险与恢复说明，不要只追求“优化数量”。

## 🚀 按用户目标开始

| 你想做什么 | 推荐入口 |
|---|---|
| 新机验机、装机或激活系统 | [验机相关](./验机相关/README.md) |
| 了解 BIOS/UEFI 固件、镜像编辑和刷写风险 | [BIOS 与固件](./BIOS与固件/README.md) |
| 了解 Windows 基础设置和常见故障 | [系统知识](./系统知识/README.md) |
| 降低游戏延迟、分析卡顿和帧时间 | [CPU 与延迟](./CPU与延迟/README.md)、[GPU 与显示](./GPU与显示/README.md)、[键鼠与 TCP 可选实验设置](./CPU与延迟/Windows键鼠与TCP低延迟可选实验设置.md)、[游戏性能验证流程](./项目导航/游戏性能验证流程.md) |
| 调整显卡、驱动、内存或笔记本硬件 | [显卡优化](./显卡优化/README.md)、[内存超频](./内存超频/README.md)、[内存与存储](./内存与存储/README.md)、[笔电相关](./笔电相关/README.md)；笔电控制中心驱动冲突可看[排障文章](./笔电相关/控制中心与Uniwill驱动冲突排查.md) |
| 了解系统优化、电源、服务、注册表和安全风险 | [系统调优与安全](./系统调优与安全/README.md) |
| 了解网络和低延迟通信 | [网络通信](./网络通信/README.md)、[TCP 可选实验设置](./CPU与延迟/Windows键鼠与TCP低延迟可选实验设置.md) |
| 使用 `tweakbyjie` 执行 Windows 优化 | [项目导航](./项目导航/README.md)、[tweakbyjie 优化项目映射](./项目导航/tweakbyjie-optimization-mapping.md) |
| 学习常用软件设置 | [软件技巧](./软件技巧/README.md) |
| 让 AI 助手接管浏览器、配置 MCP 工具链 | [AI 工具](./AI工具/README.md) |

## 📂 按主题浏览

| 分类 | 内容 | 入口 |
|---|---|---|
| [验机相关](./验机相关/README.md) | Windows 安装、激活、OOBE 和装机检查 | [目录](./验机相关/README.md) |
| [BIOS 与固件](./BIOS与固件/README.md) | BIOS/UEFI 镜像编辑、固件刷写和恢复风险 | [BIOS/UEFI 固件刷写与开机 Logo 修改指南](./BIOS与固件/BIOS与UEFI固件刷写及开机Logo修改指南.md)<br>[UEFI Editor 项目说明](./BIOS与固件/UEFI-Editor项目说明.md)<br>[机械革命笔记本 BIOS 选项与超频降压风险说明](./BIOS与固件/机械革命笔记本BIOS选项与超频降压风险说明.md)<br>[目录](./BIOS与固件/README.md) |
| [系统知识](./系统知识/README.md) | Windows 设置、命令、睡眠、虚拟内存、服务和故障排查 | [目录](./系统知识/README.md) |
| [CPU 与延迟](./CPU与延迟/README.md) | 调度、DPC/ISR、计时器、输入延迟和性能测试 | [主文与专题](./CPU与延迟/README.md) |
| [GPU 与显示](./GPU与显示/README.md) | 图形管线、帧时间、驱动模型和显示合成 | [主文与专题](./GPU与显示/README.md) |
| [内存与存储](./内存与存储/README.md) | Memory Compression、Prefetch、NVMe 和存储栈 | [主文与专题](./内存与存储/README.md) |
| [系统调优与安全](./系统调优与安全/README.md) | 电源、服务、注册表、优化等级和 VBS | [主文与专题](./系统调优与安全/README.md) |
| [显卡优化](./显卡优化/README.md) | NVIDIA/AMD 显卡实际设置和工具 | [目录](./显卡优化/README.md) |
| [内存超频](./内存超频/README.md) | DDR5 时序与稳定性测试 | [目录](./内存超频/README.md) |
| [笔电相关](./笔电相关/README.md) | 电池、电源、控制中心和笔记本硬件排障 | [控制中心与 Uniwill 驱动冲突排查](./笔电相关/控制中心与Uniwill驱动冲突排查.md)<br>[目录](./笔电相关/README.md) |
| [网络通信](./网络通信/README.md) | 运营商、APN、代理和网络转发 | [目录](./网络通信/README.md) |
| [软件技巧](./软件技巧/README.md) | 常用软件和客户端设置 | [目录](./软件技巧/README.md) |
| [AI 工具](./AI工具/README.md) | AI 编程助手、浏览器自动化与 MCP 工具链 | [目录](./AI工具/README.md) |
| [项目导航](./项目导航/README.md) | `tweakbyjie` 对应关系、测试流程和执行说明 | [目录](./项目导航/README.md) |

## 🧭 tweakbyjie 对应索引

`youshouldknow` 负责解释原理、适用范围、风险和恢复；[`tweakbyjie`](https://github.com/3304711297/tweakbyjie) 负责实际执行。建议先阅读知识说明，再决定是否运行脚本。

- [项目关联说明](./项目导航/tweakbyjie关联说明.md)
- [逐项优化映射](./项目导航/tweakbyjie-optimization-mapping.md)
- [全量逐项执行参考](./项目导航/tweakbyjie全量执行参考.md)
- [CPU 优化对应说明](./项目导航/CPU优化与tweakbyjie对应说明.md)
- [GPU 调度与显示管线](./项目导航/GPU调度与显示管线.md)
- [游戏性能验证流程](./项目导航/游戏性能验证流程.md)

脚本执行维度包括 CPU、GPU、Memory、Storage、Security、Service、Boot 和 Registry；映射表会明确哪些项目有备份/验证，哪些项目没有精确回滚能力。

## 📖 阅读建议

- 先看机制和风险，再看具体命令或注册表路径。
- 任何性能结论都应使用可重复的前后对照测试，不要只看主观感受。
- 修改系统前记录原值、创建还原点或完整备份，并确认恢复路径。
- 不要把知识文章中的示例设置理解为对所有设备都适用的默认方案。

## 🏷️ 文档元数据规范

部分文章在文件开头使用 YAML Front Matter，供站点显示统一的维护信息。当前规范只允许以下四个字段：

```yaml
---
status: reference
risk: low
applies_to:
  - Windows 10/11
verified_on: 2026-08-21
# 本次收尾未重新核验外部事实，verified_on 保留上次核验日期
---
```

- `status`：文章状态，只能使用 `stable`（稳定维护）、`reference`（参考资料）或 `experimental`（实验性内容）；
- `risk`：文章涉及的操作风险，只能使用 `low`（低风险）、`medium`（中风险）或 `high`（高风险）；
- `applies_to`：非空的适用范围列表，写明 Windows 版本、硬件/软件场景或测试环境；
- `verified_on`：最近一次内容或事实核查日期，格式为 `YYYY-MM-DD`。它表示核查时间，不替代站点显示的 Git 最后修改日期。

Front Matter 不重复维护文章标题和分类：标题以正文一级标题为准，分类以目录和 `mkdocs.yml` 导航为准。元数据必须依据正文、事实核查记录和可追溯证据人工填写，不根据关键词自动推断风险或稳定性。旧文章可以暂时没有 Front Matter，并按分类逐步迁移；加入后必须通过校验器。

本地检查命令：

```powershell
python tools/check_front_matter.py
```

涉及高风险系统操作的文章，只有在人工确认正文边界、恢复方式和核查依据后，才应填写对应风险等级。

## 📝 如何新增内容

1. 根据文章主题选择已有分类目录；
2. 将文章和它依赖的 `images/` 等资源放在同一分类目录；
3. 在本 README 的“按主题浏览”或相关任务入口登记链接；
4. 移动文章时同步更新所有相对链接，避免破坏历史入口；
5. 文章末尾附「事实核查记录」小节：逐条列出关键声明、核查结果（✅ 属实 / ❌ 勘误 / ⚠️ 依赖社区源待复核）与依据；涉及 `tweakbyjie` 执行项的声明必须对照当前源码核对，不照抄旧文档；
6. 涉及具体操作的正文建议遵循「定位 → 机制 → 验证 → 恢复 → 边界」结构。

## 📄 许可

本仓库内容采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 许可协议发布。
