---
name: qihang-f7
description: F7 升学深造（生活类）域入口卡：保研、考研、留学、申博、导师、推免。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# F7 · 升学深造（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：保研、考研、留学、申博、导师、推免

**边界**：保研/考研/留学的路径规划、时间线、材料与选校选导师
**不覆盖**：不写文书代笔（只给结构与自查）；不求职（→F8）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/F7-further-study/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 4 个库内 skill 中择优 —— 首选 `grad-plan`；其余 `grad-calendar` / `material-kit` / `school-pick` 按触发场景择用
   路径：`domains/F7-further-study/skills/local/grad-calendar/SKILL.md`、`domains/F7-further-study/skills/local/grad-plan/SKILL.md`、`domains/F7-further-study/skills/local/material-kit/SKILL.md`、`domains/F7-further-study/skills/local/school-pick/SKILL.md`
4. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
5. **DUT 绑定点**：见 `domains/F7-further-study/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（用户自查页面；工具不采集页面内容）。
6. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。
