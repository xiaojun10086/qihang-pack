# 各平台适配表

> 「启航」是为**跨平台标准件**设计的：所有内容都是 `SKILL.md` 格式，因此平台差异只体现在
> ①安装位置 ②发现方式 ③命令入口 ④记忆系统。

## 一、总览

| 平台 | 安装位置 | 发现方式 | 快捷入口 | 记忆系统 | 支持度 |
|---|---|---|---|---|---|
| **LearnBuddy / WorkBuddy** | `~/.learnbuddy/skills/qihang/`<br>或工作区 `{ws}/.learnbuddy/skills/qihang/` | 读 SKILL.md 的 `description` 自动发现 | 自然语言（无斜杠命令） | `~/.learnbuddy/MEMORY.md`<br>`{ws}/.learnbuddy/memory/` | ✅ **一等公民** |
| Claude Code | `~/.claude/skills/qihang/` | `description` 自动发现 | `/qihang` `/qihang-dlut` 等 21 个斜杠命令 | 无内置，靠文件 | ✅ 完整 |
| Codex | `~/.codex/skills/qihang/` | `description` 自动发现 | 自然语言 | 无内置 | ✅ 完整 |
| Cursor | `.cursor/rules/` | 规则加载 | 自然语言 | 无内置 | ⚠️ 需手动转规则 |
| GitHub Copilot | `.github/copilot-instructions.md` | 指令文件 | 自然语言 | 无内置 | ⚠️ 需手动转指令 |
| Gemini CLI | `~/.gemini/skills/qihang/` | `description` 自动发现 | 自然语言 | 无内置 | ✅ 完整 |
| **连小理**（= LearnBuddy，赛道二场景名） | 见上（同一平台） | 同 LearnBuddy | 同 LearnBuddy | 同 LearnBuddy | ✅ 一等公民 |

---

## 二、LearnBuddy / WorkBuddy 适配（重点）

### 2.1 安装

```bash
# 用户级（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# 或项目级（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang
```

**插件方式**：包根已含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别。

### 2.2 发现与调用

- LearnBuddy 通过 **SKILL.md 的 `description`** 自动判定何时加载，**无需斜杠命令**。
- `commands/` 目录是为 Claude Code 准备的，LearnBuddy **不使用**，可忽略（不必删）。
- 触发表述（在 `description` 中已写死）：涉及**大连理工大学校情 / 课程学习 / 备考 / 笔记 / 作业 / 科研 / 校园生活**的模糊求助。

### 2.3 记忆系统对接（关键差异）

LearnBuddy 有三层记忆，本包的工作流第 ⑦ 步「写入学习档案」直接落到这套记忆里：

| 层 | 位置 | 本包怎么写 |
|---|---|---|
| 用户级长期记忆 | `~/.learnbuddy/MEMORY.md` | 只写**跨项目**的长期约定（如作息偏好、常用课程） |
| 工作区日志 | `{ws}/.learnbuddy/memory/YYYY-MM-DD.md` | **追加式**记录当日学习动作与结论 |
| 工作区长期笔记 | `{ws}/.learnbuddy/memory/MEMORY.md` | 沉淀稳定事实（薄弱章节、错因类型、复考计划） |
| **学习档案（本包自有）** | `{ws}/.learnbuddy/memory/qihang/<域ID>.md` | 按域归档：薄弱点 / 错因 / 进度 / 上次结论 |

> 详见 `library/memory.md`。
> **红线**：F3 身心与社交、F5 健康与运动的敏感内容**不得写入任何记忆层**。

### 2.4 与 LearnBuddy 内置能力协同

| LearnBuddy 能力 | 本包如何用 |
|---|---|
| `present_files` | 输出产物（笔记 / 计划 / 卡组清单）后调用，让用户直接查看 |
| `show_widget` | 流程示意、概念图可直接内联渲染，无需落文件 |
| 子 agent（Task） | 跨域串联时，可让子 agent 并行处理不同域 |
| 对话检索 | 学习档案缺失时，用 `conversation_search` 回溯历史结论 |
| MCP 连接器 | B 域可接腾讯文档、F1 域可接腾讯地图等（按需） |

---

## 三、Claude Code 适配

```bash
cp -r qihang-pack ~/.claude/skills/qihang
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/
bash ~/.claude/skills/qihang/scripts/qihang.sh status
```

- 21 个斜杠命令：`/qihang`、`/qihang-dlut` + 19 个域命令
- 库外 skill 安装：`npx skills add <owner>/<repo>`（实测可用）或 `/plugin marketplace add`
- 安装位置：`.claude/skills/`（项目）或 `~/.claude/skills/`（全局）

---

## 四、其他平台

| 平台 | 做法 |
|---|---|
| **Codex** | `cp -r qihang-pack ~/.codex/skills/qihang`，无需其他改动 |
| **Gemini CLI** | `cp -r qihang-pack ~/.gemini/skills/qihang` |
| **Cursor** | 把 `SKILL.md` 摘要写进 `.cursor/rules/qihang.mdc`，并把 `library/` 作为附属文档 |
| **Copilot** | 把 `SKILL.md` 摘要写进 `.github/copilot-instructions.md` |
| **连小理**（= LearnBuddy） | 把 `domains/_registry.md` + `library/` 三份规则挂到平台的知识库；场景设计见 `qihang-scenario-design.html` |

---

## 五、平台探测（自动）

```bash
bash scripts/qihang.sh platform    # 自动探测本机已装/可装的平台与路径
```
