# S3 · 作业与考核

> 域 ID `S3` ｜ 所属大类 **学习类** ｜ 目录 `domains/S3-assignment/`

## 域边界

- **覆盖**：作业规划、实验报告结构、课程设计拆解、格式规范
- **不覆盖**：不代写（只给结构与自查）；不投期刊（→R4）；数据造假 → `R5`

## 触发词（命中任一即锁定本域）

`作业` ｜ `实验报告` ｜ `课程设计` ｜ `平时分` ｜ `大作业` ｜ `论文作业` ｜ `提交` ｜ `报告怎么写` ｜ `自查`

## 库内 skill（唯一通道，无需安装）

- **`lab-report`** — 实验报告脚手架（自建）
  按 IMRAD 给实验报告骨架，分配各节字数，并给出自查清单；正文由学生自己写。

- **`assignment-plan`** — 作业拆解（自建）
  把大作业/课程设计拆成里程碑与工作量，排期并标风险项，不代写正文。

- **`imrad-scaffold`** — （改造自外部 MIT 最优解 + DUT 特化）
  课程论文 / 毕设的 IMRAD 四节骨架 + 对抗性自审；想法与数据由用户提供，正文不代写

- **`code-assignment`** — 编程作业自查（自建）
  面向编程作业的自查清单：编译、边界、复杂度、可读性与引用声明逐项自检，只给检查项与定位提示，不代写代码。

- **`team-project`** — 小组作业协作（自建）
  把小组作业拆成可认领的任务块与里程碑，生成分工表、进度看板与协作纪要模板，面向需要多人协作的本科生。

## DUT 绑定点

**公开站（无需登录）**
- 教务处 https://teach.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- 综合教务系统 http://jxgl.dlut.edu.cn/student/home （作业与成绩）

## 外部承接（库内与同域降级都接不住时才启用）

> **第三档入口**：先读 `library/external-bridge.md`（触发条件 + 五步自检 + 许可门禁），
> 再按 `references/external-sources.md` §1 的顺序检索 **12 个平台**。
> **库内优先不变**：本域仍先用库内 skill；外部桥接只在**同域降级也接不住**时启用。
> **禁止编造**外部链接（硬规则 2）；候选仓库已逐个双通道核验（2026-10-03）。

**检索词**：作业 / 实验报告 / 团队项目
**平台检索式（英文，≤3 词）**：`imrad paper writing`
**适配词表（英文，候选 name+description 命中任一即算适配）**：`imrad` ｜ `assignment` ｜ `report` ｜ `academic`
**指定检索平台（只查这几个，不穷举）**：`skills.sh` ｜ `cultofclaude.com` ｜ `skillhub.club`（共 3 个）

**已核验候选**（仓库数据 2026-10-02 抓取 ｜ 链接 2026-10-03 双通道核验）

| 候选仓库 | 许可 | ★ | 综合分 | 可用性判定 |
|---|---|---|---|---|
| `kgraph57/paper-writer-skill` | MIT | 58 | 3.50 | ✅ 最优解 |
| `vishalsachdev/canvas-mcp` | MIT | 270 | 4.10 | ⚠️ 不适配 DUT |
| `anthropics/skills` | 未声明 | 179,334 | 2.85 | ⛔ 许可证缺失，不入围 |

**本域结论**：可用首选：`kgraph57/paper-writer-skill`（MIT）。

## 执行顺序

0. **先判红线**（见下文 `## ⚠️ 红线` 节）—— 命中则**拒绝并给合规替代**，**不追问**
1. 1 级库完成**需求明确**（`library/clarity.md`）：先过 §5 例外，未命中的再按关键槽与 `U` 判定
2. 1 级库完成**域审查**，确认命中 `S3`（`library/domain-review.md`）
3. 用**库内 skill**（库内 5 个：`lab-report` · `assignment-plan` · `imrad-scaffold` · `code-assignment` · `team-project`；按需求择一）执行
4. 按 `library/output-spec.md` 输出，并写入学习档案
5. 按 `library/skill-evolution.md` 记录本域习惯，并**只在可改段内**做非结构性自迭代（不改红线 / 输出契约 / 任何事实；不满足触发条件则不迭代）
6. **外部桥接（最后的兜底）**：库内与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**。

## ⚠️ 红线（不得绕过）

- **不代写正文**（只给 IMRAD 骨架与自查）
- **不编造实验数据** —— 属学术不端，须改锁并提示 `R5`
- **不代操作教学平台**（不代提交作业/报告）

