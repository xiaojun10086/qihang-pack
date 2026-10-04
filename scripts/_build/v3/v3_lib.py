# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 1 层 · 公共库】渲染器 + 域事实解析（新 skill 的红线/DUT 从 _domain.md 运行时解析，不手抄）
# 原名 gen_lib.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 被 step21_expand.py 以 `import v3_lib as G` 引用
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""「启航」v3.1 扩库生成器 · 公共库（渲染器 + 域事实解析）。

设计原则：新 skill 的「红线」与「DUT 绑定点」**不手抄**，一律从所属域
`_domain.md` 运行时解析，保证与域文件逐字一致（aligncheck M / runcheck L3-7 硬约束）。
"""
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

def read(rel):
    with io.open(os.path.join(ROOT, rel), 'r', encoding='utf-8') as f:
        return f.read()

def write(rel, text):
    p = os.path.join(ROOT, rel)
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, 'w', encoding='utf-8', newline='') as f:
        f.write(text)

def _sec(text, head_re):
    m = re.search(head_re, text, re.M)
    if not m:
        return ''
    rest = text[m.end():]
    n = re.search(r'^##\s', rest, re.M)
    return rest[:n.start()] if n else rest

def domain_facts(ddir):
    """返回 dict：id/name/cls/red/pub/priv（红线与 DUT 从域文件逐字解析）。"""
    t = read('domains/%s/_domain.md' % ddir)
    first = t.splitlines()[0].strip()
    m = re.match(r'#\s*([A-Za-z]\d)\s*[·・]\s*(.+)$', first)
    did, name = m.group(1), m.group(2).strip()
    mc = re.search(r'所属大类\s*\*\*(.+?)\*\*', t)
    cls = mc.group(1).strip() if mc else ''
    red = [l.rstrip() for l in _sec(t, r'^##\s*⚠️\s*红线[^\n]*$').splitlines()
           if l.startswith('- ')]
    dut_sec = _sec(t, r'^##\s*DUT 绑定点[^\n]*$')
    pub, priv, mode = [], [], 'pub'
    for l in dut_sec.splitlines():
        s = l.strip()
        if '公开站' in s:
            mode = 'pub'
            continue
        if '私密站' in s or ('需登录' in s and '无需登录' not in s):
            mode = 'priv'
            continue
        if not s.startswith('- '):
            continue
        item = s[2:].strip()
        if item.startswith('无（') or item == '无':
            continue
        (priv if mode == 'priv' else pub).append(item)
    return {'id': did, 'name': name, 'cls': cls, 'red': red, 'pub': pub, 'priv': priv}

def local_skills(ddir):
    p = os.path.join(ROOT, 'domains', ddir, 'skills', 'local')
    return sorted(x for x in os.listdir(p) if os.path.isdir(os.path.join(p, x)))


def render_skill(ddir, sk):
    F = domain_facts(ddir)
    L = []
    A = L.append
    slug = sk['dir']
    A('---')
    A('name: qihang-%s' % slug)
    A('description: 「启航」%s %s域库内 skill：%s' % (F['id'], F['name'], sk['desc']))
    A('version: 3.0.0')
    A('license: MIT')
    A('---')
    A('')
    A('# %s' % sk['title'])
    A('')
    A('- **归属域**：`%s` %s（%s）' % (F['id'], F['name'], F['cls']))
    A('- **来源**：%s' % sk.get('source', '自建'))
    A('- **覆盖主体**：%s' % sk['subject'])
    A('- **定位**：%s' % sk['pos'])
    A('')
    A('## 前置（不可跳过）')
    A('')
    A('1. 1 级库已完成**需求明确**（6 槽位 + 澄清门；先过 §5 例外，关键槽 `O/T/D` 齐全且不歧义即放行）')
    A('2. 1 级库已完成**域审查**，确认命中本域')
    A('')
    A('## 边界')
    A('')
    A('- 覆盖：%s' % sk['cover'])
    A('- 不覆盖：%s' % sk['nocover'])
    A('')
    A('## 执行步骤')
    A('')
    for i, s in enumerate(sk['steps'], 1):
        A('%d. %s' % (i, s))
    A('')
    if sk.get('methods'):
        A('## 方法库 · 判定细则')
        A('')
        A(sk['methods'].rstrip())
        A('')
    A('## 可执行示例')
    A('')
    for k, ex in enumerate(sk['ex'], 1):
        A('**示例 %d（%s）**' % (k, ex['kind']))
        A('')
        A('**输入**')
        A('')
        A('> %s' % ex['in'])
        A('')
        A('**澄清判定**：%s' % ex['judge'])
        A('')
        A('**输出**')
        A('')
        A('```')
        A(ex['out'].rstrip())
        A('```')
        A('')
    A('## ⚠️ 红线（不得绕过）')
    A('')
    for r in F['red']:
        A(r)
    A('')
    A('## 输出')
    A('')
    A('按 `library/output-spec.md` 输出；≤6 限制的是字段标签数，不限制内容点；详细学习请求须覆盖范围并分层讲解。')
    A('交付前须过 `library/output-checklist.md` 的 7 项硬校验。')
    A('')
    A('## DUT 绑定点')
    A('')
    for u in F['pub']:
        A('- %s' % u)
    if F['priv']:
        A('')
        A('需登录（方案 A · 只读 · 须隔离 profile）：')
        for u in F['priv']:
            A('- %s' % u)
    A('')
    A('## 失败与降级')
    A('')
    fb = sk['fallback']
    A('本 skill 不满足 → 用同域库内 `%s` 降级承接（输出首行标 `[已降级: %s → %s]`）；'
      '`%s` 仍不满足 → 纯提示词模式并标注 `[已降级]`；缺口默认不记入学习档案，仅用户明确要求保存时按档案规则处理。'
      % (fb, slug, fb, fb))
    A('')
    A('## 与同域其他库内 skill 的分工')
    A('')
    A('| 场景 | 用哪个 |')
    A('|---|---|')
    for scen, tgt in sk['duty']:
        A('| %s | `%s` |' % (scen, tgt))
    A('')
    return '\n'.join(L)
