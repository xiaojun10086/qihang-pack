# 「启航」新生学习生活一体化学伴包 v1.1

> 1 个编排器 + **7 个能力域**（A–F 外部 Skill + **G 大连理工校情内置数据域**）。
> 可插拔、跨平台、与课程解耦、**强绑定大连理工大学官方信息库**。
> 适配：连小理 / Claude Code / Codex / Cursor / Copilot。

**配套文件**

| 文件 | 作用 |
|---|---|
| `SKILL.md` | 编排器（可直接安装） |
| `references/routing-table.md` | 全量 Skill 清单 + 12 个探测平台 + 降级链 |
| `references/dlut-official-sites.md` | **DUT 官方信息库，169 条**（G 域强制引用） |
| `references/validation-report.md` | **验收报告**（子 agent 双维度测试结论） |
| `qihang-scenario-design.html` | 赛道二设计书（可视化版） |

---

## 1. 30 秒了解

**解决什么**：新生真正的困难不是"不会用 AI"，而是**需求说不清 + 工具太散 + 学习与生活割裂 + 校情信息碎片化**。

```
发起需求 ──► 拆解 + 澄清门 ──► 路由 · 探测 · 调用 ──► 要点式输出 ──► 用户确认
   ▲              │                                                    │
   └──────────────┴──────────────── 记忆闭环 ──────────────────────────┘
              (U ≤ 5% 放行 / U > 5% 追问 ≤ 3 轮)
```

**7 个能力域**

| 域 | 名称 | 类型 | 主用 |
|---|---|---|---|
| **G** | **校情信息（DUT 强绑定）** | **内置数据** | `dlut-official-sites.md`（169 条） |
| A | 学业节奏 | 外部 Skill | `googleworkspace/cli` |
| B | 课堂消化 | 外部 Skill | `obsidian-skills` |
| C | 学科答疑 | 外部 Skill | `teach` / `math-skill` |
| D | 备考冲刺 | 外部 Skill | `structured-learning` |
| E | 学术表达 | 外部 Skill | `anthropics/skills` |
| F | 生活适应 | 外部 Skill | `deep-work` / `squire` |

---

## 2. 安装（3 步，幂等）

```bash
# 1) 放进 skills 目录
cp -r qihang-pack ~/.claude/skills/qihang

# 2) 安装斜杠命令
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/

# 3) 一键装齐能力域（只装缺的）
bash ~/.claude/skills/qihang/scripts/qihang.sh install
```

**验证与体检**

```bash
bash ~/.claude/skills/qihang/scripts/qihang.sh status     # 能力域就绪度（含 G 域）
bash ~/.claude/skills/qihang/scripts/qihang.sh registry   # DUT 信息库条目/核验统计
bash ~/.claude/skills/qihang/scripts/qihang.sh probe      # 列出缺失项
```

---

## 3. 快捷调用速查

| 入口 | 用法 |
|---|---|
| **A 自然语言** | 「我高数快挂了」「机械学院官网是啥」 |
| **B 斜杠命令** | `/qihang` `/qihang-dlut` `/qihang-kaoshi` `/qihang-biji` `/qihang-jiexi` `/qihang-zuoye` `/qihang-zhou` `/qihang-zuoxi` |
| **C 一键脚本** | `qihang.sh {probe\|install\|status\|registry\|new-term}` |

| 命令 | 域 | 一句话 |
|---|---|---|
| `/qihang` | 编排器 | 先澄清门，再路由 |
| `/qihang-dlut` | **G** | 查大工学院/校区/教务/职能部门 |
| `/qihang-kaoshi` | D | 考前 N 天怎么救 |
| `/qihang-biji` | B | 讲义/录音 → 笔记 |
| `/qihang-jiexi` | C | 这道题讲一下 |
| `/qihang-zuoye` | E | 实验报告/论文/PPT |
| `/qihang-zhou` | A | 排这周的 DDL |
| `/qihang-zuoxi` | F | 管住作息与专注 |

---

## 4. DUT 强绑定规则（G 域）

1. 命中「大连理工 / 大工 / 学院名 / 校区 / 选课 / 校历 / 图书馆 / 报修 / 心理 / 资助 / 就业」等关键词 → **必须先读** `references/dlut-official-sites.md`。
2. 命中 → 给出具体 URL + 状态标记（✅ 已核验 / ⚠️ 待核实）。
3. **未命中 → 固定回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」**。
4. **绝对禁止**凭模型记忆编造 dlut.edu.cn 下的 URL、电话或单位名。

**信息库覆盖**（160 条表格行 ｜ ✅ 显式已核验 72 条 ｜ ⚠️ 待核实 23 条 ｜ 学院类 65 条经官方章程交叉核对）

| 分节 | 内容 |
|---|---|
| §0 | 新生三大入口（SSO → 门户 → 教务） |
| §1 | 学校主站与核心门户（含全校部门电话总表） |
| §2 | 三校区（凌水主校区 / 开发区校区 / 盘锦校区） |
| §3 | 教学与学习资源（教务、研院、图书馆、网信、场馆、心理…） |
| §4 | 学部与学院（按三校区分类，含旧学部撤销映射） |
| §5 | 职能部门与服务（学工、资助、就业、保卫、后勤、校医院…） |
| §6 | 官方新媒体与 i大工 APP |
| §7 | 域名规律（供程序化匹配） |
| §8 | 22 条待核实清单（禁止直接使用） |

---

## 5. 去哪找更多 Skill（12 个探测入口）

| 平台 | 入口 | 用途 |
|---|---|---|
| **skills.sh** | https://skills.sh/ | **唯一有真实安装量** |
| **GitHub** | https://github.com/topics/agent-skills | 反馈信号最全 |
| awesomeskills.dev | https://www.awesomeskills.dev/ | 按任务场景组织 |
| officialskills.sh | https://officialskills.sh/ | 厂商官方白名单 |
| SkillsMP | https://skillsmp.com/ | 330 万条穷尽扫描 |
| claude-plugins.dev | https://claude-plugins.dev/skills | 46.9k |
| LobeHub | https://lobehub.com/skills | 334k |
| ClawHub | https://clawhub.ai/ | OpenClaw 生态 |
| StudentSuite | https://github.com/StudentSuite/awesome-skills-plugins-for-students | **158 个学生向 skill** |
| VoltAgent | https://github.com/VoltAgent/awesome-agent-skills | 1000+ 清单 |
| ComposioHQ | https://github.com/ComposioHQ/awesome-claude-skills | 自动化为主 |
| 中文清单 | https://github.com/yzfly/awesome-skills-zh | 中文场景参考 |

**扩容流程**：`skills.sh 查使用量 → GitHub API 查 stars/pushed/license → 读 SKILL.md 判可用性 → 读 scripts/ 判风险 → 通过则写入 routing-table.md`

---

## 6. 验收结论摘要（详见 `references/validation-report.md`）

| 验收项 | 判定 |
|---|---|
| 探测平台 ≥7 个 | ✅ 通过（实际 12 个） |
| 先探测后比较 | ✅ 通过 |
| 使用量数据 | ⚠️ 有条件通过（**教育类 Skill 仅 `teach` 有数 736.7K**，其余无公开数据） |
| 反馈数据 | ✅ 通过（22 仓库全量 stars/推送/issues/许可证） |
| 强绑定 DUT 信息库 | ✅ 通过（169 条） |
| 无歧义细化 | ✅ 通过 |
| 子 agent 分维度测试 | ✅ 通过（可用性 + 质量风险） |
| 发现并修正缺陷 | ✅ 通过（`googleworkspace/skills` 404 → 改 `googleworkspace/cli`） |

**残留风险**：教育垂类 Skill 普遍低星（<1k）、单作者、使用量低 → 缓解方式为「高星通用底座 + 垂类补充 + 自建编排器兜底」。

---

## 7. 目录结构

```
qihang-pack/
├── SKILL.md                     编排器 v1.1（含 G 域与 DUT 硬规则）
├── README.md                    本文件
├── config.yaml                  含 school 段（DUT 强绑定）+ 学期配置
├── qihang-scenario-design.html  赛道二设计书
├── references/
│   ├── routing-table.md         Skill 清单 + 12 平台 + 降级链
│   ├── dlut-official-sites.md   DUT 官方信息库（169 条）
│   └── validation-report.md     验收报告
├── commands/                    8 个斜杠命令（新增 qihang-dlut）
└── scripts/qihang.sh            probe/install/status/registry/new-term
```

---

## 8. 可复用性设计

| 复用维度 | 做法 | 成本 |
|---|---|---|
| 换课程 | 改 `config.yaml` → `courses` | 1 行 |
| 换学期 | `qihang.sh new-term` | 1 条命令 |
| 换能力 | `routing-table.md` 增删一行 | 1 行 |
| 扩信息库 | `dlut-official-sites.md` 追加行 | 1 行 |
| 换平台 | 全是 `SKILL.md` 标准件 | 0 |
| 换人 | 整个文件夹 `git clone` | 0 |

---

## 9. 免责与许可

- 所有外部 Skill 均为公开开源项目（检索于 2026-10-01），版权归原作者，**安装前请读源码与许可证**。
- 注意：`CC-BY-NC` 类（如 academic-research-skills）**禁止商用**；部分仓库**无 LICENSE**（study-skill、math-skill、gurukul-ai），对外发布前必须确认。
- 风险提示：`sickn33/agentic-awesome-skills`（3113 脚本、含攻击性技能）**禁止整体安装**；`exam-prep-skill` 会把本地 PDF 上传百度云端 OCR。
- 涉及教材、试卷、成绩等材料时**默认不出本机**；确需云端处理须先脱敏（删姓名、学号、校名）。
- DUT 信息库中 ⚠️ 标记的 22 条 URL 未经核验，**请勿直接使用**。
- 本包自身：MIT。
