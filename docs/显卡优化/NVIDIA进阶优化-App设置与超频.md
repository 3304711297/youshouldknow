# NVIDIA 进阶优化（二）：App 设置要点与笔记本显卡超频

> **分类**：显卡优化 · NVIDIA
>
> **适用场景**：新「英伟达 App」（NVIDIA App）中需要动哪些设置；为什么不要开「自动调优」；笔记本 RTX 40 系显卡的正确超频方式与起步值。
>
> 本文关键声明已对照 NVIDIA 官方公告与社区反馈核实，核查记录见文末。系列下一篇为 NVIDIA 控制面板设置。

---

## 一、App 中值得改的三项

英伟达 App 里大部分设置项与控制面板重复——**如果你已经配置过控制面板，App 里只需要动这三项**：

| 设置项 | 建议 | 说明 |
| --- | --- | --- |
| **Battery Boost** | 关 | 电池模式下自动限制帧率以省电（插电不影响）。追求离电性能就关闭，代价是续航缩短 |
| **Smooth Motion** | 开（如果支持） | 驱动级 AI 帧生成，可让几乎任何游戏「一键翻倍」感知帧数 |
| **Whisper Mode** | 关（如果有的话） | 笔记本专属安静模式：限制帧率 + 调整风扇策略降噪，与性能取向冲突 |

**关于 Smooth Motion 的支持范围与开启方法**：原生支持 RTX 50 系；自 **GeForce 590.26 驱动（2025 年 7 月）**起扩展支持**全部 RTX 40 系（含笔记本显卡）**，RTX 30 及更早不支持。开启路径（官方）：英伟达 App → **图形 → 程序设置** → 选中游戏 → **驱动程序设置（Driver Settings）** → Smooth Motion 开（较新版本 App 另提供全局开关）。

**Smooth Motion 与 DLSS 的关系（重点）**：

| 组合 | 能否同开 | 说明 |
| --- | --- | --- |
| Smooth Motion + DLSS **帧生成**（Frame Generation） | ❌ **不可叠加** | 两者是竞争技术：官方将 Smooth Motion 定位为「**面向不支持 DLSS 帧生成的游戏**」的方案；同时开启会导致性能下降与画面异常 |
| Smooth Motion + DLSS **超分**（Super Resolution） | ✅ 可以同开 | 官方原文：Smooth Motion 可用于原生分辨率、DLSS 超分或其他缩放技术生效的游戏 |

**怎么选**：

- **游戏支持 DLSS 帧生成** → 在游戏内开帧生成，**不要**再开 Smooth Motion。原生 FG 走引擎级运动矢量，画质与流畅度显著优于驱动级插帧；
- **游戏不支持帧生成** → 用 Smooth Motion 兜底（驱动侧 AI 推测插帧，快速运动画面可能略糊 / 出现伪影，属预期）；
- 想叠加收益：DLSS 超分 + Smooth Motion 同开（缩放 + 插帧互不冲突）。

## 二、特别提醒：不要开「自动调优」

App 的 **系统 → 性能 → 自动调优** 会自动扫描并小幅超频显卡，**不建议打开**，原因：

1. **幅度很小**：自动调优以保守稳定为先，实测收益有限，尤其显存频率给得非常保守（社区普遍反馈「没什么用」）；
2. **耗时很久**：官方说明需要 **10～20 分钟**反复压力测试扫描；
3. 有社区用户反馈扫描中途出现黑屏重启。

对显卡超频有实际需求的，走下面两条路更高效。

## 三、笔记本显卡超频

### 路线 A：厂商控制台一键超频（省心）

各品牌自带控制台通常有一键超频开关。以机械革命为例：**控制台 → 性能 → 自定义模式 → 打开「超性能」开关**，即为官方预设的显卡超频，稳定性与功耗策略由厂商调校。

### 路线 B：微星小飞机手动超频（通用）

**MSI Afterburner（微星小飞机）**是通用的显卡超频工具（不限微星机型），拉核心 / 显存频率偏移值即可。

**笔记本 RTX 40 系起步参考值**（经验值，逐档摸）：

| 显卡 | 核心频率偏移 | 显存频率偏移 |
| --- | --- | --- |
| RTX 4060 Laptop | +50～150 MHz | +800～1000 MHz |
| RTX 4070 Laptop | +150～250 MHz | +800～1000 MHz |

> 显存超 800～1000 即可：再多提升不大，温度和功耗反而上去。

**安全须知**：

- 从起步值下限开始，每加一档跑一次 3DMark / 游戏实测，崩溃 / 花屏 / 驱动重置就回退一档；
- 笔记本受**功耗墙与温度墙**限制，超频幅度本就有限，散热不足时优先改善散热而不是堆频率；
- 显卡超频是软件层面的偏移设置，完全可逆（Afterburner 一键 Reset），不会变砖，但长期高温会加速老化。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| Smooth Motion：驱动级 AI 帧生成，RTX 40 系自 590.26 驱动起支持（含笔记本），RTX 30 及更早不支持 | ✅ 属实：NVIDIA 官方公告（2025-07）原文，Tom's Hardware 报道一致 |
| Smooth Motion 定位为「面向不支持 DLSS 帧生成的游戏」；与 FG 不可叠加 | ✅ 属实：官方公告原文 "for titles without DLSS Frame Generation support"；NVIDIA 驱动文档将两者列为竞争技术，同开致性能下降与画面异常 |
| Smooth Motion 可与 DLSS 超分（Super Resolution）同开 | ✅ 属实：官方公告原文（原生分辨率 / DLSS 超分 / 其他缩放技术下均可生效） |
| 逐游戏开启路径：App → 图形 → 程序设置 → 驱动程序设置 → Smooth Motion | ✅ 属实：官方公告给出的操作路径 |
| Battery Boost：电池模式限制帧率省电；Whisper Mode：笔记本降噪模式 | ✅ 属实：均为 NVIDIA 官方笔记本特性，App 中可开关 |
| 自动调优：小幅超频、耗时很久 | ✅ 属实：官方说明需 10~20 分钟扫描；社区普遍反馈幅度保守、显存给值过低，收益有限 |
| 自动调优扫描中黑屏重启案例 | ✅ 有社区反馈（NGA），个案性质 |
| MSI Afterburner 为通用显卡超频工具 | ✅ 属实 |
| 起步值：4060 笔记本核心 +50~150、4070 笔记本 +150~250、显存 +800~1000 | 💡 社区经验值：与主流实测区间相符，个体体质不同需自测，超出后收益边际递减 |
| 机械革命控制台「超性能」开关为一键超频 | 💡 厂商功能说明，按各机型控制台实际界面为准 |

**参考来源：**

- [NVIDIA 官方 — App 更新：RTX 40 系 Smooth Motion 与全局 DLSS 覆盖](https://www.nvidia.com/en-us/geforce/news/nvidia-app-global-dlss-overrides-rtx-40-series-smooth-motion/)
- [Reddit r/nvidia — DLSS 帧生成与 Smooth Motion 同开的讨论](https://www.reddit.com/r/nvidia/comments/1krikzm/do_dlss_3_frame_generation_and_smooth_motion_work/)
- [Tom's Hardware — Smooth Motion 登陆 RTX 40 系](https://www.tomshardware.com/pc-components/gpu-drivers/nvidias-new-driver-update-finally-brings-smooth-motion-to-rtx-40-series-gpus-works-like-amds-fluid-motion-frames-and-claims-to-double-your-fps-with-a-single-click-in-any-game)
- [NVIDIA 官方 — App 自动调优说明（10~20 分钟扫描）](https://www.nvidia.cn/geforce/news/nvidia-app-beta-update-av1-performance-tuning/)
- [Reddit r/nvidia — 自动调优实测讨论（幅度保守）](https://www.reddit.com/r/nvidia/comments/1d7x1vo/has_anyone_tried_the_automatic_tuning_in_nvidia/?tl=zh-hans)
- [NGA — 自动调优扫描黑屏案例](https://ngabbs.com/read.php?tid=30186670)
- [NVIDIA App 10.0.1 版本说明（性能面板与自动调优）](https://www.nvidia.cn/geforce/release-notes/NVAPP/10_0_1/Web/nvapp-v10_0_1-web-release-highlights/)
