---
name: qihang
description: 「启航」大连理工大学新生学习生活一体化学伴包（v2.0 三级结构）。入口 skill，负责需求明确、域审查、输出规范与路由。当用户提出与大连理工大学校情、课程学习、备考、笔记、作业、科研、校园生活相关的模糊求助时使用。
version: 2.0.0
license: MIT
tags: [dlut, campus, learning, library, orchestrator]
---

# 「启航」学伴包 · skill 库本体（Level 1）

三级结构：**skill 库（本入口）→ 域 → skill**

```
library/        1 级 · skill 库（只做需求明确 / 域审查 / 输出规范 / 路由）
domains/        2 级 · 域（19 个，覆盖 学习 / 生活 / 科研）
  └─ skills/
       ├─ local/      3 级 · 库内 skill（优先，无需安装）
       └─ external.md 3 级 · 库外候选（库内不满足时才装）
references/     数据与文档（DUT 官网库 / 私密站库 / 验收报告）
```

## 工作流（严格按序，不可跳步）

```
用户需求
  ↓ ①需求明确  library/clarity.md           6 槽位 + 澄清门，U ≤ 5% 才继续
  ↓ ②锁定域    domains/_registry.md          用触发词匹配；无命中走 domain-review.md 兜底
  ↓ ③域审查    library/domain-review.md      确认域边界、越界拦截、跨域串联
  ↓ ④锁定 skill domains/<域>/_domain.md      读该域的库内 skill
  ↓ ⑤库内优先  domains/<域>/skills/local/   命中即调用，无需安装
  ↓ ⑥库外兜底  domains/<域>/skills/external.md  仅当库内不满足才安装
  ↓ ⑦输出      library/output-spec.md        ≤6 条要点，写入学习档案
```

## 三份规则文件（1 级库的本体）

| 文件 | 职责 |
|---|---|
| `library/clarity.md` | 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级 |
| `library/domain-review.md` | 域审查：锁定 / 跨域 / 越界 / 无域兜底 |
| `library/output-spec.md` | 输出规范：统一模板 + 简略原则 |

## 快捷调用

| 入口 | 用法 |
|---|---|
| 自然语言 | 「我高数快挂了」「机械学院官网是啥」 |
| 斜杠命令 | `/qihang` `/qihang-dlut` + 19 个域命令，见 `commands/` |
| 一键脚本 | `bash scripts/qihang.sh {probe\|install\|status\|registry\|new-term}` |

## 硬规则

1. **库内优先**：库内有该场景 skill 就不装库外。
2. **DUT 强绑定**：命中大工关键词必须先查 `references/dlut-official-sites.md`；未收录固定回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」；**禁止编造 URL / 电话 / 单位名**。
3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件（见 `references/dlut-login-sites.md`）。
4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心。
