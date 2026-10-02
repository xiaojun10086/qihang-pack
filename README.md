# 「启航」新生学习生活一体化学伴包 v3.0.0

> **三级结构：skill 库（1级）→ 域（2级）→ skill（3级）**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：**LearnBuddy（= 连小理）**（单一目标平台）
> 定位：**纯 DUT 特化库** —— 全部能力由库内 skill 承接，**运行时零外部依赖、零外部通道**

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── LICENSE                     MIT 许可证全文
├── THIRD_PARTY_NOTICES.md      库内 skill 的改造来源与许可证归属（12 个 MIT 仓库）
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
├── commands/                    22 张 LearnBuddy 域入口卡（库 + 校情 + 20 域）
└── scripts/
    ├── selfcheck.sh             结构与计数自检
    ├── audit.sh                 安全审计 + L3 门禁实测
    ├── regress.sh               行为回归（澄清门算例 / 门禁矩阵）
    ├── aligncheck.py            全量文件级对齐审计（18 组断言）
    ├── runcheck.py              端到端运行性（每域多触发词跑完整三级链）
    └── qihang.sh                管理脚本
```

## 2. 工作流（严格按序）

```
用户需求
  ↓ ①需求明确  library/clarity.md             6 槽位 + 澄清门（先过 §5 例外；关键槽齐全即放行）
  ↓ ②锁定域    domains/_registry.md            触发词匹配
  ↓ ③域审查    library/domain-review.md        边界复核、越界改锁
  ↓ ④锁定skill domains/<域>/_domain.md         读该域的库内 skill
  ↓ ⑤执行      domains/<域>/skills/local/      库内 skill 唯一通道，命中即用，无需安装
  ↓ ⑥输出      library/output-spec.md          ≤6 条要点 + 写学习档案
```

**核心规则：库内唯一** —— 本包为纯 DUT 特化库，全部场景均由库内 skill 承接，**不安装、不引用任何库外 skill**；库内无法覆盖的细分场景走**同域降级**并记「缺口」。

## 3. 20 个域（方向自查：学习 / 生活 / 科研全覆盖）

| 大类 | 域 |
|---|---|
| **S 学习（6）** | S1 课程答疑 ｜ S2 课堂与笔记 ｜ S3 作业与考核 ｜ S4 备考与记忆 ｜ S5 学术表达 ｜ S6 语言能力 |
| **F 生活（8）** | F1 校园事务 ｜ F2 作息与专注 ｜ F3 身心与社交 ｜ F4 财务与安全 ｜ F5 健康与运动 ｜ F6 军训与志愿 ｜ F7 升学深造 ｜ F8 求职与竞赛 |
| **R 科研（6）** | R1 文献检索与管理 ｜ R2 实验与数据 ｜ R3 科研工具与代码 ｜ R4 学术产出与投稿 ｜ R5 学术规范与伦理 ｜ R6 信息搜集与输出 |

**自查结果**：20 域 × **92 个库内 skill**（每域 4–5 个）= **自建 80 + 改造 12**。
其中 **12 个 skill 由 MIT 许可的外部最优解「骨架提取 + 重写」而来**（改造来源见 `THIRD_PARTY_NOTICES.md`），已统一格式并**DUT 特化**，运行时**零外部依赖**；其余 40 个为自建。详见 `domains/_registry.md`。

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
python scripts/runcheck.py . 3    # 运行性检查（每域跑完整三级链，连跑 3 轮）
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

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | 在 `domains/` 下新增 `<域ID>-<slug>/` 目录，并在 `domains/_registry.md` 登记 | 1 个目录 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 本包为**纯 DUT 特化库**：库内 92 个 skill 均可离线直接使用，**不依赖、不引用任何库外 skill**。
- 其中 12 个 skill 由 **MIT / Apache-2.0** 许可的开源项目「骨架提取 + 重写」而来，遵循原许可保留署名（见 `THIRD_PARTY_NOTICES.md`）；其余 40 个为自建。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。
