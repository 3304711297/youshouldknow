---
applies_to:
  - Tauri v2 桌面应用开发与构建
  - 使用 WebView2 的 Windows 桌面客户端
  - 依赖 Vite / 前端打包器的混合架构桌面应用
risk: low
tweak_module: []
---

# Tauri v2 生产构建中 custom-protocol 缺失致 WebView2 回环拒绝连接排坑

> 深入剖析 Tauri v2 内核模式判定机制：为什么裸跑 `cargo build --release` 产出的二进制依然是开发版？为什么双击应用会弹出 Edge `ERR_CONNECTION_REFUSED` 报错？本文给出源码级机理与标准构建流水线。

---

## 现象与问题复现

在开发或维护基于 **Tauri v2** + **Vite** 的桌面应用程序（如各种本地反代控制台、系统工具）时，开发者常遇到以下典型故障：

1. 本地运行 `cargo build --release` 编译成功，在 `target/release/` 下顺利生成 `.exe` 可执行文件；
2. 双击运行该可执行文件，桌面弹出的应用窗口未加载任何前端页面，而是呈现 Windows WebView2（Microsoft Edge 内核）的标准网络错误页：
   * **标题**：`嗯... 无法访问此页面`
   * **正文**：`localhost 拒绝连接。`
   * **错误码**：`ERR_CONNECTION_REFUSED`
   * 底部带有深色 Microsoft Edge 标识与「刷新」按钮。

此时若在终端手动启动前端开发服务（如 `npm run dev`，监听 `http://localhost:5173`），再次点击「刷新」，窗口瞬间正常展示。

**核心矛盾**：明明指定了 `--release` 优化编译，为什么生成的生产二进制文件依然固执地去访问本地开发端口 `localhost:5173`，而不是加载内嵌的静态资源？

---

## 根因深剖：Tauri v2 的模式判定机制

很多人误以为 Rust 的 `--release` 编译开关会自动让 Tauri 将前端 `frontendDist` 打包内嵌。**这是错误的理解**。

### 1. `dev` 模式的源码判定逻辑

在 Tauri 核心代码库的宏与代码生成模块（`tauri-macros` 与 `tauri-codegen`）中，判定当前编译到底是“开发模式（Dev）”还是“生产模式（Production）”，其依据并非 `cfg!(debug_assertions)`，而是 **`custom-protocol` 特性（Feature）是否激活**：

```rust
// 摘自 tauri-macros / context.rs
ContextItems {
    dev: cfg!(not(feature = "custom-protocol")),
    // ...
}
```

* 当当前 Crate 激活了 `custom-protocol` 特性时：`cfg!(not(...))` 为 `false`，即 `dev = false`（生产模式）；
* 当当前 Crate **未激活** `custom-protocol` 时：`cfg!(not(...))` 为 `true`，即 `dev = true`（**强制判定为开发模式**）！

### 2. 代码生成阶段的分支分发

在 `tauri-codegen` 读取 `tauri.conf.json` 生成运行时上下文（`generate_context!()`）时，资源加载逻辑如下：

```rust
// 摘自 tauri-codegen / context.rs
let assets = if let Some(assets) = assets {
    quote!(#assets)
} else if dev && config.build.dev_url.is_some() {
    // 命中开发模式：丢弃静态资源打包，仅保留空资源映射
    let assets = EmbeddedAssets::default();
    quote!(#assets)
} else {
    // 生产模式：扫描 frontendDist 目录并将其全部静态文件嵌入二进制
    match &config.build.frontend_dist {
        Some(FrontendDist::Directory(path)) => {
            EmbeddedAssets::new(assets_path, &options, ...)
        }
        // ...
    }
};
```

* **如果 `dev == true`**：Tauri 将窗口的起始加载地址（`WebviewUrl`）直接烧录为配置文件中的 `build.devUrl`（例如 `http://localhost:5173`），并且**不把前端产物嵌入可执行文件**；
* **如果 `dev == false`**：Tauri 才会递归读取 `build.frontendDist`（例如 `../dist`）中的全部 HTML/JS/CSS，通过虚拟自定义协议（如 `tauri://localhost` 或 `http://tauri.localhost`）从内存中解压并服务。

### 3. 为什么“裸跑” cargo 会中招？

* **Tauri CLI 的隐式行为**：当你执行 `npm run tauri build` 或 `cargo tauri build` 时，Tauri CLI 会在后台为 `cargo` 自动追加 `--features custom-protocol`；
* **裸 cargo 的缺失**：如果你直接在 `src-tauri` 目录执行 `cargo build --release`，或者在 CI / 外部脚本中调用原始 cargo，cargo **完全不知道**需要开启此 feature；
* **致命陷阱**：若 `src-tauri/Cargo.toml` 本身**未在 `[features]` 段中显式声明 `custom-protocol`**，那么即便开发者尝试手动传入 `cargo build --release --features custom-protocol`，cargo 也会直接报错：
  ```
  error: the package 'xxx' does not contain this feature: custom-protocol
  ```

---

## 彻底解决方案

要彻底消除此问题并确保发布流水线绝对健壮，需要完成以下两步加固：

### 第一步：在 `src-tauri/Cargo.toml` 补齐特性声明

在 `src-tauri/Cargo.toml` 中显式添加标准特性映射：

```toml
[dependencies]
tauri = { version = "2", features = ["tray-icon"] }
# ... 其余依赖保持不变

[features]
# 生产构建与静态资源内嵌必备特性（严禁删除）
custom-protocol = ["tauri/custom-protocol"]
```

> **注意**：不要将 `custom-protocol` 加入 `default = ["custom-protocol"]`。如果将其设为默认特性，会导致日常开发运行 `cargo tauri dev` 时无法享受 Vite 的热重载（HMR），而会强行去读 dist 生产包。

### 第二步：规范化构建流水线

在发布或打包独立 Release 产物时，必须严格执行**两阶段构建**：

```bash
# 阶段一：编译前端静态资源（生成 dist/ 目录）
npm run build

# 阶段二：使用 Tauri CLI 完成内嵌式生产编译（推荐）
npm run tauri build -- --no-bundle

# 或者若脱离 Tauri CLI 使用原生 Cargo：
cargo build --release --features custom-protocol
```

* 使用 `--no-bundle` 参数可以跳过耗时的安装包打包（如 NSIS / MSI 安装向导生成），直接在 `src-tauri/target/release/` 下输出即开即用的单文件绿色免安装可执行文件。

---

## 检验与实证方法

构建完成后，在将产物交付给用户或打包分发之前，可采用以下两种无环境依赖的检验手段确认资源已正确内嵌：

### 1. 二进制特征串检索（静态检测）

使用简短脚本或搜索工具检查编译后的 `.exe` 二进制文件内容：

```python
with open("target/release/yourapp.exe", "rb") as f:
    data = f.read()

# 检查是否依然残留 devUrl 端口绑定
has_dev_port = b":5173" in data
# 检查是否包含自定义协议端点
has_custom_proto = b"tauri.localhost" in data

print("开发端口残留:", has_dev_port)
print("自定义协议嵌入:", has_custom_proto)
```

* 若依然显示包含开发端口且未嵌入协议，说明二进制仍处于开发模式。

### 2. 脱机冷启动实测（动态检测）

1. 完全关闭本地所有 Node / Vite / Webpack 开发服务进程（确认 `netstat -ano` 中无 5173 监听）；
2. 双击打开生成的 `.exe` 文件；
3. **预期成功结果**：界面瞬间秒开并完整渲染深色/浅色 UI、图标与交互卡片；
4. **失败结果**：界面白屏或弹出 Edge `ERR_CONNECTION_REFUSED` 报错页面。

---

## 事实核查记录

| 核查项 | 源码/文档证据 | 验证结论 |
| :--- | :--- | :--- |
| Tauri v2 模式判定依据 | `tauri-macros/src/context.rs` L35：`dev: cfg!(not(feature = "custom-protocol"))` | 属实。确实不依赖 release 编译配置，只依赖 feature |
| 资源嵌入分支判定 | `tauri-codegen/src/context.rs` L178：`else if dev && config.build.dev_url.is_some()` | 属实。dev 模式下 EmbeddedAssets 为空，仅指向 devUrl |
| WebView2 拒绝连接错误码 | Windows WebView2 捕获窗口实测（`ERR_CONNECTION_REFUSED`） | 属实。端口未监听时 Chromium 内核默认抛出此错误 |
| Cargo.toml 特性声明规范 | Tauri 官方模板与 CLI 合约：`custom-protocol = ["tauri/custom-protocol"]` | 属实。CLI 隐式传递该特性，Crate 必须具备对应 feature |
