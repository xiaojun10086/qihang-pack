---
name: qihang-f2
description: F2 作息与专注（生活类）域入口卡：拖延、作息、专注、番茄钟、时间管理、熬夜。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# F2 · 作息与专注（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：拖延、作息、专注、番茄钟、时间管理、熬夜

**边界**：作息调整、专注块排布、拖延干预、时间管理
**不覆盖**：不做学业规划内容（只在其中嵌入时间安排）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/F2-focus/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `focus-block` / `task-decompose`
   路径：`domains/F2-focus/skills/local/focus-block/SKILL.md`、`domains/F2-focus/skills/local/task-decompose/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/F2-focus/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/F2-focus/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
