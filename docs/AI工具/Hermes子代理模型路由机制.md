---
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
risk: low
tweak_module: []
status: reference
---

# Hermes 子代理模型路由机制

> 本文目标：厘清 hermes-agent 中主会话与子代理（subagent）之间的模型路由规则。前半部分基于官方文档 `delegation.md` 与 `configuration.md` 梳理机制的静态规则，中间用一次额度审计实证"继承"行为的真实性，后半部分沉淀实践范式、config.yaml 操作规范与 glm-5.3-flash 思考型模型的避坑要点，末尾附逐条事实核查记录。

---

## 一、机制原理：官方文档依据

依据 hermes-agent 官方仓库文档 `website/docs/user-guide/features/delegation.md` 与 `website/docs/user-guide/features/configuration.md`，子代理的模型路由遵循以下五条规则：

### 1. 默认行为：完整继承父会话

* 子代理默认继承父会话的 provider 与 model——主会话用什么模型，`delegate_task` 派发的子代理就用什么模型，无需任何显式配置。

### 2. 全局路由：config.yaml 顶层 delegation 字段

* 在 `config.yaml` 顶层设置 `delegation.provider` + `delegation.model`，即可将子代理统一路由到另一个 `provider:model` 组合，实现与主会话模型的解耦。

### 3. 解析优先级

* 子代理模型按以下顺序解析，取最先命中者：
  1. `delegation.base_url`（显式指定端点，优先级最高）
  2. `delegation.provider`
  3. 继承父级（默认回退行为）

### 4. 粒度限制：delegate_task 无单任务模型参数

* `delegate_task` 本身不提供单任务维度的模型参数——同一会话内派发的所有子代理共用统一配置，无法在派发时逐个指定不同模型。
* 若确需按任务分配不同模型，官方路径是 Kanban 看板的 per-task model override（按任务覆盖模型），适用于质量敏感任务。

### 5. 官方设计哲学："frontier planner, inexpensive workers"

* 主会话由旗舰（贵）模型负责规划决策，子代理由廉价模型承担执行劳动——在保证规划质量的同时压缩 token 成本，delegation 配置正是该哲学的落地开关。

---

## 二、实证案例：一次额度审计实锤"继承"行为

机制文档是一回事，账单是另一回事。以下实证链条可直接复核：

1. **现象**：主会话聊天模型切换为 WorkBuddy 的 glm-5.3-flash 后，照常通过 `delegate_task` 派发子代理干活；用户随后发现 Gemini 额度纹丝未动。
2. **取证**：查询 ZCode 的 SQLite `model_usage` 表，GLM-5.3-Flash 在最近 30 分钟内共 10 次调用、消耗 2,393,521 tokens。
3. **补刀**：其中一次被中途撤回的子代理，在 74.55 秒的生命周期内打出了 11 次 API 调用。
4. **结论**：主会话未显式配置 delegation，子代理的全部调用都落在了聊天模型同一端点上——"子代理继承聊天模型"实锤，与官方文档描述一致。

> 反向推论同样成立：Gemini 额度未掉 ≠ 子代理没干活，只说明子代理没走 Gemini。判断子代理实际使用的模型，查用量数据远比凭印象猜测可靠。

---

## 三、实践范式：不固定模型（用户拍板）

* **不固定模型**：聊天模型与子代理模型的组合保持随机变化，不在 config.yaml 中长期固定 delegation 路由。
* **口头约定优先**：用户通常会主动告知子代理模型；未告知时，子代理与聊天模型同模型（即默认继承行为）。
* **一次反例**：曾固定 `delegation.provider=custom:cpa-gui` + `model=gemini-3.8-flash`，随后被要求撤回，commit 7106e46 将 delegation 恢复为仅保留 `max_iterations: 250`。
* **理由**：固定 delegation 是每会话全局生效的配置，与"随机组合"需求天然冲突；模型选择权应留在口头指令层面，而非写死在配置文件里。

---

## 四、配置操作规范

如确需修改 delegation 配置，遵守两条硬规范：

### 1. 必须用 Python yaml 库读写

* `patch` / `write_file` 工具会拒写 config.yaml，唯一可行方式是用 Python 的 yaml 库完成读写（`yaml.safe_load` 读入、修改目标字段后 `yaml.safe_dump` 写回）。

### 2. 改后必须抽查关键字段完整性

* 写回后抽查确认 `plugins`、`moa`、`custom_providers` 等关键字段无损——整文件重写最易误伤的就是这些配置块。

---

## 五、模型特性注意：glm-5.3-flash

| 特性 | 说明 |
| :--- | :--- |
| 思考型模型 | 先消耗 token 生成思考链，再输出正文 |
| 陷阱 | `max_tokens<100` 时思考链即可耗尽配额，正文返回 `content=null`，表现为假阳性失败 |
| 误判案例 | 该现象曾被误判为"并发限制≈2"，实为 max_tokens 过小的假阳性 |
| 正确姿势 | 测试/调用给足 `max_tokens≥300`，或改为读取 `reasoning` 字段判断 |
| 并发实测 | 端点实测 15 并发零 429（10 并发 6.61s、15 并发 4.07s，全绿） |

---

## 六、边界与适用性

* 本文路由机制适用于 `delegate_task` 派发的子代理；Kanban per-task model override 是粒度更细的另一条独立路径，面向质量敏感任务。
* "未告知 = 同模型"仅在未显式配置 delegation 时成立；一旦 config.yaml 顶层写入 delegation.provider/model，继承行为即被覆盖。
* 继承是双刃剑：聊天模型切换后子代理模型随之漂移，做额度审计或性能归因前必须先确认当前主会话模型。
* max_tokens 陷阱是一切思考型模型短回复调用的通病，不限 glm-5.3-flash。

---

## 七、事实核查记录

- ✅ 子代理默认继承父会话 provider+model（delegation.md / configuration.md）
- ✅ config.yaml 顶层 delegation.provider + delegation.model 可路由到不同 provider:model
- ✅ 解析优先级：delegation.base_url > delegation.provider > 继承父级
- ✅ delegate_task 无单任务模型参数，同一会话所有子代理统一配置
- ✅ 质量敏感任务走 Kanban 看板 per-task model override
- ✅ 官方设计哲学 'frontier planner, inexpensive workers'
- ✅ 实证：切 WorkBuddy glm-5.3-flash 后派发子代理，Gemini 额度未掉
- ✅ ZCode SQLite model_usage 表：GLM-5.3-Flash 最近 30 分钟 10 次调用 2,393,521 tokens
- ✅ 被撤回子代理 74.55s 内 11 次 API 调用
- ✅ 范式：不固定模型；未告知 = 子代理与聊天模型同模型
- ✅ 曾固定 delegation.provider=custom:cpa-gui + model=gemini-3.8-flash，commit 7106e46 恢复为仅 max_iterations: 250
- ✅ config.yaml 必须用 python yaml 库读写；改后抽查 plugins/moa/custom_providers 无损
- ✅ glm-5.3-flash 思考链耗尽 max_tokens<100 → content=null 假阳性（曾误判并发限制≈2）
- ✅ 调用需 max_tokens≥300 或读 reasoning 字段
- ✅ 端点实测 15 并发零 429（10 并发 6.61s、15 并发 4.07s 全绿）
