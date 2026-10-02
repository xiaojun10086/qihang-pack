---
name: qihang-r2
description: R2 实验与数据（科研类）域入口卡：实验、数据、统计、显著性、图表、误差。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# R2 · 实验与数据（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：实验、数据、统计、显著性、图表、误差

**边界**：实验设计、数据处理、统计检验、图表规范
**不覆盖**：不写报告结构（→S3）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/R2-experiment-data/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `data-lab` / `stats-guard`
   路径：`domains/R2-experiment-data/skills/local/data-lab/SKILL.md`、`domains/R2-experiment-data/skills/local/stats-guard/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/R2-experiment-data/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/R2-experiment-data/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
