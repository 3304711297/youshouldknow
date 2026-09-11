---
status: reference
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
risk: low
verified_on: 2026-09-10
tweak_module: []
---

# Hermes 技能系统机制原理：渐进式披露与程序性记忆

> 本文目标：讲清 Hermes 技能（Skill）系统的底层设计——技能是"程序性记忆"而非提示词片段、三级渐进式披露如何按需加载、技能目录结构与优秀技能的内容标准。全文蒸馏自 Hermes Atlas 收录的机制解析文章（2026-04），并经本机工具池逐项实证。

---

## 一、技能是什么：程序性记忆，不是提示词片段

Hermes 中的技能是一份**按需加载的知识文档**，教 Agent 如何处理某一类任务——工作流、工具操作规程、排障模式、格式规范或操作手册。核心定位是**程序性记忆（procedural memory）**，与另外两类存储严格分工：

- **Memory** 存持久事实（用户偏好、环境约定、反复纠正）
- **Sessions** 存发生了什么（对话历史）
- **Skills** 存"怎么把某件事做好"（可复用方法）

这个区分很重要：它让 Hermes 在不把几百页说明书塞进每个会话的前提下，持续积累可复用的 know-how。

## 二、解决什么问题：两个坏选项之外的第三条路

没有技能系统的 Agent 只有两个坏选项：

1. **全部写进 prompt** — 成本飞涨，大量与当前任务无关的指令污染上下文；
2. **祈祷模型自己记得模式** — 遇到需要精确命令、已知坑位、环境特定步骤、固定输出风格的任务就掉链子。

Hermes 的解法是**按需加载**：平时只随身携带一份紧凑的技能索引（名称+描述+分类），任务真正需要时才加载完整技能正文。Agent 因此"默认轻量、按需专业"。

## 三、三级渐进式披露（Progressive Disclosure）

技能加载分三层，按需逐级深入：

| 层级 | 调用 | 加载内容 | 代价 |
|:--|:--|:--|:--|
| **Level 0** | `skills_list()` | 紧凑索引：技能名、描述、分类 | 极低，常驻 |
| **Level 1** | `skill_view(name)` | 完整 SKILL.md 正文 | 任务匹配时才付 |
| **Level 2** | `skill_view(name, file_path)` | 技能内部特定 reference/template/script | 深钻时才付 |

运维含义：Agent 不会把全部技能内容拖进每个会话，只在任务值得时才付出更深层级的上下文成本——技能是分层知识系统，不是常驻巨型 prompt。

> 本机实证：Hermes 工具池实存 `skills_list` 与 `skill_view(name, file_path)` 全套工具，行为与上表一致；本文开头读取格式规范时正是走 `skill_view` 路径，末尾引用模板走 `file_path` 参数——三级披露在真实会话里就是这么工作的。

## 四、技能存放：真实文件，不是隐藏魔法

技能真源目录：`~/.hermes/skills/`（Windows 本地化为 `%LOCALAPPDATA%\hermes\skills\`），存放四类来源：安装时内置、Hub 安装、Agent 自建、Agent 更新的技能。

典型结构：

```text
skills/<category>/<skill-name>/SKILL.md
                          ├── references/   # 深度参考文档
                          ├── templates/    # 模板
                          ├── scripts/      # 脚本
                          └── assets/       # 资产
```

Hermes 也能扫描外部技能目录，但**自己创建或修改技能时一律写回本地技能目录**——程序性知识的工作副本始终由 Hermes 自持。

## 五、什么才算好技能：可复用的操作模式

技能 = Markdown 正文 + YAML frontmatter + 结构化指令。一份强技能包含：**用途、何时使用、精确流程、命令示例、坑位、验证步骤**。

反例 vs 正例：

- ❌ "擅长 GitHub PR"——只是贴了个主题标签；
- ✅ "何时启用此流程 → 先检查什么 → 跑哪些命令 → 核对哪些失败模式 → 收尾前如何验证结果"——捕获了可复用的操作模式。

技能的价值门槛：**捕获到能精确复用的程度**，而非仅仅描述。

## 六、三种使用方式

1. **会话内斜杠命令**：`/plan 规划一个迁移方案`、`/github-pr-workflow 为重构建 PR`；
2. **CLI 管理**：`hermes skills list` / `search docker` / `install official/research/arxiv` / `inspect openai/skills/k8s`，官网 Skills Hub 可浏览全网技能目录；
3. **自然对话自动加载**：任务匹配时 Hermes 自行决定调取相关技能——这是最重要的一条：技能不只是手动快捷方式，更是 Agent 在真实工作中智能化运作的机制。

## 七、运维上的五大优势

1. **一致性**：已验证的工作流可复现，而非每次重新发明；
2. **更低 Token 浪费**：完整指令在需要前不占上下文；
3. **专业化**：携带大量能力而不拖重日常对话；
4. **可迭代**：工作流升级时更新技能文件即可，不赌模型记得新版本；
5. **复利**：方法一旦固化为技能，未来所有会话立即受益。

这是 Hermes 表现得像 **Agent 运行时**而非聊天壳的最清晰处之一。

## 八、三分法判定规则

| 要存的东西 | 去处 |
|:--|:--|
| 应该记住的事实 | memory（MEMORY.md / 记忆库） |
| 回顾过往对话 | sessions / session_search |
| 复用一套方法 | **skill** |

技能也回答了"Hermes 如何越用越强"这个问题：复杂任务、棘手 bug、非显然的工作流之后，Agent 通过技能管理流程把学到的方法固化成技能。很多系统谈"学习"实际是囤上下文，Hermes 的模型更干净——**事实进记忆、历史留会话、方法成技能**。

## 九、本机治理对照

- 本站实践与本机制完全咬合：技能池二八瘦身（30-50 项为宜）、痛点驱动准入、物理裁撤长尾——见 [AI Agent Skills 深度精简与全网立体看门雷达构建](./AIAgent-Skills深度精简与全网立体看门雷达构建.md)；
- 技能生命周期治理（发现/准入/维护/同步四环节）见 [Hermes-Agent 高阶指令全景与官方生态指南](./Hermes-Agent高阶指令全景与生态路线指南.md) 的生态治理章节；
- 自研技能沉淀流程（difficult task → skill）即本文"方法成技能"路径的工程化。

## 十、参考与原始链接

- 原文：[How Skills Work in Hermes Agent](https://x.com/neoaiforecast/status/2044252861710905685)（@neoaiforecast，2026-04-14，收录于 ksimback/hermes-ecosystem `research/39`）
- [Hermes Atlas](https://hermesatlas.com) · [官方技能目录](https://hermes-agent.nousresearch.com/docs/reference/skills-catalog)
- 本站关联文章：[AI Agent Skills 深度精简与全网立体看门雷达构建](./AIAgent-Skills深度精简与全网立体看门雷达构建.md)

---

## 十一、事实核查记录

- ✅ 三级渐进式披露 `skills_list()` / `skill_view(name)` / `skill_view(name, file_path)`：本机工具池实存全套，行为一致（本文写作过程即实证）
- ✅ 技能目录 `skills/<category>/<skill-name>/SKILL.md` 结构与 references/ 等四类子目录：本机 `%LOCALAPPDATA%\hermes\skills\` 实查一致（含 zcode-custom 等类别目录、多技能含 references/）
- ✅ Windows 路径本地化 `~/.hermes` → `%LOCALAPPDATA%\hermes`：本机实查
- ✅ 三分法（事实→memory/历史→sessions/方法→skills）：与本站共享记忆库治理实践一致
- ⚠️ `hermes skills install official/research/arxiv` 等 CLI 语法为原文转述，本机技能管理走 skill_manage/skill_view 流程，未复验 CLI 参数
- ⚠️ 斜杠调用示例（/plan、/github-pr-workflow、/excalidraw）为原文示例，未逐个验证
- ⚠️ "官网 Skills Hub 可浏览全网技能目录"与本站看门雷达记录（9 万+ 全网索引）一致，数量随时间变动
