---
applies_to:
  - Windows 10/11 / macOS / Linux
  - Hermes Agent 自动化运维与配置管理
  - GitHub Actions 自动化看门
risk: low
tweak_module: []
---

# Hermes 本地配置防漂移与无感守卫体系构建指南

> **定位**：Hermes Agent 客户端更新后的配置防漂移、Stash 遗留自检与无感状态栏监控实战指南。
>
> 本文针对频繁更新 Hermes 客户端构建版本（`hermes update`）时所面临的**自定义策略被静默覆盖、本地代码修改被 Stash 遗留、自研技能被误判为过期归档**三大痛点，提出了一套兼顾“云端自动化看门（Capability Watch）与本地端生命周期钩子（Gateway Hook）联动”的纯本地、零网络开销、无感状态栏指示的配置守卫体系。

---

## 一、 隐患溯源：Hermes 客户端更新后的三大漂移陷阱

作为高频迭代的开源 AI Agent 框架，Hermes 支持通过客户端界面的“更新”按钮或终端 `hermes update` 快速同步上游最新构建。然而，在深度定制工作流的环境下，更新过程暗藏三个容易被忽视的系统性隐患：

### 1. 字典深合并 (`_deep_merge`) 与新增默认值的交互副作用
Hermes 在读取配置文件（`config.yaml`）时，采用字典递归深合并策略（`_deep_merge`）：用户显式指定的叶子节点会保留，但上游新增的默认值会自动合入。
- **痛点**：若用户曾拍板禁用某项耗费 Token 或带有副作用的后台任务（例如：显式禁用每 10~15 轮自动派生重放会话的后台审查 `memory.nudge_interval: 0`、`auxiliary.background_review.enabled: false`，以及禁用 Curator 技能维护器 `curator.enabled: false`），一旦新版本重构了字段层级或在更高层级引入了具备破坏性的默认参数（如 `curator.prune_builtins: true`），用户的防御性配置可能因路径不匹配而失效。

### 2. 桌面端更新的“自动暂存但不自动弹出”机制 (`Stash Drop`)
在默认配置 `updates.non_interactive_local_changes: stash` 下：
- 客户端在非交互式更新（如桌面端点击更新按钮）前，为防止代码冲突，会自动执行 `git stash push --include-untracked` 暂存本地所有未提交的工作区变更；
- **致命陷阱**：出于安全防御，**桌面端更新成功后故意不会执行 `git stash pop`**！上游设计认为静默还原旧补丁极易导致刚更新的内核崩溃。因此，开发者随手写在本地的源码临时修改会被长期遗弃在 `git stash` 堆栈中，若不主动排查，极易导致定制功能丢失。

### 3. 技能管辖标记机制（`created_by`）与自研技能的误归档风险
自新版引入技能生命周期管理（Curator）后，系统在 `~/.hermes/skills/.usage.json` 中使用 `created_by` 标记界定技能归属：
- 随仓库发布的内置技能标为 `installed`；
- 用户手动编写或会话前台明确要求创建的技能标为 `None`；
- 唯独后台自主审查 Fork 派生创建的技能会标为 `agent`。
- **风险**：Curator 只对 `created_by: "agent"` 的技能执行 30 天陈旧（stale）与 90 天归档（archived）流转。一旦核心自研技能（如跨端共享记忆、专业方法论蒸馏技能）因早期环境配置不当被误盖上 `agent` 戳记，闲置一段时期后将被直接踢出活跃技能池，导致 Agent 在后续任务中无法召回该技能。

---

## 二、 体系设计：三位一体的无感防漂移守卫

为了避免“每次点击更新后都需要叫 AI 或人工肉眼比对配置”的繁琐流程，我们构建了一套纯本地、自愈触发的守卫架构：

```text
       用户点击桌面端「更新 Hermes」
                    │
                    ▼
          代码拉取 & 依赖安装完成
                    │
                    ▼
          Hermes 网关进程自动重启
                    │
        ┌───────────┴────────────────┐
        │  触发 gateway:startup 钩子 │
        └───────────┬────────────────┘
                    │ (后台异步线程，耗时 < 50ms)
                    ▼
       执行本地 check_config_guard()
        ├── 1. 解析 config.yaml，核验 5 大拍板键
        ├── 2. 扫描 git stash 栈，区分自动与手动暂存
        └── 3. 巡查核心技能 .usage.json 标记
                    │
                    ▼
       写入 last-result.json 本地缓存
                    │
                    ▼
       桌面端状态栏 Chip 轮询感知
        ├── 全部健康：仅显示微小绿点，界面绝对静默
        └── 发现异常：高亮红点 + 告警计数，点击弹窗查看处置建议
```

---

## 三、 工程化落地实现

### 1. 核心体检逻辑（纯标准库实现，零第三方依赖）

在本地能力清单比对脚本（`check_capability_upstream.py`）中，扩展实现针对本地配置的解析与校验：

```python
# scripts/check_capability_upstream.py 片段

def check_config_guard(check):
    """
    零网络、纯标准库体检函数：
    1. 核验 config.yaml 核心键值是否吻合拍板基线；
    2. 检查本地源码是否存在未还原的 git stash；
    3. 检查核心自研技能是否被误打 created_by: agent 标记。
    """
    problems, detail = [], []
    cfg_path = check["file"]
    
    # 1. 逐层解析 YAML 缩进树，获取点分绝对路径叶子值
    leaves = read_config_leaves(cfg_path)
    for item in check.get("expect", []):
        path, want = item["path"], item["value"]
        got = leaves.get(path, "<缺失>")
        ok = (got == want)
        if not ok:
            problems.append(f"配置键 {path} 期望 {want!r}，实际为 {got!r}")

    # 2. 检查本地 git stash 栈
    for repo in check.get("stashRepos", []):
        out = subprocess.run(["git", "-C", repo, "stash", "list", "--format=%gd|%s"],
                             capture_output=True, text=True)
        stashes = [l for l in (out.stdout or "").splitlines() if l.strip()]
        if stashes:
            problems.append(f"{repo} 存在 {len(stashes)} 条未还原 stash，请排查是否包含定制内容")

    # 3. 巡查核心自研技能标记
    usage_path = check.get("usageFile")
    protected = check.get("protectedSkills", [])
    if usage_path and os.path.exists(usage_path):
        with open(usage_path, encoding="utf-8") as f:
            usage = json.load(f)
        for name in protected:
            rec = usage.get(name, {})
            if rec.get("created_by") == "agent":
                problems.append(f"核心技能 {name} 被标记为 agent-created，面临归档风险")

    return problems, detail
```

### 2. 挂载到网关启动生命周期 (`gateway:startup`)

Hermes 自身虽然没有开放面向用户的 `post_update` 独立钩子，但其网关事件钩子机制（`~/.hermes/hooks/`）会在每次网关启动时广播 `gateway:startup` 事件。而桌面端在更新完毕后，**必然会重启网关**。

在 `~/.hermes/hooks/config-guard/` 目录下声明钩子：

- **`HOOK.yaml`**：
  ```yaml
  name: config-guard
  description: 每次网关启动时自动执行本地配置防漂移自检
  events:
    - gateway:startup
  ```

- **`handler.py`**：
  ```python
  import threading, json
  from pathlib import Path

  _checked = threading.Event()

  def _async_guard():
      import check_capability_upstream as m
      # 执行检查并将 JSON 写入 ~/.hermes/hooks/config-guard/last-result.json
      ...

  def handle(event_type: str, context: dict):
      # 单次网关启动生命周期内仅触发一次，不争抢系统资源
      if not _checked.is_set():
          _checked.set()
          threading.Thread(target=_async_guard, daemon=True).start()
  ```

### 3. 云端 Actions 与本地环境的解耦设计

在 GitHub Actions CI（如 `capability-upstream-watch.yml`）自动化看门任务中，云端 Runner 并未运行本地 Windows 桌面环境。

为了实现同一套清单在不同场景下的平滑适配，在清单文件 `capability-inventory.json` 中将组件声明为 `local-config-guard` 类型：
- **云端 GitHub Actions**：脚本自动侦测 `GITHUB_ACTIONS=true` 环境变量，自动标记为 `⏭️ Actions 跳过` 并计入跳过数，绝不因缺少本地环境而报错；
- **本地双击 `watch-capability.cmd`**：全量执行线上上游比对 + 本地配置守卫，输出完整对账报告。

---

## 四、 总结与日常操作规范

通过构建这套防漂移守卫，开发者的日常运维流程得到了极大简化：

1. **更新常态化无感**：平时在客户端点击更新后，直接正常使用，无需特意唤醒 AI 协助复核；
2. **异常直观透出**：一旦状态栏左侧出现红点并提示 `守卫告警 ×N`，点击即可直接阅读清晰的差异清单与修复指引（例如提示运行 `git stash drop` 清理过期更新缓存，或复原被覆盖的配置键）；
3. **全局定期排查**：当升级了系统全局 CLI 或调整了插件版本时，双击运行仓库根目录下的 `watch-capability.cmd`，即可一键完成全网 19 项能力组件的立体对账。
