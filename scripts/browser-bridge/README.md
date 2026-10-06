# qihang-bridge（仓库维护用，不随 release 交付）

零依赖 CDP（Chrome DevTools Protocol）接入工具，用于「用户在自己的浏览器里登录 → 本包接上去读页面」这条流程。**属于仓库维护目录，不在 `scripts/sync_release.py` 的交付白名单里，也不进 DSH 交付树**；交付技能包自身不需要它。

- 依赖：**Node.js >= 22**（用自带的全局 `fetch` 与 `WebSocket`），无第三方包。
- 契约：不写死浏览器路径、不假设端口。浏览器可执行文件从注册表 `App Paths`、系统候选路径、运行中实例反查；端口从 `<专用配置目录>/DevToolsActivePort` 取得。

## 用法

```bash
node scripts/browser-bridge/qihang-bridge.mjs doctor              # 体检：找到哪些浏览器、有没有可接入的实例
node scripts/browser-bridge/qihang-bridge.mjs open <url>          # 用本工具自有的专用实例打开（会先提示是否覆盖原页面）
node scripts/browser-bridge/qihang-bridge.mjs text --port <端口>  # 读当前页面正文
node scripts/browser-bridge/qihang-bridge.mjs eval "<js>" --port <端口>
node scripts/browser-bridge/qihang-bridge.mjs tabs --port <端口>  # 列标签页
node scripts/browser-bridge/qihang-bridge.mjs tab-new <url>       # 新开标签页（不导航走用户当前页面）
node scripts/browser-bridge/qihang-bridge.mjs shot --port <端口>  # 截图，默认存 ~/.qihang/shots/
```

常用选项：`--browser edge|chrome`、`--port <n>`、`--tab <子串>`。选项写在子命令之后。

失败即报错，不静默回退：未知子命令、`--browser` 拼错、`--tab` 无匹配、端口无实例都会以非 0 退出码结束并说明原因。

## 状态与登录态位置

| 路径 | 用途 |
|---|---|
| `~/.qihang/bridge.json` | 本工具自有实例的登记（profile 与端口） |
| `~/.qihang/browser/<edge\|chrome>` | 专用配置目录，登录态存在这里，与日常浏览器隔离 |
| `~/.qihang/shots/` | 截图输出目录 |

用 `--port` 接入用户自己的实例时，状态文件只登记该端口（不写自有 profile），避免自有实例与用户实例混成一条记录。

## 启动方式

用户侧复制即用（`--remote-debugging-port=0` 让浏览器自选空闲端口，实际端口写入 `DevToolsActivePort`）：

```text
msedge.exe --remote-debugging-port=0 --user-data-dir="%USERPROFILE%\.qihang\browser\edge" <目标入口>
chrome.exe --remote-debugging-port=0 --user-data-dir="%USERPROFILE%\.qihang\browser\chrome" <目标入口>
```

- **必须用独立配置目录**：Chrome / Edge 136 起会忽略默认配置目录上的调试端口。
- 登录态须**正常关窗**（或由本工具优雅关闭）才会落盘 cookie；强制结束进程会丢登录态。
- 陈旧状态会掩盖判断：改过代码或换过实例后，先删 `~/.qihang/bridge.json` 再验证。

## 安全边界

- 本工具只做接入与读取，**不代填用户名 / 密码 / 验证码**，认证环节留给用户本人。
- 零状态 `open` 只接管**本工具自有**的专用实例；要接入用户自己的调试实例必须显式给 `--port`。
- 不修改、删除或伪造任何校内系统记录。
