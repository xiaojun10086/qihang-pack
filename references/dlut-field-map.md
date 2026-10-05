# 校内平台 · 字段映射

> 用途：说明各平台能取到哪些字段，以及这些字段归哪个 skill 消费。
> 依据：2026-10-01 实测（`portal.dlut.edu.cn` 首页）。

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
| `course-select` | 培养方案 + 选课结果 + 成绩 | 学分缺口对照 |
| `dorm-life` | 离校流程节点 | 离校清单 |
