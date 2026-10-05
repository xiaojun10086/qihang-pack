# Skill 结构规范

「启航」的每个能力都是一个 skill，位于 `skills/<skill-name>/SKILL.md`。这是唯一必需的文件。

## 目录结构

```
qihang-pack/
├── SKILL.md              # 包入口（兼容单 skill 装载）
├── plugin.json           # 插件清单，声明 "skills": "./skills"
├── config.yaml           # 学校绑定与学期参数
├── skills/               # 25 个扁平 skill
│   └── <skill-name>/
│       └── SKILL.md
├── agents/               # 人格（persona）
├── commands/             # 斜杠命令
├── docs/                 # 文档
├── references/           # 跨 skill 共享的可核验信息源
└── scripts/ .github/     # 仓库维护用，不进 release
```

## 分发分支

`release` 是给使用者直接 clone 的交付分支，只保留运行所需内容：

```
SKILL.md  plugin.json  config.yaml  .codebuddy-plugin/
skills/   references/  agents/      commands/
docs/skill-anatomy.md   LICENSE      THIRD_PARTY_NOTICES.md
```

以下属于仓库自身的维护文件，不进 release：

```
README.md  INSTALL.md  docs/getting-started.md  docs/agents.md
scripts/   .github/    .gitattributes           .gitignore
```

清单以 `scripts/sync_release.py` 的 `WHITELIST` 为唯一真相源；main 有新提交时由 `.github/workflows/sync-release.yml` 自动重建并推送。

## Frontmatter

只允许以下字段：

| 字段 | 必需 | 说明 |
|---|---|---|
| `name` | ✅ | 小写连字符，**必须与目录名一致** |
| `description` | ✅ | 第三人称「做什么」+「何时使用」，≤1024 字符 |

运行时字段一律不写 frontmatter。

## Description 写法

description 是**唯一进入上下文的字段**，决定 skill 能否被发现。

- ✅ 写「做什么」+ 触发条件：`分步讲解一个概念或一道题，从学生已有的知识出发…当用户说「没听懂」「这步怎么来的」时使用。`
- ❌ 在 description 里概括流程步骤 —— 这会诱导模型跳过正文直接照做
- ❌ 只写「帮助学习」这类无法区分的泛化描述

## 正文章节（四段式）

```markdown
# <标题>

## Overview          # 一段话说明这个 skill 做什么、边界在哪
## When to Use       # 触发条件 + NOT for（不适用场景）
## 执行流程           # 有序步骤；可含表格、判据、平台入口
## 常见误判           # 反合理化表：❌ 错误做法 → ✅ 正确做法
```

规则：

1. 正文建议 < 500 行；超过就拆成两个 skill。
2. `执行流程` 的步骤必须可执行，不写「理解用户需求」这类空话。
3. `常见误判` 至少 4 条，覆盖该 skill 最容易出现的失败模式。
4. 需要共享资料时引用 `references/` 中的文件名，**不复制内容**。
5. 不写输出模板、评分标准、自检清单 —— 直接给结果。

## 共享行为准则

所有 skill 都遵守 `skills/using-qihang/SKILL.md` 中的三条准则：先给可用的答案、区分「解释」与「代做」、涉及事实必须给来源。skill 正文不再重复声明。
