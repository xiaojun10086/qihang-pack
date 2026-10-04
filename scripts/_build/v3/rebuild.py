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
    ('step55_realrun_fixes.py',      '真实问题 5×5 轮归因修复（示例自洽/未核验事实/触发词/站点口径）+ 修订号 3.2.3→3.2.4'),
    ('step56_v325_release.py',       'v3.2.5 工程化迭代（隔离断言 + L3 共现规则 + 指标埋点 + 版本派生）+ 修订号 3.2.4→3.2.5'),
    ('step57_risk_fixes.py',         '风险自检修复（记忆不跟踪 · INSTALL 前置澄清 · .gitattributes 注释纠错）+ 修订号 3.2.5→3.2.6'),
    ('step58_readme_download.py',    'README 下载区（release 分支 ZIP / clone 指引）+ 修订号 3.2.6→3.2.7'),
    ('step59_link_integrity.py',     '链接可用性修复（URL 边界归一 + 仅HTTP标注 + 排查话术 + 断言与负向注入）+ 修订号 3.2.7→3.2.8'),
    ('step60_url_audit.py',          '外链核验订正（教务裸根 404 改可用入口 + 信息库 5 处事实订正 + §十一 三通道复核）+ 修订号 3.2.8→3.2.9'),
    ('step61_external_bridge.py',    '**外部 skill 桥接（大改）**：降级链两档→三档 · 12 平台入口表 · 五步自检器 extskill.py · 20 域「外部承接」· 92 skill 降级段改写 · 包版本 3.2→3.3 / 修订号 3.2.9→3.3.0'),
    ('step62_source_expand.py',      '来源扩展 + 命中规则收紧：平台 12→20 · 每域只查指定的 2–3 个平台（未命中即按「无 skill 流程」回落）· §4 第 4 项扩为「脚本与指令风险」· extskill 补 3 组断言 · 负向注入第 9 类 · 修订号 3.3.0→3.3.1'),
    ('step63_release_guard.py',      '**交付分支护栏**：git pre-commit 钩子（提交时拦截不随包路径，分支感知）+ selfcheck [11]（断言 release 树 == main 交付集）+ 安装脚本 · 修订号 3.3.1→3.3.2'),
    ('step65_trigger_gate.py',       '**触发门收紧 + 锁定与降级强制**：config.yaml 立 trigger 段（三条件 / 标记词 / 不接管 / 锁定 / 四级 ladder / 自生成前置）+ SKILL.md「触发门与接管边界」+ 三处规则文件「档序强制」+ 入口卡第 0 步并修编号与旧口径 + selfcheck [8d] + 负向第 11 类 · 修订号 3.3.3→3.3.4'),
    ('step66_domain_router.py',      '**域路由两级匹配**：registry 快筛后检查各域权威触发词，含高频 DUT 路由断言 · 修订号 3.3.4→3.3.5'),
    ('step67_gate_align.py',         '**域触发门同源 + 学习内容详度**：课程级触发词同步至域与门；教学/笔记输出完整性优先、分层展开、来源可追溯并标注分轮边界 · 修订号 3.3.7→3.3.8'),
    ('step68_remove_identity.py',    '**移除强制自我身份声明**：删除配置、文档和安装说明中的人格/改称锁定；将自检改为防回归断言；修订号 3.3.8→3.3.9'),
]

# ── 分支守卫（2026-10-03 事故驱动）──────────────────────────────────────────────
# 实测踩到：仓库被（并发会话）切到 `release` 分支后，生成链**照常在 release 的工作树上跑**，
#   把本应只属于 main 的生成器文件写进了交付树。release 不含 scripts/_build，
#   一旦在它上面跑链 / 提交，污染会直接进公开交付分支。
# → **生成链只允许在 main（或非 release 分支）上跑**；确需在别的分支跑时用 QIHANG_ALLOW_BRANCH=1。
if os.path.isdir(os.path.join(ROOT, '.git')):
    import subprocess as _sp
    _br = _sp.run(['git', 'symbolic-ref', '--quiet', '--short', 'HEAD'], cwd=ROOT,
                  stdout=_sp.PIPE, stderr=_sp.DEVNULL).stdout.decode('utf-8', 'replace').strip()
    if _br == 'release' and os.environ.get('QIHANG_ALLOW_BRANCH') != '1':
        print('✖ 拒绝执行：当前分支是 `release`（交付分支）。')
        print('  生成链只能在 `main` 上跑 —— 在 release 上跑会把开发物写进交付树。')
        print('  先 `git checkout main`；确需如此请设 QIHANG_ALLOW_BRANCH=1。')
        raise SystemExit(2)
    if _br:
        print('分支：%s（生成链要求非 release）' % _br)

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
