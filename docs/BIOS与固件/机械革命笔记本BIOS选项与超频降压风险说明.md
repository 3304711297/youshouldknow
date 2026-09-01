---
applies_to:
  - Windows 11
  - 机械革命/同方模具笔电
risk: high
tweak_module: []
---

# 机械革命笔记本 BIOS 选项与超频降压风险说明

> **分类**：BIOS 与固件 · 笔记本平台调校
>
> **风险等级**：🔴 高风险。本文整理机械革命/同方类笔记本 BIOS 菜单的个案经验，不是通用优化清单。
>
> **适用前提**：必须确认完整机型、CPU、BIOS/EC 版本、控制中心版本和实际菜单结构。菜单名称相同，不代表不同机型的含义、默认值和可接受范围相同。

## 先说结论

下面的路径和选项来自用户提供的个案，常见于部分 Intel 移动平台的 OEM BIOS。它们不是 Intel 或 Windows 的统一标准。

- AMD 平台不适用 Intel E-core、IA/GT CEP、IA ICCMAX 等路径；
- 不同 CPU 世代、SKU、微码和 OEM BIOS 可能没有这些选项；
- BIOS 中能看到某个开关，不等于平台支持或修改后一定安全；
- “能进入系统”不等于稳定，必须验证冷启动、重启、睡眠、负载、WHEA 和实际性能；
- 超频/降压前应保存 BIOS 设置截图、创建系统恢复方案，并准备恢复默认值或官方 BIOS/EC Recovery；
- 本文不提供一键修改工具，也不建议把这些操作加入 `tweakbyjie` 自动优化脚本。

## 一、风险分组

| 分组 | 例子 | 主要风险 |
|---|---|---|
| 显示路径 | `dGPU Only` | 功耗、内屏/外接口、睡眠和混合显卡兼容性变化 |
| CPU 资源 | E-core、Hyper-Threading、C-state | 功耗、线程调度、性能、续航和应用兼容性变化 |
| 电压/电流 | Overclocking Lock、Undervolt Protection、CEP、ICCMAX、AC/DC Loadline | 蓝屏、WHEA、性能下降、过热、VRM 负载和不可启动 |
| 内存 | Warm Boot Test、Power Down Mode、Memory Configuration | 训练失败、黑屏、数据错误、冷启动/睡眠不稳定 |
| 安全 | VBS/HVCI、TPM/PTT、Secure Boot | BitLocker、Windows 11、凭据、驱动和安全边界受影响 |
| 平台链路 | xDCI、DMI Link Speed | USB 设备角色、芯片组链路、兼容性和性能变化 |

## 二、进入高级 BIOS 的前置条件

部分控制中心的自定义模式可能提供 `CPU Performance Menu` 或“高级 BIOS”开关。若你的机型没有该入口，不要为了显示菜单而随意修改注册表或刷入其他机型的控制中心。

控制中心开关只可能改变界面或解锁入口，不会凭空增加 BIOS、CPU、VRM 或 EC 的能力。任何高级菜单操作都应先确认官方机型资料、当前 BIOS/EC 版本和恢复方法。

## 三、显示路径：dGPU Only / 独显直连

可能的菜单示例：

```text
Advanced → Switchable Graphics → Display Mode → dGPU Only
```

### 作用与边界

`dGPU Only` 通常是 OEM 对 MUX/独显直连路径的命名：内屏或部分输出可能绕过混合显卡路径，直接由独显输出。它不是 Intel 通用 BIOS 标准，是否存在、对哪些接口生效、是否需要重启，完全依赖机型。

### 可能收益和代价

- 游戏渲染路径可能更直接，部分场景的帧时间或延迟可能改善；
- 不等于核显从系统中完全消失；
- 待机功耗、发热和续航可能变差；
- 外接显示器、内屏、睡眠、视频硬解和混合显卡切换可能变化。

修改前记录原模式，修改后分别测试电池、外接显示器、睡眠/唤醒和游戏；出现黑屏时优先按本机官方方式恢复混合显卡或 BIOS 默认值。

## 四、E-core、超线程与 CPU 资源

### 1. Active Efficient-cores = 0

可能的菜单示例：

```text
Advanced → CPU Configuration → Active Efficient-cores → 0
```

在支持该选项的 Intel 混合架构平台上，`0` 通常表示不启用 E-core，但是否允许该值、是否需要重启、BIOS 是否真正应用，取决于 CPU、微码和固件。

不要把它写成“关闭小核会丢失小核缓存”。更准确的说法是：禁用 E-core 会改变可用核心数量、线程调度和缓存/拓扑资源，具体缓存可用量和行为应以该平台拓扑和实测为准。

Intel i9-12900K 的官方规格可作为代际示例：8 个 P-core、8 个 E-core、16 核 24 线程、14MB L2 和 30MB Smart Cache。该代 E-core 不提供 Hyper-Threading，但不能把这个结论跨代套用到所有混合架构 CPU。

### 2. Hyper-Threading

可能的菜单示例：

```text
Advanced → CPU Configuration → Hyper Threading → Disabled
```

E-core 与 P-core 的 Hyper-Threading 不是互相替代的同一开关：该代 Intel E-core 通常没有 HT，而 P-core 的 HT 是独立线程能力。关闭 HT 会减少可见线程数，可能降低部分并行工作负载性能，也可能改变少数延迟敏感应用的行为。

“6 个大核及以下不要关闭超线程”不是通用技术规则。是否值得关闭，应根据应用线程数、功耗、温度、延迟目标和实测结果决定；笔记本还要考虑续航和风扇噪声。

### 3. 分簇禁用 E-core

可能的菜单示例：

```text
Advanced → Overclocking Performance Menu → Processor
→ Per Core Disable Configuration → Enabled
→ Processor Disable
```

原始个案把 `0–7` 视为大核、`8–15` 视为小核，并建议按簇关闭部分 E-core。这个编号只适用于特定平台和 BIOS，不能复制到其他 CPU。执行前必须确认 BIOS 对编号、簇大小和核心拓扑的定义。

## 五、电压、电流与保护机制

### 1. Overclocking Lock / Undervolt Protection

可能的菜单示例：

```text
Advanced → Power & Performance → CPU - Power Management Control
→ CPU Lock Configuration → Overclocking Lock → Disabled

Advanced → Overclocking Performance Menu → Overclocking Feature → Enabled
→ Undervolt Protection → Disabled
```

这些标签在部分 Intel/OEM 平台中确实存在，但不能概括为“关闭后所有电压和功耗限制都解锁”：

- CPU 是否支持超频取决于 SKU、芯片组、微码和 OEM BIOS；
- Undervolt Protection 可能限制负电压偏移或电压下限，但作用域依实现不同；
- 电压保护与超频锁不是同一个机制；
- 关闭保护可能扩大不稳定、过热或安全风险。

Intel 的电压保护资料可用于理解背景，但不能证明某个机械革命 BIOS 标签一定具有相同实现。优先使用厂商 BIOS、CPU 型号和工具的官方说明。

### 2. CEP（Current Excursion Protection）

可能的菜单示例：

```text
CEP Disable → IA CEP Enable / GT CEP Enable → Disabled
```

CEP 是处理器/平台的电流、电压异常保护机制，可能在检测到模型异常时触发限制或降频。它不是简单的 ICCMAX，也不是“关闭后必然提升性能”的开关。

IA 通常指 CPU 核心域，GT 通常指核显域；GT CEP 不等于独显保护。是否有 IA/GT CEP 开关、关闭后是否影响性能、稳定性或保护边界，必须由具体平台验证。

不要把“禁用 CEP + 手动降压”写成正确答案。它最多是高风险实验方向，必须同时观察性能、温度、功耗、WHEA 事件、蓝屏和长时间稳定性。

### 3. IA ICCMAX / IA ICC Unlimited

可能的菜单示例：

```text
Advanced → Overclocking Performance Menu
→ VR ICCMAX Current Override → IA ICC Unlimited Mode
```

“Unlimited”通常意味着将 CPU 核心域的电流上限写到较高编码或取消某一软件限流，不是物理无限，也不等于解除 PL1/PL2、温度墙、VRM 保护或电源适配器限制。

GT/核显域的电流设置只针对核显，不应当当成独显电流解锁。应保留核显电流保护，并以平台规格和稳定性验证为准，不使用跨机型的固定数值。

### 4. AC/DC Loadline

可能的菜单示例：

```text
Advanced → Power & Performance → CPU Power Management Control
→ CPU VR Settings → Core/IA VR Settings → AC Loadline
→ GT VR Settings → AC/DC Loadline
```

AC loadline 通常参与按电流估算和请求 VID，DC loadline 通常参与电压/电流/功耗遥测校准。实际单位、VRM LLC、CEP 互动和可调范围由平台决定。

不能笼统地说“数值越低越好”，也不能把个案中的 `50`、`110` 当作通用答案。DC 与实际负载线不匹配可能造成功耗/电流报告失真、错误限功耗、CEP 触发或稳定性异常。

调整后应同时比较实际核心电压、CPU Package Power、频率、温度、性能分数和 WHEA 事件。出现性能下降时，不能只看温度判断降压成功。

## 六、TVB、VBS 与 C-states

### 1. Thermal Velocity Boost（TVB）

TVB 是在温度、功耗和电流等条件有余量时的机会性加频，不是固定超频档，也不能保证打开后增加某个固定 MHz。是否支持 TVB 以及 BIOS 中是否有对应开关，取决于 CPU SKU 和代际。

可能的菜单示例：

```text
Advanced → Overclocking Performance Menu → Processor
→ Thermal Velocity Boost → Disabled
→ TVB Voltage Optimizations → Disabled
→ Enhanced Thermal Velocity Boost → Disabled
```

关闭这些选项可能影响峰值频率、温度和功耗行为，不应为了让某个降压软件工作就盲目关闭。先确认工具、CPU 和 BIOS 的官方要求，再决定是否测试。

### 2. VBS/HVCI

Windows 11 24H2 或更高版本是否启用 VBS/HVCI，应在 Windows 安全中心和系统信息中确认，不能只根据 BIOS 菜单判断。VBS 使用硬件虚拟化和 Windows Hypervisor 隔离安全环境，HVCI 是相关的代码完整性保护功能。

关闭“内核隔离/内存完整性”可能影响驱动安全、凭据保护、WSL2、Docker、虚拟机和企业策略。不要把关闭 VBS 写成降压的默认前置条件；只有在确认工具确实有此要求、理解安全代价并准备恢复方案时，才进行独立测试。

### 3. C-states 与 C1E

可能的菜单示例：

```text
Advanced → Power & Performance → CPU Power Management Control
→ C-States → Enhanced C1E → Disabled
```

C1E 是增强的 C1 空闲状态选项，不等同于关闭所有 C2/C6 等更深层 C-state。关闭后可能减少某些唤醒延迟，但也可能增加空闲功耗、温度和笔记本续航损失；现代待机还涉及操作系统、电源计划、驱动和平台协作。

不要把 C1E 关闭当成普遍性能优化。只有在存在可重复的电源状态切换、延迟或稳定性问题时，才适合做 A/B 测试。

## 七、内存选项与超频

### 1. Warm Boot Test 与 Power Down Mode

可能的菜单示例：

```text
Chipset → System Agent (SA) Configuration
→ Memory Configuration
→ Memory Test On Warm Boot → Disabled
→ Power Down Mode → No Power Down
```

`Memory Test On Warm Boot` 不是 Intel/UEFI 统一标准名称，可能影响暖重启后的内存检测、训练或快速启动策略。不能简单断言关闭它只会节省时间。

`Power Down Mode` 通常指 DRAM 的低功耗状态，不是整机断电，也不是 CPU C-state。关闭它可能改变空闲功耗、退出延迟和稳定性，具体取决于 DDR 世代、内存条、IMC 和 BIOS。

如果 BIOS 提示必须先保存、进系统、再重启进入 BIOS 才能继续调整，这是该机型的训练/保存流程提示。应遵守机型说明，不要把它推广成所有主板的固定规则。

### 2. Memory Configuration

内存频率、时序、电压和 Gear/训练选项必须以当前内存颗粒、SO-DIMM、IMC 和 BIOS 支持为准。不要直接照抄桌面 AM5、Intel 台式机或其他笔记本的作业。

内存稳定性至少需要覆盖：

- 多轮内存测试；
- 冷启动、重启和睡眠唤醒；
- 长时间游戏或生产负载；
- Windows 事件日志和 WHEA；
- 黑屏、自动回退和数据错误。

“能进系统”不是稳定标准。出现训练失败时，优先等待平台的自动回退/训练流程；不要连续强制断电。

### 3. 控制台注册表开关

个案提到：

```text
HKEY_LOCAL_MACHINE\SOFTWARE\OEM\GamingCenter2\ItemSupport
CPUPerfomanceAndOverClockMenuSupport = 0
```

该类 OEM 注册表值不是 Windows 通用接口，名称本身还可能因版本存在拼写差异。修改前应导出目标键、记录原值并确认控制中心版本；优先使用控制中心自带的高级 BIOS 开关或旧版官方控制台，不要把注册表改值当成通用超频方案。

修改注册表只可能改变控制台界面显示，不会凭空增加 BIOS 能力，也不会解除 CPU、微码、VRM 或 OEM 固件限制。

## 八、TPM/PTT、xDCI 与 DMI

### 1. TPM/PTT

可能的菜单示例：

```text
Advanced → PCH FW Configuration → PTT Configuration
→ TPM Device Selection → Disabled
```

Intel PTT 是固件 TPM 实现，Windows 可以把它作为 TPM 2.0 使用。关闭或清除 TPM/PTT 不是性能优化默认项，可能影响 BitLocker、Windows 11、Windows Hello、凭据保护和 Secure Boot 测量。

如果必须修改，先保存 BitLocker 恢复密钥，并区分“禁用 TPM 设备”和“清除 TPM 密钥”这两个完全不同的操作。

### 2. xDCI

可能的菜单示例：

```text
Chipset → PCH IO Configuration → USB Configuration → xDCI Support
```

xDCI 通常与 USB device/gadget 控制器能力相关，使平台在特定场景下充当 USB 设备；它不是普通 USB 速度开关，也不等于 USB 调试。某些设备需要该能力，某些设备可能完全不使用它。

“把 USB Configuration 全部设为 Enabled 能改善接口失效”只能作为特定机型排障经验，不能保证有效。修改前应确认哪个端口、设备或启动流程受影响。

### 3. DMI Max Link Speed

可能的菜单示例：

```text
Chipset → DMI/OPI Configuration → DMI Max Link Speed
```

DMI 是 CPU 与 PCH/芯片组之间的互联，不是独显 PCIe 链路。把 DMI 从 Gen4 降到 Gen3 可能降低互联能力，也可能用于某些平台的兼容性排障，但“必然改善南桥温度”没有通用证据，不应当作为普遍优化。

Intel Z690/B660 等平台资料列出 DMI 4.0 和不同的通道数，说明 DMI 代际、通道数和实际 BIOS 选项由平台决定。修改后必须验证存储、USB、网卡、扩展设备和温度，不能只看某个传感器数值。

## 九、稳定性测试与记录

### CPU 降压/超频

每次只改一个变量，记录 BIOS 选项、原值和新值、核心/缓存/核显电压、频率、温度、Package Power、性能分数和 WHEA 事件。

可以使用熟悉的 CPU 负载测试（例如 Cinebench R15/R23），但单次跑分不能证明稳定。应加入长时间负载、冷启动和日常应用测试。

### 内存超频

可使用 TM5 等内存稳定性工具，但配置文件、测试轮数和错误归因属于平台/社区经验，不能把某个预设当作官方标准。出现任何错误都应回滚频率、时序或电压，并检查 WHEA 和文件完整性。

### 回滚原则

- 每次只修改一个选项；
- 修改前截图和记录原值；
- 保存 BIOS Profile（若机型支持）；
- 出现 WHEA、性能下降、随机重启、黑屏或训练失败，立即恢复上一次稳定配置；
- 不连续强制断电，不把 `Ctrl+B`、`Fn+D` 等组合键当作通用恢复按键；
- 恢复键、CMOS/EC 清除和 BIOS Recovery 必须查当前机型官方手册。

## 十、事实核查记录

| 说法 | 结论 | 说明 |
|---|---|---|
| `dGPU Only` 是独显直连路径 | ⚠️ OEM/机型依赖 | 通常与 MUX/混合显卡有关，但接口、功耗和睡眠行为依机型 |
| `Active Efficient-cores=0` 可禁用 E-core | ⚠️ 平台依赖 | 常见含义如此，但选项存在性和行为依 CPU/BIOS |
| 关闭 E-core 必然丢失小核缓存 | ❌ 不准确 | 应描述为改变核心/拓扑/调度资源，不能泛化缓存损失 |
| E-core 与 Hyper-Threading 可互相替代 | ❌ 不准确 | 该代 Intel E-core 无 HT，P-core HT 是独立设置；不能跨代泛化 |
| 关闭 CEP 必然提升降压性能 | ❌ 无通用证据 | CEP 是保护机制，关闭可能改变限制/性能，也可能增加不稳定和风险 |
| IA ICC Unlimited 是物理无限电流 | ❌ 不准确 | 通常是某个核心域电流上限编码，不解除所有功耗/温度/VRM 保护 |
| TVB 关闭/开启有固定收益 | ❌ 不准确 | TVB 是有条件的机会性加频，依 SKU/温度/功耗和电流余量 |
| AC/DC Loadline 越低越好 | ❌ 不准确 | 需要匹配平台电气模型和遥测校准，错误值可能性能下降或不稳定 |
| 关闭 VBS 是降压必需步骤 | ⚠️ 工具/平台依赖 | 不能为降压盲目关闭安全功能；先查具体工具要求和恢复路径 |
| PTT 是可随意关闭的性能开关 | ❌ 不准确 | 影响 BitLocker、Windows 11、凭据和安全启动测量 |
| 全部 USB 设置 Enabled 就能修复接口 | ❓ 无通用证据 | 只能作为特定机型诊断项 |
| DMI Gen3 必然降低南桥温度 | ❓ 个案经验 | 可能降低互联能力，收益和副作用依平台，不能普遍推荐 |

## 参考来源

- [Intel Core i9-12900K 规格](https://www.intel.com/content/www/us/en/products/sku/134599/intel-core-i912900k-processor-30m-cache-up-to-5-20-ghz/specifications.html)
- [Intel Z690 芯片组规格](https://www.intel.com/content/www/us/en/products/sku/218833/intel-z690-chipset/specifications.html)
- [Intel B660 芯片组规格](https://www.intel.com/content/www/us/en/products/sku/218832/intel-b660-chipset-specifications.html)
- [Intel-SA-00289：Processor Voltage Settings Modification Advisory](https://www.intel.com/content/www/us/en/security-center/advisory/intel-sa-00289.html)
- [Intel 官方超频指南入口](https://www.intel.com/content/www/us/en/gaming/resources/how-to-overclock.html)
- [Microsoft OEM VBS](https://learn.microsoft.com/en-us/windows-hardware/design/device-experiences/oem-vbs)
- [Microsoft 内存完整性/HVCI](https://learn.microsoft.com/en-us/windows/security/hardware-security/enable-virtualization-based-protection-of-code-integrity)
- [Microsoft TPM 概述](https://learn.microsoft.com/en-us/windows/security/hardware-security/tpm/trusted-platform-module-overview)
- [机械革命官方支持入口](https://www.mechrevo.com/)

以上官方链接用于说明平台机制和安全背景，不证明某个具体机械革命型号具有本文列出的全部菜单。