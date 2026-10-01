---
name: qihang-campus-desk
description: 「启航」F1 校园事务域库内 skill：先查 DUT 信息库锁定入口与电话，再给「去哪办 / 带什么 / 多久」，查不到就明说未收录。
version: 2.0.0
license: MIT
---

# 校园事务办理台

- **归属域**：`F1` 校园事务（生活类）
- **来源**：自建·DUT
- **定位**：先查 DUT 信息库锁定入口与电话，再给「去哪办 / 带什么 / 多久」，查不到就明说未收录。

## 前置（不可跳过）

1. 1 级库已完成**需求明确**（6 槽位 + 澄清门，U ≤ 5%）
2. 1 级库已完成**域审查**，确认命中本域

## 边界

- 覆盖：选课、学籍、证明打印、一卡通、报修、公寓、离校等事务办理路径
- 不覆盖：不涉及健康（→F5）；不涉及钱（→F4）

## 执行步骤

1. 查 references/dlut-official-sites.md 锁定入口
2. 判定线上线下（线上给门户链接，线下给楼宇与电话）
3. 列出所需材料清单
4. 给出办理时长与常见卡点
5. 未收录则固定回复：信息库未收录，建议访问 www.dlut.edu.cn 核实
6. 输出办理卡片

## 输出

按 `library/output-spec.md` 模板输出，默认 ≤ 6 条要点。

## DUT 绑定点

- 校园门户 https://portal.dlut.edu.cn/
- 学生工作处 https://xsc.dlut.edu.cn/
- 后勤处 https://houqin.dlut.edu.cn/
- 保卫处 https://gach.dlut.edu.cn/

需登录：
- 一卡通 https://ecard.dlut.edu.cn/
- 校园门户办事大厅
- 离校系统 http://lx.dlut.edu.cn/

## 失败与降级

库内执行不满足 → 读同目录 `../external.md` 走库外安装；仍失败 → 纯提示词模式并标注 `[已降级]`。
