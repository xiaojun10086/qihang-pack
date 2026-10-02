---
name: qihang-s2
description: S2 课堂与笔记（学习类）域入口卡：笔记、讲义、录音、整理、概念图、思维导图。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# S2 · 课堂与笔记（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：笔记、讲义、录音、整理、概念图、思维导图

**边界**：课堂材料 → 结构化笔记 / 概念图 / 知识库沉淀
**不覆盖**：不做题目讲解（→S1）；不写实验报告（→S3）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/S2-lecture-notes/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `lecture-to-notes` / `note-normalize`
   路径：`domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md`、`domains/S2-lecture-notes/skills/local/note-normalize/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/S2-lecture-notes/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/S2-lecture-notes/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
