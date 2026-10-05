# 人格（Agents）

人格是**预置的角色与工作方式**，不是新的能力。它们负责决定「用哪种语气、按什么顺序调用哪些 skill」，能力本身仍由 `../skills/` 提供。

| 人格 | 面向 | 常用 skill |
|---|---|---|
| `study-coach` | 学习方法与备考 | `explain-stepwise` `error-diagnose` `faster-cycle` `lecture-to-notes` `exam-sprint` `recall-schedule` `reading-note` `lang-drill` |
| `research-librarian` | 科研检索与写作 | `lit-fetch` `citation-verify` `reading-note` `paper-outline` `cite-normalize` `data-lab` `code-mentor` |
| `campus-concierge` | 校务与平台代办 | `campus-search` `advisor-finder` `notice-track` `campus-desk` `course-select` `campus-proof-guide` `dorm-life` `portal-operator` |

## 宿主发现

本包**宿主无关**：人格与技能的可移植核心是 `agents/*.md` 与 `../skills/<name>/SKILL.md`（均为 `name` + `description` frontmatter），入口由包根 `../plugin.json` 的 `skills` / `agents` / `commands` 声明。安装时按目标宿主的技能 / 插件及 agent 发现规范把整包放入其目录，不改包内结构。

先核对目标宿主的发现规范，再选择安装方式；不要推定目录或清单存在就可用。常见约定（**示例，须以宿主规范为准**）：Claude Code 用 `~/.claude/agents/` 或项目 `.claude/agents/`，GitHub Copilot 用 `.github/agents/`，LearnBuddy 约定为 `~/.learnbuddy/skills/qihang/`；CodeBuddy / WorkBuddy 依 `../.codebuddy-plugin/plugin.json`。`~/.learnbuddy` 不是所有宿主的通用路径，也不应未经确认改套专家目录。

根 `../SKILL.md` 兼容读取**不等于 25 个子 skill 已注册**，更不等于 `../agents/` 的 3 个人格或 `../commands/` 的 7 个命令已被发现。应分别验收人格与命令发现、业务正文读取和共享依赖加载；本文不声明已经宿主实测。宿主未发现人格时，不能声称已切换到该人格。

## 规则与执行前置

1. 人格不复制 skill 内容，只负责编排；人格语气不能覆盖共享规则或业务边界。
2. 三个人格执行前都必须完整读取 `../skills/using-qihang/SKILL.md` 中的共享行为准则与安全兜底，再完整读取 `../config.yaml`。**只加载共享规则与配置，不重新执行总入口路由**；这同样适用于 24 个业务 skill 和 7 个 command 的前置。
3. 各文件内的相对路径以该文件所在目录为基准，不以用户当前工作目录为基准。人格实际文件位于 `../agents/`，其加载路径须从该目录计算。
4. 本会话已完整加载的共享规则与配置可复用；任一必需文件缺失或不可读时停止本包执行，并说明缺失文件，不猜测规则、配置或正文。
5. 每次调用业务 skill 前，必须完整读取相应 `../skills/<name>/SKILL.md` 正文并遵守其执行前置；名称、description 或人格里的能力列表都不能替代正文。
6. 人格之间不互相调用；需要别的能力时读取并执行对应 skill。没有匹配人格、需要总入口路由时，根入口仍须先完整读取共享规则与配置，再由 `using-qihang` 选 skill。

## 校务编排边界

`campus-concierge` 不能把「帮我查一下」等礼貌措辞当作登录或代办授权。公开查询或办理路径咨询不登录；确需登录或实际代办时，先核对明确授权及站点限制。

转入 `portal-operator` 后，必须完整读取其正文，并在打开平台前完整读取 `../config.yaml`、`../references/dlut-login-sites.md`、`../references/dlut-official-sites.md` 和 `../references/dlut-field-map.md`。配置已定义的入口以配置为准，只读取授权且允许的字段；必需文件不可读、入口缺失或限制不明时停止相关执行，不猜测。涉及金额或不可撤销操作须复述确认，身份验证等本人环节交给用户完成。

**心理服务 / 心理预约只给入口，不登录读取或代办预约内容**；人格编排或用户确认都不能绕过站点限制。浏览器能力或隐私边界不满足时说明未执行，不把提供入口说成已经代办。

## DUT 定位与维护

本包为 DUT 特化包，人格的发现描述与正文同样可能含学校绑定。换校不只是改配置或几份资料，须核对所有发现描述、正文学校绑定、插件元数据、配置与站点资料，并重新验收宿主发现、路由及授权 / 隐私边界。

使用交付技能包自身不需要 Python 依赖；维护源码仓库时应遵守 [`skill-anatomy.md`](skill-anatomy.md) 的环境、校验与回归要求。新增或修改共享加载规则时，须有相应回归测试，不能只修改说明文字。
