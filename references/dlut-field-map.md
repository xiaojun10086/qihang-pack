# 校内平台 · 字段映射

> 用途：说明各平台能取到哪些字段，以及这些字段归哪个 skill 消费。
> 依据：2026-10-01 实测（`portal.dlut.edu.cn` 首页）；2026-10-06 增补第四节「全校开课查询」（`jxgl.dlut.edu.cn` 实测）。

---

## 一、最佳聚合点：`https://portal.dlut.edu.cn/`

**首页单页即可拿到 6 类数据**，无需逐站登录。

| 区块 | 实测字段 | 消费方 |
|---|---|---|
| 我的课表 | 课程名 + 时间格（周 1–12） | `lecture-to-notes` `exam-sprint` |
| 我的借阅 | 当前借阅册数 | `lit-fetch` `notice-track` |
| 一卡通 | 账户余额、有效期 | `portal-operator` |
| 网络自助 | 网费余额、当月已用 / 剩余流量 | `portal-operator` `notice-track` |
| 我的日程 | 日期、日程条目 | `notice-track` |
| 校内通知 | 通知标题 + 日期 | `notice-track` |
| 我的邮件 | 未读条数 | `portal-operator` |
| 我的数据 / 我的收藏 | 收藏项 | `portal-operator` |

**实测可用入口**（导航栏）：
我的首页 ｜ 事务中心 ｜ 新闻资讯 ｜ 智能广场 ｜ 一网通办 ｜ 学期校历 ｜ 模型广场 ｜ 我的数据 ｜ 我的日程 ｜ 我的收藏

---

## 二、逐站字段（按需深挖时）

| 站点 | URL | 可获取字段 | 消费方 | 备注 |
|---|---|---|---|---|
| 综合教务系统 | `jxgl.dlut.edu.cn` | 课表、考试安排、培养方案、选课结果、成绩 | `course-select` `exam-sprint` `portal-operator` | 成绩明细只在用户明确要求时读取 |
| 全校开课查询（同在教务系统） | `jxgl.dlut.edu.cn` | 本学期全部开课：课程性质、课程类型、开课单位、任课教师、时间地点、选课人数与容量 | `course-select` | 独立标签页；入口 ID 每次不同，不写死；字段见第四节 |
| 图书馆 | `lib.dlut.edu.cn` | 借阅清单、续借、座位 / 研讨间预约 | `lit-fetch` `portal-operator` | — |
| 一卡通 | `ecard.dlut.edu.cn` | 余额 | `portal-operator` | 消费流水走 `ecardv8` |
| 校园门户 | `portal.dlut.edu.cn` | 待办、日程、校内通知、信息专栏 | `notice-track` `portal-operator` | 聚合点 |
| 办事大厅（一网通办） | `ehall.dlut.edu.cn` | 申请、办理进度 | `campus-desk` `portal-operator` | **与门户 SPA 是两个系统** |
| 学生工作系统 | `xsc.dlut.edu.cn` | 资助状态、评奖、请假、第二课堂 | `notice-track` `campus-desk` | 心理记录不读取 |
| 就业信息网 | `job.dlut.edu.cn` | 招聘、宣讲会、投递记录 | `notice-track` | — |
| 研究生系统 | `gs.dlut.edu.cn` | 培养、导师、开题 | `campus-desk` `advisor-finder` | — |
| 数字书院（超星） | `dlutzqsy.mh.chaoxing.com` | 课程资源、作业、测验 | `lecture-to-notes` | — |
| 大工金课平台 | `dlut.fanya.chaoxing.com` | 课程资源 | `lecture-to-notes` | — |
| 雨课堂 | `www.yuketang.cn` | 课件、随堂测验 | `lecture-to-notes` | — |
| 离校系统 | `lx.dlut.edu.cn` | 离校流程 | `dorm-life` | — |
| 统一支付平台 | `pay.dlut.edu.cn` | 缴费状态 | `portal-operator` | 涉金额，操作前先复述 |
| 财务处 | `cw.dlut.edu.cn` | 缴费、报销进度 | `portal-operator` | — |
| 校园邮箱 | `mail.dlut.edu.cn` | 通知、导师往来 | `portal-operator` | 默认不读正文 |
| 网络与信息化中心 | `its.dlut.edu.cn` | 网费、VPN、软件正版化 | `portal-operator` | — |
| i大工 APP | 应用商店 | 场馆 / 心理 / 浴室 / 校车预约 | `portal-operator` `dorm-life` | **仅 APP，无网页版** |

---

## 三、字段 → skill 的消费方式

| skill | 消费哪些字段 | 用途 |
|---|---|---|
| `lecture-to-notes` | `schedule.courses[]` | 按课表归档笔记，标注待补章节 |
| `exam-sprint` | `schedule.courses[]` + 考试安排 | 倒排冲刺计划 |
| `notice-track` | `card.balance` `net.*` `agenda[]` `notices[]` | 事务提醒（欠费 / 借阅逾期 / 待办） |
| `lit-fetch` | `library.on_loan_count` | 提醒还书，避免影响借阅额度 |
| `course-select` | 培养方案 + 选课结果 + 成绩 + 全校开课字段（第四节） | 学分缺口对照、开课清单归类 |
| `dorm-life` | 离校流程节点 | 离校清单 |

---

## 四、全校开课查询（2026-10-06 实测增补）

**入口**：`jxgl.dlut.edu.cn` → 公共服务与查询 → 全校开课查询。落地路径形如 `/student/for-std/lesson-search/index/<入口ID>`，**入口 ID 每次不同，不写死**；点开后**新开一个标签页**，不导航走用户当前页面。

**取数接口**（需登录态）：`/student/for-std/lesson-search/semester/<学期ID>/search/<入口ID>`，参数 `bizTypeAssoc`（`2` 本科 / `3` 研究生）与 `queryPage__=<页号>,<每页条数>`，返回 `data` 数组与 `_page_` 分页元数据。

- `queryPage__` 的页长可放大到 300 以上，一次取完（2026-2027 学年第一学期本科实测 4271 条 / 15 页）。
- **须由已登录页面内发起请求**：登录态不在普通 cookie 里，脱离浏览器直连取不到数据。
- 页面上的筛选下拉是历史分类，与实际数据对不上（按下拉筛常返回空），以返回字段为准，不以下拉选项为准。

| 字段 | 含义 | 备注 |
|---|---|---|
| `course.courseProperty.nameZh` | 课程性质 | 通识类课程 / 全校选修类课程 / 素质课程 / 专业课程等 |
| `courseType.nameZh` | 课程类型 | 教学班级上常为空，须回落 `course.courseType` |
| `course.courseCode` 以 `y` / `z` 结尾 | 网络通识课 | `y` 尔雅（超星学习通）；`z` 东西部联盟（智慧树）；线上学习、不排课 |
| `campus.nameZh` | 校区 | 凌水主校区 / 开发区校区 / 盘锦校区 |
| `openDepartment.nameZh` | 开课单位 | 归类的唯一可用维度 |
| `stdCount` / `limitCount` | 已选人数 / 容量 | `stdCount` 可能略大于 `limitCount` |
| `scheduleText.dateTimePlaceText.textZh` | 上课时间地点 | 未排课时为空 |
| `teacherAssignmentList[].teacher.nameZh` | 任课教师 | — |

**无「人文类」字段**：系统内不存在这一分类，人文类这类清单只能按开课单位 + 课程名人工归类，交付时须声明是人工归类。

**已知缺陷**：课程详情 `/student/for-std/lesson-search/info/<教学班ID>` 实测返回 500，勿依赖。
