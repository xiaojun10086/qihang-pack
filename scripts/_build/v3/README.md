# v3.0.0 生成链（收编层）

> **本目录是 v3.0.0 的生成器**。改域 / 改 skill 内容时改这里的**数据表**再重跑，
> 不要手改 `domains/*/skills/local/*/SKILL.md`。
>
> 与上一级 `scripts/_build/`（`build_qihang_v2.py` + `build_phase1.py` … `build_phase19.py`）
> 的关系：**那套是 v2.x 历史层**（模型停在 19 域 / 38 skill / v2.11），**只读保留、勿直接重跑**；
> 本目录才是 v3.0.0 的现行链。详见上一级 `scripts/_build/README.md` 的「历史层」段。

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

**判据**：本链在**已达 v3.0.0** 的树上重跑应**零变更**；全链连跑两遍，逐文件哈希一致；
产物通过 `scripts/selfcheck.sh` · `scripts/audit.sh` · `scripts/regress.sh` ·
`scripts/aligncheck.py` · `scripts/runcheck.py`。

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
