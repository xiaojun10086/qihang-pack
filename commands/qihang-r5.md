---
name: qihang-r5
description: R5 学术规范与伦理（科研类）域入口卡：查重、引用规范、学术诚信、AI 声明、数据合规、署名。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# R5 · 学术规范与伦理（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：查重、引用规范、学术诚信、AI 声明、数据合规、署名

**边界**：引用规范、查重、学术诚信、AI 使用声明、数据与伦理合规
**不覆盖**：不做内容写作（→S5/R4）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/R5-integrity/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `ai-disclosure` / `integrity-check`
   路径：`domains/R5-integrity/skills/local/ai-disclosure/SKILL.md`、`domains/R5-integrity/skills/local/integrity-check/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/R5-integrity/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/R5-integrity/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
