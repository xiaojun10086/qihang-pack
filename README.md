# 「启航」新生学习生活一体化学伴包 v3.4

> **默认先满足学生高频任务：学习 + 公开信息搜集；其余生活与科研专域作为可选扩展。**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：**LearnBuddy（= 连小理）**（单一目标平台）
> 定位：**DUT 特化规则与 skill 库（库内优先）** —— 文本资产离线可读；技能实际执行依赖宿主平台的模型与工具；
> 库内与同域降级都接不住时，可走**可选的外部桥接**（平台目录当前列出 20 个入口 + 五步自检，见 `library/external-bridge.md`），**外部未命中即回落原有流程**

---

## 0. 下载与快速开始

| 方式 | 一步到位 |
|---|---|
| **下载交付包（推荐）** | [`release` 分支 ZIP](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/release.zip ) |
| 在线浏览 | [github.com/xiaojun10086/qihang-pack/tree/release](https://github.com/xiaojun10086/qihang-pack/tree/release ) |
| 命令行安装 | `git clone -b release https://github.com/xiaojun10086/qihang-pack.git` |

> **`release` 分支 = 纯净交付树**（176 个文件）：只含运行所需内容 —— 无构建脚本、无内部过程文档、无本机路径。
> 下载后把目录放到 `~/.learnbuddy/skills/qihang`（用户级）或当前工作区 `.learnbuddy/skills/qihang`（项目级）即可使用，
> **无需安装任何依赖**（私密站只读为可选功能，见 `INSTALL.md` §六）。
> 开发树（含生成器链与过程文档）在 [`main` 分支](https://github.com/xiaojun10086/qihang-pack )。

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── LICENSE                     MIT 许可证全文
├── THIRD_PARTY_NOTICES.md      skill 来源说明与许可证归属（10 个 MIT 来源 + 2 项零摘录思路参考）
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── library/                  ★1 级 · skill 库（既是 skill 也是库）
│   ├── README.md             库导航页（非安装入口，无 frontmatter）
│   ├── login-policy.md       登录选择原则（A/B/C 三档）
│   ├── clarity.md            职责1：需求明确（6 槽位 + 澄清门）
│   ├── domain-review.md      职责2：域审查（锁定/越界/跨域/无域兜底）
│   ├── output-spec.md        职责3：输出规范（模板 + 简略原则）
│   └── general-fallback.md   职责4：通用兜底框架（零 skill 命中也出结果）
├── domains/                  ★2 级 · 域（20 个）
│   ├── _registry.md          域总表 + 方向自查 + 触发词消歧
│   └── <域ID>-<slug>/
│       ├── _domain.md        域定义：边界 / 触发词 / DUT 绑定点
│       └── skills/
│           └── local/<name>/SKILL.md    ★3 级 · 库内 skill（唯一通道，无需安装）
├── references/                  数据与依据
│   ├── dlut-official-sites.md      DUT 公开站信息库（142 条条目 / 表格行 162）
│   ├── dlut-login-sites.md         DUT 私密站清单（方案 A + Profile 隔离）
│   ├── dlut-field-map.md           私密站字段映射表
│   ├── dlut-url-verification.md    URL 核验台账（16 项待人工补）
│   ├── dlut-site-profiles.md       18 站画像
│   ├── browser-matrix.md           浏览器实测矩阵
│   ├── skill-compliance-audit.md   库内 skill 来源合规自检报告
│   ├── skill-selection-matrix.md   skill 选型矩阵（校园主体 → 域 → skill）
│   ├── external-sources.md         外部平台入口清单（20 个入口 + 检索规则）
│   ├── platforms.md                平台适配表
│   └── e2e-scenarios.md            3 条端到端演示路径
├── commands/                    22 张入口卡（含学习/信息搜集默认入口与各可选域卡）
└── scripts/
    ├── selfcheck.sh             结构与计数自检
    ├── audit.sh                 安全审计 + L3 门禁实测
    ├── regress.sh               行为回归（澄清门算例 / 门禁矩阵）
    ├── aligncheck.py            全量文件级对齐审计（18 组断言）
    ├── runcheck.py              结构 / 示例 / 输出契约静态检查（不调用模型或目标平台）
    ├── extskill.py              外部 skill 桥接静态自检（来源与许可门禁）
    ├── negative_test.py         负向自测（注入缺陷，断言必须 FAIL）
    ├── checkall.py              自检单入口（固定顺序 + 逐项计时 + 摘要）
    ├── metrics.py               指标埋点口径与发布门禁（唯一真相源）
    ├── dlut-read.sh             DUT 私密站只读访问辅助（方案 A 受控浏览器）
    └── qihang.sh                管理脚本
```

## 2. 默认工作流（核心快路径）

```
用户需求
  ↓ 直接描述目标，不用先选 skill / domain
  ↓ 自动分析任务并路由到最合适的能力
  ↓ 只在关键信息会改变回答时追问
  ↓ 学习任务直接辅导；事实检索给来源、日期与核验状态
```

### 2.1 第一阶段体验增强（产品化改进）

这个版本优先解决“用户不需要懂内部结构”的体验问题。第一阶段的核心改进包括：

- 统一快速上手入口与自然语言模板：不要求用户先理解 `S1/S2/R6` 等域编号
- 统一快速模板：用户直接输入自然语言即可启动
- 最小必要追问：只在关键信息会改变答案时追问，且先说明为什么需要
- 后台规则收敛：触发门、红线、安全边界保留，但在前台不暴露为复杂流程
- 结果输出统一：结论、依据、来源、下一步，减少使用者理解成本
- `bash scripts/qihang.sh quick` 展示自然语言示例；它只是帮助菜单，不会启动对话或代替宿主执行任务

**可直接使用的起始句型**：

- 「帮我理解这道题，告诉我关键思路」
- 「这节课我听不懂，帮我整理重点和笔记」
- 「我有作业，先拆任务，再给我检查点」
- 「给我做一个一周备考计划」
- 「查一下大工公开通知/课程安排，给出处和核验状态」

**默认核心域**：S1–S6 学习 + R6 学生公开信息搜集。R1 文献检索为专项扩展；F1–F8 与 R2–R5 保留为可选扩展，只有相关任务出现时才路由。普通请求不强制走 8 步工作流、外部 skill 搜索、固定输出模板、自动归档或自迭代。实时信息依赖宿主提供的搜索工具；没有工具时会明确说明无法实时核验。

### 2.2 第二、三阶段（宿主内的体验增强）

- **自动路由**：按主要目标选择学习、检索或行动交付；歧义会实质改变结果时才澄清。
- **会话连续性**：在当前对话内沿用用户已给出的目标、约束与进度；跨会话读取或保存仍须用户明确要求并遵守隐私规则。
- **交付模式**：学习辅导、带来源的信息检索、可执行的计划/检查点按任务自动选择，不要求用户先选模式。
- **反馈闭环**：用户可要求更简洁、更详细、核对来源或指出错误；默认只在当前对话修订，不收集原话、不自动持久化评价。
- **可编辑结构化内容**：按需输出表格、清单、时间线或概念层级，便于复制和继续修改。

以上能力由宿主对话与文本资产承载；本仓库不是独立 Web 应用，不提供图形界面、自动跨会话数据库或真实图像渲染。

**个人配置默认留空**：`config.yaml` 中校区、学院、年级、学期、课程、考试周和作息均未预设。`null` / 空列表表示未知；不得据此推断用户身份或经历。用户可自行确认后填写，任务无关时不追问。

## 3. 完整域库（核心 + 可选扩展）

| 大类 | 域 |
|---|---|
| **核心：S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **核心：R6 信息搜集** | 学校/课程/通知/机构等公开资料，优先官方来源并标注时效 |
| **专项扩展：R 科研（R1–R5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 |

**完整资产规模**：20 个域、92 个库内 skill。默认聚焦 7 个核心域（S1–S6、R6）；13 个生活与专项科研域保持可选。来源口径为 **80 个自建 + 12 个有来源记录**；其中 10 个基于 MIT 许可项目骨架重写，另 2 个仅参考方法论、零内容摘录。细目见 `THIRD_PARTY_NOTICES.md`。

> 92 个 skill 是提示词与流程资产的数量，不代表 92 项能力都经过目标平台实测。当前 `runcheck.py` 只做结构、示例和输出契约检查，不调用模型或 LearnBuddy。建议按高频、低风险场景分阶段验证后再扩大对外承诺。

## 4. 安装与使用

```bash
# 1) 放进 skills 目录
cp -r qihang-pack ~/.learnbuddy/skills/qihang
# 2) LearnBuddy 无需斜杠命令：22 张 commands/ 域入口卡随包提供，直接读即可
# 3) 查看状态（库内 skill 开箱即用，无任何外部依赖）
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

```bash
bash scripts/selfcheck.sh         # 结构与计数自检
bash scripts/audit.sh             # 安全审计 + L3 门禁实测
bash scripts/regress.sh 3         # 行为回归（连跑 3 轮验证确定性）
python scripts/aligncheck.py . 5  # 全量对齐审计（连跑 5 轮）
python scripts/runcheck.py . 3    # 静态契约检查（连跑 3 轮，非模型端到端测试）
python scripts/checkall.py .       # 自检单入口（静态校验器 + 计时摘要）
bash scripts/qihang.sh quick      # 快速入口（自然语言起始句型示例）
bash scripts/qihang.sh status     # 三级结构完整度
bash scripts/qihang.sh domains    # 20 域清单
bash scripts/qihang.sh registry   # DUT 信息库统计
bash scripts/qihang.sh new-term   # 换学期重置
```

## 5. DUT 融入

| 类型 | 文件 | 融入方式 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | **142 条**条目（表格行 162），20 个域的 `_domain.md` 各自标注绑定点 |
| 私密站 | `references/dlut-login-sites.md` | 19 个需登录站点，**方案 A 受控浏览器 + 只读**，分 L1/L2/L3 授权 |
| 校内信息搜集 | `domains/R6-info-retrieval/` | 导师/教师公开资料（`faculty.dlut.edu.cn`、`gs.dlut.edu.cn`）+ 公开信息检索与路由 |

**私密站安全边界**：访问脚本只打开用户可见的本机浏览器，不采集或输出网页内容；使用随机会话和一次性 Profile，退出后清理，不关闭用户的其他浏览器会话。用户自行查看页面，并可选择只分享回答必需的信息。L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | 在 `domains/` 下新增 `<域ID>-<slug>/` 目录，并在 `domains/_registry.md` 登记 | 1 个目录 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 本包为 **DUT 特化规则与 skill 库**：核心文本资产离线可读；实际执行依赖宿主平台的模型和工具能力，外部桥接为**可选增强**。
- 来源口径为 80 个自建 skill 与 12 个有来源记录的 skill（其中 10 个基于 MIT 项目重写、2 个仅参考方法论且零内容摘录）；详见 `THIRD_PARTY_NOTICES.md`。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。

## 8. 版本记录

| 版本 | 修订号 | 主要变更 |
|---|---|---|
| **v3.4** | `3.4.0` | **第一阶段体验增强**：新增 `bash scripts/qihang.sh quick` 统一快速入口与自然语言起始句型；入口与 README 增补「第一阶段体验增强」「第二、三阶段体验能力」两节（自然语言入口、软件感知原则、三种交付方式、会话连续性、反馈闭环）；`library/memory.md` 增补「当前会话的连续性」口径 —— 沿用当前会话上下文不等于写入档案，跨会话读取或保存仍须用户明确要求。 |
| v3.3 | `3.3.0` – `3.3.9` | 外部 skill 桥接（降级链两档 → 三档）、外部来源清单扩充与适配判据可执行化、触发门词表同源与域锁定加固、移除强制自我身份声明。 |

> **版本口径**：**包版本 = 两位**（`3.4`，用于包名与展示位）｜**修订号 = 三位**（`3.4.0`，用于 frontmatter / `plugin.json` / 校验断言）。两者同一条线，修订号前两位即包版本。
> 本表只记录**交付给使用者的版本线**；生成链的逐层变更记录见 `scripts/_build/v3/README.md`（开发侧文档，不随包交付）。
