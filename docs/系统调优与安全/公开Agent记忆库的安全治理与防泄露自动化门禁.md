---
applies_to:
  - AI Agent（Hermes / Claude Code / Cursor / ZCode）使用者
  - 拥有跨端长效记忆库的技术开发者
  - 参与开源协同与公共仓库运维的工程师
risk: low
tweak_module: []
---

# 公开 Agent 记忆库的安全治理与防泄露自动化门禁

> 本文系统复盘将本地 AI Agent（如 Hermes、Claude Code、Cursor、ZCode）的跨端长效记忆库推向公共 GitHub 仓库（Public Repository）时面临的数据安全边界挑战；详细阐述单一物理真源与目录联接（NTFS Junction）架构下的隐私分层治理准则，剖析 Windows 环境变量跨平台归一化（`normalize_local_path`）的技术陷阱，并给出全套 CI 自动化防泄露卫生扫描门禁方案。

---

## 一、 背景：跨端 Agent 记忆库公开化的安全挑战

在多智能体协作（如桌面端 Hermes 与开发终端 ZCode）或跨设备办公场景下，维护一套跨会话持久保留的记忆库是消除重复配置、传递系统偏好与沉淀工程经验的关键。

许多团队与个人选择将记忆库托管在 GitHub 上以便多端同步。然而，当仓库从私有（Private）转向公开（Public），或引入社区协同审查时，由于 Agent 拥有自主读写与提交记忆的能力，极易产生严重的安全与隐私事故：

1. **开发机物理路径与用户身份泄漏**：
   - 记忆正文中大范围充斥 `C:\Users\<username>\AppData\...` 或 `D:\Users\<username>\...` 等绝对路径。
   - 暴露个人 PC 的真实系统用户名、盘符划分与桌面资产结构。
2. **凭据与鉴权信息意外入库**：
   - Agent 在记录排障过程或 API 调试经验时，容易无意识将带有的 `Bearer <token>`、GitHub PAT、私钥片断甚至密码字面量直接落盘并提交。
3. **机器绑定假象与可用性崩塌**：
   - 记忆库中包含过度具体的单机物理路径，会导致迁移到新机器、换盘符或在不同操作系统（如 Linux/macOS）下运行时，Agent 误读取失效路径而产生假死或报红。

---

## 二、 记忆库的定位与分层脱敏治理准则

很多开发者面对泄露风险时的第一反应往往是“一刀切正则替换”，试图把所有路径全部替换为类似 `<username>` 或 `<USER_HOME>` 这样的伪占位符。

**这种做法是不可取的。**

AI Agent 的记忆库不是普通静态文档，它是**机器直接读取、用于执行工具调用与指令生成的动态知识库**。如果充斥着不合法的伪占位符，Agent 在读取记忆时就无法还原物理位置，直接丧失可执行性。

### 正确的分层治理准则

```text
┌─────────────────────────────────────────────────────────────────┐
│                    公开 Agent 记忆库内容分类治理                 │
├───────────────────┬─────────────────────────────────────────────┤
│ 1. 面向读者的文档  │ README、项目索引、配置清单、看门报告          │
│    （强制脱敏）   │ ➔ 100% 转换为通用环境变量：%USERPROFILE%、$HOME│
├───────────────────┼─────────────────────────────────────────────┤
│ 2. 记忆正文中的环境│ 开发机用户名 + 具体盘符 + 个人用户目录组合   │
│    （高敏环境信息）│ ➔ 强制规范为：%LOCALAPPDATA%、%USERPROFILE%  │
├───────────────────┼─────────────────────────────────────────────┤
│ 3. 客观技术知识    │ Windows 系统公共目录（C:\Windows\System32）  │
│    （知识事实保留）│ ➔ 完整保留标准路径事实，严禁盲目篡改破坏准确性 │
└───────────────────┴─────────────────────────────────────────────┘
```

- **标准环境变量优先**：
  - Windows 环境统一采用 `%USERPROFILE%`、`%LOCALAPPDATA%`、`%APPDATA%`；
  - POSIX / Linux / macOS 环境统一采用 `$HOME` 或 `~`；
  - 兼顾两者的 Agent 能够透明理解并根据宿主环境动态求值。

---

## 三、 跨平台路径归一化引擎与避坑陷阱

在将配置文件或机器数据中的绝对路径改为 `%USERPROFILE%` 等环境变量时，绝大多数开发者都会踩进一个严重的**运行时代码脱节陷阱**。

### 1. 致命陷阱：操作系统与 Python 不会自动展开环境变量

在 Python 中：
```python
# 致命错误：假设 Python 会自动认识 Windows 环境变量
path = "%USERPROFILE%/.zcode/cli/marketplace.json"
with open(path, "r") as f:  # 立即抛出 FileNotFoundError！
    ...
```
- **文件读取陷阱**：Python 原生的 `open()`、`Path()` 或 `os.path.exists()` 均将 `%USERPROFILE%` 当作纯字面量字符串，绝不会自动求值。
- **跨进程调用陷阱**：Windows 底层的 Win32 API（如 `CreateProcess`）在接收命令行参数数组时，同样不会自动展开参数中的环境变量。若执行：
  ```python
  subprocess.run(["git", "-C", "%LOCALAPPDATA%/hermes", "status"])
  ```
  Git 会把 `%LOCALAPPDATA%` 当作当前目录下的相对子文件夹，直接抛出 `fatal: cannot change to ...: No such file or directory`。

### 2. 规范的跨平台路径归一化实现 (`normalize_local_path`)

在任何代码读取配置或发起子进程调用前，必须通过专门的归一化函数进行清洗：

```python
import os
import re
from pathlib import Path

def normalize_local_path(p: str) -> str:
    """跨平台展开环境变量（%VAR%、$VAR）、~ 用户目录并归一化为当前系统标准路径。"""
    if not p:
        return ""
    
    # 1. 优先使用标准库 expandvars 展开（在 Windows 下能展开 %VAR%，在 Linux 下能展开 $VAR）
    expanded = os.path.expandvars(p)
    
    # 2. 防御性兜底：针对跨平台（如在 Linux CI 或 Bash 环境下解析 Windows 风格 %VAR%）
    if "%" in expanded:
        def _replace_win_env(m):
            var_name = m.group(1)
            # 若系统环境中存在则替换，否则可按需回退到通用默认
            return os.environ.get(var_name, m.group(0))
        expanded = re.sub(r"%([^%]+)%", _replace_win_env, expanded)
        
    # 3. 展开 ~ 符号并消除冗余路径分隔符
    return os.path.normpath(os.path.expanduser(expanded))
```

**工程铁律**：
> **在修改任何配置文件为环境变量前，必须首先在代码层落实路径展开支持与单元测试验证；绝对不能“先改配置、后改代码”。**

---

## 四、 全仓 CI 自动化防泄露卫生扫描门禁

为了确保所有提交物在推送到公共 GitHub 仓库前均经过严格审查，必须将人工防线升级为**代码级自动化门禁（Automated Hygiene Gate）**。

### 1. 静态扫描脚本 (`scripts/check_hygiene.py`)
利用 Python 扫描所有已纳入 Git 跟踪的文件（`git ls-files`），对高敏开发机用户名、私人路径与常见格式的 Token 进行严格正则比对：

```python
#!/usr/bin/env python3
"""Public repository hygiene and security scan."""
import os
import re
import subprocess
import sys

# 高危泄露匹配规则
SENSITIVE_PATTERNS = [
    # 1. 个人开发机用户名与盘符硬编码拦截
    (r"[C-Z]:[/\\]Users[/\\](?!Public|Default|All Users)[a-zA-Z0-9_\-]+[/\\]", "Hardcoded machine username path"),
    # 2. 真实 GitHub Token
    (r"ghp_[A-Za-z0-9]{20,}", "GitHub Personal Access Token"),
    (r"github_pat_[A-Za-z0-9_]{30,}", "GitHub Fine-Grained Token"),
    # 3. 云厂商与私钥块
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "Private key block"),
]

def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 仅扫描已跟踪文件，避免扫描本地临时未跟踪的调试文件
    res = subprocess.run(
        ["git", "-C", repo_root, "ls-files"],
        capture_output=True, text=True, check=True
    )
    tracked_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    violations = []
    for rel_path in tracked_files:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.isfile(full_path):
            continue
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except UnicodeDecodeError:
            continue  # 跳过二进制文件

        for pattern, desc in SENSITIVE_PATTERNS:
            for m in re.finditer(pattern, content, re.IGNORECASE):
                line_no = content[:m.start()].count("\n") + 1
                violations.append(f"{rel_path}:{line_no} - {desc}: '{m.group(0)}'")

    if violations:
        print(f"❌ Hygiene scan failed! Found {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")
        sys.exit(1)

    print(f"✅ Hygiene scan passed: scanned {len(tracked_files)} tracked files, 0 violations found.")

if __name__ == "__main__":
    main()
```

### 2. GitHub Actions 强制卡点 (`.github/workflows/ci.yml`)

在每次代码 `push` 与 `pull_request` 时，自动启动轻量 Ubuntu Runner，耗时仅需数秒即可完成全仓体检：

```yaml
name: CI & Hygiene Check

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  hygiene:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

      - name: Set up Python
        uses: actions/setup-python@42375524e23c412d93fb67b49958b491fce71c38 # v5.4.0
        with:
          python-version: '3.11'

      - name: 运行全仓防泄露与敏感路径门禁
        run: python scripts/check_hygiene.py

      - name: 验证配置清单语法与本地解析器
        run: python scripts/check_capability_upstream.py --local-only
```

---

## 五、 治理总结与长效建议

1. **制度铁律入魂**：
   - 将“记忆写入前必须执行标准环境变量转换”写入 Agent 的系统人设提示词（如 `SOUL.md`）与操作规程（`SKILL.md`），确保 Agent 在初次组织文本时就天然具备脱敏意识。
2. **拒绝盲目全量抹除**：
   - 保护 Agent 对操作系统客观知识（如 `C:\Windows\System32` 或注册表键）的引用，仅对个人用户目录实施环境变量化。
3. **自动化守护兜底**：
   - 永远不要信任“人工自查”，将卫生扫描固化为 Git Hook 或 CI 自动化门禁，是防范公共仓库数据泄露事故的唯一可靠闭环。
