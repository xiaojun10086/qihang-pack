---
description: 「启航」学伴包入口（1级库）：需求明确 → 锁定域 → 锁定skill → 库内优先
argument-hint: [你的需求，可留空]
---

按 1 级 skill 库规则处理：$ARGUMENTS

1. **需求明确**：读 `~/.claude/skills/qihang/library/clarity.md`，拆 6 槽位，算 `U = 1 − Σ(wᵢcᵢ)/Σwᵢ`。
   `U > 0.30` **且关键槽位 O/T/D 有缺失** → 追问（≤3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。
　（关键槽位齐全时直接放行，见 `library/clarity.md` §5 例外 2 与 §8 例 A。）
2. **锁定域**：读 `domains/_registry.md`，用触发词匹配；多域命中走跨域串联。
3. **域审查**：读 `library/domain-review.md`，用该域「不覆盖」条目复核，越界则改锁。
4. **锁定 skill**：读 `domains/<域>/_domain.md` → 用**库内 skill**（`skills/local/`）。
5. **库外兜底**：仅当库内不满足，才读 `skills/external.md` 走安装。
6. **输出**：按 `library/output-spec.md`，≤6 条要点，写入学习档案。
