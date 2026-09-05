---
applies_to:
  - Windows 10/11
  - zcode（Z.AI）
risk: low
tweak_module: []
status: reference
---

# ZCode headless CLI 与 GUI 会话体系辨析

> 本文目标：厘清 ZCode（Z.AI）headless CLI 与 Desktop GUI 两套会话体系的隔离关系。先给两套体系的总览对比，再以 db.sqlite 实测数据揭示会话落点差异与"GUI 不可见"现象，接着辨析两边互不相通的模型配置与额度池，随后复盘实测中的两起故障链，最终沉淀出经用户拍板的实践规范与适用边界。核心结论只有一句：**headless 会话与 GUI 会话是两套互相隔离的体系，请勿混用。**

---

## 一、两套会话体系总览

ZCode 在同一台机器上并存两套会话体系：一套是面向自动化脚本的 headless CLI（`zcode -p`），一套是面向人机协同的 Desktop GUI。二者各有一套独立的会话落点、模型配置与额度体系：

| 维度 | headless CLI | Desktop GUI |
| :--- | :--- | :--- |
| 入口 | `D:\zcode\resources\glm\zcode.cjs`（v0.16.5） | ZCode Desktop 客户端 |
| 单发调用 | `-p` / `--prompt` 无头单发 | 手动创建会话 |
| 工作目录 | `--cwd` 指定 | 主工作区 `.zcode/workspace/default` |
| 自检手段 | `zcode doctor`（version / process / node / platform） | — |
| 会话可见性 | GUI 任务列表**完全看不到** | GUI 任务列表正常显示 |
| 模型配置 | 只认 `.zcode/cli/config.json` | 走 `.zcode/v2/setting.json` |
| 额度体系 | 与 GUI 互不相通 | 独立额度池 |

一句话概括：**GUI 看不见 headless 的会话，headless 也不读 GUI 的模型配置**——两套体系只在磁盘上同住，在会话、模型与额度三个层面彼此隔离。

## 二、会话落点差异实测（db.sqlite）

### 1. 两个并行的 project_id

对 `db.sqlite` 实测，同一个目录 `D:\ai coding` 会落出两个互不隶属的 project_id：

- headless 会话（`--cwd 'D:/ai coding'`）→ `proj_d-ai-coding`
- GUI 主工作区会话（目录 `D:\ai coding\.zcode\workspace\default`）→ `proj_d-ai-coding-.zcode-workspace-default`

`--cwd` 只决定 headless 会话自己的落点；GUI 主工作区固定锚定在 `.zcode\workspace\default` 子目录，因此比前者多出 `.zcode-workspace-default` 后缀。

### 2. GUI 侧完全不可见

两个 project_id 在 db.sqlite 中并行存在、互不隶属，而 GUI 任务列表只显示后者。结果就是：**headless 会话在 GUI 端完全不可见**。实测中 6 个 headless 会话全部"隐身"——任务在后台真实跑过、真实落库，GUI 上却无任何痕迹。

## 三、模型体系分离

会话隔离只是表象，更隐蔽的是模型配置与额度的双向隔离：

- **CLI 侧**：只认 `C:\Users\VOS-User\.zcode\cli\config.json`。其中 `providers` 仅 `cpa-gui` 一项，指向本地网关 `http://127.0.0.1:18080`；`model.main` 为 `cpa-gui/gemini-3.8-flash`。
- **GUI 侧**：走 `.zcode/v2/setting.json` 与 v2 provider family OAuth 体系，与 CLI 的本地网关配置分属两套。

两边的模型选择与额度池互不相通：CLI 撞 429 / 配额耗尽，不代表 GUI 侧也不可用；反过来，GUI 侧额度充裕也救不了 CLI。排障时必须先分清"哪一侧在报错"。

## 四、故障链实录

以下两起故障均来自实测，按发生顺序复盘：

### 故障链一：EasyCLIProxyAPI 网关未启动

1. **现象**：EasyCLIProxyAPI 网关未启动，CLI 报 `AI_APICallError connect ECONNREFUSED 127.0.0.1:18080`（错误标记 `isRetryable`）。
2. **处置**：后台重启网关进程后，18080 端口恢复 LISTENING，CLI 恢复正常。
3. **启示**：CLI 的模型链路依赖本地网关进程，`connect ECONNREFUSED 127.0.0.1:18080` 首先应排查网关是否存活。

### 故障链二：Gemini 个人配额触顶

1. **现象**：Gemini 个人配额触顶，CLI 全挂，报 `RESOURCE_EXHAUSTED`，附重置倒计时 `Resets in 1h47m50s`。
2. **启示**：CLI 侧配额耗尽只能等待重置；由于模型体系分离，此时 GUI 侧的可用性不受影响。

## 五、实践规范（经用户拍板）

1. **严禁用 headless CLI 代开测试会话**。三重原因叠加：GUI 不可见（无法盯盘）、模型体系分离（配置与链路不同）、额度混淆（消耗记到谁头上说不清）。CLI 里跑过的"测试会话"对 GUI 用户而言等于没发生过。
2. **跨端验证由用户在 GUI 手动创建会话**；协同方（Hermes）只做 db.sqlite 只读监听与结果验收，不得代开。
3. **CLI 撞 429 时不得擅自改 ZCode 配置切供应商**：Desktop 自定义供应商只认 UI 内添加，配置文件层面的手工改动不在支持范围内。

## 六、适用边界

- **headless CLI 适用**：CI 脚本、无头自动化等完全脱离 GUI 的场景——会话无人盯盘、产物以文件与退出码交付。
- **必须用 GUI 会话的场景**：双人协同盯盘 / 验收——会话两边互见，GUI 端可实时查看过程；headless 会话在 GUI 中不可见，天然不满足"盯盘"需求。

## 附录：事实核查记录

以下逐条核对文中断言与实测依据，✅ 表示已实测验证：

- ✅ CLI 形态：可执行文件为 `D:\zcode\resources\glm\zcode.cjs`，版本 v0.16.5；`-p` / `--prompt` 无头单发；`--cwd` 指定工作目录；`zcode doctor` 自检项为 version / process / node / platform。
- ✅ `zcode --help` 全量参数中无 background / notify / watch / daemon 一类后台常驻参数（对比 Hermes terminal 工具有 background + notify 事件唤醒机制）。
- ✅ 落点实测（db.sqlite）：headless `--cwd 'D:/ai coding'` → `proj_d-ai-coding`；GUI 主工作区 `D:\ai coding\.zcode\workspace\default` → `proj_d-ai-coding-.zcode-workspace-default`；两个 project_id 并行存在。
- ✅ GUI 任务列表只显示 GUI 侧 project_id；实测 6 个 headless 会话全部在 GUI 不可见（"隐身"）。
- ✅ 模型分离：CLI 只认 `C:\Users\VOS-User\.zcode\cli\config.json`（providers 仅 cpa-gui → `http://127.0.0.1:18080`，`model.main` 为 `cpa-gui/gemini-3.8-flash`）；GUI 走 `.zcode/v2/setting.json` 与 v2 provider family OAuth 体系；两边模型选择与额度池互不相通。
- ✅ 故障链一：网关未启动 → `AI_APICallError connect ECONNREFUSED 127.0.0.1:18080`（isRetryable）→ 后台重启网关进程后 18080 恢复 LISTENING。
- ✅ 故障链二：配额触顶 → `RESOURCE_EXHAUSTED 'Resets in 1h47m50s'`，CLI 全挂。
- ✅ 实践规范三条与适用边界两条均经用户拍板确认。

## 参考与关联

- 本站关联文章：[Hermes-Agent 高阶指令全景与生态路线指南](./Hermes-Agent高阶指令全景与生态路线指南.md)
- 本站关联文章：[EasyCLIProxyAPI 本地网关架构与多智能体客户端适配](./EasyCLIProxyAPI本地网关架构与多智能体客户端适配.md)
- 本站关联文章：[Google Antigravity 双配额池隔离陷阱与实时监控](./Google-Antigravity双配额池隔离陷阱与实时监控.md)
