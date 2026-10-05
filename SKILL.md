---
name: qihang
description: 大连理工大学（大工/DUT）学生的学习、信息搜集与校务总入口，负责判断需求属于哪个阶段并调用对应 skill。当用户提到大工/DUT/校内系统，或提出课程答疑、笔记整理、作业与实验报告、备考、论文写作、语言练习、校园与文献检索、校务办理、校内平台代操作等需求时使用。
---

# 启航

本包是扁平 skill 包，25 个 skill 全部位于 `skills/<name>/SKILL.md`。

**路由入口与共享行为准则**：见 `skills/using-qihang/SKILL.md`。

```
skills/
├── using-qihang         总入口与路由
├── explain-stepwise     分步讲解          ├── exam-sprint        考前冲刺
├── error-diagnose       错因归因          ├── recall-schedule    记忆与间隔重复
├── faster-cycle         整门课系统学习     ├── assignment-plan    作业与小组任务拆解
├── lecture-to-notes     课堂与笔记整理     ├── lab-report         实验报告与课程论文骨架
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
