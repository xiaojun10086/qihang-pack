#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」v3.0.0 生成链 · 单入口。

按层序跑齐同目录下的各层脚本。各层自身幂等：在**已达 v3.0.0** 的树上重跑应零变更。

用法：
    python scripts/_build/v3/rebuild.py [仓库根] [--dry] [--only step42]

判据（与 scripts/_build/README.md 一致）：
    · 本链在 v3.0.0 树上重跑 = 零变更；
    · 全链连跑两遍，逐文件哈希完全一致；
    · 产物通过 selfcheck.sh / audit.sh / regress.sh / aligncheck.py / runcheck.py。

说明：交付副本（两树归并）由 release/ 下三个脚本负责，不在本入口内 —— 见 README.md。
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..', '..', '..'))
DRY = '--dry' in sys.argv
ONLY = None
if '--only' in sys.argv:
    ONLY = sys.argv[sys.argv.index('--only') + 1]

# 层序（顺序即依赖：step21 依赖 step20_*，step31 依赖 step30_*）
LAYERS = [
    ('step10_de_external.py',        '去库外化（external.md / 库外文档 / 降级段 / 步骤序号）'),
    ('step11_ext_register.py',       '改造（MIT 派生）skill 登记进 _domain.md'),
    ('step21_expand.py',             '扩库执行器（写新 SKILL.md + _domain.md + _registry.md）'),
    ('step31_inject.py',             '优化基线注入（方法库 · 判定细则 + 示例 2）'),
    ('step40_dut_deep.py',           '改造 skill 的 DUT 特化加深'),
    ('step41_docs_counts.py',        '文档计数级联（52→92 / 2–3→4–5 / 自建 40→80）'),
    ('step42_cmd_cards.py',          '域入口卡第 3 步升级为「全量库内择优」'),
    ('step43_slashfix.py',           '入口卡路径反斜杠归一（幂等兜底）'),
    ('step44_checker_thresholds.py', '校验器阈值同步（52→92）'),
    ('step50_self_evolution.py',     '习惯自迭代机制（library 规则文件 + 20 域接线 + [8] 段断言）'),
    ('step51_version_bump.py',       '版本号与计数级联（包版本 3.0.0→3.2.0 / library 9→10）'),
    ('step52_requirement_confirm.py', '需求确定门（clarity §3.1 · 理解准确率 ≥95%）+ 修订号 3.2.0→3.2.1'),
    ('step53_checkup_flow.py',       '自检查流程加固（单入口 checkall + 负向自测）+ 需求确定门算例 + 修订号 3.2.1→3.2.2'),
    ('step54_blindrun_fixes.py',     '60 子代理盲跑归因修复（假设口径/先问后述/红线短路/追问变体/域红线漏洞）+ 修订号 3.2.2→3.2.3'),
]

print('v3.0.0 生成链 · 目标树：%s' % ROOT)
print('（各层幂等；在已达 v3.0.0 的树上重跑应零变更）')
if DRY:
    print('--dry：只列出将要执行的层，不实际运行')
print('=' * 68)

env = dict(os.environ)
env['PYTHONIOENCODING'] = 'utf-8'
rc_all = 0
for name, what in LAYERS:
    if ONLY and ONLY not in name:
        continue
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        print('!! 缺层：%s' % p)
        rc_all = 1
        continue
    if DRY:
        print('  [将执行] %-30s %s' % (name, what))
        continue
    print('-- %s  ·  %s' % (name, what))
    r = subprocess.run([sys.executable, p, ROOT], cwd=ROOT,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    out = r.stdout.decode('utf-8', 'replace')
    for ln in out.rstrip().splitlines():
        print('   %s' % ln)
    if r.returncode != 0:
        print('   !! rc=%d' % r.returncode)
        rc_all = r.returncode
        break

print('=' * 68)
print('链执行完成 rc=%d' % rc_all)
sys.exit(rc_all)
