# LearnBuddy / WorkBuddy 适配表

> 「启航」是**面向 LearnBuddy / WorkBuddy 单一目标平台**的一体化 skill 包。
> 所有内容都是 `SKILL.md` 标准件，装载后靠 `description` 自动发现。
> 平台差异只体现在 **①安装位置 ②发现方式 ③入口 ④记忆系统** 四处。

## 一、总览

| 项 | 内容 |
|---|---|
| 目标平台 | **LearnBuddy / WorkBuddy**（唯一适配目标，一等公民） |
| 安装位置 | 用户级 `~/.learnbuddy/skills/qihang/`<br>项目级 `{ws}/.learnbuddy/skills/qihang/` |
| 发现方式 | 读 `SKILL.md` 的 `description` 自动发现 |
| 入口 | **自然语言**（无需斜杠命令）；`commands/` 为域入口卡，供人工检索 / 插件装载 |
| 记忆系统 | `~/.learnbuddy/MEMORY.md` + `{ws}/.learnbuddy/memory/` + 本包按域档案 |
| 插件清单 | `.codebuddy-plugin/plugin.json` |
| 场景名 | 赛道二场景名「**连小理**」= LearnBuddy（同一平台，非独立平台） |

> **适配范围**：本包只对 LearnBuddy / WorkBuddy 做适配与承诺。
> 其他 agent 只要能读 `SKILL.md` 即可装载使用，但**本包不提供其适配承诺**
> （`commands/` 是 LearnBuddy 域入口卡，不是其他平台的斜杠命令格式）。

---

## 二、安装

```bash
# 用户级（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# 或项目级（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang

# 就绪度自检
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

**插件方式**：包根已含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别装载。

---

## 三、发现与调用

- LearnBuddy 通过 **SKILL.md 的 `description`** 自动判定何时加载，**无需斜杠命令**。
- 触发表述（在 `description` 中已写死）：涉及**大连理工大学校情（学院/校区/选课/校历/职能部门/联系方式）、
  大学课程学习、备考复习、课堂笔记、作业与实验报告、科研文献、作息专注、升学求职**的**模糊求助**。
- `commands/` 是 **LearnBuddy 域入口卡**（22 张 = 库入口 1 + 校情 1 + 20 域），
  用自然语言说需求即可命中对应域，无需输入命令。

---

## 四、记忆系统对接（关键差异）

LearnBuddy 有三层记忆，本包的工作流第 **⑥** 步「输出 / 归档」直接落到这套记忆里：

| 层 | 位置 | 本包怎么写 |
|---|---|---|
| 用户级长期记忆 | `~/.learnbuddy/MEMORY.md` | 只写**跨项目**的长期约定（如作息偏好、常用课程） |
| 工作区日志 | `{ws}/.learnbuddy/memory/YYYY-MM-DD.md` | **追加式**记录当日学习动作与结论 |
| 工作区长期笔记 | `{ws}/.learnbuddy/memory/MEMORY.md` | 沉淀稳定事实（薄弱章节、错因类型、复考计划） |
| **学习档案（本包自有）** | `{ws}/.learnbuddy/memory/qihang/<域ID>.md` | 按域归档：薄弱点 / 错因 / 进度 / 上次结论 |

> 详见 `library/memory.md`。
> **红线**：F3 身心与社交、F5 健康与运动的敏感内容**不得写入任何记忆层**。

---

## 五、与 LearnBuddy 内置能力协同

| LearnBuddy 能力 | 本包如何用 |
|---|---|
| `present_files` | 输出产物（笔记 / 计划 / 卡组清单）后调用，让用户直接查看 |
| `show_widget` | 流程示意、概念图可直接内联渲染，无需落文件 |
| 子 agent（Task） | 跨域串联时，可让子 agent 并行处理不同域 |
| 对话检索（`conversation_search`） | 学习档案缺失时，回溯历史结论 |
| MCP 连接器 | F1 域可接腾讯地图、文档类可接腾讯文档等（按需） |

---

## 六、库内 skill：唯一通道（无需安装）

本包为**纯 DUT 特化库**，运行时**只指向本地库内 skill**：

| 项 | 说明 |
|---|---|
| 通道 | **库内优先** —— 缺口时可选外接（12 平台 + 五步自检），未命中即回落 |
| 规模 | `domains/*/skills/local/` 下 **92 个**（自建 80 + 由 MIT/Apache 许可外部最优解重写 12） |
| 依赖 | **核心能力零外部依赖**，离线可用 |
| 缺口 | 库内无法覆盖的细分场景走**同域降级**并记「缺口」，不引入库外通道 |

> **构建期素材红线**：GPL / AGPL / CC-BY-NC / 无 LICENSE 一律**只做思路参考，不得复制内容进包**
> （见 `references/skill-compliance-audit.md`）。素材经「骨架提取 + 重写 + DUT 特化」后成为本包自有 skill。

---

## 七、平台探测（自动）

```bash
bash scripts/qihang.sh platform    # 探测本机 LearnBuddy 安装位置与就绪度
```
