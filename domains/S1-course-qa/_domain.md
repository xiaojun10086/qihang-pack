# S1 · 课程答疑

> 域 ID `S1` ｜ 所属大类 **学习类** ｜ 目录 `domains/S1-course-qa/`

## 域边界

- **覆盖**：单点题目/概念的分步讲解、错因诊断、举一反三
- **不覆盖**：不代写作业（→S3）；不做整门课备考规划（→S4）；**不开具证明（→F1）**

## 触发词（命中任一即锁定本域）

`讲一下` ｜ `这题` ｜ `为什么` ｜ `推导` ｜ `证明` ｜ `不会做` ｜ `求解` ｜ `求证` ｜ `解释一下` ｜ `听不懂` ｜ `卡住` ｜ `怎么做` ｜ `区别` ｜ `辨析` ｜ `没听懂` ｜ `再讲一遍`

## 库内 skill（唯一通道，无需安装）

- **`explain-stepwise`** — 分步讲解（自建）
  概念问题先直接解释；解题时按需给提示和步骤，只有需要诊断时才请学生展示尝试。

- **`error-diagnose`** — 错因归因（自建）
  把做错的题按「概念 / 方法 / 计算 / 审题」四类归因，输出错因清单与再练顺序，不代做。

- **`socratic-qa`** — （改造自外部 MIT 最优解 + DUT 特化）
  不直接给答案，用五类渐进提问引导自悟；卡壳 3 轮自动降级分步讲解

- **`prereq-bridge`** — 先修补桥（自建）
  当卡点不在本题而在前置知识断层时，先回溯定位断点、只补一节最小前置，再回到原题继续。

- **`concept-contrast`** — 易混辨析（自建）
  把一组常被混淆的概念、公式或定理放进同一张多维度对照表，逐项给出差异与适用条件，用于考前快速区分。

## DUT 绑定点

**公开站（无需登录）**
- 教务处 https://teach.dlut.edu.cn/
- 数学科学学院 https://math.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- 综合教务系统 http://jxgl.dlut.edu.cn/student/home （考试安排、培养方案）

## 可选外部参考

外部 skill 搜索不是日常答疑前置条件。仅当用户明确要求外部资源，或宿主缺少完成特定任务所需的工具时，才按需参考 `library/external-bridge.md`；不得因普通解释没有精确模板而中断作答。

**检索词**：课程答疑 / 分步讲解 / 苏格拉底式提问
**平台检索式（英文，≤3 词）**：`socratic tutor`
**适配词表（英文，候选 name+description 命中任一即算适配）**：`socratic` ｜ `tutor` ｜ `explain` ｜ `learning`
**指定检索平台（只查这几个，不穷举）**：`skills.sh` ｜ `cultofclaude.com` ｜ `skillhub.club`（共 3 个）

**已核验候选**（仓库数据 2026-10-02 抓取 ｜ 链接 2026-10-03 双通道核验）

| 候选仓库 | 许可 | ★ | 综合分 | 可用性判定 |
|---|---|---|---|---|
| `bevibing/socrates-skill` | MIT | 326 | 4.25 | ✅ 最优解 |
| `mattpocock/skills` | MIT | 273,959 | 4.10 | ⚠️ 不适配 DUT |
| `bevibing/tutor-skills` | MIT | 1,313 | 3.95 | 备选 |

候选信息仅供维护者参考，不是运行期依赖或用户答疑的必经步骤。

## 执行顺序

0. **先判红线**（见下文 `## ⚠️ 红线` 节）—— 命中则**拒绝代做并给合规学习替代**（追问口径见 `library/clarity.md` §7）
1. 清晰单点问题直接处理；复杂或有歧义时才参照 `library/clarity.md` 与 `library/domain-review.md`。
2. 按任务择一：`explain-stepwise`（概念/解题）、`error-diagnose`（错因）、`socratic-qa`（互动引导）、`prereq-bridge`（先修断层）、`concept-contrast`（概念辨析）。
3. 直接讲清当前问题；需要结构化产出时参考 `library/output-spec.md`。只在用户要求保存偏好或长期记录时参考 `library/skill-evolution.md` / `library/memory.md`。

## ⚠️ 红线（不得绕过）

- **不代做**：只给讲解与同类题，**不产出可直接提交的答案**
