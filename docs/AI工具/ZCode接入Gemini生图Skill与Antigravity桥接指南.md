---
applies_to:
  - Windows 10/11
  - ZCode
  - ZCode-Antigravity
  - Google Gemini (gemini-3.1-flash-image / Nano Banana 2)
risk: low
tweak_module: []
---

# ZCode 接入 Gemini 生图 Skill 与 Antigravity 桥接指南

> 本文目标：在 ZCode 中为 Agent 配置**原生文生图能力**，打通从自然语言指令到通过 **`gemini-3.1-flash-image`（Nano Banana 2）** 生成图片并自动保存在本地工作区的完整链路。
>
> 实测环境：Windows 11 / ZCode / ZCode-Antigravity 订阅桥接 / Python 3.14。文中所有配置与排错均经真机实测验证。

---

## 一、核心原理与认知前置

### 1. 为什么有生图模型却在 ZCode 对话中“看不到图”？

在开发或使用 AI 智能体时，经常会遇到“模型宣传具备生图能力，但让 Agent 画图时却只返回文本描述，甚至产生幻觉”的现象。

核心原因在于 **“底层大模型的 API 模态” 与 “Agent 客户端的工具链（Harness/Tool）” 存在脱节**：

```text
[用户指令] "画一张利姆路魔王办公室的图"
    │
    ▼
[ZCode 对话环境] ──(纯文本与 Tool-Calling 交互)──> [大语言模型]
    │                                                    │
    │  没有可执行工具时，模型只能用语言描述画面（幻觉）     │
    │                                                    │
    ▼                                                    ▼
[无法向本地写文件] <─────────────────────────────────────┘
```

* **ZCode 是基于 Tool-Calling 的代码智能体环境**：Agent 接收文本指令，通过调用系统工具（Bash、Write 等）或 Skill/MCP 来修改磁盘文件或执行任务。
* **要让 Agent 真正输出图片**：必须为 Agent 提供一个**生图 Skill（或 MCP 工具）**。Agent 在理解绘画意图后，负责组织英文 Prompt 并调用后台脚本，后台脚本向生图后端 API 请求图片二进制数据并存为本地文件，最终呈现给用户。

### 2. 主控模型 vs 生图后端解耦

在 ZCode 的架构中，两者是完全独立的：

| 角色 | 职责 | 本文方案配置 |
| :--- | :--- | :--- |
| **主控对话模型 (Chat Controller)** | 负责日常对话、意图识别、优化 Prompt、触发工具调用 | `gemini-3.7-flash` / `gemini-3.8-flash` 等 |
| **生图后端 (Image Generation Backend)** | 接收 Prompt 并计算生成图片 Base64/二进制数据 | `gemini-3.1-flash-image` (Nano Banana 2) |

无论主控模型使用的是 Gemini、GLM、DeepSeek 还是 Claude，只要挂载了对应的生图 Skill，均可自由驱动生图后端出图。

---

## 二、常见生图方案对比与选型

| 方案 | 生图后端 | 优点 | 局限与避坑点 |
| :--- | :--- | :--- | :--- |
| **`zcode-vision-bridge`** | 智谱 BigModel (CogView-3/4 / GLM-Image) | 适合智谱生态用户，兼具识图与生图 | 原版只支持智谱 API，不支持 Google 端点 |
| **直连 Google AI Studio** | Google 官方 (`imagen-3.0-generate-002`) | 官方原生接口 | **国内网络限制严格**：极易触发 `400: User location is not supported for the API use` 地区封锁 |
| **`ZCode-Antigravity` 本地桥接 (推荐)** | `gemini-3.1-flash-image` | **免受地域封锁**，复用已有 Gemini 订阅，本地低延迟直接返回 Base64 | 需编写轻量 Skill 脚本对接本地代理接口 |

---

## 三、整体数据链路

```text
[用户发出画图指令]
        │
        ▼
[ZCode Agent] ──(自动触发)──> [Skill: gemini-image-gen]
                                     │
                                     ▼ (执行 Python 脚本)
                      [generate_image.py]
                                     │
                                     ▼ (POST /v1/chat/completions)
                   [ZCode-Antigravity 本地桥接] (http://127.0.0.1:18080)
                                     │
                                     ▼ (调用 Google 远端接口)
                         [gemini-3.1-flash-image]
                                     │
                                     ▼ (返回包含 data:image/jpeg;base64 的 JSON)
                      [Python 脚本解码并保存]
                                     │
                                     ▼
                   [本地文件: ./generated_images/xxx.jpg]
                                     │
                                     ▼
                      [ZCode 渲染展示 Markdown 预览]
```

---

## 四、具体实施与配置步骤

### 1. 确认 ZCode-Antigravity 桥接状态

检查本地 `ZCodeAntigravity` 配置文件（位于 `C:\Users\<用户名>\AppData\Local\ZCodeAntigravity\config.yaml`）：

1. 确认监听端口（默认通常为 `18080`）：
   ```yaml
   host: "127.0.0.1"
   port: 18080
   ```
2. 确认 API Key（在 `api-keys:` 列表下方，形如 `wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0`）。

### 2. 创建 Skill 目录结构

在用户全局技能目录 `~/.zcode/skills/gemini-image-gen/`（即 `C:\Users\<用户名>\.zcode\skills\gemini-image-gen\`）下创建两个文件：

```text
~/.zcode/skills/gemini-image-gen/
├── SKILL.md              # ZCode 技能定义与调度规范
└── generate_image.py     # Python 生图执行脚本
```

### 3. 编写 `SKILL.md`

`SKILL.md` 用于向 ZCode Agent 注册该技能的触发时机与调用规范：

```markdown
---
name: gemini-image-gen
description: Use this skill whenever the user asks to generate, draw, paint, or render an image, illustration, anime art, or photo using Google Gemini / Imagen 3 backend.
---

# Gemini Image Generation Skill

Use this skill to generate high quality images using Google's Imagen 3 / Gemini Image API and save them directly to the local workspace.

## How to execute

Run the generation script via Bash tool:

```bash
python "C:/Users/VOS-User/.zcode/skills/gemini-image-gen/generate_image.py" --prompt "YOUR_DETAILED_PROMPT" --output-dir "generated_images" --output-name "custom_name"
```

### Parameters
- `--prompt` (必填): 详细的英文提示词，包含主体、画风、材质、光影及构图。
- `--output-dir`: 保存目标文件夹（默认 `./generated_images`）。
- `--output-name`: 自定义保存文件名（不含扩展名）。
- `--model`: 默认为 `gemini-3.1-flash-image`。

### When Executing
1. 调用 Bash 执行上述脚本。
2. 读取脚本输出的 JSON 结果。
3. 成功后以 Markdown 图片/链接格式返回给用户展示：`![image](path/to/image.jpg)`。
```

### 4. 编写 `generate_image.py`

脚本负责自动读取 Antigravity 配置、组装请求、请求本地代理并保存 Base64 图片：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini / Nano Banana 2 Image Generation Script for ZCode Antigravity Bridge
"""

import os
import sys
import json
import base64
import argparse
from datetime import datetime
import requests

LOCAL_BRIDGE_URL = "http://127.0.0.1:18080"
LOCAL_BRIDGE_KEY = "wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0"

def get_bridge_config():
    antigravity_config = os.path.expanduser("~/AppData/Local/ZCodeAntigravity/config.yaml")
    base_url = LOCAL_BRIDGE_URL
    api_key = LOCAL_BRIDGE_KEY

    if os.path.exists(antigravity_config):
        try:
            with open(antigravity_config, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("port:"):
                        port = line.split(":", 1)[1].strip().strip('"')
                        base_url = f"http://127.0.0.1:{port}"
                    elif line.startswith("- \"") and len(line) > 10:
                        api_key = line.strip("- ").strip('"')
        except Exception:
            pass

    return base_url, api_key

def generate_via_antigravity(prompt, base_url, api_key, model="gemini-3.1-flash-image", timeout=60):
    url = f"{base_url}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise Exception(f"Antigravity Bridge Error ({response.status_code}): {response.text}")
        
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise Exception("No choices returned by Antigravity Bridge")
        
    msg = choices[0].get("message", {})
    images = []
    
    # 提取 choices[0].message.images 中的 Base64
    if "images" in msg and msg["images"]:
        for img_obj in msg["images"]:
            url_val = img_obj.get("image_url", {}).get("url", "")
            if url_val.startswith("data:image"):
                header, b64_data = url_val.split(",", 1)
                mime = "image/jpeg" if "jpeg" in header or "jpg" in header else "image/png"
                images.append((base64.b64decode(b64_data), mime))
            elif url_val.startswith("http"):
                r = requests.get(url_val, timeout=30)
                images.append((r.content, "image/jpeg"))
                
    if not images:
        raise Exception(f"No image was generated. Model reply: {msg.get('content')}")
        
    return images

def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini / Antigravity Bridge")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--model", "-m", default="gemini-3.1-flash-image", help="Model name")
    parser.add_argument("--output-dir", "-o", default="generated_images", help="Output directory")
    parser.add_argument("--output-name", "-n", default=None, help="Output file name")
    parser.add_argument("--base-url", default=None, help="Antigravity bridge base URL")
    parser.add_argument("--api-key", "-k", default=None, help="Antigravity bridge API key")
    
    args = parser.parse_args()
    
    base_url, api_key = get_bridge_config()
    if args.base_url:
        base_url = args.base_url
    if args.api_key:
        api_key = args.api_key
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        images = generate_via_antigravity(args.prompt, base_url, api_key, model=args.model)
        
        saved_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for i, (img_bytes, mime) in enumerate(images):
            ext = "png" if "png" in mime else "jpg"
            if args.output_name:
                filename = f"{args.output_name}.{ext}" if not args.output_name.endswith(f".{ext}") else args.output_name
            else:
                filename = f"gemini_image_{timestamp}_{i+1}.{ext}"
                
            filepath = os.path.abspath(os.path.join(args.output_dir, filename))
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            saved_paths.append(filepath)
            
        print(json.dumps({
            "status": "success",
            "model": args.model,
            "prompt": args.prompt,
            "images": saved_paths
        }, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "error_type": "GENERATION_FAILED",
            "message": str(e)
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 五、实机踩坑与排错速查表

| 报错现象 | 根本原因 | 解决办法 |
| :--- | :--- | :--- |
| **`401: Invalid API key`** | API Key 复制错误或大小写不一致（例如混淆了 `XdFf` 与 `XDff`）。 | 检查 `config.yaml` 中的实际字符串，或直接从配置文件动态读取。 |
| **`400: Model is not supported on /v1/images/generations`** | Antigravity 桥接中的 `gemini-3.1-flash-image` 走的是对话多模态补全协议，不支持 OpenAI 标准的生图端点。 | 将请求端点由 `/v1/images/generations` 改为 `/v1/chat/completions`，并在返回的 `choices[0].message.images` 中提取 Base64。 |
| **`400: User location is not supported for the API use`** | 直连 Google AI Studio 时，出口代理 IP 处于非支持地区（如部分机房 IP）。 | 使用本方案通过本地 Antigravity 桥接服务中转，自动规避原生地域检测。 |
| **生图质量不够细腻或风格偏差** | 提示词过于简短或使用纯中文短语。 | 让 Agent 在触发 Skill 时将提示词优化扩展为包含**艺术风格（如 3D anime comic style）、渲染引擎（octane render / Unreal Engine 5）、光影（cinematic lighting）及构图**的完整英文 Prompt。 |
