---
status: reference
risk: low
applies_to:
  - Windows 10/11 PC 显示输出
  - DisplayPort / HDMI 显示器与线材选购
verified_on: 2026-08-28
# 2026-08-28 重核 HDMI 2.2 上市状态：Ultra96 线材已上市，满带宽整机预计 2027 年
tweak_module: []
---

# DP / HDMI 协议与速率关系表

> **分类**：显卡优化 · 显示输出
>
> **适用场景**：选显示器 / 显卡 / 线材时，对照接口版本判断能点亮什么分辨率与刷新率；排查「带宽够了却带不动」的问题。
>
> 本文数字已对照 VESA / HDMI 标准规范核实，并补充有效带宽与选购避坑要点。

---

## 一、DP（DisplayPort）协议速率表

| 版本 | 链路速率 | 总带宽（原始） | 典型支持上限 |
| --- | --- | --- | --- |
| DP 1.0 / 1.1 | RBR / HBR | 8.64 / 10.8 Gbps | 最高 2560×1600 |
| DP 1.2 | HBR2（5.4Gbps × 4） | 21.6 Gbps | **4K@60** |
| DP 1.3 | HBR3（8.1Gbps × 4） | 32.4 Gbps | 5K@60 |
| DP 1.4 / 1.4a | HBR3（8.1Gbps × 4） | 32.4 Gbps | 8K@30；开 DSC 可 8K@60+ |
| DP 2.0 / 2.1 UHBR10 | 10Gbps × 4 | 40 Gbps | 4K@240 / 8K@60（DSC） |
| DP 2.1 UHBR13.5 | 13.5Gbps × 4 | 54 Gbps | 10K@60 |
| DP 2.1 UHBR20 | 20Gbps × 4 | 80 Gbps | 16K@60（DSC） |

> 子版本数字（10/13.5/20）即每通道链路速率，×4 通道得总带宽。UHBR13.5 为 DP 2.1 新增；DP 2.0 发布时只有 UHBR10/20，2.1 主要变化是新增速率档与 **DP40 / DP80 线缆认证**。

## 二、HDMI 协议速率表

| 版本 | 总带宽（原始） | 典型支持上限 |
| --- | --- | --- |
| HDMI 1.3 / 1.4 | 10.2 Gbps | 4K@30 |
| HDMI 2.0 | 18 Gbps | 4K@60 |
| HDMI 2.1 | 48 Gbps（FRL） | **4K@120 / 8K@60** |
| HDMI 2.1a | 48 Gbps | 同 2.1（新增 SBTM 源码直通） |
| HDMI 2.2 | 96 Gbps | 8K@120 HDR / 10K@85（2025 年初发布规范；满带宽整机尚未上市，Ultra96 认证线已先行上市） |

## 三、两个关键概念

**1. 原始带宽 ≠ 有效带宽（编码开销）**

| 协议 | 编码 | 有效带宽 |
| --- | --- | --- |
| DP 1.x（HBR 系列） | 8b/10b（20% 开销） | 32.4 → **~25.9 Gbps** |
| DP 2.x（UHBR 系列） | 128b/132b（~3% 开销） | 80 → **~77.6 Gbps** |
| HDMI 1.x / 2.0（TMDS） | 8b/10b（20% 开销） | 18 → **~14.4 Gbps** |
| HDMI 2.1+（FRL） | 16b/18b（~11% 开销） | 48 → **~42.7 Gbps** |

算分辨率需求时要按**有效带宽**对表——「带宽看着够却带不动」多半是忽略了编码开销或色深（10bit HDR 会显著增加码率）。

**2. DSC（显示流压缩）**

DSC 可在同等带宽下传输更高分辨率 / 刷新率——有损压缩但达到「视觉无损」，需**信号源与显示器两端都支持**。DP 1.4 起支持，8K / 4K240 等高规格基本都依赖它。

## 四、选购与避坑提示

1. **「HDMI 2.1 TMDS」陷阱**：HDMI Forum 允许旧版 HDMI 2.0（18Gbps）接口标注为「支持 HDMI 2.1（TMDS 模式）」——它并不能跑 4K@120。买屏认准 **FRL 48Gbps / 4K@120 / 8K** 字样；
2. **线材要认证**：跑满 48G 需 **Ultra High Speed HDMI 认证线**（线上印认证标、可扫码验真）；DP 2.x 对应 **DP40 / DP80 认证线**（VESA 认证）；
3. **两头都要强**：链路带宽取源（显卡）与显示器两者中较低一端，线材是第三关——三者任一不支持高规格都会降档；
4. USB-C 视频输出走的多为 **DP Alt Mode**，能力按其承载的 DP 版本计算，与 USB 速率无关；
5. HDMI 2.1 的 4K120 还带来 VRR / ALLM 等游戏特性，与 G-SYNC 兼容屏配合见系列（三）2.3 节。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| DP 各版本带宽：HBR2 21.6 / HBR3 32.4 / UHBR10 40 / UHBR13.5 54 / UHBR20 80 Gbps | ✅ 属实：与 VESA 规范一致（通道速率 ×4） |
| DP 1.2→4K60、DP 1.4+DSC→8K60、UHBR10→4K240、UHBR20→16K60(DSC) | ✅ 属实：VESA 官方能力口径 |
| UHBR13.5 为 DP 2.1 新增档位；DP 2.0 原有 UHBR10/20 | ✅ 属实 |
| HDMI 带宽：1.4 10.2 / 2.0 18 / 2.1 48 / 2.2 96 Gbps | ✅ 属实：HDMI 规范口径 |
| HDMI 2.1a 与 2.1 带宽相同（新增 SBTM） | ✅ 属实 |
| HDMI 2.2 上市状态 | ⚠️ 原表述"设备尚未上市"已部分过时，2026-08-28 重核：2025 年初发布规范；**Ultra96 认证线自 2025 Q3 起已上市**；CES 2026 仅有原型机展出，满带宽（96Gbps）显示器/整机预计 2027 年起上市（依据：[VideoCardz](https://videocardz.com/newz/first-96-gbps-hdmi-2-2-products-expected-in-2027)、[HDMI.org](https://www.hdmi.org/spec/hdmi2)）；另注意 2026 年部分产品仅实现 FRL/DSC 部分特性即标注 HDMI 2.2，不等于 96Gbps 满带宽 |
| 编码开销：8b/10b 20%、128b/132b ~3%、FRL 16b/18b ~11% | ✅ 属实：各协议编码标准 |
| 「HDMI 2.1 TMDS」实为 18Gbps 的 2.0 传输模式 | ✅ 属实：HDMI Forum 授权的命名规则，为已知选购陷阱 |
| DSC 有损但视觉无损、需两端支持 | ✅ 属实：VESA DSC 标准定位 |

**参考来源：**

- [Wikipedia — DisplayPort（各版本带宽表）](https://en.wikipedia.org/wiki/DisplayPort)
- [Wikipedia — HDMI（各版本带宽表）](https://en.wikipedia.org/wiki/HDMI)
- [VESA — DisplayPort 规格](https://www.vesa.org/)
- [HDMI Licensing Administrator — HDMI 规范](https://www.hdmi.org/)
