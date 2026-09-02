---
applies_to:
  - Windows 10
  - Windows 11
risk: medium
tweak_module: []
---

# Secure Boot 安全启动与密钥管理

> **分类**：BIOS 与固件 · 装机必改项
>
> **一句话**：Secure Boot 只管一件事——通电开机那一瞬间，谁有资格让系统跑起来。它不杀毒、不管你的 exe 文件，把"开启开关"当成全部是大错特错：生效要三件事共同决定（开关、密钥库状态、模式）。

## 它是什么

- Secure Boot 是 UEFI 固件的安保验证机制：启动时逐层验证引导加载程序等启动组件的数字签名，只放行签名合法的，未签名的全部剔除，防止 Black Lotus 这类 Bootkit 在 Windows 启动前劫持。
- 它**不是杀毒软件**：下班很早，控制权交给 Windows 后任务就结束，运行时防护是 Defender 的活。
- Win10 时代多数主板已强制支持；Win11 强制要求，且有三道门槛：**纯 UEFI 启动、CSM 彻底关闭、系统盘为 GPT 分区表**（见[UEFI、Legacy 与 CSM](./UEFI-Legacy-CSM与分区表.md)）。

## 密钥体系与两种模式

四把钥匙组成信任链（不用手动逐把管理，各厂商都有一键导入出厂默认密钥）：

| 密钥 | 角色 |
|---|---|
| PK（平台密钥） | 最高权限的"大老板"，后续钥匙都得它授权 |
| KEK（密钥交换密钥） | 中间代理，管理签名数据库 |
| db（签名数据库/白名单） | 微软、主板厂商等允许启动的签名 |
| dbx（吊销数据库/黑名单） | 被黑客利用或出漏洞的签名拉黑拦截 |

**部署（Setup）模式 ≠ 开启**：部署模式下门禁开了但名单被清空，保安不知道该拦谁，全部放行——Windows 安装程序照样判定"不支持"。必须把密钥导入、转为用户模式才算真开启。

## 三个典型症状

1. **装 Win11 报"不支持安全启动"**：安装程序不看界面开关，直接查底层状态——部署模式或 CSM 开着都会判定失败。解法：关 CSM → 找 Restore Factory Keys / Install Default Secure Boot Keys 导入出厂密钥转用户模式 → 开关设 Enabled。
2. **官方 U 盘装 Win11 第一轮重启无限循环，报 Invalid Signature Detected**：微软旧签名证书（2011 年签发）已过期，Win11 官方更新与安装介质改用 2023 新版证书，很多现售主板的 BIOS 密钥白名单还没收录。解法：更新主板 BIOS；或先临时把 Secure Boot 设 Disabled 装好系统、立刻打全 Windows Update 补丁（新证书会自动下发）并更新 BIOS，再回 BIOS 重新开启。
3. **开机索要 BitLocker 恢复密钥**：清空或关闭 Secure Boot 会改变启动环境测量值，BitLocker 判定启动环境不安全变更，100% 触发 48 位恢复密钥输入。**操作前先去微软账户确认已备份恢复密钥**。

## Linux 与老 PE

- Ubuntu/Fedora/Debian 等主流发行版使用微软签名的 shim 引导器，Secure Boot 开着直接装，什么也不用动；
- 未签名的古董 PE/维护盘会被拦截（Security Violation）：临时关掉，用完再开。

## 品牌路径参考

- 华硕：Advanced/Boot → Secure Boot 菜单（含 Key Management）；
- 微星：Settings → 高级/安全下的 Secure Boot，点 Key Management 操作；
- 技嘉：Settings/BIOS → Secure Boot → Install Default Secure Boot Keys；
- 华擎：Security → Secure Boot。

## 验证与恢复

- 验证：Win+R 输入 `msinfo32`，"安全启动状态"写"开启"即成功。
- 误改后开机报 Invalid Signature Detected：狂按 Del 进 BIOS → Load Optimized Defaults（会把安全密钥一起重置，重新导入默认密钥即可）；一般不会造成数据丢失，只是暂时找不到启动路径。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」对应集，经本地语音转录校对整理；证书时间线与品牌路径等细节以原视频画面为准：

- [电脑BIOS选项全科普EP05/Secure Boot 与密钥管理（重制版）](https://www.bilibili.com/video/BV1fG8H6BEqm/)
- [电脑BIOS选项全科普EP04/安全启动与TPM（旧版）](https://www.bilibili.com/video/BV1ta5F6HED9/)
- 相关：[TPM/PTT/fTPM 与清除风险](./TPM-PTT-fTPM与清除风险.md)
