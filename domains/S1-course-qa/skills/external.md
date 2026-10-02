# S1 · 课程答疑 — 库外 skill 候选（多源比对 v3）

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
| 1 | `socrates-skill` | `bevibing/socrates-skill` | 326 | MIT | 2026-04-02 | 5 | 3 | 2 | 5 | 4 | **4.25** | ✅ **最优解** |
| 2 | `teach` | `mattpocock/skills` | 273959 | MIT | 2026-09-29 | 5 | 5 | 5 | 3 | 2 | **4.10** | ⚠️ **不适配 DUT**（场景搭但环境错位） |
| 3 | `tutor-skills` | `bevibing/tutor-skills` | 1313 | MIT | 2026-02-28 | 5 | 3 | 3 | 4 | 3 | **3.95** | 备选 |
| 4 | `chem-skill` | `ghutchis/chem-skill` | 4 | MIT | 2025-12-28 | 5 | 3 | 0 | 3 | 3 | **3.05** | 备选 |
| 5 | `math-skill` | `googlarz/math-skill` | 9 | 未声明 | 2026-03-22 | 0 | 3 | 0 | 4 | 3 | **2.25** | ⛔ 许可证缺失，不入围 |
| 6 | `gurukul-ai` | `somenssarkar/gurukul-ai` | 0 | 未声明 | 2026-02-21 | 0 | 1 | 0 | 1 | 1 | **0.60** | ⛔ 许可证缺失，不入围 |

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
| `socrates-skill` | 5 | 苏格拉底式追问，与「不直接抛答案」完全同构 | — |
| `teach` | 3 | 通用教学法，工程向非学科向 | — |
| `tutor-skills` | 4 | 把 PDF/讲义转成讲解材料，可补 S1 材料侧 | 偏笔记向，题目讲解仍靠库内 |
| `chem-skill` | 3 | 化学专项，可补理科答疑 | ⚠️ 2025-12 后未更新 |
| `math-skill` | 4 | 学科数学专项，题型贴合高数/线代 | ⛔ 无 LICENSE |
| `gurukul-ai` | 1 | 面向 Grade 7，与大学课程错位 | ⛔ 无 LICENSE，且需 API Key |

### 1.2 DUT 落地评估

| 候选 | DUT 适配 | 环境错位点 |
|---|---|---|
| `teach` | 2 | 工程向教学法（TDD/PR 流程），与大学课程答疑场景错位 |
| `gurukul-ai` | 1 | 面向 Grade 7 中学教育，与大学完全错位 |

> 这些候选**不得作为最优解**：能跑通，但在大工的真实环境里用不上或不合规。


## 三、最优解

**库外首选：`socrates-skill`（`bevibing/socrates-skill`）** —— 综合分 4.25 ｜ DUT 适配 4/5，引导式教学与「不直接抛答案」同构；指令为英文，需接受。

> 但**首选仍是库内**：`explain-stepwise` / `error-diagnose` 零安装、零外发、红线已内置。只有库内不覆盖该细分场景时才动库外。

### 3.1 明确排除

- ⛔ `math-skill`（`googlarz/math-skill`）：**许可证缺失/未声明** → 禁止摘录、禁止再分发，仅可本地自用。⛔ 无 LICENSE
- ⛔ `gurukul-ai`（`somenssarkar/gurukul-ai`）：**许可证缺失/未声明** → 禁止摘录、禁止再分发，仅可本地自用。⛔ 无 LICENSE，且需 API Key

## 四、降级链

库内 `explain-stepwise` → 库内 `error-diagnose` → 库外 `socrates-skill`（`bevibing/socrates-skill`） → 纯提示词模式（标注 `[已降级]`）

> 触发条件见 `library/output-spec.md` §2.1；降级时输出**首行**必须带 `[已降级: 原 → 备]`。

## 五、合规与风险提醒

- **`tutor-skills`**（`bevibing/tutor-skills`）：偏笔记向，题目讲解仍靠库内
- **`chem-skill`**（`ghutchis/chem-skill`）：⚠️ 2025-12 后未更新

> 自检与许可证数据见 `references/skill-compliance-audit.md` 与 `THIRD_PARTY_NOTICES.md`。
