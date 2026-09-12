---
applies_to:
  - Windows 10/11
  - macOS / Linux（概念通用，命令以 Windows 为主）
  - 本地 HTTP 代理客户端（Clash / Karing / v2rayN 等混合端口方案）
  - Rust reqwest / Python httpx、requests / Node.js undici 使用者
risk: low
tweak_module: []
---

# 本地代理环境下的 NO_PROXY 白名单与程序库代理行为

> 本文目标：解决《Windows 命令行工具的代理行为差异速查》**未覆盖的两层盲区**——一是"怎么让指定目标**不走**代理"（`NO_PROXY` 白名单），二是"程序**内部 HTTP 库**"（而非命令行命令）的代理行为差异。
>
> 典型故障现象：代理软件开着但没连节点，本地反代服务的健康检查就卡死、客户端报"内核未启动"；或 `pip` 能查到包却死活下载不下来。这类问题用命令行视角排查会完全走偏，因为**真正的差异发生在程序库层**。
>
> 文中每条结论均附本机实测记录，不含推测。

## 一、为什么需要 NO_PROXY：代理不是"全有或全无"

设置环境变量代理时，大多数人只配了正向的三件套：

```text
HTTP_PROXY  = http://127.0.0.1:<端口>
HTTPS_PROXY = http://127.0.0.1:<端口>
ALL_PROXY   = http://127.0.0.1:<端口>
```

这等于告诉所有兼容程序："**所有**出站请求都交给这个端口"。问题随之而来——**本机环回（127.0.0.1）的请求也被送进了代理**。

一旦代理软件处于"端口在监听、但上游节点不通"的状态（例如打开了客户端却没连接节点），本机服务之间的互相调用就会全部卡死在代理上。

`NO_PROXY` 就是用来声明例外的：

```text
NO_PROXY = 127.0.0.1,localhost,::1,copilot.tencent.com,.tencent.com,pypi.org,files.pythonhosted.org
```

规则要点（与 curl / reqwest 等主流实现一致）：

- 逗号分隔，空白会被忽略；
- 支持 IP、CIDR（如 `192.168.1.0/24`）；
- 域名条目**带不带前导点等价**（`google.com` 与 `.google.com` 都匹配自身及所有子域）；
- `*` 是唯一通配符，意为匹配所有主机名（等于全局关闭代理）。

## 二、致命陷阱：端口在监听 ≠ 代理能用

这是排查此类故障时最容易误判的一点。

代理客户端即使**没有连接任何节点**，它的本地混合端口**依然处于 LISTENING 状态**。于是：

| 你以为 | 实际 |
| --- | --- |
| 端口通 = 代理正常 | 端口通只是进程活着，上游可能全挂 |
| `curl -x` 会立刻报错 | 会**挂满整个超时周期**（常见 15s）才失败 |
| 关掉代理软件＝清掉代理 | 环境变量仍在，端口可能仍被占用 |

因此《速查》里"用 `curl -sI -x` 返回 200 判断代理可用"这一步，在本场景下会让你干等 15 秒然后得到超时，**且超时并不能区分"代理没起"和"代理起了但节点不通"**。

正确的判据是**对照实验**：同时测一个必须走代理的境外目标和一个必须直连的境内目标。

```bash
curl -4 -s -o /dev/null -w "google %{http_code}\n" --max-time 8 --noproxy '*' https://www.google.com/generate_204
curl -4 -s -o /dev/null -w "baidu  %{http_code}\n" --max-time 8 --noproxy '*' https://www.baidu.com
```

- `google 000` + `baidu 200` → 代理未接管或节点未连，网络本身正常；
- `google 200` → 代理正在工作。

## 三、真正的分水岭：程序库层的行为差异

命令行工具的差异已有《速查》覆盖，但**同一个进程内部用什么 HTTP 库**，才是本类故障的决定性因素。同一台机器、同一套环境变量，实测行为可以完全相反：

| HTTP 库 | 是否读环境变量代理 | 实测表现 |
| --- | --- | --- |
| **Rust `reqwest`** | ✅ 读（`trust_env` 默认开启） | 访问 `127.0.0.1` 的本机请求**也会被送去代理**；默认读取 `NO_PROXY` |
| **Python `httpx` 0.28** | ⚠️ 版本相关，实测未走 | 同环境下 `_mounts` 的 proxy 均为 `None`，本机请求直连成功。⚠️ 勘误补充（2026-09-12 对照官方文档）：httpx **默认读环境变量代理**（`trust_env=True`）；实测未走的原因是 `Client` 在**构造时**读取环境变量生成 mounts——若客户端创建早于代理变量注入（如应用启动先于代理配置、GUI 启动未继承 shell 环境），mounts 即为 None。判断依据应是「Client 构造时环境变量是否已就位」 |
| **Python `requests` 2.33** | ✅ 读（`trust_env` 默认 True） | 但会话 `proxies` 为空时表现为直连，需按实际验证 |
| **Node.js `undici` / 内置 `fetch`** | ❌ 两者都不读 | 必须显式构造 `ProxyAgent` |

**这条表解释了一个经典现象**：同一个应用里，聊天功能正常（Python 侧直连上游），但"启动内核/健康检查"却失败（Rust 侧走了代理）。表象是"软件坏了"，实质是**两个模块用了不同的 HTTP 库**。

排查心法：**先分清这个进程用的是哪个 HTTP 库，再谈代理**。

### 代码层面的根治手段

在 Rust 侧，与其依赖用户配好 `NO_PROXY`，不如让访问本机与国内上游的客户端**显式绕过代理**：

```rust
// 本机环回直连：不受环境代理影响
let client = reqwest::Client::builder()
    .no_proxy()
    .timeout(std::time::Duration::from_secs(10))
    .build()?;
```

`reqwest` 的 `Proxy::no_proxy()` 对应 `NoProxy::from_env()`，会解析 `NO_PROXY`/`no_proxy`；而 `ClientBuilder::no_proxy()` 则更彻底——**完全不启用任何代理**，适合确认应该直连的目标。

## 四、pip 的双域名陷阱：只配一个会"半通"

这是 `NO_PROXY` 配置里最容易漏的一处，且失败形态极具迷惑性。

`pip` 一次安装涉及**两个不同的域名**：

| 域名 | 角色 | 必要？ |
| --- | --- | --- |
| `pypi.org` | 索引服务器（查询包版本、获取下载地址） | ✅ |
| `files.pythonhosted.org` | **CDN，实际下载 wheel/sdist** | ✅ |

> ⚠️ 注意是 **`.org` 不是 `.com`**。`files.pythonhosted.com` 这个域名并不存在（实测连接失败），凭印象填写会得到一条永远不生效的白名单。

用 `pip download -v` 可以确认实际下载走的 host，输出中只会出现 `https://files.pythonhosted.org`。

**只把 `pypi.org` 加进白名单会怎样**（对照实验）：

```text
# 索引阶段：成功（pypi.org 已放行）
Collecting six
# 下载阶段：全部失败（CDN 仍被送去不通的代理）
WARNING: Retrying (Retry(total=4, ...)) after connection broken by
'NewConnectionError(... port=3067 ... 由于目标计算机积极拒绝，无法连接')':
/packages/.../six-1.17.0-py2.py3-none-any.whl.metadata
ERROR: No matching distribution found for six
```

表现为"**能查到包、但下载不下来**"。两个域名都加才成功：

```text
Successfully downloaded six
six-1.17.0-py2.py3-none-any.whl    # 11050 字节落盘
```

同理，若配置了国内镜像（`pip.ini` 的 `index-url`），白名单要填的应是**镜像域名**而非官方域名。

## 五、实践建议：白名单该怎么填

按"是否真的需要代理"来划分，而不是拍脑袋：

| 类别 | 建议 | 理由 |
| --- | --- | --- |
| 本机环回 `127.0.0.1` / `localhost` / `::1` | ✅ 必加 | 本机服务互调绝不该绕代理 |
| 国内可直连的服务域名 | ✅ 加 | 少一跳，且避免代理故障时被牵连 |
| 包管理器域名（含其 CDN） | ✅ 加 | 须把索引域与下载域**都**加上 |
| 明确需要翻墙的域名 | ❌ 不加 | 加了反而强制直连导致失败 |
| 时通时不通的境外域名 | ❌ **不加** | 见下 |

**最后一行是反直觉但关键的**：像 `github.com` 这类"偶尔能直连、常态被墙"的域名，**不要**加进 `NO_PROXY`。因为一旦加入，就会强制它永远走直连——在它被墙的时候反而彻底连不上，而走代理至少还有机会。判断标准是**常态**而非当前一时的连通性。

此类域名不挂代理时的临时处理：

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY git push
```

## 六、配置生效的三个坑

1. **`setx` 不影响已运行进程**。写入注册表后，当前终端与所有既有进程仍用旧值——这会让人误判"配置没生效"。
   验证要用**新启动的进程**读取，或直接查注册表：

   ```python
   import winreg
   k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment')
   print(winreg.QueryValueEx(k, 'NO_PROXY')[0])
   ```

2. **大小写两套变量都要写**。部分实现优先读 `NO_PROXY`，缺失时才回退 `no_proxy`，安全做法是**同时设置**。

3. **区分"环境变量代理"与"配置文件里写死的代理"**。某些服务在自身配置文件中显式指定了 `proxy-url`，这类配置**不受 `NO_PROXY` 影响**——它本来就是设计成必须走代理的（例如访问境外 API 的网关）。排查时要两边都看，别只盯着环境变量。

## 七、事实核查与实测记录

- "`reqwest` 读 `ALL_PROXY`，导致本机 127.0.0.1 请求被代理"：✅ 实测（全局 `ALL_PROXY` 下，健康检查请求出现在代理核心日志中，节点不通时 15s 超时）。
- "httpx 0.28.1 在同环境未走代理"：✅ 实测（`Client._mounts` 的 proxy 均为 `None`；本机请求 0.076s 返回 200）。
- "代理未连节点时混合端口仍 LISTENING"：✅ 实测（`netstat` 显示 LISTENING，同时所有境外请求超时）。
- "仅配置 `pypi.org` 会导致能查不能下载"：✅ 实测（对照组全量 Retry 失败；补齐 CDN 域名后成功落盘 11050 字节）。
- "`files.pythonhosted.com` 不存在"：✅ 实测（连接失败；`.org` 返回 200）。
- "`NO_PROXY` 域名前导点等价、逗号分隔"：✅ 依据 curl 与 reqwest 官方文档。
- 库版本迭代可能改变默认行为，以实际 `--version` 与官方文档为准。

## 八、参考链接

- [curl 手册：`NO_PROXY` 环境变量](https://curl.se/docs/manpage.html)
- [reqwest 文档：`NoProxy`](https://docs.rs/reqwest/latest/reqwest/struct.NoProxy.html)
- [httpx 文档：HTTP Proxying / `trust_env`](https://www.python-httpx.org/advanced/proxies/)
- [PyPI：官方索引与文件托管域名说明](https://pypi.org/)
