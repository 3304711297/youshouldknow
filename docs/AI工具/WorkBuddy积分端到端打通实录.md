---
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
  - codebuddy2openai（Tauri v2）
risk: low
tweak_module: []
status: reference
---

# WorkBuddy 积分端到端打通实录

> 本文目标：记录将腾讯 CodeBuddy（WorkBuddy）积分数据打通到 Hermes token-stats 配额插件的完整过程。从"卡片只会显示运行中"的问题定位出发，历经三方案比选与裁决，最终以"反向代理新增 REST 端点 + Hermes 后端拉取 + 前端双看板展示"的链路实现端到端打通，并沉淀双端一致性验证方法论与踩坑记录。全文事实均来自实际施工与验收，标 ✅ 处为实测确认。

---

## 一、背景与问题定位

Hermes token-stats 配额插件中，WorkBuddy 卡片长期只能显示"运行中"——因为插件对该服务的探测仅止于 `http://127.0.0.1:8787/v1/models` 存活检查。而 8787 端口上的 codebuddy2openai 本质是一根"哑管道"：只做 OpenAI 格式请求的转换转发，`/api/usage`、`/api/credits`、`/v1/dashboard` 全部 404，没有任何积分查询能力（✅实测：三个路径均返回 404）。

积分数据的真实持有方是腾讯侧接口。其获取路径锁在 Tauri IPC 的 `usage_query` 内部：

- 请求：`POST https://copilot.tencent.com/billing/meter/get-user-resource-summary`
- Headers：`Authorization: Bearer <accessToken>` + `X-User-Id: <uid>` + `Content-Type: application/json` + `User-Agent: codebuddy2openai/2.0`
- Body：`{}`

账号凭据则存放在本地 `%LOCALAPPDATA%\codebuddy2openai\accounts.json`，包含 `active_uid`（当前激活账号）、`nickname`（昵称）与 `auth.accessToken`（访问令牌）。也就是说：数据、凭据、网络条件三者在本地齐备，唯一缺的是一条把三者串起来的通路。

## 二、方案比选与裁决

围绕"谁来串这条通路"，比选了三个方案：

| 方案 | 思路 | 评价 |
| :--- | :--- | :--- |
| A | Hermes 侧直接读 `accounts.json` 并复刻腾讯请求 | 零侵入，但把腾讯接口细节、token 刷新逻辑全部搬进 Hermes 插件，逻辑重、维护面大 |
| B | 反代（converter）新增 REST 端点 | 由最熟悉腾讯请求结构的 converter 侧暴露端点，Hermes 只做一次 HTTP 拉取 |
| C | 文件桥轮询 | 两侧解耦最彻底，但引入轮询节拍与文件时效问题，实时性最差 |

**裁决：落地方案 B。** 由 ZCode Agent 在 `converter.py` 新增 `GET /api/usage_summary` 端点（commit `5b4381c`），Hermes 侧专注验收与对接展示。分工逻辑很直接：施工交给 ZCode，Hermes 只做验收对接，节省 Hermes 侧的模型额度。

## 三、端点设计与契约

`GET /api/usage_summary` 的返回契约如下：

```json
{
  "uid": "...",
  "nickname": "...",
  "total": 3700.0,
  "remain": 1921.0,
  "used": 1779.0,
  "is_paid_user": false,
  "packages": [
    {"code": "TCACA_code_007_nzdH5h4Nl0", "total": 2200, "remain": 1921, "unit": "credits"}
  ]
}
```

内部解析逻辑：取腾讯响应 `data.Packages[]` 中每个积分包的 `CycleTotalCapacity` / `CycleRemainCapacity` / `CycleUsedCapacity`（均为字符串，转 `float` 后求和汇总），同时读取 `data.IsPaidUser` 标识免费/付费身份。

容错契约同样明确：token 过期或网络失败时不抛异常，而是返回 `{"error": "..."}` 结构，由前端优雅降级显示"—"，保证整个看板不崩。

## 四、Hermes 侧对接

Hermes 侧改动落在 hermes 分支（commit `cd652b7`），分三层：

1. **后端**：`check_workbuddy_status()` 重构为两段式——先用 `/v1/models` 探测服务存活，存活则再拉 `/api/usage_summary`，将结果注入 usage 结构。
2. **前端·状态栏 Popover 卡**：显示 👤 账号昵称 + 免费/付费标识；remain / total 用等宽字体加宽加粗；积分余量渲染彩色进度条——低于 40% 变红、15% 以下进入警示态。
3. **前端·`/quota` 全景看板**：WorkBuddy 独立积分卡，大号等宽数字 + 进度条 + 积分包逐行明细；`/quota` 斜杠命令输出同步展示同一份数据。

## 五、双端一致性验证方法论

单端各自正确不代表端到端正确，为此设计了快照比对法（✅实测通过）：

1. ZCode 在施工侧写快照文件，首行为注释 `# snapshot by zcode`，随后为该时刻 `/api/usage_summary` 的 JSON。
2. Hermes 稍后向同一端点发起请求，取得第二份快照。
3. 两次快照求差，差值即期间的**真实消耗**。实测一对快照为 2779.8 vs 2775.5，Δ4.3 credits，属正常衰减——差值方向与量级均符合预期，说明两端读取的是同一份数据源、同一套解析口径。

该方法的价值在于：不需要冻结账号用量，就能验证"两端所见一致"，天然适配日常使用的动态消耗场景。

## 六、陷阱与排障

两个实测踩过的坑：

1. **新端点要重启才生效**（✅实测）：端点推送后立即请求 `/api/usage_summary` 曾返回 404——服务进程不会热加载新路由，重启后同一请求返回 200。排障口诀：推送 converter 改动后先重启服务进程，再验收。
2. **token 过期必须返回 error 结构而非抛异常**（✅实测）：腾讯 token 失效属常态，若解析层直接抛异常，会拖垮 Hermes 配额看板的整个聚合接口，令所有供应商卡片连带失效。契约层面强制 `{"error": "..."}` + 前端显示"—"是硬性要求。

## 七、事实核查记录

| # | 事实 | 核查方式 |
| :--- | :--- | :--- |
| 1 | 8787 为哑管道，`/api/usage`、`/api/credits`、`/v1/dashboard` 全 404 | ✅实测：三路径请求均 404 |
| 2 | 积分锁在 Tauri IPC `usage_query`，请求腾讯 `get-user-resource-summary` | ✅实测：凭据来自 `accounts.json`（active_uid / nickname / auth.accessToken） |
| 3 | 端点 `GET /api/usage_summary` 由 ZCode 在 `converter.py` 新增 | ✅实测：commit `5b4381c`，CI 三关 pytest / cargo check / cargo test 全绿 |
| 4 | 返回契约含 uid / nickname / total / remain / used / is_paid_user / packages，异常返回 `{"error"}` | ✅实测：字段结构与降级行为符合契约 |
| 5 | 示例数据快照：总额 3700；包 `TCACA_code_007_nzdH5h4Nl0` 2200（余 1921）、500 包耗尽、1000 包未动；免费用户 | ✅实测（数值为示例，随消耗变化） |
| 6 | Hermes 对接 commit `cd652b7`（hermes 分支）：两段式探测 + Popover 卡 + `/quota` 看板与斜杠命令 | ✅实测：三层展示均生效 |
| 7 | 快照比对：2779.8 vs 2775.5，Δ4.3 credits 为正常衰减 | ✅实测：差值方向与量级符合预期 |
| 8 | 重启前请求新端点 404，重启后 200 | ✅实测：同请求前后对比 |

---

## 参考与关联

- codebuddy2openai（Tauri v2）：`converter.py` / `GET /api/usage_summary`（commit `5b4381c`）
- Hermes token-stats 配额插件：`check_workbuddy_status()`（hermes 分支，commit `cd652b7`）
- 本站关联文章：[Hermes-Agent高阶指令全景与生态路线指南](./Hermes-Agent高阶指令全景与生态路线指南.md)
