# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 发布侧 · 两树同步】源仓库 → 交付副本 逐字节比对与同步（排除 _build/.git/.learnbuddy；过程文档由 .gitignore 派生）
# 原名 sync_release.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 与 make_release.py 分工：make_release 是正式导出（git 真相源）；本脚本是开发期两树归并
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""dev(源仓库) → release(交付副本) 逐字节比对与同步。
- 排除 .git / _build / .learnbuddy / __pycache__ / .codebuddy-plugin
- 比对按 \r 归一化后的字节；不一致项用 shutil.copy2 逐个覆盖。
用法: python sync_release.py [--apply]
"""
import os, io, sys, shutil

# 用法：python sync_release.py [源仓库] [交付副本] [--apply]
_ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
DEV = os.path.abspath(_ARG[0] if _ARG else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
REL = os.path.abspath(_ARG[1] if len(_ARG) > 1 else DEV + '-release')
EX = {'.git', '_build', '.learnbuddy', '__pycache__', '.codebuddy-plugin', '.idea'}
EXF = {'.gitattributes', '.gitignore'}
APPLY = '--apply' in sys.argv

# .gitignore 明列「未随包分发」的过程文档（评审/审计/验收/需求书）不得进入交付副本
_ign = io.open(os.path.join(DEV, '.gitignore'), encoding='utf-8').read()
_PROCDOC = {os.path.basename(l.strip()) for l in _ign.splitlines()
            if l.strip().startswith('references/') and l.strip().endswith('.md')}


def walk(root):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EX]
        for f in fns:
            if f in EXF or f in _PROCDOC:
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace(os.sep, '/')] = p
    return out


def norm(p):
    with open(p, 'rb') as f:
        return f.read().replace(b'\r\n', b'\n')


a, b = walk(DEV), walk(REL)
only_dev = sorted(set(a) - set(b))
only_rel = sorted(set(b) - set(a))
diff = sorted(k for k in set(a) & set(b) if norm(a[k]) != norm(b[k]))

print('dev 文件数 %d ｜ release 文件数 %d' % (len(a), len(b)))
print('仅 dev 有 %d: %s' % (len(only_dev), only_dev[:30]))
print('仅 rel 有 %d: %s' % (len(only_rel), only_rel[:30]))
print('内容不一致 %d: %s' % (len(diff), diff[:40]))

if APPLY:
    n = 0
    for k in [x for x in only_dev + diff if x in a]:
        dst = os.path.join(REL, k.replace('/', os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(a[k], dst)
        n += 1
    print('已同步 dev → release：%d 个文件' % n)

    # 复核
    a2, b2 = walk(DEV), walk(REL)
    d2 = sorted(k for k in set(a2) & set(b2) if norm(a2[k]) != norm(b2[k]))
    print('复核：仅 dev 有 %d ｜ 仅 rel 有 %d ｜ 内容不一致 %d'
          % (len(set(a2) - set(b2)), len(set(b2) - set(a2)), len(d2)))
    print('不一致残留：', d2[:20])
