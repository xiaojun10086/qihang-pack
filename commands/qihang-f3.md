---
name: qihang-f3
description: F3 身心与社交（生活类）域入口卡：焦虑、压力、emo、室友、社团、人际。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# F3 · 身心与社交（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：焦虑、压力、emo、室友、社团、人际

**边界**：情绪压力疏导、适应问题、宿舍与人际、社团选择
**不覆盖**：**不做心理诊断、不做危机干预**；出现自伤/自杀念头立即转介专业资源

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/F3-wellbeing/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 5 个库内 skill 中择优 —— 首选 `wellbeing-checkin`；其余 `adapt-guide` / `club-pick` / `peer-talk-script` / `roommate-mediate` 按触发场景择用
   路径：`domains/F3-wellbeing/skills/local/adapt-guide/SKILL.md`、`domains/F3-wellbeing/skills/local/club-pick/SKILL.md`、`domains/F3-wellbeing/skills/local/peer-talk-script/SKILL.md`、`domains/F3-wellbeing/skills/local/roommate-mediate/SKILL.md`、`domains/F3-wellbeing/skills/local/wellbeing-checkin/SKILL.md`
4. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
5. **DUT 绑定点**：见 `domains/F3-wellbeing/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
