---
name: qihang-s5
description: S5 学术表达（学习类）域入口卡：论文、综述、答辩、PPT、引用、文献综述。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# S5 · 学术表达（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：论文、综述、答辩、PPT、引用、文献综述

**边界**：课程论文 / 综述 / 答辩展示的结构、引用规范、预审
**不覆盖**：不做文献检索管理（→R1）；不投稿（→R4）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/S5-academic-writing/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `cite-normalize` / `paper-outline`
   路径：`domains/S5-academic-writing/skills/local/cite-normalize/SKILL.md`、`domains/S5-academic-writing/skills/local/paper-outline/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/S5-academic-writing/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/S5-academic-writing/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
