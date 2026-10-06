# Skill 结构规范

「启航」v4.2.0 是 DUT 特化包，每个 skill 的正文位于 `../skills/<skill-name>/SKILL.md`。该文件是单个 skill 的必需正文，但本包执行还依赖共享规则、配置及相应资料，不能孤立复制正文后假定可用。

本文包内相对引用以本文所在目录为基准；其他文件中的相对路径也以各自文件所在目录为基准，不回退到仓库根目录或用户当前工作目录。

## 目录结构

```text
qihang-pack/
├── SKILL.md              # 包入口（兼容单 skill 读取，不代表子 skill 已注册）
├── plugin.json           # 插件清单，声明 "skills": "./skills"
├── config.yaml           # 学校绑定与学期参数
├── skills/               # 25 个扁平 skill
│   └── <skill-name>/
│       └── SKILL.md
├── agents/               # 人格（persona）
├── commands/             # 斜杠命令
├── docs/                 # 文档
├── references/           # 跨 skill 共享的可核验信息源
├── requirements-dev.txt  # 仓库维护依赖，不进 release
└── scripts/ tests/ .github/  # 仓库维护、回归测试与浏览器接入工具，不进 release
```

## 发现与加载

本包**宿主无关**：可移植核心是 `../skills/<name>/SKILL.md` 与 `../agents/*.md`（均为 `name` + `description` frontmatter），入口由 `../plugin.json` 的 `skills` / `agents` / `commands` 声明，`../config.yaml` 与 `../references/` 为宿主无关数据。安装即按目标宿主规范把整包放入其技能目录，不改变包内结构、不拆包。

先核对目标宿主的技能 / 插件发现规范，再确定安装目录与清单使用方式。`~/.learnbuddy` 及项目级 `.learnbuddy` 只是明确支持该约定的宿主的示例，不是所有宿主的通用路径；清单存在不等于宿主识别，不推定未知插件格式，也不套用未经确认的专家目录。

常见宿主约定（**示例，须以宿主规范为准**）：

```text
通用（本包清单）      依 ../plugin.json 的 "skills": "./skills"
Claude Code          ~/.claude/skills/qihang/ 或项目 .claude/skills/qihang/
GitHub Copilot       .github/skills/qihang/
LearnBuddy           ~/.learnbuddy/skills/qihang/ 或项目 .learnbuddy/skills/qihang/
CodeBuddy / WorkBuddy  依 ../.codebuddy-plugin/plugin.json 及宿主规范
```

> **`~/.learnbuddy` 已有内容 ≠ 本包已安装**：该目录下可能已存在本包 **v3.4.0 旧版**「启航」（20 域 `domains/` 三级结构、`library/` 与 L1/L2/L3 隐私分级，**没有 `skills/` 目录**）。它与本包**同源**——是本包自己的历史版式，而非另一产品，但与本包 v4.2.0 的扁平 `skills/<name>/SKILL.md` 版式不同，两者目录不可互推。安装与验收一律以本包 `../plugin.json` 与本文件为准，不按既有 `.learnbuddy` 目录结构推定本包已被宿主识别或可用。

`../commands/*.toml` 是宿主相关命令格式；宿主只识别 Markdown 命令时，按其规范转换或暂不安装 `../commands/`，不影响 `../skills/` 与 `../agents/`。

根 `../SKILL.md` 可兼容单入口读取，**不等于 25 个子 skill 已注册**；需分别验收子 skill 的发现、正文与依赖读取。`../commands/` 和 `../agents/` 的发现能力也须独立验收，本文不代表已完成宿主实测。

在支持渐进加载的宿主中，`name` 与 `description` 供发现与匹配，正文按需加载；实际发现行为由宿主决定。名称或 description 都不能替代完整正文，每次执行业务 skill 前须完整读取其正文。

## 分发分支

`release` 是给使用者获取交付内容的分支，只保留运行所需内容、结构规范与法务声明：

```text
SKILL.md  plugin.json  config.yaml  .codebuddy-plugin/
skills/   references/  agents/      commands/
docs/skill-anatomy.md   LICENSE      THIRD_PARTY_NOTICES.md
```

以下属于仓库自身的维护文件，不进 release：

```text
README.md  INSTALL.md  docs/getting-started.md  docs/agents.md
scripts/   tests/     requirements-dev.txt
scripts/browser-bridge/   scripts/jxgl/   .github/  .gitattributes  .gitignore
```

清单以 `../scripts/sync_release.py` 的 `WHITELIST` 为唯一真相源。main 提交触发 `../.github/workflows/sync-release.yml` 后，CI 必须先运行维护测试及交付校验，通过后才发布指定已提交版本。

`../scripts/browser-bridge/` 是仓库维护用的零依赖浏览器接入工具（Node >= 22，靠自带的 `fetch` 与 `WebSocket` 走 CDP，读取用户已登录的页面），同样不进 release：交付技能包自身不需要它，技能正文里的登录要求只给用户侧可复制的浏览器命令，不依赖该工具。

`../scripts/jxgl/` 是仓库维护用的综合教务系统页面内取数脚本（依赖同上，只放页面内逻辑，CDP 接入复用 `browser-bridge`，不写死学期 ID / 入口 ID / 端口），同样不进 release：交付侧以 `../references/dlut-field-map.md` 第四～七节的字段口径为准，技能正文不引用该目录。

### 维护环境与检查方式

**交付技能包自身不需要 Python 依赖**，实际执行依赖宿主能力。维护完整源码仓库则要求 **Python >= 3.11**；requirements-dev.txt 固定 **PyYAML==6.0.3** 和 **markdown-it-py==4.0.0**。以下命令均在源码仓库根目录执行，依赖安装与离线检查须区分。

```bash
# 仅维护环境需要；此准备步骤可能联网
python -m pip install -r requirements-dev.txt
# 维护回归测试
python -B -m unittest discover -s tests -v
# 默认离线只读检查当前工作树
python -B scripts/sync_release.py
# 离线只读检查指定已提交版本
python -B scripts/sync_release.py --ref HEAD
python -B scripts/sync_release.py --ref main
# 明确需要发布时才执行
python -B scripts/sync_release.py --ref main --push
```

- 默认检查当前工作树，包括交付白名单中未被忽略的新文件和未提交修改；不 fetch、不构建交付树、不写 Git 对象或引用、不创建临时索引。
- `--ref HEAD` 或 `--ref main` 检查指定已提交版本，不包含工作树未提交改动；同样离线只读，不建树、不写 Git 或临时索引。
- `--push` 只从明确解析出的已提交 ref 发布；未给 `--ref` 时默认 main，main 缺失才回退 HEAD。必须先校验通过，之后才联网、构建交付树并推送，绝不将未提交内容混入发布。
- CI 必须先通过测试及校验，再发布对应提交；工作树检查通过不代表某个已提交 ref 也通过，反之亦然。

### 校验与回归要求

校验必须覆盖下列约束；维护者新增或修改校验规则时，须同步补充相应回归测试，不能仅在文档中声明支持。

1. **白名单完整性**：每个交付白名单条目必须命中文件；默认工作树检查须覆盖白名单内未被忽略的新文件及未提交修改。
2. **Markdown 引用**：用 Markdown 解析器识别真实链接（包括引用式链接、带标题或片段的链接）及正文行内代码中的本地路径，不用正则扫描整篇文档代替解析。围栏 / 缩进代码块里的示例不算真实引用，不能因示例中的虚拟路径报悬空，也不能漏掉实际引用。远程链接不作为本地文件处理，离线校验不访问站点。
3. **路径解析**：本地目标按引用所在文件目录解析，不能通过尝试仓库根路径来掩盖错误。真实引用须指向交付文件；有意指向仓库维护文件的引用须逐条登记到 `../scripts/sync_release.py` 的 `REPO_ONLY_REFS`，不能随意豁免未登记引用。本节对同步脚本及 CI 工作流的引用属于此类。
4. **YAML frontmatter**：使用 YAML 解析器检查必填字段、允许键、字段类型及 description 长度，并验证子 skill 名称与目录一致，要求见下节。
5. **版本 SemVer 一致性**：`../plugin.json`、`../.codebuddy-plugin/plugin.json`、`../config.yaml` 的版本必须是相同的合法 SemVer 字符串，当前为 `4.2.0`；不能仅接受三个相同但不合法的任意文本。
6. **共享加载依赖**：检查根入口、24 个业务 skill、3 个 agent 和 7 个 command 的共享规则 / 配置加载前置、相对路径及依赖文件存在性；同时检查业务正文执行前读取和平台所需站点资料依赖。共享加载不等于重新路由，缺失依赖必须停止而不是猜测。
7. **执行模式隔离**：用回归测试区分工作树检查、显式 ref 检查和推送；验证只读检查不 fetch、不建树、不写 Git / 临时索引，校验失败不进入发布，推送不夹带未提交改动。

引用解析、非法 / 缺失 frontmatter、版本错误、共享依赖缺失等应有成功与失败样例。静态校验不能代替宿主发现验收或真实工具能力验证。

## Frontmatter

Skill frontmatter 必须是合法的 YAML 映射，**仅允许 `name` 与 `description`，两者必填且为非空字符串**。不能用数字、布尔值、列表或映射冒充字符串，也不能加入未允许字段。

| 字段 | 必需 | 类型与约束 |
|---|---|---|
| `name` | 是 | 字符串；小写字母、数字及连字符；子 skill 必须与所在目录名一致，根入口不套用子目录同名规则 |
| `description` | 是 | 非空字符串；第三人称说明「做什么」+「何时使用」，长度不超过 1024 字符 |

运行时指令不写入 frontmatter，放在正文中；上述字段规范不能自行套用为宿主的 agent 或 command 元数据格式。

## Description 写法

description 服务于匹配而不是执行，也不保证宿主已注册该 skill。

- 推荐写「做什么」+ 触发条件：`分步讲解一个概念或一道题，从学生已有的知识出发…当用户说「没听懂」「这步怎么来的」时使用。`
- 不要在 description 里概括流程步骤，这会诱导模型跳过正文直接照做。
- 不要只写「帮助学习」这类无法区分的泛化描述。

## 正文章节（执行前置 + 四段式）

```markdown
# <标题>

## 执行前置
声明相对路径基准，完整加载共享规则及配置；不可读则停止，不重新总入口路由。

## Overview          # 一段话说明这个 skill 做什么、边界在哪
## When to Use       # 触发条件 + NOT for（不适用场景）
## 执行流程           # 有序步骤；可含表格、判据、平台入口
## 常见误判           # 错误做法与正确做法对照
```

规则：

1. 正文建议少于 500 行；超过时考虑拆分。
2. `执行流程` 的步骤必须可执行，不写「理解用户需求」这类空话。
3. `常见误判` 至少 4 条，覆盖该 skill 最容易出现的失败模式。
4. 需要共享资料时引用 `../references/` 中的文件，不复制内容；写入业务 skill 的路径须从该 skill 所在目录计算。
5. 不额外堆叠输出模板、评分标准、自检清单，直接给用户需要的结果；执行前置和安全检查不可省略。

## 共享行为准则与依赖

规则统一维护在 `../skills/using-qihang/SKILL.md`：先给可用的答案、区分「解释」与「代做」、涉及事实必须给来源、涉及查询先判是否需要登录，以及安全兜底。各业务正文不复制规则全文，但必须显式声明完整加载该文件与 `../config.yaml`。

- 根 `../SKILL.md` 必须先完整读取共享规则与配置，再进入总入口路由。
- 24 个业务 skill、3 个 agent、7 个 command 执行前须完整读取共享规则与配置；这里只加载规则，不重新执行总入口路由。总入口不递归读取自己。
- 本会话已完整加载的共享规则与配置可复用；每次调用业务 skill 仍须先完整读取相应正文，不凭名称、description 或简短摘要执行。
- 必需文件缺失或不可读时，停止本包执行并明确说明缺少什么，不猜测规则、配置、正文或站点权限。

以下是写入各执行文件时的路径示例，不是本文所在目录下的实际引用：

```text
根 SKILL.md：skills/using-qihang/SKILL.md、config.yaml
业务 skills/<name>/SKILL.md：../using-qihang/SKILL.md、../../config.yaml
agents/<name>.md 与 commands/<name>.toml：../skills/using-qihang/SKILL.md、../config.yaml
using-qihang 调用业务正文：../<name>/SKILL.md
```

`../skills/portal-operator/SKILL.md` 还须在打开平台前完整读取 `../references/dlut-login-sites.md`、`../references/dlut-official-sites.md` 和 `../references/dlut-field-map.md`。入口遵从配置，授权须明确，礼貌措辞不构成授权；心理服务 / 心理预约只给入口，不登录读取或代办预约内容。必需文件、入口或限制无法核对时停止相关执行。

## 迁校与扩展验收

DUT 特化不只存在于配置或三份站点资料。换校必须全面核对所有发现描述、正文中的学校绑定、插件元数据、配置和站点资料，重新验收宿主发现、路由、路径引用、授权及隐私边界；不得承诺只改 4 个文件或 3 行即可完成。

常规学期参数集中在配置中，也须核对规则与资料变化。新增 skill 或共享依赖时，须同步补齐加载声明、引用和回归测试，再做宿主发现验收；文档说明不能替代验证结果。
