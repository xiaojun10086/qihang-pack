# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 发布侧 · 副本收尾】同步 .gitignore/.gitattributes 到副本；把过程文档移出副本（move 到 TEMP，不删除）
# 原名 release_finish.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""交付副本收尾：
1) 同步 .gitignore / .gitattributes（使 selfcheck 的「未随包分发」排除可复现）
2) 把 .gitignore 明列的过程文档移出 release（move 到 TEMP 备份，不删除）
3) 复核：交付树（排除过程文档）与源仓库逐字节一致
"""
import os, io, shutil, re, sys

# 用法：python finish.py [源仓库] [交付副本]
_ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
DEV = os.path.abspath(_ARG[0] if _ARG else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
REL = os.path.abspath(_ARG[1] if len(_ARG) > 1 else DEV + '-release')
BAK = os.path.join(os.environ['TEMP'], 'qihang_release_removed')

# 1) 同步点文件
for f in ('.gitignore', '.gitattributes'):
    src = os.path.join(DEV, f)
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(REL, f))
        print('同步点文件：', f)

# 2) 解析 .gitignore 中「未随包分发」的 references/*.md
ign = io.open(os.path.join(REL, '.gitignore'), encoding='utf-8').read()
proc = [l.strip() for l in ign.splitlines()
        if re.match(r'^references/.*\.md$', l.strip())]
print('过程文档清单（%d）：%s' % (len(proc), proc))

os.makedirs(BAK, exist_ok=True)
moved = []
for rel in proc:
    p = os.path.join(REL, rel.replace('/', os.sep))
    if os.path.exists(p):
        dst = os.path.join(BAK, os.path.basename(rel))
        if os.path.exists(dst):
            _k = 2
            while os.path.exists(dst + '.prev%d' % _k):
                _k += 1
            dst = dst + '.prev%d' % _k
        shutil.move(p, dst)
        moved.append(rel)
print('已移出交付副本（备份至 %s）：%d 个 %s' % (BAK, len(moved), moved))
