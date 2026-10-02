---
name: qihang
description: 「启航」学伴包库入口卡（1 级库）：需求明确 → 锁定域 → 锁定 skill → 库内优先。
---

# 启航 · 库入口（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**提出需求即可；
> 本卡列出库入口的标准处理步骤，供人工检索与插件装载，**不需要输入任何命令**。

1. **需求明确**：读 `library/clarity.md`，拆 6 槽位，算 `U = 1 − Σ(wᵢcᵢ)/Σwᵢ`。
   `U > 0.30` **且关键槽位 `O/T/D` 缺失或出现歧义（`cᵢ = 0.5`）** → 追问
   （≤3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。
2. **锁定域**：读 `domains/_registry.md`，用触发词匹配；多域命中走跨域串联（≤4 域）。
3. **域审查**：读 `library/domain-review.md`，用该域「不覆盖」条目复核，越界则改锁。
4. **锁定 skill**：读 `domains/<域>/_domain.md` → 用**库内 skill**（`skills/local/`）。
5. **库外兜底**：仅当库内不满足，才读 `skills/external.md` 走安装。
6. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档（F3/F5 除外）。
