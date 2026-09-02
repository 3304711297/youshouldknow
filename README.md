# YouShouldKnow 💡

<p align="center">
  <strong>现代化 Windows 系统、硬件底层、游戏性能调优与日常实用知识库</strong>
</p>

<p align="center">
  <a href="https://3304711297.github.io/youshouldknow/"><img src="https://img.shields.io/badge/Docs-Online%20Read-blue?style=flat-square&logo=gitbook" alt="Docs"></a>
  <a href="https://github.com/3304711297/youshouldknow/actions/workflows/docs.yml"><img src="https://img.shields.io/github/actions/workflow/status/3304711297/youshouldknow/docs.yml?branch=main&label=CI%20Build&style=flat-square" alt="CI Status"></a>
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6?style=flat-square&logo=windows" alt="Platform">
  <img src="https://img.shields.io/badge/Theme-MkDocs%20Material-526CFE?style=flat-square&logo=materialformkdocs" alt="MkDocs">
  <img src="https://img.shields.io/badge/License-CC--BY--4.0-green?style=flat-square" alt="License">
</p>

---

## 📖 项目简介

**YouShouldKnow** 是一个深度聚焦于 **Windows 系统底层调优、硬件特性解析、游戏延迟优化与 AI 工具链** 的实用知识库。

- 🌐 **在线阅读站点**：[https://3304711297.github.io/youshouldknow/](https://3304711297.github.io/youshouldknow/)
- 🎯 **双向工程联动**：与优化脚本工具集 [tweakbyjie](https://github.com/3304711297/tweakbyjie) 保持严格同步。知识库负责**原理解析与风险辨析**，执行层负责**安全自动化实施**，并通过跨仓库 Coverage 审计矩阵保持 100% 严密对齐。

---

## 📚 知识体系全景 (14 大核心分类)

全部文章位于 [`docs/`](./docs/) 目录下，按以下分类系统化归档：

| 分类 | 核心内容与精选主题 |
| :--- | :--- |
| **🔍 验机相关** | 笔记本与整机验机流程、Windows 审核模式 (OOBE) 进阶验机技巧 |
| **⚡ CPU 与延迟** | Intel / AMD 核心调度原理、异构线程分配、中断亲和性与 DPC 延迟解析 |
| **🎮 GPU 与显示** | Windows 图形管线、MPO 机制、帧生成与 Reflex/Anti-Lag 低延迟深度辨析 |
| **🛠️ 显卡优化** | NVCleanstall 驱动精简、NVIDIA 控制面板/App 设置、ReBAR 强制开启、DP/HDMI 速率表 |
| **💾 内存与存储** | Windows 内存压缩机制、MMAgent 策略、NVMe 固态硬盘底层特性与读写优化 |
| **🔥 内存超频** | DDR5 超频速查表、Intel 12/13/14 代海力士 M-die / 英睿达颗粒实机超频参数调校 |
| **🔌 BIOS 与固件** | BIOS 选项科普系列（XMP/EXPO、Secure Boot、TPM、PBO、功耗墙等 20 篇，含出处）、UEFI 开机 Logo 修改、固件刷写、移动端笔记本 BIOS 选项与超频降压安全边界 |
| **💻 笔电相关** | 机械革命/同方模具控制中心与 Uniwill 驱动冲突排查、电池充电管理与跳电机制 |
| **🛡️ 系统调优与安全** | Windows 调优核心原则、系统服务精简原则、VBS 与安全缓解、设备管理器禁用类优化辨析 |
| **🧩 系统知识** | Defender 恢复边界、Windows 启动配置 BCD 深度解析、电源计划创建与定制指南 |
| **🌐 网络通信** | Windows 网络栈调优、Karing TUN 转发配置、四大运营商频段与 APN 设置速查 |
| **📦 软件技巧** | Steam 客户端性能设置与下载优化、日常高效软件配置手册 |
| **🤖 AI 工具** | CDP 远程调试接管日常 Edge 浏览器、ZCode 接入 Gemini 生图 Skill 与 Antigravity 桥接指南 |
| **🗺️ 项目导航** | tweakbyjie 关联说明、优化项目映射、全量执行参考与自动生成覆盖矩阵 |

---

## 🔄 知识库与执行脚本联动架构

```text
┌────────────────────────────────────────────────────────┐
│                   YouShouldKnow (知识库)               │
│  - 深度原理解析 (Why)        - 安全风险评级 (Risk)      │
│  - 社区方案辨析 (Trade-off)  - 硬件平台差异 (Platform)  │
└───────────────────────────┬────────────────────────────┘
                            │ 严格双向映射 (Coverage 44项全覆盖)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   tweakbyjie (PowerShell)              │
│  - 模块化安全执行 (How)      - 还原快照体系 (Backup)     │
│  - 条件预检灰掉 (Preflight)  - 退出码与无人值守支持     │
└────────────────────────────────────────────────────────┘
```

---

## 🛠️ 本地预览与开发

本项目基于 MkDocs Material 构建，内置严格的 Front Matter 元数据校验与死链检查机制：

```bash
# 1. 安装文档依赖
pip install -r requirements-docs.txt

# 2. 执行 Front Matter 元数据与覆盖矩阵检查
python tools/check_front_matter.py
python scripts/gen-matrix.py

# 3. 严格模式构建与死链排查
mkdocs build --strict
lychee --config lychee.toml "docs/**/*.md"

# 4. 本地实时预览热加载
mkdocs serve
```

---

## 🤝 贡献与规范

欢迎提交 Issue 补充实用知识或提交 Pull Request！
- 新增 Markdown 文章需包含规范的 YAML Front Matter（`applies_to`, `risk`, `tweak_module`）。
- 遵循中英文混排排版规范（中英之间保留空格）。
- 提交前请运行 `python tools/check_front_matter.py` 确保自检通过。

---

## 📄 开源许可

本项目文档采用 [CC-BY-4.0 (知识共享署名 4.0 国际许可协议)](https://creativecommons.org/licenses/by/4.0/) 开源。
