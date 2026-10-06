# 「启航」大连理工大学学习 · 信息搜集 · 校务助手 v4.2.1

> 面向大连理工大学（大工 / DUT）学生 ｜ 强绑定 DUT 公开站与需登录的校内平台
> 结构：**扁平 skill 包，25 个 skill**，按「学习 → 巩固 → 产出 → 数据代码 → 检索 → 校务」六个阶段组织
> 用法：直接用自然语言说需求，**不需要斜杠命令，也不需要先选分类**

---

## 0. 快速开始

本包**宿主无关**：可移植核心是 `skills/<name>/SKILL.md`（`name` + `description` frontmatter）与 `agents/*.md`，入口由 `plugin.json` 的 `"skills": "./skills"`（并声明 `agents` / `commands`）描述，`config.yaml` 与 `references/` 为宿主无关数据。安装时**按目标宿主的发现规范把整包放入该宿主的技能目录**，不改包内结构、不拆包、不改名。

```bash
git clone https://github.com/xiaojun10086/qihang-pack.git
```

常见宿主约定（**示例，安装前须核对宿主规范**，以宿主实际目录与清单格式为准）：

| 宿主 | 技能目录 | 人格 / 命令 |
|---|---|---|
| 通用（本包清单） | 依 `plugin.json` 的 `"skills": "./skills"` | `agents/*.md`、`commands/*.toml` |
| Claude Code | `~/.claude/skills/qihang/` 或项目 `.claude/skills/qihang/` | `~/.claude/agents/`、`.claude/commands/`（Markdown） |
| GitHub Copilot | `.github/skills/qihang/` | `.github/agents/`、`.github/prompts/` |
| LearnBuddy 约定 | `~/.learnbuddy/skills/qihang/` 或项目 `.learnbuddy/skills/qihang/` | 依宿主规范 |
| CodeBuddy / WorkBuddy | 依 `.codebuddy-plugin/plugin.json` 及宿主规范 | 依宿主规范 |
| DSH（DeepSeek Harness） | `dsh/config.example.yaml` 的 `customSkillDirs` 指向本包 `skills/` 与生成的 `dsh/commands/` | 命令技能、人格与 preset 由 `dsh/build_dsh_pack.py` 生成，详见 [`dsh/README.md`](dsh/README.md) |

- 上表是**常见约定，不是各宿主实测结论**；目录或清单存在不等于宿主已注册该包。
- **`~/.learnbuddy` 下可能已有本包旧版「启航」**（v3.4.0：20 域 `domains/` 三级结构、无 `skills/` 目录）。它与本包**同源**，是本包自己的历史版本而非另一产品，但与本包 v4.2.1 的扁平 `skills/<name>/SKILL.md` 版式不同；不按其目录结构推定本包已安装或可用。
- **DSH 必须走适配层**：它只在扫描根直属子目录找 `<name>/SKILL.md`，不支持递归发现，且不读 `commands/*.toml`。适配产物全在 `dsh/` 下（原包结构不变），安装见 [`dsh/README.md`](dsh/README.md)。
- `commands/*.toml` 是宿主相关命令格式；宿主只识别 Markdown 命令时，按其规范转换或暂不安装 `commands/`。
- 根 `SKILL.md` 能作为单入口兼容读取，**不等于 25 个子 skill 已注册**。还需验收子 skill 是否被发现、正文及共享资料是否可读；`commands/` 的 7 个命令和 `agents/` 的 3 个人格也需分别验收，不能由清单或目录存在推定可用。安装说明见 [`INSTALL.md`](INSTALL.md)。

**发现与加载验收通过后怎么开始**：直接说需求即可。

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
├── config.yaml           # 学校绑定与学期参数（常规学期配置入口）
├── skills/               # 25 个扁平 skill
│   └── <skill-name>/SKILL.md
├── agents/               # 3 个人格：study-coach / research-librarian / campus-concierge
├── commands/             # 7 个斜杠命令：/learn /notes /exam /paper /code /search /campus
├── docs/                 # skill-anatomy / getting-started / agents
├── references/           # 可核验信息源：dlut-official-sites / dlut-login-sites / dlut-field-map
├── dsh/                  # DSH 适配层：装配脚本 / 命令技能 / 人设 / preset / 配置样例
└── scripts/ .github/     # 仓库维护用（发布对齐、浏览器接入工具），不进 release
```

**只要交付内容**（不含 README、INSTALL 等仓库说明文档及维护脚本，保留结构规范）：

直接下载整包（zip / tar.gz，解压即用）：

- [release.zip](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/release.zip)
- [release.tar.gz](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/release.tar.gz)

或克隆交付分支：

```bash
git clone -b release https://github.com/xiaojun10086/qihang-pack.git
```

**DSH 适配版**（在 `release` 之上叠加 `dsh/` 适配层，原包结构不变）：

- [dsh-qihang-release.zip](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/dsh-qihang-release.zip)
- [dsh-qihang-release.tar.gz](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/dsh-qihang-release.tar.gz)

```bash
git clone -b dsh-qihang-release https://github.com/xiaojun10086/qihang-pack.git
```

`release` 分支的交付白名单见 `scripts/sync_release.py`，DSH 交付树见 `dsh/build_dsh_pack.py`。main 提交分别触发 `.github/workflows/sync-release.yml`（发布 `release`）与 `.github/workflows/sync-dsh-release.yml`（发布 `dsh-qihang-release`）；CI 必须先通过维护测试及交付校验，才从指定已提交版本构建并推送对应交付分支，失败不得发布。

**加载机制**：在支持渐进加载的宿主中，`name` + `description` 用于发现与匹配，正文按需加载；具体发现行为以宿主规范和验收结果为准。名称或 description 不能替代执行指令：选中业务 skill 后，必须完整读取其 `SKILL.md` 正文再执行。

结构规范见 [`docs/skill-anatomy.md`](docs/skill-anatomy.md)。

---

## 2. 25 个 skill

| 阶段 | skill | 做什么 |
|---|---|---|
| — | `using-qihang` | 总入口与路由；四条共享行为准则 |
| 学习 | `explain-stepwise` | 分步讲解一个概念或一道题 |
| 学习 | `error-diagnose` | 从多道错题里归因 |
| 学习 | `faster-cycle` | 系统学完一门课 |
| 学习 | `lecture-to-notes` | 讲义 / 课堂整理成可复习笔记 |
| 学习 | `reading-note` | 精读论文与专著 |
| 学习 | `lang-drill` | 语言能力练习 |
| 巩固 | `exam-sprint` | 考前冲刺排程 |
| 巩固 | `recall-schedule` | 记忆与间隔重复排程 |
| 产出 | `assignment-plan` | 大作业与小组任务拆解 |
| 产出 | `lab-report` | 实验报告骨架与自查 |
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

## 3. 四条共享行为准则

共享规则统一维护在 `skills/using-qihang/SKILL.md`，不在各业务正文中复制规则全文，但必须显式加载：根 `SKILL.md` 在路由前先完整读取共享规则与 `config.yaml`；24 个业务 skill、3 个 agent、7 个 command 也必须先完整读取这两份文件，才能执行。本会话已完整加载的共享规则与配置可复用；业务 skill、agent 与 command 的前置只加载共享规则，不重新执行总入口路由。任何必需文件不可读时，停止本包执行并说明原因，不猜规则或配置。

各文件中的包内相对路径都以**该文件所在目录**为基准，不以当前工作目录为基准；每次调用业务 skill 都要先完整读取其正文。四条共享行为准则如下。

1. **先给可用的答案** —— 结论放最前面；只追问会改变答案、安全边界或下一步行动的信息，一轮内一次问完。
2. **区分「解释」与「代做」** —— 讲方法、给结构、给路径、给同类练习可以；不产出用于提交的成品（作业答案、论文正文、可提交代码、文书）。判据是用途：说「交上去」不给成品，说「自己对着学」就讲透。
3. **涉及事实必须给来源** —— 校内信息优先官方来源，附出处与日期；未实时核验就明说「未核验」，不编造 URL、电话、单位名、时间。
4. **涉及查询先判是否需要登录** —— 公开站直接查；只在统一认证后可见的（门户、教务系统、一卡通、图书馆账户、离校系统、报名与审批表单），先给出登录要求再转 `portal-operator`：由用户本人用**自己的浏览器**登录，本包不代开浏览器、不代填用户名 / 密码 / 验证码；要本包直接操作页面时浏览器需带调试端口启动——**最快捷做法**是用专用配置目录加 `--remote-debugging-port=0` 启动一次，登录一次即长期免登录，端口写入该目录的 `DevToolsActivePort`——用户确认已登录后本包才接入。完整流程见 `skills/portal-operator/SKILL.md`。

### 安全兜底（高于以上全部）

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗或疑似诈骗（含未遂） | 挂失银行卡 + **96110** + **110** |
| 急症、外伤、意识异常 | **120**，不诊断、不给药 |

**红线**：要求篡改校内系统记录（成绩、学籍、缴费、考勤、评奖等），或编写绕开统一身份认证 / 频次限制的抓取脚本，一律拒绝——**用户授权不构成改写依据**，只给正规申诉或更正渠道。

---

## 4. 校内平台代操作

`portal-operator` 仅在确需登录查询或实际代办、用户明确授权且站点限制允许时，打开目标平台执行操作并回报结果。公开信息查询和办理路径咨询不登录；「帮我查一下」「帮我办一下」等礼貌措辞本身不等于登录或代办授权，范围不明时先问必要问题。

**最快捷登入路径**（要本包直接操作页面时先给这一条）：让用户用自己的浏览器，以**专用配置目录 + `--remote-debugging-port=0`** 启动一次并登录，登录一次即长期免登录；实际端口写入该目录的 `DevToolsActivePort`，本包据此接入，不猜端口、不撞已占用端口。仓库内另有零依赖接入工具 `scripts/browser-bridge/` 与教务系统页面内取数脚本 `scripts/jxgl/`（均为维护用，不进 release）。

打开平台前，先完整读取 `config.yaml`、[`references/dlut-login-sites.md`](references/dlut-login-sites.md)、[`references/dlut-official-sites.md`](references/dlut-official-sites.md) 及 [`references/dlut-field-map.md`](references/dlut-field-map.md)，核对站点限制与允许读取的字段。配置已定义的入口以配置为准，不用硬编码覆盖，也不拼接未登记地址。必需文件不可读、入口缺失或限制无法确认时，停止本包相关执行，不猜测。

**授权及站点限制核对通过后，以下操作仍须复述确认**：

| 类别 | 处理 |
|---|---|
| 涉及支付金额 | 复述金额与用途，用户确认后再继续 |
| 不可撤销操作（提交报名、退课、退宿申请等） | 复述操作内容与后果，用户确认后再提交 |

**心理服务 / 心理预约只给入口**，不登录读取或代办预约内容，用户确认也不解除站点限制。

其余查询只在授权范围及站点限制内执行；身份认证、验证码、人脸识别等本人环节须暂停交给用户。凭证不主动保存或输出到文件、日志或回复正文，操作前须核对浏览器及工具记录设置，不能保证宿主缓存或 trace 绝不留存；不满足隐私边界时不启动登录。无关身份证号、银行卡、家庭信息不主动读取也不转述。浏览器能力不可用时说明未执行，不把提供入口说成已经办完。

---

## 5. DUT 融入

| 类型 | 文件 | 内容 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | 学校主站、校区、教学资源、学部学院、职能部门、官方新媒体；含域名规律与未核实清单 |
| 需登录站 | `references/dlut-login-sites.md` | 45 个需登录站点；含 WebVPN 注意事项与易混淆系统对照 |
| 字段映射 | `references/dlut-field-map.md` | 门户聚合点可取的 6 类数据 + 逐站字段 + 归哪个 skill 消费 |

**使用纪律**：涉及校情、教务、学院、校区、职能部门的问题，先查表定位入口；表未命中时说明「信息库未收录」，从 `config.yaml` 的 `school.official` 引导核实，不臆造 URL。配置不可读或入口缺失时停止相关执行，请用户恢复配置或提供官方材料，不猜地址。

---

## 6. 复用与扩展

本包定位是 **DUT 特化包**，不是只改几行配置即可迁移的通用多校模板。

| 换什么 | 修改与验收范围 |
|---|---|
| 换学期 / 课程 | 常规参数集中在 `config.yaml` 的 `term` / `courses` / `exam_weeks`；核对相关规则与站点资料是否也有变化，不承诺固定行数 |
| 加 skill | 增加业务正文与必需的 `name`、`description`，声明共享规则及配置加载前置，并补齐发现、依赖、引用和回归验收 |
| 扩 DUT 信息库 | 更新 `references/dlut-*.md`，核对来源、站点限制、字段归属及使用方引用 |
| 换学校 | 全面核对所有发现描述、正文中的学校绑定、插件元数据、配置与站点资料，并重新验收宿主发现、路由、引用及授权 / 隐私边界；不只是改配置与三份资料 |

### 维护与发布

**使用交付技能包自身不需要 Python 依赖**；实际执行仍依赖宿主模型及工具。以下仅针对维护完整源码仓库：Python **>= 3.11**，依赖由 `requirements-dev.txt` 固定为 **PyYAML==6.0.3**、**markdown-it-py==4.0.0**。

在仓库根目录使用以下命令（依赖准备与只读检查是不同步骤）。

```bash
# 维护环境准备；使用交付包不需要此步骤
python -m pip install -r requirements-dev.txt
# 维护回归测试
python -B -m unittest discover -s tests -v
# 默认离线、只读检查当前工作树
python -B scripts/sync_release.py
# 离线、只读检查指定已提交版本
python -B scripts/sync_release.py --ref HEAD
python -B scripts/sync_release.py --ref main
# 仅在确需发布时执行：先校验指定提交，再联网、构建并推送
python -B scripts/sync_release.py --ref main --push
```

- 默认检查包含交付白名单内的未提交修改，以及未被忽略的新文件；不 fetch、不构建交付树、不写 Git 对象或引用，也不创建临时索引。
- `--ref HEAD` 或 `--ref main` 只检查相应已提交版本，不包含未提交修改，同样离线只读；不能用它代替工作树检查。
- `--push` 只发布明确解析出的已提交 ref；未传 `--ref` 时默认选 main，main 缺失才回退 HEAD。校验通过后才能联网、构建和推送，绝不包含未提交改动。
- CI 必须先运行维护测试及交付校验，再发布对应提交。校验规范与回归要求见 [`docs/skill-anatomy.md`](docs/skill-anatomy.md)。

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
| **v4.2.1** | `4.2.1` | **第三方独立复核订正**：按 3 轮相互独立复核的 40 条候选缺陷（撤回 1 条）修订 25 个 skill 与信息库——登录样板统一为「独立配置目录 + 自动端口」并注明 Chrome / Edge 136 起忽略默认配置目录；补齐信息库字段口径、访问日期与「已核验 / 未核验（来源已登记）/ 信息库未收录」状态词口径；修正跨 skill 去向点名、路由歧义与判定顺序；补全校务平台 URL 与联系电话；包结构与 DUT 定位不变。 |
| **v4.2.0** | `4.2.0` | **登录流程提速与浏览器接入**：共享行为准则第四条与 `portal-operator` 的登录要求改为「专用配置目录 + `--remote-debugging-port=0` 自动端口」的复制即用命令，登录一次长期免登录，端口经 `DevToolsActivePort` 自动发现；新增仓库维护用零依赖接入工具 `scripts/browser-bridge/`（不进 release）；包结构与 DUT 定位不变。 |
| **v4.1.0** | `4.1.0` | **通用宿主适配**：安装说明改为宿主无关模型，给出常见宿主（通用清单 / Claude Code / GitHub Copilot / LearnBuddy / CodeBuddy · WorkBuddy）约定对照与命令格式提示；`plugin.json` 增声明 `agents` / `commands` 入口；包结构与 DUT 定位不变。 |
| **v4.0.2** | `4.0.2` | **校验与加载契约修复**：默认离线只读检查工作树，显式 ref 检查与发布分离；补齐 Markdown / YAML / semver / 共享加载依赖校验及回归要求，CI 先测试、校验再发布；统一入口与业务正文加载前置、平台站点限制及授权边界；明确宿主发现和 DUT 迁校验收范围。 |
| **v4.0.1** | `4.0.1` | **交付闸门加固**：`verify()` 新增版本一致性断言（`plugin.json` / `.codebuddy-plugin/plugin.json` / `config.yaml` 三处副本必须相同，不一致即校验失败）；引用检查从只认 `.md` 扩到 `.py` / `.yml` / `.yaml` / `.json` 等代码与配置文件，指向未交付文件的引用须逐条登记于 `REPO_ONLY_REFS`，否则校验失败。 |
| **v4.0** | `4.0.0` | **系统性重构**：三级结构（`domains/` 92 skill）→ 扁平结构（`skills/` 25 skill）；取消澄清门 / 域审查 / 输出规范 / 记忆落点 / 外部桥接；`portal-operator` 支持用户授权后代为操作校内平台；`config.yaml` 精简为学校绑定 + 学期参数；新增 `agents/`、`commands/`、`docs/`、`plugin.json`。 |
| v3.4 | `3.4.0` | 第一阶段体验增强：统一快速入口与自然语言起始句型。 |
| v3.3 | `3.3.0` – `3.3.9` | 外部 skill 桥接、外部来源清单扩充、触发门词表同源与域锁定加固。 |
