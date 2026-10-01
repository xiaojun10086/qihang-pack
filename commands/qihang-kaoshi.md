---
description: 备考冲刺（D 域）：考前 N 天生成冲刺路线图
argument-hint: [科目 章节 考试日期 剩余天数]
---

命中 **D 域 · 备考冲刺**。需求：$ARGUMENTS

1. 澄清三项（缺一即问）：科目与章节？距考试几天？要「冲刺计划」还是「错题卡组」？
2. 探测 → 缺则装 → 调用：
   - 首选 `GlacierXiaowei/structured-learning-skill`（中文，3 步突击 / 7 步系统，会判分记错）
   - 备用 `peter209393/anki-card-skills`（生成可导入卡组）
   - 再备 `sickn33/agentic-awesome-skills · examprep-ai`（高分路线图 + 题目预测）
   ```bash
   npx skills add glacierxiaowei/structured-learning
   ```
3. 输出：7 天倒排计划（每天 ≤2 个番茄钟），产物给出 `.apkg` 或任务清单落点。
