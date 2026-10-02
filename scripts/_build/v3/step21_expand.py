# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 5 层 · 扩库执行器】写新 SKILL.md（已存在即跳过）+ 更新每个 _domain.md 的库内清单与执行顺序第 3 步 + 更新 _registry.md
# 原名 gen_run.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 库内 skill 红线/DUT 由 v3_lib 从 _domain.md 逐字解析，故新 skill 与域文件天然一致
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""「启航」v3.1 扩库 · 执行器：写 40 个新 SKILL.md + 更新 _domain.md 与 _registry.md。"""
import os, io, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v3_lib as G
from step20_content_s import S
from step20_content_f import F
from step20_content_r import R

NEW = {}
NEW.update(S); NEW.update(F); NEW.update(R)

ROOT = G.ROOT
def rd(p): return G.read(p)
def wr(p, t): G.write(p, t)

# ---------- 1. 写新 SKILL.md ----------
created = []
for ddir, sks in NEW.items():
    for sk in sks:
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (ddir, sk['dir'])
        p = os.path.join(ROOT, rel)
        if os.path.exists(p):
            print('  [SKIP 已存在] %s' % rel); continue
        wr(rel, G.render_skill(ddir, sk))
        created.append(rel)
print('新写 SKILL.md：%d 个' % len(created))

# ---------- 2. 更新每个 _domain.md ----------
def dom_id_dir_map():
    m = {}
    for d in sorted(x for x in os.listdir(os.path.join(ROOT, 'domains'))
                    if os.path.isdir(os.path.join(ROOT, 'domains', x))):
        did = d.split('-')[0]
        m[did] = d
    return m
IDDIR = dom_id_dir_map()

for ddir, sks in NEW.items():
    rel = 'domains/%s/_domain.md' % ddir
    t = rd(rel)
    # 2a. 库内 skill 清单：在「## DUT 绑定点」前插入新条目
    block = ''
    for sk in sks:
        block += '- **`%s`** — %s（%s）\n  %s\n\n' % (
            sk['dir'], sk['title'], sk.get('source', '自建'), sk['pos'])
    anchor = '\n## DUT 绑定点'
    if anchor not in t:
        print('  [WARN] %s 缺 DUT 锚点，未插库内清单' % rel)
    else:
        # 避免重复插入
        if ('- **`%s`**' % sks[0]['dir']) not in t:
            t = t.replace(anchor, '\n' + block.rstrip('\n') + '\n' + anchor, 1)
    # 2b. 执行顺序第 3 步：列出全部库内 skill
    m = re.search(r'^3\. 用\*\*库内 skill\*\*.*$', t, re.M)
    if m:
        old = re.findall(r'`([\w-]+)`', m.group(0))
        alldirs = G.local_skills(ddir)
        names = old + [x for x in alldirs if x not in old]
        names = [x for x in names if x in alldirs]  # 只保留真实存在的
        line = '3. 用**库内 skill**（库内 %d 个：%s；按需求择一）执行' % (
            len(names), ' · '.join('`%s`' % n for n in names))
        t = t[:m.start()] + line + t[m.end():]
    else:
        print('  [WARN] %s 未找到执行顺序第 3 步' % rel)
    wr(rel, t)
print('已更新 _domain.md：%d 个' % len(NEW))

# ---------- 3. 更新 _registry.md ----------
reg_rel = 'domains/_registry.md'
reg = rd(reg_rel)
# 3a. 头行
reg = re.sub(r'> 共 \*\*20 个域 / \d+ 个库内 skill（每域 [\d–]+ 个，其中 12 个改造自 MIT 外部最优解并已 DUT 特化）\*\*',
             '> 共 **20 个域 / 92 个库内 skill（每域 4–5 个，其中 12 个改造自 MIT 外部最优解并已 DUT 特化）**', reg)
# 3b. 每行第 4 列 == 实体
out_lines = []
for line in reg.split('\n'):
    m = re.match(r'^\|\s*`([A-Za-z]\d)`\s*\|([^|]*)\|([^|]*)\|\s*([^|]+?)\s*\|\s*$', line)
    if m and m.group(1) in IDDIR:
        did = m.group(1)
        ddir = IDDIR[did]
        real = G.local_skills(ddir)
        cell = ' · '.join('`%s`' % x for x in real)
        line = '| `%s` |%s|%s| %s |' % (did, m.group(2), m.group(3), cell)
    out_lines.append(line)
reg = '\n'.join(out_lines)
# 3c. 自查表 skill 覆盖行
reg = re.sub(r'\| 库内 skill 覆盖 \| \*\*\d+ 个（自建 \d+ \+ 外部改造 12，运行时零外部依赖）\*\* \|',
             '| 库内 skill 覆盖 | **92 个（自建 80 + 外部改造 12，运行时零外部依赖）** |', reg)
wr(reg_rel, reg)
print('已更新 _registry.md')
print('完成')
