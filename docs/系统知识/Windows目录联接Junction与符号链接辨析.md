---
applies_to:
  - Windows 10
  - Windows 11
risk: low
tweak_module: []
---

# Windows 目录联接 Junction 与符号链接辨析

## 文档范围

Windows NTFS 支持三种"链接"：硬链接（Hard Link）、符号链接（Symbolic Link）、目录联接（Junction，也称软联接 Soft Link）。三者常被混用，但适用对象、权限要求与删除语义差异很大。本文给出一手实测的对照结论、创建命令与一个真实场景——**让多个 AI 助手共享同一份数据目录（如共享长期记忆库），实现零拷贝零同步**。全部命令行为实测于 Windows 11（10.0.26200）x64。

## 三种链接对照

| 特性 | 硬链接 Hard Link | 符号链接 Symbolic Link | 目录联接 Junction |
|------|------------------|------------------------|-------------------|
| 适用对象 | 仅文件 | 文件与目录 | **仅目录** |
| 跨卷 | ✗ 同卷内 | ✓ 可跨卷、可指向 UNC/网络路径 | ✗ 仅本地卷 |
| 需要管理员 | ✗ | ✓ 默认需要（或开启开发者模式） | **✗ 免管理员** |
| 目标可不存在（悬空） | ✗ | ✓ | ✓ 创建时目标可先不存在* |
| 典型用途 | 省空间的多份文件名 | 兼容旧路径、指向移动位置 | 应用数据目录共享/搬移 |

\* Junction 指向的目标删除后链接仍在（悬空），访问报错；重建目标目录即恢复。

## 创建与查看

```bat
:: cmd（注意 mklink 参数一律反斜杠路径，正斜杠会被 cmd 当作开关报「无效开关」）
mklink /J "C:\data\link" "C:\data\real"      :: 目录联接
mklink /D "C:\data\link" "C:\data\real"      :: 目录符号链接（需管理员/开发者模式）
mklink /H "C:\data\file.txt" "C:\data\real.txt"  :: 文件硬链接
```

```powershell
# PowerShell（免管理员，推荐脚本中使用）
New-Item -ItemType Junction -Path 'C:\data\link' -Target 'C:\data\real'
Get-Item 'C:\data\link' | Select-Object LinkType, Target   # 查看：Junction + 指向
```

```bat
:: 列出目录下的全部 reparse point（链接与联接都会出现）
dir /AL C:\data
```

**Git Bash / MSYS 环境的坑**：在 Git Bash 里执行 `cmd //c "mklink /J C:/x/y ..."` 会因 cmd 把正斜杠路径段（如 `/Users`）解析为命令开关而报「无效开关」；MSYS 的路径改写也无法纠正 `mklink` 的参数形式。**遇到报错改用 PowerShell 的 `New-Item -ItemType Junction` 最稳。**

## 程序透明性与删除语义（实测）

- **文件级操作会"穿透"链接**：通过链接路径读写、删除某个文件，实际操作的就是目标目录里的文件——这正是"共享目录"的原理，所有程序（含服务、计划任务）经 Win32 文件 API 访问均透明。
- **删除链接本体不会动目标内容**。对指向目录的 Junction 实测（Windows 11）：

| 删除方式 | 结果 |
|----------|------|
| `rmdir <链接>`（不带 /s） | 仅删除链接，目标完好 |
| `rd /s /q <链接>` | 仅删除链接，目标完好 |
| Git Bash `rm -rf <链接>` | 仅删除链接，目标完好 |
| PowerShell `Remove-Item -Recurse -Force <链接>` | 仅删除链接，目标完好 |
| `Remove-Item <链接>\a.txt`（经链接删文件） | **目标中的文件被删除** |

结论：对链接根目录执行递归删除是安全的（只摘除联接点）；但**经链接路径逐个删除/修改文件，作用的就是真实目标**。批量清理前先想清楚操作的是"链接"还是"链接里的内容"。

## 实战：多个 AI 助手共享同一份数据目录

AI 编码助手（如 ZCode、Hermes 等）各自维护一套长期记忆/知识目录。两个助手各存一份必然漂移，每次切换都要手工同步。用 Junction 让其中一个目录成为唯一真源、另一个变成指向它的联接：

1. 选定真源目录（例如助手 A 的记忆目录）；
2. 把助手 B 的同名目录整体移入真源（或确认内容已合并），然后**删除 B 的原目录**；
3. 用 PowerShell 建立联接：`New-Item -ItemType Junction -Path 'B的记忆目录' -Target 'A的记忆目录'`；
4. 此后 B 读写自己的路径，落盘的就是 A 的真源目录——**切换助手零同步**。

配套注意事项：

- **git 仓库侧**：若 B 的目录原本是某个 git 仓库的跟踪对象，换联接后 git 会把联接当普通目录遍历，把共享内容收进 B 的仓库——需在 B 仓库的 `.gitignore` 排除该路径；**`.gitignore` 对已跟踪文件不生效**，需先 `git rm -r --cached <路径>` 再提交；
- 备份/同步工具（网盘、镜像脚本）通常会跟随联接造成同一份数据被重复备份，按需排除；
- 不要让联接指向自己的上级目录（自我嵌套），会造成递归遍历死循环。

## 出处与参考

- [mklink 命令文档（Microsoft Learn）](https://learn.microsoft.com/zh-cn/windows-server/administration/windows-commands/mklink)
- [fsutil reparsepoint 查询（Microsoft Learn）](https://learn.microsoft.com/zh-cn/windows-server/administration/windows-commands/fsutil-reparsepoint)
- [New-Item 建立联接与符号链接（Microsoft Learn）](https://learn.microsoft.com/zh-cn/powershell/module/microsoft.powershell.management/new-item)
- [硬链接、联接与符号链接辨析（Microsoft Learn）](https://learn.microsoft.com/zh-cn/windows/win32/fileio/hard-links-and-junctions)
- 删除语义、免管理员创建、Git Bash 兼容性为本机 Windows 11（10.0.26200）x64 实测结论（2026-09-05）。
