# NVCleanstall 精简安装 NVIDIA 显卡驱动

> **分类**：显卡优化
> **适用场景**：希望去除 NVIDIA 驱动中的遥测、App、附加组件，只保留纯净驱动的安装与更新
> **核查说明**：本文基于 NVCleanstall v1.19.0 界面截图整理；下载源、开发者预览驱动链接、NV Platform Controllers 说明、NVENC 补丁与 MPO 禁用等关键结论均已检索核实（TechPowerUp、NVIDIA 官方知识库、NVIDIA 开发者文档等），详见文末核查记录。

## 一、它是什么

NVCleanstall 是 **TechPowerUp 开发**的免费绿色工具，用于在安装 NVIDIA 驱动前"做减法"：从官方驱动包中剔除遥测、NVIDIA App、各类附加组件，并可选打上 NVENC 解锁、禁用 MPO 等调整补丁，得到一个只装驱动的干净安装流程。

## 二、下载软件

| 来源 | 地址 | 说明 |
| --- | --- | --- |
| **官方（推荐）** | `techpowerup.com/download/techpowerup-nvcleanstall/` | TechPowerUp 是 NVCleanstall 的开发方，此为官方下载页 |
| 官方产品页 | `techpowerup.com/nvcleanstall/` | 功能介绍与下载入口 |

> ⚠️ **勘误**：`nvcleanstall.net` 这个域名**不是可用的官网**——实测它只返回一个 "OK" 占位响应，没有任何页面内容（该域名归 TechPowerUp 所有，推测仅作内部用途）。网上部分教程把它写成"官网"，实际下载请认准 TechPowerUp。当前最新版本为 v1.19.0。

## 三、获取驱动

| 类型 | 来源 | 说明 |
| --- | --- | --- |
| 正式版（Game Ready） | NVIDIA 官网驱动下载页（nvidia.com/drivers），按型号搜索 Game Ready 驱动 | 日常使用首选 |
| 开发者预览版（非最新） | `developer.nvidia.com/downloads/shadermodel6-9-preview-driver` | Shader Model 6.9 预览驱动（GeForce 590.10 起，590.26 及以后版本更佳），面向需要 Cooperative Vectors / DXR 1.2 等新特性的开发者；页面可能需要免费注册/登录 NVIDIA 开发者账号；预览驱动非 Game Ready 正式版，稳定性自担 |

## 四、NVCleanstall 使用步骤

启动后选择 **【Use driver files on disk】**（使用本地驱动文件），选中第三步下载的驱动程序 exe，进入组件选择页。

### 1. 组件选择页（Select Components To Install）

按下表勾选（即参考截图的勾选方案）：

| 组件 | 勾选 | 说明 |
| --- | --- | --- |
| Display Driver (required) | ✅ 必选 | 显卡驱动本体 |
| PhysX | ✅ | 物理引擎，老游戏与部分游戏需要 |
| NV Platform Controllers | ✅ 仅笔记本 | **笔记本必勾**：这是 RTX 30 系及更新笔记本 GPU 的电源管理组件（Dynamic Boost、可配置 TDP），不装会导致独显回落低功耗模式、性能大幅下降；**台式机不需要** |
| Legacy Control Panel | ❌ | 老版控制面板，一般无需（但若禁用 NVIDIA Container 又想用控制面板，可考虑保留，见下文注意事项） |
| HD Audio via HDMI | ❌ | **用 HDMI/DP 输出声音（显示器喇叭/耳机接显卡）的用户必须勾选**，否则无声音 |
| Microsoft Visual C++ 2017 Runtimes | ❌ | 一般系统已具备 |
| USB-C Driver | ❌ | 仅使用显卡 USB-C（VirtualLink）接口时需要 |
| FrameView SDK | ❌ | 帧率监控组件，可用其他工具替代 |
| Quadro View / Virtual Audio / Telemetry | ❌ | 专业卡多屏布局 / 虚拟音频 / 遥测，普通用户不需要 |
| NVIDIA DLSS SDK | ❌ | 开发者用 DLSS 集成文件 |
| NVIDIA App / NV App Components / NV Container / ShadowPlay / NV Backend / NVIDIA App MessageBus | ❌ | NVIDIA App 全家桶、录屏（ShadowPlay）与后台服务；**注意：不用 NVIDIA App/GeForce Experience 的录屏、自动调优功能才可不装** |

### 2. 安装调整页（Installation Tweaks）

| 选项 | 参考勾选 | 说明 |
| --- | --- | --- |
| Disable Installer Telemetry & Advertising | ✅ | 禁用安装器遥测与广告 |
| Unattended Express Installation | ❌ | 不勾它才会弹出下述 NVIDIA 安装界面进行交互式安装；勾上则是静默安装 |
| Perform a Clean Installation | ✅ | 安装时自动执行清洁安装（会预先清除旧驱动残留文件） |
| Add Hardware Support | ❌ | 为更多硬件 ID 添加支持，一般无需 |
| Enable DLSS Indicator | ✅ | 游戏内显示当前 DLSS 版本（右上角小字），便于确认预设是否生效 |
| Disable Multiplane Overlay (MPO) | ✅ | 禁用 MPO。NVIDIA 官方知识库认可此操作（等效注册表 `OverlayTestMode=5`），可解决部分系统的桌面闪烁/卡顿问题；个别用户反馈禁用后 YouTube 反而闪烁，若有异常可改回 |
| Disable Ansel | ✅ | 禁用游戏内照片模式 Ansel |
| Show Expert Tweaks | ✅ | 显示下方专家选项（不勾则隐藏本页部分选项） |
| Disable Driver Telemetry (Experimental) | ✅ | 禁用驱动遥测（实验性） |
| Disable NVIDIA Container (Experimental) | ❌→⚠️ 谨慎 | 软件自己标注了后果：**会导致 NVIDIA 控制面板无法使用**（也会影响 NVIDIA App 相关功能）。参考截图勾选了它，但如果你还需要控制面板/App（如本仓库其他文章的设置项），建议不勾 |
| Disable NVIDIA HD Audio device sleep timer | ❌ | 防止 HDMI 音频设备休眠断连，有此问题的用户可勾 |
| Enable Message Signaled Interrupts | ✅ | 启用 MSI 消息信号中断，可降低中断开销（对延迟敏感场景有帮助） |
| Disable HDCP | ✅→⚠️ 按需 | 禁用 HDCP 输出加密。**副作用：Netflix 等 DRM 受保护内容将无法播放**；需要采集卡录制、或纯本地内容用户才建议勾 |
| Apply NVENC Video Encoding Session Limit Patch | ✅ | 解除消费级显卡 NVENC 并发编码会话数限制（官方限制：2019 年 3 路 → 2023 年 5 路 → 2024 年起 8 路，专业卡无限制）。挂 Plex/Jellyfin 转码、多路推流用户收益明显 |
| Start external application | ❌ | 安装完成后运行外部程序 |

### 3. 数字签名与反作弊（页面底部）

由于勾选了上述修改类补丁，需要处理驱动签名：

| 选项 | 参考勾选 | 说明 |
| --- | --- | --- |
| Rebuild digital signature | ✅ | 对修改后的驱动重建数字签名（勾选修改项后必须） |
| Use method compatible with Easy-Anti-Cheat | ✅ | 使用与 Easy Anti-Cheat 兼容的签名方式，避免被反作弊系统拦截 |
| Automatically accept the "driver unsigned" warning | ✅ | 安装时自动接受"驱动未签名"警告弹窗 |

> ⚠️ 修改并重签名的驱动会触发 Windows 的未签名提示，这是正常现象；**玩带内核级反作弊网游（EAC/BattlEye/TP 等）的用户请保持 EAC 兼容方式勾选，若遇异常建议回退官方原版驱动**。

完成后点击 **【Install】**，会弹出 NVIDIA 驱动安装界面。

## 五、安装驱动（NVIDIA 安装程序）

1. 选择 **【NVIDIA 图形驱动程序】**，点击下一步；
2. 选择 **【自定义】**，点击下一步；
3. 勾选 **【PhysX 系统软件】** 与 **【执行清洁安装】**——后者 NVCleanstall 已通过 "Perform a Clean Installation" 替你自动勾上；
4. 点击安装，等待完成即可。

> **注意**：若安装程序组件列表中出现 **NV Platform Controllers / NV Platform Controllers and Framework**——**笔记本用户务必勾选**（RTX 30 系及更新笔记本 GPU 的 Dynamic Boost 电源管理依赖它），**台式机无需勾选**。

## 六、注意事项速查

- **笔记本**：NV Platform Controllers 不装 = 独显锁低功耗，这是笔记本精简驱动最常见的翻车点；
- **HDMI/DP 输出音频**：HD Audio via HDMI 组件必须装，否则显卡输出的声音消失；
- **NVIDIA App/控制面板依赖者**：不要勾 "Disable NVIDIA Container"（软件已注明会破坏控制面板）；
- **流媒体用户**：勾了 "Disable HDCP" 就看不了 Netflix 等受保护内容；
- **反作弊网游玩家**：保持 EAC 兼容签名方式；出问题先回退官方原版驱动排查。

## 事实核查记录

| 原文观点 | 核查结论 | 说明 |
| --- | --- | --- |
| 官网是 nvcleanstall.net，第三方是 techpowerup.com | ❌ 勘误 | nvcleanstall.net 实测仅返回 "OK" 占位响应，无任何页面；NVCleanstall 由 TechPowerUp 开发，techpowerup.com 才是官方下载源（TechPowerUp 官网，实测域名行为） |
| 开发者版本驱动：developer.nvidia.com/downloads/shadermodel6-9-preview-driver | ✅ 属实 | SM 6.9 预览驱动真实存在（GeForce 590.10 首发、590.26+ 推荐），含 Cooperative Vectors、DXR 1.2 等特性；匿名访问可能跳转开发者登录页（NVIDIA RTX Kit 页面、GeForce 论坛、Guru3D 论坛） |
| NV Platform Controllers：笔记本勾选，台式不需勾选 | ✅ 属实 | 该组件为 RTX 30 系+笔记本 GPU 的电源管理驱动（Dynamic Boost、可配置 TDP），缺失时独显回落低功耗模式；台式机无此机制不需要（NVCleanstall 界面原文、TechPowerUp 论坛、NVIDIA 论坛多方一致） |
| 执行清洁安装已由 NVCleanstall 自动勾上 | ✅ 属实 | 对应 Tweaks 页 "Perform a Clean Installation" 勾选状态，截图确认 |
| NVENC 会话数补丁的作用 | ✅ 属实 | 消费级 NVENC 并发会话限制为 NVIDIA 官方策略：3 路（2019）→ 5 路（2023）→ 8 路（2024 起，SDK 12.2 文档确认"非认证 GPU 每系统 8 个"），补丁可完全解除（VideoCardz、Tom's Hardware、NVIDIA 开发者论坛） |
| 禁用 MPO 的合理性 | ✅ 属实 | NVIDIA 官方知识库提供 mpo_disable.reg（注册表 OverlayTestMode=5）作为闪烁/卡顿问题的官方修复；NVCleanstall 该选项等效（NVIDIA 官方支持页） |
| Disable NVIDIA Container 的风险 | ✅ 属实（界面已标注） | 软件界面原文注明 "(Experimental, breaks NVIDIA Control Panel)"，会导致 NVIDIA 控制面板/App 部分功能不可用 |
| Disable HDCP 的副作用 | ⚠️ 已知代价 | 禁用后输出不再经 HDCP 加密，受 DRM 保护内容（Netflix 4K 等）将拒绝播放；采集/本地用途才建议启用 |
| 重签驱动 + EAC 兼容方式 + 自动接受未签名警告 | ✅ 与界面一致 | 勾选修改类补丁后需重建签名；EAC 兼容方式避免反作弊误判；未签名警告为正常现象 |

## 参考来源

1. TechPowerUp — NVCleanstall 官方下载页：<https://www.techpowerup.com/download/techpowerup-nvcleanstall/>
2. TechPowerUp — NVCleanstall 产品介绍页：<https://www.techpowerup.com/nvcleanstall/>
3. NVIDIA Developer — Shader Model 6.9 Preview Driver：<https://developer.nvidia.com/downloads/shadermodel6-9-preview-driver>
4. NVIDIA RTX Kit（SM 6.9 / Cooperative Vectors 特性说明）：<https://developer.nvidia.com/rtx-kit>
5. TechPowerUp 论坛 — NV Platform Controllers 与笔记本 Dynamic Boost 的关系：<https://www.techpowerup.com/forums/threads/nvcleanstall-outdated-descriptions-please-update-following-to-stop-laptop-users-from-getting-dynamic-boost-removed.313598/>
6. NVIDIA 官方知识库 — What is Multi-Plane Overlay (MPO) 及官方禁用方法：<https://nvidia.custhelp.com/app/answers/detail/a_id/5157/>
7. VideoCardz — GeForce NVENC 并发会话上限提升至 8：<https://videocardz.com/newz/nvdia-geforce-gpus-now-support-up-to-8-concurrent-nvenc-encoding-sessions>
8. Tom's Hardware — NVENC 并发限制提升（5 路）报道：<https://www.tomshardware.com/news/nvidia-increases-concurrent-nvenc-sessions-on-consumer-gpus>
