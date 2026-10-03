# skill 选型矩阵（面向对象：校园主体 → 域 → skill）

> 用途：**决定该造哪些 skill**。选型以「大学校园主体」（人的身份 × 所处阶段）为第一依据，
> 而不是按抽象功能堆砌 —— 同一功能在不同主体下需求强度不同（例：**文献综述**，本科生「够用即可」，
> 研究生要 **PRISMA 系统流程**）。
> 本文件是 v3.1 扩库的**设计基线**；落地后由 `scripts/runcheck.py` 逐域校验。

## 1. 校园主体分类（服务对象）

| 代号 | 主体 | 所处阶段 | 高频诉求 |
|---|---|---|---|
| **N** | 本科新生 | 大一入学适应 | 军训、第一次选课、一卡通、宿舍、社团、想家、高数第一课 |
| **U** | 在读本科生 | 大二–大三 学业主力 | 作业实验、四六级、期中期末、大创竞赛、奖学金、兼职 |
| **G** | 毕业年级本科生 | 大四 出口期 | 保研/考研/留学、秋招实习、毕业设计 |
| **M** | 硕士研究生 | 科研入门 | 导师、文献、实验、组会、投稿、专利 |
| **D** | 博士研究生 | 科研深水 | 基金、高水平论文、答辩、学术伦理 |
| **P** | 学生干部 / 社团负责人 | 组织者 | 活动策划、志愿时长、社会实践立项 |
| **T** | 教师 / 导师 | 被查对象 + 科研主体 | 公开资料被检索、基金申报、指导研究生 |
| **S** | 行政 / 教务人员 | 流程另一侧 | 办事流程、证明开具、信息公开 |

> **面向对象的含义**：skill 的「覆盖主体」必须明确。同一域内，**主体不同 → 选不同 skill**
> （如 S2：本科生用课堂笔记 skill，研究生用文献精读 skill）。
> 选型时不看「功能名像不像」，看「**这个主体在这个阶段会不会真的遇到它**」。

## 2. 主体 × 域 → skill 选型矩阵

| 域 | 主服务主体 | 现有 skill | 拟补 skill（面向主体） | 补后 |
|---|---|---|---|---|
| **S1** 课程答疑 | N U | explain-stepwise · error-diagnose · socratic-qa | `prereq-bridge` 先修补桥（**N**：卡点在前置知识）· `concept-contrast` 易混辨析（**U**：考前辨析） | 5 |
| **S2** 课堂与笔记 | U M | lecture-to-notes · note-normalize · link-notes | `reading-note` 精读笔记（**M**：论文/专著三色标记法） | 4 |
| **S3** 作业与考核 | U | lab-report · assignment-plan · imrad-scaffold | `code-assignment` 编程作业自查（**U** 工科：不代写代码）· `team-project` 小组作业协作（**U**：分工与进度） | 5 |
| **S4** 备考与记忆 | U | exam-sprint · recall-schedule · faster-cycle | `mock-paper` 模拟卷与错题回炉（**U**）· `open-book-index` 开卷索引页（**U**） | 5 |
| **S5** 学术表达 | U G M | paper-outline · cite-normalize · argument-slides | `thesis-format` 学位论文格式自检（**G M**）· `abstract-tune` 摘要打磨（**M**） | 5 |
| **S6** 语言能力 | U M | lang-drill · pronounce-drill · ielts-coach | `academic-english` 学术英语（**M**：论文句式/时态）· `listening-drill` 精听训练（**U**） | 5 |
| **F1** 校园事务 | N U | campus-desk · campus-proof-guide | `course-select` 选课与培养方案核对（**N U**）· `dorm-life` 公寓与离校（**N U**） | 4 |
| **F2** 作息与专注 | N U | focus-block · task-decompose · deep-work | `sleep-reset` 作息重置（**N U**：熬夜后回调）· `anti-procrastinate` 拖延干预（**U**） | 5 |
| **F3** 身心与社交 | N U | wellbeing-checkin · peer-talk-script | `adapt-guide` 新生适应（**N**：想家/落差）· `roommate-mediate` 宿舍沟通（**N U**）· `club-pick` 社团选择（**N**） | 5 |
| **F4** 财务与安全 | U | money-guard · budget-plan | `aid-apply` 奖助勤工申请（**U**：条件核对/材料/时间线）· `part-time-guard` 兼职避坑（**U**：押金/合同） | 4 |
| **F5** 健康与运动 | U | health-guide · clinic-path | `insurance-claim` 医保报销（**U**：门诊/住院/异地）· `fitness-plan` 锻炼与体测（**U**：结合校园场馆） | 4 |
| **F6** 军训与志愿 | N U P | service-log · volunteer-hours | `military-prep` 军训准备（**N**：体能/物品/防晒）· `social-practice` 社会实践立项（**P**：选题/立项/报告） | 4 |
| **F7** 升学深造 | G | grad-plan · grad-calendar | `school-pick` 选校与夏令营（**G**：梯度策略/投递）· `material-kit` 升学材料结构（**G**：不代写） | 4 |
| **F8** 求职与竞赛 | G U | career-kit · competition-pick · resume-tailor | `interview-drill` 面试演练（**G**：STAR 结构）· `intern-search` 实习搜寻（**G**：渠道/时间线） | 5 |
| **R1** 文献检索与管理 | M D | lit-map · citation-verify · lit-fetch | `review-method` 系统综述（**M D**：PRISMA）· `lit-manage` 文献库管理（**M**：Zotero 结构） | 5 |
| **R2** 实验与数据 | U M | data-lab · stats-guard · stats-workflow | `exp-design` 实验设计（**M**：对照/变量/样本量）· `viz-spec` 图表规范（**M**：期刊要求） | 5 |
| **R3** 科研工具与代码 | U M | tool-setup · repro-env · code-mentor | `git-workflow` 科研 Git 协作（**M**：分支/冲突）· `sim-tool` 仿真工具上手（**U M**：MATLAB/COMSOL） | 5 |
| **R4** 学术产出与投稿 | M D T | submit-kit · rebuttal-structure · defense-qa | `patent-draft` 专利交底书（**M D**）· `grant-apply` 基金申报（**D T**） | 5 |
| **R5** 学术规范与伦理 | G M D | integrity-check · ai-disclosure | `plagiarism-guard` 查重前自检（**G M**：只给方法不代降重）· `ethics-review` 伦理审查（**M D**：知情同意/数据合规） | 4 |
| **R6** 信息搜集与输出 | 全体 | advisor-finder · campus-search | `notice-track` 通知公告追踪（**全体**：报名/考试/评奖节点）· `org-lookup` 机构场馆查询（**全体**：部门职能/办事地点） | 4 |

**规模**：52 → **92**（新增 40；每域 4–5 个）。
**分布**：S 类 29 · F 类 35 · R 类 28。

## 3. 「需求没命中任何 skill」时的兜底（必须得出有效结果）

现状缺口：`library/domain-review.md` 写了「给该域的**通用框架**」「降级为**通用问答**」，
但**包里并不存在这个框架** —— 指向悬空。v3.1 补齐：

| 情形 | 兜底路径 | 产出保证 |
|---|---|---|
| 命中域 + 有对口 skill | 直接用（库内优先） | 标准输出 |
| 命中域 + **无**对口 skill | ① 同域另一 skill 降级（降级目标在 skill 内已指名）→ ② 该域**通用框架** | 输出首行标 `[已降级: 原 → 备]` + 记缺口 |
| **命中 0 个域** | 六步通用框架（`library/general-fallback.md`） | **必给**：复述 + 拆解 + 分层建议 + 不确定性标注 + 1 个下一步 + 缺口记录 |
| 极模糊（身心两可等） | 先按安全兜底**反问 1 问** | 不得直接判域作答 |

**六步通用框架**（任何输入都能跑出有效结果）：

1. **复述**：用自己的话复述需求，标注理解偏差风险
2. **拆解**：拆成 2–4 个可独立回应的子问题
3. **分别回应**：每个子问题给「能做/不能做 + 怎么做/get 哪个入口」
4. **标注不确定**：凡未经核验的信息标 ⚠️，不臆造 URL/电话/人名
5. **给下一步**：恰好 1 个可执行动作（去哪个站/问谁/做什么）
6. **记缺口**：写入学习档案，作为后续扩库依据

> 保证：**即使零 skill 命中，也产出一份结构完整、可执行、标注了不确定性的答复**，
> 而不是「本包没有这个」一句话了事。

## 4. 优化基线（现有 52 个 skill 已一并执行：方法库 + 第二示例 + DUT 特化加深）

| 项 | 要求 |
|---|---|
| **第二示例** | 每个 skill 补一个**边界/失败例**（不该命中的情形 + 降级路径），让红线可测 |
| **方法库/判定细则** | 把 6 步通用流程背后的真细则写入（如 S1 三类卡点各怎么处理、R2 统计前提检查清单） |
| **改造 skill 的 DUT 特化** | 10 个 MIT 改造 skill 中仍偏通用的表述，换成大工具体站点/流程/场景 |
| **清理空话** | 删除「依据」栏自我指涉（如「XXX 流程（库内 skill）」），换成真实依据 |
| **来源标注** | 每个 skill 的「来源」行必须存在且与 `THIRD_PARTY_NOTICES.md` 一致（现有 2 个缺失） |
