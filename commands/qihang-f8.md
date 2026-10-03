---
name: qihang-f8
description: F8 求职与竞赛（生活类）域入口卡：简历、面试、实习、竞赛、证书、秋招。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# F8 · 求职与竞赛（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：简历、面试、实习、竞赛、证书、秋招

**边界**：简历、面试、实习求职、学科竞赛与创新创业项目
**不覆盖**：不做升学规划（→F7）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/F8-career/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 5 个库内 skill 中择优 —— 首选 `career-kit`；其余 `competition-pick` / `intern-search` / `interview-drill` / `resume-tailor` 按触发场景择用
   路径：`domains/F8-career/skills/local/career-kit/SKILL.md`、`domains/F8-career/skills/local/competition-pick/SKILL.md`、`domains/F8-career/skills/local/intern-search/SKILL.md`、`domains/F8-career/skills/local/interview-drill/SKILL.md`、`domains/F8-career/skills/local/resume-tailor/SKILL.md`
4. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
5. **DUT 绑定点**：见 `domains/F8-career/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
6. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。
