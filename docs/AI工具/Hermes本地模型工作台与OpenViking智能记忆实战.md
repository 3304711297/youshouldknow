---
applies_to:
  - Windows 10/11
  - hermes-agent（NousResearch）
  - llama.cpp
  - OpenViking
risk: low
tweak_module: []
status: reference
---

# Hermes 本地模型工作台与 OpenViking 智能记忆检索实战

> 本文目标：完整记录在 Windows 11 环境下，为 Hermes Agent 搭建**本地 llama.cpp CUDA 硬件加速模型工作台**，并将双端共享记忆库接入 **OpenViking 智能语义层级检索** 与 **Serverless 懒人网关（按需唤醒 + 空闲休眠）** 的工程落地全流程。解决三大核心痛点：C 盘空间紧张、大模型显存霸占，以及长文本记忆库检索时的 Token 暴击与关键词错失。

---

## 一、架构总览与分层设计

传统基于全局文本匹配（Grep）的 Agent 记忆管理在文档规模扩大后，面临两大死穴：一是关键词不匹配时完全搜空，二是单次读取整篇长文档造成几十 KB 的 Prompt 膨胀，挤占主模型注意力。

本文采用**二级派生索引架构**，将 Git 仓库确立为唯一真源，OpenViking 作为检索层，并在前端架设自愈网关：

```text
       shared-agent-memory (Git main 分支 —— 唯一物理真源 SSOT)
                         │
        ┌────────────────┴────────────────┐
 [即时驱动] post-commit / post-merge   [探活校准] HEAD SHA 对比
        │                                 │
        └────────────────┬────────────────┘
                         ↓ (单向注入，严禁反向覆盖 Git)
       本地 BGE-M3 (RTX 4070 Laptop, CUDA 加速, 端口 18082, 1024维向量)
                         +
       本地 Gemini 3.8 Flash (端口 18080, 秒级 L0/L1 摘要提炼)
                         │
                         ↓
       OpenViking 核心服务 (HTTP 127.0.0.1:1934, 独立 venv)
       虚拟文件系统: viking://resources/shared-memory/
                         │
                         ↓
       Serverless 懒加载网关 (HTTP 127.0.0.1:1933)
       - 提问时按需自动唤醒 18082 与 1934
       - 2 分钟空闲自动杀进程、100% 释放 GPU 显存
                         │
                         ↓
       Hermes 原生 Memory Provider (openviking 插件, 保守召回策略)
```

---

## 二、C 盘空间治理：NTFS Junction 透明重定向

Hermes Desktop 默认将本地模型与运行时引擎存放在系统盘用户目录（`C:\Users\<user>\AppData\Local\hermes\`）。动辄数十 GB 的模型会迅速吃紧 C 盘。

利用 Windows 原生 NTFS 目录联接（Junction），可在不侵入修改任何应用源码的前提下，将存储物理转移至 D 盘：

```cmd
:: 创建 D 盘物理目标目录并建立软链接
mkdir D:\HermesModels
mkdir D:\HermesRuntimes

mklink /J C:\Users\<user>\AppData\Local\hermes\models D:\HermesModels
mklink /J C:\Users\<user>\AppData\Local\hermes\runtimes D:\HermesRuntimes
```

* **效果验证**：后续通过客户端下载的任何 GGUF 模型、临时 `.part` 文件及解压后的 llama.cpp CUDA 二进制引擎，**对 C 盘的空间占用均为 0 字节**。

---

## 三、8GB 显存适配黄金法则与模型选型

以移动端主流的 **RTX 4070 Laptop (8GB 显存) + 24GB 内存** 为例，本地运行大模型切忌盲目追求参数量：

1. **黄金参数上限**：单模型体积宜控制在 **≤ 5.5GB**。8GB 显存扣除系统与桌面开销（约 1GB），剩余约 7GB，模型加载占 5GB，保留 2GB 供 KV Cache，可达成 **100% 纯 GPU 满血运行**（45~60 tokens/s），风扇不啸叫、机器不发烫。
2. **拒绝传统 27B/35B Dense 模型**：超过 8G 必须借用系统内存（总线带宽仅 60GB/s），生成速度暴跌至 4~8 tokens/s，体验断崖。
3. **MoE 混合专家架构的例外**：参数量虽大，但若为稀疏激活（如 `Qwen3-Coder-30B-A3B`，实际每次仅激活 3B），仍能保持 20+ tokens/s 的可用速度。

### 推荐落地模型组合

| 模型分类 | 具体推荐 GGUF 文件 | 体积 | 特点与定位 |
| :--- | :--- | :--- | :--- |
| **向量检索** | `gpustack/bge-m3-Q8_0.gguf` | 605 MB | 1024 维高精多语言嵌入，8G 显存毫无压力，2ms 极速响应 |
| **通用推理** | `unsloth/Qwen3.5-9B-Q4_K_M.gguf` | 5.3 GB | 纯显存满血运行，代码与工具调用强劲，带完整思考链 |
| **深度思考** | `unsloth/DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf` | 4.4 GB | 离线深度逻辑推演，完整输出 `<think>` 思维过程 |

---

## 四、OpenViking 语义层级检索与本地向量加速

### 1. llama-server 向量批处理陷阱规避
OpenViking 摄入长 Markdown 知识文档时，单次请求包含大量上下文。`llama-server` 默认批大小为 512，会导致：
`input (2356 tokens) is too large to process. increase the physical batch size`

必须显式启动并调大批处理参数：
```bash
llama-server.exe -m D:\HermesModels\bge-m3-Q8_0.gguf --embedding --port 18082 --host 127.0.0.1 -c 8192 -b 8192 --ubatch-size 8192 -ngl 99
```

### 2. OpenViking 服务配置（ov.conf）
将向量端点指向本地 18082，摘要提炼（VLM）指向本地网关提供的 Gemini 3.8 Flash：
```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 1934
  },
  "storage": {
    "workspace": "C:/Users/VOS-User/.openviking/data"
  },
  "embedding": {
    "dense": {
      "provider": "openai",
      "api_base": "http://127.0.0.1:18082/v1",
      "api_key": "local",
      "model": "bge-m3",
      "dimension": 1024
    }
  },
  "vlm": {
    "provider": "openai",
    "api_base": "http://127.0.0.1:18080/v1",
    "api_key": "<GATEWAY_KEY>",
    "model": "gemini-3.8-flash"
  }
}
```

### 3. L0 / L1 / L2 阶梯式 Token 节省
文档导入至 `viking://resources/shared-memory/` 后，系统自动生成三层表示：
- **L0（~100 tokens）**：一句话摘要，检索召回首选；
- **L1（~2k tokens）**：结构大纲，决策规划参考；
- **L2**：原始全文，仅在精准钻取时加载。

---

## 五、Serverless 懒人网关：按需自动唤醒与空闲休眠

为了实现“不用时 0 显存、用时免人工干预”，在前端设计了轻量代理网关（监听标准 1933 端口）：

### 1. 运行机制
1. **冷启动唤醒**：Hermes 向 `127.0.0.1:1933` 发送检索请求时，网关检测到底层 18082 与 1934 处于离线状态，立即在后台以 `CREATE_NO_WINDOW` 静默拉起服务，并在 5~6 秒内就绪并转发响应；
2. **空闲倒计时回收**：网关内置心跳检测，若连续 **2 分钟**没有新的记忆库交互，自动执行终止指令杀掉底层进程，**100% 释放 800MB 显存**；
3. **开机自启**：在 `Startup` 目录放置 `.vbs` 脚本静默拉起网关，由于网关本身仅占约 15MB 内存且 CPU 占用为 0%，用户日常完全无感。

### 2. 警惕客户端「本地运行时」常驻吃爆内存陷阱
在 Hermes 客户端「提供方 → 本地模型」界面中，若开启「已安装 llama.cpp 运行时」，Hermes 会在后台常驻拉起 `llama-server.exe` 并加载完整的 7B/9B 聊天模型，**常驻吃掉近 3GB（2,911 MB）系统内存**！
- **避坑准则**：对话模型由用户按需随时自由切换，切勿为了本地聊天而长期开启常驻引擎；
- 该客户端常驻开关**必须显式关闭**（点击「■ 关闭」按钮，或设置 `local_runtime.enabled: false`）；
- 记忆向量化仅由上述 2 分钟 Serverless 懒人网关管理，绝不让本地聊天大模型在后台长期吞噬内存。

---

## 六、Hermes 召回策略与双端防漂移

### 1. Hermes 保守召回配置
在 `config.yaml` 中配置，防止历史碎片过度污染主会话：
```yaml
memory:
  provider: openviking
  openviking:
    endpoint: http://127.0.0.1:1933
    recall_limit: 3
    recall_score_threshold: 0.35
    recall_prefer_abstract: true
    recall_resources: true
    recall_timeout_seconds: 15.0
```

### 2. Git 双驱动增量同步
- **即时驱动**：在 Git 仓库部署 `post-commit` 与 `post-merge` 钩子，本地或外部提交后自动触发后台增量重扫；
- **探活对比**：比对当前仓库 HEAD SHA 与上次同步记录，相同 commit 秒级跳过，杜绝重复计算。

---

## 七、运维命令速查

| 操作 | 命令 |
| :--- | :--- |
| **检查服务状态** | `python scripts/openviking_service.py status` |
| **手动重启服务** | `python scripts/openviking_service.py restart` |
| **验证语义检索** | `ov.exe find "检索关键词"` |
| **强制全量同步** | `python scripts/sync_shared_memory_openviking.py --force` |
| **检查 Hermes 状态** | `hermes memory status` |
