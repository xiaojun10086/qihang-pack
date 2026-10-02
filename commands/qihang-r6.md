---
name: qihang-r6
description: R6 信息搜集与输出（科研类）域入口卡：导师信息、教师主页、部门联系方式、通知公告、信息公开。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# R6 · 信息搜集与输出（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：导师信息、老师是谁、教师主页、联系方式、部门电话、通知、公告、信息公开

**边界**：校内网站公开信息（导师 / 教师、部门、通知、机构、场馆）的搜集与规范输出
**不覆盖**：文献检索（→R1）；需登录的私密站内容（→F1）；选导师规划（→F7）

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位，算 U；**先过 §5 的 6 条「不追问例外」（优先级 4 红线 > 6 通用知识型 > 1 校情横切 > 2 关键槽齐全 > 5 紧急豁免 > 3 显式要求）**；未命中例外且关键槽 `O/T/D` 缺失 / 歧义（`cᵢ = 0.5`）→ 才追问。
2. **域审查**：读 `domains/R6-info-retrieval/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内择优**：按**主体与任务**在本域 4 个库内 skill 中择优 —— 首选 `advisor-finder`；其余 `campus-search` / `notice-track` / `org-lookup` 按触发场景择用
   路径：`domains/R6-info-retrieval/skills/local/advisor-finder/SKILL.md`、`domains/R6-info-retrieval/skills/local/campus-search/SKILL.md`、`domains/R6-info-retrieval/skills/local/notice-track/SKILL.md`、`domains/R6-info-retrieval/skills/local/org-lookup/SKILL.md`
4. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点（每条标来源与核验状态），并按 `library/memory.md` 归档。
5. **DUT 绑定点**：见 `domains/R6-info-retrieval/_domain.md`；本域只处理公开站，不涉及登录档位。
