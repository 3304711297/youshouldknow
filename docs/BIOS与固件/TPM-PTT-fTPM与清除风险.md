---
applies_to:
  - Windows 10
  - Windows 11
risk: high
tweak_module: []
---

# TPM/PTT/fTPM 与清除风险

> **分类**：BIOS 与固件 · 装机必改项
>
> **风险等级**：🔴 高（清除操作）。清 TPM 销毁的是密钥不是文件，但 BitLocker 密封密钥没了等于数据解不开——清除前必须备份恢复密钥。
>
> **一句话**：TPM 是主板里的"保险箱"（信任根），私钥永不出芯片；Intel 叫 PTT、AMD 叫 fTPM、独立插卡叫 discrete TPM，三者对 Windows 11 都算 TPM 2.0。

## 它管什么

TPM（Trusted Platform Module，可信平台模块）不是杀毒软件也不是加密软件，它是**信任根**，主要干四件事：

1. **生成密钥**：为系统安全提供密钥管理；
2. **内部造密钥**：在芯片内部生成加密私钥（如 RSA/ECC），私钥永不出芯片——这是硬指标，操作系统、病毒甚至拆开机箱都拿不到；
3. **度量启动完整性**：PCR（平台配置寄存器）记录启动各阶段的哈希值（"启动指纹"），任何环节被篡改 PCR 值就变；
4. **密封（Seal）**：把秘密绑死在系统状态上，状态变了就解不开。

BitLocker 加密、Windows Hello（PIN/指纹/人脸）、VBS 虚拟化安全的密钥都密封在 TPM 里——所以 Win11 把 TPM 2.0 定为强制要求（TPM 1.2 不认）。

## 三种形态

| 形态 | 位置 | 说明 |
|---|---|---|
| 独立 TPM | 主板插卡/焊芯片 | 硬件级最强，零售主板几乎不带，品牌机出厂可能有 |
| Intel PTT（Intel Platform Trust Technology） | 跑在平台固件里 | 六代酷睿起支持，BIOS 开关即启用 |
| AMD fTPM | 跑在 CPU 内的安全处理器（PSP） | AM4/AM5 平台默认方案，BIOS 开关即启用 |

**别被三个名字吓到**：对 Win11 来说三者都合规、都过检查。注意零售主板出厂开关可能默认关闭——装 Win11 前去 BIOS 确认打开；TPM 显示"未就绪"先看开关。

## AMD fTPM 卡顿大坑

2022~2024 年部分锐龙平台开启 fTPM 后，出现打字突然冻结、游戏画面定格 1~3 秒的现象——是早期固件频繁写固件芯片引发的问题，**不是硬件坏了**：去主板官网更新最新 BIOS（含平台安全处理器补丁）即可根治，别白忙活换内存。

## 清除 TPM：三个风险与铁律

**清除 = 删密钥，不删盘上文件**——盘上字节原样没动，但密钥作废后解不开，等于锁死。

1. **BitLocker 恢复密钥**：密封在 TPM 里的卷主密钥没了，下次开机索要 48 位恢复密钥；没备份（微软账户里）则数据在但解不开，等于不可接受损失；
2. **Windows Hello 凭据**：PIN、指纹、人脸全部重设；
3. **证书与授权**：依赖 TPM 的证书需重新配置。

**铁律：清 TPM 之前先备份 48 位恢复密钥（或暂停 BitLocker 保护）**。误清了别慌：用恢复密钥解锁后 BitLocker 会自动重新密封密钥到 TPM，不用重加密、全盘数据不丢。

### 三个清除入口

Windows 设置里"清除 TPM"、BIOS 里 Clear TPM 选项、或部分主板把开关关掉再开（等效清除）。注意：**清 CMOS ≠ 清 TPM**——Clear CMOS 清的是普通设置，有时顺带擦 PCR 寄存器，但不保证清掉 TPM 所有权。

### 卖二手前

正确姿势：先暂停 BitLocker 保护、备份好恢复密钥，再清 TPM——买家拿不到你的数据，你也确认了密钥清干净。

## 品牌路径参考

Intel 平台：Advanced → PCH-FW Configuration（南桥固件配置）→ PTT 设 Enabled；AMD 平台：AMD CBS / Advanced → Trusted Computing → AMD fTPM 设 Enabled。改完看变更摘要再确认，F10 保存。

## 验证

- `tpm.msc`：显示"TPM 已就绪"、规格版本 2.0；
- `msinfo32`：可信平台模块"已准备好"；
- Linux 用 tpm2 工具读取属性。
三处都对得上才算真就绪。

## 出处与核查说明

本文整理自 B 站 UP 主「所盼皆欣然」对应集，经本地语音转录校对整理；细节以原视频画面为准：

- [电脑BIOS选项全科普EP06/TPM/PTT/fTPM与清除风险（重制版）](https://www.bilibili.com/video/BV1a88c6iE6G/)
- [电脑BIOS选项全科普EP04/安全启动与TPM（旧版）](https://www.bilibili.com/video/BV1ta5F6HED9/)
- 相关：[Secure Boot 安全启动与密钥管理](./SecureBoot安全启动与密钥管理.md)、[BIOS 恢复默认设置的三种方法](./BIOS恢复默认设置的三种方法.md)
