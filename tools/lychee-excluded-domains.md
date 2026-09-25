# lychee 排除域名人工复核台账

`lychee.toml` 的 `exclude` 列表把这些域名排除出 CI 自动死链检查（CI runner 上稳定 403/超时，或站点拒绝爬虫）。排除不等于豁免：每个域名对应的外链由人工复核负责。本台账记录排除原因与最近一次人工复核时间，**每次往 docs/ 新增指向这些域名的链接时，应在本表登记并复核目标可达性**。

维护规则：

1. 新增排除域名时，在 lychee.toml 加注释说明原因，并同步在本表加行（建档日期）；
2. 复核时只需确认文章中的具体链接目标可访问、内容仍支撑正文声明，把「最近人工复核」改为当时日期；
3. 若某域名在 CI 上恢复稳定可达，可从 exclude 移除并删除本表对应行。

| 域名 | 排除原因 | 最近人工复核 |
| --- | --- | --- |
| www.grc.com | 站点拒绝爬虫/不稳定 | 2026-08-28 建档（未单独复核） |
| profileinspector.io | 站点拒绝爬虫/不稳定 | 2026-08-28 建档（未单独复核） |
| blog.csdn.net | 站点拒绝爬虫 | 2026-08-28 建档（未单独复核） |
| bbs.nga.cn / ngabbs.com | 站点拒绝爬虫 | 2026-08-28 建档（未单独复核） |
| www.chiphell.com | 站点拒绝爬虫 | 2026-08-28 建档（未单独复核） |
| www.overclock.net | CI 上 403 | 2026-08-28 建档（未单独复核） |
| iknow.lenovo.com.cn | CI（美国 runner）持续超时 | 2026-08-28 建档（未单独复核） |
| www.intel.com / community.intel.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| nvidia.custhelp.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| videocardz.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| www.reddit.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| cs.stackexchange.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| forum.dcs.world | CI 上 403 | 2026-08-28 建档（未单独复核） |
| wccftech.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| blurbusters.com / forums.blurbusters.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| forums.guru3d.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| help.xmg.gg | CI 上 403 | 2026-08-28 建档（未单独复核） |
| www.tenforums.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| h30471.www3.hp.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| www.atera.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| dokumen.pub | CI 上 403 | 2026-08-28 建档（未单独复核） |
| www.elevenforum.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| forum-en.msi.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| zhuanlan.zhihu.com | 站点拒绝爬虫 | 2026-08-28 建档（未单独复核） |
| superuser.com | CI 上 403 | 2026-08-28 建档（未单独复核） |
| forums.tomshardware.com | 2026-08-29 起站点对 CI runner 返回 403（此前可达），链接为目标帖两处 | 2026-08-29 建档（目标帖内容此前核查属实） |
| techcommunity.microsoft.com | 2026-08-29 起站点对 CI runner 返回 403（此前可达），涉及驱动签名与 TPM 绕过讨论帖等 3 处引用 | 2026-08-29 建档（微软官方社区，内容此前核查属实；后续可考虑改链 learn.microsoft.com 存档） |
| www.asus.com | 2026-08-29 CI runner 访问 403（封锁呈间歇性，本地经代理可达） | 2026-08-29 建档 |
| www.digitalfoundry.net | 2026-08-29 访问 403（DLSS 4.5 Preset L 实测文，2026-08-28 核查时可达；封锁呈间歇性） | 2026-08-29 建档（内容 2026-08-28 核查属实） |
| cn.game-console.org | 2026-08-29 CI runner 访问 403（电源计划社区资料站） | 2026-08-29 建档（内容此前核查属实） |
| www.bilibili.com / b23.tv | 2026-08-29 起对 CI runner 返回 412（反爬前置校验，本地经代理可达），涉及视频引用多处 | 2026-08-29 建档（B 站为视频源主域，人工复核时直接浏览器打开即可） |
| www.bleepingcomputer.com | 2026-09-04 起 Cloudflare 防护对 CI runner 返回 503 与 1h 速率惩罚（本地浏览器可达） | 2026-09-04 建档（Windows 11 绕过 MSA 报道核查属实）；**2026-09-09 发现 lychee.toml 排除行误写双反斜杠致正则永不匹配、排除断链**（本次 CI failure 34326142701 即此因），已修正并验证模式可匹配目标 URL |
| www.nccgroup.com | 2026-09-05 起 Cloudflare/WAF 对 CI runner 与 lychee 返回 403（本地浏览器可达） | 2026-09-05 建档（Ollama CVE 技术通告核查属实） |
| linustechtips.com | 2026-09-09 起 Cloudflare WAF 对 CI runner 与爬虫返回 403（本地浏览器可达） | 2026-09-09 建档（DDR5 Hynix A-die 调优讨论帖核查属实）；2026-09-09 排除行同 b23.tv/firpe.cn 一并修正双反斜杠笔误 |
| www.newegg.com | 2026-09-14 起 CI runner (GitHub Actions) 访问连接超时/反爬阻断 | 2026-09-14 建档（电源选型计算文核查属实） |
| github.com blob 链接 | 2026-09-14 起 GitHub 前端对 CI runner 高并发访问 blob 页面间歇性返回 503 限流 | 2026-09-14 建档（tweakbyjie 与 karing-docu 两处 blob 文档核查属实） |
| web.archive.org (bswaterb 快照) | 2026-09-24 起 Internet Archive 历史快照回放返回 404（原站已离线，CDX 快照索引存在但回放服务不稳定） | 2026-09-25 建档（本地已复核原站离线、CDX 索引存在，教程核心原理已在正文提炼） |

**2026-08-29 备注**：当日出现跨站点批量封锁潮（tomshardware → techcommunity → asus → digitalfoundry → game-console 依次暴露），均为 403 拦爬虫性质，已按上表逐个建档；如后续 CI 仍零星暴露新域名，继续按本台账机制处理即可。

---

## 本地误报（CI 可达，**禁止**加排除）

以下域名在**本地**（中国大陆出口）被 WAF 拒绝，但 GitHub Actions runner 可正常访问，CI 检查为绿。**不要把它们加进 `lychee.toml` 的 `exclude`**——加了会让 CI 失去对这几条链接的监控，反而掩盖将来真正的死链。

| 域名 | 本地现象 | 认定为本地误报的依据 | 建档 |
| --- | --- | --- | --- |
| www.corsair.com | 3 条链接（`docs/验机相关/装机法.md` 的 140/142/147 行）稳定 403；已试 3 次重试、多种 UA（含 lychee 默认 UA）均 403 | 同一 revision 下 CI 与本地 lychee 计数**完全一致**（876 Total / 446 Unique / 131 Excluded），CI 报 0 Errors、本地报 3 Errors ⇒ 差异只可能来自出口网络；且 CI 历史上真实报过错（run 34868340301 报 1 Error），证明 CI 检查确实生效 | 2026-09-15 |

**判断方法**（区分"该加排除"与"本地误报"）：取同一 revision，比较 CI 与本地 lychee 的统计块。

- `Total` / `Unique` / `Excluded` 一致而 `Errors` 不同 → 差异只能来自网络出口，属**本地误报**，不要动 `lychee.toml`；
- CI 与本地都报同样的错误 → 按上方排除表流程建档（加 `exclude` + 本表登记）。

**本地跑检查时的免除方式**（仅为本地排查方便，不进仓库配置）：

```bash
lychee --config lychee.toml --exclude 'https://www\.corsair\.com/' "./**/*.md"
```
