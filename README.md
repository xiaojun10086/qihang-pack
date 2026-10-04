# 「启航」新生学习生活一体化学伴包 v3.3

> **默认先满足学生高频任务：学习 + 公开信息搜集；其余生活与科研专域作为可选扩展。**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：**LearnBuddy（= 连小理）**（单一目标平台）
> 定位：**DUT 特化规则与 skill 库（库内优先）** —— 文本资产离线可读；技能实际执行依赖宿主平台的模型与工具；
> 库内与同域降级都接不住时，可走**可选的外部桥接**（12 平台 + 五步自检，见 `library/external-bridge.md`），**外部未命中即回落原有流程**

---

## 0. 下载与快速开始

| 方式 | 一步到位 |
|---|---|
| **下载交付包（推荐）** | [`release` 分支 ZIP](https://github.com/xiaojun10086/qihang-pack/archive/refs/heads/release.zip ) |
| 在线浏览 | [github.com/xiaojun10086/qihang-pack/tree/release](https://github.com/xiaojun10086/qihang-pack/tree/release ) |
| 命令行安装 | `git clone -b release https://github.com/xiaojun10086/qihang-pack.git` |

> **`release` 分支 = 纯净交付树**（173 个文件）：只含运行所需内容 —— 无构建脚本、无内部过程文档、无本机路径。
> 下载后把目录放到 `~/.learnbuddy/skills/qihang`（用户级）或当前工作区 `.learnbuddy/skills/qihang`（项目级）即可使用，
> **无需安装任何依赖**（私密站只读为可选功能，见 `INSTALL.md` §六）。
> 开发树（含生成器链与过程文档）在 [`main` 分支](https://github.com/xiaojun10086/qihang-pack )。

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── LICENSE                     MIT 许可证全文
├── THIRD_PARTY_NOTICES.md      skill 来源说明与许可证归属（10 个 MIT 来源 + 2 项零摘录思路参考）
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── library/                  ★1 级 · skill 库（既是 skill 也是库）
│   ├── README.md             库导航页（非安装入口，无 frontmatter）
│   ├── login-policy.md       登录选择原则（A/B/C 三档）
│   ├── clarity.md            职责1：需求明确（6 槽位 + 澄清门）
│   ├── domain-review.md      职责2：域审查（锁定/越界/跨域/无域兜底）
│   ├── output-spec.md        职责3：输出规范（模板 + 简略原则）
│   └── general-fallback.md   职责4：通用兜底框架（零 skill 命中也出结果）
├── domains/                  ★2 级 · 域（20 个）
│   ├── _registry.md          域总表 + 方向自查 + 触发词消歧
│   └── <域ID>-<slug>/
│       ├── _domain.md        域定义：边界 / 触发词 / DUT 绑定点
│       └── skills/
│           └── local/<name>/SKILL.md    ★3 级 · 库内 skill（唯一通道，无需安装）
├── references/                  数据与依据
│   ├── dlut-official-sites.md      DUT 公开站信息库（142 条条目 / 表格行 162）
│   ├── dlut-login-sites.md         DUT 私密站清单（方案 A + Profile 隔离）
│   ├── dlut-field-map.md           私密站字段映射表
│   ├── dlut-url-verification.md    URL 核验台账（22 项待人工补）
│   ├── dlut-site-profiles.md       19 站画像
│   ├── browser-matrix.md           浏览器实测矩阵
│   ├── skill-compliance-audit.md   库内 skill 来源合规自检报告
│   ├── skill-selection-matrix.md   skill 选型矩阵（校园主体 → 域 → skill）
│   ├── platforms.md                平台适配表
│   └── e2e-scenarios.md            3 条端到端演示路径
├── commands/                    22 张入口卡（含学习/信息搜集默认入口与各可选域卡）
└── scripts/
    ├── selfcheck.sh             结构与计数自检
    ├── audit.sh                 安全审计 + L3 门禁实测
    ├── regress.sh               行为回归（澄清门算例 / 门禁矩阵）
    ├── aligncheck.py            全量文件级对齐审计（18 组断言）
    ├── runcheck.py              结构 / 示例 / 输出契约静态检查（不调用模型或目标平台）
    └── qihang.sh                管理脚本
```

## 2. 默认工作流（核心快路径）

```
用户需求
  ↓ 看目标 → 直接选一个匹配的学习或信息检索 skill
  ↓ 只在关键信息会改变回答时追问
  ↓ 学习任务直接辅导；事实检索给来源、日期与核验状态
```

**默认核心域**：S1–S6 学习 + R6 学生公开信息搜集。R1 文献检索为专项扩展；F1–F8 与 R2–R5 保留为可选扩展，只有相关任务出现时才路由。普通请求不强制走 8 步工作流、外部 skill 搜索、固定输出模板、自动归档或自迭代。实时信息依赖宿主提供的搜索工具；没有工具时会明确说明无法实时核验。

## 3. 完整域库（核心 + 可选扩展）

| 大类 | 域 |
|---|---|
| **核心：S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **核心：R6 信息搜集** | 学校/课程/通知/机构等公开资料，优先官方来源并标注时效 |
| **专项扩展：R 科研（R1–R5）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 |

**完整资产规模**：20 个域、92 个库内 skill。默认聚焦 7 个核心域（S1–S6、R6）；13 个生活与专项科研域保持可选。来源口径为 **80 个自建 + 12 个有来源记录**；其中 10 个基于 MIT 许可项目骨架重写，另 2 个仅参考方法论、零内容摘录。细目见 `THIRD_PARTY_NOTICES.md`。

> 92 个 skill 是提示词与流程资产的数量，不代表 92 项能力都经过目标平台实测。当前 `runcheck.py` 只做结构、示例和输出契约检查，不调用模型或 LearnBuddy。建议按高频、低风险场景分阶段验证后再扩大对外承诺。

## 4. 安装与使用

```bash
# 1) 放进 skills 目录
cp -r qihang-pack ~/.learnbuddy/skills/qihang
# 2) LearnBuddy 无需斜杠命令：22 张 commands/ 域入口卡随包提供，直接读即可
# 3) 查看状态（库内 skill 开箱即用，无任何外部依赖）
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

```bash
bash scripts/selfcheck.sh         # 结构与计数自检
bash scripts/audit.sh             # 安全审计 + L3 门禁实测
bash scripts/regress.sh 3         # 行为回归（连跑 3 轮验证确定性）
python scripts/aligncheck.py . 5  # 全量对齐审计（连跑 5 轮）
python scripts/runcheck.py . 3    # 静态契约检查（连跑 3 轮，非模型端到端测试）
python scripts/checkall.py .       # 自检单入口（静态校验器 + 计时摘要）
bash scripts/qihang.sh status     # 三级结构完整度
bash scripts/qihang.sh domains    # 20 域清单
bash scripts/qihang.sh registry   # DUT 信息库统计
bash scripts/qihang.sh new-term   # 换学期重置
```

## 5. DUT 融入

| 类型 | 文件 | 融入方式 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | **142 条**条目（表格行 162），20 个域的 `_domain.md` 各自标注绑定点 |
| 私密站 | `references/dlut-login-sites.md` | 19 个需登录站点，**方案 A 受控浏览器 + 只读**，分 L1/L2/L3 授权 |
| 校内信息搜集 | `domains/R6-info-retrieval/` | 导师/教师公开资料（`faculty.dlut.edu.cn`、`gs.dlut.edu.cn`）+ 公开信息检索与路由 |

**私密站安全边界**：访问脚本只打开用户可见的本机浏览器，不采集或输出网页内容；使用随机会话和一次性 Profile，退出后清理，不关闭用户的其他浏览器会话。用户自行查看页面，并可选择只分享回答必需的信息。L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | 在 `domains/` 下新增 `<域ID>-<slug>/` 目录，并在 `domains/_registry.md` 登记 | 1 个目录 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 本包为 **DUT 特化规则与 skill 库**：核心文本资产离线可读；实际执行依赖宿主平台的模型和工具能力，外部桥接为**可选增强**。
- 来源口径为 80 个自建 skill 与 12 个有来源记录的 skill（其中 10 个基于 MIT 项目重写、2 个仅参考方法论且零内容摘录）；详见 `THIRD_PARTY_NOTICES.md`。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。
