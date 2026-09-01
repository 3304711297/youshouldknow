---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# 验机相关

Windows 安装、OOBE / Audit Mode、激活与装机检查的知识分类。

## 文章

- [Windows 审核模式 AuditMode 与 OOBE](./Windows审核模式_AuditMode与OOBE.md) — 审核模式的进入、用途与 OOBE 状态的边界
- [Windows 11 跳过联网激活并创建本地账户](./Windows-11-跳过联网激活并创建本地账户.md) — OOBE 阶段跳过联网与本地账户创建
- [Windows 激活与数字许可证验机指南](./Windows激活与数字许可证验机指南.md) — 激活状态、`slmgr` 与数字许可证核验
- [装机法](./装机法.md) — 42 条装机守则与事实核查（最小系统/散热/内存/电源/运输）

## 建议阅读顺序

```text
Windows 安装 → OOBE/AuditMode → 跳过联网/本地账户 → 激活核验 → 装机法查漏
```

1. 先读 [AuditMode 与 OOBE](./Windows审核模式_AuditMode与OOBE.md) 理清审核模式与 OOBE 状态的边界；
2. 需要跳过联网时，查 [跳过联网](./Windows-11-跳过联网激活并创建本地账户.md)；
3. 再用 [激活指南](./Windows激活与数字许可证验机指南.md) 核验数字许可证；
4. 装机与运输前，用 [装机法](./装机法.md) 做清单式查漏。

## 与其他分类的边界

- `BIOS与固件/`：固件刷写与 Logo 修改的高风险操作；`验机相关/` 负责装机与系统初始化阶段。
- `系统知识/`：装好系统后的日常设置与排障；`验机相关/` 聚焦首次开机与验收。
