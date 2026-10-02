#!/usr/bin/env bash
# 「启航」学伴包 · 自检脚本（v2.6 稳健重写版）
# 用法: bash scripts/selfcheck.sh
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1
TMP="${ROOT}/.selfcheck.tmp"

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
.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh scripts/audit.sh"
miss=0; cnt=0
for f in $REQ; do
  cnt=$((cnt+1))
  [ -f "$f" ] || { bad "缺失: $f"; miss=$((miss+1)); }
done
[ "$miss" -eq 0 ] && ok "全部 $cnt 个必备文件在位"

# ---------- 2. 19 域三级结构 ----------
echo "[2] 19 域三级结构"
nd=0; nbad=0
for d in domains/*/; do
  [ -d "$d" ] || continue
  b=$(basename "$d"); nd=$((nd+1))
  [ -f "${d}_domain.md" ] || { bad "$b 缺 _domain.md"; nbad=$((nbad+1)); }
  [ -f "${d}skills/external.md" ] || { bad "$b 缺 skills/external.md"; nbad=$((nbad+1)); }
  n=$(find "${d}skills/local" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
  [ "${n:-0}" -ge 1 ] || { bad "$b 无库内 skill"; nbad=$((nbad+1)); }
done
[ "$nd" -eq 19 ] && ok "域数 = 19" || bad "域数 = $nd（期望 19）"
[ "$nbad" -eq 0 ] && ok "所有域三级结构完整" || bad "$nbad 处缺失"

# ---------- 3. frontmatter ----------
echo "[3] SKILL.md frontmatter"
nf=0; nfm=0
for f in $(find . -name SKILL.md -not -path './dev/*' -not -path './proc/*' 2>/dev/null | sort); do
  nf=$((nf+1))
  head -1 "$f" | grep -q '^---$' || { bad "无 frontmatter: $f"; nfm=$((nfm+1)); continue; }
  grep -q '^name:' "$f" || { bad "缺 name: $f"; nfm=$((nfm+1)); }
  grep -q '^description:' "$f" || { bad "缺 description: $f"; nfm=$((nfm+1)); }
done
[ "$nfm" -eq 0 ] && ok "$nf 个 SKILL.md frontmatter 全部合规" || bad "$nfm 处不合规"

# ---------- 4. 交叉引用 ----------
echo "[4] 文档交叉引用"
: > "$TMP"
for f in $(find . -name '*.md' -not -path './dev/*' -not -path './proc/*' 2>/dev/null | sort); do
  grep -oE '(library|references|domains|scripts|commands)/[A-Za-z0-9_./-]+\.md' "$f" 2>/dev/null | sort -u > "${TMP}.refs"
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    [ -e "$p" ] || echo "BROKEN|$p|$f" >> "$TMP"
  done < "${TMP}.refs"
done
nbroke=$(grep -c '^BROKEN' "$TMP" 2>/dev/null)
nbroke=${nbroke:-0}
if [ "$nbroke" -eq 0 ]; then ok "无失效引用"
else bad "$nbroke 处失效引用"; grep '^BROKEN' "$TMP" | head -8 | sed 's/^BROKEN|/       /'; fi

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

_dup=0
for f in $(find domains -name '*.md' 2>/dev/null); do
  c=$(grep -c '^## ⚠️ 红线（不得绕过）' "$f" 2>/dev/null)
  c=${c:-0}
  [ "$c" -gt 1 ] && { bad "红线段重复: $f（$c 段）"; _dup=$((_dup+1)); }
done
[ "$_dup" -eq 0 ] && ok "无重复红线段"

_di=0
for f in $(find domains -path '*skills/local*' -name SKILL.md 2>/dev/null); do
  d=$(grep -E '^- ' "$f" 2>/dev/null | sort | uniq -d | wc -l | tr -d ' ')
  d=${d:-0}
  [ "$d" -gt 0 ] && { bad "红线条目重复: $f（$d 条）"; _di=$((_di+1)); }
done
[ "$_di" -eq 0 ] && ok "红线条目无重复"

_nr=$(grep -rl '## ⚠️ 红线' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
[ "${_nr:-0}" -eq 19 ] && ok "域文件红线覆盖 19/19" || bad "域文件红线覆盖 $_nr/19"

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
[ "${nsk:-0}" -eq 19 ] && ok "库内 skill = 19" || bad "库内 skill = $nsk（期望 19）"
libn=$(ls -1 library/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${libn:-0}" -eq 8 ] && ok "library 文件数 = 8" || warn "library 文件数 = $libn（期望 8）"
cmdn=$(ls -1 commands/*.md 2>/dev/null | wc -l | tr -d ' ')
[ "${cmdn:-0}" -eq 21 ] && ok "commands = 21" || warn "commands = $cmdn（期望 21）"
pub=$(grep -c '^|' references/dlut-official-sites.md 2>/dev/null); pub=${pub:-0}
echo "   info DUT 公开站表格行: $pub"
[ -f .codebuddy-plugin/plugin.json ] && ok "插件清单有效" || bad "插件清单缺失"

# ---------- 汇总 ----------
: > "$TMP" 2>/dev/null || true
echo "========================================"
printf '结果: OK %s ｜ WARN %s ｜ FAIL %s\n' "$P" "$W" "$F"
if [ "$F" -eq 0 ]; then echo "结论: 可交付"; exit 0; else echo "结论: 需修复后交付"; exit 1; fi
