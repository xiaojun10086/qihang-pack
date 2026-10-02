#!/usr/bin/env bash
# 「启航」学伴包 · 自检脚本（v2.6 稳健重写版）
# 用法: bash scripts/selfcheck.sh
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
# v2.7：本脚本**不创建任何临时文件**（旧版为 TMP="${ROOT}/.selfcheck.tmp"）。
# 原因（实测）：部分受限环境把 rm 做成"失败即封"的拦截器，
# 旧版在 EXIT trap 里 rm 临时文件，会导致**整个脚本静默失败、零输出**；
# 旧版还把 .selfcheck.tmp / .selfcheck.tmp.refs 留在仓库根目录。

P=0; W=0; F=0
ok()   { printf '  OK   %s\n' "$1"; P=$((P+1)); }
warn() { printf '  WARN %s\n' "$1"; W=$((W+1)); }
bad()  { printf '  FAIL %s\n' "$1"; F=$((F+1)); }

echo "「启航」项目自检"
echo "========================================"

# ---------- 1. 必备文件 ----------
echo "[1] 必备文件完整性"
REQ="SKILL.md README.md INSTALL.md PROJECT.md ROADMAP.md config.yaml
library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md
library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md
domains/_registry.md
references/dlut-official-sites.md references/dlut-login-sites.md references/dlut-field-map.md
references/dlut-url-verification.md references/dlut-site-profiles.md references/browser-matrix.md
references/skill-sources.md references/skill-compliance-audit.md references/platforms.md
references/e2e-scenarios.md references/acceptance-v2.md references/validation-report.md
.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh scripts/audit.sh scripts/regress.sh"
miss=0; cnt=0
for f in $REQ; do
  cnt=$((cnt+1))
  [ -f "$f" ] || { bad "缺失: $f"; miss=$((miss+1)); }
done
[ "$miss" -eq 0 ] && ok "全部 $cnt 个必备文件在位"

# ---------- 2. 19 域三级结构 ----------
echo "[2] 19 域三级结构"
# v2.7：改为单遍统计（原逐域循环会起 ~60 个子进程，受限环境易被中断）
nd=$(find domains -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
n_dom=$(find domains -maxdepth 2 -name '_domain.md' 2>/dev/null | wc -l | tr -d ' ')
n_ext=$(find domains -maxdepth 3 -path '*/skills/external.md' 2>/dev/null | wc -l | tr -d ' ')
n_lsk=$(find domains -path '*skills/local/*/SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
nbad=0
[ "$nd" -eq 19 ] && ok "域数 = 19" || { bad "域数 = $nd（期望 19）"; nbad=$((nbad+1)); }
[ "$n_dom" -eq 19 ] && ok "19 个 _domain.md 在位" || { bad "_domain.md = $n_dom（期望 19）"; nbad=$((nbad+1)); }
[ "$n_ext" -eq 19 ] && ok "19 个 skills/external.md 在位" || { bad "external.md = $n_ext（期望 19）"; nbad=$((nbad+1)); }
[ "$n_lsk" -eq 38 ] && ok "38 个库内 skill 在位" || { bad "库内 skill = $n_lsk（期望 38）"; nbad=$((nbad+1)); }
[ "$nbad" -eq 0 ] && ok "所有域三级结构完整" || bad "$nbad 处缺失"

# ---------- 3. frontmatter ----------
echo "[3] SKILL.md frontmatter"
# v2.7：单次 awk 取代「逐文件 3 次 grep」（原为 ~120 个子进程）
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
# v2.7：单遍 grep -r 取全部引用，再在 shell 内用内建 test 判定（原为逐文件 ~280 个子进程）
_refs=$(grep -rhoE '(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*]+[.]md' \
        --include='*.md' . 2>/dev/null | sort -u)
nbroke=0; nref=0
while IFS= read -r p; do
  [ -n "$p" ] || continue
  nref=$((nref+1))
  if [ ! -e "$p" ]; then
    nbroke=$((nbroke+1))
    [ "$nbroke" -le 8 ] && printf '       %s\n' "$p"
  fi
done <<< "$_refs"
# 说明：路径字符集排除了 </>* 等，故「domains/<域>/_domain.md」这类**占位符**不会被误判为失效引用。
if [ "$nbroke" -eq 0 ]; then ok "无失效引用（检查 $nref 处）"
else bad "$nbroke 处失效引用"; fi

# ---------- 5. 陈旧文件 ----------
echo "[5] 陈旧 / 无关文件"
STALE="references/routing-table.md .extracted dev proc
scripts/__pycache__ scripts/_build/__pycache__
scripts/build_qihang_v2.py scripts/build_phase1.py scripts/build_phase2.py"
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
_bad_th=$(grep -rlE "(U ?[≤≥><]=? ?5%|U ?≈ ?0\.05|threshold: 0\.05)" --include='*.md' --include='*.yaml' --include='*.html' . 2>/dev/null | grep -v _build | grep -v review-report | grep -v 需求确认书 | grep -v clarity.md | wc -l | tr -d ' ')
[ "${_bad_th:-0}" -eq 0 ] && ok "无旧阈值残留" || bad "$_bad_th 个文件仍有旧阈值（期望 0.30）"

_od=$(grep -rlnE '\bD 域\b' domains/ library/ SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "${_od:-0}" -eq 0 ] && ok "无 v1.1 旧域名残留" || bad "$_od 个文件含旧域名"

# v2.7：单遍统计（原逐文件 grep 为 ~95 个子进程）
_dup=$(grep -rc '^## ⚠️ 红线（不得绕过）' domains --include='*.md' 2>/dev/null \
       | awk -F: '$2>1' | wc -l | tr -d ' ')
[ "${_dup:-0}" -eq 0 ] && ok "无重复红线段" || bad "$_dup 个文件红线段重复"

# v2.7：单次 awk 检测「同一 skill 内红线条目重复」
_di=$(awk '/^## ⚠️ 红线/{inr=1;next} inr&&/^## /{inr=0}
  inr&&/^- /{k=FILENAME "|" $0; if(seen[k]++){print FILENAME; print FILENAME > "/dev/stderr"}}
' $(find domains -path '*skills/local*' -name SKILL.md 2>/dev/null | sort) 2>/dev/null \
  | sort -u | wc -l | tr -d ' ')
[ "${_di:-0}" -eq 0 ] && ok "红线条目无重复" || bad "$_di 个文件红线条目重复"

_nr=$(grep -rl '## ⚠️ 红线' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
[ "${_nr:-0}" -eq 19 ] && ok "域文件红线覆盖 19/19" || bad "域文件红线覆盖 $_nr/19"

# v2.7 新增：库内 skill 的红线条目必须与所属域**逐条一致**（防措辞漂移）
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
grep -q '最后 3 条是反例' library/domain-review-cases.md 2>/dev/null && bad "用例集反例表述过时" || ok "用例集反例表述正确"

# ---------- 8. 计数 ----------
echo "[8] 计数一致性"
nsk=$(find domains -path '*skills/local*' -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "${nsk:-0}" -eq 38 ] && ok "库内 skill = 38（每域 2 个）" || bad "库内 skill = $nsk（期望 38）"
# 单遍统计每域 skill 数（避免逐域起子进程）
_pbad=$(find domains -path '*skills/local/*/SKILL.md' 2>/dev/null | awk -F/ '{print $2}' \
        | sort | uniq -c | awk '$1!=2' | wc -l | tr -d ' ')
[ "${_pbad:-0}" -eq 0 ] && ok "每域均为 2 个库内 skill" || bad "$_pbad 个域的库内 skill 数 ≠ 2"
libn=$(ls -1 library/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${libn:-0}" -eq 8 ] && ok "library 文件数 = 8" || warn "library 文件数 = $libn（期望 8）"
cmdn=$(ls -1 commands/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${cmdn:-0}" -eq 21 ] && ok "commands = 21" || warn "commands = $cmdn（期望 21）"
pub=$(grep -c '^|' references/dlut-official-sites.md 2>/dev/null); pub=${pub:-0}
echo "   info DUT 公开站表格行: $pub"
[ -f .codebuddy-plugin/plugin.json ] && ok "插件清单有效" || bad "插件清单缺失"

# ---------- 9. 多源比对与 DUT 适配 ----------
echo "[9] 库外多源比对"
# grep -L 一次列出缺失文件（2 个子进程，替代逐域循环）
_ma=$(grep -L "综合分" domains/*/skills/external.md 2>/dev/null | wc -l | tr -d ' ')
_mb=$(grep -L "DUT 落地评估" domains/*/skills/external.md 2>/dev/null | wc -l | tr -d ' ')
if [ "${_ma:-0}" -eq 0 ] && [ "${_mb:-0}" -eq 0 ]; then
  ok "19 域 external.md 均含「多源比对 + DUT 落地评估」"
else
  bad "external.md 缺项：多源比对 $_ma 个 / DUT 评估 $_mb 个"
fi
if [ -f references/skill-matrix-v3.md ]; then ok "存在 skill-matrix-v3.md"
else bad "缺 references/skill-matrix-v3.md"; fi

# ---------- 10. 仓库清洁度（临时文件零残留） ----------
echo "[10] 临时文件残留"
_tmp=$(find . -maxdepth 2 -name ".selfcheck.tmp*" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
[ "${_tmp:-0}" -eq 0 ] && ok "无 .selfcheck.tmp* 残留" || bad "仍有 $_tmp 个自检临时文件残留"

# ---------- 汇总 ----------
echo "========================================"
printf '结果: OK %s ｜ WARN %s ｜ FAIL %s\n' "$P" "$W" "$F"
if [ "$F" -eq 0 ]; then echo "结论: 可交付"; exit 0; else echo "结论: 需修复后交付"; exit 1; fi
