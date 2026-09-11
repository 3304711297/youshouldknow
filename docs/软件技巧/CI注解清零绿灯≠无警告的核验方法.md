---
applies_to:
  - GitHub Actions 工作流（任何带 Annotations 的 CI）
  - 使用第三方 action 且以 40 位 SHA 钉版的仓库
  - 需要把 CI 警告「清零」而非「压掉」的维护场景
risk: low
tweak_module: []
---

# CI 绿灯不等于没问题：注解要单独查

> 本文目标：破除两个让 CI 噪声长期存活的错觉——**绿灯也可能带警告**，以及**界面显示的数量不等于实际数量**。
>
> 两个坑都来自实测：一次跨 9 个仓库的注解治理中，GitHub 界面显示「1 warning」，实际本地有 60 条。

## 坑一：conclusion 是 success，注解照样有 warning

**现象**：Actions 页面一排绿勾，PR 也能合，但仓库的 Annotations 区长期挂着一条：

```text
Node.js 20 is deprecated. The following actions target Node.js 20
but are being forced to run on Node.js 24
```

**根因**：`conclusion` 只反映**步骤有没有失败**。warning 级注解不阻断流程，因此 job 照样 success。
看绿勾判断「干净了」从机制上就是错的——这两件事在 GitHub 的模型里根本不在一个维度。

**正确核验方式**：查 check-run 的 `output.annotations_url`，而不是看 run 状态。

```bash
SHA=$(git rev-parse HEAD)
gh api "repos/<owner>/<repo>/commits/$SHA/check-runs" \
  --jq '.check_runs[].output.annotations_url' \
| while read url; do
    gh api "$url" --jq '.[] | "\(.annotation_level) | \(.message)"'
  done | sort | uniq -c
# 输出为空 = 真的零注解
```

**教训**：「CI 绿了」和「CI 没有警告」是两个独立命题。宣称清零前，必须查注解接口。

## 坑二：界面显示的注解数量有上限（约 10 条）

**现象**：Annotations 区显示「1 warning」，修掉它、再跑，又冒出下一条——像打地鼠。

**根因**：GitHub 界面一次只渲染有限条注解（实测约 10 条）。`pnpm -r lint` 本地跑出来是 60 条，
界面上永远只显示前 10 条。**你看到的不是全量**。

**修法**：以本地全量输出为准建立清单，一次清完，不要按界面显示逐条修。

```bash
# 建立本地基准（JSON 便于统计与分区）
pnpm exec eslint src -f json > lint.json
python - <<'EOF'
import json, collections
for f in json.load(open("lint.json")):
    if f["warningCount"]:
        print(f['warningCount'], f["filePath"],
              dict(collections.Counter(m["ruleId"] for m in f["messages"])))
EOF
```

文件多、互不重叠时，按文件集分区并行处理；处理完再跑一次全量 lint 确认归零。

## 附：Node.js 20 弃用警告的定位与修法

这条警告的具体根因值得一提，因为**直觉很容易找错方向**：

**它与 workflow 里的 `node-version` 无关**。是 action 自身的 `action.yml` 声明了 `runs.using: node20`，
GitHub 强制在 node24 上运行才弹注解。

定位要分两步——先把钉版的 SHA 映射回 tag，再查那个 tag 的运行时：

```bash
# 1. SHA → tag（annotated tag 取 ^{} 剥离后的那行）
git ls-remote --tags https://github.com/<owner>/<action> | grep <sha-prefix>

# 2. 查该 tag 的运行时
gh api repos/<owner>/<action>/contents/action.yml?ref=<tag> \
  --jq '.content' | base64 -d | grep using:
```

两个省事的经验：

- **`composite` 类型的 action 没有 node 运行时**，永不产生此警告。看到 `using: composite`
  就可以直接排除，不必查版本（如 `lycheeverse/lychee-action`、`dtolnay/rust-toolchain`）。
- 升级前扫一眼 release note 的 Breaking Changes。例如 `actions/checkout` v7 会阻断
  `pull_request_target` / `workflow_run` 场景下的 fork checkout，对某些仓库是破坏性的。

## 延伸：清零不是压制

把 warning 「清零」有两条路：改代码消除根因，或加 `eslint-disable` 让规则闭嘴。
**只有前者算清零**——压制会让警告从清单里消失，但问题还在，且下次加规则时又会冒出来。

判定是否真清零的可复核标准：全仓库扫描，应当既没有 `any`，也没有 `eslint-disable`。

```bash
rg -n 'as any|: any\b|<any>|\bany\[\]|eslint-disable' packages/*/src packages/*/tests
# 无输出 = 真清零
```
