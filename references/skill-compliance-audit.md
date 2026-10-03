# 库内 Skill 来源合规自检报告（合法性 + 可用性）

> 自检时间：2026-10-02 ｜ 对象：本包 **92 个库内 skill** 的来源素材
> 数据来源：GitHub API 实抓（stars / pushed_at / `license.spdx_id` / archived）+ 本地重写实测
> 口径：本包为 **DUT 特化库（库内优先）**：**核心能力运行期零外部依赖**，外部内容默认仅作**构建期素材**；
> 自 v3.3.0 起新增**可选的外部桥接**（只在库内与同域降级都接不住时启用，且须过五步自检与许可门禁），**外部未命中即回落原有流程**。

---

## 一、合法性（License）自检

**判定标准（构建期素材门禁）**

| 判定 | 许可证类型 | 允许行为 |
|---|---|---|
| ✅ **可摘录可重写** | MIT / Apache-2.0 / BSD / ISC / CC0 等宽松许可 | 可复制、可改写、可商用（保留版权声明） |
| ⚠️ **仅可思想参考** | **GPL-3.0 / AGPL** 等强 copyleft | **不得复制内容进包**（否则本包须整体 GPL 化）；仅可参考思路 |
| ❌ **禁商用** | **CC-BY-NC** 系列 | 校内非商用可用；**对外发布须替换** |
| ⛔ **零内容摘录** | **专有 / 无 LICENSE** | 默认「保留所有权利」，**不得复制任何内容**；仅可参考方法论并全量重写 |

### 1.1 结论汇总

| 判定 | 数量 | 说明 |
|---|---|---|
| ✅ 宽松许可（可改造） | **10 个 skill** | 骨架提取 + 全量重写 + DUT 特化 |
| ⛔ 专有许可（零摘录） | **2 个 skill** | 仅参考方法论思路，全量重写 |
| 自建 | **40 个 skill** | 无外部来源 |

### 1.2 关键合法性发现（已处置）

| # | 发现 | 影响 | 处置 |
|---|---|---|---|
| 1 | `NeoLabHQ/context-engineering-kit` 是 **GPL-3.0** | 若摘录其内容，**本包须整体以 GPL-3.0 发布** | **未吸收**（仅思路参考，零内容） |
| 2 | `Imbad0202/academic-research-skills` 为 **CC-BY-NC 4.0** | 禁止商用 | **未吸收** |
| 3 | **2 个仓库无 LICENSE**（mordor-forge/study-skill、googlarz/math-skill、somenssarkar/gurukul-ai） | 默认保留所有权利 | **未吸收**（禁止摘录） |
| 4 | `Gabberflast/academic-pptx-skill` 实抓 frontmatter 标注**专有许可**（与矩阵曾记 MIT 不符） | 若摘录即侵权 | **降级为「零内容摘录」**，S5/R4 两处均以本项目语言全量重写 |
| 5 | `sickn33/agentic-awesome-skills` 含 3113 脚本 / 31 个攻击性技能 | 无法人工审计 | **未吸收** |

### 1.3 ⭐ 本包已吸收内容的合法性（自查重点）

本包向库内 skill 吸收了 **12 个**外部最优解，逐项核验（明细见 `THIRD_PARTY_NOTICES.md` §三）：

| 吸收来源 | 原许可 | 吸收方式 | 判定 |
|---|---|---|---|
| `bevibing/socrates-skill` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `kepano/obsidian-skills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `kgraph57/paper-writer-skill` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `hluaguo/learn-faster-kit` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `YANZHANLIN/ielts-claude-skills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `alirezarezvani/claude-skills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `Paramchoudhary/ResumeSkills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `Lucaswangzcx/literature-downloader-skill` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `K-Dense-AI/scientific-agent-skills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `mattpocock/skills` | MIT | 骨架提取 + 重写 | ✅ 合法 |
| `Gabberflast/academic-pptx-skill`（→ S5） | 专有 | **零内容摘录** + 全量重写 | ✅ 无侵权 |
| `Gabberflast/academic-pptx-skill`（→ R4） | 专有 | **零内容摘录** + 全量重写 | ✅ 无侵权 |

**结论：包内现有内容 0 侵权风险。** 其余 40 个库内 skill 均为自建。

---

## 二、可用性自检

### 2.1 库内 skill 可用性（本包主体）

| 项 | 结论 |
|---|---|
| 库内 skill 总数 | **92 个**（每域 4–5 个） |
| 运行期外部依赖 | **零**（不安装、不调用、不下载库外 skill） |
| 离线可用 | ✅ 全程离线 |
| 每域红线一致性 | ✅ 库内 skill 红线与所属域 `_domain.md` **逐条一致**（由 `regress.sh` / `aligncheck.py` 断言） |
| 结构契约 | ✅ 均含必需小节（前置/边界/执行步骤/可执行示例/红线/输出/DUT 绑定点/失败与降级） |

### 2.2 构建期素材探测（GitHub API 客观数据）

| 仓库 | Stars | 最近推送 | 许可证 | 合法性 | 备注 |
|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | MIT | ✅ | 已吸收（R3/code-mentor） |
| anthropics/skills | 179,227 | 2026-09-29 | 子目录 Apache-2.0 | ✅ | 未吸收 |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | MIT | ✅ | 已吸收（S2/link-notes） |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | **CC-BY-NC** | ❌ 禁商用 | 未吸收 |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | MIT | ⚠️ | **禁整体安装**，未吸收 |
| googleworkspace/cli | 31,219 | 2026-09-24 | Apache-2.0 | ✅ | 未吸收 |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | MIT | ✅ | 已吸收（F2/deep-work） |
| Paramchoudhary/ResumeSkills | 2,501 | 2026-06-19 | MIT | ✅ | 已吸收（F8/resume-tailor） |
| **NeoLabHQ/context-engineering-kit** | 1,737 | 2026-08-26 | **GPL-3.0** | ⚠️ 强 copyleft | 仅思路，零内容 |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | **专有** | ⛔ 零摘录 | 仅思路（S5/R4 全量重写） |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | MIT | ✅ | 已吸收（S6/ielts-coach） |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | MIT | ✅ | 已吸收（S3/imrad-scaffold） |
| jakedahn/pomodoro | 56 | 2025-10-23 | MIT | ✅ | 未吸收 |
| **mordor-forge/study-skill** | 40 | 2026-07-17 | **无 LICENSE** | ⛔ | 未吸收 |
| eddiebelaval/squire | 21 | 2026-08-16 | MIT | ✅ | 未吸收（密钥明文落盘） |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | MIT | ✅ | 未吸收 |
| **googlarz/math-skill** | 9 | 2026-03-22 | **无 LICENSE** | ⛔ | 未吸收 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | MIT | ✅ | 未吸收（v2 摘录，v3 改自建） |
| ghutchis/chem-skill | 4 | 2025-12-28 | MIT | ✅ | 未吸收 |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | MIT | ✅ | 未吸收（上传百度云端 OCR） |
| Haadhi76/SOP_Consultant | 4 | 2026-06-15 | MIT | ✅ | 未吸收 |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | Apache-2.0 | ✅ | 未吸收（v2 摘录，v3 改自建） |
| xwmxcz/papers-skill | 1 | 2026-06-11 | MIT | ✅ | 未吸收 |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | MIT | ✅ | 未吸收 |
| peter209393/anki-card-skills | 0 | 2026-09-27 | MIT | ✅ | 未吸收 |
| **somenssarkar/gurukul-ai** | 0 | 2026-02-21 | **无 LICENSE** | ⛔ | 未吸收 |

**清理结论**：**无一个仓库处于 archived 状态**；`googleworkspace/skills` 已确认为 404。

---

## 三、自检结论

| 检查项 | 结论 |
|---|---|
| 本包已吸收内容是否合法 | ✅ **0 侵权**（10 个 MIT + 2 个专有但零摘录） |
| 是否存在 GPL 污染风险 | ✅ 已识别 1 个（NeoLabHQ）并**未吸收** |
| 是否存在禁商用依赖 | ✅ 已识别 1 个（CC-BY-NC）并**未吸收** |
| 是否存在无证使用 | ✅ 已识别 3 个无 LICENSE 仓库并**未吸收** |
| 是否存在运行期外部依赖 | ✅ **无** —— 纯 DUT 特化库，运行时零外部通道 |
| 是否存在不可用仓库 | ✅ 无 archived；1 个 404 已替换 |
