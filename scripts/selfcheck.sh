#!/usr/bin/env bash
# 「启航」学伴包 · 自检脚本
# 用法: bash scripts/selfcheck.sh
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
# 本脚本**不创建任何临时文件**（旧版为 TMP="${ROOT}/.selfcheck.tmp"）。
# 原因（实测）：部分受限环境把 rm 做成"失败即封"的拦截器，
# 旧版在 EXIT trap 里 rm 临时文件，会导致**整个脚本静默失败、零输出**；
# 旧版还把 .selfcheck.tmp / .selfcheck.tmp.refs 留在仓库根目录。

# ---------- 排除口径（单一真相源，供 [4] / [7] 复用）----------
# 开发树特有内容**不随包分发**，不得参与「产品文档交叉引用 / 阈值一致性」判定。
# 判据必须两边等价：交付副本既无 .learnbuddy / .git，也无生成器链 scripts/_build。
# 若源仓库把它们算进来，就会出现「副本全绿、源仓库假阳性 FAIL」的口径漂移。
#   _EXDIR = 开发树 / IDE / 记忆目录（含生成器链 scripts/_build）
#   _EXDEV = .gitignore 明列「未随包分发」的过程文档（评审 / 审计 / 验收 / 需求书）
_EXDIR="--exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea --exclude-dir=_build"
_EXDEV=""
for _g in $(grep -E '^references/.*[.]md$' .gitignore 2>/dev/null); do
  _EXDEV="$_EXDEV --exclude=$(basename "$_g")"
done

P=0; W=0; F=0
ok()   { printf '  OK   %s\n' "$1"; P=$((P+1)); }
warn() { printf '  WARN %s\n' "$1"; W=$((W+1)); }
bad()  { printf '  FAIL %s\n' "$1"; F=$((F+1)); }

echo "「启航」项目自检"
echo "========================================"

# ---------- 1. 必备文件 ----------
echo "[1] 必备文件完整性"
REQ="SKILL.md README.md INSTALL.md config.yaml
LICENSE THIRD_PARTY_NOTICES.md
library/README.md library/clarity.md library/domain-review.md library/output-spec.md
library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md
library/skill-evolution.md library/experience.md
domains/_registry.md
references/dlut-official-sites.md references/dlut-login-sites.md references/dlut-field-map.md
references/dlut-url-verification.md references/dlut-site-profiles.md references/browser-matrix.md
references/skill-compliance-audit.md
references/platforms.md references/e2e-scenarios.md
.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh scripts/audit.sh scripts/regress.sh scripts/aligncheck.py scripts/runcheck.py scripts/checkall.py scripts/negative_test.py scripts/metrics.py"
miss=0; cnt=0
for f in $REQ; do
  cnt=$((cnt+1))
  [ -f "$f" ] || { bad "缺失: $f"; miss=$((miss+1)); }
done
[ "$miss" -eq 0 ] && ok "全部 $cnt 个必备文件在位"

# ---------- 2. 20 域三级结构 ----------
echo "[2] 20 域三级结构"
# 改为单遍统计（原逐域循环会起 ~60 个子进程，受限环境易被中断）
nd=$(find domains -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
n_dom=$(find domains -maxdepth 2 -name '_domain.md' 2>/dev/null | wc -l | tr -d ' ')
n_lsk=$(find domains -path '*skills/local/*/SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
n_ext=$(find domains -path '*/skills/external.md' 2>/dev/null | wc -l | tr -d ' ')
nbad=0
[ "$nd" -eq 20 ] && ok "域数 = 20" || { bad "域数 = $nd（期望 20）"; nbad=$((nbad+1)); }
[ "$n_dom" -eq 20 ] && ok "20 个 _domain.md 在位" || { bad "_domain.md = $n_dom（期望 20）"; nbad=$((nbad+1)); }
[ "$n_lsk" -eq 92 ] && ok "92 个库内 skill 在位" || { bad "库内 skill = $n_lsk（期望 92）"; nbad=$((nbad+1)); }
[ "$n_ext" -eq 0 ] && ok "无库外通道 external.md（纯本地）" || { bad "仍存在 $n_ext 个 skills/external.md（应为 0）"; nbad=$((nbad+1)); }
[ "$nbad" -eq 0 ] && ok "所有域三级结构完整" || bad "$nbad 处缺失"

# ---------- 3. frontmatter ----------
echo "[3] SKILL.md frontmatter"
# 单次 awk 取代「逐文件 3 次 grep」（原为 ~120 个子进程）
_ff=$(awk '
  FNR==1{if(fn!="")chk(); fn=FILENAME; first=0; hasname=0; hasdesc=0}
  FNR==1 && $0 ~ /^---[[:space:]]*$/{first=1}
  /^name:/{hasname=1}
  /^description:/{hasdesc=1}
  END{if(fn!="")chk()}
  function chk(){ if(fn !~ /SKILL[.]md$/)return; if(!first||!hasname||!hasdesc) print fn }
' $(find . -name SKILL.md -not -path './dev/*' -not -path './proc/*' 2>/dev/null | sort) 2>/dev/null)
nf=$(find . -name SKILL.md -not -path './dev/*' -not -path './proc/*' 2>/dev/null | wc -l | tr -d ' ')
nfm=$(printf '%s\n' "$_ff" | grep -c . )
nfm=${nfm:-0}
if [ "$nfm" -eq 0 ]; then ok "$nf 个 SKILL.md frontmatter 全部合规"
else bad "$nfm 处不合规"; printf '%s\n' "$_ff" | head -6 | sed 's/^/       /'; fi

# ---------- 4. 交叉引用（零临时文件版） ----------
echo "[4] 文档交叉引用"
# 单遍 grep -r 取全部引用，再在 shell 内用内建 test 判定
# 扫描范围套用文件头的全局排除口径 $_EXDIR / $_EXDEV —— 记忆日志会「提及」文件名、
# 生成器链脚本会「生成」文件名，两者都不是产品文档引用，必须一并排除。
_refs=$(grep -rhoE '(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*]+[.]md' \
        --include='*.md' $_EXDEV $_EXDIR . 2>/dev/null | sort -u)
nbroke=0; nref=0
while IFS= read -r p; do
  [ -n "$p" ] || continue
  nref=$((nref+1))
  if [ ! -e "$p" ]; then
    nbroke=$((nbroke+1))
    [ "$nbroke" -le 8 ] && printf '       %s\n' "$p"
  fi
done <<< "$_refs"
# **裸文件名**引用（无目录前缀，如 `xxx-review.md`）同样必须存在。
# 原正则只认「带目录前缀」的路径，此类断链会被漏检（实测：曾有文件引用不存在的 review 副本）。
# 口径：只取反引号内、不含斜杠的 *.md 名，按「全仓库是否存在同名文件」判定。
# _BARE_SKIP = 故意不存在于仓库的名字（见 [5] 陈旧文件清单中的历史文件名，
#              以及 skill 示例里「运行时产物」的文件名，如学习档案 MISSION.md）
_BARE_SKIP="references/routing-table.md routing-table.md MISSION.md"
_bare=$(grep -rhoE '`[A-Za-z0-9][A-Za-z0-9_.-]*[.]md`' --include='*.md' $_EXDEV $_EXDIR \
        . 2>/dev/null | tr -d '`' | sort -u)
while IFS= read -r b; do
  [ -n "$b" ] || continue
  case " $_BARE_SKIP " in *" $b "*) continue ;; esac
  nref=$((nref+1))
  if [ -z "$(find . -name "$b" -not -path './.git/*' -print -quit 2>/dev/null)" ]; then
    nbroke=$((nbroke+1))
    [ "$nbroke" -le 8 ] && printf '       %s（裸文件名，全仓库无同名文件）\n' "$b"
  fi
done <<< "$_bare"
# 说明：路径字符集排除了 </>* 等，故「domains/<域>/_domain.md」这类**占位符**不会被误判为失效引用。
if [ "$nbroke" -eq 0 ]; then ok "无失效引用（检查 $nref 处）"
else bad "$nbroke 处失效引用"; fi

# ---------- 5. 陈旧文件 ----------
echo "[5] 陈旧 / 无关文件"
STALE="references/routing-table.md .extracted dev proc
scripts/__pycache__ 
"
ns=0
for f in $STALE; do [ -e "$f" ] && { warn "待清: $f"; ns=$((ns+1)); }; done
[ "$ns" -eq 0 ] && ok "无陈旧文件"

# ---------- 6. 脚本语法 ----------
echo "[6] 脚本语法"
for s in scripts/*.sh; do
  [ -e "$s" ] || continue
  bash -n "$s" 2>/dev/null && ok "$(basename "$s")" || bad "$(basename "$s") 语法错误"
done

# ---------- 7. 阈值 / 旧域名 / 红线去重 / 版本 / 清单 ----------
echo "[7] 一致性与红线"
# 口径与 [4] 统一：套用 $_EXDIR / $_EXDEV。
# 历史评审报告（如 review-report-v2.3.md）会**引用**旧阈值「U ≤ 5%」来记录"改了什么"，
# 过程文档本就不随包分发，不得算作残留 —— 原实现用 `grep -v 需求确认书` 硬编码文件名，
# 漏掉其余过程文档，导致源仓库假阳性 FAIL。
# clarity.md 单独豁免：它是唯一「口径沿革」正文（可能引用历史阈值作对照），属产品文档中的合法例外。
_bad_th=$(grep -rlE "(U ?[≤≥><]=? ?5%|U ?≈ ?0\.05|threshold: 0\.05)" \
          --include='*.md' --include='*.yaml' --include='*.html' --exclude=clarity.md \
          $_EXDEV $_EXDIR . 2>/dev/null | wc -l | tr -d ' ')
[ "${_bad_th:-0}" -eq 0 ] && ok "无旧阈值残留" || bad "$_bad_th 个文件仍有旧阈值（期望 0.30）"

_od=$(grep -rlnE '\b[A-G] 域\b' domains/ library/ SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "${_od:-0}" -eq 0 ] && ok "无 v1.1 旧域名残留" || bad "$_od 个文件含旧域名"

# 单遍统计（原逐文件 grep 为 ~95 个子进程）
_dup=$(grep -rc '^## ⚠️ 红线（不得绕过）' domains --include='*.md' 2>/dev/null \
       | awk -F: '$2>1' | wc -l | tr -d ' ')
[ "${_dup:-0}" -eq 0 ] && ok "无重复红线段" || bad "$_dup 个文件红线段重复"

# 单次 awk 检测「同一 skill 内红线条目重复」
_di=$(awk '/^## ⚠️ 红线/{inr=1;next} inr&&/^## /{inr=0}
  inr&&/^- /{k=FILENAME "|" $0; if(seen[k]++){print FILENAME; print FILENAME > "/dev/stderr"}}
' $(find domains -path '*skills/local*' -name SKILL.md 2>/dev/null | sort) 2>/dev/null \
  | sort -u | wc -l | tr -d ' ')
[ "${_di:-0}" -eq 0 ] && ok "红线条目无重复" || bad "$_di 个文件红线条目重复"

_nr=$(grep -rl '## ⚠️ 红线' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
[ "${_nr:-0}" -eq 20 ] && ok "域文件红线覆盖 20/20" || bad "域文件红线覆盖 $_nr/20"

# 库内 skill 的红线条目必须与所属域**逐条一致**（防措辞漂移）
# 单次 awk 完成全部比对：既快，也避免受限环境对子进程数的限制
_rd=$(awk '
  function save(f){S[f]=sig}
  FNR==1{if(prev!="")save(prev);prev=FILENAME;sig="";inred=0}
  /^## ⚠️ 红线/{inred=1;next}
  inred&&/^## /{inred=0;next}
  inred&&/^- /{sig=sig $0 "\n"}
  END{
    if(prev!="")save(prev)
    fail=0
    for(f in S){split(f,a,"/"); if(a[length(a)]!="_domain.md")continue
      d=a[1] "/" a[2]; ref=S[f]
      for(g in S){if(g==f)continue; split(g,b,"/")
        if(b[1] "/" b[2]!=d)continue; if(b[3]!="skills")continue
        if(S[g]!=ref)fail++}}
    print fail
  }' $(find domains -name '_domain.md' -o -name 'SKILL.md' 2>/dev/null | sort) 2>/dev/null)
if [ "${_rd:-0}" -eq 0 ]; then ok "库内 skill 红线与域文件逐条一致"
else bad "$_rd 处红线漂移"; fi

_v=$(grep -rhoE 'version: [0-9]+\.[0-9]+\.[0-9]+' --include=SKILL.md . 2>/dev/null | sort -u | tr '\n' ' ')
echo "   info 库内 skill 版本: $_v"

_l3=$(grep -c '成绩明细' config.yaml 2>/dev/null); _l3=${_l3:-0}
[ "$_l3" -ge 1 ] && ok "config L3 含「成绩明细」" || bad "config L3 缺「成绩明细」"
_l2=$(grep -c '邮箱未读提示' config.yaml 2>/dev/null); _l2=${_l2:-0}
[ "$_l2" -ge 1 ] && ok "config L2 含「邮箱未读提示」" || bad "config L2 缺「邮箱未读提示」"
# L3 关键词表必须**覆盖** config.yaml 的 L3_forbidden 全部条目（防「文档 7 项、脚本漏拦」）
# 实测踩过：脚本漏「绩点」（属成绩明细）、多「简历」（文档三处清单均无）。
_l3items=$(grep 'L3_forbidden:' config.yaml 2>/dev/null | head -1 | sed 's/.*\[//; s/\].*//' | tr ',' ' ')
_l3keys=$(grep -oE 'L3_KEYS="[^"]*"' scripts/dlut-read.sh 2>/dev/null | head -1 | sed 's/L3_KEYS="//; s/"$//')
_l3miss=0; _l3cnt=0
for _it in $_l3items; do
  _it=$(echo "$_it" | tr -d ' ')
  [ -z "$_it" ] && continue
  _l3cnt=$((_l3cnt+1)); _hit=0
  for _k in $_l3keys; do
    case "$_it" in *"$_k"*) _hit=1; break ;; esac
  done
  [ "$_hit" -eq 0 ] && { _l3miss=$((_l3miss+1)); echo "        未覆盖: $_it"; }
done
[ "${_l3miss:-0}" -eq 0 ] && [ "${_l3cnt:-0}" -ge 7 ] \
  && ok "L3 关键词表覆盖 config 全部 $_l3cnt 项" \
  || bad "L3 关键词表漏覆盖 $_l3miss 项（config 共 $_l3cnt 项）"
grep -q '最后 3 条是反例' library/domain-review-cases.md 2>/dev/null && bad "用例集反例表述过时" || ok "用例集反例表述正确"

# ---------- 7c. 隔离 / L3 判级 / 指标埋点 ----------
# 把临时 Profile、会话隔离与页面内容不采集等承诺变成可判 FAIL 的检查。
echo "[7c] 隔离 / L3 判级 / 指标埋点"
_iso1=$(grep -c 'SESSION_ID="qihang-' scripts/dlut-read.sh 2>/dev/null); _iso1=${_iso1:-0}
_iso2=$(grep -c 'PROFILE_DIR="$(mktemp -d' scripts/dlut-read.sh 2>/dev/null); _iso2=${_iso2:-0}
_iso3=$(grep -c 'rm -rf -- "$PROFILE_DIR"' scripts/dlut-read.sh 2>/dev/null); _iso3=${_iso3:-0}
_all=$(grep -c 'close --all' scripts/dlut-read.sh 2>/dev/null); _all=${_all:-0}
[ "$_iso1" -ge 1 ] && [ "$_iso2" -ge 1 ] && [ "$_iso3" -ge 1 ] && [ "$_all" -eq 0 ] \
  && ok "独立随机会话 + 一次性 Profile + 退出清理，不影响其他会话" \
  || bad "dlut-read.sh 缺少会话隔离 / Profile 清理护栏"
_iso2=$(grep -cE 'profile\[\[:space:\]\]\+ignored' scripts/dlut-read.sh 2>/dev/null); _iso2=${_iso2:-0}
_iso3=$(grep -c '^  exit 5$' scripts/dlut-read.sh 2>/dev/null); _iso3=${_iso3:-0}
[ "$_iso2" -ge 1 ] && [ "$_iso3" -ge 1 ] \
  && ok "隔离校验生效（扫描 ignored 警告 + rc=5 中止）" \
  || bad "dlut-read.sh 缺隔离校验（警告扫描 $_iso2 / rc=5 $_iso3）"
_capture=$(grep -cE '(^|[[:space:]])ab[[:space:]]+(snapshot|read)([[:space:]]|$)' scripts/dlut-read.sh 2>/dev/null); _capture=${_capture:-0}
[ "$_capture" -eq 0 ] && ok "网页内容不由脚本读取或打印" \
  || bad "dlut-read.sh 包含页面读取命令"
_l3b=$(grep -c '插入型变体' scripts/dlut-read.sh 2>/dev/null); _l3b=${_l3b:-0}
[ "$_l3b" -ge 3 ] && ok "L3 类 B 共现规则齐备（$_l3b 条）" \
  || bad "L3 类 B 共现规则不足（$_l3b 条，期望 ≥3）"
_mt1=$(grep -c '"leak":' scripts/metrics.py 2>/dev/null); _mt1=${_mt1:-0}
_mt2=$(grep -c 'QIHANG_TRACE' scripts/metrics.py 2>/dev/null); _mt2=${_mt2:-0}
[ "$_mt1" -ge 1 ] && [ "$_mt2" -ge 1 ] \
  && ok "指标脚本就位（机制字段埋点 + 可一键关闭）" \
  || bad "指标脚本缺埋点字段或开关（$_mt1 / $_mt2）"

# ---------- 8. 计数 ----------
echo "[8] 计数一致性"
nsk=$(find domains -path '*skills/local*' -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "${nsk:-0}" -eq 92 ] && ok "库内 skill = 92（每域 4–5 个）" || bad "库内 skill = $nsk（期望 92）"
# 单遍统计每域 skill 数（避免逐域起子进程）；每域应为 4 或 5 个
_pbad=$(find domains -path '*skills/local/*/SKILL.md' 2>/dev/null | awk -F/ '{print $2}' \
        | sort | uniq -c | awk '$1<4 || $1>5' | wc -l | tr -d ' ')
[ "${_pbad:-0}" -eq 0 ] && ok "每域均为 4–5 个库内 skill" || bad "$_pbad 个域的库内 skill 数不在 4–5"
libn=$(ls -1 library/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${libn:-0}" -eq 12 ] && ok "library 文件数 = 12" || warn "library 文件数 = $libn（期望 12）"
cmdn=$(ls -1 commands/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${cmdn:-0}" -eq 22 ] && ok "commands = 22" || warn "commands = $cmdn（期望 22）"
pub=$(grep -c '^|' references/dlut-official-sites.md 2>/dev/null); pub=${pub:-0}
echo "   info DUT 公开站表格行: $pub"
[ -f .codebuddy-plugin/plugin.json ] && ok "插件清单有效" || bad "插件清单缺失"

# ---------- 8b. 入口唯一性与声明 ----------
echo "[8b] 入口唯一性与声明"
# 堵住「同名双入口」盲区 —— 此前包根 SKILL.md 与 library/SKILL.md
# 都写 `name: qihang` 且红线表已分叉，而四个校验器当时**全绿**（纯结构性盲区）。
#
# ⚠️ 为什么编号是 8b 而不是 11（**锚点冲突，实测踩过**）：
#   phase15 用 `rep('# ---------- 11. 交付分支一致性（有 .git 时才查；交付树无 .git → 跳过） ----------
# 事故驱动（2026-10-03 两次）：release 分支被 git add -f 塞进 .learnbuddy/.idea/过程文档。
# 判据：release 树里**每个**文件都必须存在于 main（release ⊆ main 恒成立）——「只在 release 出现」即污染。
# ⚠️ 首版曾把 `.learnbuddy/` 等**预先过滤掉**，而它恰恰是最常见的污染源 → 断言对真实事故完全无效；
#    实测（故意污染 release 后 [11] 仍报 OK）发现后改为**不预先过滤**，
#    这正是本项目「断言必须经负向自检，否则可能是空转」的又一实例。
echo "[11] 交付分支一致性"
if [ -d .git ] && git rev-parse --verify --quiet release >/dev/null 2>&1; then
  _extra=$(git ls-tree -r release --name-only | while IFS= read -r _f; do
             git cat-file -e "main:$_f" 2>/dev/null || echo "$_f"
           done)
  if [ -n "$_extra" ]; then
    _n=$(printf '%s\n' "$_extra" | grep -c . )
    bad "release 分支含 $_n 个不随包文件（应为 0）"
    printf '%s\n' "$_extra" | head -8 | while IFS= read -r _l; do echo "       + $_l"; done
    echo "       → 修法：python scripts/_build/v3/release/release_branch.py --apply --allow-delete"
  else
    ok "release 树 == main 交付集（无多余文件）"
  fi
else
  ok "无 .git 或无 release 分支 → 跳过（交付树正常路径）"
fi

# ---------- 汇总 ----------', '[9]+[10] + 汇总')` 插入第 9/10 节，
#   其幂等护栏要求「[9]…[10]…汇总」**整块连续**。若本节插在 [10] 与「汇总」之间，
#   该连续性被破坏 → phase15 每跑一轮就再追加一份 [9]/[10]；
#   而本节自己的护栏（要求「[11] + 汇总」相邻）同样失效 → 两个区块**互相引爆**，
#   实测第 2 轮 selfcheck.sh 出现两份 [9]/[10]/[11]，第 3 轮 phase17 直接 rc=1。
#   → 本节必须插在 **[9] 之前**，两个护栏才同时成立。编号 8b 保证输出顺序单调。
_dupname=$(awk '
  FNR==1{fm=0; inname=0}
  FNR==1 && $0=="---"{fm=1;next}
  fm && /^name:/{v=$0; sub(/^name:[[:space:]]*/,"",v); print v; fm=0; next}
  fm && /^[A-Za-z_][A-Za-z0-9_-]*:/{next}
' $(find . -name SKILL.md -not -path './.git/*' -not -path './.learnbuddy/*' 2>/dev/null | sort) 2>/dev/null \
  | sed 's/[[:space:]]*$//' | grep -v '^$' | sort | uniq -d | tr '\n' ' ')
if [ -z "$_dupname" ]; then ok "SKILL.md 的 name 全域唯一（无同名入口）"
else bad "SKILL.md 存在同名入口: $_dupname"; fi

if [ -f SKILL.md ] && [ ! -e library/SKILL.md ]; then
  ok "入口唯一：包根 SKILL.md 在位 · library/ 下无 SKILL.md"
else bad "入口不唯一（library/SKILL.md 不应存在，应为 library/README.md）"; fi

_dmiss=0
for d in LICENSE THIRD_PARTY_NOTICES.md; do
  [ -f "$d" ] || { bad "缺声明文件: $d"; _dmiss=$((_dmiss+1)); }
done
[ "$_dmiss" -eq 0 ] && ok "LICENSE / THIRD_PARTY_NOTICES.md 声明文件齐全"

# .gitignore 不随包交付时，排除已在导出阶段完成 —— 断言降级为说明项
if [ -f .gitignore ]; then
  _gi=$(grep -c '^references/.*[.]md$' .gitignore); _gi=${_gi:-0}
  [ "$_gi" -ge 8 ] && ok "过程文档已由 .gitignore 排除（$_gi 项）" \
    || bad "gitignore 排除不足（$_gi 项，期望 ≥8）"
else
  ok "发布副本：无 .gitignore（过程文档已在导出阶段剔除）"
fi

# ---------- 8c. 不强制自我身份 ----------
echo "[8c] 不强制自我身份"
if grep -qE '^identity:|^[[:space:]]+self_intro:|^[[:space:]]+no_rename:' config.yaml 2>/dev/null; then
  bad "config.yaml 仍包含固定身份配置"
else
  ok "config.yaml 不含固定身份配置"
fi
for _f in SKILL.md INSTALL.md library/output-spec.md commands/qihang.md; do
  if grep -qE '人格锁定|身份锁定|identity[.]self_intro|我是连小理' "$_f" 2>/dev/null; then
    bad "$_f 仍包含强制自我身份声明"
  else
    ok "$_f 不含强制自我身份声明"
  fi
done
if grep -qF '安装完成后回复一句「安装完成」' SKILL.md 2>/dev/null \
   && grep -qF '首次使用引导' SKILL.md 2>/dev/null; then
  ok "SKILL.md 保留安装后简短确认 + 首次使用引导"
else
  bad "SKILL.md 缺少安装后行为约定（应含确认句与首次使用引导）"
fi

# ---------- 8d. 触发门与核心快路径 ----------
# 核心请求直接走学习/公开信息快路径；外部桥接、复杂澄清和扩展域均按需使用。
echo "[8d] 触发门与核心快路径"
for _k in '^trigger:' '^  when_any:' '^  dlut_markers:' '^  learning_markers:' '^  learning_intents:' \
          '^  not_triggered_behavior:' '^  lock_after_trigger:' '^  ladder:' '^  self_generate_requires:'; do
  if grep -q "$_k" config.yaml 2>/dev/null; then ok "config.yaml 含 $_k"
  else bad "config.yaml 缺 $_k（触发门真相源不完整）"; fi
done
for _k in '触发门与接管边界' '不接管' '优先走核心快路径' '需要时加载官方资料或专项规则'; do
  if grep -qF "$_k" SKILL.md 2>/dev/null; then ok "SKILL.md 触发门含「$_k」"
  else bad "SKILL.md 触发门缺「$_k」"; fi
done
# 词表同源（v3.3.6）：门词表必须是 20 域触发词的并集 —— 防「域能锁、门不放行」的 39 处矛盾复发
_gatewords=$(sed -n '/^  learning_markers:/,/^  learning_intents:/p' config.yaml 2>/dev/null)
_cov=0
for _w in 概念图 卡组 引用规范 军训 作息 简历 投稿 专利 查重 讲义 emo 助学金; do
  printf '%s' "$_gatewords" | grep -q "$_w" && _cov=$((_cov+1))
done
[ "${_cov:-0}" -ge 10 ] && ok "门词表与域表同源（12 个代表词命中 $_cov 个）" \
  || bad "门词表与域表不同源（代表词仅命中 ${_cov:-0}/12）—— 会把能锁定的问题挡在门外"
for _k in '^  out_of_scope_markers:' '^  boundary_note:'; do
  grep -q "$_k" config.yaml 2>/dev/null && ok "config.yaml 含 $_k" || bad "config.yaml 缺 $_k"
done
grep -qF '越界信号' SKILL.md 2>/dev/null && ok "SKILL.md 已声明越界信号" || bad "SKILL.md 缺越界信号"
for _t in 明确涉及大连理工大学 '学习或校园生活诉求' 自述为大连理工大学学生; do
  if grep -qF "$_t" SKILL.md 2>/dev/null; then ok "触发条件在位：$_t"
  else bad "触发条件缺：$_t"; fi
done
for _f in library/domain-review.md library/general-fallback.md library/external-bridge.md; do
  if grep -qF '核心快路径' "$_f" 2>/dev/null; then ok "$(basename "$_f") 已声明核心快路径优先"
  else bad "$(basename "$_f") 未说明核心请求不走强制降级链"; fi
done
if grep -qF '触发门' commands/qihang.md 2>/dev/null; then ok "入口卡已接入触发门"
else bad "commands/qihang.md 未接入触发门"; fi
if grep -qF '检索 12 平台' commands/qihang.md 2>/dev/null; then
  bad "入口卡仍写「检索 12 平台」（v3.3.1 起已改为按域指定 2–3 个）"
else ok "入口卡平台口径已更新"; fi

# ---------- 8e. 域锁定：两级匹配接线 + 触发词覆盖度（v3.3.5） ----------
# 事故驱动：规则干跑实测「图书馆 / 教务 / 课表 / 成绩 / 降重 / 不想活」全部 **0 域命中**，
#   因为它们只出现在各域 `_domain.md` 的**细筛词表**里，而路由当时**只查 `_registry.md` 的示意层**。
#   本段把「细筛层必须接线」和「高频校情词必须可达」都钉成断言。
echo "[8e] 域锁定两级匹配与覆盖度"
if grep -q '两级匹配' library/domain-review.md 2>/dev/null; then
  ok "domain-review 已声明「两级匹配」"
else bad "domain-review 未声明两级匹配（只查 _registry 会漏锁）"; fi
if grep -q '_domain.md' library/domain-review.md 2>/dev/null; then
  ok "domain-review 已指向 _domain.md 细筛层"
else bad "domain-review 未指向 _domain.md 细筛层"; fi
if grep -q '示意层' domains/_registry.md 2>/dev/null; then
  ok "_registry.md 已标明触发词列是示意层"
else bad "_registry.md 未标明示意层（易被当成权威表）"; fi
_alltrig=$(cat domains/*/_domain.md 2>/dev/null)
_thin=0
for _d in domains/*/; do
  _t=$(sed -n '/^## *触发词/,/^## /p' "$_d/_domain.md" 2>/dev/null | grep -o '`[^`]*`' | wc -l | tr -d ' ')
  if [ "${_t:-0}" -lt 8 ]; then _thin=$((_thin+1)); bad "$(basename "$_d") 细筛触发词仅 ${_t} 个（要求 ≥8）"; fi
done
[ "${_thin:-0}" -eq 0 ] && ok "20 域细筛触发词均 ≥8 个"
for _w in 图书馆 教务 课表 成绩 一卡通 宿舍 选课 报修; do
  if printf '%s' "$_alltrig" | grep -q "$_w"; then ok "高频校情词可达：$_w"
  else bad "高频校情词不可达：$_w（会掉进无域兜底）"; fi
done
if sed -n '/^## *触发词/,/^## /p' domains/F3-wellbeing/_domain.md 2>/dev/null | grep -qE '不想活|轻生|自杀'; then
  ok "F3 细筛含危机词（危机路径可达）"
else bad "F3 细筛缺危机词（危机信号可能落进无域兜底）"; fi

# ---------- 9. 库内唯一通道（纯 DUT 特化库） ----------
echo "[9] 库内唯一通道"
# 纯本地化后，唯一的「通道」就是库内 skill；不得存在任何库外通道残留。
_extfile=$(find domains -path '*/skills/external.md' 2>/dev/null | wc -l | tr -d ' ')
[ "${_extfile:-0}" -eq 0 ] && ok "无 skills/external.md（库外通道已删除）" \
  || bad "仍存在 $_extfile 个 skills/external.md"
# 产品**文档**不得再出现「通道性」表述（库外兜底/首选、external.md 路径引用）
# 说明：① 仅「说明本包不再有库外通道」的描述性文字不算残留，故只匹配具体通道写法；
#       ② 只扫 *.md（校验脚本自身含这些字面量属正常，不参与残留判定）。口径同 [4]。
_extref=$(grep -rlE '库外兜底|库外首选|skills/external\.md|external\.md' \
          --include='*.md' $_EXDEV $_EXDIR . 2>/dev/null | wc -l | tr -d ' ')
[ "${_extref:-0}" -eq 0 ] && ok "无「库外通道」表述残留" \
  || bad "$_extref 个文件仍含库外通道表述"
# 每个域必须至少有 2 个库内 skill（唯一通道必须完备）
_dmin=$(find domains -path '*skills/local/*/SKILL.md' 2>/dev/null | awk -F/ '{print $2}' \
        | sort | uniq -c | awk '$1<2' | wc -l | tr -d ' ')
[ "${_dmin:-0}" -eq 0 ] && ok "20 域库内 skill 均 ≥2（通道完备）" \
  || bad "$_dmin 个域库内 skill <2（通道不完备）"

# ---------- 10. 仓库清洁度（临时文件零残留） ----------
echo "[10] 临时文件残留"
_tmp=$(find . -maxdepth 2 -name ".selfcheck.tmp*" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
[ "${_tmp:-0}" -eq 0 ] && ok "无 .selfcheck.tmp* 残留" || bad "仍有 $_tmp 个自检临时文件残留"

# ---------- 汇总 ----------
echo "========================================"
printf '结果: OK %s ｜ WARN %s ｜ FAIL %s\n' "$P" "$W" "$F"
if [ "$F" -eq 0 ]; then echo "结论: 可交付"; exit 0; else echo "结论: 需修复后交付"; exit 1; fi
