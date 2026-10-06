# 安装与使用

> 「启航」v4.1.0 是 DUT 特化的扁平 skill 包，25 个 skill 位于 `skills/<name>/SKILL.md`。
> 文本资产离线可读；实际执行依赖宿主平台的模型、发现机制与工具能力。

---

## 一、安装

本包**宿主无关**，不绑定单一宿主约定。可移植核心是 `skills/<name>/SKILL.md`（`name` + `description` frontmatter）与 `agents/*.md`；入口由包根 `plugin.json` 描述（`"skills": "./skills"`，并声明 `agents` / `commands`），`config.yaml` 与 `references/` 为宿主无关数据。安装方式统一为：**把整包放入目标宿主的技能目录**，不改包内结构、不拆包、不改名。

**先查目标宿主的技能 / 插件发现规范**：确认支持的安装目录、清单格式、子目录发现方式与作用域，再按该宿主规范安装。本包不声明所有宿主采用相同约定，也不声明已完成各宿主实测。

常见宿主约定（**示例，须以宿主规范为准**）：

| 宿主 | 技能目录 | 人格 / 命令 |
|---|---|---|
| 通用（本包清单） | 依 `plugin.json` 的 `"skills": "./skills"` | `agents/*.md`、`commands/*.toml` |
| Claude Code | `~/.claude/skills/qihang/` 或项目 `.claude/skills/qihang/` | `~/.claude/agents/`、`.claude/commands/`（Markdown） |
| GitHub Copilot | `.github/skills/qihang/` | `.github/agents/`、`.github/prompts/` |
| LearnBuddy 约定 | `~/.learnbuddy/skills/qihang/` 或项目 `.learnbuddy/skills/qihang/` | 依宿主规范 |
| CodeBuddy / WorkBuddy | 依 `.codebuddy-plugin/plugin.json` 及宿主规范 | 依宿主规范 |
| DSH（DeepSeek Harness） | `dsh/config.example.yaml` 的 `customSkillDirs` 指向本包 `skills/` 与 `dsh/commands/` | 转成 `dsh/personas/` + `dsh/preset.example.yaml` |

**DSH 需要适配层**：DSH 只在扫描根的**直属**子目录里找 `<name>/SKILL.md`，不支持递归 `**/SKILL.md`，把包根交给它只会发现 0 个技能；它的命令是插件注册的 TS 对象，不读 `commands/*.toml`。适配产物（命令技能、人设、preset、配置样例）都在 `dsh/` 下，原包结构不变，详见 [`dsh/README.md`](dsh/README.md)。

```bash
# 通用做法：克隆后按上表（或宿主规范）复制到该宿主的技能目录
git clone https://github.com/xiaojun10086/qihang-pack.git

# 获取 release 交付内容；下载本身不等于已注册到宿主
# 不含 README、INSTALL 等仓库说明文档与维护脚本，保留结构规范
git clone -b release https://github.com/xiaojun10086/qihang-pack.git

# DSH 适配版：含 dsh/ 适配层，可直接按 dsh/README.md 挂载
git clone -b dsh-qihang-release https://github.com/xiaojun10086/qihang-pack.git
```

**插件清单不是通用安装保证**：包根 `plugin.json` 声明 `"skills": "./skills"` 及 `agents` / `commands`，同时含 `.codebuddy-plugin/plugin.json`。宿主是否识别这些清单、如何发现技能，须按其规范确认；不能自行推定未知插件格式或专家目录。

**命令格式提示**：`commands/*.toml` 为宿主相关命令格式；宿主只识别 Markdown 命令时，按其规范转换或暂不安装 `commands/`，不影响 `skills/` 与 `agents/` 使用。DSH 侧已由 `dsh/build_dsh_pack.py` 自动转成「仅用户可调用」的技能，无需手工转换。

**安装验收**：

1. 确认根 `SKILL.md` 是否能作为单入口读取；兼容读取根入口**不等于 25 个子 skill 已注册**。
2. 分别核对宿主是否发现 `skills/` 中的 25 个 skill，是否能完整读取选中 skill 的正文、共享规则、配置及必需资料；不能只看名称或 description。
3. `commands/` 的 7 个命令和 `agents/` 的 3 个人格是否被发现须独立验收；存在文件不等于宿主支持。
4. 用普通需求验证实际加载链和路径解析；浏览器等工具不可用时，应说明能力边界，不把未执行说成已完成。

**使用依赖**：交付技能包自身不需要 Python 依赖，也不需要为阅读技能文本安装维护包。实际操作需要宿主提供相应工具；代为操作校内平台还要求可用且满足隐私边界的浏览器能力，不能假定每个宿主都自带。

---

## 二、用法

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

**斜杠命令**（可选，须宿主支持并发现 `commands/`）：`/learn` `/notes` `/exam` `/paper` `/code` `/search` `/campus`。

**加载前置**：根 `SKILL.md` 必须先完整读取 `skills/using-qihang/SKILL.md` 与 `config.yaml`，再进入路由。24 个业务 skill、3 个 agent、7 个 command 执行前也必须先完整读取这两份文件；只加载共享规则，不重新执行总入口路由。每次调用业务 skill 都须完整读取其正文后执行，不能用 description 代替正文。会话内已完整加载的共享规则与配置可复用；任一必需文件不可读时停止本包执行并说明原因，不猜测。各相对路径以对应文件所在目录为基准，不以当前工作目录为基准。

---

## 三、配置

常规学期 / 课程参数集中在 `config.yaml`；以下是部分字段示例，不是可覆盖完整配置的模板，不能删去版本、入口等其他字段。

```yaml
school:
  name: 大连理工大学
  domain: dlut.edu.cn
student:
  campus: null      # 凌水主校区 / 开发区校区 / 盘锦校区
  college: null
  grade: null
term: null
courses: []
exam_weeks: []
```

`null` 表示未知，**不会被当作事实使用**。只有用户明确确认的信息才作为个人背景。配置中的平台入口是执行依据，站点资料与限制也须保持一致；修改学校名称并不完成迁校。

---

## 四、校内平台代操作

`portal-operator` 仅在确需登录查询或实际代办、用户授权范围明确且站点限制允许时执行，然后回报实际结果。公开信息查询和办理路径咨询不登录；「帮我查一下」「帮我办一下」等礼貌措辞不单独构成授权，权限或范围未知时先问必要问题。

打开平台前，先完整读取 `config.yaml`、`references/dlut-login-sites.md`、`references/dlut-official-sites.md` 和 `references/dlut-field-map.md`，核对入口、站点限制及可读字段。配置已定义的入口以配置为准，不用硬编码覆盖、不拼接未登记地址。必需文件不可读、入口缺失或限制无法确认时停止相关执行，不猜地址或权限。

| 类别 | 处理 |
|---|---|
| 查询类（课表、成绩、通知、借阅） | 仅在明确授权和站点允许的字段范围内执行 |
| 涉及支付金额 | 复述金额与用途，确认后继续 |
| 不可撤销操作（提交报名、退课、退宿） | 复述操作内容与后果，确认后提交 |
| 心理服务 / 心理预约 | 只给入口，不登录读取或代办预约内容；授权不能解除站点限制 |

**凭证处理**：用户名、密码、验证码等凭证不主动保存或输出到文件、日志或回复正文。先核对浏览器与工具的记录设置，不保证宿主缓存或 trace 绝不留存；无法满足隐私边界时不启动登录。页面上的身份证号、银行卡、家庭信息不主动读取也不转述。

**平台打不开时**：身份认证、短信验证码、人脸识别等本人环节 → 停下请用户完成再继续；系统维护或校外不可达 → 说明原因并给替代路径（线下窗口 / 公开来源；WebVPN 仅在用户明确要求校外访问时使用）。浏览器工具不可用时说明未执行，不把提供入口说成已代办。

---

## 五、安全兜底

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗 | 挂失银行卡 + **96110** + **110** |
| 急症、外伤、意识异常 | **120** |

---

## 六、扩展

本包是 **DUT 特化包**，不是只改 4 个文件或 3 行即可换校的通用模板。

| 换什么 | 修改与验收范围 |
|---|---|
| 换学期 / 课程 | 更新 `config.yaml` 的 `term` / `courses` / `exam_weeks`，同时核对规则及站点资料变化，不承诺固定修改行数 |
| 加 skill | 补充正文及必需的 `name`、`description`，声明共享规则与配置加载前置，并验收发现、引用、依赖和回归测试 |
| 扩 DUT 信息库 | 更新 `references/dlut-*.md`，核对来源、站点限制、字段归属及使用方引用 |
| 换学校 | 全面核对所有发现描述、正文中的学校绑定、插件元数据、配置与站点资料，再验收宿主发现、路由、引用、授权及隐私边界 |

结构与维护规范见 [`docs/skill-anatomy.md`](docs/skill-anatomy.md)。

---

## 七、仓库维护（非交付包使用依赖）

维护完整源码仓库要求 **Python >= 3.11**；`requirements-dev.txt` 固定 **PyYAML==6.0.3** 和 **markdown-it-py==4.0.0**。使用交付包不需要安装这些依赖。

在仓库根目录准备维护环境并运行测试、检查；依赖准备可能联网，不属于离线只读校验。

```bash
python -m pip install -r requirements-dev.txt
python -B -m unittest discover -s tests -v
python -B scripts/sync_release.py
python -B scripts/sync_release.py --ref HEAD
python -B scripts/sync_release.py --ref main
```

- 默认检查当前工作树，包括白名单内未提交修改及未被忽略的新文件；离线只读，不 fetch、不建交付树、不写 Git、不创建临时索引。
- `--ref HEAD` 或 `--ref main` 离线只读检查指定已提交版本，不包含未提交修改。
- `--push` 仅从明确解析出的已提交 ref 发布；未传 `--ref` 时默认 main，main 缺失才回退 HEAD。必须先校验通过，再联网、构建并推送，不包含未提交改动。
- CI 必须先通过上述维护测试与交付校验，再发布对应提交。
