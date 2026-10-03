# 构建期生成器（非运行期）

> ## ⚠️ 版本分层（v3.0.0 起）
>
> | 层 | 位置 | 状态 |
> |---|---|---|
> | **现行链（v3.0.0）** | `scripts/_build/v3/` | ✅ 改内容改这里；单入口 `scripts/_build/v3/rebuild.py` |
> | **历史链（≤ v2.11）** | 本目录 `build_qihang_v2.py` + `build_phase1.py` … `build_phase19.py` | 🔒 **只读保留**。模型停在 **19 域 / 38 skill / v2.11** |
>
> **禁止在 v3.0.0 的树上直接重跑历史链**：它会把共享文件（`library/*`、
> `domains/_registry.md`、`README`/`INSTALL` 计数、`scripts/selfcheck.sh` 阈值…）
> **回退到 v2.11 口径**，把已是 20 域 / 92 skill 的树改坏。
> 历史链只在「想复盘 v2.11 生成过程」时对着 **v2.11 基线树** 使用。
>
> 本文件以下内容均为**历史链（v2.x）**的记录，保留原样以便追溯。

---

## 发布方式（**v3.2.5 起：单仓库双分支**）

> 此前是「源仓库目录 + 交付副本目录」两棵树（`qihang-pack` / `qihang-pack-release`），靠
> `v3/release/sync_release.py` 单向下发、`verify.py` 逐字节终检。**该线已退役**（脚本保留为历史）。
> **v3.2.5 起改为一个仓库两条分支** —— 交付物由 git 跟踪状态保证纯净，不再手工维护排除表。

| 分支 | 角色 | 内容 |
|---|---|---|
| `main` | **开发树**（唯一真相源） | 全部内容：含生成器 `scripts/_build/`、记忆 `.learnbuddy/`、过程文档 |
| `release` | **纯净交付树（直接分发给用户）** | `main` 的跟踪树 − `scripts/_build/**` − `.learnbuddy/**` = **174 文件** |

```bash
python scripts/_build/v3/release/release_branch.py            # 只比对（默认，零副作用）
python scripts/_build/v3/release/release_branch.py --apply    # 刷新 release 分支
git push origin main release                                  # 发布
```

### 改 `main` 之后，`release` **不会自动同步**（刻意如此）

- **同步动作是显式的**：只有跑 `--apply` 才刷新。不跑 = release 停在旧内容，**且不会有任何提示**。
- **判据是「内容」不是「提交」**：工具比对的是**交付文件集合**的树。只改 `.learnbuddy/`（记忆）或
  `scripts/_build/`（生成器）时，**即使 main 领先 release 好几个提交，差异项仍是 0、无需刷新**；
  反之只要动了交付文件（`domains/` `library/` `commands/` `scripts/`(非 _build) `SKILL.md` `config.yaml` …）就必须刷新。
- ⚠️ **别用 `git diff release..main` 判断「要不要同步」**：它永远会列出 `.learnbuddy/**` 与 `scripts/_build/**`
  （那正是排除项），看着像「积压一大堆」，其实与交付无关。**只看工具的「差异项 = 0 / N」。**
- **`--apply` 的「防误删闸」**（2026-10-03 实测事故换来）：
  · 交付文件数 < **150**（当前 174）→ 中止（几乎必然是 main 树被误删）
  · 差异里出现任何 **D（删除）** → 中止，并提示如何在 main 上修回；确要删除须加 `--allow-delete`
  · 只比对模式同样提示但不改动；`--apply` 被拦时返回 **rc=2**
  · **为什么需要它**：worktree 里少了文件（如刚 `git checkout release` 过、或写入被中断）时，
    一条 `git commit -a`（= `git add -u`）会把「缺失」当成**删除**提交进 main，本工具会**忠实照搬** →
    交付包静默少核心文件。工具没错（garbage in, garbage out），但「照搬误删」必须在刷新前挡住。
- **为什么不做成自动**（提交即刷 / post-commit hook）：① 会把**半成品**（WIP 提交）也推进交付分支；
  ② 每轮都产生一个 release 提交，历史噪声大；③ 出问题时难定位「是哪个 main 提交导致的」。
  **推荐节奏：一批改动收口 → 看差异 → `--apply` → `push`。**
- 刷新只写**本地** release 分支的提交；**真正到用户手里还要 `git push origin release`**
  （用户侧用 `git clone -b release` 或 `git archive release | tar -x` 拉取）。

**纯净性由 git 跟踪状态保证**（比手工排除表可靠）：`references/` 下 8 份过程文档、
`__pycache__`、`.idea`、`.vscode`、`*.pyc` **均未被 git 跟踪** → 天然不进 `release` 分支。
`release_branch.py` **从不触碰工作树与真实索引**（`GIT_INDEX_FILE` 指向临时索引：
`read-tree(main) → rm --cached(排除项) → write-tree → commit-tree → update-ref`），
因此可随时重跑、零数据丢失风险。

- ⚠️ **不要用 `git merge main`**：`.learnbuddy` 每轮都在改而 release 上无此路径 → modify/delete 冲突；
  且 main 新增的 `_build` 文件会被并进 release，破坏纯净性。
- ⚠️ **不要在日常工作树里 `git checkout release`**：`.learnbuddy/` 与 `scripts/_build/` 在 main 上被跟踪，
  检出 release 时会被从磁盘移除（切回 `main` 即恢复）。查看 / 分发包请用
  `git archive release | tar -x -C <目录>` 或 `git clone -b release <url>`。

---

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
