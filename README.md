# YouShouldKnow

Windows 系统、硬件、游戏性能与日常使用知识库（中文）。

- **在线阅读**：<https://3304711297.github.io/youshouldknow/>
- 全部内容位于 [`docs/`](./docs/)，按 13 个分类组织；站点由 MkDocs Material 构建，推送 main 后自动发布
- 与姊妹仓库 [tweakbyjie](https://github.com/3304711297/tweakbyjie)（PowerShell 优化工具集）联动：`docs/项目导航/` 下的映射与执行参考把知识条目对应到脚本的实际执行项，并由 tweak 仓库的 Coverage 审计保证两边清单一致

## 本地开发

```bash
pip install -r requirements-docs.txt
mkdocs serve   # 实时预览
```
