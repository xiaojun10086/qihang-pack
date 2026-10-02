---
name: qihang
description: 「启航」大连理工大学新生学习·生活·科研一体化学伴包（三级结构：skill 库 → 域 → skill）。当用户提出与大连理工大学校情（学院/校区/选课/校历/职能部门/联系方式）、大学课程学习、备考复习、课堂笔记、作业与实验报告、科研文献、作息专注、升学求职相关的**模糊求助**时使用。负责需求明确（澄清门）、域审查、库内优先路由与输出规范。
version: 2.9.0
license: MIT
agent_created: true
tags: [dlut, campus, learning, freshman, library, orchestrator, learnbuddy]
---

# 「启航」学伴包 · 入口（v2.9.0）

三级结构：**skill 库（本入口）→ 域 → skill**

```
library/        1 级 · skill 库（只做 需求明确 / 域审查 / 输出规范 / 记忆归档）
domains/        2 级 · 域（19 个，覆盖 学习 / 生活 / 科研）
  └─ skills/
       ├─ local/      3 级 · 库内 skill（优先，无需安装）
       └─ external.md 3 级 · 库外候选（库内不满足时才装）
references/     数据与文档（DUT 官网库 / 私密站库 / 合规自检 / 平台适配）
```

## 工作流（严格按序，不可跳步）

```
用户需求
  ↓ ①需求明确  library/clarity.md           6 槽位 + 澄清门，U ≤ 0.30 才继续
  ↓ ②锁定域    domains/_registry.md          用触发词匹配；无命中走 domain-review.md 兜底
  ↓ ③域审查    library/domain-review.md      确认域边界、越界拦截、跨域串联
  ↓ ④锁定 skill domains/<域>/_domain.md      读该域的库内 skill
  ↓ ⑤库内优先  domains/<域>/skills/local/   命中即调用，无需安装
  ↓ ⑥库外兜底  domains/<域>/skills/external.md  仅当库内不满足才安装
  ↓ ⑦输出      library/output-spec.md        ≤6 条要点，过 output-checklist 校验
  ↓ ⑧归档      library/memory.md             写学习档案（F3/F5 敏感域除外）
```

## 五份规则文件（1 级库的本体）

| 文件 | 职责 |
|---|---|
| `library/clarity.md` | 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级 |
| `library/domain-review.md` | 域审查：锁定 / 跨域 / 越界 / 无域兜底 |
| `library/output-spec.md` | 输出规范：统一模板 + 简略原则 + 交付前校验 |
| `library/memory.md` | **学习档案**：四类内容 + 分层落点 + 敏感域红线 |
| **`library/login-policy.md`** | **登录选择原则**：A/B/C 三档 + 标准话术 + 安全保障 |

**配套**：`library/domain-review-cases.md`（22 条越界用例，含 3 条反例）· `library/output-checklist.md`（7 项硬校验）

## 快捷调用

| 入口 | 用法 |
|---|---|
| **LearnBuddy / WorkBuddy** | **自然语言即可**（靠 `description` 自动发现，无需命令）；装到 `~/.learnbuddy/skills/qihang/` |
| 域入口卡 | `commands/` 21 张（库入口 + 校情 + 19 域），供人工检索 / 插件装载 |
| 一键脚本 | `bash scripts/qihang.sh {status\|platform\|probe\|install\|domains\|registry\|records\|new-term}` |

平台适配详见 `references/platforms.md` 与 `INSTALL.md`。


## 红线总览（v2.5.0 · 复核后新增，优先级高于澄清门）

**顺序：先判红线 → 再判澄清门 → 再锁域。** 命中红线时**不追问细节**（追问等于变相承诺）。

| 类别 | 覆盖域 | 红线 |
|---|---|---|
| **学术诚信** | S3 S4 S5 R1 R2 R4 R5 | 不代写正文 / 不编造数据 / 不伪造引文 / 不代考买卖答案 / 不代改规避查重 / 不隐藏 AI 痕迹 |
| **代操作** | F1 F4 R3 R4 | 不代操作系统（选课/缴费/提交/投稿/报名） |
| **编造经历** | F7 F8 | 不编造经历、学历、获奖、时间线 |
| **安全兜底** | F2 F3 F4 F5 F6 | F3 危机立即转介并停止其他建议；F4 已转账立即止损（挂失 + 96110 + 110）；F5 急症直接 120；F6 伤病改锁 F5 |
| **隐私** | F4 F5 全包 | 第三方健康 / 财务 / 心理隐私不分析、不外传、不写档 |
| **L3 禁读** | 私密站 | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细（**关键词包含匹配，变体同样拦截**） |

**拒绝必须给出路**：不做「只说不做」的拒绝，须给合规替代（给结构 / 给路径 / 给规范）。

## 硬规则

1. **库内优先**：库内有该场景 skill 就不装库外。
2. **DUT 强绑定**：命中大工关键词必须先查 `references/dlut-official-sites.md`；未收录固定回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」；**禁止编造 URL / 电话 / 单位名**。
3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件；**必须用独立浏览器 Profile**（见 `references/dlut-login-sites.md` §0.1）。
4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心；内容**不写入任何记忆层**。
5. **摘录红线**：GPL-3.0 与「无 LICENSE」的库外 skill **只做外部调用，不得复制内容进本包**（见 `references/skill-compliance-audit.md`）。
6. **登录由用户决定（对话中）**：先判 A/B/C 三档 —— A 不登录即可答就直接答；B 先给不登录版本再**一句话**提示可登录；C 才明确请求。请求时必须含「**为什么需要 / 我怎么做 / 安全保障 / 你可以不登录**」四要素。**绝不为了「输出更全」而强行索要登录**；用户拒绝登录时**仍给完整通用流程**（见 `library/login-policy.md`）。
7. **信息尽量全面，但以公开优先**：能公开站说满就不读站内；确需登录时**一次问清、批量读取**（复用 SSO 同会话），只沉淀「栏目结构」元信息，**不沉淀用户个人数据**。

