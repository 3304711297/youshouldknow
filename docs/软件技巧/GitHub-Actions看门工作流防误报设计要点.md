---
applies_to:
  - GitHub Actions 定时看门工作流（upstream watch / version check 类）
  - 自建依赖清单 + JSON 基线比对脚本（Python/Shell）
  - 任何「拉上游 → 比基线 → 开 Issue」模式的自动化巡检
risk: low
tweak_module: []
---

# GitHub Actions 看门工作流防误报设计要点

> 本文目标：从真实治理（四轮 Issue 收口 + 根因修复）中提炼看门工作流的四类根因与修法。看门的价值在于「开了单就该处理」——误报一多，用户就会关闭通知，看门形同虚设。
>
> 适用场景：`cron` 定时拉取上游（npm / GitHub Releases / commits / 网页计数器）→ 与本地基线比对 → 差异开 Issue 提醒。前三个坑是**告警噪声**（假阳性），坑四是**产物漂移**（本地与云端互相打架）——四个全部来自实测，可复用到任何仓库。

## 坑一：没有内容级去重，同一变更反复开单

**现象**：某插件的上游变更昨天已评估并关闭 Issue，今天（或下次 cron）watcher 又为**同一批 commit** 开出一张新 Issue。

**根因**：Issue 去重逻辑只查「是否存在未关闭的同标签 Issue」：

```yaml
EXISTING_ISSUE=$(gh issue list --state open --label "upstream-watch" --json number --jq '.[0].number')
```

Issue 一旦关闭，同样的变更就会再开新单——因为**基线没有回写**，watcher 的世界里「上次提醒过」这个状态根本不存在。

**修法（按优先级）**：
1. **收口时回写基线**：评估完不留尾巴——更新基线 commit/tag 并随清单推 main，下次比对自然为「一致」；
2. **关单时删除已消失组件**：如果 Issue 对应的组件本地已卸载，把它的基线条目一并删除，而不是留着基线继续「落后于上游」；
3. **防御性兜底**：开单前比对新单内容与近 N 天已关闭 Issue 是否同 commit（可用 issue 搜索 API）。

**教训**：关闭 Issue ≠ 处理完毕。看门的收口动作必须包含「让下次比对不再报警」，否则闭环是假的。

## 坑二：把「日期刷新」当成更新信号（最隐蔽）

**现象**：上游组件总数一字未变（如 90,698 = 90,698），watcher 却天天报「有更新（0 技能）」。

**根因**：比对条件混入了元数据字段：

```python
# 错误：上游每日重跑索引，extractedAt 恒等于当天
behind = bool(total != rec_total or (extracted_at and rec_date and extracted_at > rec_date))
```

这个 bug 还有个加剧因素：**工作流只有 `issues: write` 权限，没有 `contents: write`，回写不了清单里的日期**——于是从装机第二天起，这条「日期落后」永远成立，必然天天误报。

**修法**：更新信号只认**实质内容变化**：

```python
# 正确：仅数量增长计为待跟进；缩量属上游数据波动，无需本地动作
behind = total > rec_total
```

**判断标准**：问一句「这个字段变化后，用户需要做什么动作？」——日期刷新不需要任何动作，就不配当信号。

## 坑三：实时计数器天然漂移，基线永远追不上

**现象**：基线写了 1393，触发验证时上游变 1395，回写 1395 后再查变 1396——收口永远差一步。

**根因**：某些上游（社区市场、聚合索引）的 total 是**分钟级漂移的实时计数器**，不是稳定版本号。「精确对齐」在这个模式下不可能。

**修法**：
- 基线按**收口时点的实测值**回写，不追中间值；
- 容忍「下次运行小幅正向偏差」，这正是该类源的常态（也因坑二的修法，仅增长才报警，缩量不动作）；
- 若漂移频繁到失控，把报警阈值从「any diff」放宽为「增长 ≥ N」。

## 坑四：本地与云端重复跑同一套检查，产物互相打架

**现象**：GitHub Issue 正文是一份完整的「全 ✅ 最新」报告，本地工作区却散落着另一份同名报告，内容全是 `⚠️ 查询失败：HTTP Error 403: rate limit exceeded`。两份产物对不上，用户不知道该信谁。

**根因（两条叠加，缺一不可）**：

1. **相对路径 + 任意工作目录 → 产物甩得到处都是**：

    ```python
    # 错误：相对路径，脚本在哪个目录跑，报告就写在哪里
    REPORT_PATH = "capability-report.md"
    ```

    在工作区根目录执行 `python scripts/check_capability_upstream.py`，报告就生成在仓库外；仓库里还留着一份陈旧副本——同一份数据三个地方各说各话。

2. **本地裸跑没有凭据 → 撞上匿名限流**：CI 用 `secrets.GITHUB_TOKEN`（5000 次/小时），本地直接跑脚本没注入 token，走匿名配额（60 次/小时），一打就穿。更麻烦的是这类脚本常配有 `.cmd` 封装，封装里有 `gh auth token` 注入，但**直接调脚本的人根本不走那条路**。

**修法（四道，逐层收口）**：

1. **产物路径绝对锚定**：用脚本自身位置反推仓库根，杜绝甩文件：

    ```python
    REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    REPORT_PATH = os.path.join(REPO_ROOT, "capability-report.md")
    ```

2. **端云职责解耦——本地只做云端做不了的事**：云端没有你的本机环境，客户端种子清单、本地配置守卫这类**本地专属项**只能本地跑；18 项外部上游交给 CI 每日定时跑即可，本地重复跑纯属浪费配额还制造分歧。加个开关：

    ```python
    local_only = "--local-only" in sys.argv
    if local_only and check["type"] not in ("local-merged-marketplace", "local-config-guard"):
        skipped += 1   # 云端托管的组件，本地直接跳过
    ```

    本地模式下**不改写、不收口云端 Issue**——真源唯一定格在 CI 产出的 Issue 正文。

3. **大面积失败熔断**：网络波动或限流时不许写盘，否则残缺数据会覆盖掉上一份好报告：

    ```python
    if not on_actions and not local_only and failed_queries >= 3:
        sys.stderr.write("上游查询大面积失败，已中止写入，防残缺数据覆盖")
        return 1
    ```

4. **报告不进版本库**：`capability-report.md` 从 git 跟踪移除并写进 `.gitignore`。它是**运行产物**不是源码，跟踪它必然产生「本地改了、CI 也改了」的冲突。

**判断标准**：问一句「这个检查项，云端 runner 有环境跑吗？」——有就交给 CI，本地别碰；没有才留本地。两边跑同一件事，迟早打架。

## 附：配套的工作流卫生

- **编辑已有 Issue 时同步刷新标题**：`gh issue edit "$EXISTING" --title "$TITLE" --body-file report.md`——否则标题残留过期的「N 项待跟进」，正文已清零也看不出来；
- **非 GitHub 源优雅降级**：爬虫类检查（带浏览器 UA 的 API / 页面解析）异常时严格标记 `⚠️ 暂不可达` 并保持基线，`behind=False` 绝不计入 outdated，绝不误开 Issue，不阻塞整体检查；
- **收口靠「比对结果」而非「人工判断」**：工作流里 `has_updates == 'false'` 分支自动关单，用户只需修数据，不用手动关 Issue。

## 速查表

| 症状 | 根因 | 修法 |
|------|------|------|
| 同一变更反复开单 | 关单未回写基线，无内容级去重 | 收口动作 = 评估 + 回写/删基线 + 推 main |
| 「有更新（0 技能）」 | 日期刷新被当信号 + 无权限回写日期 | `behind` 只认实质内容变化 |
| 基线永远追不上 | 实时计数器天然漂移 | 按收口时点实测回写；仅增长报警 |
| 标题数与正文不符 | 编辑路径漏了 `--title` | edit 时同步刷新标题 |
| 上游站挂了也开单 | 无优雅降级 | 异常 → behind=False + 标记不可达 |
| 本地与云端报告不一致 | 相对路径甩文件 + 裸跑无 token 撞限流 | 路径绝对锚定 + `--local-only` 解耦 + 失败熔断 + 报告不入库 |
