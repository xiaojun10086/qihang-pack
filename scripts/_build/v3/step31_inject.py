# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 7 层 · 优化注入器】幂等注入「方法库 · 判定细则」与「示例 2」；并清理输出示例中的自指涉「（库内 skill）」
# 原名 gen_opt_run.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等判据：skill 已含 `## 方法库` 或 `示例 2` 即跳过
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""Phase C 注入：为既有 skill 插入「方法库 · 判定细则」与「示例 2（边界 / 失败例）」。
幂等：已含 `## 方法库` 或 `示例 2` 的 skill 跳过。
"""
import os, sys, io, re, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

def load(mod):
    spec = importlib.util.spec_from_file_location(mod, os.path.join(HERE, mod + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

OPT = {}
for mod, name in (('step30_opt_s', 'OPT_S'), ('step30_opt_f', 'OPT_F'), ('step30_opt_r', 'OPT_R')):
    OPT.update(getattr(load(mod), name))

def rd(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()

def wr(p, t):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(t)

FENCE = '```'

def block_methods(methods):
    return '## 方法库 · 判定细则\n\n' + methods + '\n\n'

def block_ex2(inp, judge, out):
    return ('**示例 2（边界 / 失败例 —— 不该命中的情形）**\n\n'
            '**输入**\n\n> ' + inp + '\n\n'
            '**澄清判定**：' + judge + '\n\n'
            '**输出**\n\n' + FENCE + '\n' + out + '\n' + FENCE + '\n\n')

done, skip, miss = [], [], []
for dirname, cfg in sorted(OPT.items()):
    hits = []
    for dp, dns, fns in os.walk(os.path.join(ROOT, 'domains')):
        if 'SKILL.md' in fns and os.path.basename(dp) == dirname:
            hits.append(os.path.join(dp, 'SKILL.md'))
    if len(hits) != 1:
        miss.append((dirname, len(hits)))
        continue
    path = hits[0]
    t = rd(path)
    if '## 方法库' in t or '示例 2' in t:
        skip.append(dirname)
        continue
    if '## 可执行示例' not in t or '## ⚠️ 红线' not in t:
        miss.append((dirname, 'sections'))
        continue

    # 1) 方法库：插到「## 可执行示例」之前
    assert t.count('\n## 可执行示例\n') == 1, (dirname, t.count('\n## 可执行示例\n'))
    t = t.replace('\n## 可执行示例\n',
                  '\n' + block_methods(cfg['methods']) + '## 可执行示例\n', 1)

    # 2) 首个示例改名为「示例 1（正常命中）」
    t = t.replace('## 可执行示例\n\n**输入**',
                  '## 可执行示例\n\n**示例 1（正常命中）**\n\n**输入**', 1)

    # 3) 示例 2 插到「## ⚠️ 红线」之前
    e = cfg['ex2']
    assert t.count('\n## ⚠️ 红线') == 1, (dirname, t.count('\n## ⚠️ 红线'))
    t = t.replace('\n## ⚠️ 红线',
                  '\n' + block_ex2(e['in'], e['judge'], e['out']) + '## ⚠️ 红线', 1)

    wr(path, t)
    done.append(dirname)

# 4) 清理输出示例中的自指涉「（库内 skill）」
REF_FIX = 0
for dp, dns, fns in os.walk(os.path.join(ROOT, 'domains')):
    if 'SKILL.md' not in fns:
        continue
    p = os.path.join(dp, 'SKILL.md')
    t = rd(p)
    if '（库内 skill）' in t:
        t2 = t.replace('；分步讲解流程（库内 skill）', '；本 skill 的卡点定位 → 提示 → 解法 → 同类题四步流程')
        t2 = t2.replace('（库内 skill）', '')
        wr(p, t2)
        REF_FIX += t.count('（库内 skill）')
        print('自指涉修正：', p.replace('\\', '/').split('domains/')[-1])

print('注入完成：%d 个' % len(done))
print('跳过（已优化）：%d 个  %s' % (len(skip), ','.join(skip)))
print('未命中：%d  %s' % (len(miss), miss))
print('自指涉修正共 %d 处' % REF_FIX)
