#!/usr/bin/env bash
# 「启航」回归测试
# 用法: bash scripts/regress.sh          # 跑一轮
#       bash scripts/regress.sh 3        # 连跑 3 轮（验证确定性）
#
# 与 selfcheck.sh / audit.sh 的分工：
#   selfcheck.sh  静态结构与计数
#   audit.sh      安全与门禁
#   regress.sh    **行为回归**：澄清门算例 / L3 门禁矩阵 / 红线一致性 / 结构不变量
#
# 设计约束：**零临时文件**（受限环境里 rm 可能被拦截，写临时文件会让脚本静默失败）；
#           **不依赖 seq 等外部命令**（Windows Git Bash 精简环境可能缺）；
#           **rc=127 视为环境抖动**：受限环境在高负载下偶发「子进程启动失败」，
#           表现为退出码 127（而非被测脚本的真实结论）。对 127 做**有限重试**，
#           避免把环境抖动误判成功能缺陷。
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT" || exit 1

ROUNDS="${1:-1}"
case "$ROUNDS" in ''|*[!0-9]*) ROUNDS=1 ;; esac
[ "$ROUNDS" -lt 1 ] && ROUNDS=1

# 澄清门用例：名称|o|t|d|w|c|b|期望判定
CLARITY_CASES="
例甲-三关键槽显式|1|1|1|0|0|0|放行
例乙-单题答疑|1|1|0.8|0|0|0|放行
例丙-对象歧义且缺产出|0.5|0.8|0|0|0|0.8|追问
例丁-全歧义(旧版漏洞)|0.5|0.5|0|0|0|0|追问
例戊-全槽位齐全|1|1|1|1|1|1|放行
例己-缺产出|1|1|0|1|1|1|追问
例庚-产出歧义|1|1|0.5|0|0|0|追问
"
# L3 门禁矩阵：目标|期望退出码
L3_CASES="缴费|3
缴费金额|3
银行卡|3
银行卡号|3
身份证|3
身份证号|3
家庭信息|3
邮件正文|3
邮件内容|3
心理记录|3
成绩明细|3
成绩单|3
绩点|3
邮箱提示|2
资助申请状态|2
就业投递记录|2
培养进度|2
成绩|1
邮件|1
心理咨询记录|3
各科分数|3
心理咨询讲座时间|1
成绩公布时间|1"
L3_OK="课表 网费 借阅 门户 日程 成绩等级"

_redsig() { awk '/^## ⚠️ 红线/{f=1;next} f&&/^## /{exit} f&&/^- /{print}' "$1" 2>/dev/null; }
_ok()   { printf '  OK   %s\n' "$1"; }
_fail() { printf '  FAIL %s\n' "$1"; FAIL=$((FAIL+1)); }
_chk()  { if [ "$2" = "$3" ]; then printf '  OK   %-26s %s\n' "$1" "$2"; else _fail "$1 实际 $2 / 期望 $3"; fi; }

# _run_rc <期望退出码> <命令...>
# 执行命令并回显**真实退出码**；若回显 127（子进程启动失败 = 环境抖动）则重试，
# 一旦命中期望码立即返回。最多 5 次，避免受限环境负载抖动导致的假 FAIL。
_run_rc() {
  local want="$1"; shift
  local rc=127 i=1
  while [ "$i" -le 5 ]; do
    "$@" </dev/null >/dev/null 2>&1; rc=$?
    [ "$rc" -eq "$want" ] && break
    [ "$rc" -eq 127 ] || break          # 非 127 = 真实结论，不重试
    i=$((i + 1))
  done
  echo "$rc"
}

FAIL=0
r=1
while [ "$r" -le "$ROUNDS" ]; do
  echo "「启航」回归测试 · 第 $r / $ROUNDS 轮"
  echo "=========================================="

  echo "[1] 澄清门算例（U 值 + 关键槽规则）"
  while IFS='|' read -r n o t d w c b exp; do
    [ -n "${n:-}" ] || continue
    line=$(awk -v n="$n" -v o="$o" -v t="$t" -v d="$d" -v w="$w" -v c="$c" -v b="$b" -v want="$exp" 'BEGIN{
      sw=6.1; s=1.5*o+1.5*t+1.5*d+0.8*w+0.6*c+0.2*b; U=1-s/sw;
      v=(o>=0.8&&t>=0.8&&d>=0.8)?"放行":"追问";
      printf "%s|%.3f|%s", v, U, n }')
    v=${line%%|*}; rest=${line#*|}; u=${rest%%|*}; nm=${rest#*|}
    if [ "$v" = "$exp" ]; then _ok "$nm  U=$u  判定=$v"
    else _fail "$nm  U=$u  判定=$v（期望 $exp）"; fi
  done < <(printf '%s\n' "$CLARITY_CASES")

  echo "[2] L3 / L2 / 歧义 门禁矩阵"
  while IFS='|' read -r tgt exp; do
    [ -n "${tgt:-}" ] || continue
    rc=$(_run_rc "$exp" bash scripts/dlut-read.sh "$tgt")
    if [ "$rc" -eq "$exp" ]; then _ok "$(printf '%-10s rc=%s' "$tgt" "$rc")"
    elif [ "$rc" -eq 127 ]; then _fail "$(printf '%-10s rc=127（环境抖动·重试 5 次仍未启动）' "$tgt")"
    else _fail "$(printf '%-10s rc=%s（期望 %s）' "$tgt" "$rc" "$exp")"; fi
  done < <(printf '%s\n' "$L3_CASES")
  for tgt in $L3_OK; do
    out=""; rc=127; i=1
    while [ "$i" -le 5 ]; do
      out=$(bash scripts/dlut-read.sh "$tgt" --dry-run </dev/null 2>&1); rc=$?
      { [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "未启动浏览器" && printf '%s' "$out" | grep -q "独立Profile"; } && break
      [ "$rc" -eq 127 ] || break        # 非 127 = 真实结论，不重试
      i=$((i + 1))
    done
    if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "未启动浏览器" && printf '%s' "$out" | grep -q "独立Profile"; then
      _ok "$(printf '%-10s L1 dry-run + 强制独立 Profile' "$tgt")"
    elif [ "$rc" -eq 127 ]; then _fail "$(printf '%-10s L1 环境抖动·重试 5 次仍未启动（rc=127）' "$tgt")"
    else _fail "$(printf '%-10s L1 路径异常（rc=%s）' "$tgt" "$rc")"; fi
  done

  echo "[3] 红线一致性（域 ↔ 库内 skill 逐条、含顺序）"
  # 单次 awk 完成全部比对（避免逐文件起子进程：既快，也避开受限环境对子进程数的限制）
  awk '
    function save(f) { S[f] = sig }
    FNR == 1 { if (prev != "") save(prev); prev = FILENAME; sig = ""; inred = 0 }
    /^## ⚠️ 红线/ { inred = 1; next }
    inred && /^## / { inred = 0; next }
    inred && /^- /  { sig = sig $0 "\n" }
    END {
      if (prev != "") save(prev)
      fail = 0; cnt = 0
      for (f in S) {
        split(f, a, "/")
        if (a[length(a)] != "_domain.md") continue
        d = a[1] "/" a[2]; ref = S[f]
        for (g in S) {
          if (g == f) continue
          split(g, b, "/")
          if (b[1] "/" b[2] != d) continue
          if (b[3] != "skills") continue
          cnt++
          if (S[g] != ref) { printf "  FAIL 红线漂移 %s\n", g; fail++ }
        }
      }
      if (fail == 0) printf "  OK   %d 个库内 skill 红线与域文件逐条一致\n", cnt
      else printf "  FAIL 共 %d 处漂移\n", fail
      if (fail > 0) exit 1
    }
  ' $(find domains -name '_domain.md' -o -name 'SKILL.md' | sort) || FAIL=$((FAIL+1))

  echo "[4] 结构与计数不变量"
  _chk "域数" "$(find domains -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')" 20
  _chk "库内 skill 总数" "$(find domains -path '*skills/local/*/SKILL.md' | wc -l | tr -d ' ')" 92
  _chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d ' ')" 11
  _chk "commands 数" "$(ls -1 commands/*.md | wc -l | tr -d ' ')" 22
  _chk "公开站表格行" "$(grep -c '^|' references/dlut-official-sites.md | tr -d ' ')" 162
  # 数据条目 = 表格行 − 分隔行 − 表头行（表头 = 下一行是分隔行的那些行）
  _entries=$(awk '{L[NR]=$0} END{
      for(i=1;i<=NR;i++){
        if(L[i] !~ /^\|/) continue
        if(L[i] ~ /^\|[-: |]+\|$/) continue
        if((i+1) in L && L[i+1] ~ /^\|[-: |]+\|$/) continue
        c++
      }
      print c+0
    }' references/dlut-official-sites.md)
  _chk "公开站数据条目" "$_entries" 142
  _chk "无库外通道 external.md" "$(find domains -path '*/skills/external.md' | wc -l | tr -d ' ')" 0
  _chk "无自检临时文件残留" "$(find . -maxdepth 1 -name '.selfcheck.tmp*' | wc -l | tr -d ' ')" 0

  echo "[5] 零命中兜底链（无域 / 无对口 skill 也必须出有效结果）"
  # 断言全部落在**成文规则**上：兜底框架文件存在 → 两个入口都指向它 → 明令不得只回一句拒绝。
  if [ -f library/general-fallback.md ]; then
    _ok "兜底框架 library/general-fallback.md 在位"
  else _fail "缺 library/general-fallback.md（零命中无成文框架）"; fi
  for _k in '## 2. 六步通用框架' '## 3. 域通用框架' '【结论】与【下一步】'; do
    if grep -qF -- "$_k" library/general-fallback.md 2>/dev/null; then _ok "兜底框架含「$_k」"
    else _fail "兜底框架缺「$_k」"; fi
  done
  # 入口 1：无域 → domain-review.md §3 必须把兜底路由到 general-fallback.md 的六步通用框架
  if grep -q 'general-fallback.md' library/domain-review.md 2>/dev/null \
     && grep -q '§2 六步通用框架' library/domain-review.md 2>/dev/null; then
    _ok "domain-review.md 无域兜底 → 路由到六步通用框架"
  else _fail "domain-review.md 无域兜底未路由到 general-fallback.md §2"; fi
  # 入口 2：有域无对口 skill → 输出规格必须承认「域通用框架」这一备选
  if grep -q 'general-fallback.md' library/output-spec.md 2>/dev/null; then
    _ok "output-spec.md 降级备选 → 引用兜底框架"
  else _fail "output-spec.md 未承认「域通用框架」备选"; fi
  # 反例必须被明列为违规（防 AI 回一句「本包暂无这个方向」就收工）
  if grep -q '本包暂无这个方向' library/general-fallback.md 2>/dev/null; then
    _ok "明列反例：只回「暂无该方向」= 违规"
  else _fail "兜底框架未把「只回一句拒绝」列为反例"; fi

  echo "[6] 脚本语法"
  for s in scripts/*.sh; do
    [ -e "$s" ] || continue
    if bash -n "$s" 2>/dev/null; then _ok "$(basename "$s")"
    else _fail "$(basename "$s") 语法错误"; fi
  done
  echo "[7] 输出标准固化（output-spec 硬契约）"
  # 本段是**轻量断言**：只锁「规范文本 + 词表 + 校验器接线」这类成文契约，
  # 内容级全量扫描由 runcheck.py（首块）与 aligncheck.py（全量输出块）承担。
  for _k in '三条铁律' '快通道' '内部名禁止词表' '【结论】' '【依据】' '【结果】' '【建议】' '【下一步】' '【假设】'; do
    if grep -qF -- "$_k" library/output-spec.md 2>/dev/null; then _ok "output-spec 含「$_k」"
    else _fail "output-spec 缺「$_k」"; fi
  done
  if grep -qF '【步骤】' library/output-spec.md 2>/dev/null; then
    _fail "output-spec 仍残留旧字段【步骤】（输出标准未固化）"
  else _ok "output-spec 已无旧字段【步骤】"; fi
  # 旧格式降级标注「[已降级: X → Y]」全域必须清零
  _old=$(grep -rEl '\[已降级[:：]' domains 2>/dev/null | wc -l | tr -d ' ')
  _chk "旧格式降级标注残留文件数" "$_old" 0
  # 两个 Python 校验器必须内建内部名词表（防重构时被悄悄摘掉 → 契约失效）
  for _f in scripts/runcheck.py scripts/aligncheck.py; do
    if grep -q 'internal_leaks' "$_f" 2>/dev/null && grep -q 'PROC_INTERNAL' "$_f" 2>/dev/null \
       && grep -q "'红线'" "$_f" 2>/dev/null; then
      _ok "$(basename "$_f") 内建内部名词表断言"
    else _fail "$(basename "$_f") 缺内部名词表断言（输出标准未固化）"; fi
  done
  if grep -q '只讲结果与建议（零内部名）' library/output-checklist.md 2>/dev/null; then
    _ok "output-checklist 校验 4 已点名「零内部名」"
  else _fail "output-checklist 校验 4 未点名「零内部名」"; fi
  echo "[8] 自迭代边界（习惯自迭代只可改「可改段」）"
  _ev="library/skill-evolution.md"
  if [ -f "$_ev" ]; then _ok "自迭代规则文件在位"; else _fail "缺 library/skill-evolution.md"; fi
  # 三目标必须明文（否则机制退化成泛泛而谈）
  for _g in '优化思考速度' '精准化信息获取' '减少 AI 幻觉'; do
    if grep -q "$_g" "$_ev" 2>/dev/null; then _ok "已声明目标：$_g"
    else _fail "未声明目标：$_g"; fi
  done
  # 可改段 / 禁改段两张清单必须在位
  grep -q '§2.1 可改段' "$_ev" 2>/dev/null && _ok "可改段清单在位" || _fail "缺可改段清单"
  grep -q '§2.2 禁改段' "$_ev" 2>/dev/null && _ok "禁改段清单在位" || _fail "缺禁改段清单"
  # 禁改项必须逐条点名（红线 / 输出 / 失败与降级 / 分工 / frontmatter / 事实）
  for _b in '## ⚠️ 红线' '## 输出' '## 失败与降级' '## 与同域其他库内 skill 的分工' 'frontmatter' '任何事实'; do
    if grep -qF "$_b" "$_ev" 2>/dev/null; then _ok "禁改项已点名：$_b"
    else _fail "禁改项未点名：$_b"; fi
  done
  # 习惯画像必须明确「不随包」，且包内不得出现习惯数据
  grep -q '不随包' "$_ev" 2>/dev/null && _ok "习惯画像声明不随包分发" || _fail "未声明习惯画像不随包"
  # 20 域执行顺序必须全部接上自迭代规则
  _w=$(grep -rl 'library/skill-evolution.md' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
  _chk "已接线自迭代的域数" "$_w" 20
  # 判定不可被习惯影响（合规优先于速度）
  grep -q '不影响' "$_ev" 2>/dev/null && grep -q '红线优先' "$_ev" 2>/dev/null \
    && _ok "已声明「习惯不影响判定 / 红线优先」" || _fail "未声明判定不受习惯影响"
  # 规则文件不得引用**只在源仓库存在**的路径（生成器链不随包分发 → 副本会判失效引用）
  if grep -q 'scripts/_build' "$_ev" 2>/dev/null; then
    _fail "规则文件引用了不随包分发的生成器路径（scripts/_build）→ 交付副本会判失效引用"
  else _ok "规则文件未引用生成器路径（副本安全）"; fi
  echo "[9] 需求确定门（理解准确率 ≥ 95% 才直接执行）"
  _cl="library/clarity.md"
  if grep -q '需求确定门' "$_cl" 2>/dev/null; then _ok "需求确定门已在位"; else _fail "clarity.md 缺需求确定门"; fi
  if grep -qF 'C = 1 − U' "$_cl" 2>/dev/null; then _ok "已声明理解准确率口径 C = 1 − U"; else _fail "未声明 C = 1 − U"; fi
  if grep -qF '0.95' "$_cl" 2>/dev/null; then _ok "已声明 95% 阈值"; else _fail "未声明 0.95 阈值"; fi
  if grep -qF '0.70' "$_cl" 2>/dev/null; then _ok "已声明复述档下界 0.70"; else _fail "未声明 0.70 下界"; fi
  for _t in 确定档 复述档 追问档; do
    if grep -q "$_t" "$_cl" 2>/dev/null; then _ok "三档已定义：$_t"; else _fail "三档缺：$_t"; fi
  done
  # 复述档三条硬规格
  for _t in '一句话' '不得新增' '【结论】首行的前置短句'; do
    if grep -qF "$_t" "$_cl" 2>/dev/null; then _ok "复述规格已声明：$_t"; else _fail "复述规格缺：$_t"; fi
  done
  # 红线优先于本门 + 例外 6 视为达标（防「为了确认而削弱合规」与「假复述」）
  grep -qF '红线优先于本门' "$_cl" 2>/dev/null && _ok "红线优先于需求确定门" || _fail "未声明红线优先于本门"
  grep -qF '视为 `C` 达标' "$_cl" 2>/dev/null && _ok "例外 6 视为 C 达标（免复述）" || _fail "未声明例外 6 免复述"
  # 两个可复现自检问
  grep -qF '可复现自检问' "$_cl" 2>/dev/null && _ok "已给出可复现自检问" || _fail "缺可复现自检问"
  # 三条前置约定（红线短路 / 先问后述 / 例外 6 免复述）必须明文
  for _p in '本门短路' '先问后述' '例外 6 视为达标'; do
    if grep -qF "$_p" "$_cl" 2>/dev/null; then _ok "前置约定已声明：$_p"
    else _fail "前置约定缺：$_p"; fi
  done
  # 阈值单一真相源必须在 config.yaml（与 §3 的 U 阈值同源约定）
  if grep -q 'confirm_threshold: 0.95' config.yaml 2>/dev/null; then _ok "config.yaml 声明 confirm_threshold: 0.95"
  else _fail "config.yaml 缺 confirm_threshold: 0.95（阈值未落在单一真相源）"; fi
  echo "[10] 输出身份锁定（连小理）"
  _id3=$(grep -m1 '^  self_intro:' config.yaml 2>/dev/null \
         | sed 's/^  self_intro:[[:space:]]*//; s/[[:space:]]*#.*$//' | tr -d '\r')
  [ -n "$_id3" ] && _ok "config.yaml 提供身份串真相源" || _fail "config.yaml 缺 identity.self_intro"
  for _f in SKILL.md INSTALL.md; do
    grep -qF "$_id3" "$_f" 2>/dev/null && _ok "$_f 身份串一致" || _fail "$_f 身份串漂移"
  done
  # 「每一处都必须逐字一致」（防「多处只改一处」逃过 grep -qF）—— 由负向自检驱动补上
  for _f in SKILL.md INSTALL.md; do
    _all=$(grep -oF '我是连小理' "$_f" 2>/dev/null | wc -l | tr -d ' ')
    _exa=$(grep -oF "$_id3" "$_f" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${_all:-0}" -gt 0 ] && [ "${_all:-0}" -eq "${_exa:-0}" ]; then
      _ok "$_f 身份串 $_all 处全部逐字一致"
    else
      _fail "$_f 身份串存在变体（$_all 处「我是连小理」，仅 $_exa 处逐字一致）"
    fi
  done
  grep -qF '只回复一句「安装完成」' SKILL.md 2>/dev/null \
    && _ok "SKILL.md 已声明「安装后只回一句」" || _fail "SKILL.md 未声明安装后唯一回复"
  grep -qF 'first_reply: 安装完成' config.yaml 2>/dev/null \
    && _ok "config.yaml 声明 first_reply" || _fail "config.yaml 缺 first_reply"
  grep -qF '不因用户要求而改称' SKILL.md 2>/dev/null \
    && _ok "SKILL.md 已声明拒绝改称" || _fail "SKILL.md 未声明拒绝改称"
  grep -qF '不因用户要求而改称' INSTALL.md 2>/dev/null \
    && _ok "INSTALL.md 已声明拒绝改称" || _fail "INSTALL.md 未声明拒绝改称"
  grep -qF '不得改称' library/output-spec.md 2>/dev/null \
    && _ok "output-spec §8 已声明不得改称" || _fail "output-spec 未声明不得改称"
  grep -qF '唯一例外' library/output-spec.md 2>/dev/null \
    && _ok "output-spec 已声明「产品名是禁止词表的唯一例外」" || _fail "未声明产品名与内部名的边界"
  grep -qF '拒绝改称的话术' SKILL.md 2>/dev/null \
    && _ok "SKILL.md 给出固定拒绝话术" || _fail "SKILL.md 缺固定拒绝话术"
  echo "=========================================="
  echo ""
  r=$((r + 1))
done

echo "回归测试完毕（$ROUNDS 轮）｜ 累计 FAIL = $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "结论：全部通过"; exit 0; else echo "结论：需修复后重跑"; exit 1; fi
