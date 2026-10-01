---
description: 学科答疑（C 域）：数学 / 物理 / 化学 / 编程逐步讲解
argument-hint: [题目或知识点]
---

命中 **C 域 · 学科答疑**。问题：$ARGUMENTS

1. 先判学科 → 探测 → 缺则装 → 调用：
   | 学科 | Skill | 安装 |
   | --- | --- | --- |
   | 数学 / 统计 | `googlarz/math-skill` | `npx skills add googlarz/math-skill` |
   | 物理 | `somenssarkar/gurukul-ai` | `npx skills add somenssarkar/gurukul-ai` |
   | 化学 | `ghutchis/chem-skill` | `npx skills add ghutchis/chem-skill` |
   | 编程 | `egouilliard-leyton/python-tutor-skill` | `npx skills add egouilliard-leyton/python-tutor-skill` |
2. **先要用户自己写一步**（retrieve-first），再给提示，不直接给答案。
3. 输出：① 卡点定位 ② 一句关键提示 ③ 正确解法 ④ 同类题 1 道。
