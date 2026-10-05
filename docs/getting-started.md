# 快速上手

## 安装

```bash
# 用户级（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# 或项目级
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang
```

插件方式：包根含 `plugin.json`，声明 `"skills": "./skills"`，支持 skill 目录发现的主机可直接装载。

## 用法

直接用自然语言说需求，**不需要记分类名，也不需要斜杠命令**。

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

```
学习 ──→ 巩固 ──→ 产出 ──→ 数据代码 ──→ 检索 ──→ 校务
```

包内 `using-qihang` 是入口，负责把你的说法路由到下面六个阶段的 skill；多数时候不必点名它。

- **学习**：`explain-stepwise` `error-diagnose` `faster-cycle` `lecture-to-notes` `reading-note` `lang-drill`
- **巩固**：`exam-sprint` `recall-schedule`
- **产出**：`assignment-plan` `lab-report` `paper-outline` `cite-normalize`
- **数据代码**：`data-lab` `code-mentor`
- **检索**：`campus-search` `advisor-finder` `notice-track` `lit-fetch` `citation-verify`
- **校务**：`campus-desk` `course-select` `campus-proof-guide` `dorm-life` `portal-operator`

## 三条共享行为准则

1. **先给可用的答案** —— 结论放最前面，只追问会改变答案的信息。
2. **区分「解释」与「代做」** —— 讲方法、给结构、给路径可以；不产出用于提交的成品。
3. **涉及事实必须给来源** —— 校内信息优先官方来源，附出处与日期，不编造。

## 安全兜底

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗 | 挂失银行卡 + **96110** + **110** |
| 急症、外伤 | **120** |

## 配置

`config.yaml` 是唯一需要按学期修改的文件：学校绑定、学期、修读课程。个人信息留空表示未知，不会被当作事实使用。
