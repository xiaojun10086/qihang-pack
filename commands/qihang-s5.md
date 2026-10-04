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

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/S5-academic-writing/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 5 个库内 skill 中择优 —— 首选 `paper-outline`；其余 `abstract-tune` / `argument-slides` / `cite-normalize` / `thesis-format` 按触发场景择用
   路径：`domains/S5-academic-writing/skills/local/abstract-tune/SKILL.md`、`domains/S5-academic-writing/skills/local/argument-slides/SKILL.md`、`domains/S5-academic-writing/skills/local/cite-normalize/SKILL.md`、`domains/S5-academic-writing/skills/local/paper-outline/SKILL.md`、`domains/S5-academic-writing/skills/local/thesis-format/SKILL.md`
4. **输出与保存**：按 `library/output-spec.md` 输出 ≤6 条要点；默认不读写学习档案，仅用户明确要求保存时按 `library/memory.md` 处理。
5. **DUT 绑定点**：见 `domains/S5-academic-writing/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（用户自查页面；工具不采集页面内容）。
6. **外部桥接（按需）**：库内 skill 与同域降级都接不住，且外部能力确有帮助时，读 `library/external-bridge.md` → 只查本域指定平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。
