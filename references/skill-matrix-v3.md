# 库外 Skill 多源比对矩阵 v3

> 生成：`scripts/_build/build_phase14.py` ｜ 基准日 **2026-10-02**
> 数据：GitHub API 实抓（stars / license / pushed_at / archived / size）+ 12 平台可达性实测
> 评分口径与门禁见各域 `skills/external.md` §二；本表为全量汇总。

## 一、19 域最优解一览

| 域 | 名称 | 库外候选数 | 库外最优解（合规 ∩ DUT≥3） | 综合分 | DUT 适配 | 库内首选（永远优先） | 库内备选 |
|---|---|---|---|---|---|---|---|
| `S1` | 课程答疑 | 6 | `socrates-skill`（`bevibing/socrates-skill`） | **4.25** | 4 | `explain-stepwise` | `error-diagnose` |
| `S2` | 课堂与笔记 | 6 | `obsidian-skills`（`kepano/obsidian-skills`） | **4.40** | 4 | `lecture-to-notes` | `note-normalize` |
| `S3` | 作业与考核 | 3 | `paper-writer`（`kgraph57/paper-writer-skill`） | **3.50** | 3 | `lab-report` | `assignment-plan` |
| `S4` | 备考与记忆 | 4 | `learn-faster-kit`（`hluaguo/learn-faster-kit`） | **4.10** | 4 | `exam-sprint` | `recall-schedule` |
| `S5` | 学术表达 | 4 | `academic-pptx-skill`（`Gabberflast/academic-pptx-skill`） | **4.25** | 3 | `paper-outline` | `cite-normalize` |
| `S6` | 语言能力 | 3 | `ielts`（`YANZHANLIN/ielts-claude-skills`） | **4.55** | 4 | `lang-drill` | `pronounce-drill` |
| `F1` | 校园事务 | 2 | **无（纯自建）** | — | — | `campus-desk` | `campus-proof-guide` |
| `F2` | 作息与专注 | 3 | `deep-work`（`alirezarezvani/claude-skills`） | **4.40** | 4 | `focus-block` | `task-decompose` |
| `F3` | 身心与社交 | 0 | **无（纯自建）** | — | — | `wellbeing-checkin` | `peer-talk-script` |
| `F4` | 财务与安全 | 0 | **无（纯自建）** | — | — | `money-guard` | `budget-plan` |
| `F5` | 健康与运动 | 0 | **无（纯自建）** | — | — | `health-guide` | `clinic-path` |
| `F6` | 军训与志愿 | 0 | **无（纯自建）** | — | — | `service-log` | `volunteer-hours` |
| `F7` | 升学深造 | 3 | **无（纯自建）** | — | — | `grad-plan` | `grad-calendar` |
| `F8` | 求职与竞赛 | 2 | `ResumeSkills`（`Paramchoudhary/ResumeSkills`） | **4.70** | 3 | `career-kit` | `competition-pick` |
| `R1` | 文献检索与管理 | 5 | `literature-downloader-skill`（`Lucaswangzcx/literature-downloader-skill`） | **4.55** | 5 | `lit-map` | `citation-verify` |
| `R2` | 实验与数据 | 3 | `scientific-agent-skills`（`K-Dense-AI/scientific-agent-skills`） | **4.25** | 3 | `data-lab` | `stats-guard` |
| `R3` | 科研工具与代码 | 3 | `teach`（`mattpocock/skills`） | **4.10** | 4 | `tool-setup` | `repro-env` |
| `R4` | 学术产出与投稿 | 3 | `academic-pptx-skill`（`Gabberflast/academic-pptx-skill`） | **3.80** | 3 | `submit-kit` | `rebuttal-structure` |
| `R5` | 学术规范与伦理 | 1 | **无（纯自建）** | — | — | `integrity-check` | `ai-disclosure` |

**汇总**：19 域中 **12 域有合规库外最优解**，**7 域为纯自建**；候选行 **51 条**，涉及 **42 个仓库**；其中 **11 条因许可证缺失被排除**、**1 条仅可外部调用**。

### 「适配 DUT 大学生活吗」的量化答案

| 口径 | 条数 | 占候选总数 |
|---|---|---|
| **DUT 适配 ≥ 4**（推荐直接用） | 12 | 24% |
| DUT 适配 3（可用，需改造） | 20 | 39% |
| **DUT 适配 ≤ 2（环境错位，不作最优解）** | 19 | 37% |

**结论**：库外候选整体只是「通用底座 + 少量中文垂类」，**真正开箱贴合 DUT 本科新生日常的比例不高**；大工的适配度主要由**库内 38 个自建 skill + DUT 站点强绑定**承担，库外仅作降级增强。

### 环境错位清单（DUT ≤ 2，共 19 条）

| 域 | 候选 | DUT | 错位点 |
|---|---|---|---|
| `S1` | `teach`（`mattpocock/skills`） | 2 | 工程向教学法（TDD/PR 流程），与大学课程答疑场景错位 |
| `S1` | `gurukul-ai`（`somenssarkar/gurukul-ai`） | 1 | 面向 Grade 7 中学教育，与大学完全错位 |
| `S2` | `lecture-to-study-guide`（`Jellypod-Inc/school-skills`） | 2 | IB/IGCSE 课堂语境，与大学课堂材料形态不同 |
| `S2` | `youtube-notetaker`（`dair-ai/dair-academy-plugins`） | 2 | 英文 YouTube 课程场景；DUT 主要用中文录播/雨课堂回放 |
| `S3` | `canvas-mcp`（`vishalsachdev/canvas-mcp`） | 1 | 同上：与 DUT 作业提交平台不同，无法直连 |
| `S5` | `academic-research-skills`（`Imbad0202/academic-research-skills`） | 2 | 英文科研写作链路 + 需 API Key，本科新生阶段偏重 |
| `S5` | `paper-tutor-skills`（`cabbage2000-lab/paper-tutor-skills`） | 2 | 同上 |
| `F1` | `googleworkspace/cli`（`googleworkspace/cli`） | 1 | Google 生态：DUT 学生无 Google 账号/校园 Gmail，日历-文档链路在国内校园跑不通 |
| `F1` | `canvas-mcp`（`vishalsachdev/canvas-mcp`） | 1 | Canvas LMS：DUT 用超星学习通 / 雨课堂 / 自建教务，平台错位 |
| `F2` | `habit-tracker`（`eddiebelaval/squire`） | 2 | 密钥可能明文落盘；打卡类也可用手机自带工具 |
| `F2` | `pomodoro`（`jakedahn/pomodoro`） | 2 | 二进制仅 macOS ARM；Windows 用户用不了 |
| `F7` | `SOP_Consultant`（`Haadhi76/SOP_Consultant`） | 2 | SOP 为北美研究生申请文书；DUT 主流路径是保研/考研，文书形态不同 |
| `F7` | `10xcolleges`（`tydev-new/10xcolleges`） | 1 | 美国选校数据，与国内升学体系无交集 |
| `F7` | `paper-tutor-skills`（`cabbage2000-lab/paper-tutor-skills`） | 2 | 面向研究生科研；本科新生路径规划用不上（且许可证未声明） |
| `F8` | `interview-prep`（`sourikduttanyu/interview-prep`） | 2 | 0★、题库偏海外技术面，与国内校招面试差异大 |
| `R1` | `paper-tutor-skills`（`cabbage2000-lab/paper-tutor-skills`） | 2 | 研究生向；本科新生文献需求靠库内 lit-map 已够 |
| `R3` | `superpowers`（`obra/superpowers`） | 2 | 同前：软件开发方法论 |
| `R4` | `academic-research-skills`（`Imbad0202/academic-research-skills`） | 2 | 同上 |
| `R4` | `paper-tutor-skills`（`cabbage2000-lab/paper-tutor-skills`） | 2 | 同上 |

## 二、许可证分布（本轮实抓复核）

| 判定 | 数量 | 处置 |
|---|---|---|
| ✅ 宽松许可（MIT/Apache/BSD/CC0） | 39 | 可外部调用，其中经核验的可摘录 |
| ⚠️ 强 copyleft / 禁商用 | 1 | **只做外部调用，禁止摘录进包** |
| ⛔ 无 LICENSE / API 未识别 | 11 | **禁止摘录、禁止再分发** |

## 三、与 v2.6 相比的修正

| # | v2.6 原判 | 本轮实测 | 处置 |
|---|---|---|---|
| 1 | `wentorai/Research-Claw` 标 MIT ✅ | GitHub API 返回 **未声明**（NOASSERTION） | 改判「许可证未声明」，降权并标注 |
| 2 | `Imbad0202/academic-research-skills` 标 CC-BY-NC 4.0 | GitHub API 返回 **未声明** | 按**最保守**处置（视同禁商用 + 禁摘录） |
| 3 | `anthropics/skills` 标 Apache-2.0(子目录) | 仓库**根目录**未声明总许可证 | 标注「子目录许可，根目录未声明」 |
| 4 | R2 候选仓库名写作 `openai`，许可证「未查到」却判 ✅ 合法 | 实为 **`openai/skills`**（27,841★），根目录未声明 | **修正仓库名**，合规改判为 0（不入围） |
| 5 | `GlacierXiaowei` 安装命令写作 `structured-learning` | 实际仓库名 `structured-learning-skill` | 修正安装命令 |
| 6 | 教育垂类「只有 mattpocock/teach 入榜」 | 新发现 `bevibing/tutor-skills` 1,313★、`GarethManning/education-agent-skills` 817★、`bevibing/socrates-skill` 326★、`Lucaswangzcx/literature-downloader-skill` 230★ | **结论过时**，已补入候选表 |

## 四、新增收录（v2.6 未收录）

| 仓库 | ★ | 许可证 | 收录域 |
|---|---|---|---|
| `bevibing/socrates-skill` | 326 | MIT | S1 |
| `bevibing/tutor-skills` | 1313 | MIT | S2 |
| `vishalsachdev/canvas-mcp` | 270 | MIT | S3 · F1 |
| `Lucaswangzcx/literature-downloader-skill` | 230 | MIT | R1 |
| `WenyuChiou/zotero-skills` | 55 | MIT | R1 |
| `cabbage2000-lab/paper-tutor-skills` | 33 | NOASSERTION | R1 · S5 · R4 |
| `lowwwbank/anything-to-course` | 18 | MIT | S2 · S4 |
| `flysheep-ai/education-skills` | 106 | MIT | S6 |
| `obra/superpowers` | 294023 | MIT | R3 |
| `K-Dense-AI/scientific-agents` | 192 | MIT | R2 |
| `openai/skills` | 27841 | NOASSERTION | R2 |

## 五、方法论（下一轮沿用）

1. **先过门禁再看分**：许可证不清 → 直接出局，评分不参与排序。
2. **适配度权重最高（0.45）**：星多但场景不搭的（如通用办公套件之于校务）不给高分。
3. **库内优先不可动摇**：库外仅在「库内不覆盖该细分场景」时启用，且必须走降级链。
4. **平台可达性也是事实**：12 平台中本机实测仅 4 个可达（见 `skill-sources.md`），故「多源比对」以 **GitHub API 可核验数据**为主干，平台侧作为发现渠道。
