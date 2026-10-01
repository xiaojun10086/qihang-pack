# 「启航」学伴包 · 项目文档

> 版本 v2.0 ｜ 更新 2026-10-01 ｜ 面向大连理工大学 2026 级本科新生
> 适配：连小理 / Claude Code / Codex / Cursor / Copilot

---

## 1. 一句话定位

把「新生一句模糊求助」变成「结构化可执行方案」的**可插拔 skill 包**；
**三级结构：skill 库 → 域 → skill**，并强绑定大工的公开站与需登录的私密站。

---

## 2. 三级结构

```
【1级】library/        skill 库（既是 skill 也是库）
       只做三件事：①需求明确 ②域审查 ③输出规范，不承载具体业务
        ↓
【2级】domains/        19 个域，覆盖 学习 / 生活 / 科研
        ↓
【3级】skills/         local/  库内 skill（优先，无需安装）
                       external.md  库外候选（库内不满足才装）
```

| 级别 | 允许做 | 禁止做 |
|---|---|---|
| 1 级 | 澄清需求、锁定域、审查域、规范输出、路由 | 承载学科知识、写死业务 |
| 2 级 | 定义边界与触发词、列域内 skill、声明 DUT 绑定点 | 直接回答问题 |
| 3 级 | 执行具体任务 | 跳过澄清门 |

---

## 3. 工作流（严格按序，不可跳步）

```
用户需求
  ↓ ① 需求明确   library/clarity.md          6 槽位 + 澄清门，U ≤ 5% 才继续
  ↓ ② 锁定域     domains/_registry.md         触发词匹配
  ↓ ③ 域审查     library/domain-review.md     边界复核，越界改锁
  ↓ ④ 锁定 skill domains/<域>/_domain.md      读该域的库内 skill
  ↓ ⑤ 库内优先   skills/local/                命中即调用，无需安装
  ↓ ⑥ 库外兜底   skills/external.md           仅库内不满足才安装
  ↓ ⑦ 输出       library/output-spec.md       ≤6 条要点 + 写学习档案
```

**澄清门**：`U = 1 − ∏cᵢ`；`U > 5%` 追问，最多 3 轮、每轮 ≤3 问，
优先级 `时间 > 对象 > 产出 > 约束 > 背景 > 任务`；3 轮后按假设执行并显式标注。

**核心规则：库内优先** —— 库内有就不装库外，规避低星 / 无许可证 / 需 API Key 的第三方风险。

---

## 4. 19 个域

| 大类 | 域 |
|---|---|
| **S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **R 科研（5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 |

每域含：`_domain.md`（边界/触发词/DUT绑定点）+ `skills/local/`（1 个库内 skill）+ `skills/external.md`。
**方向空白域 4 个**（F3 / F4 / F5 / F6）—— 无成熟开源 skill，纯自建。

---

## 5. DUT 融入

| 类型 | 文件 | 内容 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | **160 条**表格行（✅ 72 / ⚠️ 23 / 学院类 65），三校区 + 全部学院 + 职能部门 |
| 私密站 | `references/dlut-login-sites.md` | **19 个**需登录站 + 方案 A 流程 + L1/L2/L3 授权 + Profile 隔离要求 |
| Skill 来源 | `references/skill-sources.md` | 12 个探测平台 |
| 验收 | `references/validation-report.md` | 4 路并行子 agent 的测试结论 |

**三大入口**：`sso.dlut.edu.cn` → `portal.dlut.edu.cn` → `jxgl.dlut.edu.cn`

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。
L3 级（缴费金额 / 银行卡 / 身份证 / 邮件正文 / 心理记录）**禁止读取**。
**Profile 必须隔离**：`--profile "$HOME/.qihang/browser-profile"`（实测踩坑，见下）。

**已实测（2026-10-01）**：`portal.dlut.edu.cn` 首页单页即可拿到 6 类 L1 数据
（课表 / 借阅 / 一卡通 / 网费 / 邮件未读 / 日程通知），是**全包最佳聚合点**。

---

## 6. 安装与使用

```bash
cp -r qihang-pack ~/.claude/skills/qihang
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/
bash ~/.claude/skills/qihang/scripts/qihang.sh status
```

| 命令 | 作用 |
|---|---|
| `/qihang` | 库入口（澄清门 → 锁域 → 锁 skill） |
| `/qihang-dlut` | 查校情（公开站 + 私密站） |
| `/qihang-s1` … `/qihang-r5` | 19 个域命令 |
| `qihang.sh status \| domains \| probe \| registry \| new-term` | 管理脚本 |

---

## 7. 当前状态（v2.0）

| 项 | 状态 |
|---|---|
| 三级结构 | ✅ 完成（95 文件，生成器驱动） |
| 19 域 + 19 库内 skill | ✅ **已产品化**：每域含可执行示例 + 4 域含安全护栏 |
| 越界用例集 / 输出校验清单 | ✅ 14 条用例（含 3 反例）· 7 项硬校验 |
| DUT 公开信息库 | ✅ 160 条 |
| DUT 私密站清单 | ✅ 19 站 + 方案 A |
| 方案 A 实机验证 | ✅ 通过（含 Profile 隔离修正） |
| 库外 skill 联调 | ⬜ 未做 |
| 学习档案（跨会话记忆） | ⬜ 未做 |
| 赛道二提交物 | 🟡 设计书已有，需按 v2.0 同步 |

---

## 8. 目录一览

```
qihang-pack/
├── SKILL.md                  入口
├── PROJECT.md                本文件
├── ROADMAP.md                分阶段开发计划
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── library/                  1级 skill 库
│   ├── SKILL.md  clarity.md  domain-review.md  output-spec.md
│   ├── domain-review-cases.md   越界用例集（14 条，含 3 反例）
│   └── output-checklist.md      输出 7 项硬校验
├── domains/                  2级 19 个域
│   └── <ID>-<slug>/{_domain.md, skills/{local/, external.md}}
├── references/               公开站 / 私密站 / 来源 / 验收 / 需求确认书
├── commands/                 21 个斜杠命令
├── scripts/                  qihang.sh + 2 支结构生成器
└── qihang-scenario-design.html  赛道二设计书
```

---

## 9. 免责

外部 skill 均为公开开源项目（2026-10-01 检索），安装前请读源码与许可证。
`CC-BY-NC` 禁商用；`study-skill`/`math-skill`/`gurukul-ai` 无 LICENSE；
`sickn33/agentic-awesome-skills` 禁止整体安装。DUT 信息库 ⚠️ 条目未经核验。
本包自身 MIT。
