# 「启航」大连理工大学学习 · 信息搜集 · 校务助手 v4.0

> 面向大连理工大学（大工 / DUT）学生 ｜ 强绑定 DUT 公开站与需登录的校内平台
> 结构：**扁平 skill 包，25 个 skill**，按「学习 → 巩固 → 产出 → 数据代码 → 检索 → 校务」六个阶段组织
> 用法：直接用自然语言说需求，**不需要斜杠命令，也不需要先选分类**

---

## 0. 快速开始

```bash
git clone https://github.com/xiaojun10086/qihang-pack.git
cp -r qihang-pack ~/.learnbuddy/skills/qihang     # 或项目级 .learnbuddy/skills/qihang
```

**装完怎么开始**：直接说需求即可。

- 「这步怎么来的，没听懂」→ 分步讲解
- 「下周考高数，怎么复习」→ 考前冲刺
- 「帮我上教务系统查一下这学期课表」→ 校内平台代操作
- 「最近有什么奖学金通知」→ 通知跟踪

---

## 1. 结构

```
qihang-pack/
├── SKILL.md              # 包入口（兼容单 skill 装载）
├── plugin.json           # 插件清单，"skills": "./skills"
├── config.yaml           # 学校绑定与学期参数（唯一需要按学期修改的文件）
├── skills/               # 25 个扁平 skill
│   └── <skill-name>/SKILL.md
├── agents/               # 3 个人格：study-coach / research-librarian / campus-concierge
├── commands/             # 6 个斜杠命令：learn / notes / exam / paper / search / campus
├── docs/                 # skill-anatomy / getting-started / agents
└── references/           # 可核验信息源：dlut-official-sites / dlut-login-sites / dlut-field-map
```

**加载机制**：启动时只有每个 skill 的 `name` + `description` 进入上下文，`SKILL.md` 正文按需加载。因此 description 决定能不能被发现。

结构规范见 [`docs/skill-anatomy.md`](docs/skill-anatomy.md)。

---

## 2. 25 个 skill

| 阶段 | skill | 做什么 |
|---|---|---|
| — | `using-qihang` | 总入口与路由；三条共享行为准则 |
| 学习 | `explain-stepwise` | 分步讲解一个概念或一道题 |
| 学习 | `error-diagnose` | 从多道错题里归因 |
| 学习 | `faster-cycle` | 系统学完一门课 |
| 学习 | `lecture-to-notes` | 讲义 / 课堂整理成可复习笔记 |
| 学习 | `reading-note` | 精读论文与专著 |
| 学习 | `lang-drill` | 语言能力练习 |
| 巩固 | `exam-sprint` | 考前冲刺排程 |
| 巩固 | `recall-schedule` | 记忆与间隔重复排程 |
| 产出 | `assignment-plan` | 大作业与小组任务拆解 |
| 产出 | `lab-report` | 实验报告与课程论文骨架 |
| 产出 | `paper-outline` | 论文结构与答辩准备 |
| 产出 | `cite-normalize` | 参考文献格式与文献管理 |
| 数据代码 | `data-lab` | 实验数据处理与统计 |
| 数据代码 | `code-mentor` | 编程学习与科研代码 |
| 检索 | `campus-search` | 校园公开信息检索 |
| 检索 | `advisor-finder` | 导师与教师资料 |
| 检索 | `notice-track` | 通知与截止节点跟踪 |
| 检索 | `lit-fetch` | 文献检索与全文获取 |
| 检索 | `citation-verify` | 引文核验 |
| 校务 | `campus-desk` | 校园事务办理路径 |
| 校务 | `course-select` | 选课与培养方案对照 |
| 校务 | `campus-proof-guide` | 证明开具 |
| 校务 | `dorm-life` | 宿舍、报修、离校 |
| 校务 | `portal-operator` | 校内平台代操作 |

---

## 3. 三条共享行为准则

所有 skill 都遵守，正文不再重复声明：

1. **先给可用的答案** —— 结论放最前面；只追问会改变答案、安全边界或下一步行动的信息，一轮内一次问完。
2. **区分「解释」与「代做」** —— 讲方法、给结构、给路径、给同类练习可以；不产出用于提交的成品（作业答案、论文正文、可提交代码、文书）。判据是用途：说「交上去」不给成品，说「自己对着学」就讲透。
3. **涉及事实必须给来源** —— 校内信息优先官方来源，附出处与日期；未实时核验就明说「未核验」，不编造 URL、电话、单位名、时间。

### 安全兜底（高于以上全部）

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗 | 挂失银行卡 + **96110** + **110** |
| 急症、外伤、意识异常 | **120**，不诊断、不给药 |

---

## 4. 校内平台代操作

`portal-operator` 在用户明确授权后**直接打开目标平台并执行操作**，然后回报结果，而不是给一个链接让用户自己去。

**只在两处停下确认**：

| 类别 | 处理 |
|---|---|
| 涉及支付金额 | 复述金额与用途，用户确认后再继续 |
| 不可撤销操作（提交报名、退课、退宿申请等） | 复述操作内容与后果，用户确认后再提交 |

其余查询类操作直接执行。凭证（用户名 / 密码 / 验证码）只留在浏览器会话里，不写入任何文件、日志或回复正文。页面上的身份证号、银行卡、家庭信息不主动读取也不转述。

平台入口见 [`references/dlut-login-sites.md`](references/dlut-login-sites.md)，字段映射见 [`references/dlut-field-map.md`](references/dlut-field-map.md)。

---

## 5. DUT 融入

| 类型 | 文件 | 内容 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | 学校主站、校区、教学资源、学部学院、职能部门、官方新媒体；含域名规律与未核实清单 |
| 需登录站 | `references/dlut-login-sites.md` | 45 个需登录站点；含 WebVPN 注意事项与易混淆系统对照 |
| 字段映射 | `references/dlut-field-map.md` | 门户聚合点可取的 6 类数据 + 逐站字段 + 归哪个 skill 消费 |

**使用纪律**：涉及校情、教务、学院、校区、职能部门的问题，先查表定位入口；表未命中时回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」，不臆造 URL。

---

## 6. 复用与扩展

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换学期 / 课程 | `config.yaml` 的 `term` / `courses` / `exam_weeks` | 3 行 |
| 加 skill | 新建 `skills/<name>/SKILL.md`，frontmatter 只写 `name` + `description` | 1 个文件 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |
| 换学校 | `config.yaml` 的 `school` 段 + `references/dlut-*.md` | 4 处 |

---

## 7. 免责

- 本包为 **DUT 特化 skill 包**：skill 文本离线可读；实际执行依赖宿主平台的模型与工具能力。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 第三方来源与许可归属见 [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)。
- 本包自身：MIT。

---

## 8. 版本记录

| 版本 | 修订号 | 主要变更 |
|---|---|---|
| **v4.0** | `4.0.0` | **系统性重构**：三级结构（`domains/` 92 skill）→ 扁平结构（`skills/` 25 skill）；取消澄清门 / 域审查 / 输出规范 / 记忆落点 / 外部桥接；`portal-operator` 支持用户授权后代为操作校内平台；`config.yaml` 精简为学校绑定 + 学期参数；新增 `agents/`、`commands/`、`docs/`、`plugin.json`。 |
| v3.4 | `3.4.0` | 第一阶段体验增强：统一快速入口与自然语言起始句型。 |
| v3.3 | `3.3.0` – `3.3.9` | 外部 skill 桥接、外部来源清单扩充、触发门词表同源与域锁定加固。 |
