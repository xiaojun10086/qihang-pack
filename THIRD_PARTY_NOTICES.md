# 第三方来源与许可证归属（THIRD PARTY NOTICES）

> 数据来源：GitHub API 实抓（stars / pushed_at / `license.spdx_id` / archived）+ 本机安装实测。
> 检索时间：2026-10-01。完整逐项审计见 `references/skill-compliance-audit.md`。
> 本包自身以 **MIT** 发布（见 `LICENSE`）。

## 一、许可证四档判定标准

| 判定 | 许可证类型 | 允许行为 |
|---|---|---|
| ✅ 可摘录可分发 | MIT / Apache-2.0 / BSD 等宽松许可 | 可复制内容进本包、可商用（保留版权声明） |
| ⚠️ 仅可外部调用 | **GPL-3.0** 等强 copyleft | **不得复制内容进包**（否则本包须整体 GPL 化）；只能运行时调用 |
| ❌ 禁商用 | **CC-BY-NC** 系列 | 校内非商用可用；**对外发布须替换** |
| ⛔ 不可摘录 | **无 LICENSE** | 默认「保留所有权利」，**不得复制进包、不得再分发**；仅本地自用 |

## 二、需要特别标注的依赖（**红线**）

| 仓库 | 许可证 | 约束 |
|---|---|---|
| `NeoLabHQ/context-engineering-kit` | **GPL-3.0** | **仅外部调用** —— 禁止摘录任何内容进本包 |
| `Imbad0202/academic-research-skills` | **CC-BY-NC 4.0** | 禁商用；对外发布须替换 |
| `mordor-forge/study-skill` | **无 LICENSE** | ⛔ 禁止摘录、禁止再分发，仅限本地自用 |
| `googlarz/math-skill` | **无 LICENSE** | ⛔ 同上 |
| `somenssarkar/gurukul-ai` | **无 LICENSE** | ⛔ 同上（且内容仅 Grade 7 可用） |
| `sickn33/agentic-awesome-skills` | MIT | ⚠️ 含 **3113 个脚本 / 31 个攻击性技能**，无法人工审计 → **禁止整体安装** |

## 三、本包已摘录内容的合法性（自查重点）

本包向库内 skill 摘录了两个外部技能的内容，逐项核验：

| 摘录来源 | 许可证 | 判定 |
|---|---|---|
| `Jellypod-Inc/school-skills` | **MIT** | ✅ 合法（可复制、可商用，保留版权声明即可） |
| `GlacierXiaowei/structured-learning-skill` | **Apache-2.0** | ✅ 合法（可复制、可商用，须保留 NOTICE） |

**结论：包内现有摘录 0 侵权风险。** 其余 17 个库内 skill 均为自建。

## 四、库外候选全量清单（26 个仓库，按 Stars 降序）

| 仓库 | Stars | 最近推送 | 许可证 | 合法性 | 可用性 |
|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | MIT | ✅ | ✅ |
| anthropics/skills | 179,227 | 2026-09-29 | 子目录 Apache-2.0 | ✅ | ✅ |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | **CC-BY-NC** | ❌ 禁商用 | ✅ |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | MIT | ✅ | ✅ |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | MIT | ⚠️ | ❌ **禁整体安装** |
| googleworkspace/cli | 31,219 | 2026-09-24 | Apache-2.0 | ✅ | ✅ |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | MIT | ✅ | ⚠️ 只取单个 skill |
| Paramchoudhary/ResumeSkills | 2,501 | 2026-06-19 | MIT | ✅ | ✅ |
| **NeoLabHQ/context-engineering-kit** | 1,737 | 2026-08-26 | **GPL-3.0** | ⚠️ 强 copyleft | ✅ 仅外部调用 |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | MIT | ✅ | ✅ |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | MIT | ✅ | ✅ |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | MIT | ✅ | ✅ |
| jakedahn/pomodoro | 56 | 2025-10-23 | MIT | ✅ | ⚠️ 停滞 11 个月 |
| **mordor-forge/study-skill** | 40 | 2026-07-17 | **无 LICENSE** | ⛔ | ⚠️ 禁摘录 |
| eddiebelaval/squire | 21 | 2026-08-16 | MIT | ✅ | ⚠️ 密钥明文落盘 |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | MIT | ✅ | ✅ |
| **googlarz/math-skill** | 9 | 2026-03-22 | **无 LICENSE** | ⛔ | ⚠️ 禁摘录 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | MIT | ✅ | ✅ |
| ghutchis/chem-skill | 4 | 2025-12-28 | MIT | ✅ | ⚠️ 9 个月未更新 |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | MIT | ✅ | ⚠️ 上传百度云端 OCR |
| Haadhi76/SOP_Consultant | 4 | 2026-06-15 | MIT | ✅ | ✅ |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | Apache-2.0 | ✅ | ✅ 实测装通 |
| xwmxcz/papers-skill | 1 | 2026-06-11 | MIT | ✅ | ⚠️ 1★，代码量极小 |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | MIT | ✅ | ⚠️ 无标准 SKILL.md |
| peter209393/anki-card-skills | 0 | 2026-09-27 | MIT | ✅ | ⚠️ 需 API Key |
| **somenssarkar/gurukul-ai** | 0 | 2026-02-21 | **无 LICENSE** | ⛔ | ❌ 仅 Grade 7 |

**清理结论**：**无一个仓库处于 archived 状态**；`googleworkspace/skills` 已确认 404（改用 `googleworkspace/cli`）。

## 五、安装通道实测（本机实跑，2026-10-01）

| 通道 | 结果 |
|---|---|
| LearnBuddy 原生：`find-skills` | ✅ 可用（检索后安装到 `~/.learnbuddy/skills/`） |
| `npx skills add <owner>/<repo>` | ✅ **可用**（通用 skills CLI）—— 6 个仓库 / 70+ skill 装通 |
| 手动 `git clone` + 复制 | ✅ 可用 |

**环境限制**：本机沙箱有批量删除保护（单轮 50 次上限），文件多的仓库安装会反复重试而变慢；
**不影响本包使用**（库内 38 个 skill 开箱即用，库外仅作增强）。

## 六、免责

外部 skill 均为公开开源项目，安装前请自行阅读源码与许可证。
DUT 信息库中标 ⚠️ 的条目**未经核验**，请勿直接使用。本包与上述任何仓库无隶属关系。
