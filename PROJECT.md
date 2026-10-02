# 「启航」学伴包 · 项目文档

> 版本 v2.10 ｜ 更新 2026-10-02 ｜ 面向大连理工大学 2026 级本科新生  
> 适配：**LearnBuddy（= 连小理）**（单一目标平台）

---

## 1. 一句话定位

把「新生一句模糊求助」变成「结构化可执行方案」的**可插拔 skill 包**；  
**三级结构：skill 库 → 域 → skill**，并强绑定大工的公开站与需登录的私密站。

---

## 2. 三级结构

```
【1级】library/        skill 库（既是 skill 也是库）
       只做四件事：①需求明确 ②域审查 ③输出规范 ④记忆归档，不承载具体业务
        ↓
【2级】domains/        19 个域，覆盖 学习 / 生活 / 科研
        ↓
【3级】skills/         local/  库内 skill（优先，无需安装）
                       external.md  库外候选（库内不满足才装）
```

| 级别  | 允许做                           | 禁止做         |
| --- | ----------------------------- | ----------- |
| 1 级 | 需求明确、域审查、输出规范、记忆归档          | 承载学科知识、写死业务 |
| 2 级 | 定义边界与触发词、列域内 skill、声明 DUT 绑定点 | 直接回答问题      |
| 3 级 | 执行具体任务                        | 跳过澄清门       |

---

## 3. 工作流（严格按序，不可跳步）

```
用户需求
  ↓ ① 需求明确   library/clarity.md          6 槽位 + 澄清门，U ≤ 0.30 才继续
  ↓ ② 锁定域     domains/_registry.md         触发词匹配
  ↓ ③ 域审查     library/domain-review.md     边界复核，越界改锁
  ↓ ④ 锁定 skill domains/<域>/_domain.md      读该域的库内 skill
  ↓ ⑤ 库内优先   skills/local/                命中即调用，无需安装
  ↓ ⑥ 库外兜底   skills/external.md           仅库内不满足才安装
  ↓ ⑦ 输出       library/output-spec.md       ≤6 条要点
  ↓ ⑧ 归档       library/memory.md            写学习档案（F3/F5 敏感域除外）
```

**澄清门**：`U = 1 − Σ(wᵢcᵢ)/Σwᵢ`；`U > 0.30` 追问，最多 3 轮、每轮 ≤3 问，  
优先级 `时间 > 对象 > 产出 > 约束 > 背景 > 任务`；3 轮后按假设执行并显式标注。

**核心规则：库内优先** —— 库内有就不装库外，规避低星 / 无许可证 / 需 API Key 的第三方风险。

---

## 4. 19 个域

| 大类          | 域                                                                                   |
| ----------- | ----------------------------------------------------------------------------------- |
| **S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力                        |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **R 科研（5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理                        |

每域含：`_domain.md`（边界/触发词/DUT绑定点）+ `skills/local/`（**2 个**库内 skill）+ `skills/external.md`。  
**方向空白域 4 个**（F3 / F4 / F5 / F6）—— 库外无任何候选；另有 F1 / F7 / R5 虽有候选但均**不达门禁**。二者合计 **7 个域最终纯自建**。

---

## 5. DUT 融入

| 类型       | 文件                                     | 内容                                                    |
| -------- | -------------------------------------- | ----------------------------------------------------- |
| 公开站      | `references/dlut-official-sites.md`    | **159 条**表格行 / **139 条**条目（✅ 67 / ⚠️ 21），三校区 + 全部学院 + 职能部门 |
| 私密站      | `references/dlut-login-sites.md`       | **19 个**需登录站 + 方案 A 流程 + L1/L2/L3 授权 + Profile 隔离要求   |
| Skill 来源 | `references/skill-sources.md`          | 12 个探测平台                                              |
| **合规自检** | `references/skill-compliance-audit.md` | 合法性（MIT/GPL/CC-BY-NC/无 LICENSE 四档）+ 可用性逐项             |
| 验收       | `references/validation-report.md`      | 4 路并行子 agent 的测试结论                                    |

**三大入口**：`sso.dlut.edu.cn` → `portal.dlut.edu.cn` → `jxgl.dlut.edu.cn`

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。  
L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**禁止读取**。  
**Profile 必须隔离**：`--profile "$HOME/.qihang/browser-profile"`（实测踩坑，见下）。

**已实测（2026-10-01）**：`portal.dlut.edu.cn` 首页单页即可拿到 6 类 L1 数据  
（课表 / 借阅 / 一卡通 / 网费 / 邮件未读 / 日程通知），是**全包最佳聚合点**。

---

## 6. 安装与使用

**LearnBuddy / WorkBuddy（推荐）** —— 自然语言即可，无需斜杠命令：

```bash
cp -r qihang-pack ~/.learnbuddy/skills/qihang
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```


| 命令 / 入口                                                                               | 作用                      |
| ------------------------------------------------------------------------------------- | ----------------------- |
| `commands/qihang.md` | 库入口卡（澄清门 → 锁域 → 锁 skill） |
| `commands/qihang-dlut.md` | 校情入口卡（公开站 + 私密站） |
| `commands/qihang-s1.md` … `commands/qihang-r5.md` | 19 个域入口卡 |
| `qihang.sh status \| platform \| domains \| records \| probe \| registry \| new-term` | 管理脚本                    |

完整安装说明见 `INSTALL.md`；平台适配见 `references/platforms.md`。

## 6.1 平台适配

| 项 | 内容 |
|---|---|
| **目标平台** | **LearnBuddy / WorkBuddy**（唯一适配目标，一等公民） |
| 安装位置 | `~/.learnbuddy/skills/qihang/`（项目级：`{ws}/.learnbuddy/skills/qihang/`） |
| 入口 | **自然语言**（无需斜杠命令）；`commands/` 21 张域入口卡供人工检索 |
| 记忆系统 | `~/.learnbuddy/MEMORY.md` + `{ws}/.learnbuddy/memory/` + 本包按域档案 |
| 插件清单 | `.codebuddy-plugin/plugin.json` |
| **连小理**（= LearnBuddy） | 同一平台（赛道二场景名），非独立适配 |

> 其他 agent 只要能读 `SKILL.md` 即可装载，但**本包不提供适配承诺**。

---

## 7. 当前状态（v2.10.0）

| 项                  | 状态                                                                                                                           |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| 三级结构               | ✅ 完成（生成器驱动 · 19 域 / **38 库内 skill** / **162 个文件**）                                                                                                            |
| 19 域 + **38 库内 skill** | ✅ **已产品化**：**每域 2 个**、均含可执行示例；4 空白域含安全护栏                                                                                               |
| 越界用例集 / 输出校验清单     | ✅ **22 条**用例（含 3 反例）· **7 项**硬校验                                                                                                     |
| DUT 公开信息库          | ✅ **159 条**表格行 / **139 条**条目（✅ 67 / ⚠️ 21）                                                                                                                      |
| DUT 私密站清单          | ✅ **19 站** + 方案 A + L1/L2/L3                                                                                                                |
| 方案 A 实机验证          | ✅ 通过（含 Profile 隔离修正）                                                                                                         |
| **DUT 取数固化**       | ✅ `dlut-read.sh`（L1 直读 / L2 需确认 / L3 拒绝）+ `dlut-field-map.md` 字段映射表                                                    |
| 库外 skill 联调        | ✅ 安装通道实测可用（`npx skills add`）；合规自检完成；**12 平台多源比对 v3**（`references/skill-matrix-v3.md`） |
| **平台适配** | ✅ **LearnBuddy / WorkBuddy 单一目标平台**（`~/.learnbuddy/skills/` + `.codebuddy-plugin/`）；v2.8 起移除 Claude Code 适配 |
| 学习档案（跨会话记忆）        | ✅ 规则与工具就绪（`library/memory.md` + `qihang.sh records`）；跨会话实跑待验                                                                 |
| 赛道二提交物             | ✅ 设计书已对齐当前结构（19 域三级结构）                                                                                                      |
| **端到端验收**          | ✅ `e2e-scenarios.md` 3 条路径 + `acceptance-v2.md`（15 项通过 14 项）                                                              |

---

## 8. 目录一览

```
qihang-pack/
├── SKILL.md                  入口
├── INSTALL.md                安装指南（LearnBuddy）
├── PROJECT.md                本文件
├── ROADMAP.md                分阶段开发计划
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── .codebuddy-plugin/        LearnBuddy / WorkBuddy 插件清单
├── library/                  1级 skill 库
│   ├── SKILL.md  clarity.md  domain-review.md  output-spec.md  memory.md
│   ├── domain-review-cases.md   越界用例集（22 条）
│   └── output-checklist.md      输出 7 项硬校验
├── domains/                  2级 19 个域
│   └── <ID>-<slug>/{_domain.md, skills/{local/, external.md}}
├── references/
│   ├── dlut-official-sites.md     公开站 139 条条目   ├── dlut-login-sites.md   私密站 19 站
│   ├── dlut-field-map.md          字段映射表       ├── dlut-url-verification.md  URL 核验
│   ├── dlut-site-profiles.md      站点画像         ├── browser-matrix.md     浏览器矩阵
│   ├── skill-sources.md           12 个探测平台     ├── skill-matrix-v3.md    库外比对矩阵
│   ├── skill-compliance-audit.md  合规自检         ├── platforms.md          平台适配表
│   ├── e2e-scenarios.md           3 条端到端演示   ├── acceptance-v2.md      验收报告 v2
│   ├── validation-report.md       阶段 1/2 验收    ├── alignment-audit-v3.md 全量对齐复核
│   ├── review-report-v2.2.md      复查报告 v2.2    ├── review-report-v2.3.md  复查报告 v2.3
│   ├── review-report-v2.4.md      复查报告 v2.4    ├── stress-test-v3.md      多轮压测
│   └── 需求确认书-v2三级结构.md
├── commands/                 21 张 LearnBuddy 域入口卡（库 + 校情 + 19 域）
├── scripts/
│   ├── qihang.sh             管理脚本（平台探测 / 状态 / 档案 / 信息库统计）
│   ├── dlut-read.sh          DUT 私密站只读取数（L1/L2/L3 硬拦截）
│   ├── selfcheck.sh          结构自检    ├── audit.sh       安全审计
│   ├── regress.sh            行为回归    ├── aligncheck.py  全量对齐审计
│   └── _build/build_*.py     结构生成器（改域后按序重跑）
└── qihang-scenario-design.html  赛道二设计书
```



---

## 9. 免责

外部 skill 均为公开开源项目（2026-10-01 检索），安装前请读源码与许可证。  
`CC-BY-NC` 禁商用；`study-skill`/`math-skill`/`gurukul-ai` 无 LICENSE；  
`sickn33/agentic-awesome-skills` 禁止整体安装。DUT 信息库 ⚠️ 条目未经核验。  
本包自身 MIT。
