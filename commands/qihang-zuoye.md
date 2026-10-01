---
description: 学术表达（E 域）：实验报告 / 课程论文 / 展示 PPT
argument-hint: [类型 主题 字数/时长 截止日]
---

命中 **E 域 · 学术表达**。需求：$ARGUMENTS

1. 澄清三项：类型（实验报告 / 课程论文 / PPT）？主题与字数？截止日？
2. 探测 → 缺则装 → 调用：
   - `anthropics/skills`（docx / pptx / xlsx / pdf 文档底座）
   - `Imbad0202/academic-research-skills`（论文全流程 + 模拟审稿预审）
   - `kgraph57/paper-writer-skill`（IMRAD 实验报告）
   - `Gabberflast/academic-pptx-skill`（答辩 PPT 结构）
   ```bash
   /plugin marketplace add anthropics/skills
   /plugin marketplace add Imbad0202/academic-research-skills
   ```
3. 输出：① 结构大纲 ② 各节字数分配 ③ 3 条改进建议 ④ 交付文件落点。
4. 免责：AI 为副驾驶，不代写、不隐藏 AI 使用痕迹。
