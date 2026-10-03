# v3.0.0 生成链（收编层）

> **本目录是 v3.0.0 的生成器**。改域 / 改 skill 内容时改这里的**数据表**再重跑，
> 不要手改 `domains/*/skills/local/*/SKILL.md`。
>
> 与上一级 `scripts/_build/`（`build_qihang_v2.py` + `build_phase1.py` … `build_phase19.py`）
> 的关系：**那套是 v2.x 历史层**（模型停在 19 域 / 38 skill / v2.11），**只读保留、勿直接重跑**；
> 本目录才是 v3.0.0 的现行链。详见上一级 `scripts/_build/README.md` 的「历史层」段。
>
> **发布分支（v3.2.5 起）**：本目录 `release/` 下 —— `release_branch.py` 是**现行**
> （单仓库双分支：`main` 开发 → `release` 纯净交付；`git archive release` / `clone -b release` 分发）；
> `sync_release.py` / `verify.py` 是**历史**（两目录线的下发与终检，已退役）；`finish.py` 更早（一次性收尾）。
> 判据与命令见上一级 README 的「发布方式」段。
>
> **双目录线退役的连带简化**：此前「两处记忆必须逐字节同源」（副本不含 `.learnbuddy/`，须手动镜像）
> 这条铁律**随之消失** —— `main` 成为记忆的**唯一落点**，`release` 分支天然不含 `.learnbuddy/`。

---

## 为什么会有这一层

v3.0.0 的扩库与优化，原先是用一批**一次性脚本**在 `%TEMP%` 里跑出来的（原名 `gen_lib.py`、
`gen_content_*.py`、`gen_opt_*.py`、`qihang_v3_step1/2.py` 等）。它们硬编码绝对路径、
部分还是冲着**交付副本**跑的 —— 仓库里没有任何一份能复现 v3.0.0 的生成链。
后果：临时目录一旦被清理，v3.0.0 的内容就无法再重新生成。

本层把这些脚本**收编入库**，做三件机械变换（**语义未改**）：

| 变换 | 说明 |
|---|---|
| ROOT 参数化 | 统一为 `python <脚本> [仓库根]`，默认 = 仓库根；与 `build_phaseN.py .` 口径一致 |
| 幂等化 | 目标文件不存在 / 已处理过 → 跳过，不再抛异常（原版在已成的树上重跑会崩） |
| 去砂箱禁忌 | 不给 `scripts/audit.sh` 引入 `rm -rf` / `rmtree` / `os.system(` 等命中项 |

另有两处**行为修正**（已在文件头注明）：`step42` 直接把路径写为 `/`（原版写反斜杠、靠
`step43` 事后归一）；`release/finish.py` 用 `shutil.move` 取代 `os.remove`（受限环境会拦截删除）。

---

## 层序

```bash
python scripts/_build/v3/rebuild.py            # 默认作用于仓库根
python scripts/_build/v3/rebuild.py <仓库根>    # 指定目标树（推荐先在副本上试跑）
python scripts/_build/v3/rebuild.py --dry      # 只列层，不执行
```

| 序 | 脚本 | 作用 | 原名 |
|---|---|---|---|
| 1 | `scripts/_build/v3/v3_lib.py` | 公共库：渲染器 + **从 `_domain.md` 运行时解析红线/DUT**（新 skill 不手抄，故与域文件天然逐字一致） | `gen_lib.py` |
| 2 | `scripts/_build/v3/step10_de_external.py` | 去库外化：删 `external.md` 与两份库外文档；库内 skill 降级段改写；`_domain.md` / `commands` 步骤序号收敛 | `qihang_v3_step1.py` |
| 3 | `scripts/_build/v3/step11_ext_register.py` | 12 个改造（MIT 派生）skill 登记进 `domains/*/_domain.md`；F7 触发词消歧 | `qihang_v3_step2.py` |
| 4 | `scripts/_build/v3/step20_content_s.py` · `_f.py` · `_r.py` | 新增 skill 内容表（S 11 / F 17 / R 12）——纯数据 | `gen_content_*.py` |
| 5 | `scripts/_build/v3/step21_expand.py` | 扩库执行器：写新 `SKILL.md`（已存在即跳过）+ 更新 `domains/_registry.md` | `gen_run.py` |
| 6 | `scripts/_build/v3/step30_opt_s.py` · `_f.py` · `_r.py` | 优化基线内容表：每个 skill 的「方法库 · 判定细则」+「示例 2」——纯数据 | `gen_opt_*.py` |
| 7 | `scripts/_build/v3/step31_inject.py` | 幂等注入方法库与示例 2；清理输出示例中的自指涉 | `gen_opt_run.py` |
| 8 | `scripts/_build/v3/step40_dut_deep.py` | 改造 skill 的 DUT 特化加深 | `gen_dut_deep.py` |
| 9 | `scripts/_build/v3/step41_docs_counts.py` | 文档计数级联：52→92 ｜ 2–3→4–5 ｜ 自建 40→80 | `gen_docs_counts.py` |
| 10 | `scripts/_build/v3/step42_cmd_cards.py` | 20 张域入口卡第 3 步升级为「全量库内择优」 | `gen_cmd_cards.py` |
| 11 | `scripts/_build/v3/step43_slashfix.py` | 路径反斜杠归一（幂等兜底） | `_slashfix.py` |
| 12 | `scripts/_build/v3/step44_checker_thresholds.py` | 校验器阈值同步（52→92） | `gen_counts.py` |
| 13 | `scripts/_build/v3/step50_self_evolution.py` | **习惯自迭代机制**：新增 `library/skill-evolution.md`（1 级库第 6 份规则）+ 20 域执行顺序接线 + `regress.sh [8]` 边界段 + `runcheck` 接线断言 | 新增层 |
| 14 | `scripts/_build/v3/step51_version_bump.py` | **版本号与计数级联**：包版本 → `3.2`（两位 · 展示位）／修订号 → `3.2.0`（三位 · 字段与断言）；`library` 文件数 9 → 10 | 新增层 |
| 15 | `scripts/_build/v3/step52_requirement_confirm.py` | **需求确定门**：`library/clarity.md` §3.1（理解准确率 `C = 1 − U`，三档 0.95 / 0.70）+ `config.yaml` 阈值 + `regress [9]`；修订号 → `3.2.1` | 新增层 |
| 16 | `scripts/_build/v3/step53_checkup_flow.py` | **自检查流程加固**：新增 `scripts/checkall.py`（单入口 · 逐项计时 · 模拟跑摘要）与 `scripts/negative_test.py`（负向自测 · 断言非空转）+ 需求确定门算例（例 D/E）+ `aligncheck` 口径断言；修订号 → `3.2.2` | 新增层 |
| 17 | `step54_blindrun_fixes.py` · `step55_realrun_fixes.py` · `step56_v325_release.py` | 盲跑 / 真实问题归因修复 + v3.2.5 工程化迭代（隔离断言 · L3 共现规则 · 指标埋点）；修订号 `3.2.2 → 3.2.5` | 新增层 |
| 18 | `step57_risk_fixes.py` · `step58_readme_download.py` | 风险自检修复（记忆不跟踪 · 交付剔除 `.gitignore`）+ README 下载区；修订号 `3.2.5 → 3.2.7` | 新增层 |
| 19 | `step59_link_integrity.py` · `step60_url_audit.py` | 链接可用性修复（URL 边界归一 · 仅 HTTP 标注 · 排查话术）+ 外链核验订正（教务裸根 404 · 信息库 5 处事实订正 · 三通道复核）；修订号 `3.2.7 → 3.2.9` | 新增层 |
| 20 | `step61_external_bridge.py` | **外部 skill 桥接（大改）**：降级链**两档 → 三档**（同域库内 → 外部桥接 → 纯提示词）· 12 平台入口表 `references/external-sources.md` · 1 级规则 `library/external-bridge.md` · 第 6 个校验器 `scripts/extskill.py` · 20 域 `## 外部承接` · 92 个 skill 降级段改写 · `library` 规则数 10→11；**包版本 `3.2 → 3.3` / 修订号 → `3.3.0`** | 新增层 |

**版本号口径（v3.2 起统一）**：**包版本 = `3.2`**（两位，用于 README 标题 / 包根 `SKILL.md` 标题 / `qihang.sh` 状态行 / `config.yaml` 首行注释）
｜**修订号 = `3.2.2`**（三位，用于 92 个库内 `SKILL.md` frontmatter、包根 `SKILL.md` frontmatter、`.codebuddy-plugin/plugin.json`、`config.yaml` 的 `version:`、`aligncheck.py` 期望值）。
**包版本 = 修订号前两位**，同一包版本线内**修订号递增**；由 `aligncheck.py` 硬断言「展示位必须是两位形态」。
历史陈述（如 `自 v3.0.0 起…`）描述的是**当时的变更**，不追改。

> ⚠️ **归一格式，不归一版本值**：任何「头部/整块归一」的层（如 step51 处理 `config.yaml`）必须**保留文件里既有的修订号**，
> 否则会把更靠后层升过的版本**改回去**（实测：3.2.2 被改回 3.2.1 → 全链第 1 遍变更 1 个文件）。

**判据**：本链在**已达 v3.2** 的树上重跑应**零变更**；全链连跑两遍，逐文件哈希一致；
产物通过 `scripts/checkall.py .`（内部即跑齐 `selfcheck.sh` · `audit.sh` · `aligncheck.py` · `runcheck.py` · `regress.sh`），
可用 `--negative` 追加负向自测。

---

## 交付副本（两树归并）

`release/` 下三件套负责「源仓库 → 交付副本」：

```bash
python scripts/_build/v3/release/sync_release.py <源仓库> <交付副本> --apply
python scripts/_build/v3/release/finish.py       <源仓库> <交付副本>
python scripts/_build/v3/release/verify.py       <源仓库> <交付副本>
```

| 脚本 | 作用 |
|---|---|
| `scripts/_build/v3/release/sync_release.py` | 逐字节比对 + 同步（排除 `_build` / `.git` / `.learnbuddy`；过程文档由 `.gitignore` 派生） |
| `scripts/_build/v3/release/finish.py` | 同步 `.gitignore` / `.gitattributes` 到副本；把过程文档移出副本（move 到 `%TEMP%`，不删） |
| `scripts/_build/v3/release/verify.py` | 终检：交付树 = 源仓库 − 过程文档，逐字节一致 |

**与 `scripts/_build/make_release.py` 的分工**：`make_release.py` 是**正式导出器**
（真相源 = git 索引 ∩ 磁盘 − `.gitignore`）；本目录的 `release/` 是**开发期两树归并**。
两者不要互相替代；排除清单只写在 `.gitignore` 一处，**不在此另建第二份**。

---

## 已知缺口（从零复现不完整，需人工介入）

1. **外部 skill 抓取层未收编**。12 个改造 skill 的**成品**已入库，`step11` 只做登记；
   其**原始素材抓取**当时依赖 GitHub 检索脚本，未随包收编。即：本链能重跑**内容与结构**，
   但「从零拉取外部最优解」这一段不可离线复现（符合本包「运行时零外部依赖」的定位）。
2. **`step41` / `step44` 是「旧基线补丁」型**（52→92）。在已达 92 的树上重跑全部报 MISS，
   属正常（无副作用）；若从旧基线（52）起跑则正常生效。
3. **阴性测试**（`scripts/_build/v3/tests/`）需要 Git Bash 与可用的 `scripts/regress.sh`：

   ```bash
   python scripts/_build/v3/tests/negtest.py          # 注入 4 类缺陷 → checker 应 FAIL → 还原
   python scripts/_build/v3/tests/negtest_fallback.py # 移走 library/general-fallback.md → [5] 段应 FAIL
   ```
