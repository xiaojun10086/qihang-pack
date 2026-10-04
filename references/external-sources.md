# 外部 skill 来源清单（**20 平台**）· 复核 2026-10-03（v3.3.1 扩充）

> **用途**：`library/external-bridge.md`**§3 检索顺序**的入口表。
> 只在**库内 skill 与同域降级都接不住**时才启用 —— 本表**不取代**库内通道。
> **与 v3.0.0 去库外化的关系**：本表只登记**平台入口**，**不含**任何 per-domain 外部 skill 文件；
> 各域的外部候选写在 2 级 `_domain.md` 的 `## 外部承接` 段（**1 级 / 2 级承载，3 级不落**）。
> **核验方式**：三通道交叉（系统解析 ×5 ｜ AliDNS DoH ｜ DNSPub DoH）
> ＋ TCP 80/443 端口探测 ＋ 双协议实抓（HTTP / HTTPS 各重试 3 次）。
> **本轮结论：下表 20 个入口全部实测 200 可达**（2026-10-03；扩充的 8 个为新收录）。
> 同批候选里 **`claudeskills.wiki` 实测不可达（连接超时）→ 不予收录**（硬规则 2：不登记打不开的入口）。

| # | 平台 | 检索入口 | 规模 | 使用量 | 质量门禁 | 局限 | 核验日 |
|---|---|---|---|---|---|---|---|
| 1 | **skills.sh** | https://skills.sh/ | 1.5M+ | ✅ installs | 无 | 只有流行度，无质量分级 | 2026-10-03 |
| 2 | **Skillselion** | https://skillselion.com/ | 62,300+ skills ｜ 12,700+ 市场 | ✅ **installs 追踪** | 无 | 偏 Claude Code 生态 | 2026-10-03 |
| 3 | **Cult of Claude** | https://cultofclaude.com/ | 32,198 skills ｜ 17,499 agents | 无 | ✅ **评分门禁**（未过线不收录） | 爬公开 GitHub，非人工 | 2026-10-03 |
| 4 | **Agensi** | https://www.agensi.io/ | 200+ | 无 | ✅ **8 点安全扫描**（逐个过审） | 目录小；含付费条目 | 2026-10-03 |
| 5 | **SkillHub** | https://skillhub.club/ | 7,000+ | 无 | ✅ **AI 评估打分** | 中文站，覆盖偏国内场景 | 2026-10-03 |
| 6 | **ClaudeSkills.info** | https://claudeskills.info/ | 658+ | 无 | ✅ 社区评审 | 数量少；无付费层 | 2026-10-03 |
| 7 | **claudemarketplaces.com** | https://claudemarketplaces.com/ | 2,500+ 市场 | 无 | 无 | 是「市场目录」，不是 skill 目录 | 2026-10-03 |
| 8 | **officialskills.sh** | https://officialskills.sh/ | 660 | 无 | ✅ 仅收厂商官方 | 只收官方，覆盖窄 | 2026-10-03 |
| 9 | **addyosmani/agent-skills** | https://github.com/addyosmani/agent-skills | 精选集 | 无 | ✅ 人工精选（生产级） | 偏工程方向 | 2026-10-03 |
| 10 | **vercel-labs/skills** | https://github.com/vercel-labs/skills | 官方工具链 + 索引 | 无 | ✅ Vercel 维护 | 是工具 + 索引，非纯目录 | 2026-10-03 |
| 11 | **SkillsMP** | https://skillsmp.com/ | 3.2M+ | 无 | 无 | 无质量分级，需自行审计 | 2026-10-03 |
| 12 | **LobeHub Skills** | https://lobehub.com/skills | 33 万+ | 口径不明 | 无 | 无教育分类 | 2026-10-03 |
| 13 | **claude-plugins.dev** | https://claude-plugins.dev/skills | 4.6 万 | 口径不明 | 无 | 自动索引，无人工把关 | 2026-10-03 |
| 14 | **awesomeskills.dev** | https://www.awesomeskills.dev/ | 4.1 万 | ✅ | 无 | 教育场景空白 | 2026-10-03 |
| 15 | **ClawHub** | https://clawhub.ai/ | 未公开 | 口径不明 | 无 | 特定生态（OpenClaw） | 2026-10-03 |
| 16 | **GitHub Topics** | https://github.com/topics/agent-skills | 2.3 万仓库 | 无 | ✅ stars / issues | 无使用量 | 2026-10-03 |
| 17 | **VoltAgent 清单** | https://github.com/VoltAgent/awesome-agent-skills | 1000+ | 无 | ✅ | 纯清单，非 skill 本体 | 2026-10-03 |
| 18 | **ComposioHQ 清单** | https://github.com/ComposioHQ/awesome-claude-skills | 1000+ | 无 | ✅ | 偏自动化方向 | 2026-10-03 |
| 19 | **StudentSuite** | https://github.com/StudentSuite/awesome-skills-plugins-for-students | 158 | 无 | ✅ | 面向境外课程体系 | 2026-10-03 |
| 20 | **中文清单（yzfly）** | https://github.com/yzfly/awesome-skills-zh | 精选 | 无 | ✅ | 活跃度低 | 2026-10-03 |
## 一、命中规则：**每域只查指定的 2–3 个平台**（v3.3.1 收紧）

> **为什么收紧**：20 个平台逐个穷举既慢又易发散。改为**每域预指定 2–3 个平台**，
> 查完即止 —— **指定平台内没有合格候选，就按「无 skill 流程」回落**（见 §三），
> **不换平台再找、不扩大到全表**。

> **例外（1 域）**：`R6-info-retrieval` 不指定 skill 平台 —— 本域直查第一方官方来源
> （教师主页 / 部门电话 / 通知公告），外部 skill 平台不是本域前置条件
> （见 `domains/R6-info-retrieval/_domain.md` §工具与来源）。其余 19 域一律照本条执行。
> 该例外由 `scripts/extskill.py` §6 断言：豁免集合与本行一致，多一个少一个都判 FAIL。

```
① 读该域 _domain.md 的「## 外部承接 → 指定检索平台（2–3 个）」—— 只查这几个
   （S1-course-qa 该段名为「## 可选外部参考」，指定平台位相同；R6 见上方例外）
② 在指定平台内用「域检索词」检索；命中候选 → 进 GitHub 取 stars / license / pushed_at / archived
③ 读候选 SKILL.md 判可用性；读 scripts/ 与正文判「脚本与指令风险」（见 external-bridge §4）
④ 过 external-bridge §4 五步自检 → 全过才可外接
⑤ **指定平台内无合格候选 → 终止检索，按「无 skill 流程」回落**（不是失败，是预期路径）
```

**检索上限（硬）**：每域**最多 2 轮**检索、**最多评估 3 个候选**；超出即回落。
理由：外接是「兜底」不是「主路径」，时间与上下文必须封顶。

**检索式写法（v3.3.1 实测补，否则必然 0 命中）**

- 用**英文关键词**，**≤3 个词**；中文长句与 5 词以上会被 AND 叠加成空结果。
  · ✅ `claude skill ielts tutor`（少词）　· ✅ `literature review`（更稳）
  · ❌ `帮我找一个能练雅思口语的 skill`（中文长句）　· ❌ `claude skill english ielts tutor speaking practice`（词过多）
- 同义词用 **OR** 而不是空格：`sop OR application`。
- 每域的**检索式**写在 `_domain.md` 的「**平台检索式**」行，直接照抄即可。

**两段分工（v3.3.1 澄清）**

| 角色 | 谁承担 | 干什么 |
|---|---|---|
| **发现入口** | 本域**指定的 2–3 个平台** | 先在这里检索；命中候选名 → 下一步 |
| **元数据与核验源** | GitHub（stars / license / pushed_at / archived）＋ Skillselion（installs） | 取**可核验字段**，跑五步自检；平台自身不提供 LICENSE 判定 |

> 只说「在 skills.sh 里找到了」**不算证据** —— 必须有 GitHub 侧字段（LICENSE / 最近推送）才能过自检。

## 二、按域指定的平台（唯一真相源）

| 域类 | 指定平台（2–3 个） | 选择理由 |
|---|---|---|
| **S1–S6（学习类）** | `skills.sh` ｜ `cultofclaude.com` ｜ `skillhub.club` | 学习垂类重**质量信号 + 中文适配**：installs 看热度、评分门禁看质量、中文站看国内可用性 |
| **F1–F8（生活类）** | `skills.sh` ｜ `agensi.io` | 生活类常涉**个人数据** → 优先**逐个安全过审**（Agensi 8 点扫描）的目录；`skills.sh` 补热度和覆盖 |
| **已复核无候选的 F3/F4/F5/F6** | `agensi.io` ｜ `officialskills.sh` | 敏感域只要**最保守**的两个（安全扫描 + 厂商官方）；已复核确认无候选，查 2 个即可 |
| **R1–R6（科研类）** | `skillselion.com` ｜ `officialskills.sh` ｜ `skillsmp.com` | 科研重**厂商官方与安装量**：installs 追踪 + 官方目录 + 大目录负责「发现」 |

> 各域的**具体指定**写在 2 级 `_domain.md` 的 `## 外部承接` 段（`scripts/extskill.py` 会断言
> 「2–3 个」且「必须在本表 20 个之内」—— 两者任一不符即 FAIL，防编造平台）。

## 二、许可红线（**硬**，与 `THIRD_PARTY_NOTICES.md` 同源）

- `MIT / Apache-2.0 / BSD / CC0 / ISC` → **合规 = 5**：可外部调用，**改造后须署名**。
- `GPL / AGPL / LGPL / CC-BY-NC` → **合规 = 2**：**只允许外部调用，禁止摘录任何内容进本包**。
- **无 LICENSE / 无法识别** → **合规 = 0**：**禁止使用**（不入围，不得作为候选）。
- **任何情况下都禁止把外部 skill 的正文复制进本包**；本包只**指向**外部入口。

## 三、「没有找到」怎么判（= 按无 skill 流程处理）

在**指定平台内**检索后，出现下列任一情形即判**未命中**，终止检索并**按「无 skill 流程」**（`library/general-fallback.md` 的六步框架 / 纯提示词模式）输出：

1. 指定平台内**检索不到**与该域核心动作对应的 skill；
2. 检索到但**合规 = 0**（无 LICENSE / 无法识别许可）；
3. 检索到但**五步自检任一不过**（含 §4 第 4 项「脚本与指令风险」）；
4. 候选全部为**清单仓库 / 占位仓库**（无标准 `SKILL.md`）；
5. 候选与**适配词表**零命中（`name + description` 一个词都命不中 → 判不适配）；
6. 已到**检索上限**（每域 ≤2 轮 / 评估 ≤3 个候选）仍未拿到合格候选。

> **未命中不是失败** —— 本包的承诺是「任何输入都能跑出有效结果」，回落路径必须能出结果。

## 四、全局反向词表（命中任一即淘汰 · 第二道闸）

> **为什么需要它（v3.3.1 真机演练查出）**：正向词会**偶然命中** —— 演练中一个
> **医学图像分割**仓库的描述里顺带写着 "collection of **literature reviews**"，
> 于是被误判成 R1「文献检索」的合格候选。**单一正向匹配不足以判定适配。**
> 判据改为：**正向词 ≥1 命中 且 反向词 0 命中**。

| 反向词（英文，小写匹配） | 指向的域外场景 |
|---|---|
| `medical` `clinical` `patient` `segmentation` `diagnosis` | 医疗 / 影像 / 诊断 |
| `blockchain` `crypto` `trading` `stock` `forex` | 加密 / 交易 / 证券 |
| `game` `gaming` `gacha` | 游戏 |
| `dating` `ecommerce` `shop` `ads` `marketing` `seo` | 社交 / 电商 / 营销 |
| `codebase` `repository` `refactor` `leetcode` | 代码库 / 刷题（非课程答疑） |

> 反向词表是**全局的**（不按域分），因为上表列的都是**本包 20 个域之外**的场景；
> 某域确有例外时，在该域「适配词表」里显式列出该词即可（域内优先于全局）。

## 五、与信息库的关系

- 本表的链接**必须真实可达**（硬规则 2：禁止编造 URL）→ 每次改动后跑
  `python scripts/extskill.py .` 复核（含可达性与登记一致性）。
- 各域「已核验候选」的仓库清单以 **2 级 `_domain.md` 的 `## 外部承接`** 为准；
  本表只维护**平台入口**，不重复登记候选仓库。

## 七、真机演练记录（亲测 · 2026-10-03）

> 工具：`bridge_probe.py --live`（位于 **build 侧 `_build/` 内，不随包分发**，故此处不写其完整路径）。
> 它读本域「平台检索式 / 适配词表」**真发检索请求**，对候选跑五步自检，打印档位结论。

| 域 | 指定平台数 | 演练结论 |
|---|---|---|
| `S6-language` | 3 | 命中 → 档 2（`EmbraceAGI/Mr.G-Your-AI-English-…-Tutor`，MIT） |
| `S5-academic-writing` | 3 | 命中 → 档 2（`delibae/claude-prism`，MIT；`PaperDebugger` 因 AGPL 仅可外部调用） |
| `R1-literature` | 3 | 命中 → 档 2（`asreview/asreview`，Apache-2.0） |
| `F8-career` | 3 | 命中 → 档 2（`career-ops-hq/career-ops`，MIT） |
| `F4-money-safety` | 2 | **指定平台内未命中 → 档 3**（无 skill 流程） |
| `F6-service` | 2 | **指定平台内未命中 → 档 3** |
| `F3-wellbeing` / `F5-health` | 2 | **红线域 → 禁外接**，不检索，直接档 3 |

**演练当场抓出并修掉的 3 个缺陷**（这就是「亲测」的价值）：

1. **检索式用中文长句会 100% 0 命中** → 补 `_domain.md` 的「平台检索式（英文，≤3 词）」。
2. **自检第 5 项写成"需人工判定" = 默认通过 → 假命中**：
   实测 `R1` 一度"命中" `HiLab-git/SSL4MIS`（**医学图像分割**）、`S1` 一度"命中" `learn-codebase`（读代码库）。
   → 改为**可执行两段判据**：正向命中本域「适配词表」≥1 **且** 反向命中全局「反向词表」0。
3. **纯正向匹配仍会被"顺带词组"骗过**：`SSL4MIS` 描述里顺带写着
   "a collection of **literature reviews**" → 于是被判成 R1 的合格候选。
   → 加**全局反向词表**（`medical` / `clinical` / `segmentation` … 23 词）作第二道闸，实测已正确淘汰。

> **教训**：外接判据里**任何"需人工判定"的项，都等于默认通过** ——
> 要么给可执行判据，要么把它降级为「降权项」而不是「通过项」。

## 六、已核验候选仓库池（**登记唯一真相源**）

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
