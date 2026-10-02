# 构建期生成器（非运行期）

> **修改 19 个域时用这里，不用于日常运行。**

| 脚本 | 作用 | 何时跑 |
|---|---|---|
| `build_qihang_v2.py` | 生成 1 级库 + 19 域骨架 + 私密站清单 | 改 `DOMAINS` 后 |
| `build_qihang_v2_extras.py` | 生成 config / 21 个命令 / qihang.sh / README | 接上一个 |
| `build_phase1.py` | 给 19 个库内 skill 补可执行示例 + 4 域安全护栏 + 用例集/校验清单 | 接上一个 |
| `build_phase2.py` | 给 19 个 external.md 补许可证列与合规标注 | 接上一个 |
| `build_phase3.py` | **复核修复层**：澄清门公式 / 红线体系(19域) / 域档案矛盾 / 触发词消歧 / 降级链 / 校验清单扩展 | 接上一个 |

**严格顺序（v2.11 全量）**：`v2 → extras → phase1 … phase19`

```bash
for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do
  case "$p" in v2|v2_extras) f="build_qihang_${p}.py" ;; *) f="build_phase${p}.py" ;; esac
  python "scripts/_build/$f" .
done
python scripts/_build/build_phase19.py .   # 链末结构层（单独跑，见文末说明）
bash scripts/selfcheck.sh && bash scripts/audit.sh   # 跑完必自检
```

| 层 | 作用 |
|---|---|
| `build_phase4`–`build_phase12` | 复核修复与文档同步（v2.2–v2.6 各轮） |
| **链末收敛层** | **`phase17` / `phase18` / `phase19` —— 历史层（phase1–16）可留 MISS；v2.11 起链末为 `phase19`，判据 = 它报 0 未命中 + 四项校验器全绿 + 两遍哈希一致** |
| **`build_phase13`** | **库内 skill 扩容：每域 1 → 2（共 38）** |
| **`build_phase14`** | **库外候选多源比对 + 选优 + 生成 `skill-matrix-v3.md`** |
| **`build_phase15`** | **复查修复层（v2.6 → v2.7，21 条缺陷 / 20 组修复）** |
| **`build_phase16`** | **LearnBuddy 专向化层（v2.7 → v2.8）：移除 Claude Code 适配 + `commands/` 改写为域入口卡** |
| **`build_phase17`** | **漏检缺陷修复层（v2.8 → v2.9）：检查器全量化 · L3 清单去重 · 口径统一 · `qihang.sh` 可复现性** |
| **`build_phase18`** | **规则可执行性修复层（v2.9 → v2.10）：裸词澄清 · 澄清门 cᵢ 判定细则 · 域冲突对齐 · 无对口 skill 降级链 · 红线体系补漏** |
| **`build_phase19`** | **结构优化层（v2.10 → v2.11）：消除同名双入口 · 开发侧过程文档移出版本控制 · 补 LICENSE/CHANGELOG/THIRD_PARTY_NOTICES · 校验器补盲** |

✅ **全量重跑已安全**（v2.9 起）：
- `build_qihang_v2.py` 改为**暂存目录生成 + 逐文件覆盖**，不再 `rmtree` 目标目录
  （旧版会把整个仓库删空，含 `.git`，实测 161 文件 → 0）；
- `references/dlut-login-sites.md` 的 §0.1/§0.2 手工增补由 `build_phase17.py` **幂等补回**；
- 链末 `build_phase17.py` 负责平台口径兜底、授权清单收敛、计数与去重归一化。

**验证口径**：全链连跑两遍，逐文件哈希应**完全一致**（实测 161 文件 0 变更），
且产物需通过 `selfcheck.sh` / `audit.sh` / `regress.sh` / `aligncheck.py` 四项。

---

## v2.11 链末结构层（`build_phase19.py`）

`phase19` 是 v2.11 新增的**链末层**，跑在 `phase18` 之后。上面的循环行只到 `18`
（**刻意如此**：`phase17` 对那行的完成判据是固定文本，追加 `19` 会让它每轮报未命中），
所以 `phase19` 单独一行执行。完整序列（v2.11 全量）：

```bash
for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do
  case "$p" in v2|v2_extras) f="build_qihang_${p}.py" ;; *) f="build_phase${p}.py" ;; esac
  python "scripts/_build/$f" .
done
python scripts/_build/build_phase19.py .
bash scripts/selfcheck.sh && bash scripts/audit.sh
```

本层负责：

- **唯一入口**：包根 `SKILL.md` 是唯一安装单元；`library/` 提供不带 `name` 的导航页。
  每轮链都会重新生成 `library/` 下的同名入口文件，故本层**每轮都要再退役一次**
  （移到 `%TEMP%/qihang-retired/<本次运行>/`，不删，可取证回滚）。
- **过程文档出库**：8 份评审 / 审计 / 验收 / 需求书写进 `.gitignore`（文件留在磁盘，链照跑）。
- **声明类文件**：`LICENSE` / `CHANGELOG.md` / `THIRD_PARTY_NOTICES.md`。
- **校验器补盲**：`selfcheck.sh` 新增 `[8b] 入口唯一性与声明`；`aligncheck.py` 排除未分发文档。

**⚠️ 本层只写 `.gitignore`，不执行任何 git 命令。** 首次启用需人工执行一次
「把 8 份开发侧过程文档移出版本控制」（`git rm --cached`，幂等）：

```bash
# 路径从 .gitignore 派生（单一真相源），不在此重复枚举：
git rm --cached -q -- $(grep -E '^references/.*[.]md$' .gitignore)
```

---

## 发布副本构建器（`make_release.py`）

`scripts/_build/make_release.py` 把本仓库导出为**只含交付物**的发布副本：

```bash
python scripts/_build/make_release.py [目标目录]   # 默认 ../qihang-pack-release
```

- **导出集合的唯一真相源是 git + `.gitignore`**：
  `git ls-files --cached --others --exclude-standard` ∩ 磁盘存在，
  再减去 `scripts/_build/`、`.gitignore`、`.gitattributes`。
  「什么不进交付物」只写在 `.gitignore` 一处 —— **不要在本目录另建第二份排除清单**
  （v2.10 前的发布器就是硬编码了一份，实测漂移过）。
- **两处必须对齐的口径差异**（均已踩过，勿删代码里的相应处理）：
  · git 索引里可能仍有「已从磁盘删除」的路径（如 v2.11 退役的 `library/` 下同名入口文件）
    → 枚举时必须与磁盘取交集，否则 `copy2` 直接 FileNotFoundError；
  · `.learnbuddy/`（AI 工作记忆）**被 git 跟踪、却不在 `.gitignore`**
    → 需按目录名显式滤掉，否则 2 份记忆日志会被打进交付物。
- **覆盖式导出必须配「陈旧文件移出」**：导出不删目录，所以「上版有、本版没有」的文件
  会静默留在交付物里（实测：旧副本留着已退役的 `library/` 下同名入口文件，
  正是「同名双入口」缺陷本身）→ 由 `prune_stale()` 移到 `%TEMP%/qihang-release-retired/`。
- **发布期改写不回写仓库**：副本里 `selfcheck.sh` 的 `[8b]`（依赖 `.gitignore`）与
  `aligncheck.py` 关联的文件总数口径都不同，由本工具在导出时改写。
- 导出后在副本内实测四条命令验收：
  `bash scripts/selfcheck.sh` · `bash scripts/audit.sh` · `bash scripts/regress.sh 3` ·
  `python scripts/aligncheck.py`。
