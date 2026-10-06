# 校内平台 · 字段映射

> 用途：说明各平台能取到哪些字段，以及这些字段归哪个 skill 消费。
> 依据：2026-10-01 实测（`portal.dlut.edu.cn` 首页）；2026-10-06 增补第四～七节（均为 `jxgl.dlut.edu.cn` 实测）。

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
| 综合教务系统 | `jxgl.dlut.edu.cn` | 课表、考试安排、培养方案（完成情况）、选课结果、成绩 | `course-select` `exam-sprint` `portal-operator` | 成绩明细只在用户明确要求时读取；页面细节见第五、六节 |
| 全校开课查询（同在教务系统） | `jxgl.dlut.edu.cn` | 本学期全部开课：课程性质、课程类型、开课单位、任课教师、时间地点、选课人数与容量 | `course-select` | 独立标签页；入口 ID 每次不同，不写死；字段见第四节 |
| 图书馆 | `lib.dlut.edu.cn` | 借阅清单、续借、座位 / 研讨间预约 | `lit-fetch` `portal-operator` | — |
| 一卡通 | `ecard.dlut.edu.cn` | 余额 | `portal-operator` | 卡内充值入口 https://ecard.dlut.edu.cn/info/1013/1139.htm （正文为图片，细则须人工核对）；消费流水走 `ecardv8` |
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
| i大工 APP | 应用商店 | 场馆 / 心理 / 浴室 / 校车预约 | `portal-operator` `dorm-life` | 场馆 / 浴室 / 校车仅 APP；心理另有网页入口（`dlut-login-sites.md` #29） |

---

## 三、字段 → skill 的消费方式

| skill | 消费哪些字段 | 用途 |
|---|---|---|
| `lecture-to-notes` | `schedule.courses[]` | 按课表归档笔记，标注待补章节 |
| `exam-sprint` | `schedule.courses[]` + 考试安排 | 倒排冲刺计划 |
| `notice-track` | `card.balance` `net.*` `agenda[]` `notices[]` | 事务提醒（欠费 / 借阅逾期 / 待办） |
| `lit-fetch` | `library.on_loan_count` | 提醒还书，避免影响借阅额度 |
| `course-select` | 培养方案 + 选课结果 + 成绩 + 全校开课字段（第四、五节） | 学分缺口对照、开课清单归类 |
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
| `examMode.nameZh` | 考核方式 | — |
| `teachLang.nameZh` | 授课语言 | — |
| `requiredPeriodInfo.total` / `.weeks` | 总学时 / 周次 | — |
| `course.tags[].nameZh` | 课程标签 | — |
| `teacherAssignmentList[].teacher.nameZh` | 任课教师 | — |

**取数流程（须在已登录页面内执行）**：

1. **入口是 JS SPA，没有 `href`**：在已打开的教务首页里 `click()` 入口的**文本节点**（不是链接），会**新开一个标签页**；点完等约 3 秒再列标签页。新页初始 `title` / `url` 可能为空，**不要判定为失败**。
2. **不要按标签页序号取数**：标签页顺序会变动，用 URL 片段（如 `lesson-search`）匹配目标页。
3. **分块取**：一次 5 页 × 300 条，避免单次 CDP 返回体过大；总页数从 `_page_.totalPages` 取。同一教学班可能重复出现，按 `lessonId` 去重。

```js
// 在已登录的开课查询页内执行；<学期ID> 与 <入口ID> 从落地 URL 取，不写死
(async () => {
  const nm = (o) => (o && (o.nameZh || o.name)) || null;
  const slim = (d) => ({
    lessonId: d.id,
    lessonName: d.nameZh,
    lessonCode: d.code,
    courseName: d.course && d.course.nameZh,
    courseCode: d.course && d.course.code,
    credits: d.course && d.course.credits,
    courseType: nm(d.courseType) || nm(d.course && d.course.courseType),
    courseProperty: nm(d.course && d.course.courseProperty) || nm(d.courseProperty),
    openDept: nm(d.openDepartment),
    campus: nm(d.campus),
    stdCount: d.stdCount,
    limitCount: d.limitCount,
    teachers: (d.teacherAssignmentList || [])
      .map((t) => nm(t.teacher) || nm(t))
      .filter(Boolean)
      .join(',') || d.teacherAssignmentStr || null,
    schedule: d.scheduleText && d.scheduleText.dateTimePlaceText
      ? d.scheduleText.dateTimePlaceText.textZh : null,
  });
  const api = (page) =>
    '/student/for-std/lesson-search/semester/<学期ID>/search/<入口ID>'
    + '?bizTypeAssoc=2&queryPage__=' + page + ',300&_=' + Date.now();
  const rows = [];
  let page = 1;
  let total = 1;
  while (page <= total) {
    const res = await fetch(api(page), { headers: { 'X-Requested-With': 'XMLHttpRequest' } });
    const json = await res.json();
    total = (json._page_ && json._page_.totalPages) || 1;
    rows.push.apply(rows, json.data.map(slim));
    page += 1;
  }
  const seen = {};
  const unique = rows.filter((r) => !seen[r.lessonId] && (seen[r.lessonId] = 1));
  return JSON.stringify({ total: unique.length, rows: unique });
})()
```

**筛选控件不可信（易错）**：`selectize` 组件 `setValue` 后点「查询」结果数不变（值没进请求）；自己拼 URL 带筛选参数会直接返回「无数据」。**一律以接口返回字段为准**，筛选用本地过滤。

**无「人文类」字段**：系统内不存在这一分类，人文类这类清单只能按开课单位 + 课程名人工归类，交付时须声明是人工归类。

**已知缺陷**：课程详情 `/student/for-std/lesson-search/info/<教学班ID>` 实测返回 500，勿依赖。

---

## 五、培养方案完成情况（2026-10-06 实测增补）

**入口**：`jxgl.dlut.edu.cn` → 「培养方案完成情况」（常用服务区与「培养方案」分组各有一个入口）。落地路径形如 `/student/for-std/program-completion-preview/info/<入口ID>`，**入口 ID 每次不同，不写死**；点开后**新开一个标签页**。

页面可获取：毕业要求总学分与已完成学分、**一级模块**的要求/已完成/未完成/在读学分与子模块数、**各级子模块**的同类数据、**方案内逐门课程**（课程代码、开课学期、是否必修、学分、成绩、绩点、系统检查情况、最终检查情况、备注），以及独立的「**计划外完成情况**」表。

**DOM 结构（关键）**：

- 模块头与课程表是**兄弟节点**，按文档顺序关联；模块头类名 `.module-tpl depth-N`（N 为层级），名称在 `.module-name`，学分文本在 `.title-item.credits`。**不要靠嵌套查找**。
- **须连点约 4 轮「展开全部」**才拿到全部层级，点一次会漏。
- 页面上的「**展开一级/二级…/展开全部/收起全部**」与「**仅看未完成**」是筛选控件，改动前先确认当前展开状态。

**展开脚本（在已登录页面内执行，连点 4 轮）**：

```js
(async () => {
  const clean = (s) => (s || '').replace(/\s+/g, ' ').trim();
  let clicks = 0;
  for (let round = 0; round < 4; round++) {
    const btns = [...document.querySelectorAll('*')].filter(
      (e) => e.children.length === 0 && /^展开(全部|一级|二级|三级|四级)?$/.test(clean(e.innerText))
    );
    if (!btns.length) break;
    for (const b of btns) { b.click(); clicks++; }
    await new Promise((r) => setTimeout(r, 900));
  }
  return JSON.stringify({ clicks, tables: document.querySelectorAll('table').length });
})()
```

**抽取脚本要点**：按文档顺序**平铺遍历** `.module-tpl` 与 `table`；用 `.module-tpl` 的 `depth-N` 取层级、`.module-name` 取名、同级 `headBox` 文本取「要求 / 已完成 / 未完成 / 在读」与「子模块：要求 / 已完成 / 未完成」数字；**按表头是否含「开课学期 + 是否必修」区分方案内表与计划外表**，再按 `depth` 重建层级树；合并同名一级模块，`已完成 / 要求学分` 从 body 正则兜底。

| 字段 | 位置 | 备注 |
|---|---|---|
| 模块层级 | `.module-tpl` 的 `depth-1` 起 | 实际存在 depth 3、4 的嵌套子模块 |
| 模块/子模块名称 | `.module-name` | — |
| 要求 / 已完成 / 未完成 / 在读学分 | 同级文本「学分：要求 X \| 已完成 Y \| 未完成 Z(在读 W)」 | 在读学分只出现在部分层级 |
| 子模块数 | 「子模块：要求 X \| 已完成 Y \| 未完成 Z」 | 只出现在一级模块 |
| 课程行 | 方案内表 10 列 | 课程名称/课程代码/开课学期/是否必修/学分/成绩/绩点/系统检查情况/最终检查情况/备注 |
| 开课学期 | 如 `1-1`、`3-3` | 形如 `1-2,1-3,2-1,…` 表示**多学期任选其一**，不是要都修 |
| 在读状态 | 「系统检查情况」列 | 取值：在读 / 未修 / … |
| 计划外课程 | 「计划外完成情况」表 **7 列**（无开课学期、无是否必修） | **列数与方案内表不同** |

**取数口径（易错）**：

1. **必须按表头区分两张表**：方案内表含「开课学期 + 是否必修」，计划外表没有。不区分会把计划外课程误挂到最后一个子模块下。
2. **子模块在 DOM 抽取时会被拍平**（depth≥2 的节点都并到一级模块下）→ 统计前须按 `depth` 重建层级树，否则父子节点重复计数。
3. 「计划外完成情况」的课程**不计入培养方案进度**，是独立的另一栏。
4. 交叉验证：用第六节的「我的课表」核对「在读」课程，两处应一致。

**交付时必须如实标注的口径差异**（实测存在，勿替系统补全）：

- 各一级模块要求学分相加 **≠** 系统顶部显示的毕业要求总学分（实测 157 vs 150）；
- 某模块的要求学分 **≠** 其子模块要求相加（实测「专业课程」72 vs 60）。

→ 原样列出并建议用户向学院/教务处核实，不推断为笔误或补全规则。

**高价值发现点**：「计划外课程」常出现在 A 系列数学课等特殊班型课程上（方案要求的是标准课名，实读是 A 系列课名）→ 这类课需走**课程替代申请**才计入方案，发现即显著提示。

**无「人文类」分类**：与第四节同，系统只有课程性质（通识类课程 / 全校选修类课程 / 素质课程 / 专业课程等），不存在人文类字段。

---

## 六、我的课表（2026-10-06 实测增补）

**入口**：`jxgl.dlut.edu.cn` → 「我的课表」（常用服务区与「课程与教材」分组各有一个入口）。落地路径 `/student/for-std/course-table`（**无入口 ID**，可直接访问）。

- 纯展示页（周课表网格），正文每门课形如 `<课程号>.<序号> <课程名> <教室> (<周次>) <星期> (节次) 上课组:… 人数:已选/容量`，可直接从 `innerText` 提取。
- 页内有「大课表 / 全部课程 / 打印」开关；未安排具体时间地点的课程只在「全部课程」里。
- 用于核对「在读」课程、与培养方案进度交叉验证。

**提取方式**：直接读页面 `innerText`，按上述格式正则切分即可，无需解析 DOM。读不到课程时先确认页内「全部课程」开关已打开（未排课的课程只在「全部课程」里）。

---

## 七、浏览器接入与取数操作（2026-10-06 实测增补）

教务系统的取数都在**用户已登录的浏览器**里做，登录前提与授权纪律见 `portal-operator`；落地入口、取数流程与字段口径见第四～六节。以下是操作层的共性要点：

- **端口**：从专用配置目录下的 `DevToolsActivePort` **第一行**读；文件缺失、或修改时间早于本次启动时刻，即视为无效。
- **只连不关**：接入的浏览器归用户所有，取数结束只断开连接，**不结束浏览器进程**，否则用户登录态丢失。
- **按 URL 片段定位目标页**：标签页顺序会变动，不按序号取；新开的 SPA 页初始 `title` / `url` 可能为空，不要判定为失败。
- **中文乱码**：CDP 的 HTTP 端点声明 `latin-1` 编码，须按 utf8 重新解码响应 buffer，否则中文全是乱码。
- **SPA 入口要点击**：入口多为 JS 渲染、没有 `href`，须 `click()` 文本节点，且会新开标签页；点完等约 3 秒再列标签页。
- **分块取数**：单次请求或返回体过大会失败，按分页分块取，再在本地合并去重。
- **只读**：这些页面只用于取数，不改写任何系统记录。

**脚本落点**：上述操作脚本属仓库维护工具，不进交付包；交付包内以本节与第四～六节的口径为准，由 agent 临场在已登录页面内执行等价脚本。
