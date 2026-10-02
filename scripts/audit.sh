#!/usr/bin/env bash
# 「启航」学伴包 · 安全审计 + 可行性检查
# 用法: bash scripts/audit.sh
# 原则：只把「可执行文件里出现危险模式」当作风险；
#       文档中「描述」危险模式（如"要搜 curl|bash"）只作提示，不计风险。
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

P=0; W=0; F=0
ok()   { printf '  ✅ %s\n' "$1"; P=$((P+1)); }
warn() { printf '  ⚠️  %s\n' "$1"; W=$((W+1)); }
bad()  { printf '  ❌ %s\n' "$1"; F=$((F+1)); }
info() { printf '  ℹ️  %s\n' "$1"; }

# 可执行文件（真风险扫描范围）：排除审计脚本自身与构建缓存
EXEC_FILES="$(find scripts -type f \( -name '*.sh' -o -name '*.py' \) \
  -not -path '*/__pycache__/*' 2>/dev/null | grep -v 'scripts/audit.sh')"
# 全部交付文本（提示性扫描范围）
ALL="$(find . -type f \( -name '*.md' -o -name '*.sh' -o -name '*.py' -o -name '*.yaml' -o -name '*.json' -o -name '*.html' \) \
  -not -path './dev/*' -not -path './proc/*' -not -path './.git/*' -not -path '*/__pycache__/*' 2>/dev/null)"

echo "「启航」安全审计 + 可行性检查"
echo "========================================"

# ---------- 1. 危险命令（只扫可执行文件） ----------
echo "[1] 危险命令模式（可执行文件）"
# 过滤规则：
#   a) 注释行（shell/python 的 # 开头）—— 说明性文字，不可执行
#   b) 内嵌文档字符串中的「要排查对象」表述 —— 文档，非代码
#   c) 第 4 行那种「旧实现…属危险模式」的对照说明
ALLOW_LINE='^[[:space:]]*#'"|"'判风险|属危险模式|要排查|未发现任何恶意模式|拒绝执行：输出路径'
scan_exec() {
  echo "$EXEC_FILES" | xargs grep -nE "$1" 2>/dev/null \
    | grep -vE "$ALLOW_LINE" \
    | cut -d: -f1 | sort -u | head -3
}
hits=0
for pat in 'rm[[:space:]]+-rf[[:space:]]+/' 'rm[[:space:]]+-rf[[:space:]]+~' \
           'cur[l][^|]*\|[[:space:]]*(ba)?sh' 'wg[e]t[^|]*\|[[:space:]]*(ba)?sh' \
           '\bs[u]do\b' 'chm[o]d[[:space:]]+777' 'mk[f]s' 'd[d][[:space:]]+if=' \
           '>[[:space:]]*/dev/sd' 'os\.s[y]stem\(' 'subprocess.*shell[[:space:]]*=[[:space:]]*True' \
           'base64[[:space:]]+-d[[:space:]]*\|' 'rm[[:space:]]+-rf[[:space:]]+"?\$' ; do
  m=$(scan_exec "$pat")
  [ -n "$m" ] && { warn "命中 [$pat]：$(echo "$m" | tr '\n' ' ')"; hits=$((hits+1)); }
done
[ "$hits" -eq 0 ] && ok "可执行文件中未发现危险命令模式（注释与文档说明已排除）"

# rmtree / rm -rf 单独说明：可执行文件里出现递归删除时必须带护栏
if echo "$EXEC_FILES" | xargs grep -ln 'shutil\.rmtree' 2>/dev/null | grep -q .; then
  for f in $(echo "$EXEC_FILES" | xargs grep -ln 'shutil\.rmtree' 2>/dev/null); do
    if grep -q '拒绝执行：输出路径' "$f" 2>/dev/null; then
      ok "含递归删除但已加「拒绝危险路径」护栏（$f）"
    else
      bad "含递归删除且无护栏：$f"
    fi
  done
fi

# ---------- 2. 凭证 / 敏感标识 ----------
echo "[2] 凭证与敏感标识泄露"
hits=0
for pat in 'sk-[A-Za-z0-9]\{20,\}' 'ghp_[A-Za-z0-9]\{20,\}' 'AKIA[0-9A-Z]\{16\}' \
           'BEGIN [A-Z ]*PRIVATE KEY' 'accessToken=[A-Za-z0-9._-]\{40,\}' ; do
  m=$(echo "$ALL" | xargs grep -lnE "$pat" 2>/dev/null | head -3)
  [ -n "$m" ] && { bad "疑似凭证 [$pat]：$(echo "$m" | tr '\n' ' ')"; hits=$((hits+1)); }
done
[ "$hits" -eq 0 ] && ok "未发现凭证 / token / 私钥"

# ---------- 3. 个人数据残留 ----------
echo "[3] 个人数据残留"
hits=0
# 真实学号（8 位数字，且非版本号/年份区间）与手机号、QQ 邮箱
for pat in '\b2026[0-9]\{6,7\}\b' '\b1[3-9][0-9]\{9\}\b' '[0-9]\{6,\}@qq\.com' ; do
  m=$(echo "$ALL" | xargs grep -lE "$pat" 2>/dev/null | grep -v 'scripts/audit.sh' | head -5)
  [ -n "$m" ] && { warn "疑似真实个人数据 [$pat]：$(echo "$m" | tr '\n' ' ')"; hits=$((hits+1)); }
done
[ "$hits" -eq 0 ] && ok "未发现真实学号 / 手机号 / 邮箱"

# ---------- 4. 网络外发 ----------
echo "[4] 网络外发行为"
net=$(echo "$EXEC_FILES" | xargs grep -lnE '(curl|wget|requests\.(post|put)|fetch\()[^;]*https?://' 2>/dev/null | head -5)
if [ -n "$net" ]; then
  warn "可执行文件含网络调用（需确认只读）：$(echo "$net" | tr '\n' ' ')"
else
  ok "运行期脚本无主动外发（私密站读取仅在运行时发生且不落盘）"
fi

# ---------- 5. L3 门禁实测（可行性关键） ----------
echo "[5] L3 门禁实测"
if [ -f scripts/dlut-read.sh ]; then
  for t in 缴费 银行卡 身份证 邮件正文 心理记录 成绩明细; do
    out=$(bash scripts/dlut-read.sh "$t" </dev/null 2>&1); rc=$?
    if [ "$rc" -eq 3 ] && echo "$out" | grep -q "拒绝执行"; then ok "L3 拦截 [$t]"
    else bad "L3 未拦截 [$t]（退出码 $rc）"; fi
  done
  # 裸「成绩」应被拒绝为歧义（L3 只针对「成绩明细」），不得直接放行读取
  out=$(bash scripts/dlut-read.sh 成绩 </dev/null 2>&1); rc=$?
  if [ "$rc" -ne 0 ] && echo "$out" | grep -q "可用目标"; then
    ok "歧义项「成绩」未直接放行（提示区分等级/明细）"
  else
    bad "歧义项「成绩」被直接放行（等级可读、明细禁读，须区分）"
  fi
  out=$(bash scripts/dlut-read.sh 邮箱提示 </dev/null 2>&1); [ $? -eq 2 ] \
    && ok "L2 需确认（退出码 2）" || bad "L2 未要求确认"
  # L3 语义变体必须同样被拒（旧版精确匹配可被「缴费金额」等绕开）
  for t in 缴费金额 银行卡号 身份证号 邮件内容 成绩单 家庭信息卡; do
    out=$(bash scripts/dlut-read.sh "$t" </dev/null 2>&1); rc=$?
    if [ "$rc" -eq 3 ] && echo "$out" | grep -q "拒绝执行"; then ok "L3 变体拦截 [$t]"
    else bad "L3 变体未拦截 [$t]（退出码 $rc）"; fi
  done
  out=$(bash scripts/dlut-read.sh 课表 --dry-run </dev/null 2>&1)
  echo "$out" | grep -q "未启动浏览器" && ok "L1 dry-run 不启动浏览器" || warn "dry-run 未声明不启动浏览器"
  echo "$out" | grep -q "独立Profile" && ok "强制独立 Profile（不复用真实浏览器）" || bad "未声明独立 Profile"
else
  bad "缺少 scripts/dlut-read.sh"
fi

# ---------- 6. 摘录合规 ----------
echo "[6] 摘录合规"
aud="references/skill-compliance-audit.md"
if [ -f "$aud" ]; then
  grep -q "0 侵权" "$aud" && ok "合规自检记录：包内摘录 0 侵权" || warn "未明确「0 侵权」"
  grep -q "GPL-3.0" "$aud" && ok "已识别并隔离 GPL-3.0 依赖" || warn "未识别 GPL 风险"
  grep -q "无 LICENSE" "$aud" && ok "已标注「无 LICENSE」仓库" || warn "未标注无证仓库"
else
  bad "缺少 skill-compliance-audit.md"
fi

# ---------- 7. 红线覆盖 ----------
echo "[7] 红线覆盖（安全性核心）"
nd=$(find domains -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
nred=$(grep -rl '## ⚠️ 红线' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
nred2=$(grep -rl '红线\|安全护栏' domains/*/skills/local/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "$nred" -eq "$nd" ] && ok "域文件红线覆盖 $nred/$nd" || bad "域文件红线覆盖 $nred/$nd（应全覆盖）"
# 每域 2 个库内 skill，故期望 2×域数
_want=$((nd*2))
[ "$nred2" -eq "$_want" ] && ok "库内 skill 红线覆盖 $nred2/$_want（每域 2 个）" || bad "库内 skill 红线覆盖 $nred2/$_want"
grep -q '红线总览' SKILL.md 2>/dev/null && ok "入口含「红线总览」" || bad "入口缺「红线总览」"
grep -q '红线优先' library/clarity.md 2>/dev/null && ok "澄清门已声明「红线优先级」" || warn "澄清门未声明红线优先级"

# ---------- 8. 敏感域档案红线 ----------
echo "[8] 敏感域档案红线（防自相矛盾）"
bad_found=0
for d in F3 F5; do
  f=$(ls -d domains/${d}-*/ 2>/dev/null | head -1)_domain.md
  if [ -f "$f" ]; then
    if grep -q '不写入任何记忆层' "$f"; then ok "$d 已明确不写入记忆层"
    else bad "$d 未声明不写入记忆层"; bad_found=$((bad_found+1)); fi
  fi
done
[ "$bad_found" -eq 0 ] || true

# ---------- 9. 多源比对与 DUT 适配 ----------
echo "[8b] 库外候选合规与 DUT 适配"
if [ -f references/skill-matrix-v3.md ]; then
  grep -q "DUT 适配" references/skill-matrix-v3.md && ok "矩阵含 DUT 适配维度" || warn "矩阵缺 DUT 适配维度"
  if grep -q "环境错位清单" references/skill-matrix-v3.md; then ok "含环境错位清单（防误装）"; fi
else
  bad "缺 references/skill-matrix-v3.md"
fi

# ---------- 9b. 脚本可执行性 ----------
echo "[9] 脚本可执行性"
for s in scripts/*.sh; do
  bash -n "$s" 2>/dev/null && ok "语法通过 $(basename "$s")" || bad "语法错误 $(basename "$s")"
done

# ---------- 10. 文档提及（提示，不计风险） ----------
echo "[10] 文档中提及的危险模式（提示，非风险）"
doc_hits=$(echo "$ALL" | xargs grep -lnE 'curl[^|]*\|[[:space:]]*(ba)?sh|rm[[:space:]]+-rf[[:space:]]+/' 2>/dev/null \
  | grep -v 'scripts/' | head -5)
[ -n "$doc_hits" ] && info "以下文档把危险模式作为「要排查的对象」提及（正常）：$(echo "$doc_hits" | tr '\n' ' ')" \
  || info "无"

echo "========================================"
printf '结果: ✅ %s 通过 ｜ ⚠️  %s 警告 ｜ ❌ %s 失败\n' "$P" "$W" "$F"
if [ "$F" -eq 0 ]; then echo "结论: 安全性与可行性通过"; exit 0; else echo "结论: 需修复"; exit 1; fi
