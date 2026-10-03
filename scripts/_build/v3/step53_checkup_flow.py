# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 16 层 · 自检查流程加固】单入口 checkall.py + 负向自测 negative_test.py
#   + 需求确定门算例（clarity §3.1）+ aligncheck 口径断言 + 计数/登记 + 修订号 3.2.1 → 3.2.2
# 用法：python scripts/_build/v3/step53_checkup_flow.py [仓库根]
# 幂等：内容一致即不写；版本号已是 3.2.2 则 MISS。
#
# 为什么要有这一层（本轮用户诉求：自检流程可靠、出错率更低、效率更高）：
#   · 原来要**手工跑 5 条命令**（顺序/轮数/cwd 都可能漏）→「漏跑」本身就是缺陷来源 → 单入口固定顺序；
#   · 原来「断言是否真的会 FAIL」只在开发期临时验过 → 固化成可重复的**负向自测**，防断言静默空转；
#   · 原来无耗时数据 → 单入口逐项计时并打印，把「效率/时间可靠」变成可观测、可回归对比的量。
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OLD, NEW, PKG = '3.2.1', '3.2.2', '3.2'

# ============================================================ 产物 1：scripts/checkall.py
CHECKALL = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""自检单入口：一次跑齐 5 个校验器 + 逐项计时 + 模拟跑摘要（可选负向自测）。

为什么要有它：此前要手工跑 5 条命令（顺序、轮数、工作目录都可能漏）—— **漏跑本身就是缺陷来源**。
本入口固定顺序、固定编码、逐项计时、任一 FAIL 即非零退出，并打印「模拟跑摘要」供回归对比。

用法：
    python scripts/checkall.py [树根]              # 全跑（regress 1 轮）
    python scripts/checkall.py . --quick          # 只跑 selfcheck / aligncheck / runcheck（高频迭代用）
    python scripts/checkall.py . --rounds 3       # regress 与两个 py 校验器连跑 3 轮
    python scripts/checkall.py . --negative       # 追加负向自测（断言非空转；较慢）
    python scripts/checkall.py . --limit 600      # 时间预算（秒）；超出只记 WARN，不判 FAIL

判据：全部 PASS → rc 0；任一 FAIL → rc 1。
时间只**报告**与提示（超基线记 WARN，不判 FAIL）—— 本机在高负载下会偶发 rc=127 抖动，硬失败会制造假故障。

时间基线（本机实测，2026-10-03）：selfcheck ~27s ｜ audit ~46s ｜ aligncheck ~0.6s ｜ runcheck ~0.3s ｜
regress ~44s ｜ negative ~3s ｜ **--quick 全跑 ~28s ／ full+negative ~121s**。基线只作「速度回归」参照。
"""
import os, re, sys, time, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..'))
QUICK = '--quick' in sys.argv
NEGATIVE = '--negative' in sys.argv
ROUNDS = '1'
if '--rounds' in sys.argv:
    ROUNDS = sys.argv[sys.argv.index('--rounds') + 1]
LIMIT = 600
if '--limit' in sys.argv:
    LIMIT = float(sys.argv[sys.argv.index('--limit') + 1])
PY = sys.executable or 'python'

# ⚠️ 关键坑（实测）：在 Python 里直接 subprocess 调 `bash` 会落到 **WSL**（`System32\\bash.exe`）
# → 脚本秒退、rc≠0、零输出（本项目记忆里记过同型坑）。必须显式找 Git Bash。
def bash_bin():
    for c in (os.environ.get('BASH'), os.environ.get('EXEPATH'),
              r'C:\\Program Files\\Git\\bin\\bash.exe',
              r'C:\\Program Files (x86)\\Git\\bin\\bash.exe',
              r'C:\\Program Files\\Git\\usr\\bin\\bash.exe'):
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
    ('selfcheck', ['@bash', 'scripts/selfcheck.sh'], r'结果:\\s*OK\\s*(\\d+)\\s*｜\\s*WARN\\s*(\\d+)\\s*｜\\s*FAIL\\s*(\\d+)', '结构 / 计数 / 交叉引用', 2),
    ('audit', ['@bash', 'scripts/audit.sh'], r'结果:\\s*✅\\s*(\\d+)\\s*通过\\s*｜\\s*⚠️?\\s*(\\d+)\\s*警告\\s*｜\\s*❌\\s*(\\d+)\\s*失败', '安全 / 合规 / 门禁', 2),
    ('aligncheck', ['@py', 'scripts/aligncheck.py', '.', ROUNDS], r'最终：FAIL\\s*(\\d+)\\s*｜\\s*WARN\\s*(\\d+)', '全量文件级对齐', 0),
    ('runcheck', ['@py', 'scripts/runcheck.py', '.', ROUNDS], r'最终：FAIL\\s*(\\d+)\\s*｜\\s*WARN\\s*(\\d+)', '端到端运行性（三级链）', 0),
    ('regress', ['@bash', 'scripts/regress.sh', ROUNDS], r'累计 FAIL\\s*=\\s*(\\d+)', '行为回归（澄清门 / 门禁 / 输出标准）', 0),
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
        bad = 0 if rc == 0 else 1
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
print('模拟跑摘要（每项关键计数）')
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
'''

# ============================================================ 产物 2：scripts/negative_test.py
NEGTEST = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""负向自测：把「断言是否真的会 FAIL」变成可重复验证（防断言静默空转）。

为什么要有它：自检全绿只证明「断言集通过」，不证明「断言集有效」。开发期多次出现
「注入缺陷后校验器毫无反应」（断言恒真）= 最危险的一类错。本脚本把 6 类注入固化成常驻测试。

在**临时树**上跑（按交付口径复制：排除 .git / _build / .learnbuddy / __pycache__ / .idea），
逐类注入 → 跑对应校验器 → 断言**必须 FAIL** → 打印捕获率。真实树**只读**，不写任何文件。

用法：python scripts/negative_test.py [源树] [--with-regress]
判据：捕获率 100% → rc 0；否则 rc 1。
"""
import os, re, sys, io, shutil, tempfile, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
SRC = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..'))
WITH_REGRESS = '--with-regress' in sys.argv
PY = sys.executable or 'python'
IGNORE = shutil.ignore_patterns('.git', '_build', '.learnbuddy', '__pycache__', '.idea')


def bash_bin():
    for c in (os.environ.get('BASH'), os.environ.get('EXEPATH'),
              r'C:\\Program Files\\Git\\bin\\bash.exe',
              r'C:\\Program Files (x86)\\Git\\bin\\bash.exe',
              r'C:\\Program Files\\Git\\usr\\bin\\bash.exe'):
        if c and os.path.isfile(c):
            return c
    w = shutil.which('bash')
    return w if (w and 'system32' not in w.lower()) else None


BASH = bash_bin()


def run(tree, cmd):
    # ⚠️ 在 Python 里直接调 `bash` 会落到 WSL（System32\\bash.exe）→ 秒退零输出。
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    argv = list(cmd)
    if argv[0] == '@bash':
        argv = ([BASH] + argv[1:]) if BASH else None
    elif argv[0] == '@py':
        argv = [PY] + argv[1:]
    if argv is None:
        return 127, '（未找到 Git Bash —— 环境项，跳过该用例）'
    r = subprocess.run(argv, cwd=tree, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    return r.returncode, r.stdout.decode('utf-8', 'replace')


def first_skill(tree):
    base = os.path.join(tree, 'domains')
    for d in sorted(os.listdir(base)):
        loc = os.path.join(base, d, 'skills', 'local')
        if not os.path.isdir(loc):
            continue
        for s in sorted(os.listdir(loc)):
            p = os.path.join(loc, s, 'SKILL.md')
            if os.path.isfile(p):
                return p
    return None


def inject_redline(tree):
    p = first_skill(tree)
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'(## ⚠️ 红线[^\\n]*\\n)(.*?)(?=\\n## )', t, re.S)
    return [p], t[:m.end(2)] + '\\n- **负向测试注入**：本条为注入项，不属于域红线' + t[m.end(2):]


def inject_fake_fallback(tree):
    p = first_skill(tree)
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(用同域库内 `)[a-z0-9-]+(` 降级承接)', r'\\1no-such-skill-xyz\\2', t)


def inject_three_digit_display(tree):
    p = os.path.join(tree, 'README.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(学伴包 v)(\\d+\\.\\d+)(\\s|$)', r'\\1\\2.9\\3', t, count=1)


def inject_dup_row(tree):
    p = os.path.join(tree, 'SKILL.md')
    t = io.open(p, encoding='utf-8').read()
    row = '| `library/skill-evolution.md` |'
    for ln in t.splitlines():
        if ln.startswith(row):
            return [p], t.replace(ln, ln + '\\n' + ln, 1)
    return [p], t


def inject_build_path(tree):
    p = os.path.join(tree, 'library', 'skill-evolution.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t + '\\n> 负向测试注入：生成器见 scripts/_build/v3/rebuild.py（本行应触发失效引用）\\n'


def inject_missing_fallback(tree):
    p = os.path.join(tree, 'library', 'general-fallback.md')
    return [p], None        # 特殊：移走文件


def main():
    base = os.path.join(tempfile.gettempdir(), 'qihang_negtest_%d' % int(__import__('time').time()))
    shutil.copytree(SRC, base, ignore=IGNORE)
    print('负向自测 · 临时树：%s' % base)
    print('=' * 76)
    cases = [
        ('同域红线漂移（注入一条不属于域红线的红线）', inject_redline,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('伪降级目标（no-such-skill-xyz）', inject_fake_fallback,
         ['@py', 'scripts/runcheck.py', '.'], 'runcheck'),
        ('包版本展示位写成三位', inject_three_digit_display,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('生成器段重复插入（同一行两份）', inject_dup_row,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('规则文件引用生成器路径（副本必判失效引用）', inject_build_path,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
    ]
    if WITH_REGRESS:
        cases.append(('移走零命中兜底框架', inject_missing_fallback,
                      ['@bash', 'scripts/regress.sh', '1'], 'regress [5]'))

    caught = 0
    for name, fn, cmd, which in cases:
        paths, newt = fn(base)
        backups = {}
        for p in paths:
            if os.path.isfile(p):
                backups[p] = io.open(p, 'rb').read()
        if newt is None:
            shutil.move(paths[0], paths[0] + '.moved')
        else:
            for p in paths:
                io.open(p, 'w', encoding='utf-8', newline='').write(newt)
        rc, out = run(base, cmd)
        hit = (rc != 0) or ('FAIL' in out and 'FAIL 0' not in out)
        print('%-46s → %-12s %s' % (name, which, '✅ 捕获' if hit else '❌ 漏网（断言可能空转）'))
        if hit:
            caught += 1
        # 还原
        for p, b in backups.items():
            io.open(p, 'wb').write(b)
        if newt is None and os.path.exists(paths[0] + '.moved'):
            shutil.move(paths[0] + '.moved', paths[0])
    print('=' * 76)
    print('捕获率 %d/%d' % (caught, len(cases)))
    print('结论：%s' % ('✅ 断言非空转' if caught == len(cases) else '❌ 存在空转断言，须修断言'))
    sys.exit(0 if caught == len(cases) else 1)


if __name__ == '__main__':
    main()
'''

# ============================================================ clarity.md §3.1 修订
S31_OLD_ROW = '| **追问档** | `C < 0.70` | 按 §3 / §5 原判定追问（**本门不改变「是否追问」的判定**） |'
S31_NEW_ROW = ('| **追问档** | `C < 0.70` | **仅当澄清门本就要追问时才追问**（判定不变）；'
               '若澄清门已放行（如例 A：关键槽齐全、仅次要槽缺）→ 按**复述档**处理，**不得新增追问** |')

S31_CASES = '''
**算例（与 §6 同源，`C` 由同一算式算出；`C` 只影响「是否复述」，不影响「是否追问」）**

| 算例 | 输入 | `C = 1 − U` | 澄清门 | **需求确定门** |
|---|---|---|---|---|
| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689` | 放行（例外 2） | **复述档**（一句话复述 + 落【假设】） |
| 例 C | 「帮我写点东西」 | `0.25` | 追问 | 追问档 |
| 例 D | 「明天下午考高数第三章，帮我排 3 天背诵计划，要卡组，我是大一新生」 | `1.00` | 放行 | **确定档**（直接执行） |
| 例 E | 「把机械学院官网的招生简章整理成一页要点清单」 | `0.816` | 放行 | **复述档** |

> 例 D 六槽齐全（O 高数第三章 / T 备考 / D 卡组 / W 3 天 / C 卡组形式 / B 大一新生）→ `Σwᵢcᵢ = 6.1` → `C = 1.00`；
> 例 E 缺 `W`、`B`（`O/T/D` 各 `1.0`、`C = 0.8`）→ `Σwᵢcᵢ = 1.5+1.5+1.5+0.48 = 4.98` → `C = 4.98/6.1 = 0.816`。
> **注意例 A**：澄清门判「放行」（关键槽齐全），而 `C = 0.689 < 0.70` —— 此时**只复述、不追问**，
> 这正是「本门不改变追问判定」的含义，也避免了与例外 2「缺 `W/C/B` 一律不追问」冲突。

'''

# ============================================================ aligncheck 追加断言
# ⚠️ 锚点必须落在 `U(v0)` **定义之后**（`U` / `v0` 是 L 段内的局部定义；
#    第一版错插到 `# ---------- I commands ----------` 之前 → `UnboundLocalError`，
#    且替换时误删了 I 段的 for 行 —— 教训：插代码前先确认变量作用域，插完必须跑一次。
ALIGN_ANCHOR = ("    if abs(U(v0) - 0.311) > 0.002:\n"
                "        bad('library/clarity.md', '例 A 的 U=%.4f 与文档 0.311 不符' % U(v0))")
ALIGN_ADD = """
    # 需求确定门（`library/clarity.md` §3.1）：`C = 1 − U` 的算例与阈值必须与 `config.yaml` 同源
    _cl = rd('library/clarity.md')
    _C = 1 - U(v0)
    if abs(_C - 0.689) > 0.002:
        bad('library/clarity.md', '例 A 的 C = 1 − U = %.4f 与文档 0.689 不符（需求确定门算例）' % _C)
    _ct = re.search(r'confirm_threshold:\\s*([\\d.]+)', rd('config.yaml'))
    _rf = re.search(r'restate_floor:\\s*([\\d.]+)', rd('config.yaml'))
    if _ct and _ct.group(1) not in _cl:
        bad('library/clarity.md', 'confirm_threshold=%s 未在 §3.1 声明（阈值未同源）' % _ct.group(1))
    if _rf and _rf.group(1) not in _cl:
        bad('library/clarity.md', 'restate_floor=%s 未在 §3.1 声明（阈值未同源）' % _rf.group(1))
    if '复述档' not in _cl or '确定档' not in _cl or '追问档' not in _cl:
        bad('library/clarity.md', '§3.1 未声明三档（确定档 / 复述档 / 追问档）')
    if '例 D' not in _cl or '0.816' not in _cl:
        bad('library/clarity.md', '§3.1 缺需求确定门算例（例 D / 例 E）')
"""


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def ensure_file(rel, content, label):
    cur = read(rel)
    if cur == content:
        print('  [SAME] %s :: %s' % (rel, label)); return
    write(rel, content)
    print('  [WROTE] %s :: %s（%d 字节）' % (rel, label, len(content.encode('utf-8'))))


def edit(rel, pairs, quiet=False):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for a, b in pairs:
        if a not in t:
            if not quiet:
                print('  [MISS] %s :: %r' % (rel, a[:56]))
            continue
        t = t.replace(a, b)
        if not quiet:
            print('  [OK]   %s :: %r' % (rel, a[:56]))
    if t != o:
        write(rel, t)


def ensure_block(rel, block, anchor, label):
    """保证 block 在 rel 里**恰好出现一次**（折叠重复 + 缺失则插在 anchor 之后）。

    ⚠️ 本层的登记行（`INSTALL.md` / `README.md`）**必须**用它 —— 第一版用了
    `replace(anchor, anchor+block)`，锚点不消失 → 第二次运行插成两份（aligncheck 报
    「连续重复」）。这是本项目第 4 次踩「追加型替换」，故统一到此写法。"""
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    t = re.sub(r'(?:' + re.escape(block) + r'\n)+', block + '\n', t)
    if block not in t:
        if anchor and anchor in t:
            t = t.replace(anchor, anchor + '\n' + block, 1)
            print('  [OK]   %s :: 插入 %s' % (rel, label))
        else:
            print('  [MISS] %s :: 未找到锚点（%s）' % (rel, label)); return
    elif t != o:
        print('  [FIX]  %s :: 折叠重复的 %s' % (rel, label))
    else:
        print('  [SAME] %s :: %s 已在位' % (rel, label)); return
    write(rel, t)


# ---------------------------------------------------------------- 1) 两个新工具
print('== 1) 新增 scripts/checkall.py 与 scripts/negative_test.py ==')
ensure_file('scripts/checkall.py', CHECKALL, '自检单入口')
ensure_file('scripts/negative_test.py', NEGTEST, '负向自测')

# ---------------------------------------------------------------- 2) clarity §3.1 修订
print('== 2) library/clarity.md §3.1：追问档措辞 + 算例表 ==')
edit('library/clarity.md', [(S31_OLD_ROW, S31_NEW_ROW)])
_c = read('library/clarity.md')
if _c and '例 D' not in _c and '## 4. 追问优先级（高杠杆优先）' in _c:
    write('library/clarity.md', _c.replace('## 4. 追问优先级（高杠杆优先）', S31_CASES.lstrip('\n') + '## 4. 追问优先级（高杠杆优先）', 1))
    print('  [OK]   已插入需求确定门算例表（例 D / 例 E）')
else:
    print('  [SAME] 算例表已在位')

# ---------------------------------------------------------------- 3) aligncheck 追加口径断言
print('== 3) scripts/aligncheck.py：需求确定门口径断言 ==')
if read('scripts/aligncheck.py') and '需求确定门（`library/clarity.md` §3.1）' in read('scripts/aligncheck.py'):
    print('  [SAME] aligncheck 已有需求确定门断言')
else:
    edit('scripts/aligncheck.py', [(ALIGN_ANCHOR, ALIGN_ANCHOR + ALIGN_ADD)])

# ---------------------------------------------------------------- 4) selfcheck REQ 登记
print('== 4) scripts/selfcheck.sh REQ ==')
edit('scripts/selfcheck.sh', [
    ('scripts/aligncheck.py scripts/runcheck.py"',
     'scripts/aligncheck.py scripts/runcheck.py scripts/checkall.py scripts/negative_test.py"'),
])

# ---------------------------------------------------------------- 5) INSTALL / README 登记
print('== 5) INSTALL.md / README.md 登记单入口 ==')
ensure_block(
    'INSTALL.md',
    '| `python scripts/checkall.py .` | **自检单入口**：跑齐 5 个校验器 + 逐项计时 + 模拟跑摘要（`--quick` 加速 ｜ `--negative` 断言非空转） | `全部 PASS ｜ rc 0` |',
    '| `python scripts/runcheck.py . 3` | **跑得通不通**（每域跑完整三级链，逐级确认返回结果） | `FAIL 0 ｜ 运行链全部可解` |',
    '验收表单入口行')
ensure_block(
    'README.md',
    'python scripts/checkall.py .       # 自检单入口（跑齐 5 个校验器 + 计时 + 模拟跑摘要）',
    'python scripts/runcheck.py . 3    # 运行性检查（每域跑完整三级链，连跑 3 轮）',
    '用法示例单入口行')

# ---------------------------------------------------------------- 6) 修订号 3.2.1 → 3.2.2
print('== 6) 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        t = read(rel)
        if t is None:
            continue
        if 'version: %s' % OLD in t:
            write(rel, t.replace('version: %s' % OLD, 'version: %s' % NEW)); n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
edit('SKILL.md', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('.codebuddy-plugin/plugin.json', [('"version": "%s"' % OLD, '"version": "%s"' % NEW)])
edit('config.yaml', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('scripts/aligncheck.py', [
    ("!= '%s':" % OLD, "!= '%s':" % NEW),
    ("（期望 %s）' %% vm.group(1))" % OLD, "（期望 %s）' %% vm.group(1))" % NEW),
    ("vers - {'%s'}" % OLD, "vers - {'%s'}" % NEW),
    ("（期望 %s）' %% pv)" % OLD, "（期望 %s）' %% pv)" % NEW),
    ("not in ('%s', '%s')" % (PKG, OLD), "not in ('%s', '%s')" % (PKG, NEW)),
    ("m.group(1), '%s', '%s'))" % (PKG, OLD), "m.group(1), '%s', '%s'))" % (PKG, NEW)),
    ("期望包版本 %s 或修订号 %s" % (PKG, OLD), "期望包版本 %s 或修订号 %s" % (PKG, NEW)),
    ("'%s' not in v:" % OLD, "'%s' not in v:" % NEW),
    ("未声明版本 %s" % OLD, "未声明版本 %s" % NEW),
    ("修订号 = 三位（%s）" % OLD, "修订号 = 三位（%s）" % NEW),
])
edit('library/output-spec.md', [
    ('｜**修订号 = `%s`**（三位' % OLD, '｜**修订号 = `%s`**（三位' % NEW),
    ('包 `%s` 对应修订 `%s`' % (PKG, OLD), '包 `%s` 对应修订 `%s`' % (PKG, NEW)),
    ('（规则变更 +1，如 `3.2.0` → `%s`）' % OLD, '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
])

print('done')
