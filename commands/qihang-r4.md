---
name: qihang-r4
description: R4 学术产出与投稿（科研类）域入口卡：投稿、期刊、专利、会议、基金、大创结题。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# R4 · 学术产出与投稿（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：投稿、期刊、专利、会议、基金、大创结题

**边界**：论文投稿、专利与会议、基金申报、返修回复
**不覆盖**：不做出稿前的结构打磨（→S5）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/R4-publication/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `rebuttal-structure` / `submit-kit`
   路径：`domains/R4-publication/skills/local/rebuttal-structure/SKILL.md`、`domains/R4-publication/skills/local/submit-kit/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/R4-publication/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/R4-publication/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
