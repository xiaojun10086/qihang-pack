---
name: qihang-s4
description: S4 备考与记忆（学习类）域入口卡：考试、复习、背诵、突击、卡组、刷题。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# S4 · 备考与记忆（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：考试、复习、背诵、突击、卡组、刷题

**边界**：考前冲刺规划、间隔重复、卡组生成、模拟卷
**不覆盖**：不做单题讲解（→S1）；不写课程论文（→S5）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/S4-exam-prep/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `exam-sprint` / `recall-schedule`
   路径：`domains/S4-exam-prep/skills/local/exam-sprint/SKILL.md`、`domains/S4-exam-prep/skills/local/recall-schedule/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/S4-exam-prep/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/S4-exam-prep/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
