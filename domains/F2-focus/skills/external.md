# F2 · 作息与专注 — 库外 skill 候选

> **使用规则**：先确认库内 skill `focus-block` 不能满足需求，再读本表。
> 安装前三步：① 探测是否已装 ② **读源码与许可证** ③ 装后验证。
> **摘录红线**：GPL-3.0 与「无 LICENSE」一律**只做外部调用，不得复制内容进本包**。

| # | Skill | 仓库 | 许可证 | 合规判定 | 安装命令 |
|---|---|---|---|---|---|
| 1 | `deep-work` | `alirezarezvani/claude-skills` | MIT | ✅ 合法 | `/plugin marketplace add alirezarezvani/claude-skills` |
| 2 | `habit-tracker` | `eddiebelaval/squire` | MIT | ⚠️ 有风险行为 | `手动 install.sh（需 API Key）` |
| 3 | `pomodoro` | `jakedahn/pomodoro` | MIT | ⚠️ 停滞 | `npx skills add jakedahn/pomodoro（仅 macOS ARM）` |

## ⚠️ 合规提醒

- **`habit-tracker`**（eddiebelaval/squire）：内容会上传第三方或密钥落盘，用前先读源码
- **`pomodoro`**（jakedahn/pomodoro）：近 11 个月未更新；二进制仅 macOS ARM

## 降级链

库内 skill → 上表第 1 项 → 上表第 2 项 → 上表第 3 项 → 纯提示词模式

> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`