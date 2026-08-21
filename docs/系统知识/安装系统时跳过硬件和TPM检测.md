# 安装系统时跳过硬件和 TPM 检测

> **分类**：系统知识 · 系统安装
>
> **适用场景**：在老电脑、无 TPM 模块或 CPU 不在支持列表的设备上安装 Windows 11 时，绕过安装程序的硬件兼容性检测（TPM 2.0 / 安全启动 / CPU / 内存）。
>
> 本文方法已对照多家科技媒体与微软社区信源交叉验证，核查记录见文末。

---

## 背景

Windows 11 安装程序会检查 TPM 2.0、安全启动（Secure Boot）、受支持 CPU 列表与内存容量，不满足则直接提示「该电脑无法运行 Windows 11」并中止安装。绕过方式有两类：用 PE 环境直接部署镜像（不经过安装程序的硬件检查），或在安装程序内用注册表关闭各项检查。

## 方案一：PE 部署安装（推荐）

工具链：**Ventoy**（多合一启动盘）→ **FirPE**（PE 维护系统）→ **Dism++ / EasyRC**（镜像部署工具）。

1. 用 Ventoy 制作启动 U 盘，放入 FirPE 的 PE 镜像与 Windows 系统镜像；
2. 从 U 盘启动进入 FirPE；
3. 用 Dism++ 或 EasyRC 选择系统镜像（WIM/ESD/ISO），指定引导分区与系统分区后直接部署。

**原理**：DISM 部署是把镜像直接展开到磁盘分区，完全绕过 `setup.exe` 的硬件检测环节，老主板也畅通无阻。

> EasyRC 为免费一键装机工具，FirPE 官方提供图文教程；Dism++ 同为常用部署/维护工具，两者皆可。

## 方案二：LabConfig 注册表（安装程序内绕过）

适用于直接用微软原版 ISO 的 USB 安装盘装系统（方案一行不通、或目标机是不支持 TPM 的老主板）：

1. 安装程序进入**版本选择页面**时按 `Shift + F10`，弹出命令提示符；
2. 输入 `regedit` 回车，打开注册表编辑器；
3. 定位到：

   ```text
   HKEY_LOCAL_MACHINE\SYSTEM\Setup
   ```

4. 在 `Setup` 下新建项，命名为 `LabConfig`；
5. 在 `LabConfig` 中新建四个 **DWORD (32 位) 值**：

   | 数值名称 | 绕过的检查项 |
   | --- | --- |
   | `BypassTPMCheck` | TPM 2.0 检查 |
   | `BypassSecureBootCheck` | 安全启动检查 |
   | `BypassRAMCheck` | 内存容量检查 |
   | `BypassCPUCheck` | CPU 型号检查 |

6. 将四个值的数值数据全部设为 `1`（十六进制），关闭窗口继续安装，硬件检测即被跳过。

> 📌 补充：如需同时绕过存储空间（64GB）检查，可再加一个同类型的 `BypassStorageCheck` = 1。
>
> 📌 另一路线：**已装好系统、仅想原地升级**（如 Win10 → Win11）时，用的是另一个键——`HKLM\SYSTEM\Setup\MoSetup` 下新建 DWORD 值 `AllowUpgradesWithUnsupportedTPMOrCPU` = 1，与本文的 LabConfig（全新安装场景）适用时机不同。

## ⚠️ 风险提示

微软明确表示在不受支持的硬件上运行 Windows 11 可能出现兼容性问题，且此类设备不保证能收到后续更新（包括安全更新）。绕过检测属于自行承担风险的行为，老设备建议优先考虑继续使用受支持的系统版本。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| LabConfig 四项 DWORD（BypassTPMCheck / BypassSecureBootCheck / BypassRAMCheck / BypassCPUCheck = 1）可绕过安装检测 | ✅ 属实：Tom's Hardware、StarWind、Microsoft Tech Community 等多家信源记载的同一标准方法 |
| 操作位置：版本选择页 `Shift+F10` → `regedit` → `HKLM\SYSTEM\Setup` 下新建 `LabConfig` | ✅ 属实：各教程路径一致，DWORD (32 位)、数值 1（十六进制）均正确 |
| Ventoy / FirPE / Dism++ / EasyRC 工具链真实可用 | ✅ 属实：均为社区广泛使用的免费工具，EasyRC 有 FirPE 官方图文教程及大量演示视频 |
| PE 内 DISM 部署不经过安装程序硬件检测 | ✅ 属实：DISM 直接展开镜像到分区，不运行 setup 硬件检查环节 |
| BypassStorageCheck（补充项）与 MoSetup\AllowUpgradesWithUnsupportedTPMOrCPU（升级路线） | ✅ 属实：均为社区与微软问答文档记载的既有键值 |
| 不受支持硬件可能收不到更新 | ✅ 属实：微软官方对最低要求外设备的声明口径 |

**参考来源：**

- [Tom's Hardware — How to Bypass Windows 11's TPM, CPU and RAM Requirements](https://www.tomshardware.com/how-to/bypass-windows-11-tpm-requirement)
- [StarWind Software — Bypass TPM and Install Windows 11 on Unsupported Hardware](https://www.starwindsoftware.com/blog/bypass-tpm-and-install-windows-11-on-unsupported-hardware/)
- [Microsoft Tech Community — Bypass Windows 11 system requirements during installation](https://techcommunity.microsoft.com/discussions/windows11/how-to-bypass-windows-11-system-requirements-during-installation-on-an-old-lapto/4060758)
- [Microsoft Learn Q&A — Install Windows 11 without Secure Boot](https://learn.microsoft.com/en-us/answers/questions/2121461/install-windows-11-without-secure-boot-on-an-unsup)
- [FirPE Project — 如何在 PE 内使用 EasyRC 安装系统](https://firpe.cn/page-554)
- [Ventoy 官网](https://www.ventoy.net)
