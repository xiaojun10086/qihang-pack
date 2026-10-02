# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 阴性测试 · 兜底文件缺失】把 library/general-fallback.md 移走后，regress.sh 的 [5] 段应出现 FAIL；随后还原
# 原名 negtest_fallback.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""阴性测试（字节模式）：移走 general-fallback.md 后，[5] 段应出现 FAIL。"""
import os, shutil, subprocess, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'library/general-fallback.md')
TMP = os.path.join(os.environ['TEMP'], 'qihang_v3_hold_fallback.md')


def _bash():
    """Windows 上 `bash` 可能解析到 WSL（System32\bash.exe，未安装即报错）。
    优先 Git Bash；找不到就回退到名字，由调用者改用 Git Bash 运行。"""
    for c in (r'C:/Program Files/Git/bin/bash.exe', r'C:/Program Files (x86)/Git/bin/bash.exe',
              'bash'):
        p = c if os.path.exists(c) else shutil.which(c)
        if p and 'system32' not in str(p).lower():
            return p
    return 'bash'


def run():
    r = subprocess.run([_bash(), 'scripts/regress.sh'], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return r.stdout.decode('utf-8', 'replace')


shutil.move(SRC, TMP)
try:
    out = run()
    sec = out.split('[5]')[-1]
    print('---- 移走后 [5] 段 ----')
    print(sec[:800])
finally:
    shutil.move(TMP, SRC)
    print('---- 还原后 ----')
    print(run().strip().splitlines()[-1])
