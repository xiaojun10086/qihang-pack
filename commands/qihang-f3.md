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

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `domains/F3-wellbeing/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill `peer-talk-script` / `wellbeing-checkin`
   路径：`domains/F3-wellbeing/skills/local/peer-talk-script/SKILL.md`、`domains/F3-wellbeing/skills/local/wellbeing-checkin/SKILL.md`
4. **库外兜底**：仅当库内不满足，才读 `domains/F3-wellbeing/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `domains/F3-wellbeing/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
