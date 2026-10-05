# 第三方来源与许可证归属（THIRD PARTY NOTICES）

> 本包自身以 **MIT** 发布（见 `LICENSE`）。
> 数据来源：GitHub API 实抓（stars / pushed_at / `license.spdx_id` / archived）+ 本机安装实测。
> 检索时间：2026-10-01；v3 改造落地：2026-10-02；v4 结构重构：2026-10-05。
> 完整逐项审计记录已随 v3 结构归档；本表保留归属结论。

## 一、说明：本包为「纯 DUT 特化库」

自 **v3.0.0** 起，本包**只指向本地库内 skill，不含任何库外安装通道**：

- **v4.0 结构**：库内 **25 个 skill** = **自建 15 个** + **10 个有来源记录**（8 个基于 MIT 来源骨架重写；2 个只参考方法论、零内容摘录）。
- 外部内容仅作为**构建期素材**：下载到本地 → **统一格式 + DUT 特化重写** → 融入本包。
- 改造后的产物是本项目**自己的 skill**，版权归本项目；仅保留对原作者的**署名与许可声明**（本文件）。
- **运行期无外部依赖**：不安装、不调用任何库外 skill 包。v4.0 已移除 v3.3 的「外部桥接」通道；包内覆盖不到的需求一律明说未收录并给官方核实路径。
- **v4.0 重构**：v3 的 92 个 skill 折叠为 25 个扁平 skill，下表给出有来源记录的 skill 在新结构中的落点。

## 二、许可证四档判定标准（构建期素材门禁）

| 判定 | 许可证类型 | 允许行为 |
|---|---|---|
| ✅ 可摘录可重写 | MIT / Apache-2.0 / BSD / ISC / CC0 等宽松许可 | 可复制、可改写、可商用（保留版权声明） |
| ⚠️ 仅可思想参考 | **GPL-3.0 / AGPL** 等强 copyleft | **不得复制内容进包**（否则本包须整体 GPL 化）；仅可参考思路 |
| ❌ 禁商用 | **CC-BY-NC** 系列 | 校内非商用可用；**对外发布须替换** |
| ⛔ 零内容摘录 | **专有 / 无 LICENSE** | 默认「保留所有权利」，**不得复制任何内容**；仅可参考方法论思路并全量重写 |

## 三、本包已吸收内容的来源与合法性（自查重点）

本包对 **10 个**有外部来源记录的 skill 逐项核验（旧结构名 → v4 skill）：

| # | v4 skill（旧结构名） | 吸收来源仓库 | 原许可 | 吸收方式 | 判定 |
|---|---|---|---|---|---|
| 1 | `explain-stepwise`（S1/socratic-qa） | `bevibing/socrates-skill` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 2 | `lecture-to-notes`（S2/link-notes） | `kepano/obsidian-skills` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 3 | `lab-report`（S3/imrad-scaffold） | `kgraph57/paper-writer-skill` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 4 | `faster-cycle`（S4/faster-cycle） | `hluaguo/learn-faster-kit` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 5 | `paper-outline`（S5/argument-slides） | `Gabberflast/academic-pptx-skill` | **专有** | **零内容摘录**，方法论思路参考 + 全量重写 | ✅ 无侵权（仅参考思路） |
| 6 | `lang-drill`（S6/ielts-coach） | `YANZHANLIN/ielts-claude-skills` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 7 | `lit-fetch`（R1/lit-fetch） | `Lucaswangzcx/literature-downloader-skill` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 8 | `data-lab`（R2/stats-workflow） | `K-Dense-AI/scientific-agent-skills` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 9 | `code-mentor`（R3/code-mentor） | `mattpocock/skills` | **MIT** | 骨架提取 + 重写 | ✅ 合法 |
| 10 | `paper-outline`（R4/defense-qa） | `Gabberflast/academic-pptx-skill` | **专有** | **零内容摘录**，方法论思路参考 + 全量重写 | ✅ 无侵权（仅参考思路） |

**结论：包内现有内容 0 侵权风险。** 其中 **8 个**基于 MIT 许可仓库内容骨架重写（保留署名与许可声明），**2 个**仅参考专有许可仓库的方法论且**零内容摘录**。其余 **15 个**库内 skill 为自建。

v3 有来源记录中的 `F2/deep-work`（`alirezarezvani/claude-skills`，MIT）与 `F8/resume-tailor`（`Paramchoudhary/ResumeSkills`，MIT）在 v4.0 折叠中**已整体移除**，包内不含其任何内容，故不再列入。

## 四、构建期素材全量清单（按 Stars 降序）

> 下表为**构建期探测过的候选池**（用于选型比对），**不是运行期依赖**。全部候选均未被本包在运行期引用。

| 仓库 | Stars | 最近推送 | 许可证 | 合法性 | 是否吸收 |
|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | MIT | ✅ | ✅ 吸收（`code-mentor`） |
| anthropics/skills | 179,227 | 2026-09-29 | 子目录 Apache-2.0 | ✅ | — |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | **CC-BY-NC** | ❌ 禁商用 | — |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | MIT | ✅ | ✅ 吸收（`lecture-to-notes`） |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | MIT | ⚠️ 含攻击性技能 | ❌ 未吸收 |
| googleworkspace/cli | 31,219 | 2026-09-24 | Apache-2.0 | ✅ | — |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | MIT | ✅ | ⚠️ 原 F2/deep-work 已移除 |
| Paramchoudhary/ResumeSkills | 2,501 | 2026-06-19 | MIT | ✅ | ⚠️ 原 F8/resume-tailor 已移除 |
| NeoLabHQ/context-engineering-kit | 1,737 | 2026-08-26 | **GPL-3.0** | ⚠️ 强 copyleft | ❌ 仅思路，零内容 |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | **专有** | ⛔ 零内容摘录 | ⚠️ 仅思路（`paper-outline` 全量重写） |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | MIT | ✅ | ✅ 吸收（`lang-drill`） |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | MIT | ✅ | ✅ 吸收（`lab-report`） |
| jakedahn/pomodoro | 56 | 2025-10-23 | MIT | ✅ | — （学习节奏用自建） |
| mordor-forge/study-skill | 40 | 2026-07-17 | **无 LICENSE** | ⛔ | ❌ 未吸收 |
| eddiebelaval/squire | 21 | 2026-08-16 | MIT | ✅ | — （密钥明文落盘，不取） |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | MIT | ✅ | — |
| googlarz/math-skill | 9 | 2026-03-22 | **无 LICENSE** | ⛔ | ❌ 未吸收 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | MIT | ✅ | — （v2 摘录，v3 已改自建） |
| ghutchis/chem-skill | 4 | 2025-12-28 | MIT | ✅ | — |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | MIT | ✅ | — （上传百度云端 OCR，不取） |
| Haadhi76/SOP_Consultant | 4 | 2026-06-15 | MIT | ✅ | — |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | Apache-2.0 | ✅ | — （v2 摘录，v3 已改自建） |
| xwmxcz/papers-skill | 1 | 2026-06-11 | MIT | ✅ | — （1★，代码量极小） |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | MIT | ✅ | — （无标准 SKILL.md） |
| peter209393/anki-card-skills | 0 | 2026-09-27 | MIT | ✅ | — （需 API Key） |
| somenssarkar/gurukul-ai | 0 | 2026-02-21 | **无 LICENSE** | ⛔ | ❌ 未吸收 |
| bevibing/socrates-skill | — | — | MIT | ✅ | ✅ 吸收（`explain-stepwise`） |
| hluaguo/learn-faster-kit | — | — | MIT | ✅ | ✅ 吸收（`faster-cycle`） |
| Lucaswangzcx/literature-downloader-skill | — | — | MIT | ✅ | ✅ 吸收（`lit-fetch`） |
| K-Dense-AI/scientific-agent-skills | — | — | MIT | ✅ | ✅ 吸收（`data-lab`） |

**清理结论**：**无一个仓库处于 archived 状态**；`googleworkspace/skills` 已确认 404。

## 五、免责

1. 本包为 **DUT 特化 skill 包**：不引用外部 skill，上表候选池同时充当许可判定依据。
2. 基于 MIT 来源的 8 个 skill **已重写并 DUT 特化**，保留原作者署名与许可声明；另 2 个只参考方法论，**零内容摘录**。
3. DUT 信息库中标 ⚠️ 的条目**未经核验**，请勿直接使用。
4. 本包与上述任何仓库无隶属关系。
