---
name: qihang
description: 大连理工大学（大工/DUT）学生的学习、信息搜集与校务总入口，负责判断需求属于哪个阶段并调用对应 skill。当用户提到大工/DUT/校内系统，或提出课程答疑、笔记整理、作业与实验报告、备考、论文写作、语言练习、校园与文献检索、校务办理、校内平台代操作等需求时使用。
---

# 启航

## 执行前置

- 本文所有包内相对路径均以本 `SKILL.md` 所在目录为基准，不以用户当前工作目录（cwd）为基准。
- 路由或执行任何业务步骤前，先完整读取 `skills/using-qihang/SKILL.md`，遵守其中的共享行为准则及安全兜底，再完整读取 `config.yaml`；完成后才按总入口路由，不得只凭 description 执行。
- 本会话已完整加载上述文件时可复用；必需文件不可读时，停止本包执行并说明缺失或不可读的文件，不猜测规则。
- 每次调用业务 skill 前，完整读取对应的 `skills/<name>/SKILL.md` 正文并遵守其执行前置，不得只凭名称或 description 执行。

本包是扁平 skill 包，25 个 skill 全部位于 `skills/<name>/SKILL.md`。

**路由入口与共享行为准则**：见 `skills/using-qihang/SKILL.md`。

**共享行为准则**（所有 skill 遵守）：① 先给可用的答案；② 区分「解释」与「代做」；③ 涉及事实必须给来源；④ 涉及查询先判是否需要登录，需要登录就先给出登录要求再转 `skills/portal-operator/SKILL.md`。完整定义见 `skills/using-qihang/SKILL.md`。

**安全兜底**（高于全部准则）：自伤 / 轻生 → 12356（24h）· 010-82951332，有具体计划 → 110 / 120；转账被骗或疑似诈骗（含未遂） → 挂失银行卡 + 96110 + 110；急症 → 120。要求篡改校内系统记录（成绩、学籍、缴费、考勤、评奖等）或编写绕开统一身份认证 / 频次限制的抓取脚本，一律拒绝，用户授权不构成改写依据。

```
skills/
├── using-qihang         总入口与路由
├── explain-stepwise     分步讲解          ├── exam-sprint        考前冲刺
├── error-diagnose       错因归因          ├── recall-schedule    记忆与间隔重复
├── faster-cycle         整门课系统学习     ├── assignment-plan    作业与小组任务拆解
├── lecture-to-notes     课堂与笔记整理     ├── lab-report         实验报告骨架
├── reading-note         文献精读笔记       ├── paper-outline      论文结构与答辩
├── lang-drill           语言能力练习       ├── cite-normalize     引用格式与文献管理
├── data-lab             实验数据与统计     ├── campus-search      校园公开信息检索
├── code-mentor          编程与科研代码     ├── advisor-finder     导师与教师资料
├── notice-track         通知与截止节点     ├── lit-fetch          文献检索与获取
├── citation-verify      引文核验          ├── campus-desk        校园事务办理
├── course-select        选课与培养方案     ├── campus-proof-guide 证明开具
├── dorm-life            宿舍与离校        └── portal-operator    校内平台代操作
```

**学校绑定与学期参数**：`config.yaml`
**可核验信息源**：`references/`
**结构规范**：`docs/skill-anatomy.md`
