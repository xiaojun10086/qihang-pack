# 大连理工大学 需登录站点清单

> 配套 `dlut-official-sites.md`（公开站）使用。
> 使用方式：用户明确授权后，由 `portal-operator` skill 打开目标站点并代为执行操作。
> 登录动作由用户本人完成或使用用户已授权的会话；凭证不写入任何文件。

**入口**：统一身份认证 https://sso.dlut.edu.cn/ —— 多数系统的前置登录。

**WebVPN 注意**：https://webvpn.dlut.edu.cn/login 有 Referer 校验，手拼 URL 会报「不正确的 HTTP Referer」，只能从 WebVPN 门户点资源卡进入。WebVPN 登录态 ≈ 校外可达全校内网，只在用户明确要求校外访问时使用。

---

## 1. 核心站点

| # | 站点 | URL | 可获取 | 备注 |
|---|---|---|---|---|
| 1 | 统一身份认证 | https://sso.dlut.edu.cn/ | 单点登录入口 | 其他站点的前置登录 |
| 2 | 校园门户 | https://portal.dlut.edu.cn/ | 待办、日程、通知、信息专栏 | 最佳聚合点，首页单页可拿多类数据 |
| 3 | 综合教务系统 | http://jxgl.dlut.edu.cn/student/ucas-sso/login | 课表、成绩、选课、考试安排、培养方案完成情况、全校开课查询 | 高频；**仅 HTTP**；页面路径与字段见 `dlut-field-map.md` 第四～七节 |
| 4 | 图书馆 | https://lib.dlut.edu.cn/ | 借阅、续借、座位/研讨间预约 | — |
| 5 | 一卡通 / 玉兰卡 | https://ecard.dlut.edu.cn/ | 余额 | 卡内充值入口 https://ecard.dlut.edu.cn/info/1013/1139.htm （「一卡通充值说明」，2024-08-31 发布，正文为图片、无文字步骤，细则须人工核对）；消费流水见 #38 |
| 6 | 学生工作系统 | https://xsc.dlut.edu.cn/ | 资助、评奖、请假、第二课堂 | 心理记录不读取 |
| 7 | 统一支付平台 | http://pay.dlut.edu.cn/ | 缴费状态 | 涉金额，操作前先复述 |
| 8 | 财务处 | http://cw.dlut.edu.cn/ | 缴费、报销进度 | 个人数据需登录 |
| 9 | 就业信息网 | https://job.dlut.edu.cn/ | 招聘、宣讲会、投递记录 | — |
| 10 | 研究生系统 | https://gs.dlut.edu.cn/ | 培养、导师、开题 | — |
| 11 | 研究生招生报名 | https://yjszs.dlut.edu.cn/zsbm | 报名状态 | — |
| 12 | 校园邮箱 | https://mail.dlut.edu.cn/ | 通知、导师往来 | 默认不读正文 |
| 13 | 数字书院（超星） | https://dlutzqsy.mh.chaoxing.com/ | 课程资源、作业、测验 | — |
| 14 | 大工金课平台 | https://dlut.fanya.chaoxing.com/ | 课程资源 | — |
| 15 | 雨课堂 | https://www.yuketang.cn/ | 课件、随堂测验 | 非 DUT 域 |
| 16 | 离校系统 | http://lx.dlut.edu.cn/ | 离校流程 | **仅 HTTP** |
| 17 | 网络与信息化中心 | https://its.dlut.edu.cn/ | 网费、VPN、软件正版化 | — |
| 18 | 校园网自助服务 | http://tulip.dlut.edu.cn/ | 网费自助、流量查询 | **仅 HTTP** |
| 19 | i大工 APP | 应用商店 | 场馆 / 心理 / 浴室 / 校车预约 | 场馆 / 浴室 / 校车**无网页版**；心理另有网页入口（见 #29）。均需用户本人操作 |

## 2. 补充站点

> 2026-10-04 实测。「实测」列为本机出网直连结果；`302 → 统一身份认证` 表示未登录时重定向到 SSO。

| # | 站点 | URL | 可获取 | 实测 |
|---|---|---|---|---|
| 20 | WebVPN | https://webvpn.dlut.edu.cn/login | 37 项校内资源代理；校外访问校内系统的唯一正门 | 200 |
| 21 | 智慧学工 | http://dutxg.dlut.edu.cn/ | 学工应用（29 项）、我的主页、自助打印 | 200 |
| 22 | 学工系统 | http://dutsa.dlut.edu.cn/cas/account/index | 学工业务办理（**与智慧学工是两个系统**） | 302 → SSO |
| 23 | 研究生管理信息系统 | https://dutgs.dlut.edu.cn/pyxx/LoginCAS.aspx?a=1 | 培养、选课、成绩、开题 | 302 → SSO |
| 24 | 一网通办 | https://workflow.dlut.edu.cn/ | 待办、待阅、办事流程 | 200 |
| 25 | 一张表平台（我的数据） | https://data.dlut.edu.cn/ep | 个人数据汇总（门户「我的数据」） | 302 → SSO |
| 26 | 大工云盘 | http://pan.dlut.edu.cn/cas | 文件存储与共享 | 302 → SSO |
| 27 | 自助打印服务平台 | http://eproof.dlut.edu.cn/sso/login.jsp | 成绩单、在读证明自助打印 | 302 → SSO |
| 28 | 迎新系统 | https://dutyx.dlut.edu.cn/yxwz/ | 迎新流程（新生入学） | 200 |
| 29 | 心理服务 | http://xinlixlt.dlut.edu.cn/xlogin/cas | 心理咨询预约 | 302；只给入口，不读取预约内容 |
| 30 | 组织工作一体化平台 | https://zzgz.dlut.edu.cn/cas | 党务、党员发展 | 302 → SSO |
| 31 | 数字党校培训平台 | http://szdx.dlut.edu.cn | 党课学习与考试 | 200 |
| 32 | 图书馆系统（OPAC） | https://opac.lib.dlut.edu.cn/meta-local/opac/cas/rosetta | 馆藏、借阅、续借 | 302 → SSO |
| 33 | 图书馆座位 / 研讨间预约 | https://smart.lib.dlut.edu.cn/caslogin/ | 座位、研讨间预约 | 302 → SSO |
| 34 | 科技查新 / 查收查引 | https://tns.lib.dlut.edu.cn/kycgfwptweb/home | 查收查引委托、论文收录证明 | 200 |
| 35 | 智能广场（校内 AI 助手） | http://chat.dlut.edu.cn/page/site/newPc | 校内 AI 助手对话 | 200 |
| 36 | 模型广场（大模型网关） | http://aigw.dlut.edu.cn/ | 大模型 API 网关 | 200；**仅 HTTP** |
| 37 | 校园缴费平台（电费 / 网费） | http://ecardpayment.dlut.edu.cn/ | 宿舍电费、网费充值 | 200；涉金额，操作前先复述 |
| 38 | 玉兰卡（新版门户） | https://ecardv8.dlut.edu.cn/webportal/sso/login | 余额、消费流水 | 302 → SSO |
| 39 | 办事大厅（一网通办服务大厅） | https://ehall.dlut.edu.cn/ | 办理类服务（约 90 项申请 / 审批） | 302 → SSO；**与门户 SPA 是两个系统** |
| 40 | 自助证明打印（办事大厅侧） | https://eproofweb.dlut.edu.cn/api/engine-system/cas/mangeLogin | 证明打印（**与 eproof 是两个系统**） | 302 → SSO；裸根 403 |
| 41 | 统一身份认证大屏 | https://apm.dlut.edu.cn/dashboard/ | 认证运行状态大屏 | 200；只给入口，不解读 |
| 42 | 国际学生信息管理系统 | http://is.dlut.edu.cn/isms/user/tylogin | 留学生学籍与注册 | 303 → 登录页；**仅 HTTP** |
| 43 | 调查问卷系统（问卷星企业版） | https://dlutwj.wjx.cn/corplogin.aspx | 校内问卷填报 | 200；**非 DUT 域** |
| 44 | 科技成果转化平台 | https://tt.dlut.edu.cn/ | 成果转化、专利运营 | 200；非学生高频 |
| 45 | 校园网测速 | http://speedtest.dlut.edu.cn/ | 网速自测 | 200；**仅 HTTP** |

---

## 3. 易混淆的系统对

| 容易混淆 | 区别 |
|---|---|
| `dutxg` 智慧学工 / `dutsa` 学工系统 | 前者面向学生事务应用，后者面向学工业务办理；都需登录，不要互相替代 |
| `eproof` / `eproofweb` | 两个不同的证明打印系统 |
| 门户 SPA / `ehall` 办事大厅 | 两个不同的系统，门户是聚合展示，办事大厅是申请审批 |
| `tycg` / `tycgzx` | `tycgzx` 是文体场馆中心官网，`tycg` 是另一系统 |

## 4. 不登记为入口的地址

以下地址**不写入入口清单**，需要时由用户从门户或 WebVPN 内点入：

- 门户「全部服务」中的校内网段直连类（工程训练中心在线选课、创新创业项目管理平台、科研创新平台、站群系统、主站系统、融媒体编辑系统等）：`10.8.x.x` 为校内私网段、`202.118.x.x` 为校内公网段，**校外不可达**。
- WebVPN 资源清单中未登记的 17 项（协同办公自动化、党委组织部、国有资产统筹管理平台、采购综合管理平台、教师主页、日语视频语料库、体育场馆服务、信息化建设管理系统、校园防控平台、专业学位论文管理系统、创新创业管理平台、校友数据库、试剂耗材综合管理系统、数智化课程教学实践平台、基金会综合管理平台、机构知识库、图书管理系统）。
- 主机名（供人工复查）：`oamain` `zuzhibu` `gztc` `cgbmis` `xmgl` `mbamis` `cxcygl` `alumnidata` `sjhczhgl` `csteach` `edfdata` `dlutir` `meta.lib` `tycg` `202.118.76.109` `202.118.76.16:8083` `210.30.96.50`
