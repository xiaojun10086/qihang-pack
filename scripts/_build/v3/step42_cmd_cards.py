# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 10 层 · 域入口卡升级】20 张 commands/qihang-*.md 的第 3 步从「首选/备选」升级为「全量库内择优（含路径）」
# 原名 gen_cmd_cards.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 收编时把路径分隔符直接写为 `/`（原版写反斜杠，靠 step43 事后归一）；step43 保留为幂等兜底
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""把 20 个域入口卡（commands/qihang-*.md）的第 3 步从「首选/备选」升级为「全量库内择优」。"""
import io, os, re, glob, collections, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

# 1) 从 _registry.md 解析 域ID -> [skill...]（表格第 4 列）
reg = io.open(os.path.join(ROOT, 'domains/_registry.md'), encoding='utf-8').read()
dom_skills = collections.OrderedDict()
for m in re.finditer(r'^\|\s*`([SFR]\d)`\s*\|[^|]*\|[^|]*\|\s*(.+?)\s*\|\s*$', reg, re.M):
    did, cell = m.group(1), m.group(2)
    names = re.findall(r'`([\w-]+)`', cell)
    dom_skills[did] = names

# 2) 域ID -> 域目录名
dirs = {}
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    mp = re.match(r'^([SFR]\d)-', d)
    if mp:
        dirs[mp.group(1)] = d

changed = []
for did, names in dom_skills.items():
    cf = os.path.join(ROOT, 'commands', 'qihang-%s.md' % did.lower())
    if not os.path.exists(cf):
        print('!! 缺入口卡', cf)
        continue
    t = io.open(cf, encoding='utf-8').read()
    old_first = re.search(r'首选 `([\w-]+)`', t)
    first = old_first.group(1) if old_first and old_first.group(1) in names else names[0]
    rest = [n for n in names if n != first]
    dd = dirs[did]
    n = len(names)
    others = ' / '.join('`%s`' % x for x in rest)
    new_block = (
        '3. **库内择优**：按**主体与任务**在本域 %d 个库内 skill 中择优 —— 首选 `%s`；其余 %s 按触发场景择用\n'
        '   路径：%s\n'
        % (n, first, others,
           '、'.join('`domains/%s/skills/local/%s/SKILL.md`' % (dd, x) for x in names))
    )
    t2, cnt = re.subn(r'^3\. \*\*库内[^\n]*\n(?:[ \t]+路径：[^\n]*\n)?',
                      lambda _m, _nb=new_block: _nb, t, count=1, flags=re.M)
    if cnt != 1:
        print('!! 未匹配第3步', did)
        continue
    io.open(cf, 'w', encoding='utf-8', newline='\n').write(t2)
    changed.append('%s(%d)' % (did, n))

print('入口卡更新：%d 张  %s' % (len(changed), ' '.join(changed)))
