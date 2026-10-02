# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 12 层 · 校验器阈值同步】校验器阈值同步：selfcheck/regress/audit 中 52 → 92、每域 2–3 → 4–5
# 原名 gen_counts.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 在已达 92 的树上重跑为 MISS（无害）
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
import os, io, sys
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
def edit(rel, pairs):
    p = os.path.join(ROOT, rel)
    t = io.open(p, 'r', encoding='utf-8').read()
    o = t
    for a, b in pairs:
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:60])); continue
        t = t.replace(a, b); print('  [OK] %s :: %r' % (rel, a[:50]))
    if t != o:
        io.open(p, 'w', encoding='utf-8', newline='').write(t)

print('== selfcheck.sh ==')
edit('scripts/selfcheck.sh', [
 ('[ "$n_lsk" -eq 52 ] && ok "52 个库内 skill 在位" || { bad "库内 skill = $n_lsk（期望 52）"; nbad=$((nbad+1)); }',
  '[ "$n_lsk" -eq 92 ] && ok "92 个库内 skill 在位" || { bad "库内 skill = $n_lsk（期望 92）"; nbad=$((nbad+1)); }'),
 ('[ "${nsk:-0}" -eq 52 ] && ok "库内 skill = 52（每域 2–3 个）" || bad "库内 skill = $nsk（期望 52）"',
  '[ "${nsk:-0}" -eq 92 ] && ok "库内 skill = 92（每域 4–5 个）" || bad "库内 skill = $nsk（期望 92）"'),
 ('# 单遍统计每域 skill 数（避免逐域起子进程）；每域应为 2 或 3 个',
  '# 单遍统计每域 skill 数（避免逐域起子进程）；每域应为 4 或 5 个'),
 ("| sort | uniq -c | awk '$1!=2 && $1!=3' | wc -l | tr -d ' ')",
  "| sort | uniq -c | awk '$1<4 || $1>5' | wc -l | tr -d ' ')"),
 ('[ "${_pbad:-0}" -eq 0 ] && ok "每域均为 2–3 个库内 skill" || bad "$_pbad 个域的库内 skill 数不在 2–3"',
  '[ "${_pbad:-0}" -eq 0 ] && ok "每域均为 4–5 个库内 skill" || bad "$_pbad 个域的库内 skill 数不在 4–5"'),
])

print('== regress.sh ==')
edit('scripts/regress.sh', [
 ("_chk \"库内 skill 总数\" \"$(find domains -path '*skills/local/*/SKILL.md' | wc -l | tr -d ' ')\" 52",
  "_chk \"库内 skill 总数\" \"$(find domains -path '*skills/local/*/SKILL.md' | wc -l | tr -d ' ')\" 92"),
])

print('== audit.sh ==')
edit('scripts/audit.sh', [
 ('# 每域 2–3 个库内 skill，故期望 = 实际库内 skill 数（且 ≥ 2×域数）',
  '# 每域 4–5 个库内 skill，故期望 = 实际库内 skill 数（且 ≥ 2×域数）'),
 ('ok "库内 skill 红线覆盖 $nred2/$nlocal（每域 2–3 个）"',
  'ok "库内 skill 红线覆盖 $nred2/$nlocal（每域 4–5 个）"'),
])
print('done')
