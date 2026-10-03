# 外部 skill 来源清单（12 平台）· 复核 2026-10-03

> **用途**：`library/external-bridge.md`**§3 检索顺序**的入口表。
> 只在**库内 skill 与同域降级都接不住**时才启用 —— 本表**不取代**库内通道。
> **与 v3.0.0 去库外化的关系**：本表只登记**平台入口**，**不含**任何 per-domain 外部 skill 文件；
> 各域的外部候选写在 2 级 `_domain.md` 的 `## 外部承接` 段（**1 级 / 2 级承载，3 级不落**）。
> **核验方式**：三通道交叉（系统解析 ×5 ｜ AliDNS DoH ｜ DNSPub DoH）
> ＋ TCP 80/443 端口探测 ＋ 双协议实抓（HTTP / HTTPS 各重试 3 次）。
> **本轮结论：下表 12 个入口全部实测 200 可达**（2026-10-03）。

| # | 平台 | 检索入口 | 规模 | 使用量 | 反馈 | 局限 | 实测 |
|---|---|---|---|---|---|---|---|
| 1 | **skills.sh** | https://skills.sh/ | 1.5M+ | 有 installs | 无 | 只有流行度，无质量分级 | 200 |
| 2 | **GitHub Topics** | https://github.com/topics/agent-skills | 2.3 万仓库 | 无 | 有 stars / issues | 无使用量 | 200 |
| 3 | awesomeskills.dev | https://www.awesomeskills.dev/ | 4.1 万 | 有 | 无 | 教育场景空白 | 200 |
| 4 | officialskills.sh | https://officialskills.sh/ | 660 | 无 | 仅更新时间 | 只收厂商官方 | 200 |
| 5 | SkillsMP | https://skillsmp.com/ | 3.2M+ | 无 | 部分 | 无质量分级 | 200 |
| 6 | claude-plugins.dev | https://claude-plugins.dev/skills | 4.6 万 | 口径不明 | 部分 | 自动索引，无人工把关 | 200 |
| 7 | LobeHub Skills | https://lobehub.com/skills | 33 万+ | 口径不明 | 无 | 无教育分类 | 200 |
| 8 | ClawHub | https://clawhub.ai/ | 未公开 | 口径不明 | 无 | 特定生态 | 200 |
| 9 | StudentSuite | https://github.com/StudentSuite/awesome-skills-plugins-for-students | 158 | 无 | 有 | 面向境外课程体系 | 200 |
| 10 | VoltAgent 清单 | https://github.com/VoltAgent/awesome-agent-skills | 1000+ | 无 | 有 | 纯清单，非 skill 本体 | 200 |
| 11 | ComposioHQ 清单 | https://github.com/ComposioHQ/awesome-claude-skills | 1000+ | 无 | 有 | 偏自动化方向 | 200 |
| 12 | 中文清单（yzfly） | https://github.com/yzfly/awesome-skills-zh | 精选 | 无 | 有 | 活跃度低 | 200 |

## 一、检索顺序（照此办，不要跳步）

```
① 先用「域检索词」在 1 / 2 / 5 号平台做**语义检索**（覆盖面最大）
② 命中候选 → 进 GitHub 取 stars / license / pushed_at / archived（3 / 9 / 10 / 11 / 12 号多为清单，用于交叉发现）
③ 读候选的 SKILL.md 判**可用性**（有无标准 frontmatter、是否只是清单/占位）
④ 读候选的 scripts/ 判**脚本风险**（联网下载并执行、提权、批量删除、外发凭证一律判不合格）
⑤ 过 §4 五步自检 → 全过才可外接；任一不过 → 换候选或回落
```

## 二、许可红线（**硬**，与 `THIRD_PARTY_NOTICES.md` 同源）

- `MIT / Apache-2.0 / BSD / CC0 / ISC` → **合规 = 5**：可外部调用，**改造后须署名**。
- `GPL / AGPL / LGPL / CC-BY-NC` → **合规 = 2**：**只允许外部调用，禁止摘录任何内容进本包**。
- **无 LICENSE / 无法识别** → **合规 = 0**：**禁止使用**（不入围，不得作为候选）。
- **任何情况下都禁止把外部 skill 的正文复制进本包**；本包只**指向**外部入口。

## 三、与信息库的关系

- 本表的链接**必须真实可达**（硬规则 2：禁止编造 URL）→ 每次改动后跑
  `python scripts/extskill.py .` 复核（含可达性与登记一致性）。
- 各域「已核验候选」的仓库清单以 **2 级 `_domain.md` 的 `## 外部承接`** 为准；
  本表只维护**平台入口**，不重复登记候选仓库。

## 四、已核验候选仓库池（**登记唯一真相源**）

> **规则**：2 级 `_domain.md` 的 `## 外部承接` 段里出现的**每一个** `owner/repo`，
> 都必须在本节出现 —— 否则 `scripts/extskill.py` 判 FAIL（防编造）。
> **核验方式**：双通道（`HTTPS GET github.com/<owner>/<repo>` ＋ `git ls-remote`），
> **核验日期 2026-10-03，38/38 全部存在**。
> 许可列取自各仓库 LICENSE（抓取日 2026-10-02）；`未声明` = 仓库无 LICENSE → **合规 = 0，禁止使用**。

| # | owner/repo | 许可 | 合规 | 用途 |
|---|---|---|---|---|
| 1 | `googleworkspace/cli` | Apache-2.0 | 5 | F1 候选 |
| 2 | `vishalsachdev/canvas-mcp` | MIT | 5 | F1 / S3 候选 |
| 3 | `alirezarezvani/claude-skills` | MIT | 5 | F2 最优解 |
| 4 | `eddiebelaval/squire` | MIT | 5 | F2 备选 |
| 5 | `jakedahn/pomodoro` | MIT | 5 | F2 备选 |
| 6 | `Haadhi76/SOP_Consultant` | MIT | 5 | F7 候选 |
| 7 | `tydev-new/10xcolleges` | MIT | 5 | F7 候选 |
| 8 | `cabbage2000-lab/paper-tutor-skills` | 未声明 | 0 | F7 / R4 ⛔ 不入围 |
| 9 | `Paramchoudhary/ResumeSkills` | MIT | 5 | F8 最优解 |
| 10 | `sourikduttanyu/interview-prep` | MIT | 5 | F8 备选 |
| 11 | `Lucaswangzcx/literature-downloader-skill` | MIT | 5 | R1 最优解 |
| 12 | `WenyuChiou/zotero-skills` | MIT | 5 | R1 备选 |
| 13 | `xwmxcz/papers-skill` | MIT | 5 | R1 备选 |
| 14 | `K-Dense-AI/scientific-agent-skills` | MIT | 5 | R2 最优解 |
| 15 | `K-Dense-AI/scientific-agents` | MIT | 5 | R2 备选 |
| 16 | `openai/skills` | 未声明 | 0 | R2 ⛔ 不入围 |
| 17 | `mattpocock/skills` | MIT | 5 | R3 / S1 候选 |
| 18 | `obra/superpowers` | MIT | 5 | R3 备选 |
| 19 | `egouilliard-leyton/python-tutor-skill` | MIT | 5 | R3 备选 |
| 20 | `Gabberflast/academic-pptx-skill` | MIT | 5 | R4 / S5 最优解 |
| 21 | `Imbad0202/academic-research-skills` | 未声明 | 0 | R4 / S5 ⛔ 不入围 |
| 22 | `NeoLabHQ/context-engineering-kit` | GPL-3.0 | 2 | R5 唯一候选（**仅外部调用**） |
| 23 | `bevibing/socrates-skill` | MIT | 5 | S1 最优解 |
| 24 | `bevibing/tutor-skills` | MIT | 5 | S1 / S2 备选 |
| 25 | `kepano/obsidian-skills` | MIT | 5 | S2 最优解 |
| 26 | `0x-man/mindmap-skill` | MIT | 5 | S2 备选 |
| 27 | `kgraph57/paper-writer-skill` | MIT | 5 | S3 最优解 |
| 28 | `anthropics/skills` | 未声明 | 0 | S3 ⛔ 不入围 |
| 29 | `hluaguo/learn-faster-kit` | MIT | 5 | S4 最优解 |
| 30 | `GlacierXiaowei/structured-learning-skill` | Apache-2.0 | 5 | S4 备选 |
| 31 | `lowwwbank/anything-to-course` | MIT | 5 | S4 备选 |
| 32 | `hameefy/claude-latex-skill` | MIT | 5 | S5 备选 |
| 33 | `YANZHANLIN/ielts-claude-skills` | MIT | 5 | S6 最优解 |
| 34 | `tianmind-studio/english-coach` | MIT | 5 | S6 备选 |
| 35 | `flysheep-ai/education-skills` | MIT | 5 | S6 备选 |
| 36 | `ghutchis/chem-skill` | MIT | 5 | 化学方向备选（未落域） |
| 37 | `googlarz/math-skill` | 未声明 | 0 | ⛔ 不入围 |
| 38 | `somenssarkar/gurukul-ai` | 未声明 | 0 | ⛔ 不入围 |
