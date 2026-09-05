---
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
  - zcode（Z.AI）
risk: low
tweak_module: []
status: reference
---

# Hermes-ZCode 双 Agent 跨端协同机制实战

> 本文目标：还原一套已在本机跑通的"双桌面 Agent 协同"机制——ZCode 负责施工（写代码、跑任务），Hermes 负责盯盘（监听进度、审计产物、完工后接手验证）。核心解决一个痛点：施工方埋头干活时，监听方的聊天框完全空闲休眠，如何在零人工介入的前提下被自动唤醒并接手。

---

## 一、背景与定位

两套桌面 Agent 各有分工：ZCode 专注施工，Hermes 承担监听、审计与接手。理想流程是"派活 → 放手 → 完工自动唤醒 → 接手验证"，但默认情况下 Hermes 主对话在等待期间完全休眠，ZCode 完工也不会通知对方，闭环就断在"唤醒"这一环。

本文方案把闭环拆成三层，全部跑在 Windows 本机：

| 层 | 载体 | 职责 |
| :--- | :--- | :--- |
| 监听层 | ZCode SQLite 会话库 | 提供施工进度的唯一事实来源 |
| 守护层 | Hermes `scripts/watch_zcode.py` | 轮询库表，判定会话 settled |
| 唤醒层 | `terminal(background=True, notify=true)` | 进程退出事件唤醒 Hermes 主对话 |

## 二、机制总览

```
ZCode 施工 ──写入──▶ SQLite 会话库（session 表）
                          │ 只读轮询（每 3 秒）
                          ▼
        Hermes watch_zcode.py ──15s 滑动窗口──▶ 判定 settled
                          │
                          ▼
        watcher 进程 exit 0 ──▶ Hermes 内部 Process Exit Event
                          │
                          ▼
        主对话自动唤醒 ──▶ 自主执行接手验证
```

三个关键设计：

1. **只读监听**：Hermes 侧对 ZCode 数据库只读不写，避免跨进程写锁冲突。
2. **退出即信号**：不依赖 Windows 系统通知，而是把"watcher 进程退出"本身当作信号源。
3. **双向都有解**：Hermes 等 ZCode 靠守护进程，ZCode 等 Hermes 靠握手文件（见三.5）。

## 三、实战步骤

### 1. 监听层：只读读取 ZCode 会话库

ZCode 的会话数据落在本地 SQLite 库 `C:\Users\VOS-User\.zcode\cli\db\db.sqlite`。Hermes 侧必须以只读模式打开：

```python
conn = sqlite3.connect(r'file:C:\Users\VOS-User\.zcode\cli\db\db.sqlite?mode=ro', uri=True)
```

**严禁以可写方式打开该库**——ZCode 运行中持有写锁，写入会触发 `database is locked` 死锁。

`session` 表关键字段：`id` / `title` / `project_id` / `time_created` / `time_updated` / `task_type`。查询时用 `task_type != 'subagent_child'` 过滤子代理、只取主会话；活跃度指标 = `time_updated` 距当前的秒数，数值越大表示该会话越久无动静。

### 2. 守护层：watch_zcode.py

Hermes 侧脚本 `scripts/watch_zcode.py`（118 行）把"库静止"翻译成"进程退出"：

- 每 3 秒轮询一次库；
- 以 15 秒滑动窗口判定 settled：窗口内无新事件才算完工；
- 忽略历史遗留的 step-start 子代理事件，避免假阳性；
- 支持 `--timeout` 参数兜底超时；
- 完工时输出 `ZCode session <id> has settled!` 并以 exit 0 退出。

### 3. 唤醒层：后台守护 + 事件唤醒

用 `terminal(background=True, notify=true)` 启动守护进程。进程退出会触发 Hermes 内部的 Process Exit Event——它是应用内事件总线，独立于 Windows 系统通知开关，不受系统通知设置影响——从而自动唤醒主对话。

### 4. 全链路演练实录

一次完整演练的时间线（✅ 实测）：

| 时刻 | 事件 |
| :--- | :--- |
| T+0 | 后台启动 ZCode 任务 |
| T+2s | 挂上守护进程（notify=true） |
| 施工期间 | 聊天框完全空闲休眠，零人工介入 |
| 完工 | ZCode 进程 exit 0 → watcher 检测到 settled 自动退出 |
| 随即 | Hermes 被自动唤醒，立即自主执行接手验证（WorkBuddy 积分复核） |

全程无需用户输入。

### 5. 反向等待：ZCode 等 Hermes

ZCode 侧没有内置的后台通知钩子——`zcode --help` 全量参数中不存在 background / notify / watch / daemon。等价模式是**回合内阻塞轮询 + 握手文件**：

1. Hermes 接手前，ZCode 在同一回合内阻塞轮询；
2. Hermes 完工后写入握手文件 `%TEMP%\hermes_handshake.txt`；
3. ZCode 每秒检查一次该文件，一旦出现即继续同回合执行接手。

文件机制本身已实测（`HANDSHAKE-RECEIVED after 0.0s`）；端到端流程尚待 GUI 真实任务顺带验证（⚠️ 待复核）。

## 四、陷阱与排障

1. **"开始盯"指令必须趁 ZCode 施工中单独发出。** 若与"zcode 已完成"合并成同一条消息到达，监听窗口已被跳过，无守护可触发唤醒——实测因此错过 370 秒。
2. **headless CLI 会话在 GUI 里看不到。** headless 会话落在 `proj_d-ai-coding` 项目，而 GUI 主区对应 `proj_d-ai-coding-.zcode-workspace-default`，两者不是同一个项目，GUI 界面查不到 CLI 会话（另篇详述）。
3. **历史子代理事件可致 watcher 永不退出。** 曾有子代理的最后事件停留在 step-start，完工判定永远不满足；修复手段即守护层的 15 秒滑动窗口 + 过滤子代理。

## 五、边界与适用性

- **适用**：Windows 本机"一方施工、一方审计"的双 Agent 分工，需要"完工即唤醒"的自动化闭环；前提是 Hermes 已部署 `scripts/watch_zcode.py` 且能访问 ZCode 数据目录。
- **不适用**：跨机器协同（会话库在本机盘上）；ZCode 库表结构变更后需同步调整查询字段。
- **成本与纪律**：watcher 常驻仅 3 秒一次轮询，开销可忽略；真正的门槛是"盯盘指令必须趁施工中单独发送"的交互纪律。

## 六、事实核查记录

| 条目 | 状态 |
| :--- | :--- |
| 监听层只读打开方式与 session 表字段 | ✅ 实测 |
| watch_zcode.py 3s 轮询 / 15s 滑动窗口 / settled 输出与 exit 0 | ✅ 实测 |
| Process Exit Event 自动唤醒主对话 | ✅ 实测 |
| 全链路演练（T+0 → 接手验证，全程免人工） | ✅ 实测 |
| "开始盯"与完工消息合并导致错过 370 秒 | ✅ 实测 |
| CLI 会话与 GUI 主区项目标识不一致 | ✅ 实测 |
| 握手文件轮询（HANDSHAKE-RECEIVED after 0.0s） | ✅ 实测 |
| 反向等待端到端（GUI 真实任务顺带验证） | ⚠️ 待复核 |
