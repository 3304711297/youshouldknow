# 调整 Windows 滚动条宽度与高度

> **分类**：系统知识 · 界面优化
>
> **适用场景**：27 寸 2K 及以上分辨率显示器在 100% 缩放下，默认滚动条细如牙签、不易点中；通过注册表自定义滚动条粗细与长度。Win10 / Win11 通用。
>
> 本文方法已对照微软注册表指南与多个技术社区信源交叉验证，核查记录见文末。

---

## 原理

滚动条尺寸由注册表 `WindowMetrics` 下的值控制，单位为**负的缇（twips）**：96 DPI 下 **1 像素 = 15 缇**，所以数值以 **-15 为一个单位**增减，且必须能被 15 整除。

- 默认值 `-255` ≈ 17 像素宽；
- **数值越负（绝对值越大），滚动条越粗**；反之越细。

## 操作步骤

1. 右键开始菜单 →「运行」（或 `Win + R`），输入 `regedit` 打开注册表编辑器；
2. 定位到：

   ```text
   计算机\HKEY_CURRENT_USER\Control Panel\Desktop\WindowMetrics
   ```

3. 在右侧找到 `ScrollWidth`（控制竖向滚动条的**宽度**）；
4. 修改数值：默认 `-255`，想加粗可改为 `-495`（≈ 33 像素）；
5. **注销或重启电脑**后生效（WindowMetrics 仅在登录时读取，改完不重启不会有任何变化）。

## 调整技巧

| 目标 | 操作 | 示例 |
| --- | --- | --- |
| 再粗一点 | 每次再减 15 | -495 → -510 → -525 |
| 太粗了 | 每次加 15 | -495 → -480 → -465 |
| 恢复默认 | 改回 | `-255` |

- 合理区间大致在 `-100 ~ -1000`（约 7~66 像素），超出可能显示异常；
- 想调整横向滚动条的**高度（长度方向）**，修改同目录下的 `ScrollHeight`，规则相同；
- 两个值的数据类型为**字符串（REG_SZ）**，直接在原值上修改数据即可，不要新建其他类型的值。

## 命令行方式（可选）

```bat
reg add "HKCU\Control Panel\Desktop\WindowMetrics" /v ScrollWidth /t REG_SZ /d "-495" /f
```

执行后同样需要注销重新登录生效。也可以用 Winaero Tweaker 等工具在图形界面中调整同一设置。

---

## 事实核查记录

| 声明 | 核查结果 |
| --- | --- |
| 注册表位置 `HKCU\Control Panel\Desktop\WindowMetrics`，值为 `ScrollWidth` / `ScrollHeight` | ✅ 属实：《Microsoft Windows XP Registry Guide》即有记载，历代 Windows 沿用至今，Win10/Win11 有效 |
| 默认值 -255，以 -15 为一个单位，必须被 15 整除 | ✅ 属实：值为负缇，96 DPI 下 1 像素 = 15 缇；-255 ≈ 17 像素 |
| 数值越负滚动条越粗（如 -495 ≈ 33 像素） | ✅ 属实：社区多信源一致（Winaero：-100 ~ -1000 区间，越负越大） |
| 修改后需注销/重启生效 | ✅ 属实：WindowMetrics 仅在登录时读取（ElevenForum、Winaero 均确认） |
| 数值类型为 REG_SZ 字符串 | ✅ 属实：虽是数字但以字符串类型存储，社区命令行示例一致 |

> ⚠️ 勘误备注：本主题部分转载版本中「想调粗改为 -180」的示例方向写反——-180（≈12 像素）比默认 -255 更**细**，加粗应改得更负（如 -495），请注意辨别。

**参考来源：**

- [Microsoft Windows XP Registry Guide（WindowMetrics 章节）](https://dokumen.pub/microsoft-windows-xp-registry-guide-9780735617889-0735617880.html)
- [Winaero — How to change the scrollbar width size](https://winaero.com/how-to-change-the-scrollbar-width-size-in-windows-8-1/)
- [ElevenForum — Change scrollbar size in Windows 11](https://www.elevenforum.com/t/change-scrollbar-size-in-windows-11.6465/page-3)
