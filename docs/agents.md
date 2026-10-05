# 人格（Agents）

人格是**预置的角色与工作方式**，不是新的能力。它们负责决定「用哪种语气、按什么顺序调用哪些 skill」，能力本身仍由 `skills/` 提供。

| 人格 | 面向 | 常用 skill |
|---|---|---|
| `study-coach` | 学习方法与备考 | `explain-stepwise` `error-diagnose` `faster-cycle` `exam-sprint` `recall-schedule` |
| `research-librarian` | 科研检索与写作 | `lit-fetch` `citation-verify` `reading-note` `paper-outline` `cite-normalize` `data-lab` `code-mentor` |
| `campus-concierge` | 校务与平台代办 | `campus-search` `advisor-finder` `notice-track` `campus-desk` `course-select` `campus-proof-guide` `dorm-life` `portal-operator` |

## 规则

1. 人格不复制 skill 内容，只负责编排。
2. 三个人格共享同一套行为准则与安全兜底（见 `skills/using-qihang/SKILL.md`）。
3. 人格之间不互相调用；需要别的能力时直接调用对应 skill。
4. 没有匹配人格时按 `using-qihang` 的路由直接选 skill。
