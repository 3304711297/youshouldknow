---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# Windows 激活与数字许可证验机指南

## 检查位置

设置 → 系统 → 激活

检查：

- Windows 是否已激活；
- Windows 版本是否正确；
- 是否存在数字许可证。

## 命令检查

管理员 CMD：

```cmd
slmgr /dli
slmgr /dlv
slmgr /xpr
```

## 常见许可证类型

### OEM

通常绑定设备主板，常见于品牌机和预装系统。

### Retail

零售许可证，可根据微软规则转移。

### Volume

批量授权，主要用于组织环境。

## 验机注意

激活状态正常并不代表硬件一定全新。

新机验收还需要结合：

- SSD 健康状态；
- 通电时间；
- 驱动状态；
- BIOS 信息；
- 硬件检测结果。

Windows 激活检查只是验机的一部分。
## 事实核查记录

核验基准：微软官方 slmgr 文档与许可类型公开资料（2026-08-29 重核：微软 Learn《Slmgr.vbs Options》页面在线核验通过，/dli、/dlv、/xpr 选项记载一致；OEM/Retail/Volume 许可类型机制未变化）。

| 声明 | 核查结果 |
| --- | --- |
| 设置→系统→激活 为激活状态检查入口；slmgr /dli、/dlv、/xpr 为标准查询命令 | ✅ 属实：微软 slmgr.vbs 官方文档记载 |
| OEM 绑定设备主板、Retail 可按微软规则转移、Volume 用于组织批量授权 | ✅ 属实：与微软许可类型公开说明一致 |
| 激活状态正常不代表硬件全新 | ✅ 判断合理：激活只反映许可证与硬件指纹绑定关系，与使用时长无关 |
