# 库外 Skill 自检报告（合法性 + 可用性）

> 自检时间：2026-10-01 ｜ 对象：`domains/*/skills/external.md` 中的全部候选
> 数据来源：GitHub API 实抓（stars / pushed_at / license.spdx_id / archived）+ 本地安装实测

---

## 一、合法性（License）自检

**判定标准**

| 判定 | 许可证类型 | 允许行为 |
|---|---|---|
| ✅ **可摘录可分发** | MIT / Apache-2.0 / BSD 等宽松许可 | 可复制内容进本包、可商用 |
| ⚠️ **仅可外部调用** | **GPL-3.0** 等强 copyleft | **不得复制内容进包**（否则本包须整体 GPL 化）；只能运行时调用 |
| ❌ **禁商用** | **CC-BY-NC** 系列 | 校内非商用可用；**对外发布须替换** |
| ⛔ **不可摘录** | **无 LICENSE** | 默认「保留所有权利」，**不得复制进包、不得再分发**；仅本地自用 |

### 1.1 结论汇总

| 判定 | 数量 | 仓库 |
|---|---|---|
| ✅ 宽松许可 | 21 | 见下表 |
| ⚠️ 强 copyleft（GPL-3.0） | **1** | `NeoLabHQ/context-engineering-kit` |
| ❌ 禁商用（CC-BY-NC 4.0） | **1** | `Imbad0202/academic-research-skills` |
| ⛔ 无 LICENSE | **3** | `mordor-forge/study-skill`、`googlarz/math-skill`、`somenssarkar/gurukul-ai` |

### 1.2 关键合法性发现（需处置）

| # | 发现 | 影响 | 处置 |
|---|---|---|---|
| 1 | **`NeoLabHQ/context-engineering-kit` 是 GPL-3.0**（原以为宽松） | 若把其 skill 内容摘进本包，**本包须整体以 GPL-3.0 发布** | 已在 R5 只写「外部调用命令」，**新增禁止摘录标注** |
| 2 | `academic-research-skills` 为 **CC-BY-NC 4.0** | 禁止商用；赛道作品若被推广为「典型案例」须评估 | 保持外部调用 + 明示「对外发布需替换」 |
| 3 | **3 个仓库无 LICENSE 文件** | 默认保留所有权利，摘录/再分发均侵权 | 标注「**仅限本地自用，禁止摘录进包**」 |
| 4 | `sickn33/agentic-awesome-skills` 含 3113 个脚本、31 个攻击性技能 | 无法人工审计 | **禁止整体安装**，只允许摘取单个 SKILL.md 文本 |

### 1.3 ⭐ 本包已摘录内容的合法性（自查重点）

本包向 19 个库内 skill 中**摘录**了两个外部技能的内容，逐项核验：

| 摘录来源 | 许可证 | 判定 |
|---|---|---|
| `Jellypod-Inc/school-skills` | **MIT** | ✅ 合法（可复制、可商用，保留版权声明即可） |
| `GlacierXiaowei/structured-learning-skill` | **Apache-2.0** | ✅ 合法（可复制、可商用，须保留 NOTICE） |

**结论：包内现有摘录 0 侵权风险。**其余 17 个库内 skill 均为自建。

---

## 二、可用性自检

### 2.1 逐项结果（按 Stars 降序）

| 仓库 | Stars | 最近推送 | 许可证 | 合法性 | 可用性 | 备注 |
|---|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | MIT | ✅ | ✅ | 全榜唯一教育类入榜（736.7K installs） |
| anthropics/skills | 179,227 | 2026-09-29 | 子目录 Apache-2.0 | ✅ | ✅ | 官方 |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | MIT | ✅ | ✅ | 零脚本 |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | **CC-BY-NC** | ❌ 禁商用 | ✅ | 需 API Key + 联网 |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | MIT | ⚠️ | ❌ | **禁整体安装** |
| googleworkspace/cli | 31,219 | 2026-09-24 | Apache-2.0 | ✅ | ✅ | A 域正解（原 skills 仓库 404） |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | MIT | ✅ | ⚠️ | 只取单个 skill，勿整体装 |
| Paramchoudhary/ResumeSkills | 2,501 | 2026-06-19 | MIT | ✅ | ✅ | — |
| **NeoLabHQ/context-engineering-kit** | 1,737 | 2026-08-26 | **GPL-3.0** | ⚠️ 强 copyleft | ✅ | **仅外部调用** |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | MIT | ✅ | ✅ | 零脚本 |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | MIT | ✅ | ✅ | 完整版 v3 付费 |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | MIT | ✅ | ✅ | 本地 pandoc |
| jakedahn/pomodoro | 56 | 2025-10-23 | MIT | ✅ | ⚠️ | 停滞 11 个月；二进制仅 macOS ARM |
| **mordor-forge/study-skill** | 40 | 2026-07-17 | **无 LICENSE** | ⛔ | ⚠️ | 需 Go 编译；禁止摘录 |
| eddiebelaval/squire | 21 | 2026-08-16 | MIT | ✅ | ⚠️ | 密钥明文落盘 |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | MIT | ✅ | ✅ | 零脚本 |
| **googlarz/math-skill** | 9 | 2026-03-22 | **无 LICENSE** | ⛔ | ⚠️ | 禁止摘录 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | MIT | ✅ | ✅ | `--force` 会覆盖已有 |
| ghutchis/chem-skill | 4 | 2025-12-28 | MIT | ✅ | ⚠️ | 9 个月未更新 |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | MIT | ✅ | ⚠️ | **本地上传百度云端 OCR** |
| Haadhi76/SOP_Consultant | 4 | 2026-06-15 | MIT | ✅ | ✅ | — |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | Apache-2.0 | ✅ | ✅ | **实测装通** |
| xwmxcz/papers-skill | 1 | 2026-06-11 | MIT | ✅ | ⚠️ | 1★，代码量极小（10KB） |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | MIT | ✅ | ⚠️ | **无标准 SKILL.md** |
| peter209393/anki-card-skills | 0 | 2026-09-27 | MIT | ✅ | ⚠️ | 需 API Key |
| **somenssarkar/gurukul-ai** | 0 | 2026-02-21 | **无 LICENSE** | ⛔ | ❌ | 仅 Grade 7 可用 |

**清理结论**：**无一个仓库处于 archived 状态**；`googleworkspace/skills` 已确认为 404（改用 `googleworkspace/cli`）。

### 2.2 安装通道实测（本机实跑，2026-10-01）

| 通道 | 结果 |
|---|---|
| `npx skills add <owner>/<repo>` | ✅ **可用**。通用 skills CLI（npm 包），下载 + 落地 skill 目录成功 |
| LearnBuddy 原生：`find-skills` | ✅ 可用。检索后安装到 `~/.learnbuddy/skills/` |
| 手动 clone / 复制 | ✅ 可用 |

**实测逐项结果**

| 仓库 | 目标 skill | 落地结果 | 判定 |
|---|---|---|---|
| `GlacierXiaowei/structured-learning-skill` | structured-learning | ✅ 软链建立，LICENSE 实测 Apache-2.0（与 API 一致） | **成功** |
| `mattpocock/skills@teach` | teach | ✅ 落地 | **成功** |
| `googleworkspace/cli` | 41 个 `gws-*`（calendar / tasks / drive / docs / sheets / gmail …） | ✅ 全部落地 | **成功** |
| `YANZHANLIN/ielts-claude-skills` | ielts / reading / speaking / writing | ✅ 4 个落地 | **成功** |
| `Paramchoudhary/ResumeSkills` | 26 个（resume-* / career-* / interview-*） | ✅ 全部落地 | **成功** |
| `xwmxcz/papers-skill` | papers-research | ✅ 落地 | **成功** |
| `K-Dense-AI/scientific-agent-skills` | adaptyv / aeon / 13c-metabolic-flux … | ✅ 落地 | **成功** |
| `Jellypod-Inc/school-skills` | — | ⏳ 单次安装耗时过长（环境**批量删除保护**反复重试） | **环境受限** |

**关键结论**
1. `npx skills add` 的**下载链路完全可用** —— 6 个仓库、70+ 个 skill 实测成功。
2. 部分 agent 目录因环境**批量删除保护**（单轮 50 次上限）未写入 —— **不影响本包使用**（库内 38 个 skill 开箱即用，库外仅作增强）。
3. 部分仓库（skill 数量多、文件多）会因逐个重试而**显著变慢**，建议改用 `git clone` + 手动复制到 `~/.learnbuddy/skills/`。

**因此**：本文档的「可用性」列以 **GitHub API 客观数据**（存在性 / archived / 许可证 / 推送时间）为准，安装通道结论以本表实测为准。


---

## 三、需要落到包内的修正

1. R5 的 `external.md`：为 `NeoLabHQ/context-engineering-kit` 增加 **GPL-3.0 禁止摘录** 标注
2. 3 个无 LICENSE 仓库：在对应 `external.md` 增加 **⛔ 禁止摘录** 标注
3. `skill-sources.md`：补充「合法性四档判定标准」
4. 每域 `external.md` 表头：加一句「摘录前先查许可证；GPL/无 LICENSE 一律只做外部调用」

---

## 四、自检结论

| 检查项 | 结论 |
|---|---|
| 本包已摘录内容是否合法 | ✅ **0 侵权**（MIT + Apache-2.0） |
| 是否存在 GPL 污染风险 | ✅ 已识别 1 个并隔离（只作外部调用） |
| 是否存在禁商用依赖 | ⚠️ 1 个（CC-BY-NC），已标注，对外发布需替换 |
| 是否存在无证使用 | ✅ 已识别 3 个并标注禁止摘录 |
| 是否存在不可用仓库 | ✅ 无 archived；1 个 404 已替换 |
| 安装通道是否可用 | ✅ `npx skills add` 实测可用 |
