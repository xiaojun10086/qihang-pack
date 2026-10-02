# S1 · 课程答疑 — 库外 skill 候选

> **使用规则**：先确认库内 skill `explain-stepwise` 不能满足需求，再读本表。
> 安装前三步：① 探测是否已装 ② **读源码与许可证** ③ 装后验证。
> **摘录红线**：GPL-3.0 与「无 LICENSE」一律**只做外部调用，不得复制内容进本包**。

| # | Skill | 仓库 | 许可证 | 合规判定 | 安装命令 |
|---|---|---|---|---|---|
| 1 | `teach` | `mattpocock/skills` | MIT | ✅ 合法 | `npx skills add mattpocock/skills@teach` |
| 2 | `math-skill` | `googlarz/math-skill` | 无 LICENSE | ⛔ **无 LICENSE** | `npx skills add googlarz/math-skill` |
| 3 | `gurukul-ai` | `somenssarkar/gurukul-ai` | 无 LICENSE | ⛔ **无 LICENSE** | `手动 clone（需 API Key）` |
| 4 | `chem-skill` | `ghutchis/chem-skill` | MIT | ✅ 合法 | `手动 zip（纯本地）` |

## ⚠️ 合规提醒

- **`math-skill`**（googlarz/math-skill）：默认保留所有权利 —— **禁止摘录、禁止再分发**，仅限本地自用
- **`gurukul-ai`**（somenssarkar/gurukul-ai）：默认保留所有权利 —— **禁止摘录、禁止再分发**，仅限本地自用

## 降级链

库内 skill → 上表第 1 项 → 上表第 2 项 → 上表第 3 项 → 纯提示词模式

> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`