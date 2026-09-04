---
applies_to:
  - Windows 10/11
  - Google Antigravity / EasyCLIProxyAPI 使用者
  - Hermes Agent 桌面端使用者
risk: low
tweak_module: []
---

# Google Antigravity 与 CloudCode PA 双配额池隔离陷阱与实时监控

> 本文目标：讲清使用 Google 官方 OAuth 凭据监控 Antigravity 配额时一个极易踩坑的现象——**同一账号、同一 Token，请求 `cloudcode-pa` 与 `daily-cloudcode-pa` 会返回完全不同、各自独立的剩余配额与重置时间**；解析 Google 云端多配额桶（Quota Bucket）机制，并给出桌面微服务无阻直连与持久化监控方案。
>
> 实测环境：Google AI Pro 个人订阅 / EasyCLIProxyAPI 0.2.71 (Core 7.2.149) / Windows 11 / Hermes Agent 桌面端。

## 一、 现象直击：为什么查出的额度两边不一样？

在开发或配置桌面端额度悬浮卡片时，很多开发者会直接调用 Google 官方提供的配额汇总接口：`retrieveUserQuotaSummary`。但在实际调用中，会出现让人极为困惑的现象：

| 监控端点 | 请求目标 | 真实返回结果（以 Pro 订阅实测为例） |
| :--- | :--- | :--- |
| `https://cloudcode-pa.googleapis.com/...` | **通用 CloudCode 生产服务** | 5h 剩余 **100%** / 周剩余 **43%**<br>重置点：`09/09 16:07` |
| `https://daily-cloudcode-pa.googleapis.com/...` | **Antigravity 专有服务集群** | 5h 剩余 **74%** / 周剩余 **87%**<br>重置点：`09/04 19:03` / `09/11 09:03` |

- **直观矛盾**：明明是同一个 Google 邮箱账号，拿着同一串 `ya29...` 访问令牌，在同一秒内发起请求，为什么一个显示周配额仅剩 43%，另一个显示周配额还有 87%？
- **根因锁定**：**Google 云端按业务接入场景划分了完全解耦的独立配额池（Quota Buckets）**。

## 二、 核心机制剖析

### 1. 双微服务集群与配额隔离
- **`cloudcode-pa.googleapis.com`**：面向通用 Google Cloud Code 插件（如 VS Code / IntelliJ 原生 Cloud Code 插件）以及通用开发者的通用配额服务；
- **`daily-cloudcode-pa.googleapis.com`**：Antigravity 订阅计划专用的配额与模型路由通道。无论是在网页端、官方客户端还是通过 EasyCLIProxyAPI 代理网关，用户通过 Antigravity 调用的 Gemini 3.8/3.7/3.6 等模型，其消耗全部扣减在 `daily-cloudcode-pa` 的配额桶内。

### 2. 配额桶模型设计
在返回的 JSON 结构中，包含两组模型桶（Buckets）：
1. **Gemini Models**：
   - `gemini-5h`（5小时滚动时间窗口）：平滑瞬时爆发请求，防止单用户突发流量拥塞集群；
   - `gemini-weekly`（每周总配额窗口）：对应订阅层级（如 Google AI Pro）的周调用总量基准。
2. **Claude and GPT models (3P 协同池)**：
   - `3p-5h` 与 `3p-weekly`：包含 Claude Opus、Claude Sonnet、GPT-OSS 等协同模型。

**结论**：如果要精确监控日常通过 Antigravity / EasyCLIProxyAPI 调用 AI 模型的真实消耗，**必须严格请求 `daily-cloudcode-pa` 端点**，否则读取到的是未消耗的通用闲置桶，或者产生严重的数据偏差。

## 三、 正确请求构造与规范

经实机抓包与源码反编译，正确的 Google Antigravity 配额查询请求规范如下：

```http
POST https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary HTTP/1.1
Host: daily-cloudcode-pa.googleapis.com
Authorization: Bearer ya29.a0AdMD...（从凭据文件提取的有效 OAuth Access Token）
Content-Type: application/json
User-Agent: antigravity/hub/2.8.1 windows/amd64

{"project": "aicode-consumers"}
```

- **Project ID**：必须固定传入 `aicode-consumers`；
- **代理要求**：在国内网络环境下，请求必须正确路由至本地代理（如 `http://127.0.0.1:3067`）；
- **Token 来源**：EasyCLIProxyAPI 登录后的 JSON 凭据（如 `D:\EasyCLIProxyAPI\auth\antigravity-*.json`）中直接保存了明文的当前有效 `access_token`，无需解密即可直接使用。

## 四、 桌面端架构最佳实践

在向 Hermes Agent、VS Code 或自定义桌面插件提供配额监控时，不建议在前端浏览器/WebView 环境中直接向 Google 发起高频轮询（易遭遇跨域 CORS 拦截、缺少网络代理配置、或频繁打扰 Google 触发限流）。

业界最佳实践是**构建本地微服务中继（Micro-Service Relay）**：

```text
[桌面前端状态栏微件 (UI)]
        │ 定时轮询 (GET http://127.0.0.1:18088/quota)
        ▼
[本地 Python 轻量微服务 (端口 18088)] 
        │ 30 秒内存防抖缓存 (支持 ?force=1 穿透刷新)
        ▼
[读取本地凭据 D:\EasyCLIProxyAPI\auth\antigravity-*.json]
        │ 经本地代理 127.0.0.1:3067
        ▼
[Google 官方 daily-cloudcode-pa 接口]
```

### 1. 核心优势
- **极速响应**：前端轮询由本地内存缓存提供毫秒级（<1ms）响应，完全不阻塞主界面；
- **防抖保护**：30 秒内存缓存机制避免了桌面端多窗口高频请求触发 Google 服务端风控；
- **支持手动穿透**：当用户点击界面上的“刷新”图标时，前端携带 `?force=1` 请求，微服务立刻穿透缓存直连 Google，并返回更新时间戳，形成高确信度的用户反馈闭环；
- **完全解耦**：彻底摆脱对特定代理软件私有补丁接口的依赖，即使网关重启或版本迭代，配额监控依然 100% 独立稳定运行。
