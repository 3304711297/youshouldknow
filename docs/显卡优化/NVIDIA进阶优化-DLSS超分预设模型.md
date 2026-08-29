# NVIDIA 进阶优化（四）：DLSS 超分预设模型

> **分类**：显卡优化 · NVIDIA
>
> **适用场景**：用 NVIDIA App 的「DLSS 超分模型覆盖」强制游戏使用更新的 DLSS 超分模型（如把老游戏的 CNN 模型换成 DLSS 4 的 Transformer 模型），不依赖游戏自带的版本。全系列 RTX 显卡适用（含 RTX 20/30）。
>
> 本文已对照 NVIDIA 官方公告与 TechPowerUp 等权威测试核实；其中一处流传资料的预设字母错误已勘误，见文末核查记录。

---

## 一、什么是 DLSS 超分预设

DLSS 超分（Super Resolution）的画质取决于背后的**模型**。不同时期的驱动 / 游戏 DLL 内置了多套模型，按「预设 A～F、J、K、L/M」等字母区分（CNN 旧架构与 Transformer 新架构）。游戏默认用哪套取决于其自带的 DLSS 版本——通过 NVIDIA App 的**模型覆盖**功能，可以强制指定更新的模型，让老游戏立刻享受新模型的画质提升。

## 二、预设模型对照表

| 预设 | 架构 · 时代 | 说明与适用 |
| --- | --- | --- |
| A | CNN · DLSS 2.0 初版 | 最早期模型，仅作画质对比基线 |
| B | CNN · DLSS 2.1 | 早期精修，同上 |
| C | CNN · DLSS 2.3/2.4 | **DLSS 2.x 时代最佳画质**，老游戏默认；兼容性优先时选它 |
| D | CNN · DLSS 2.5+ | 2.x 末期精修版，4K 与性能档口碑好，部分游戏默认 |
| E | CNN · DLSS 3.x | **DLSS 3 时代游戏默认**（DLAA / 质量 / 平衡档），CNN 架构最佳 |
| F | CNN · DLSS 3.x | 性能 / 超高性能档位使用的 CNN |
| **J** | **Transformer · DLSS 4 初版** | 随 RTX 50 系 / DLSS 4 首发（2025-01） |
| **K** | **Transformer · DLSS 4 精修版** | DLAA / 质量 / 平衡档的官方默认：较 J 更稳、鬼影更少，性能开销低于 L |
| **L** | **Transformer · DLSS 4.5（2026-01）** | 官方称迄今最强画质（3×3 上采样），开销高于 K，官方定位偏 4K 超分场景；M 为衍生变体 |

> ✏️ **勘误**：部分流传资料把 DLSS 4 的 Transformer 模型称作「预设 E」——**错误**。预设 E 是 DLSS 3.x 的 CNN 模型；Transformer 是**预设 J / K**（DLSS 4.5 为 L/M）。另注意：同一字母在不同画质档位（质量 / 平衡 / 性能）含义可能不同，覆盖时以 App 选项描述为准。

## 三、Transformer 模型（J/K）的特点

- **2 倍参数量**的 Transformer 架构：画面时间稳定性大幅提升、鬼影与闪烁显著减少，1080p 与 4K 细节质量均有提升；
- 性能开销略高于 CNN：超分本身约 **1%～4%**（TechPowerUp 实测；RTX 20/30 偏高、RTX 40/50 最低）；
- **RTX 20/30 系也能用**——DLSS 4 超分模型覆盖支持全系 RTX，这与帧生成（仅 RTX 40/50）不同，老卡也能白嫖画质升级。

## 四、如何设置（NVIDIA App）

1. 英伟达 App → **图形 → 程序设置** → 选择游戏；
2. 找到 **「DLSS 超分模型覆盖」（DLSS Override – Model Preset）**；
3. 选项含义：
   - **使用游戏设置**——不覆盖（默认）；
   - **推荐（Recommended）**——DLSS 4.5 起 App 以「Recommended」取代原先的「Latest」：多数画质档位指向预设 K，**推荐直接选这个**；4K 超分场景可指定 L 对比画质与性能取舍；
   - **指定预设**——手动选 A～F / J / K / L 等做对比测试；
4. 应用后重启游戏生效。

## 五、风险与注意事项

- **逐游戏测试**：个别游戏与 Transformer 模型存在兼容性问题（闪退、崩溃、性能不升反降），部分游戏「HDR + 新模型」组合有画面异常——出问题就改回「使用游戏设置」；
- **驱动更新后覆盖可能被重置**，大版本驱动升级后记得复查；
- 老游戏（DLSS 2.x DLL）覆盖后收益最明显，本来就是 DLSS 3.x 的游戏提升相对小一些。

## 六、进阶：DLSSTweaks

开源工具 [DLSSTweaks](https://github.com/emoose/DLSSTweaks) 可以做比 App 更细的覆盖（模型 + 参数级），需要自行下载 DLSS 库文件并放到指定位置，操作门槛较高，有折腾需求的进阶用户使用。它是第三方工具，不属于 `tweakbyjie` 的自动化执行范围。

### 6.1 部署与配置示例

以下步骤整理自用户提供的配置截图，文件名和目录是**某个版本、某个游戏的示例**，不能假定所有游戏都完全相同：

1. 从 [DLSSTweaks Releases](https://github.com/emoose/DLSSTweaks/releases) 获取与当前版本匹配的文件，并先阅读该版本的说明；
2. 将工具要求的运行时文件（截图示例为 `nvngx.dll`、`dlsstweaks.ini` 和 `DLSSTweaksConfig.exe`）放到目标游戏实际使用 DLSS 的目录。截图示例路径为“游戏根目录 / 虚幻引擎游戏目录 / Binaries / Win64”，实际文件名、目录和 DLL 要求以游戏目录结构及工具版本说明为准；
3. 运行 `DLSSTweaksConfig.exe`，在 `DLSSQualityLevels` 部分将 `Enable` 设为 `True`，再保存配置；
4. 进入游戏，将输出分辨率设为 4K，并选择 DLSS 的“超高性能（Ultra Performance）”档。不要把这个档位与 Windows 的 `Ultimate Performance` 电源计划混淆。

### 6.2 Ultra Performance 比例换算示例

截图用目标输出高度 2160（4K）演示内部渲染高度比例：

| 内部渲染高度 | 目标输出高度 | 换算 | 截图示例输入 |
| ---: | ---: | ---: | ---: |
| 240p | 2160p | `240 ÷ 2160 ≈ 0.111` | `0.11` |
| 360p | 2160p | `360 ÷ 2160 ≈ 0.167` | `0.17` |
| 540p | 2160p | `540 ÷ 2160 = 0.25` | `0.25` |

这些数字只是纵向分辨率比例的计算示范，不等于每个版本的 `UltraPerformance` 配置字段语义，也不代表画质无损。比例越低，细节、稳定性、文字可读性和伪影风险通常越需要单独评估。

### 6.3 验证、回滚与兼容性

- 保存后重启游戏，在游戏内选择 DLSS；不要只根据配置程序显示“已保存”就认定生效；
- 可按截图思路在配置程序中启用调试 HUD，将 `OverrideDlssHud` 设为 `Force enable`，进入游戏后查看屏幕角落显示的实际渲染分辨率。字段名称和可用值可能随版本变化，以当前版本说明为准；
- 使用 [游戏性能验证流程](../项目导航/游戏性能验证流程.md) 记录真实帧率、1% Low、帧时间、延迟、画质伪影和稳定性，不要只看右下角显示帧数；
- 修改前备份游戏目录中的原始 DLSS DLL、配置文件和相关替换文件。游戏更新或验证文件完整性后，替换文件可能被覆盖，需要重新核对；
- 出现闪退、黑屏、画面异常、反作弊提示或游戏无法启动时，先退出游戏，删除/移出 DLSSTweaks 替换文件并恢复原始 DLL，再回到游戏默认 DLSS 设置；联机游戏优先遵守游戏和反作弊系统的规则，不要在不确定时强行使用 DLL 替换；
- DLSSTweaks 修改的是游戏运行时 DLL/配置，不等同于 NVCleanstall 中的 NVIDIA DLSS SDK，也不等同于 NVIDIA App 的官方模型覆盖。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| Transformer 模型为预设 J（DLSS 4 初版）/ K（2025-01 精修，官方推荐）/ L、M（DLSS 4.5） | ✅ 属实：NVIDIA 官方 App 更新公告与 DLSS 4.5 公告、Reddit 预设指南一致 |
| 「预设 E = DLSS 4 Transformer」 | ❌ 勘误：预设 E 是 DLSS 3.x 的 CNN 模型（DLAA/质量/平衡档默认）；Transformer 是 J/K |
| Transformer 2 倍参数量、更稳更少鬼影、1080p/4K 细节提升 | ✅ 属实：官方与 TechPowerUp 画质实测一致 |
| 预设 K 为官方「最新 / 推荐」选项 | ⚠️ 已过时，2026-08-28 重核更新：DLSS 4.5（2026-01）引入预设 L（画质更强、开销更高，定位 4K 超分），且 App 以「Recommended」取代「Latest」——多数档位的推荐指向 K，4K 场景可选 L（依据：[NVIDIA DLSS 4.5 公告](https://www.nvidia.com/en-us/geforce/news/dlss-4-5-super-resolution-available-now/)、[Digital Foundry 实测](https://www.digitalfoundry.net/features/dlss-4-5-preset-l-tested-how-good-can-a-4k-upscale-from-720p-look)、[社区选型指南](https://www.reddit.com/r/nvidia/comments/1q5f3bd/dlss_preset_selection_guide/)） |
| 开销约 1～4%（老卡偏高、40/50 最低） | ✅ 属实：TechPowerUp 实测区间 |
| RTX 20/30 也可用 DLSS 4 超分模型 | ✅ 属实：超分模型覆盖全系 RTX 可用（区别于帧生成的 40/50 限定） |
| 设置路径：App → 图形 → 程序设置 → DLSS 超分模型覆盖 | ✅ 属实：官方公告及帮助文档给出的路径 |
| 个别游戏兼容性问题（闪退 / 性能反降 / HDR 异常）、驱动更新重置覆盖 | ✅ 属实：社区普遍反馈，官方帮助亦有提示 |
| DLSSTweaks 为开源进阶覆盖工具 | ✅ 属实：GitHub 开源项目（emoose/DLSSTweaks） |
| 截图示例中的部署文件和目录 | ⚠️ 版本/游戏相关：`nvngx.dll`、`dlsstweaks.ini`、`DLSSTweaksConfig.exe` 与 `Binaries/Win64` 只是用户提供截图中的示例，实际名称和目录必须以当前 Release 说明及目标游戏为准 |
| Ultra Performance 比例 `0.11` / `0.17` / `0.25` | ⚠️ 算术示例：分别由 `240/2160`、`360/2160`、`540/2160` 换算，不能外推为所有版本配置字段或画质保证 |
| `OverrideDlssHud = Force enable` 可显示实际渲染分辨率 | ⚠️ 版本相关：截图所示字段和显示行为需以当前 DLSSTweaks 版本验证，不能保证所有版本都存在 |
| DLSSTweaks 文件替换可在游戏更新或完整性验证后保留 | ❌ 不成立：更新或完整性验证可能覆盖替换文件，需重新核对并准备原文件回滚 |

**参考来源：**

- [NVIDIA 官方 — App 更新：DLSS 覆盖功能（预设 J/K 说明）](https://www.nvidia.com/en-us/geforce/news/gfecnt/20251/nvidia-app-update-dlss-overrides-and-more/)
- [NVIDIA 官方 — DLSS 4.5 超分（预设 L/M）](https://www.nvidia.com/en-us/geforce/news/dlss-4-5-super-resolution-available-now/)
- [NVIDIA 官方帮助 — 在 App 中启用 DLSS 4 覆盖](https://nvidia.custhelp.com/app/answers/detail/a_id/5620/)
- [TechPowerUp — DLSS 4 Transformer 画质与性能实测](https://www.techpowerup.com/review/nvidia-dlss-4-transformers-image-quality/)
- [Reddit r/nvidia — DLSS Preset Selection Guide](https://www.reddit.com/r/nvidia/comments/1q5f3bd/dlss_preset_selection_guide/)
- [Reddit r/nvidia — 激活预设 K 指南](https://www.reddit.com/r/nvidia/comments/1if7y27/little_guide_to_activating_dlls_preset_k_which_is/)
- [GitHub — emoose/DLSSTweaks](https://github.com/emoose/DLSSTweaks)
