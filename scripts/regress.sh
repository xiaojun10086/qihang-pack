#!/usr/bin/env bash
# 「启航」回归测试（v2.7 新增）
# 用法: bash scripts/regress.sh          # 跑一轮
#       bash scripts/regress.sh 3        # 连跑 3 轮（验证确定性）
#
# 与 selfcheck.sh / audit.sh 的分工：
#   selfcheck.sh  静态结构与计数
#   audit.sh      安全与门禁
#   regress.sh    **行为回归**：澄清门算例 / L3 门禁矩阵 / 红线一致性 / 结构不变量
#
# 设计约束：**零临时文件**（受限环境里 rm 可能被拦截，写临时文件会让脚本静默失败）；
#           **不依赖 seq 等外部命令**（Windows Git Bash 精简环境可能缺）。
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
简历|3
邮箱提示|2
成绩|1"
L3_OK="课表 网费 借阅 门户 日程"

_redsig() { awk '/^## ⚠️ 红线/{f=1;next} f&&/^## /{exit} f&&/^- /{print}' "$1" 2>/dev/null; }
_ok()   { printf '  OK   %s\n' "$1"; }
_fail() { printf '  FAIL %s\n' "$1"; FAIL=$((FAIL+1)); }
_chk()  { if [ "$2" = "$3" ]; then printf '  OK   %-26s %s\n' "$1" "$2"; else _fail "$1 实际 $2 / 期望 $3"; fi; }

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
    bash scripts/dlut-read.sh "$tgt" </dev/null >/dev/null 2>&1
    rc=$?
    if [ "$rc" -eq "$exp" ]; then _ok "$(printf '%-10s rc=%s' "$tgt" "$rc")"
    else _fail "$(printf '%-10s rc=%s（期望 %s）' "$tgt" "$rc" "$exp")"; fi
  done < <(printf '%s\n' "$L3_CASES")
  for tgt in $L3_OK; do
    out=$(bash scripts/dlut-read.sh "$tgt" --dry-run </dev/null 2>&1); rc=$?
    if [ "$rc" -eq 0 ] && printf '%s' "$out" | grep -q "未启动浏览器" && printf '%s' "$out" | grep -q "独立Profile"; then
      _ok "$(printf '%-10s L1 dry-run + 强制独立 Profile' "$tgt")"
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
  _chk "域数" "$(find domains -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')" 19
  _chk "库内 skill 总数" "$(find domains -path '*skills/local/*/SKILL.md' | wc -l | tr -d ' ')" 38
  _chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d ' ')" 8
  _chk "commands 数" "$(ls -1 commands/*.md | wc -l | tr -d ' ')" 21
  _chk "公开站表格行" "$(grep -c '^|' references/dlut-official-sites.md | tr -d ' ')" 160
  _chk "external.md 含 DUT 落地评估" "$(grep -l 'DUT 落地评估' domains/*/skills/external.md | wc -l | tr -d ' ')" 19
  _chk "无自检临时文件残留" "$(find . -maxdepth 1 -name '.selfcheck.tmp*' | wc -l | tr -d ' ')" 0

  echo "[5] 脚本语法"
  for s in scripts/*.sh; do
    [ -e "$s" ] || continue
    if bash -n "$s" 2>/dev/null; then _ok "$(basename "$s")"
    else _fail "$(basename "$s") 语法错误"; fi
  done
  echo "=========================================="
  echo ""
  r=$((r + 1))
done

echo "回归测试完毕（$ROUNDS 轮）｜ 累计 FAIL = $FAIL"
if [ "$FAIL" -eq 0 ]; then echo "结论：全部通过"; exit 0; else echo "结论：需修复后重跑"; exit 1; fi
