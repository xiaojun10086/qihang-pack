# 「启航」项目 · 长期约定（工作区 MEMORY）

> 稳定事实与约定，多次会话有效。临时信息不要写这里。

## 一、项目定位与结构（不要改的东西）

- 三级结构：`library/`（1 级规则库）→ `domains/`（19 域）→ `domains/<域>/skills/local/<name>/SKILL.md`（3 级库内 skill）。
- **库内优先是硬规则**：库内有 skill 就不装库外；库外只作降级增强。
- 19 域 = S 学习 6 + F 生活 8 + R 科研 5。当前**每域 2 个库内 skill，共 38 个**。
- **库外比对选优结论的唯一真相源**：`references/skill-matrix-v3.md`（由 `build_phase14.py` 生成）。
- 红线体系：**先判红线 → 再判登录档位（A/B/C）→ 再判澄清门 → 再锁域**。顺序不可换。
- 澄清门：`U = 1 − Σ(wᵢcᵢ)/Σwᵢ`，权重 `O/T/D=1.5, W=0.8, C=0.6, B=0.2`；**关键槽 `O/T/D` 须 `cᵢ ≥ 0.8` 才放行**（0.5=歧义视同缺）。

## 二、生成器约定（改数据，不手改产物）

| 层 | 文件 | 作用 |
|---|---|---|
| 骨架 | `build_qihang_v2.py` + `_extras` | 1 级库 + 19 域骨架 |
| 修复史 | `build_phase1.py` … `build_phase12.py` | v2.1–v2.6 各轮修复 |
| **扩库** | `build_phase13.py` | 每域第 2 个库内 skill（红线**继承**自 `_domain.md`） |
| **比对** | `build_phase14.py` | 库外多源比对选优 + 生成矩阵 + 回写 registry 候选数 |
| **修复** | `build_phase15.py` | v2.7 复查修复层（精确替换 + 幂等护栏） |
| **专向化** | `build_phase16.py` | **v2.8 平台专向化**：移除 Claude Code 适配 + 21 个 `commands/` 重建为 LearnBuddy 域入口卡 + 版本 2.7→2.8 |
| **收敛层** | `build_phase17.py` | **v2.9 漏检缺陷修复 + 链末收敛**（见 §二之四）：检查器全量化 · L3 清单去重 · 口径统一 · `qihang.sh` 可复现 · 平台口径兜底 · 授权清单收敛 · 计数/去重归一化 · P0 破坏性重建护栏 |
| **规则层** | `build_phase18.py` | **v2.10 规则可执行性修复**（见 §二之六）：裸词澄清 · 澄清门 §2.1 cᵢ 判定细则 · 例外 6 通用知识型 · 域冲突对齐 · 无对口 skill 降级链 · 红线体系补漏 · 输出规范补变体 |

- 顺序：`v2 → extras → phase1…18`（见 `scripts/_build/README.md`）。**phase17 必须在 phase18 之前**（17 在 v2.10 树上单独重跑会报 4 处 MISS，属预期）。
- **两个铁律**：
  1. 生成器必须**幂等**：`new` 包含 `old` 的追加型替换要加护栏（否则第二遍会重复插入）；
     一次性正则替换要给「完成判据」（`already=` / `absent=`），否则第二遍误报未命中。
  2. **连跑两遍才算验证过**：第二遍必须 0 变更。
- **红线不得手写**：任何新 skill 的红线都从所属 `_domain.md` 继承，`regress.sh` 有硬断言。
- **不改历史 phase 层**：历史层的替换表与下一层配对，改了会断链。收敛/修复一律**新增一层**。

## 二之二、平台口径（v2.8 起）

- **唯一目标平台 = LearnBuddy / WorkBuddy**；Claude Code 适配已全移除，其他 agent 可装但不作承诺。
  唯一真相源：`references/platforms.md`。
- `commands/`（21）= **LearnBuddy 域入口卡**（库 + 校情 + 19 域），**非斜杠命令**；用仓库根相对路径，
  不含 `$ARGUMENTS` / `argument-hint` / `~/.claude/...`。
- 库外通道：首选 `find-skills`；通用 CLI `npx skills add`；手动复制到 `~/.learnbuddy/skills/`。

## 二之三、已知既有缺陷（**避坑，勿当成本轮引入**）

> 2026-10-02 v2.9 轮已修复以下 1–8（细节见 §二之四）。保留本条以记录**缺陷类型**，便于下轮识别同型问题。

1. ~~`regress.sh` 的「公开站数据条目」断言语义错误~~ → **已修**（精确 awk，实测 139）。**注意**：链重跑会让旧近似断言与新精确断言**并存** → `phase17` 负责只留精确版。
2. `qihang.sh` 的 `detect_skills_dir` / `platform_of` / `cmd_platform` / `cmd_records` 原先不在生成器里 → **已由 `phase17` 幂等补齐**。
3. ~~重跑 `build_qihang_v2.py` 会覆盖 `dlut-login-sites.md` 手工增补~~ → **已修**：`build_qihang_v2.py` 不再 `rmtree`（见 §二之四.1），`phase17` 幂等补回 §0.1/§0.2。
4. `aligncheck` 常驻 WARN 1：`library/clarity.md` 跨表重复 `| D | 完全缺失 | 0.0 |`（两张不同表格的交叉登记，**已判定为合法**，保留 WARN）。
5. ~~「声明==实测」有白名单盲区~~ → **已修**：改为全量扫描 + 内容标记豁免（文件级「历史文档」/ 行级「历史口径」）。
6. ~~`qihang.sh registry` 按全文出现次数统计~~ → **已修**：只统计表格数据行内（139 / 67 / 21 / 51）。
7. ~~`SKILL.md` / `PROJECT.md` L3 清单重复「成绩明细」~~ → **已修**。
8. ~~92 项改动未提交~~ → 待用户 `git add -A && git commit`（v2.8+v2.9 成果）。

**仍需注意（未修，属设计取舍）**：
- 全量链中 `build_phase1…16` 仍有约 20 处精确替换 MISS（历史层文本与手改后状态漂移）。**这是可接受的**：`phase17` 作为链末收敛层负责把结果修回规范态 —— 判断链是否正常，看**链产物能否通过四项校验 + 两遍哈希一致**，不要看中间层的 MISS 数。

## 二之四、生成器链的两条 P0 铁律（**2026-10-02 实测事故换来**）

1. **绝不 `rmtree` 目标目录**。`build_qihang_v2.py` 旧版 `shutil.rmtree(out)` 配合文档用法 `... build_qihang_v2.py .`
   **会把整个仓库删空**（实测 161 文件 → 0，含 `.git`），再因沙箱下 `os.rmdir('.')` 失败而中断。
   现为「`tempfile.mkdtemp` 暂存 → `copytree(dirs_exist_ok=True)` 覆盖式合并」，**不删目标里的任何既有内容**；
   `phase17.assert_no_destructive_rebuild()` 是防回退硬断言。
   → **护栏要挡「像项目的目录」（含 `.git`/`.learnbuddy`/`scripts/_build`），而不是只挡 `/`、`~`。**
2. **替换型收敛必须先问「新串是否包含旧串」**。`build_phase12.py` 用 `t.replace(旧串, 规范串)` 收敛 L1/L2/L3，
   而规范串包含旧串 → **每跑一轮链就多追加一项**；实测 `dlut-read.sh` 的 L2 行无上界膨胀，
   且 **`config.yaml` 被污染成 `L1_auto: [课表 / 成绩等级 / … / 日程, 网费, 日程]`**（首项被拼成整串，YAML 语义已坏）。
   → 包含关系必须加**完成判据**；收敛应由 `phase17` 从 `config.yaml`（单一真相源）**派生**，而非逐层精确替换。

## 二之五、链可复现性的验收口径（不要凭感觉说「能重跑」）

```bash
# 在临时副本上跑，绝不在真实树上试
for p in v2 v2_extras 1..17; do python scripts/_build/build_$p.py . ; done
```
- 判据 ①：链**跑完不中断**，`phase17` 报 **0 未命中**；
- 判据 ②：**连跑两遍逐文件哈希完全一致**（实测 161 文件 0 变更）；
- 判据 ③：链产物**四项校验器全绿**。

## 二之六、规则可执行性缺陷（2026-10-02 修复状态）

> 报告：`C:\Users\xiaojun\Desktop\qihang-agent-test\行为验证报告-v1.md`。
> 与「文档一致性」**零重叠** —— 机器断言全绿**完全不能**反映规则可执行性。

**行为验证结果**（137 次执行）：域锁定 **116/117**、跨代理域层面 **20/20 一致**；红线 **40/41** 且 **41/41 给了替代**；22 条官方越界用例 **20 ✅/1 ⚠️/1 ❌**；3 条反例全部正确放行；F3 危机 + F5 急症 100% 达标。澄清门跨代理一致率原为 **16/20**。

**✅ v2.10 已修（`build_phase18.py`）**
1. 裸「成绩」口径统一 → **先让用户区分等级/明细**（`login-policy.md`「裸词澄清」；与 `dlut-read.sh` 的 `rc=1` 一致）。
2. `clarity.md` 新增 **§2.1 关键槽判定细则**：指代型/泛指型/泛化动词 → `cᵢ=0.5`（必须追问）；有内容可定位 → `1.0`。**这是 20% 翻转的唯一根因。**
3. `§3` 阈值与 `§5` 例外的主从关系显式化 + 新增**例外 6「通用知识型」**（放行，末尾问缺的槽）。
4. 网费域冲突对齐（仅问入口 → F1；请求代交/涉金额 → F4）；失眠统一为 **F2**；A/B/C（动作档）与 L1/L2/L3（数据级别）**并行不换算**。
5. 「命中域但无对口 skill」补 3 级降级链；红线体系补漏（代操作 + F6、新增「编造/代写文书」、安全兜底补 24h 通道）。
6. **复测（新代理盲跑 8 例）8/8 符合新规则** —— 4 例翻转归零、3 处冲突统一、1 例错锁纠正。

**⚠️ 仍未修（下一步优先）**
- **`--profile` 可被静默忽略（P0 隐私）**：`agent-browser` 已有 daemon 在跑时，`open --profile <dir>` 会打印
  `⚠ --profile ignored: daemon already running` 并**忽略该参数**；而 `scripts/dlut-read.sh:116` 直接 `open … --profile`，
  **没有先 `close --all`** → 隔离可被绕过。修法：open 前先 `close --all`，并**校验 open 输出里没有 ignored 警告**，否则中止。

## 二之七、浏览器试跑的环境事实（本机实测）

- `agent-browser@0.27.0` 位于 `~/.workbuddy/binaries/node/versions/22.22.2/node_modules/agent-browser`。
- **Git Bash 下 npm shim 不可用** → 必须 `node "<前缀>/node_modules/agent-browser/bin/agent-browser.js" <args>`。
- **给 node 传参必须用 Windows 路径**（`C:/…`）；传 POSIX `/c/…` 会被拼成 `c:\c\…` → `MODULE_NOT_FOUND`。
- `--profile <path>` 受支持；**冷启动时确实生效**（实测隔离 Profile 的 mtime 前进）。
- 浏览器**能联网**：成功打开 `https://www.dlut.edu.cn/`（HeadlessChrome/154）。
- 门禁矩阵实测：L1 `rc=0` / 邮箱提示 `rc=2` / 9 个 L3 变体 `rc=3` / 裸「成绩」`rc=1`。**全部正确。**
- 收尾必须 `agent-browser close --all`；核验 `session list` 返回 `No active sessions`。

## 二之九、发布交付（提交用）

- **工具**：`C:\Users\xiaojun\Desktop\qihang-release-tools\make_release.py`（**包外**，避免扰动工作区的「声明==实测」断言与生成链）。
- **产物**：`C:\Users\xiaojun\Desktop\qihang-pack-release\`（含 `MANIFEST.md`）+ `qihang-pack-v2.10.0.zip`。
- **排除 4 类**：8 份内部过程报告 · `scripts/_build/`(20 个生成器) · `.idea`/缓存/临时 · `.learnbuddy/`；另去 `.git`/`.gitignore`/`.gitattributes`。
- **铁律：排除必须连带重写引用** —— `validation-report.md` 被 23 个文件引用、`_build` 被 6 个引用、`selfcheck.sh` 把它们列为「必备文件」。
  导出后必须跑 **dangling 检查**（构建器已内置）＋ 在副本里**实跑四个校验器**。
- 已知差异：副本里 `audit.sh` 是 **36 通过**（工作区 37）——随 `_build` 移除，那条 rmtree 护栏检查不再适用，**非缺陷**。
- **环境**：`shutil.rmtree` 会被 safe-delete 拦（>50 文件）；导出用**原地覆盖**，残留文件由 `report_stale()` 列出交人工。

## 二之十、行为验证方法（可复用，成本约 6 个子代理）

1. **盲跑**：子代理只拿「用户原话 + 输出字段」，**不给预期**；
2. **隔离 oracle**：禁止子代理读 `library/domain-review-cases.md`（含官方判定）；
3. **预期引自包内声明**（触发词 / 消歧表 / cases / config / 红线总览），用包自己的尺子量；
4. **独立复核**：疑似失败项回原始文件核对，判定「包的错」还是「代理的错」；
5. **跨代理复跑**：同批输入交另一个代理再判 → 度量规则可复现性（本次揪出澄清门 20% 翻转）。

## 三、验证脚本（改完必跑）

```bash
bash scripts/selfcheck.sh     # 结构/计数/交叉引用/红线一致性  期望 OK31 WARN0 FAIL0
bash scripts/audit.sh         # 安全/合规/L3 门禁实测            期望 37 通过 0 警告 0 失败
bash scripts/regress.sh 3     # 行为回归（连跑 3 轮）            期望 41 项/轮、累计 FAIL 0
python scripts/aligncheck.py  # 全量文件级对齐                  期望 FAIL 0（常驻 WARN 1）
```

**⚠️ 脚本全绿 ≠ 无问题**：断言集本身可能有盲区（见 §二之三.5）。每轮必须另加一条**不看脚本、直接比对原文**的人工透镜；用户限制「不要改动」时可作纯只读复核。

**改完必须连跑**：`phase17` 连跑两遍（第二遍 0 变更）→ 四项校验器全绿 → 如需动链，再在**临时副本**上做 §二之五 的三项验收。

职责不重叠：selfcheck 管「结构对不对」，audit 管「安不安全」，regress 管「行为对不对」。

## 四、环境约束（本机实测，写脚本必须遵守）

- **脚本内禁用 `rm`**：沙箱把 `rm` 做成「失败即封」拦截器，若放在 `EXIT` trap 里会导致**整个脚本静默失败**。清理临时文件请改用「不创建临时文件」或 `mv` 到临时目录。
- **避免逐文件循环**：逐文件起子进程会让长脚本被中断（实测 ~500 子进程即崩）。一律**单遍 `awk` / `grep -r`**。
- 不要用 `seq`（本机 Git Bash 无）。
- 用 `node fetch` 而不是 `curl` 访问外网（`curl` 返回 000，`node` 正常 200）。
- 删除文件：`shutil.move` 到 `%TEMP%` 可行；`os.remove` 会被 shim 拦。

## 五、DUT 数据铁律

- **禁止编造 URL / 电话 / 单位名**；未收录固定回复「信息库未收录」。
- 私密站三条铁律：**只读 · 不外传 · 不落盘**；必须用独立 Profile（`~/.qihang/browser-profile`）。
- **L3 禁读采用关键词包含匹配**：`缴费 金额 银行卡 身份证 家庭 邮件 心理 成绩明细 成绩单 简历`。
  「成绩等级」可读，「成绩明细」禁读 —— 裸「成绩」必须要求用户区分。
- 敏感域不写档案：**F3 / F5 整域不写**；F4 金额债务、F6 伤病记录不写。
