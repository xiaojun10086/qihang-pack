# jxgl（仓库维护用，不随 release 交付）

综合教务系统（`jxgl.dlut.edu.cn`）取数用的**页面内脚本**。与 `scripts/browser-bridge/` 同类：属于仓库维护目录，**不在 `scripts/sync_release.py` 的交付白名单里，也不进 DSH 交付树**。

- 依赖：**Node.js >= 22**，且只用于驱动 `scripts/browser-bridge/qihang-bridge.mjs`；本目录脚本本身零依赖，在页面里执行。
- 这里**不放 CDP 客户端**：接入、端口发现、标签页选择全部由 `scripts/browser-bridge/qihang-bridge.mjs` 承担，本目录只放页面内逻辑，避免两套接入实现各自漂移。
- **不写死学期 ID、入口 ID、端口**：学期与入口每次都可能不同，由调用方传入或从页面推导；端口由 `DevToolsActivePort` 自动发现。

## 用法

先按 `scripts/browser-bridge/README.md` 让用户在自己的浏览器里登录（**不代登录**），再在**已登录的目标标签页**上执行：

```bash
# 全校开课查询：先写入入口参数（两个 ID 从落地 URL 与页面自身请求里取，不要沿用上一次的）
node scripts/browser-bridge/qihang-bridge.mjs eval "window.__QIHANG__={semester:'<学期ID>',entry:'<入口ID>'}" --tab lesson-search --port <端口>
# 取数（结果较大，重定向到文件）
node scripts/browser-bridge/qihang-bridge.mjs eval --file scripts/jxgl/fetch-lessons.js --tab lesson-search --port <端口> > all-courses.json

# 培养方案完成情况：先连点 4 轮展开全部，再抽取
node scripts/browser-bridge/qihang-bridge.mjs eval --file scripts/jxgl/expand-all.js --tab program-completion --port <端口>
node scripts/browser-bridge/qihang-bridge.mjs eval --file scripts/jxgl/extract-program-plan.js --tab program-completion --port <端口> > program-plan.json

# 开课查询页的表格口径（与接口口径互为校验）
node scripts/browser-bridge/qihang-bridge.mjs eval --file scripts/jxgl/extract-in-page.js --tab lesson-search --port <端口> > lesson-search-table.json
```

## 脚本

| 文件 | 作用 |
|---|---|
| `fetch-lessons.js` | 开课查询：页面内分块 `fetch` 全部分页（每次 5 页 × 300 条），按 `lessonId` 去重后返回 JSON |
| `expand-all.js` | 培养方案完成情况：连点 4 轮「展开全部」等按钮（只点一次会漏层级） |
| `extract-program-plan.js` | 培养方案完成情况：平铺遍历 `.module-tpl` 与 `table`，按 `depth` 重建层级树，并区分方案内表与计划外表 |
| `extract-in-page.js` | 开课查询页：按 `[data-original-title]` 抽取课程代码 / 开课部门 / 课程类型 / 总学时 / 授课语言 / 考核方式 / 是否必修 |

## 边界

- **只读**：不修改、删除或伪造任何校内系统记录，不代替用户登录。
- **只断开连接，不结束浏览器进程**：浏览器归用户所有，结束进程会让用户丢登录态。
- 字段口径、页面结构与踩坑见 `references/dlut-field-map.md` 第四～七节；本目录只放可执行实现。
- 交付技能包内**不引用本目录**：交付侧以 `references/dlut-field-map.md` 的口径为准，由 agent 在已登录页面内执行等价脚本。
