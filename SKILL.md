---
name: qihang
description: 「启航」大连理工大学新生学习生活一体化学伴包（三级结构）。入口 skill，负责需求明确、域审查、输出规范与路由。当用户提出与大连理工大学校情、课程学习、备考、笔记、作业、科研、校园生活相关的模糊求助时使用。
version: 2.11.0
license: MIT
tags: [dlut, campus, learning, library, orchestrator]
---

# 「启航」学伴包 · 入口（v2.11.0）

三级结构：**skill 库（本入口）→ 域 → skill**

```
library/        1 级 · skill 库（只做需求明确 / 域审查 / 输出规范 / 路由）
domains/        2 级 · 域（19 个，覆盖 学习 / 生活 / 科研）
  └─ skills/
       ├─ local/      3 级 · 库内 skill（优先，无需安装）
       └─ external.md 3 级 · 库外候选（库内不满足时才装）
references/     数据与文档（DUT 官网库 / 私密站库）
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
| `library/memory.md` | 学习档案：四类内容 + 分层落点 + 敏感域红线 |
| `library/login-policy.md` | 登录选择原则：A/B/C 三档 + 标准话术 + 安全保障 |

## 快捷调用

| 入口 | 用法 |
|---|---|
| 自然语言 | 「我高数快挂了」「机械学院官网是啥」 |
| 斜杠命令 | `/qihang` `/qihang-dlut` + 19 个域命令，见 `commands/` |
| 一键脚本 | `bash scripts/qihang.sh {probe\|install\|status\|registry\|new-term}` |


## 红线总览（优先级高于澄清门）

**顺序：先判红线 → 再判登录档位 → 再判澄清门 → 再锁域。**
命中红线时**不追问细节**（追问等于变相承诺）；**仅当「需要改锁」时可追问 1 个问题**，其余一律**直接拒绝 + 给合规替代**。

| 类别 | 覆盖域 | 红线 |
|---|---|---|
| **学术诚信** | S3 S4 S5 R1 R2 R4 R5 | 不代写正文 / 不编造数据 / 不伪造引文 / 不代考买卖答案 / 不代改规避查重 / 不隐藏 AI 痕迹 |
| **代操作** | F1 F4 F6 R3 R4 | 不代操作系统（选课/缴费/提交/投稿/报名/**志愿时长登记**） |
| **编造 / 代写文书** | F7 F8 | 不编造经历、学历、获奖、时间线；**不代写个人陈述 / 文书正文** |
| **安全兜底** | F2 F3 F4 F5 F6 | F3 危机立即转介并停止其他建议（**24h 通道 12356 / 010-82951332**；**已有具体计划 → 立即 110 / 120**）；F4 已转账立即止损（挂失 + 96110 + 110）；F5 急症直接 120；F6 伤病改锁 F5 |
| **隐私** | F4 F5 全包 | 第三方健康 / 财务 / 心理隐私不分析、不外传、不写档 |
| **L3 禁读** | 私密站 | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细 |

**拒绝必须给出路**：不做「只说不做」的拒绝，须给合规替代（给结构 / 给路径 / 给规范）。

## 硬规则

1. **库内优先**：库内有该场景 skill 就不装库外。
2. **DUT 强绑定**：命中大工关键词必须先查 `references/dlut-official-sites.md`；未收录固定回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」；**禁止编造 URL / 电话 / 单位名**。
3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件（见 `references/dlut-login-sites.md`）。
4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心。
