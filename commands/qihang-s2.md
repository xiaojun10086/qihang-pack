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

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/S2-lecture-notes/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 4 个库内 skill 中择优 —— 首选 `lecture-to-notes`；其余 `link-notes` / `note-normalize` / `reading-note` 按触发场景择用
   路径：`domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md`、`domains/S2-lecture-notes/skills/local/link-notes/SKILL.md`、`domains/S2-lecture-notes/skills/local/note-normalize/SKILL.md`、`domains/S2-lecture-notes/skills/local/reading-note/SKILL.md`
4. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
5. **DUT 绑定点**：见 `domains/S2-lecture-notes/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（用户自查页面；工具不采集页面内容）。
6. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。
