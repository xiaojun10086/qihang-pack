---
name: qihang-dlut
description: 「启航」校情入口卡：查大连理工大学学院 / 校区 / 教务 / 职能部门 / 需登录站点。
---

# 校情横切 · 入口（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**问「机械学院官网是啥」即可，
> 本卡是该横切的标准处理步骤。

**硬性规则**
1. **先读** `references/dlut-official-sites.md`（公开站）；涉及登录项再读 `references/dlut-login-sites.md`。
2. 命中 → 输出 `【结论】+【网址】+【状态 ✅/⚠️】+【建议】`（口径见 `library/output-spec.md` §2「校情查询」）。
3. **未命中 → 固定回复**：「信息库未收录该条目，建议访问 https://www.dlut.edu.cn/ 核实」。
4. **禁止编造**任何 dlut.edu.cn 下的 URL、电话或单位名。
5. 标 ⚠️ 的条目必须带上「待核实」。
6. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。

**私密站（方案 A）**：用受控浏览器打开 → 请你本人登录 → 我只读读取 → **不落盘、不外传**。
涉 L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。
**必须使用独立 Profile**：`~/.qihang/browser-profile`。
