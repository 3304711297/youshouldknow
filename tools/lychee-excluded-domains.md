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
