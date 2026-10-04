#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自检单入口：一次跑齐静态检查器 + 逐项计时 + 结果摘要（可选负向自测）。

为什么要有它：此前要手工跑多条命令（顺序、轮数、工作目录都可能漏）—— **漏跑本身就是缺陷来源**。
本入口固定顺序、固定编码、逐项计时、任一 FAIL 即非零退出，并打印检查项摘要供回归对比。

用法：
    python scripts/checkall.py [树根]              # 全跑（regress 1 轮）
    python scripts/checkall.py . --quick          # 只跑 selfcheck / aligncheck / runcheck（高频迭代用）
    python scripts/checkall.py . --rounds 3       # regress 与两个 py 校验器连跑 3 轮
    python scripts/checkall.py . --negative       # 追加负向自测（断言非空转；较慢）
    python scripts/checkall.py . --limit 600      # 时间预算（秒）；超出只记 WARN，不判 FAIL

判据：全部 PASS → rc 0；任一 FAIL → rc 1。
时间只**报告**与提示（超基线记 WARN，不判 FAIL）—— 本机在高负载下会偶发 rc=127 抖动，硬失败会制造假故障。

时间基线（本机实测，2026-10-03）：selfcheck ~27s ｜ audit ~46s ｜ aligncheck ~0.6s ｜ runcheck ~0.3s ｜
regress ~44s ｜ negative ~3s（2026-10-04 起含「零注入交付树基线」，多跑一遍 checkall → ~30s）｜
**--quick 全跑 ~28s ／ full+negative ~121s**。基线只作「速度回归」参照。
"""
import os, re, sys, time, shutil, subprocess

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..'))
QUICK = '--quick' in sys.argv
NEGATIVE = '--negative' in sys.argv
# ⚠️ 递归护栏：`negative_test.py` 的「零注入交付树基线」会回调 checkall —— 不阻断的话
# `checkall.py . --negative` 会变成 checkall → negative → checkall → … 无限递归。
if os.environ.get('QIHANG_NEGTEST_CHILD'):
    NEGATIVE = False
ROUNDS = '1'
if '--rounds' in sys.argv:
    ROUNDS = sys.argv[sys.argv.index('--rounds') + 1]
LIMIT = 600
if '--limit' in sys.argv:
    LIMIT = float(sys.argv[sys.argv.index('--limit') + 1])
PY = sys.executable or 'python'

# ⚠️ 关键坑（实测）：在 Python 里直接 subprocess 调 `bash` 会落到 **WSL**（`System32\bash.exe`）
# → 脚本秒退、rc≠0、零输出（本项目记忆里记过同型坑）。必须显式找 Git Bash。
def bash_bin():
    for c in (os.environ.get('BASH'), os.environ.get('EXEPATH'),
              r'C:\Program Files\Git\bin\bash.exe',
              r'C:\Program Files (x86)\Git\bin\bash.exe',
              r'C:\Program Files\Git\usr\bin\bash.exe'):
        if c and os.path.isfile(c):
            return c
    w = shutil.which('bash')
    return w if (w and 'system32' not in w.lower()) else None


BASH = bash_bin()


def resolve(cmd):
    """把带标记的命令解析成真实 argv；bash 类缺 Git Bash 时返回 None（按环境项跳过，不判 FAIL）。"""
    if cmd[0] == '@bash':
        return ([BASH] + cmd[1:]) if BASH else None
    if cmd[0] == '@py':
        return [PY] + cmd[1:]
    return cmd


# 顺序即依赖：selfcheck（结构）→ audit（安全）→ aligncheck（对齐）→ runcheck（可跑）→ regress（行为）
# 末位数字 = **FAIL 计数的分组序号**（`K` 列表的 `fgrp`）：
#   计数次序（从 0 开始）；selfcheck/audit 的 FAIL 在最后，aligncheck/runcheck/regress 在最前。
CHECKS = [
    ('selfcheck', ['@bash', 'scripts/selfcheck.sh'], r'结果:\s*OK\s*(\d+)\s*｜\s*WARN\s*(\d+)\s*｜\s*FAIL\s*(\d+)', '结构 / 计数 / 交叉引用', 2),
    ('audit', ['@bash', 'scripts/audit.sh'], r'结果:\s*✅\s*(\d+)\s*通过\s*｜\s*⚠️?\s*(\d+)\s*警告\s*｜\s*❌\s*(\d+)\s*失败', '安全 / 合规 / 门禁', 2),
    ('aligncheck', ['@py', 'scripts/aligncheck.py', '.', ROUNDS], r'最终：FAIL\s*(\d+)\s*｜\s*WARN\s*(\d+)', '全量文件级对齐', 0),
    ('runcheck', ['@py', 'scripts/runcheck.py', '.', ROUNDS], r'最终：FAIL\s*(\d+)\s*｜\s*WARN\s*(\d+)', '静态路由 / 示例 / 输出契约', 0),
    ('extskill', ['@py', 'scripts/extskill.py', '.'], r'结果:\s*OK\s*(\d+)\s*｜\s*WARN\s*(\d+)\s*｜\s*FAIL\s*(\d+)', '外部 skill 桥接（接线 + 登记 + 许可）', 2),
    ('regress', ['@bash', 'scripts/regress.sh', ROUNDS], r'累计 FAIL\s*=\s*(\d+)', '行为回归（澄清门 / 门禁 / 输出标准）', 0),
]

BASELINE = {'selfcheck': 35.0, 'audit': 55.0, 'aligncheck': 5.0, 'runcheck': 5.0, 'regress': 60.0}

print('自检单入口 · 目标树：%s' % ROOT)
print('模式：%s ｜ regress 轮数 %s ｜ 时间预算 %.0fs' % ('quick' if QUICK else 'full', ROUNDS, LIMIT))
print('=' * 76)
env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'

rows, failed, warned, skipped = [], [], [], []
t_all = time.time()
for name, cmd, pat, what, fgrp in CHECKS:
    if QUICK and name in ('audit', 'regress'):
        print('-- %-11s 跳过（--quick）' % name)
        continue
    argv = resolve(cmd)
    if argv is None:
        print('-- %-11s %-22s SKIP  未找到 Git Bash（bash 类校验无法运行；环境项，不判 FAIL）' % (name, what))
        skipped.append(name)
        continue
    t0 = time.time()
    r = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    out = r.stdout.decode('utf-8', 'replace')
    rc = r.returncode
    if rc == 127:                     # 本机已知抖动：子进程启动失败，重试一次再判
        time.sleep(0.5)
        r = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
        out = r.stdout.decode('utf-8', 'replace')
        rc = r.returncode
        note = '（rc=127 抖动，已重试）'
    else:
        note = ''
    dt = time.time() - t0
    m = re.search(pat, out)
    if m:
        nums = [int(x) for x in m.groups()]
        bad = nums[fgrp]
        detail = ' / '.join(str(x) for x in nums)
    else:
        bad = 1
        detail = '未匹配到结果行（rc=%d）' % rc
    ok = (rc == 0 and bad == 0)
    rows.append((name, what, ok, dt, detail, note))
    if not ok:
        failed.append(name)
    if dt > BASELINE.get(name, 60.0):
        warned.append('%s %.1fs（基线 ~%.0fs）' % (name, dt, BASELINE.get(name, 60.0)))
    print('-- %-11s %-22s %s  %6.1fs  [%s]%s'
          % (name, what, 'PASS' if ok else 'FAIL', dt, detail, note))
    if not ok:
        tail = [l for l in out.rstrip().splitlines() if 'FAIL' in l or '失败' in l or 'Error' in l][:6]
        for l in tail:
            print('     | %s' % l.strip())
        if not tail:
            for l in out.rstrip().splitlines()[-4:]:
                print('     > %s' % l.strip())

if NEGATIVE:
    print('-- %-11s %-22s' % ('negative', '负向自测（断言非空转）'))
    t0 = time.time()
    argv = ([PY, 'scripts/negative_test.py', '.'])
    r = subprocess.run(argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    out = r.stdout.decode('utf-8', 'replace')
    dt = time.time() - t0
    print(out.rstrip())
    ok = (r.returncode == 0)
    rows.append(('negative', '负向自测', ok, dt, '捕获率见上', ''))
    if not ok:
        failed.append('negative')

total = time.time() - t_all
print('=' * 76)
print('校验结果摘要（每项关键计数）')
for name, what, ok, dt, detail, note in rows:
    print('  %-11s %-6s %6.1fs  %s' % (name, 'PASS' if ok else 'FAIL', dt, detail))
if skipped:
    print('  !! 未运行 %d 项（缺 Git Bash）：%s' % (len(skipped), ', '.join(skipped)))
print('-' * 76)
if warned:
    print('时间提示（超基线，非失败）：%s' % '；'.join(warned))
print('总耗时 %.1fs ｜ 预算 %.0fs ｜ %s' % (total, LIMIT, '在预算内' if total <= LIMIT else '超预算（WARN）'))
print('结论：%s' % ('✅ 全部 PASS' if not failed else '❌ 失败项 %d：%s' % (len(failed), ', '.join(failed))))
sys.exit(0 if not failed else 1)
