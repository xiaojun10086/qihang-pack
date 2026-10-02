# 「启航」新生学习生活一体化学伴包 v2.9.0

> **三级结构：skill 库（1级）→ 域（2级）→ skill（3级）**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：**LearnBuddy（= 连小理）**（单一目标平台）

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── INSTALL.md                安装指南（LearnBuddy）
├── PROJECT.md                项目文档（简略）
├── ROADMAP.md                分阶段开发计划
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── .codebuddy-plugin/        LearnBuddy / WorkBuddy 插件清单
├── library/                  ★1 级 · skill 库（既是 skill 也是库）
│   ├── SKILL.md              库本体
│   ├── login-policy.md       登录选择原则（A/B/C 三档）
│   ├── clarity.md            职责1：需求明确（6 槽位 + 澄清门）
│   ├── domain-review.md      职责2：域审查（锁定/越界/跨域/无域兜底）
│   ├── output-spec.md        职责3：输出规范（模板 + 简略原则）
│   ├── memory.md             职责4：学习档案（分层落点 + 敏感域红线）
│   ├── domain-review-cases.md  越界用例集（22 条）
│   └── output-checklist.md     输出 7 项硬校验
├── domains/                  ★2 级 · 域（19 个）
│   ├── _registry.md          域总表 + 方向自查
│   └── <域ID>-<slug>/
│       ├── _domain.md        域定义：边界 / 触发词 / DUT 绑定点
│       └── skills/           ★3 级 · skill
│           ├── local/<name>/SKILL.md   库内 skill（优先，无需安装）
│           └── external.md             库外候选 + 许可证列（库内不满足才装）
├── references/
│   ├── dlut-official-sites.md      DUT 公开站信息库（139 条条目）
│   ├── dlut-login-sites.md         DUT 私密站清单（方案 A + Profile 隔离）
│   ├── dlut-field-map.md           私密站字段映射表
│   ├── skill-sources.md            12 个 skill 探测平台（含可达性实测）
│   ├── skill-matrix-v3.md          **库外候选多源比对矩阵（19 域选优）**
│   ├── skill-compliance-audit.md   合法性 + 可用性自检报告
│   ├── platforms.md                各平台适配表
│   ├── e2e-scenarios.md            3 条端到端演示路径
│   ├── acceptance-v2.md            验收报告 v2（赛道二 5 要素 + 4 维度）
│   ├── validation-report.md        阶段 1/2 验收报告
│   ├── review-report-v2.2.md      复查报告 v2.2
│   ├── review-report-v2.3.md      复查报告 v2.3
│   ├── review-report-v2.4.md      **复查报告 v2.4（本轮）**
│   ├── stress-test-v3.md          **多轮压测报告**
│   ├── alignment-audit-v3.md      全量对齐 · 可行性 · 多轮复核（v3）
│   ├── browser-matrix.md / dlut-site-profiles.md / dlut-url-verification.md
│   └── 需求确认书-v2三级结构.md
├── commands/                    21 张 LearnBuddy 域入口卡（库 + 校情 + 19 域）
└── scripts/
    ├── qihang.sh                管理脚本（平台探测 / 状态 / 档案 / 信息库统计）
    ├── dlut-read.sh             DUT 私密站只读取数（L1/L2/L3 硬拦截）
    ├── selfcheck.sh             结构自检（计数 / 交叉引用 / 红线一致性）
    ├── audit.sh                 安全审计（危险命令 / 凭证 / L3 门禁实测）
    ├── regress.sh               **行为回归**（澄清门算例 / L3 门禁矩阵，支持多轮）
    ├── aligncheck.py            全量文件级对齐审计（15 组断言）
    └── _build/build_*.py        结构生成器（改域后按序重跑）
```

## 2. 工作流（严格按序）

```
用户需求
  ↓ ①需求明确  library/clarity.md             6 槽位 + 澄清门，U ≤ 0.30
  ↓ ②锁定域    domains/_registry.md            触发词匹配
  ↓ ③域审查    library/domain-review.md        边界复核、越界改锁
  ↓ ④锁定skill domains/<域>/_domain.md         读库内 skill
  ↓ ⑤库内优先  skills/local/                   命中即用，无需安装
  ↓ ⑥库外兜底  skills/external.md              仅库内不满足才安装
  ↓ ⑦输出      library/output-spec.md          ≤6 条要点 + 过 output-checklist
  ↓ ⑧归档      library/memory.md               写学习档案（F3/F5 敏感域除外）
```

**核心规则：库内优先** —— 库内有就不装库外，避免低星 / 无许可证 / 需 API Key 的第三方风险。

## 3. 19 个域（方向自查：学习 / 生活 / 科研全覆盖）

| 大类 | 域 |
|---|---|
| **S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **R 科研（5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 |

**自查结果**：19 域 × 每域 **2 个**库内 skill = **38 个库内 skill**；**12 个域**有「合规且适配 DUT」的库外**最优解**（另有 3 个域有候选但不达门禁）；**7 个域为纯自建**（F1、F3、F4、F5、F6、F7、R5 —— 库外要么许可证不清、要么环境错位）。详见 `references/skill-matrix-v3.md`。

## 4. 安装与使用

**LearnBuddy / WorkBuddy（推荐）**

```bash
cp -r qihang-pack ~/.learnbuddy/skills/qihang
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

用**自然语言**即可，无需斜杠命令。包根含 `.codebuddy-plugin/plugin.json`，可作插件识别。

21 张 `commands/` 域入口卡随包提供（不需要输入命令）；学习档案见 `library/memory.md`，自检脚本见 `scripts/`。

```bash
# 通用管理脚本（探测 LearnBuddy 安装位置）
bash scripts/qihang.sh platform   # 探测本机平台与安装路径
```

```bash
bash scripts/selfcheck.sh         # 结构与计数自检（v2.7 起 38 skill）
bash scripts/audit.sh             # 安全审计 + L3 门禁实测
bash scripts/qihang.sh status     # 三级结构完整度
bash scripts/qihang.sh platform   # 平台探测与安装路径
bash scripts/qihang.sh domains    # 19 域清单
bash scripts/qihang.sh records    # 学习档案（--clear 清空）
bash scripts/qihang.sh probe      # 库外候选缺失项
bash scripts/qihang.sh registry   # DUT 信息库统计
bash scripts/qihang.sh new-term   # 换学期重置

# DUT 私密站只读取数（L1 直读 / L2 需 --yes / L3 拒绝）
bash scripts/dlut-read.sh 课表 --dry-run
```

## 5. DUT 融入

| 类型 | 文件 | 融入方式 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | **139 条**条目（表格行 159），19 个域的 `_domain.md` 各自标注绑定点 |
| 私密站 | `references/dlut-login-sites.md` | 19 个需登录站点，**方案 A 受控浏览器 + 只读**，分 L1/L2/L3 授权 |

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | `scripts/_build/build_qihang_v2.py` 的 `DOMAINS` → 重跑（顺序见 `scripts/_build/README.md`） | 改数据即可 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 加库外候选 | 对应域 `skills/external.md` | 1 行 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 外部 skill 均为公开开源项目（2026-10-01 检索），安装前请读源码与许可证。
- `CC-BY-NC` 禁止商用；部分仓库无 LICENSE（study-skill / math-skill / gurukul-ai）。
- `sickn33/agentic-awesome-skills`（3113 脚本、含攻击性技能）**禁止整体安装**。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。
