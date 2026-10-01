# 「启航」新生学习生活一体化学伴包 v2.0

> **三级结构：skill 库（1级）→ 域（2级）→ skill（3级）**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：连小理 / Claude Code / Codex / Cursor / Copilot

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── PROJECT.md                项目文档（简略）
├── ROADMAP.md                分阶段开发计划
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── library/                  ★1 级 · skill 库（既是 skill 也是库）
│   ├── SKILL.md              库本体
│   ├── clarity.md            职责1：需求明确（6 槽位 + 澄清门）
│   ├── domain-review.md      职责2：域审查（锁定/越界/跨域/无域兜底）
│   └── output-spec.md        职责3：输出规范（模板 + 简略原则）
├── domains/                  ★2 级 · 域（19 个）
│   ├── _registry.md          域总表 + 方向自查
│   └── <域ID>-<slug>/
│       ├── _domain.md        域定义：边界 / 触发词 / DUT 绑定点
│       └── skills/           ★3 级 · skill
│           ├── local/<name>/SKILL.md   库内 skill（优先，无需安装）
│           └── external.md             库外候选（库内不满足才装）
├── references/
│   ├── dlut-official-sites.md   DUT 公开站信息库
│   ├── dlut-login-sites.md      DUT 私密站清单（方案 A）
│   ├── skill-sources.md         12 个 skill 探测平台
│   ├── validation-report.md     验收报告
│   └── 需求确认书-v2三级结构.md
├── commands/                    斜杠命令
└── scripts/
    ├── qihang.sh                管理脚本
    └── build_qihang_v2.py       结构生成器（改域后重跑）
```

## 2. 工作流（严格按序）

```
用户需求
  ↓ ①需求明确  library/clarity.md             6 槽位 + 澄清门，U ≤ 5%
  ↓ ②锁定域    domains/_registry.md            触发词匹配
  ↓ ③域审查    library/domain-review.md        边界复核、越界改锁
  ↓ ④锁定skill domains/<域>/_domain.md         读库内 skill
  ↓ ⑤库内优先  skills/local/                   命中即用，无需安装
  ↓ ⑥库外兜底  skills/external.md              仅库内不满足才安装
  ↓ ⑦输出      library/output-spec.md          ≤6 条要点 + 写学习档案
```

**核心规则：库内优先** —— 库内有就不装库外，避免低星 / 无许可证 / 需 API Key 的第三方风险。

## 3. 19 个域（方向自查：学习 / 生活 / 科研全覆盖）

| 大类 | 域 |
|---|---|
| **S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **R 科研（5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 |

**自查结果**：19 域 × 每域 1 个库内 skill = 19 个库内 skill；15 个域有库外候选；**4 个域为方向空白**（F3、F4、F5、F6），直接依赖库内自建 skill。

## 4. 安装与使用

```bash
# 1) 放进 skills 目录
cp -r qihang-pack ~/.claude/skills/qihang
# 2) 安装斜杠命令
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/
# 3) 查看状态（库内 skill 开箱即用，库外为可选增强）
bash ~/.claude/skills/qihang/scripts/qihang.sh status
```

```bash
bash scripts/qihang.sh status     # 三级结构完整度
bash scripts/qihang.sh domains    # 19 域清单
bash scripts/qihang.sh probe      # 库外候选缺失项
bash scripts/qihang.sh registry   # DUT 信息库统计
bash scripts/qihang.sh new-term   # 换学期重置
```

## 5. DUT 融入

| 类型 | 文件 | 融入方式 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | 160 条，19 个域的 `_domain.md` 各自标注绑定点 |
| 私密站 | `references/dlut-login-sites.md` | 19 个需登录站点，**方案 A 受控浏览器 + 只读**，分 L1/L2/L3 授权 |

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。L3 级（缴费/银行卡/身份证/邮件正文/心理记录）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | `scripts/build_qihang_v2.py` 的 `DOMAINS` → 重跑 | 改数据即可 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 加库外候选 | 对应域 `skills/external.md` | 1 行 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 外部 skill 均为公开开源项目（2026-10-01 检索），安装前请读源码与许可证。
- `CC-BY-NC` 禁止商用；部分仓库无 LICENSE（study-skill / math-skill / gurukul-ai）。
- `sickn33/agentic-awesome-skills`（3113 脚本、含攻击性技能）**禁止整体安装**。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。
