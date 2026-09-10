---
status: reference
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
risk: low
verified_on: 2026-09-10
tweak_module: []
---

# Hermes 多 Profile 编队实战：从单助手到隔离的多 Agent 团队

> 本文目标：讲透 Hermes Profiles 多 Agent 编队的正确心智模型——用状态隔离而非提示词雕花构建团队、四角色参考架构（指挥塔/研究员/写手/工程师）、SOUL.md 与 AGENTS.md 的职责分界、七步落地流程。全文蒸馏自 Hermes Atlas 收录的编队实战文章（2026-04），并结合本站子代理委派实践对照。

---

## 一、核心心智模型：编队始于隔离，不是更好的提示词

多数人用一个 AI 助手强行兼任研究员、写手、码农、项目经理、操盘手。起初能用，随后人设糊成一团、上下文脏乱、记忆噪音化。Hermes 的解法是 **Profiles（配置档）**——它们不是装饰性人格皮肤，而是**隔离的 Agent 环境**。

一个 Profile 可以隔离：**configuration、sessions、memory、skills、personality、cron state、gateway state** 七类状态。多 Agent 系统失败的头号原因就是万事共享同一份记忆与语气；角色分工只有在新状态彼此隔离时才能持久沉淀。

一句话：**从一个 Agent 到真正多 Agent 团队的跨越，始于隔离，而非更好的提示词。**

## 二、四角色参考架构

作者给出的四人队形（名字可自定，结构是通用的）：

| 角色 | 定位 | 优化目标 | 职责 |
|:--|:--|:--|:--|
| **指挥塔**（orchestrator） | 命令中心，做交通调度而非瓶颈 | 规划、优先级、依赖管理、质控、综合 | 定义目标、拆分工作、路由给对的专家、汇总最终产出 |
| **研究员** | 怀疑式、证据优先、结构化 | 溯源、验证、标注不确定性 | 文献综述、市场调研、来源核实；**保护全队不被坏假设污染** |
| **写手** | 清晰、结构化、受众意识 | 表达质量 | 把验证过的素材变成文章/简报/文案/脚本；不需要持有研究过程全上下文 |
| **工程师** | 直接、证据驱动、实现导向 | 可复现性、日志、diff、已验证结果 | 建功能、debug、审码、跑测试 |

两个关键洞察：

- **研究员的价值是降低全系统的幻觉置信度**，不只是"会搜"；
- **写手的产出变好，恰因为它不同时兼任研究员和 debug**——输入更干净，专注沟通质量。

## 三、SOUL.md 与 AGENTS.md 的职责分界

多 Agent 设置最常见的错误：只改名字。若每个 Profile 底层的声音、优先级、运作风格全同，你拥有的不是团队，是**贴了标签的克隆**。

| 文件 | 管什么 | 放什么 |
|:--|:--|:--|
| **SOUL.md**（每 Profile 一份） | 持久身份：语气、默认行为、强项、优先级、忌讳 | 指挥塔要结构化果断；研究员要证据优先带怀疑；写手要清晰带受众意识；工程师要精确测试导向 |
| **AGENTS.md**（项目级共享） | 共享项目上下文，而非身份 | 仓库结构、编码约定、工作流规则、工具使用预期 |

分界铁律：**SOUL.md 定义 Agent 是谁；AGENTS.md 定义它们的共同任务语境**。别把临时项目细节塞进 SOUL.md。

## 四、七步落地流程

前提：主 Hermes 环境已可用（模型/Provider、密钥、日常环境都工作正常）——**从能跑的基线克隆，永远好过从零配置**。

**Step 1** 从工作基线出发（主 Profile 即指挥塔）。

**Step 2** 克隆创建专家 Profile：

```bash
hermes profile create alan --clone
hermes profile create mira --clone
hermes profile create turing --clone
```

`--clone` 复制 config.yaml、.env、SOUL.md 等基础设置，但**新 Profile 仍获得隔离的 memory 与 session 历史**。

**Step 3** 验证 Profile 确实存在：`hermes profile list`；磁盘上应在 `~/.hermes/profiles/<name>/` 各自成目录。CLI 和磁盘都要确认。

**Step 4** 给每个 Profile 写真正的 SOUL.md（`~/.hermes/profiles/<name>/SOUL.md`），按上表定义持久身份。**只改 Profile 名不改 SOUL.md = 没有团队**。

**Step 5** 共享上下文放项目级 AGENTS.md，与身份分离——身份住 SOUL.md，项目语境住 AGENTS.md，稳定团队需要稳定身份+共享语境，而非一坨混合指令。

**Step 6** 维护一份团队花名册文件（如 `~/.hermes/team-agents.md`）：每个 Agent 的角色、交接规则、何时用哪个 Profile、各自的好产出长什么样。一个地方讲清整套系统。

**Step 7** 真正分而用之：`hermes -p alan` / `hermes -p mira` / `hermes -p turing`。收益来自**实际分开使用**——Alan 不会继承 Mira 的写作会话，Turing 不会继承 Alan 的研究记忆，各自长期专精。

**进阶**：把 Profiles 与 Hermes gateway 消息平台组合——不同 Profile 以不同消息身份运行、远程监督、经 Telegram 路由工作，角色边界跨聊天与任务保持完整。Profile 从本地组织特性升级为实时多 Agent 控制面。

## 五、扩展路径与边界

扩展节奏：指挥塔起步 → 加一个专家 → **验证交接顺畅** → 再扩。团队的价值在角色边界的清晰度，不在数量——最聪明的多 Agent 团队不是最大的那个。

> 本站对照：单机本地环境的并发实测上限约 2（本地网关限流 + 资源争抢），重编队场景（swarm 式集群）不适合本机；更常用的形态是**单会话内 delegate_task 派发子代理**（子代理任务委派规范），与本篇的 Profile 级编队互补——前者任务级隔离、后者身份级隔离。Profile 状态隔离的目录事实与本站会话存储路径考证一致。

## 六、参考与原始链接

- 原文：[How to Build a Multi-Agent Team in Hermes](https://x.com/neoaiforecast/status/2043455838459920718)（@neoaiforecast，2026-04-12，收录于 ksimback/hermes-ecosystem `research/28`；`research/40` 为同文副本）
- [Hermes Atlas](https://hermesatlas.com)
- 本站关联文章：[Hermes 子代理模型路由机制](./Hermes子代理模型路由机制.md) — delegate_task 与 Profile 编队的互补关系
- 本站关联文章：[Hermes×ZCode 双 Agent 跨端协同机制实战](./Hermes-ZCode双Agent跨端协同机制实战.md) — 跨端而非同机编队的另一条路径

---

## 七、事实核查记录

- ✅ Profiles 隔离七类状态（config/sessions/memory/skills/personality/cron/gateway）：原文；Profile 目录结构 `~/.hermes/profiles/<name>/` 与本站配置文件所述 profile 机制一致
- ✅ `hermes profile create <name> --clone` / `hermes profile list` / `hermes -p <name>` 命令族：原文转述，与本站"config.yaml needs no restart (re-read at spawn)"的 profile 重读机制相容
- ✅ SOUL.md 定身份 / AGENTS.md 定项目语境的分界：原文；本站 Hermes 环境实存 SOUL.md 且承担身份职责，方向一致
- ✅ 本机并发上限 ≈2 的判断：本站 09-05 资源评估实证（本地网关限流），本篇据此给出"重编队慎用"的本地化修正
- ⚠️ Alan/Mira/Turing 为作者个人队形的命名示例，非官方推荐名
- ⚠️ "gateway + Telegram 路由"进阶玩法未在本机复验（本机 Telegram 走频道运营而非 bot 网关）
