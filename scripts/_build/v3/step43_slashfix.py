# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 11 层 · 路径归一兜底】把入口卡中的 `domains\` 归一为 `domains/`，使交叉引用能被 selfcheck/aligncheck 实际校验
# 原名 _slashfix.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""入口卡路径反斜杠归一为 '/'（使交叉引用可被 selfcheck/aligncheck 实际校验）。"""
import io, glob, os, sys

# 收编修正：原版 glob 依赖 CWD，现改为按 ROOT 定位
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

n = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'commands', 'qihang-*.md'))):
    t = io.open(f, encoding='utf-8').read()
    t2 = t.replace('domains\\', 'domains/')
    if t2 != t:
        io.open(f, 'w', encoding='utf-8', newline='\n').write(t2)
        n += 1
print('反斜杠归一：%d 张' % n)
