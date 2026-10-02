# F2 · 作息与专注 — 库外 skill 候选（多源比对 v3）

> **使用规则**：先确认库内 skill 不能满足需求，再读本表。**库内优先是硬规则**（见 `SKILL.md` 硬规则 1）。
> **数据来源**：GitHub API 实抓 **2026-10-02**（stars / license / pushed_at / archived / size）；
> 平台侧复核见 `references/skill-sources.md`，全量矩阵见 `references/skill-matrix-v3.md`。
> **摘录红线**：**GPL-3.0 / AGPL / CC-BY-NC / 无 LICENSE** 一律**只做外部调用，不得复制内容进本包**。

## 一、候选比对（按综合分降序）

> **两个「适配」不一样**：
> **场景适配** = 这个 skill 干不干这件事；**DUT 适配** = 在 DUT 本科新生的真实环境
> （中文语境 / 超星·雨课堂·自建教务 / 国内升学与校招 / 无 Google 账号 / Windows 为主）里用不用得上。
> **只有 DUT 适配 ≥ 3 的候选才有资格当最优解。**

| # | 候选 | 仓库 | ★ | 许可证 | 最近推送 | 合规 | 可用 | 社区 | 场景适配 | DUT 适配 | 综合分 | 结论 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `deep-work` | `alirezarezvani/claude-skills` | 27194 | MIT | 2026-08-30 | 5 | 5 | 4 | 4 | 4 | **4.40** | ✅ **最优解** |
| 2 | `habit-tracker` | `eddiebelaval/squire` | 21 | MIT | 2026-08-16 | 5 | 3 | 1 | 3 | 2 | **3.20** | ⚠️ **不适配 DUT**（场景搭但环境错位） |
| 3 | `pomodoro` | `jakedahn/pomodoro` | 56 | MIT | 2025-10-23 | 5 | 2 | 1 | 3 | 2 | **3.05** | ⚠️ **不适配 DUT**（场景搭但环境错位） |

## 二、评分口径（可复算）

```
合规 = 5（MIT/Apache/BSD/CC0/ISC）  2（GPL/AGPL/LGPL 或 CC-BY-NC）  0（无 LICENSE / API 未识别）
可用 = 5 基准；已归档 → 0；最近推送 > 180 天 −2；需 API Key/联网 −2；仓库 > 100MB −1（下限 0）
社区 = 5（★≥100k）4（★≥10k）3（★≥1k）2（★≥100）1（★≥10）0（★<10）
适配 = 0–5，**人工判定**：是否直接覆盖本域核心动作（逐条理由见 §1.1）
DUT适配 = 0–5，**人工判定**：在 DUT 本科新生真实环境是否可用（中文/超星·雨课堂/国内升学与校招/无 Google 账号/Windows）
         （逐条理由见 §1.2；未特别标注者默认与「场景适配」同值）

综合分 = 0.25×合规 + 0.15×可用 + 0.15×社区 + **0.45×适配**   （满分 5.00）
并列时先比「适配」、再比星数（**适配优先** —— 本包不采信「唯星数论」，见 `skill-sources.md` 关键结论）
基准日 = 2026-10-02 ｜ 陈旧阈值 = 180 天
```

**门禁**：`合规 = 0` 的候选**不得**作为最优解（许可证缺失 → 禁止摘录、禁止再分发）；`合规 = 2` 只能外部调用。

### 1.1 场景适配逐条理由

| 候选 | 场景适配 | 理由 | 备注 |
|---|---|---|---|
| `deep-work` | 4 | 深度工作法，与专注块同构 | ⚠️ 仓库含大量无关 skill，只取单个 |
| `habit-tracker` | 3 | 习惯打卡 | ⚠️ 密钥可能明文落盘，用前读源码 |
| `pomodoro` | 3 | 番茄钟 | ⚠️ 停滞 11 个月；二进制仅 macOS ARM |

### 1.2 DUT 落地评估

| 候选 | DUT 适配 | 环境错位点 |
|---|---|---|
| `habit-tracker` | 2 | 密钥可能明文落盘；打卡类也可用手机自带工具 |
| `pomodoro` | 2 | 二进制仅 macOS ARM；Windows 用户用不了 |

> 这些候选**不得作为最优解**：能跑通，但在大工的真实环境里用不上或不合规。


## 三、最优解

**库外首选：`deep-work`（`alirezarezvani/claude-skills`）** —— 综合分 4.40 ｜ DUT 适配 4/5，专注法通用，无地域依赖。

> 但**首选仍是库内**：`focus-block` / `task-decompose` 零安装、零外发、红线已内置。只有库内不覆盖该细分场景时才动库外。

## 四、降级链

库内 `focus-block` → 库内 `task-decompose` → 库外 `deep-work`（`alirezarezvani/claude-skills`） → 纯提示词模式（标注 `[已降级]`）

> 触发条件见 `library/output-spec.md` §2.1；降级时输出**首行**必须带 `[已降级: 原 → 备]`。

## 五、合规与风险提醒

- **`deep-work`**（`alirezarezvani/claude-skills`）：⚠️ 仓库含大量无关 skill，只取单个

> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`。
