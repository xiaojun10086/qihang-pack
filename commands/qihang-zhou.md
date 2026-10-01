---
description: 学业节奏（A 域）：排本周 DDL 与考试倒排
argument-hint: [本周任务 / 截止日 / 考试日期]
---

命中 **A 域 · 学业节奏**。输入：$ARGUMENTS

1. 探测 → 缺则装 → 调用：
   - `googleworkspace/gws-tasks`（DDL 清单）
   - `googleworkspace/gws-calendar`（时间块排布）
   ```bash
   /plugin marketplace add googleworkspace/skills
   ```
2. 读取 `config.yaml` 的 `courses` 与 `exam_weeks`，自动倒排。
3. 输出：① 本周 DDL 按「紧急×重要」排序（≤7 条）② 每天 1–2 个时间块 ③ 冲突项与取舍建议 ④ 已写入日历/任务的落点。
