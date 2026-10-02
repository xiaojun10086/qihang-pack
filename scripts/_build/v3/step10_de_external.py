# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 2 层 · 去库外化】删 19 个 external.md + 两份库外文档；38 个库内 skill 降级段改写；_domain.md 与 commands 步骤序号收敛
# 原名 qihang_v3_step1.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 原版 ROOT 指向交付副本；收编后统一由参数指定
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
import os, re, shutil, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

# 备份改为显式开关（本层幂等；需要留档时加 --backup）
if '--backup' in sys.argv:
    BAK = os.path.join(os.environ['TEMP'], 'qihang_v3_backup')
    if not os.path.exists(BAK):
        shutil.copytree(ROOT, BAK, ignore=shutil.ignore_patterns('.learnbuddy', '.git', '.idea', '_build'))
        print('backup ->', BAK)

TRASH = os.path.join(os.environ['TEMP'], 'qihang_v3_removed')
os.makedirs(TRASH, exist_ok=True)

def trash(rel):
    """幂等：文件不存在或已退役过 → 静默跳过（原版直接 shutil.move 会抛异常）。"""
    src = os.path.join(ROOT, rel.replace('/', os.sep))
    if not os.path.exists(src):
        return False
    dst = os.path.join(TRASH, rel.replace('/', '__'))
    if os.path.exists(dst):
        return False
    shutil.move(src, dst)
    print("removed:", rel)
    return True

# ---------- 1. 删除 19 个 external.md + 2 个外部来源文档 ----------
for dirpath, dirnames, names in os.walk(os.path.join(ROOT, 'domains')):
    for n in names:
        if n == 'external.md':
            rel = os.path.relpath(os.path.join(dirpath, n), ROOT).replace(os.sep, '/')
            trash(rel)
trash('references/skill-matrix-v3.md')
trash('references/skill-sources.md')

def repl(path, fn):
    p = os.path.join(ROOT, path)
    t = open(p, encoding='utf-8', newline='').read()
    t2 = fn(t)
    if t != t2:
        open(p, 'w', encoding='utf-8', newline='').write(t2)
        return True
    return False

# ---------- 2. 38 个库内 SKILL.md:失败与降级段改写 ----------
OLD_FAIL = '库内执行不满足 → 读上一级 `../../external.md` 走库外安装；仍失败 → 纯提示词模式并标注 `[已降级]`。'
NEW_FAIL = '本 skill 不满足 → 用同域另一库内 skill 降级承接（输出首行标 `[已降级: 本 → 备]`）；仍不满足 → 纯提示词模式并标注 `[已降级]`，并在学习档案记「缺口」（见 `library/memory.md`）。'

n_sk = 0
for dp, dn, fn_ in os.walk(os.path.join(ROOT, 'domains')):
    for n in fn_:
        if n == 'SKILL.md' and 'skills' + os.sep + 'local' in dp:
            p = os.path.join(dp, n)
            t = open(p, encoding='utf-8', newline='').read()
            if OLD_FAIL in t:
                open(p, 'w', encoding='utf-8', newline='').write(t.replace(OLD_FAIL, NEW_FAIL))
                n_sk += 1
print("SKILL.md 降级段改写:", n_sk)

# ---------- 3. 19 个 _domain.md:删步骤 4(库外),步骤 5 → 4 ----------
n_dom = 0
for dp, dn, fn_ in os.walk(os.path.join(ROOT, 'domains')):
    if os.path.basename(dp).startswith(('S', 'F', 'R')) and '_domain.md' in fn_:
        p = os.path.join(dp, '_domain.md')
        t = open(p, encoding='utf-8', newline='').read()
        t2 = re.sub(r'^4\. 库内不满足 → 读 `skills/external\.md` 走库外安装\n', '', t, flags=re.M)
        t2 = re.sub(r'^5\. ', '4. ', t2, count=1, flags=re.M)
        if t2 != t:
            open(p, 'w', encoding='utf-8', newline='').write(t2)
            n_dom += 1
print("_domain.md 步骤改写:", n_dom)

# ---------- 4. 19 个域 commands:删步骤 4(库外),5→4、6→5 ----------
n_cmd = 0
for n in sorted(os.listdir(os.path.join(ROOT, 'commands'))):
    if not re.match(r'qihang-[sfr]\d+\.md$', n):
        continue
    p = os.path.join(ROOT, 'commands', n)
    t = open(p, encoding='utf-8', newline='').read()
    t2 = re.sub(r'^4\. \*\*库外兜底\*\*：仅当库内不满足，才读 `domains/[^`]+/skills/external\.md` 走安装（LearnBuddy 用 `find-skills`）。\n', '', t, flags=re.M)
    t2 = re.sub(r'^5\. \*\*输出与归档\*\*', '4. **输出与归档**', t2, count=1, flags=re.M)
    t2 = re.sub(r'^6\. \*\*DUT 绑定点\*\*', '5. **DUT 绑定点**', t2, count=1, flags=re.M)
    if t2 != t:
        open(p, 'w', encoding='utf-8', newline='').write(t2)
        n_cmd += 1
print("commands 步骤改写:", n_cmd)

# ---------- 5. commands/qihang.md:删步骤 5(库外),6 → 5 ----------
def fix_main(t):
    t = re.sub(r'^5\. \*\*库外兜底\*\*：仅当库内不满足，才读 `skills/external\.md` 走安装。\n', '', t, flags=re.M)
    t = re.sub(r'^6\. \*\*输出与归档\*\*', '5. **输出与归档**', t, count=1, flags=re.M)
    return t
print("qihang.md:", repl('commands/qihang.md', fix_main))

# ---------- 6. 验证:项目内不再有 external 引用(脚本除外) ----------
# 收编修正：上一版把「未随包分发」的过程文档（评审/审计/验收/需求书）也算成残留 ——
# 那些文档本就在描述「去库外化」这件事，含 external 属正常。此处按 .gitignore 排除。
print("--- 残留检查 ---")
_PROCDOC = set()
_gi = os.path.join(ROOT, '.gitignore')
if os.path.exists(_gi):
    for _l in open(_gi, encoding='utf-8').read().splitlines():
        _l = _l.strip()
        if _l.startswith('references/') and _l.endswith('.md'):
            _PROCDOC.add(os.path.basename(_l))
for dp, dn, fn_ in os.walk(ROOT):
    dn[:] = [d for d in dn if d not in ('.learnbuddy', '.git', '.idea', 'scripts')]
    for n in fn_:
        if n.endswith(('.md', '.yaml', '.json')) and n not in _PROCDOC:
            p = os.path.join(dp, n)
            t = open(p, encoding='utf-8', errors='replace').read()
            if 'external' in t.lower():
                print("  残留:", os.path.relpath(p, ROOT).replace(os.sep, '/'))
print("  （排除 %d 份未随包分发的过程文档）" % len(_PROCDOC))
