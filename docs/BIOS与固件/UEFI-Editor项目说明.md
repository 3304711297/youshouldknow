# UEFI Editor 项目说明

> **分类**：BIOS 与固件 · 外部工具参考
>
> **风险等级**：🔴 极高风险
>
> 本文只说明开源项目的能力、流程和限制，不下载、打包或运行其中的工具，也不提供修改后的 BIOS 镜像。

## 项目是什么

[ BoringBoredom/UEFI-Editor ](https://github.com/BoringBoredom/UEFI-Editor) 是一个面向 Aptio V/AMI UEFI 固件的网页编辑器，项目定位接近开源的 AMIBCP 替代方向。

在线页面：<https://boringboredom.github.io/UEFI-Editor/>

它主要帮助用户分析和修改 BIOS 镜像中的设置表单、隐藏条件和访问级别。它不是 BIOS 读取器、刷写器、签名绕过工具，也不是主板救砖工具。

## 官方 README 体现的配套工具

项目说明的典型流程需要多个工具配合：

- [UEFITool NE](https://github.com/LongSoft/UEFITool/releases)：打开 BIOS、搜索和提取固件区域；
- [UEFITool 0.28.0](https://github.com/LongSoft/UEFITool/releases/tag/0.28.0)：按项目说明将修改后的文件替换回镜像；
- [IFRExtractor-RS](https://github.com/LongSoft/IFRExtractor-RS/releases)：把提取出的 PE32/Setup 内容转换为可读的 IFR 信息；
- UEFI Editor：上传相关文件，在网页界面中查看表单、导航和修改选项。

工具版本和固件结构需要匹配。项目没有正式 Release 标签，使用前应查看仓库当前 README、提交和依赖状态，并自行验证下载来源。

## 镜像编辑流程概念

项目 README 给出的流程可以概括为：

1. 使用 UEFITool NE 打开**当前设备对应版本**的 BIOS 镜像；
2. 搜索目标设置，定位 `Setup/PE32 image section`；
3. 提取 PE32 section；
4. 用 IFRExtractor-RS 转换提取结果；
5. 提取 `AMITSE` 和 `setupdata` 等相关文件；
6. 将所需文件上传到 UEFI Editor；
7. 在 GUI 中分析 Form、设置项和隐藏条件；
8. 下载修改后的文件和变更日志；
9. 使用 UEFITool 按原类型回填，区分 `Replace as is` 与 `Replace body`；
10. 保存为新镜像，保留原始镜像不被覆盖。

这套流程只描述“如何编辑镜像中的内容”，没有证明修改后的镜像能够被某一台主板接受或正常启动。

## 关键概念

### Setup、Form 和引用

BIOS 设置通常由多个 Form 和引用关系组成。顶层引用、父级 Form 或菜单入口不完整时，单独修改一个子项可能不会显示或不会真正生效。

### Suppress If

`Suppress If` 条件可以控制嵌套设置是否隐藏。项目 README 提醒：看到该操作码不一定代表当前条件已生效，错误解除父级条件可能造成菜单异常。

### Access Level

`Access Level` 是另一种控制设置可见性的方式。项目说明提到某些固件中 `05` 可能有效，但数值并不是跨固件通用标准；不同主板必须以自身结构和测试结果为准。

项目还提醒，不要不加判断地同时使用多种可见性修改方式，因为不同 UEFI 的行为不同。

### Setup、VarStore、VarOffset 和 Size

当使用 IFR 输出或 UEFI Shell 变量方式时，需要确认：

- 哪个 `Setup` 区域实际生效；
- `VarStoreName` 和 `VarStoreId` 是否对应；
- `VarOffset` 是否属于当前 BIOS 版本；
- `Size` 的单位和数值是否正确；
- 修改前后的变量值是否符合当前设备的定义。

不同 BIOS 版本可能改变结构和偏移。不能把别人的 `VarOffset`、`VarStore` 或命令直接套到另一台机器。

## 不刷修改版 BIOS 的另一条路线

项目 README 还介绍了通过 UEFI Shell 和 `grub-mod-setup_var` 修改变量的路线：

- 准备 FAT32 U 盘；
- 将 Shell 文件放到 `EFI/BOOT/BOOTX64.EFI`；
- 读取当前 BIOS 版本对应的 IFR 输出；
- 使用 `setup_var_cv` 读取或写入指定变量。

命令形式类似：

```text
setup_var_cv VarStoreName VarOffset Size Value
```

这条路线不一定需要刷入完整修改版 BIOS，但它仍然直接修改 UEFI 变量，可能导致设置错误、无法启动或需要清除 CMOS。它不是低风险方案，也不是所有固件都支持。

项目 README 的示例还提醒，遇到异常时可能需要强制关机并重置 CMOS；这不等于完整恢复方案。执行前仍应有官方恢复路径和硬件级维修后备方案。

## 重要限制

UEFI Editor 不能替你完成以下事情：

- 判断你的主板是否支持该修改；
- 读取或写入 BIOS 芯片；
- 绕过厂商签名、完整性校验或写保护；
- 生成适用于所有平台的通用 BIOS；
- 保证修改后的镜像可以启动；
- 提供 BIOS Flashback、SPI 编程器或售后级救砖能力；
- 恢复被破坏的原始固件状态。

项目 README 还明确提到：有多个 Setup 区域时，需要确认哪个区域和实际 BIOS 设置匹配；不同 BIOS 版本之间不能随意混用提取文件和偏移。

## 与刷写流程的关系

必须把以下三个阶段分开：

```text
读取/提取 BIOS
    ↓
编辑 BIOS 镜像或 UEFI 变量
    ↓
通过官方更新、Flashback、FPT 或编程器写入
```

UEFI Editor 主要位于第二阶段。即使编辑器成功导出文件，也不代表第三阶段安全可行。尤其是华硕等具有严格校验的主板，普通方式可能拒绝修改后的镜像，可能需要官方 Flashback 或专业编程器；具体以主板文档为准。

## 安全使用原则

- 只处理当前设备和当前 BIOS 版本的文件；
- 保存完整原始镜像、原始模块和修改前设置；
- 修改前确认官方 BIOS Recovery、Flashback、编程器或售后路径；
- 不覆盖原始备份，不使用来源不明的 BIOS 镜像；
- 不因“网页能打开文件”就继续刷写；
- 不在生产设备、公司受管设备或唯一工作电脑上尝试；
- 任何无法确认的 Form、变量、偏移或替换类型都应停止。

## 参考链接

- [UEFI-Editor GitHub 仓库](https://github.com/BoringBoredom/UEFI-Editor)
- [UEFI-Editor 在线页面](https://boringboredom.github.io/UEFI-Editor/)
- [UEFITool 项目](https://github.com/LongSoft/UEFITool)
- [IFRExtractor-RS 项目](https://github.com/LongSoft/IFRExtractor-RS)
- [BIOS 与 UEFI 固件刷写及开机 Logo 修改指南](./BIOS与UEFI固件刷写及开机Logo修改指南.md)

## 与 tweakbyjie 的边界

UEFI Editor 和 BIOS 固件修改不属于 `tweakbyjie` 的 Windows 优化执行范围。不要把固件镜像编辑、UEFI 变量写入或刷 BIOS 功能加入 PowerShell 优化菜单。

## 事实核查记录

核验基准：UEFI-Editor 上游项目资料与 UEFI Setup 规范概念（2026-08-29 重核：BoringBoredom/UEFI-Editor 仓库仍存在且截至当日仍无正式 Release 标签，在线页面 boringboredom.github.io/UEFI-Editor 可正常访问；配套工具链接均有效——UEFITool NE 仍在维护（最新 A75，2026-07-10 发布）、UEFITool 0.28.0 标签存在、IFRExtractor-RS 最新 v1.6.1（2026-03-11 发布））。

| 声明 | 核查结果 |
| --- | --- |
| Setup/Form/Suppress If/Access Level/VarStore/VarOffset 为 UEFI Setup 的真实概念 | ✅ 属实：与 EDK2/UEFI 规范术语一致 |
| 项目功能与配套工具描述 | ⚠️ 以上游 README 为准，随项目版本演进可能变化（2026-08-29 重核：仓库在线、README 流程描述未变，无正式 Release） |
| 不刷修改版 BIOS 也可用 VarStore/Shell 变量方式调整部分选项 | ⚠️ 社区路线，可行性依机型固件而异 |
