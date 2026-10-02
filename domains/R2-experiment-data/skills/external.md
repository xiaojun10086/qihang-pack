# R2 · 实验与数据 — 库外 skill 候选（多源比对 v3）

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
| 1 | `scientific-agent-skills` | `K-Dense-AI/scientific-agent-skills` | 47304 | MIT | 2026-10-01 | 5 | 4 | 4 | 4 | 3 | **4.25** | ✅ **最优解** |
| 2 | `scientific-agents` | `K-Dense-AI/scientific-agents` | 192 | MIT | 2026-09-29 | 5 | 5 | 2 | 4 | 3 | **4.10** | 备选 |
| 3 | `jupyter-notebook` | `openai/skills` | 27841 | 未声明 | 2026-09-08 | 0 | 5 | 4 | 3 | 3 | **2.70** | ⛔ 许可证缺失，不入围 |

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
| `scientific-agent-skills` | 4 | 学科科研 skill 大合集，覆盖广 | ⚠️ 仓库 472MB，安装慢 |
| `scientific-agents` | 4 | 科研推理 AGENTS 画像，方法侧补充 | — |
| `jupyter-notebook` | 3 | Notebook 工作流 | ⚠️ 仓库根目录未声明总许可证，原表仓库名有误已修正 |

### 1.2 DUT 落地评估

**本域无「场景搭但环境错位」的候选。**


## 三、最优解

**库外首选：`scientific-agent-skills`（`K-Dense-AI/scientific-agent-skills`）** —— 综合分 4.25 ｜ DUT 适配 3/5，偏生物信息/计算化学；本科基础实验课用不上。

> 但**首选仍是库内**：`data-lab` / `stats-guard` 零安装、零外发、红线已内置。只有库内不覆盖该细分场景时才动库外。

### 3.1 明确排除

- ⛔ `jupyter-notebook`（`openai/skills`）：**许可证缺失/未声明** → 禁止摘录、禁止再分发，仅可本地自用。⚠️ 仓库根目录未声明总许可证，原表仓库名有误已修正

## 四、降级链

库内 `data-lab` → 库内 `stats-guard` → 库外 `scientific-agent-skills`（`K-Dense-AI/scientific-agent-skills`） → 纯提示词模式（标注 `[已降级]`）

> 触发条件见 `library/output-spec.md` §2.1；降级时输出**首行**必须带 `[已降级: 原 → 备]`。

## 五、合规与风险提醒

- **`scientific-agent-skills`**（`K-Dense-AI/scientific-agent-skills`）：⚠️ 仓库 472MB，安装慢

> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`。
