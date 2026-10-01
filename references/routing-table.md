# 路由表 · 全量 Skill 清单（v1.1）

> 验收与实测数据见 `validation-report.md` ｜ DUT 官网信息库见 `dlut-official-sites.md`
> 数据抓取时间：2026-10-01

---

## 0. 去哪找更多 Skill（12 个探测入口）

| 平台 | 检索入口 | 用途 |
|---|---|---|
| **skills.sh** | https://skills.sh/ ｜ `npx skills add <owner>/<repo>` | **唯一有真实安装量**，选型首选验证 |
| **GitHub** | https://github.com/topics/agent-skills ｜ https://github.com/topics/claude-skills | 反馈信号最全（stars/issues/推送） |
| awesomeskills.dev | https://www.awesomeskills.dev/ | 唯一按**任务场景**组织，跨平台 |
| officialskills.sh | https://officialskills.sh/ | 660 个厂商官方技能，可信白名单 |
| SkillsMP | https://skillsmp.com/ | 330 万条，按职业分类，做穷尽扫描 |
| claude-plugins.dev | https://claude-plugins.dev/skills | 46.9k，终端内检索 |
| LobeHub Skills | https://lobehub.com/skills | 334k，可 sort=ratingAverage |
| ClawHub | https://clawhub.ai/ | OpenClaw 生态 |
| VoltAgent/awesome-agent-skills | https://github.com/VoltAgent/awesome-agent-skills | 1000+ 分类清单 |
| ComposioHQ/awesome-claude-skills | https://github.com/ComposioHQ/awesome-claude-skills | 自动化/MCP 为主 |
| StudentSuite（学生向） | https://github.com/StudentSuite/awesome-skills-plugins-for-students | **158 students skills**，最对口 |
| 中文清单 | https://github.com/yzfly/awesome-skills-zh | 中文场景（活跃度低，仅参考） |

**探测流程（每次扩容都跑）**：
```
1) skills.sh 查使用量 → 2) GitHub API 查 stars/pushed/license → 3) 读 SKILL.md 判可用性 → 4) 读 scripts/ 判风险 → 5) 通过则写入本表
```

---

## 1. 域总览

| 域 | 名称 | 类型 | 主用 Skill |
|---|---|---|---|
| **G** | **校情信息（DUT 强绑定）** | **内置数据域** | `references/dlut-official-sites.md` |
| A | 学业节奏 | 外部 Skill | `googleworkspace/cli` |
| B | 课堂消化 | 外部 Skill | `school-skills` / `obsidian-skills` |
| C | 学科答疑 | 外部 Skill | `math-skill` 等 |
| D | 备考冲刺 | 外部 Skill | `structured-learning` |
| E | 学术表达 | 外部 Skill | `anthropics/skills` |
| F | 生活适应 | 外部 Skill | `pomodoro` / `squire` |

> **G 域说明（消歧义）**：G 域**不是**外部 Skill，而是本包内置的**结构化数据表**。任何涉及大工的提问（选课时间、学院联系方式、校区地址、报修电话、入口网址）**必须查表回答**，查不到就明说「信息库未收录」，**不得凭模型记忆作答**。

---

## 2. G 域 · 校情信息（DUT 强绑定）

| 触发意图 | 数据来源 | 输出 |
|---|---|---|
| 选课 / 成绩 / 培养方案 | `dlut-official-sites.md` §0 + §3 | 给出 `jxgl.dlut.edu.cn` 入口与教务处链接 |
| 学院 / 专业 / 老师 | §4 学部与学院 | 给出学院官网 URL + 所在校区 |
| 校区 / 地址 / 怎么去 | §2 校区 | 三校区地址与官网 |
| 校历 / 放假 / 考试周 | §3（中文校历标⚠️） | 给出入口，注明直链待核 |
| 图书馆 / 自习 / 场馆 | §3 | 给出分馆链接，场馆注明「仅 i大工 APP」 |
| 心理 / 资助 / 就业 / 报修 | §5 职能部门 | 给出官网与电话 |
| 不知道问谁 | §1 全校部门联系方式总表 | 给出 `office.dlut.edu.cn` 电话页 |

**硬规则**：本表未命中的 URL 一律回复「信息库未收录，请访问 https://www.dlut.edu.cn/ 核实」，**禁止编造**。

---

## 3. A 域 · 学业节奏（课表 / DDL / 考试周）

| 触发关键词 | Skill | 仓库 | 安装命令 |
|---|---|---|---|
| 课表、排期、日历、冲突 | `gws-calendar` | **googleworkspace/cli** | `/plugin marketplace add googleworkspace/cli` |
| 作业、DDL、待办、倒排 | `gws-tasks` | **googleworkspace/cli** | 同上 |
| 课业文件、云盘整理 | `gws-drive` | **googleworkspace/cli** | 同上 |
| 课程大纲、补充阅读 | `research/syllabus` | `alirezarezvani/claude-skills` | `/plugin marketplace add alirezarezvani/claude-skills` |

> ⚠️ **修正记录**：v1.0 误写为 `googleworkspace/skills`，实测 **404 不存在**；正确仓库为 **`googleworkspace/cli`**（31,219★，Apache-2.0，2026-09-24 推送）。
> ⚠️ 若学校未启用 Google Workspace，本域可降级为「本地 ICS + 手写 tasks.md」，见 `config.yaml` 的 `domains.A.fallback`。
> 验收：**通过（有条件）** — 需 Google 账号授权。

## 4. B 域 · 课堂消化

| 触发关键词 | Skill | 仓库 | 安装命令 | 验收 |
|---|---|---|---|---|
| 讲义、课堂笔记、学习指南 | `lecture-to-study-guide` | `Jellypod-Inc/school-skills` | `/plugin marketplace add Jellypod-Inc/school-skills` | ✅ 可用（6★，`--force` 会覆盖已有 skills，注意） |
| 笔记沉淀、知识库 | `obsidian-skills` | `kepano/obsidian-skills` | `/plugin marketplace add kepano/obsidian-skills` | ✅ 推荐（49,056★，零脚本） |
| 概念图、思维导图 | `mindmap-skill` | `0x-man/mindmap-skill` | `npx skills add 0x-man/mindmap-skill` | ✅ 可用（16★，零脚本） |
| 视频讲座转笔记 | `youtube-notetaker` | `dair-ai/dair-academy-plugins` | `/plugin marketplace add dair-ai/dair-academy-plugins` | ⚠️ 需联网 |

## 5. C 域 · 学科答疑

| 触发关键词 | Skill | 仓库 | 安装命令 | 验收 |
|---|---|---|---|---|
| 数学、概率、统计 | `math-skill` | `googlarz/math-skill` | `npx skills add googlarz/math-skill` | ⚠️ 可用但**无 LICENSE**（9★） |
| 物理概念 | `gurukul-ai` | `somenssarkar/gurukul-ai` | 手动 clone | ⚠️ 需 API Key + 联网，仅 Grade 7 可用，**无 LICENSE** |
| 化学结构式 | `chem-skill` | `ghutchis/chem-skill` | 手动 zip | ✅ 纯本地（4★，9 个月未更新） |
| 编程入门 | `python-tutor` | `egouilliard-leyton/python-tutor-skill` | 手动 `install.sh` | ⚠️ **无标准 SKILL.md**，自动发现会失败 |
| 编程入门（替代） | `teach` | `mattpocock/skills` | `npx skills add mattpocock/skills@teach` | ✅ **推荐替代**（736.7K installs） |

> **本域整体偏弱**：无高星高可用选项。建议优先用 D 域 `structured-learning` + 底层 `teach` 组合承担。

## 6. D 域 · 备考冲刺

| 触发关键词 | Skill | 仓库 | 安装命令 | 验收 |
|---|---|---|---|---|
| 突击、系统学、判分 | `structured-learning`（中文） | `GlacierXiaowei/structured-learning-skill` | `npx skills add glacierxiaowei/structured-learning` | ✅ **主用**（Apache-2.0，零脚本，Windows 友好） |
| Anki、卡组 | `anki-cards` | `peter209393/anki-card-skills` | 手动 `install.sh` | ⚠️ 需 API Key（默认本地 TTS） |
| 高分路线图 | `examprep-ai` | `sickn33/agentic-awesome-skills` | **仅摘单个 SKILL.md** | ❌ **禁止整体安装**（3113 脚本不可审计） |
| FSRS 排程 | `study` | `mordor-forge/study-skill` | 需 Go 1.22+ 编译 | ⚠️ **无 LICENSE**，降为备选 |
| 课程材料→复习结构 | `exam-prep` | `Candlest/exam-prep-skill` | 手动 clone | ⚠️ **本地 PDF 上传百度云端 OCR**，含版权风险 |
| 通用学习教练 | `learn-faster-kit` | `hluaguo/learn-faster-kit` | `npx skills add hluaguo/learn-faster-kit` | 未测 |

## 7. E 域 · 学术表达

| 触发关键词 | Skill | 仓库 | 安装命令 | 验收 |
|---|---|---|---|---|
| 文档底座 | `document-skills` | `anthropics/skills` | `/plugin marketplace add anthropics/skills` | ✅ **推荐**（179,227★，官方） |
| 论文 + 审稿预审 | `academic-research-skills` | `Imbad0202/academic-research-skills` | `/plugin marketplace add Imbad0202/academic-research-skills` | ⚠️ **需 API Key + 联网**，**CC-BY-NC 禁商用** |
| 实验报告（IMRAD） | `paper-writer` | `kgraph57/paper-writer-skill` | `npx skills add kgraph57/paper-writer-skill` | ✅ 本地 pandoc，无网络（58★） |
| 答辩 / 展示 PPT | `academic-pptx-skill` | `Gabberflast/academic-pptx-skill` | 手动上传 claude.ai | ✅ 零脚本（1,097★） |
| LaTeX | `claude-latex-skill` | `hameefy/claude-latex-skill` | `npx skills add hameefy/claude-latex-skill` | 未测 |
| 中文科研工作流 | `codex-claude-academic-skills` | `zLanqing/codex-claude-academic-skills` | 手动复制 | 未测 |

## 8. F 域 · 生活适应

| 触发关键词 | Skill | 仓库 | 安装命令 | 验收 |
|---|---|---|---|---|
| 番茄钟、专注 | `pomodoro` | `jakedahn/pomodoro` | `npx skills add jakedahn/pomodoro` | ⚠️ **二进制仅 macOS ARM**，Windows 需替代；**近 11 个月未更新** |
| 习惯、作息 | `habit-tracker` | `eddiebelaval/squire` | 手动 `install.sh` | ⚠️ 需 API Key，密钥明文落盘 |
| 深度工作 | `productivity/deep-work` | `alirezarezvani/claude-skills` | `/plugin marketplace add alirezarezvani/claude-skills` | ⚠️ 仓库脚本面大（含渗透类技能），**只取该 skill** |
| 资料整理 | `file-organizer` | `ComposioHQ/awesome-claude-skills` | `/plugin marketplace add ComposioHQ/awesome-claude-skills` | ✅ 可用 |
| 雅思 / 四六级 | `ielts` | `YANZHANLIN/ielts-claude-skills` | 手动复制 | ✅ 零脚本（307★，完整版 v3 付费） |
| 英语口语 | `english-coach` | `tianmind-studio/english-coach` | `npx skills add tianmind-studio/english-coach` | 未测 |

## 9. 底层常驻

| Skill | 仓库 | 安装命令 | 作用 | 验收 |
|---|---|---|---|---|
| `teach` | mattpocock/skills | `npx skills add mattpocock/skills@teach` | 长期学习档案 + 间隔重复课程 | ✅ **强烈推荐**（736.7K installs，全榜唯一教育类） |
| `handoff` | mattpocock/skills | `npx skills add mattpocock/skills@handoff` | 长会话压缩交接 | ✅ |

---

## 10. 降级链（每个域至少 2 级）

| 域 | 一级 | 二级 | 三级（纯上下文） |
|---|---|---|---|
| A | googleworkspace/cli | 本地 ICS + tasks.md | 手写周计划模板 |
| B | obsidian-skills | school-skills | 直接输出笔记正文 |
| C | teach | math-skill | 分步讲解 + 要求用户先写一步 |
| D | structured-learning | anki-card-skills | structured-learning 的纯提示词模式 |
| E | anthropics/skills | paper-writer | 直接生成 Markdown 正文 |
| F | deep-work | squire | 手写番茄钟记录表 |

**降级触发条件**：① 安装失败 ② 探测不到 ③ 需要 API Key 而用户未提供 ④ 平台不兼容（如 macOS 专用）。触发后输出须标注 `[已降级: 原 → 备]`。
