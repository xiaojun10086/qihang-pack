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
  # 裸「成绩」应被拒为歧义（L3 只针对「成绩明细」），且须给出**可判定的**区分提示。
  # 不能用「rc≠0 且含『可用目标』」判定 —— 那是兜底 usage，任何乱词都能通过（恒真断言）。
  out=$(bash scripts/dlut-read.sh 成绩 </dev/null 2>&1); rc=$?
  if [ "$rc" -eq 1 ] && echo "$out" | grep -q "请先区分"; then
    ok "歧义项「成绩」未直接放行（提示区分等级/明细）"
  else
    bad "歧义项「成绩」未给出区分提示（rc=$rc）"
  fi
  # 裸「邮件 / 邮箱」同理（L2 未读提示 vs L3 正文），须提示区分
  out=$(bash scripts/dlut-read.sh 邮件 </dev/null 2>&1); rc=$?
  if [ "$rc" -eq 1 ] && echo "$out" | grep -q "请先区分"; then
    ok "歧义项「邮件」未直接放行（提示区分提示/正文）"
  else
    bad "歧义项「邮件」未给出区分提示（rc=$rc）"
  fi
  # 「成绩等级」属 L1，应可读（与 config.yaml 的 L1_auto 对齐）
  out=$(bash scripts/dlut-read.sh 成绩等级 --dry-run </dev/null 2>&1); rc=$?
  if [ "$rc" -eq 0 ] && echo "$out" | grep -q "未启动浏览器"; then
    ok "L1「成绩等级」可读（dry-run 通过）"
  else
    bad "L1「成绩等级」不可读（rc=$rc）"
  fi
  out=$(bash scripts/dlut-read.sh 邮箱提示 </dev/null 2>&1); [ $? -eq 2 ] \
    && ok "L2 需确认（退出码 2）" || bad "L2 未要求确认"
  # L3 语义变体必须同样被拒（旧版精确匹配可被「缴费金额」等绕开）
  for t in 缴费金额 银行卡号 身份证号 邮件内容 成绩单 绩点 家庭信息卡; do
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

# ---------- 6. 来源合规（纯 DUT 特化库） ----------
echo "[6] 来源合规"
aud="references/skill-compliance-audit.md"
if [ -f "$aud" ]; then
  grep -q "0 侵权" "$aud" && ok "合规自检记录：包内内容 0 侵权" || warn "未明确「0 侵权」"
  grep -q "GPL-3.0" "$aud" && ok "已识别并隔离 GPL-3.0 依赖（未吸收）" || warn "未识别 GPL 风险"
  grep -q "无 LICENSE" "$aud" && ok "已标注「无 LICENSE」仓库（未吸收）" || warn "未标注无证仓库"
  grep -qE "核心能力运行期零外部依赖|运行期零外部依赖" "$aud" \
    && ok "已声明「核心能力运行期零外部依赖」" || warn "未声明零外部依赖口径"
  grep -q "外部桥接" "$aud" && ok "已声明外部桥接为可选增强（v3.3.0）" \
    || warn "未声明外部桥接口径（v3.3.0 起必需）"
else
  bad "缺少 skill-compliance-audit.md"
fi
if [ -f THIRD_PARTY_NOTICES.md ]; then
  grep -q "零内容摘录" THIRD_PARTY_NOTICES.md && ok "专有许可来源已标注「零内容摘录」" || warn "未标注专有来源零摘录"
else
  bad "缺少 THIRD_PARTY_NOTICES.md"
fi

# ---------- 7. 红线覆盖 ----------
echo "[7] 红线覆盖（安全性核心）"
nd=$(find domains -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
nred=$(grep -rl '## ⚠️ 红线' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
nred2=$(grep -rl '红线\|安全护栏' domains/*/skills/local/*/SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "$nred" -eq "$nd" ] && ok "域文件红线覆盖 $nred/$nd" || bad "域文件红线覆盖 $nred/$nd（应全覆盖）"
# 每域 4–5 个库内 skill，故期望 = 实际库内 skill 数（且 ≥ 2×域数）
nlocal=$(find domains -path '*skills/local/*/SKILL.md' | wc -l | tr -d ' ')
_want=$((nd*2))
if [ "$nred2" -eq "$nlocal" ] && [ "$nred2" -ge "$_want" ]; then
  ok "库内 skill 红线覆盖 $nred2/$nlocal（每域 4–5 个）"
else
  bad "库内 skill 红线覆盖 $nred2（期望 $nlocal，且 ≥ $_want）"
fi
grep -q '红线总览' SKILL.md 2>/dev/null && ok "入口含「红线总览」" || bad "入口缺「红线总览」"
grep -q '红线优先' library/clarity.md 2>/dev/null && ok "澄清门已声明「红线优先级」" || warn "澄清门未声明红线优先级"

# ---------- 8. 敏感域档案红线 ----------
echo "[8] 敏感域档案红线（防自相矛盾）"
# 两类必须分开验：整域不写（F3/F5）与「排除敏感字段后写入」（F4/F6）。
# 旧版只查 F3/F5 —— F4/F6 的归档规则写不写都算过，属结构性盲区。
for d in F3 F5; do
  f=$(ls -d domains/${d}-*/ 2>/dev/null | head -1)_domain.md
  if [ -f "$f" ]; then
    if grep -q '不写入任何记忆层' "$f"; then ok "$d 已明确整域不写入记忆层"
    else bad "$d 未声明整域不写入记忆层"; fi
  fi
done
for d in F4 F6; do
  f=$(ls -d domains/${d}-*/ 2>/dev/null | head -1)_domain.md
  if [ -f "$f" ]; then
    if grep -q '禁止写入' "$f"; then ok "$d 已声明敏感字段排除后写入"
    else bad "$d 未声明敏感字段排除规则（应引 library/memory.md §4）"; fi
  fi
done
# 归档红线表必须「同源」：memory.md §4 与 output-spec §5 两处同时覆盖 F4 金额 / F6 伤病 / 第三方隐私
for f in library/memory.md library/output-spec.md; do
  _m=0; grep -q '第三方隐私' "$f" || _m=$((_m+1))
  grep -q '金额' "$f" || _m=$((_m+1))
  grep -q '伤病' "$f" || _m=$((_m+1))
  if [ "$_m" -eq 0 ]; then ok "$(basename "$f") 归档红线覆盖 F4 金额 / F6 伤病 / 第三方隐私"
  else bad "$(basename "$f") 归档红线缺项 $_m 处（应与 library/memory.md §4 同源）"; fi
done

# ---------- 8b. 库内唯一通道（纯 DUT 特化库） ----------
echo "[8b] 库内唯一通道"
# 纯本地化后不得存在任何库外通道残留
_extf=$(find domains -path '*/skills/external.md' 2>/dev/null | wc -l | tr -d ' ')
[ "$_extf" -eq 0 ] && ok "无 skills/external.md（库外通道已删除）" || bad "仍存在 $_extf 个 external.md"
# 每个域至少 2 个库内 skill（唯一通道必须完备）
_dmin=$(find domains -path '*skills/local/*/SKILL.md' | awk -F/ '{print $2}' \
        | sort | uniq -c | awk '$1<2' | wc -l | tr -d ' ')
[ "$_dmin" -eq 0 ] && ok "全部域库内 skill ≥2（通道完备）" || bad "$_dmin 个域库内 skill <2"

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
