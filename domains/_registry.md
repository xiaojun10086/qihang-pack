# 域总表（Level 2 Registry）

> 共 **20 个域 / 92 个库内 skill（每域 4–5 个，其中 12 个改造自 MIT 外部最优解并已 DUT 特化）**

## 锁定规则

1. 1 级库先做**需求明确**（6 槽位 + 澄清门）
2. 用下表**触发词**匹配锁定域；命中多个 → 走跨域串联
3. 无域可命中 → 走 `library/domain-review.md` 的兜底流程

## S · 学习类（6 域）

*课程、课堂、作业、备考、表达、语言*

| 域 ID | 名称 | 触发词 | 库内 skill |
|---|---|---|---|
| `S1` | 课程答疑 | 讲一下、这题、为什么、推导、证明… | `concept-contrast` · `error-diagnose` · `explain-stepwise` · `prereq-bridge` · `socratic-qa` |
| `S2` | 课堂与笔记 | 笔记、讲义、录音、整理、概念图… | `lecture-to-notes` · `link-notes` · `note-normalize` · `reading-note` |
| `S3` | 作业与考核 | 作业、实验报告、课程设计、平时分、大作业… | `assignment-plan` · `code-assignment` · `imrad-scaffold` · `lab-report` · `team-project` |
| `S4` | 备考与记忆 | 考试、复习、背诵、突击、卡组… | `exam-sprint` · `faster-cycle` · `mock-paper` · `open-book-index` · `recall-schedule` |
| `S5` | 学术表达 | 论文、综述、答辩、PPT、引用… | `abstract-tune` · `argument-slides` · `cite-normalize` · `paper-outline` · `thesis-format` |
| `S6` | 语言能力 | 英语、四六级、雅思、托福、口语… | `academic-english` · `ielts-coach` · `lang-drill` · `listening-drill` · `pronounce-drill` |

## F · 生活类（8 域）

*事务、作息、身心、财务、健康、军政、升学、求职*

| 域 ID | 名称 | 触发词 | 库内 skill |
|---|---|---|---|
| `F1` | 校园事务 | 选课、学籍、证明、一卡通、报修… | `campus-desk` · `campus-proof-guide` · `course-select` · `dorm-life` |
| `F2` | 作息与专注 | 拖延、作息、专注、番茄钟、时间管理… | `anti-procrastinate` · `deep-work` · `focus-block` · `sleep-reset` · `task-decompose` |
| `F3` | 身心与社交 | 焦虑、压力、emo、室友、社团… | `adapt-guide` · `club-pick` · `peer-talk-script` · `roommate-mediate` · `wellbeing-checkin` |
| `F4` | 财务与安全 | 生活费、奖学金、助学金、兼职、诈骗… | `aid-apply` · `budget-plan` · `money-guard` · `part-time-guard` |
| `F5` | 健康与运动 | 生病、就医、医保、锻炼、饮食… | `clinic-path` · `fitness-plan` · `health-guide` · `insurance-claim` |
| `F6` | 军训与志愿 | 军训、国防、志愿、社会实践、志愿时长… | `military-prep` · `service-log` · `social-practice` · `volunteer-hours` |
| `F7` | 升学深造 | 保研、考研、留学、申博、导师、推免… | `grad-calendar` · `grad-plan` · `material-kit` · `school-pick` |
| `F8` | 求职与竞赛 | 简历、面试、实习、竞赛、证书… | `career-kit` · `competition-pick` · `intern-search` · `interview-drill` · `resume-tailor` |

## R · 科研类（6 域）

*文献、实验、工具、产出、规范、信息搜集*

| 域 ID | 名称 | 触发词 | 库内 skill |
|---|---|---|---|
| `R1` | 文献检索与管理 | 文献、综述、引用、Zotero、知网… | `citation-verify` · `lit-fetch` · `lit-manage` · `lit-map` · `review-method` |
| `R2` | 实验与数据 | 实验、数据、统计、显著性、图表… | `data-lab` · `exp-design` · `stats-guard` · `stats-workflow` · `viz-spec` |
| `R3` | 科研工具与代码 | Python、MATLAB、仿真、Git、环境… | `code-mentor` · `git-workflow` · `repro-env` · `sim-tool` · `tool-setup` |
| `R4` | 学术产出与投稿 | 投稿、期刊、专利、会议、基金… | `defense-qa` · `grant-apply` · `patent-draft` · `rebuttal-structure` · `submit-kit` |
| `R5` | 学术规范与伦理 | 查重、引用规范、学术诚信、AI 声明、数据合规… | `ai-disclosure` · `ethics-review` · `integrity-check` · `plagiarism-guard` |
| `R6` | 信息搜集与输出 | 导师信息、教师主页、联系方式、通知、公告、信息公开… | `advisor-finder` · `campus-search` · `notice-track` · `org-lookup` |

## 方向自查（覆盖度）

| 检查项 | 结果 |
|---|---|
| 域总数 | 20（S 6 / F 8 / R 6） |
| 库内 skill 覆盖 | **92 个（自建 80 + 外部改造 12，离线零依赖）**；另有**可选外部桥接**（12 平台 + 五步自检） |
| 学习类覆盖 | ✅ 课程/课堂/作业/备考/表达/语言 |
| 生活类覆盖 | ✅ 事务/作息/身心/财务/健康/军政志愿/升学/求职 |
| 科研类覆盖 | ✅ 文献/实验/工具/产出/规范/信息搜集 |
| DUT 绑定 | ✅ 20 域全部标注公开站与私密站点 |


## 触发词消歧

同一词面命中多域时，**按 `O`（对象）+ `T`（任务）判归属**，不默认跨域串联：

| 词面 | 可能误命中 | 正确归属判据 |
|---|---|---|
| **综述** | S5 / R1 | 检索与管理文献 → `R1`；写正文 → `S5`（但只给结构） |
| **引用 / 参考文献** | S5 / R1 / R5 | 检索核验 → `R1`；格式排版 → `S5`；查重诚信 → `R5`。**混合表述（如「引用格式老是标错」）按「主要诉求」判**：要**改格式** → `S5`；要**验真伪** → `R1`；要**降重/规避查重** → `R5`（红线）。**并列双诉求**（如「查重没过，顺便把引用格式也改一遍」）→ 先按 `R5` 给**规范与自查**（红线只禁「代改以规避查重」，给规范**不拦**），再按 `S5` 给格式规范，**两域结论并列输出** —— 不得因其中之一涉红线就整体沉默（对齐 `library/output-spec.md` §2「混合请求」） |
| **实验** | S3 / R2 | 写报告结构 → `S3`；设计与统计 → `R2` |
| **四六级** | S4 / S6 / F1 | **应试突击（背单词/刷题/考前冲刺）→ `S4`**；**语言能力提升 → `S6`**；报名时间与流程 → `F1` |
| **网费 / 学费 / 缴费** | F1 / F4 | **仅问入口 / 流程 → `F1`**；**请求「帮我交 / 帮我付 / 代缴 / 转账」或涉金额与止损 → `F4`**（代操作红线 + 金额属 L3 禁读）。判据：原话出现「帮我交/帮我付/代缴/转账」→ `F4`。**拒绝后的替代分工**：**入口与流程由 `F1` 提供**（`campus-desk`），**止损与红线话术由 `F4` 提供**（`money-guard`） |
| **面试** | F7 / F8 | 升学类（考研复试、保研） → `F7`；求职类 → `F8` |
| **论文** | S5 / R4 | 课程论文 → `S5`；期刊投稿与返修 → `R4` |
| **PPT / 板书** | S2 / S5 | 课堂笔记用途 → `S2`；学术汇报用途 → `S5` |
| **作业题 / 原题** | S1 / S3 | 求讲解 → `S1`；求产出可提交答案 → `S3`（红线） |
| **翻译 / 润色** | S6 / S5 / R4 | 语言学习 → `S6`；论文表达 → `S5`；投稿前 → `R4` |
| **背单词 / 记忆法** | S4 / S6 | 应试备考 / 突击 → `S4`；语言能力长期提升 → `S6`。**与「四六级」行合读：判据是「突击 vs 长期」，不是「四六级 vs 其它」** |
| **「求」类动词** | S1 | 「求推荐/求资源」不是 S1；仅「求解/求证」才属 `S1` |
| **证明** | S1 / F1 | 数学证明、证明某命题 → `S1`；**开具证明**（在学/成绩/党团） → `F1` |
| **失眠 / 睡不着** | F2 / F3 | 想调作息、作息紊乱 → `F2`；**持续失眠 + 情绪/危机信号** → `F3`（并触发危机红线） |
| **预算 / 记账** | F4 / F2 | 钱怎么花 → `F4`；时间怎么安排 → `F2` |
| **导师** | F7 / R6 | **查导师公开资料（是谁/什么方向/怎么联系）→ `R6`**；**选导师策略 / 套磁规划 / 升学时间线 → `F7`**。判据：任务是「查」→ R6，任务是「选/规划」→ F7。常见串联：先 R6 查资料 → 再 F7 定策略 |
| **官网 / 电话 / 通知** | F1 / R6 | **问办理流程（怎么办）→ `F1`**；**问信息本身（是什么/联系方式/在哪查）→ `R6`** |

**红线优先于消歧**：命中 A 域红线时，先按红线拒绝/改锁，再处理域归属。
