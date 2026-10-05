# 快速上手

## 安装

「启航」v4.1.0 是 DUT 特化包，但**安装宿主无关**：可移植核心是 `skills/<name>/SKILL.md`（`name` + `description` frontmatter）与 `agents/*.md`，入口由包根 `../plugin.json` 声明（`skills` / `agents` / `commands`），`../config.yaml` 与 `../references/` 为宿主无关数据。安装即**按目标宿主规范把整包放入其技能目录**，不改包内结构、不拆包。

先查目标宿主的技能 / 插件发现规范，确认目录约定、清单格式与子目录发现方式，再安装；不假定 WorkBuddy 或其他宿主通用。

常见宿主约定（**示例，须以宿主规范为准**）：通用宿主依 `../plugin.json` 的 `"skills": "./skills"`；Claude Code 为 `~/.claude/skills/qihang/` 或项目 `.claude/skills/qihang/`；GitHub Copilot 为 `.github/skills/qihang/`；LearnBuddy 约定为 `~/.learnbuddy/skills/qihang/` 或项目 `.learnbuddy/skills/qihang/`；CodeBuddy / WorkBuddy 依 `../.codebuddy-plugin/plugin.json`。`../commands/*.toml` 为宿主相关格式，宿主只识别 Markdown 命令时按其规范转换或暂不安装。

包根 `../plugin.json` 声明 `"skills": "./skills"`，但清单是否被识别由宿主决定；不推定未知插件格式或专家目录。根 `../SKILL.md` 兼容单入口读取，**不等于 25 个子 skill 已注册**。安装后分别验收：

- 子 skill 是否被发现，选中后的完整正文、共享规则、配置和必需资料是否可读。
- `../commands/` 的 7 个命令、`../agents/` 的 3 个人格是否各自被发现；目录存在不等于可用。
- 实际所需工具是否可用；无浏览器等能力时应说明未执行，不声称已完成代操作。

这是一份验收要求，不是已完成各宿主实测的声明。详见 [`../INSTALL.md`](../INSTALL.md)。**使用交付技能包自身不需要 Python 依赖**；维护源码仓库的环境要求另见 [`skill-anatomy.md`](skill-anatomy.md)。

## 用法

发现与加载验收通过后，直接用自然语言说需求，**不需要记分类名，也不需要斜杠命令**。

| 你想做什么 | 直接这样说 |
|---|---|
| 搞懂一个概念 | 「这步怎么来的，没听懂」 |
| 系统学一门课 | 「我这学期要自学信号与系统」 |
| 整理笔记 | 「把这份讲义整理成笔记」 |
| 备考 | 「下周考高数，怎么复习」 |
| 写实验报告 | 「实验报告的数据处理部分怎么写」 |
| 查校务 | 「转专业需要什么材料」 |
| 查通知 | 「最近有什么奖学金通知」 |
| 查文献 | 「帮我找关于柔性传感器的综述」 |
| 代操作平台 | 「帮我上教务系统查一下这学期课表」 |

## 六个阶段

```text
学习 ──→ 巩固 ──→ 产出 ──→ 数据代码 ──→ 检索 ──→ 校务
```

包内 `using-qihang` 是总入口，负责把需求路由到下面六个阶段的 skill；多数时候不必点名它。根入口必须先完整读取 `../skills/using-qihang/SKILL.md` 和 `../config.yaml`，再路由。

- **学习**：`explain-stepwise` `error-diagnose` `faster-cycle` `lecture-to-notes` `reading-note` `lang-drill`
- **巩固**：`exam-sprint` `recall-schedule`
- **产出**：`assignment-plan` `lab-report` `paper-outline` `cite-normalize`
- **数据代码**：`data-lab` `code-mentor`
- **检索**：`campus-search` `advisor-finder` `notice-track` `lit-fetch` `citation-verify`
- **校务**：`campus-desk` `course-select` `campus-proof-guide` `dorm-life` `portal-operator`

24 个业务 skill、3 个 agent、7 个 command 执行前也须完整读取共享规则与配置；**加载共享规则不重新触发总入口路由**。每次调用业务 skill 都必须先完整读取其正文，不能只看名称或 description 执行。本会话已经完整加载的共享规则与配置可复用，任一必需文件不可读则停止本包执行并说明原因，不猜测。所有相对路径以对应文件所在目录为基准，不以当前工作目录为基准。

## 三条共享行为准则

1. **先给可用的答案** —— 结论放最前面，只追问会改变答案、安全边界或下一步行动的信息。
2. **区分「解释」与「代做」** —— 讲方法、给结构、给路径可以；不产出用于提交的成品。
3. **涉及事实必须给来源** —— 校内信息优先官方来源，附出处与日期；未实时核验要明说，不编造。

## 校内平台代操作边界

`portal-operator` 只在确需登录或实际代办、授权范围明确且站点限制允许时操作；礼貌措辞如「帮我查一下」本身不构成授权。公开信息查询及办理路径咨询不登录。

打开平台前，先完整读取 `../config.yaml`、`../references/dlut-login-sites.md`、`../references/dlut-official-sites.md` 和 `../references/dlut-field-map.md`，核对站点限制与可读字段。配置已定义的入口以配置为准，不硬编码覆盖、不猜地址。必需文件不可读、入口缺失或限制无法确认时停止相关执行。

涉及金额或不可撤销操作时仍须复述确认，身份验证等本人环节交给用户完成。**心理服务 / 心理预约只给入口，不登录读取或代办预约内容**，授权不解除站点限制。凭证不主动保存或输出，先核对浏览器及工具记录设置；不能保证宿主缓存或 trace 绝不留存，无法满足隐私边界时不启动登录。

## 安全兜底

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗 | 挂失银行卡 + **96110** + **110** |
| 急症、外伤 | **120** |

## 配置与迁校

常规学期、修读课程和考试周参数集中在 `../config.yaml`，个人信息留空表示未知，不会被当作事实使用；规则与站点资料有变化时也需核对，不承诺只改固定行数。

本包是 **DUT 特化包**，换校不能只改配置与三份资料。需全面核对所有发现描述、正文中的学校绑定、插件元数据、配置与站点资料，并重新验收宿主发现、路由、引用及授权 / 隐私边界。维护校验与回归要求见 [`skill-anatomy.md`](skill-anatomy.md)。
