# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 发布侧 · 两树终检】源仓库 ↔ 交付副本 逐字节比对（排除 .gitignore 明列「未随包分发」的过程文档）
# 原名 final_align.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""终检：源仓库 ↔ 交付副本 逐字节比对（排除 .gitignore 明列「未随包分发」的过程文档）。"""
import os, io, re, sys

# 用法：python verify.py [源仓库] [交付副本]
_ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
DEV = os.path.abspath(_ARG[0] if _ARG else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
REL = os.path.abspath(_ARG[1] if len(_ARG) > 1 else DEV + '-release')
EX = {'.git', '_build', '.learnbuddy', '__pycache__', '.idea'}
# 2026-10-03（第二轮）：原先 EX 还含 '.codebuddy-plugin' —— 那是产品文件所在目录
# （`.codebuddy-plugin/plugin.json` 是必备文件，也是版本号落点）。终检若把它排除，
# 「两树完全一致」就是**漏了 1 个文件的假一致**（实测：副本曾停在 3.0.0，而终检报「完全一致」）。

ign = io.open(os.path.join(DEV, '.gitignore'), encoding='utf-8').read()
proc = {l.strip() for l in ign.splitlines() if re.match(r'^references/.*\.md$', l.strip())}
proc_names = {os.path.basename(x) for x in proc}


def walk(root):
    out = {}
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in EX]
        for f in fns:
            if f in proc_names:
                continue
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root).replace(os.sep, '/')] = p
    return out


def norm(p):
    with open(p, 'rb') as f:
        return f.read().replace(b'\r\n', b'\n')


a, b = walk(DEV), walk(REL)
od, orr = sorted(set(a) - set(b)), sorted(set(b) - set(a))
diff = sorted(k for k in set(a) & set(b) if norm(a[k]) != norm(b[k]))
print('源仓库 %d 个文件 ｜ 交付副本 %d 个文件（均已排除 %d 个过程文档）'
      % (len(a), len(b), len(proc_names)))
print('仅源仓库有：%d  %s' % (len(od), od[:10]))
print('仅交付副本有：%d  %s' % (len(orr), orr[:10]))
print('内容不一致：%d  %s' % (len(diff), diff[:10]))
print('判定：%s' % ('✅ 两树完全一致（交付树 = 源仓库 − 过程文档）'
                  if not od and not orr and not diff else '❌ 存在漂移'))
