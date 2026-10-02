# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 阴性测试 · 注入缺陷】故意注入 4 类缺陷（红线漂移 / 降级目标不存在 / 输出缺【结论】【下一步】），确认 checker 会 FAIL，随后还原
# 原名 negtest.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""阴性测试：故意注入 4 类缺陷，确认 checker 会 FAIL，然后还原。
零临时文件依赖；还原用 shutil.copy2 逐文件写回（不用 rm）。
"""
import io, os, shutil, subprocess, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
PY = sys.executable
BAK = os.path.join(os.environ['TEMP'], 'qihang_v3_negbak')

def rd(p):
    return io.open(p, 'r', encoding='utf-8').read()

def wr(p, t):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(t)

def run(cmd):
    """字节模式：Windows 下 text=True 会按 GBK 解码 UTF-8 输出而崩。"""
    r = subprocess.run(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.stdout.decode('utf-8', 'replace')

os.makedirs(BAK, exist_ok=True)

CASES = []
# 1) 红线漂移：改一条本地 skill 的红线（应被 aligncheck M / runcheck L3-7 抓）
p1 = os.path.join(ROOT, 'domains/S1-course-qa/skills/local/explain-stepwise/SKILL.md')
# 2) 降级目标指向不存在的 skill（应被 runcheck L3-8 抓）
p2 = os.path.join(ROOT, 'domains/F1-campus-affairs/skills/local/campus-desk/SKILL.md')
# 3) 示例输出缺【结论】（应被 aligncheck O6 / runcheck L3-5 抓）
p3 = os.path.join(ROOT, 'domains/F2-focus/skills/local/deep-work/SKILL.md')

for p in (p1, p2, p3):
    shutil.copy2(p, os.path.join(BAK, os.path.basename(os.path.dirname(p)) + '_SKILL.md'))
    CASES.append((p, rd(p)))

def restore():
    for p, orig in CASES:
        wr(p, orig)

# --- 注入 ---
t = rd(p1); t = t.replace('- **不代做**：只给讲解与同类题',
                          '- **不代做**：只给讲解（本行已人为篡改，用于阴性测试）', 1)
wr(p1, t)

t = rd(p2); t = t.replace('用同域库内 `campus-proof-guide` 降级承接',
                          '用同域库内 `no-such-skill-xyz` 降级承接', 1)
t = t.replace('`campus-desk` → `campus-proof-guide`',
              '`campus-desk` → `no-such-skill-xyz`')
wr(p2, t)

t = rd(p3)
t = t.replace('【结论】', '【要旨】', 1)          # 破坏「结论前置」
t = t.replace('【下一步】', '【后续】', 1)        # 破坏【下一步】
wr(p3, t)

print('== 注入完成，运行 checker ==')
o = run([PY, 'scripts/aligncheck.py'])
print('[aligncheck] FAIL 行:')
for l in o.splitlines():
    if 'FAIL' in l or '✗' in l or '重大' in l:
        print('   ', l[:120])
print('   tail:', o.strip().splitlines()[-1] if o.strip() else '(空)')

o2 = run([PY, 'scripts/runcheck.py'])
print('[runcheck] 命中行:')
for l in o2.splitlines():
    if 'FAIL' in l or '错' in l or '降级' in l or '结论' in l or '下一步' in l:
        print('   ', l[:140])
print('   tail:', o2.strip().splitlines()[-1] if o2.strip() else '(空)')

# --- 还原 ---
restore()
print('== 已还原 ==')
o3 = run([PY, 'scripts/aligncheck.py'])
o4 = run([PY, 'scripts/runcheck.py'])
print('还原后 aligncheck:', o3.strip().splitlines()[-1])
print('还原后 runcheck :', o4.strip().splitlines()[-1])
