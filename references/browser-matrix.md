# 可驱动浏览器矩阵

> 本包私密站接入（方案 A）依赖 `agent-browser` CLI。
> 本文件列出**实际可驱动的浏览器/引擎/云端 provider**，以及各自的适用场景与取舍。

---

## 一、本机实测可用（推荐）

| # | 方式 | 命令 | 状态 |
|---|---|---|---|
| 1 | **内置 Chrome 154**（chrome-for-testing） | 默认，无需指定 | ✅ **已实测可用**（本包方案 A 默认） |
| 2 | 内置 Chrome 152 | 自动回退 | ✅ 已安装 |
| 3 | **本机 Chrome**（复用安装版） | `--executable-path "C:\Program Files\Google\Chrome\Application\chrome.exe"` | ✅ 路径存在 |
| 4 | **本机 Edge** | `--executable-path "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"` | ✅ 路径存在 |

> 实测环境：Windows 11 x64 · Node 22.22.2 · `agent-browser 0.27.0`

---

## 二、通过 `--executable-path` 可驱动的浏览器

只要给到可执行文件路径即可（Chromium 内核均可）：

| 浏览器 | 典型路径（Windows） |
|---|---|
| Google Chrome | `C:\Program Files\Google\Chrome\Application\chrome.exe` |
| Microsoft Edge | `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe` |
| Brave | `...\BraveSoftware\Brave-Browser\Application\brave.exe` |
| Vivaldi / Opera / 360 极速（Chromium 内核） | 各自安装目录 |
| Chromium 便携版 | 直接指向 `chrome.exe` |

**取舍**：用本机浏览器 = 省一次 200MB 下载；但**必须配 `--profile` 独立目录**，否则会复用该浏览器的既有登录态。

---

## 三、浏览器引擎

| 引擎 | 说明 | 适用 |
|---|---|---|
| **`chrome`（默认）** | 完整 Chromium | **推荐**：能跑 JS、能登录、能截图 |
| `lightpanda` | 轻量引擎，速度快、体积小 | 仅适合**静态抓取**；**不支持登录态交互**，故本包方案 A **不用** |

```bash
--engine chrome        # 默认
--engine lightpanda    # 仅静态
```

---

## 四、连接到**已在运行**的浏览器（复用登录态）

| 方式 | 命令 | 说明 |
|---|---|---|
| CDP 端口连接 | `--cdp 9222` | 需先用 `--remote-debugging-port=9222` 启动浏览器 |
| 自动连接 | `--auto-connect` | 连接正在运行的 Chrome，**复用其登录态** |

> ⚠️ **本包默认禁用这两种方式** —— 它们会继承用户真实浏览器的**全部登录态**（不止 DUT），
> 远超本包所需的最小权限。**仅在用户明确知情并同意时使用。**

---

## 五、云端 / 移动端 provider

| provider | 说明 | 本包是否使用 |
|---|---|---|
| `ios` | 真实 iOS 设备/模拟器上的 Safari | ❌ 不需要 |
| `browserbase` · `kernel` · `browseruse` · `browserless` · `agentcore` | 云端浏览器（需各自账号/Key） | ❌ 涉及把校园站点访问外发到第三方云，**隐私不适用** |

```bash
--provider ios
--provider browserbase   # 需 Key
```

**结论**：本包的私密站场景**一律用本机 Chrome + 独立 Profile**，不使用云端 provider（避免把校内访问外发）。

---

## 六、本包的推荐配置

```bash
agent-browser --session "$SESSION_ID" open <url> --headed \
  --profile "$HOME/.qihang/browser-profile.XXXXXX"
```

| 参数 | 为什么 |
|---|---|
| `--headed` | 用户需在窗口内**亲眼看到**并**自行登录** |
| `--session <随机名>` | 本次只操作自己的 agent-browser 会话，不影响用户其他会话 |
| `--profile <一次性目录>` | **强制隔离**，不复用真实浏览器登录态；退出后删除 |
| 不加 `--auto-connect` / `--cdp` | 避免继承全量登录态 |
| 不加 `--provider` | 避免把校内访问外发到云端 |
| 不调用 `snapshot` / `read` | 工具不采集、复制或输出网页内容；用户自行查看并决定是否分享最少必要字段 |

**收尾必做**：只关闭本次随机会话并删除其一次性 Profile。打开失败、隔离校验失败或清理失败都必须显式报错；禁止用 `close --all` 影响其他会话。

---

## 七、异常退出后的清理

```bash
# 查看一次性 Profile 是否有异常残留；只删除确认属于本包的目录
find "$HOME/.qihang" -maxdepth 1 -type d -name 'browser-profile.*' -print
```

仅在确认没有对应浏览器进程仍在使用目录后，手动删除异常残留。正常执行会自动清理。
