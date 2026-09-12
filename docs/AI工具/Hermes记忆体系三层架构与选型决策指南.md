---
status: reference
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
risk: low
verified_on: 2026-09-10
tweak_module: []
---

# Hermes 记忆体系三层架构与选型决策指南

> 本文目标：系统梳理 Hermes Agent 记忆体系的三层架构（原生层 / 官方可插拔层 / 社区插件层），纠正社区流传最广的两个误传（"80% 自动合并"与"Curator 管记忆"），并给出 8 个官方记忆 Provider 的架构差异对照与过重记忆层的五条报警信号。内容蒸馏自 Hermes Atlas 站长 @KSimback 的记忆体系指南（2026-05），结合本站双记忆库实践交叉验证。

---

## 一、为什么记忆是 Agent 的分水岭

没有记忆的 Agent 只是无状态函数——每个 prompt 都像第一次对话：上周二建立的编码约定这周二重新发明，个人助手反复追问同样的问题。记忆让对话机器人变成**可复利**的系统，这也是 Mem0（融资 $24M）、Letta（$10M）、Zep、Hindsight 等记忆基础设施成为独立品类的原因。

Hermes 的独特之处在于：Nous Research 把记忆当作**一等插件基础设施**而非功能点——基础层常驻运行，之上是可插拔 Provider 体系（8 种架构可选），再上是社区插件层。

## 二、三层架构总览

| 层 | 构成 | 角色 | 可替换性 |
|:--|:--|:--|:--|
| **Layer 1 原生层** | 2 个 Markdown 文件 + SQLite 会话库 | 开箱即用的"便签 + 档案馆" | 不可移除，永远在底层运行 |
| **Layer 2 官方 Provider** | 8 个官方记忆插件（单选） | 语义召回 / 用户建模 / 大规模检索 | 一次只跑一个，切换是干净启动 |
| **Layer 3 社区插件** | Mnemosyne、GBrain 等 | 填补官方 8 家没有的能力 | 叠加在两层之上，不冲突 |

关键理解：**三层是叠加而非替换**。换 Layer 2 Provider 不会清掉 Layer 1；社区插件在两层之上叠加。

## 三、Layer 1 原生层：便签与档案馆

### 1. 两个 Markdown 文件 = 永远在眼前的便签

Hermes 安装即在 `~/.hermes/` 创建：

- **MEMORY.md** — Agent 的通用知识便签（项目上下文、技术决策、跨会话事实），上限约 **2,200 字符**
- **USER.md** — 关于用户本人的便签（偏好、工作风格、角色），上限约 **1,375 字符**

设计意图是**小而常驻**：每次会话开始，两个文件的**全部内容**被注入 prompt，Agent 无需检索即可"看见"。它们不是档案柜，是便签。写入由 Agent 自主调用 `memory` 工具（add / replace / remove 三种动作；没有 read——因为内容已全量在上下文里）。

### 2. 误传一：不存在"80% 自动合并"

社区文章普遍声称"记忆达上限 80% 时 Hermes 自动合并条目"。Atlas 站长进入 `agent/memory_manager.py` 源码核实，真相是：

- **80% 规则只是一条 prompt 指令，不是代码逻辑**。系统提示头部显示实时填充仪表（如 `MEMORY: 1,847/2,200 chars (84 percent)`）并附指令"超过 80% 时先合并再新增"；
- **执行与否取决于模型自觉**：Agent 读了指令后自行决定是否照做；
- 真正的硬约束在代码里：文件已达上限时，任何 add 调用都会**报错并列出当前条目**，强制 Agent 先 replace/remove 腾空间。

利弊同源：Nous 信任模型自己管便签（完全自主），但调教不佳的 Agent 可能无限期停在满格状态，本该替换旧条目的信息被静默丢弃。

> 本站实践印证：双记忆库架构一文记录的"顶格减法 SOP"（先迁后删、抽验召回再删）正是对这一设计的工程化补丁——不能依赖自动合并，必须手动做减法。

### 3. 误传二：Curator 不碰记忆文件

v0.12 引入的 "Autonomous Curator" 常被描述为"自动记忆管理"——**不是**。Curator 只治理技能库 `~/.hermes/skills/`（按使用度在 active → stale → archived 间移动技能），**从不触碰 MEMORY.md / USER.md**。

### 4. SQLite 会话库 = 按需检索的档案馆

`~/.hermes/state.db`（SQLite；旧版本文献中曾名 hermes_state.db）存每一轮会话：用户消息、Agent 回复、工具调用、推理步骤，外加每会话 token 数与美元成本。默认保留 **90 天**，超期每 24 小时自动清理。

关键设计：**不自动注入 prompt**（否则等于每次对话贴上全部聊天记录），Agent 需要时按需检索。检索基于 SQLite FTS5 全文索引，双索引并行：

- 普通词级索引（"我们讨论过内容策略吗？"）
- trigram 子串索引（处理子串与代码 token，"找出提到 github 的所有会话"）

心智模型一句话：**两个 Markdown 文件 = Agent 脑子里永远记着的事；会话库 = Agent 知道去哪查的事**。跨所有未来会话都有用的事实 → 写 MEMORY.md（常驻）；可能再用但无需常驻 → 留在会话库（按需查）。

附带价值：因为捕获了完整推理步骤与工具调用加经济数据，这个库就是一份完整的**训练轨迹**，想微调时可整体导出。

## 四、Layer 2：8 个官方 Provider 对照

入口命令：`hermes memory setup`，菜单选择。铁律：**一次只能跑一个 Provider**（每个 Provider 暴露自己的 Agent 工具，三个竞争性"搜记忆"工具并存会干扰模型决策）；无论是否启用 Provider，Layer 1 原生层永远在底层运行。

| Provider | 架构押注 | 适用场景 |
|:--|:--|:--|
| **Honcho**（Plastic Labs） | 多步推理建模"你怎么思考"，构建会演化的推理模式画像 | Discord 社区最常被引用的最爱；多身份 Agent 共享同一用户画像 |
| **Mem0** | 云端 30 秒接入，自动抽取事实+去重+语义搜索 | "别问了直接给我记忆"型用户；生态最广（AWS Strands SDK 独家记忆 Provider）；v3 算法 LongMemEval 94.8 |
| **Hindsight**（Vectorize.io） | 四网络（世界/事件/观点/原始观察）+ 四路并行检索融合（关键词/向量/图遍历/时近） | 基准王：首个公开跨 LongMemEval 90 分（91.4）；唯一带 reflect 工具（Agent 对自身记忆做推理） |
| **Holographic** | 1991 年的 Holographic Reduced Representations 全息约化表示，本地 SQLite | **唯一零依赖**：无网络、无 API key、无 LLM，检索亚毫秒级；气隙环境首选 |
| **OpenViking** | 分层文件系统上下文库：每条知识三级加载（一句话摘要→段落大纲→全文） | 成本敏感场景：先读便宜的摘要，相关才加载深层；记忆像普通文件一样可 cat/grep/手改 |
| **RetainDB** | 纯云 SaaS，$20/月 10 万次查询 | 最低摩擦；"Memory Router"模式一行配置透明拦截 LLM 调用加记忆；团队共享记忆免运维 |
| **ByteRover** | 记忆即 git 仓库（.brv/context-tree/ Markdown 文件），5 级检索其中 4 级零 LLM 调用 | 可 branch/merge/回滚记忆；上下文压缩前钩子抽取高价值洞见，正面修"重启失忆"缺陷 |
| **Supermemory** | 自研向量图引擎，<300ms 延迟扛 1000 亿 token/月 | 规模与延迟领导者；context fencing 防记忆反馈回路；消费级使用属杀鸡用牛刀 |

> 本站对照：实际生产使用 OpenViking 作低频检索层（其三级加载与"文件可手改"特性与双记忆库 SOP 完全咬合），与上表描述一致。

## 五、Layer 3：社区插件双雄与选型纪律

社区插件分两种形态——与官方 8 家正面竞争的 MemoryProvider 插件，和占据不同生态位的伴生插件。代价是更少的打磨与文档，换来官方没有的能力。

**GBrain**（garrytan，MIT，~18k★）— 作者本人自用：不做 MemoryProvider 子类，以 skillpack + MCP 服务器形态插入，本体论位置不同。8 层知识引擎：认识论层（记录"谁在何时以何种置信度说了什么"）、自接线知识图（自动抽取实体关系，零额外 LLM 调用）、Dream Cycles 过夜自主合成、混合检索（向量+关键词+RRF 融合+多查询扩展+余弦重排）。适合：想要图谱但不想付图数据库成本、git 作记录系统、已有 Markdown 保险库（Obsidian/Logseq/Notion/Roam 迁移覆盖）。

**Mnemosyne**（AxDSan）— 最强社区 MemoryProvider 替代：全本地（无云/key/网络），检索 <2ms。分级记忆架构（working / episodic / scratchpad 三层+后台固化通道），独门能力是**记忆带时间感**——可问"上周二我对 X 的认知是什么"并得到当时点的理解。社区里唯一被写了专属 Hermes 技能包装的插件。

其他值得知道：Ladybug Memory（本地+1~10 重要度评分）、yantrikdb（可解释检索排序，"为什么召回这条"）、hermes-agentmemory（真删除+操作审计，解决"让它忘但暗中留摘要"）、PLUR（跨 Agent 共享 .plur/ 目录，Hermes/Cursor/Claude Code 互通）、FlowState-QMD（预测性预热）。

**选型纪律**：真跑生产，从官方 8 家起步，只在确认了具体能力缺口后再上 Layer 3。

**一个反直觉发现**：memory-as-skill（把记忆做成技能）在实践中**不成立**——所有可信的持久记忆都走 MemoryProvider 接口，声称"做记忆"的技能（如 Mnemosyne 的 SKILL.md）只是教 Agent 如何使用插件的包装。

## 六、过重记忆层的五条报警信号

1. **响应明显变慢**——原来 1 秒现在 3 秒+，记忆层在每一轮都加活
2. **账单爬升但用量没变**——部分 Provider 每次保存都触发后台 LLM 调用
3. **Agent 开始自相矛盾**——同一事实两个会话两个说法：只累积不固化，水井已污染
4. **会话中途上下文爆掉**——贪婪的记忆层挤占了正经对话的上下文预算
5. **工作质量实际没变好**——最关键的一条：加了两周，说不出 Agent 具体哪里更好，就拆掉它

## 七、参考与原始链接

- 原文：[The Hermes Agent Memory Guidebook](https://x.com/KSimback/status/2058262328496554021)（@KSimback，2026-05-23，收录于 ksimback/hermes-ecosystem `research/45`）
- [Hermes Atlas 记忆专题](https://hermesatlas.com)（作者维护的生态地图，含 Memory 分类）
- 本站关联文章：[Hermes 双记忆库并行架构与迁移 SOP](./Hermes双记忆库并行架构与迁移SOP.md) — 本站对 80% 误传的工程化补丁
- 本站关联文章：[Hermes 本地模型工作台与 OpenViking 智能记忆实战](./Hermes本地模型工作台与OpenViking智能记忆实战.md)

---

## 八、事实核查记录

- ✅ MEMORY.md 上限约 2,200 字符、USER.md 约 1,375 字符，每会话全量注入 prompt（原文 + 本站 MEMORY.md 实测 3,000 字符上限，v0.12 起有调整，量级一致）
- ✅ 80% 合并为 prompt 指令非代码逻辑；满格时 memory 工具 add 报错强制腾挪（原文引 agent/memory_manager.py 源码考证）
- ✅ Curator 只治理技能库，不触碰记忆文件（原文；本站配置守卫亦实证 curator 仅产 skills/.curator_ledger.jsonl）
- ✅ 会话库 SQLite FTS5 双索引（词级+trigram）、90 天默认保留（原文）
- ✅ Layer 2 Provider 单选互斥、Layer 1 常驻底层（原文，与本站 provider=openviking 叠加语义一致）
- ✅ 8 家 Provider 架构特征逐条对照原文（Hindsight 91.4 LongMemEval / Mem0 v3 94.8 / Holographic 零依赖等）
- ⚠️ Mem0 融资 $24M、Letta $10M、GBrain ~18k★ 为原文转述的社区数字，未独立核实
- ⚠️ ByteRover 修复的 issue #17251 编号未复核上游仓库
