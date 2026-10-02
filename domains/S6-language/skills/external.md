# S6 · 语言能力 — 库外 skill 候选（多源比对 v3）

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
| 1 | `ielts` | `YANZHANLIN/ielts-claude-skills` | 307 | MIT | 2026-07-20 | 5 | 5 | 2 | 5 | 4 | **4.55** | ✅ **最优解** |
| 2 | `english-coach` | `tianmind-studio/english-coach` | 17 | MIT | 2026-09-24 | 5 | 5 | 1 | 4 | 4 | **3.95** | 备选 |
| 3 | `education-skills` | `flysheep-ai/education-skills` | 106 | MIT | 2026-01-30 | 5 | 3 | 2 | 3 | 3 | **3.35** | 备选 |

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
| `ielts` | 5 | 雅思四科，直接对应四六级/留学语言需求 | 完整版 v3 为付费 |
| `english-coach` | 4 | 英语口语陪练，中文场景友好 | — |
| `education-skills` | 3 | 中文教育 skill 集合，语言类可挑 | — |

### 1.2 DUT 落地评估

**本域无「场景搭但环境错位」的候选。**


## 三、最优解

**库外首选：`ielts`（`YANZHANLIN/ielts-claude-skills`）** —— 综合分 4.55 ｜ DUT 适配 4/5，雅思为主；四六级需自行裁剪，但语言训练骨架可直接用。

> 但**首选仍是库内**：`lang-drill` / `pronounce-drill` 零安装、零外发、红线已内置。只有库内不覆盖该细分场景时才动库外。

## 四、降级链

库内 `lang-drill` → 库内 `pronounce-drill` → 库外 `ielts`（`YANZHANLIN/ielts-claude-skills`） → 纯提示词模式（标注 `[已降级]`）

> 触发条件见 `library/output-spec.md` §2.1；降级时输出**首行**必须带 `[已降级: 原 → 备]`。

## 五、合规与风险提醒

- **`ielts`**（`YANZHANLIN/ielts-claude-skills`）：完整版 v3 为付费

> 自检与许可证数据见 `references/skill-compliance-audit.md` 与 `THIRD_PARTY_NOTICES.md`。
