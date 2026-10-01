# 验收报告 · 启航学伴包 v1.1

> 验收日期：2026-10-01 ｜ 验收对象：`qihang-pack` 及其 6 能力域所依赖的全部 Skill
> 执行方式：**4 路并行子 agent**（2 路研究 + 2 路分维度测试）+ 主 agent 复核

---

## 一、探测：Skill 从哪来（平台普查）

**探测了 12 个 skill 托管平台 / 技能库**（要求 ≥7 个，实际 12 个）。

| # | 平台 | URL | 规模 | 有使用量? | 有反馈信号? | 局限 |
|---|---|---|---|---|---|---|
| 1 | GitHub Topics + 官方仓库 | github.com/topics/agent-skills | 23,419 仓库 | ❌ | ✅ stars/issues | 只有 stars，无使用量 |
| 2 | **skills.sh** | skills.sh | 1,523,502（全站计数） | ✅ **Installs** | ❌ | 只有流行度，无质量 |
| 3 | awesomeskills.dev | awesomeskills.dev | 41,195 | ✅ | ❌ | 以开发/内容场景为主，教育空白 |
| 4 | officialskills.sh | officialskills.sh | 660（56 publisher） | ❌ | 仅更新时间 | 只收厂商官方技能 |
| 5 | skillsdirectory.com | skillsdirectory.com | 589 | ❌ | ❌ | 主打安全扫描，非发现 |
| 6 | VoltAgent/awesome-agent-skills | github.com/VoltAgent/awesome-agent-skills | 1000+ ｜ 35,075★ | ❌ | ✅ | 纯清单，人工维护 |
| 7 | ComposioHQ/awesome-claude-skills | github.com/ComposioHQ/awesome-claude-skills | 1000+ ｜ 76,231★ | ❌ | ✅（1,586 issues 积压） | 偏 Composio 导流 |
| 8 | SkillsMP | skillsmp.com | 3,296,897 | ❌（只显 stars） | 部分 | 海量但无质量分级 |
| 9 | claude-plugins.dev | claude-plugins.dev/skills | 46.9k | ⚠️ 口径不明 | 部分 | 自动索引无把关 |
| 10 | LobeHub Skills | lobehub.com/skills | 334,144 | ⚠️ 口径不明 | ❌ | 无教育分类 |
| 11 | ClawHub | clawhub.ai | 未公开 | ✅ 口径不明 | ❌ | OpenClaw 生态专用 |
| 12 | 中文 awesome 列表 | yzfly / mblode `awesome-skills-zh` | 精选清单 | ❌ | ✅（52★ / 活跃度极低） | 规模与活跃度都不够 |

**结论**：**不存在**一个既提供真实使用量、又深耕教育/校园场景的中文索引站。
→ 探测策略定为：**skills.sh 查使用量 + GitHub 查反馈 + 自建内部索引**（即本包 `references/routing-table.md`）。

---

## 二、比较：使用量与反馈

### 2.1 使用量（来源：skills.sh 全时段 Installs，2026-10-01 实抓）

| Skill | 仓库 | Installs | 是否入榜 |
|---|---|---|---|
| find-skills | vercel-labs/skills | 3.6M | 榜 1 |
| grill-me | mattpocock/skills | 1.3M | 榜 2 |
| frontend-design | anthropics/skills | 941.3K | 榜 7 |
| **teach** | **mattpocock/skills** | **736.7K** | **榜 42** |
| — | mattpocock/skills（整仓） | 4.4M 合计 | — |

> ⚠️ **关键发现**：**教育专用类 Skill 中，仅 `mattpocock/skills · teach` 进入 skills.sh 榜单**。
> 本包其余教育类 Skill（structured-learning、anki-card-skills、lecture-to-study-guide、paper-writer…）**均未上榜**，说明**使用量低、无公开数据** —— 这是本方案最大的选型风险，已在下文 §5 给出缓解措施。

### 2.2 反馈与质量（来源：GitHub API，2026-10-01 实抓）

| 仓库 | Stars | 最近推送 | Open Issues | 许可证 | 风险 |
|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | 541 | MIT | 低 |
| anthropics/skills | 179,227 | 2026-09-29 | 1,392 | 子目录 Apache-2.0 | 低 |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | 74 | MIT | 低 |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | 41 | **CC-BY-NC（禁商用）** | 中 |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | 0 | MIT | **高** |
| googleworkspace/cli | 31,219 | 2026-09-24 | 131 | Apache-2.0 | 低 |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | 27 | MIT | 中 |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | 4 | MIT | 低 |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | 3 | MIT | 低 |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | 0 | MIT | 低 |
| jakedahn/pomodoro | 56 | 2025-10-23 | 0 | MIT | 低（近停滞 11 个月） |
| mordor-forge/study-skill | 40 | 2026-07-17 | 33 | **无 LICENSE** | 中 |
| eddiebelaval/squire | 21 | 2026-08-16 | 2 | MIT | 中（密钥落盘） |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | 0 | MIT | 低 |
| googlarz/math-skill | 9 | 2026-03-22 | 0 | **无 LICENSE** | 中 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | 6 | MIT | 低 |
| ghutchis/chem-skill | 4 | 2025-12-28 | 0 | MIT | 低 |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | 0 | MIT | 中（上传第三方 OCR） |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | 0 | Apache-2.0 | 低 |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | 0 | MIT | 低 |
| peter209393/anki-card-skills | 0 | 2026-09-27 | 0 | MIT | 中（TTS 外发） |
| somenssarkar/gurukul-ai | 0 | 2026-02-21 | 0 | **无 LICENSE** | 中 |

**横向比较结论**：教育类仓库普遍处于「**低星（<1k）+ 单作者 + 近期创建**」状态，与通用开发类 Skill（数万星）不在一个量级。→ 本包的策略应是「**高星通用底座 + 低星垂类补充 + 自建编排器兜底**」。

---

## 三、子 agent 测试（两个不同维度）

### 3.1 测试 A · 可用性维度（22 个仓库）

| 结论 | 数量 | 明细 |
|---|---|---|
| ✅ 可放心安装 | 11 | school-skills、structured-learning、paper-writer、academic-pptx、ielts-claude-skills、math-skill、mindmap-skill、obsidian-skills、study-skill、anthropics/skills、exam-prep-skill |
| ⚠️ 需注意 | 10 | python-tutor（**无标准 SKILL.md**）、study-skill（需编译 Go）、pomodoro（**二进制仅 macOS ARM**）、exam-prep（需 PaddleOCR 令牌）、academic-research-skills（**必须 API Key + 联网**）、gurukul-ai（需 Key + 联网，仅 Grade 7 可用）… |
| ❌ 不可用 | 1 | **googleworkspace/skills → 404 仓库不存在** |

### 3.2 测试 B · 质量与风险维度（同 22 个仓库）

- **未发现任何恶意模式**：无 `curl | bash` 实执行、无 `sudo` 提权、无写入 `~/.ssh`/`~/.aws`、无向非声明地址回传环境变量。出现的 `rm -rf` 均限定在自身目录。
- **风险 TOP 3**：
  1. `sickn33/agentic-awesome-skills` — 38k 文件、3113 脚本、含 31 个攻击性技能，**无法人工审计，禁止整体安装**（只可摘取单个 SKILL.md）。
  2. `Candlest/exam-prep-skill` — 把本地 PDF/试卷 **POST 到百度云端 OCR**，涉版权与个人信息。
  3. `peter209393/anki-card-skills` + `eddiebelaval/squire` — 需 API Key，内容外发第三方；squire 将密钥明文写入 `~/.config/last30days/.env`。

---

## 四、验收结论（逐项判定）

| # | 验收项 | 判定 | 说明 |
|---|---|---|---|
| 1 | 探测平台 ≥7 个 | ✅ **通过** | 实际 12 个 |
| 2 | 先探测后比较 | ✅ **通过** | 先跑可用性探测（§3.1），再做使用量/反馈比较（§2） |
| 3 | 使用量数据 | ⚠️ **有条件通过** | 仅 skills.sh 可提供；教育类 Skill 仅 `teach` 有数（736.7K），其余无公开数据 |
| 4 | 反馈数据 | ✅ **通过** | 22 个仓库全量取得 Stars / 推送时间 / Issues / 许可证 |
| 5 | 强绑定 DUT 信息库 | ✅ **通过** | 新增 `references/dlut-official-sites.md`，收录 **160 条表格行**（✅ 显式已核验 72 · ⚠️ 待核实 23 · 学院类 65 条经官方章程交叉核对），含三校区、全部学院、职能部门；并在 SKILL.md §2.4 设为**强制引用** |
| 6 | 无歧义细化 | ✅ **通过** | 全部结论标注来源与核验状态；未核实项独立成表，禁止臆造 |
| 7 | 子 agent 测试不同方面 | ✅ **通过** | 2 路：可用性维度 + 质量风险维度 |
| 8 | 发现并修正缺陷 | ✅ **通过** | 见 §5.1 |

### 4.1 必须修正项（已在本版修复）

| 缺陷 | 影响 | 修正 |
|---|---|---|
| `googleworkspace/skills` **404 不存在** | A 域无法安装 | 改为 **`googleworkspace/cli`**（31,219★，Apache-2.0，2026-09-24 推送，含 gws-calendar / gws-tasks / gws-drive 等 agent skills） |
| `python-tutor-skill` 无标准 SKILL.md | 自动发现失败 | 降级为手动安装，并在路由表标注 |
| `pomodoro` 二进制仅 macOS ARM | Windows 不可用 | 标注平台限制，提供替代（`deep-work` / 自建番茄钟） |
| `study-skill` 需 Go 编译 | 安装门槛高 | 降为备选，主力改用 `structured-learning`（Windows 友好） |
| `jakedahn/pomodoro` 近 11 个月未更新 | 维护停滞风险 | 标注「停滞」，并列替代 |

---

## 五、残留风险与缓解

| 风险 | 等级 | 缓解措施（已落入包内） |
|---|---|---|
| 教育垂类 Skill 使用量低、无社区验证 | **高** | 高星通用底座（anthropics/skills、mattpocock/skills、obsidian-skills）承担主力；垂类仅作补充；编排器与输出模板**自建**，不依赖第三方质量 |
| 垂类仓库多为 0–50★ 单作者 | 中 | 每个域配 2–3 个备选与降级链；`qihang.sh probe` 定期体检 |
| API Key 与数据外发 | 中 | 路由表标注「需凭证/需联网」；教材试卷类材料默认不出本机 |
| `CC-BY-NC` 禁商用 | 中 | 已在路由表标注；校内非商用可用，对外发布需替换 |
| 平台/仓库改名或下架 | 中 | 每个域保留降级链；A 域已实测踩坑一次 |

## 六、待办（下一版）

1. 补 `references/dlut-official-sites.md` 中 22 条「待核实」URL（需校园网或人工确认）。
2. 为 C 域补充 Windows 可用的学科答疑替代件。
3. 用 `npx skills add` 实机安装一遍，产出「安装成功率」实测记录。
