#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部 skill 桥接 · 静态自检器（第 6 个校验器）。

它把 `library/external-bridge.md` 的规则变成**可执行的断言**，覆盖两头：
  一、**接线完整性**：1 级规则在位 → 2 级每域有「外部承接」→ 3 级每个 skill 的降级段是三档。
  二、**登记一致性**：凡被引用的外部仓库，必须在 `references/external-sources.md` 的核验范围内，
      且许可门禁被如实标注（GPL/AGPL/CC-BY-NC 必须标「仅外部调用」）。

为什么需要它：外部通道一旦重新引入，最容易出的错是「**编造链接**」与「**许可失守**」——
这两类错**都不会**被原有 5 个校验器抓到（它们只查库内结构）。

用法：python scripts/extskill.py [树根]
判据：全部 PASS → rc 0；任一 FAIL → rc 1。
"""
import io
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') \
    else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)

FAIL = []
WARN = []
OK = []


def bad(m):
    FAIL.append(m)


def warn(m):
    WARN.append(m)


def ok(m):
    OK.append(m)


def rd(p):
    with io.open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


LOCAL_PREFIX = ('references/', 'library/', 'domains/', 'scripts/', 'commands/', '.learnbuddy/')
LOCAL_EXT = re.compile(r'\.(md|py|sh|json|ya?ml|txt|html?)$')


def repos_in(text):
    """抽出形如 `owner/repo` 的仓库标识；**排除**本地路径与占位写法。"""
    out = set()
    for m in re.finditer(r'`([A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)`', text):
        r = m.group(1)
        if r.startswith(LOCAL_PREFIX) or LOCAL_EXT.search(r):
            continue
        if r in ('owner/repo', 'owner/repo.git'):
            continue
        out.add(r)
    return out


# ---------- 1. 1 级规则在位 ----------
if os.path.isfile('library/external-bridge.md'):
    t = rd('library/external-bridge.md')
    ok('library/external-bridge.md 在位')
    for h in ('## 1. 本包的三档降级链', '## 4. 五步自检', '## 5. 许可门禁', '## 7. 回落'):
        if h not in t:
            bad('external-bridge.md 缺小节 %s' % h)
    for w in ('档 1', '档 2', '档 3', '纯提示词'):
        if w not in t:
            bad('external-bridge.md 未写清 %s（三档口径不全）' % w)
    if '不得把「外部桥接」当作**第一选择**' not in t:
        bad('external-bridge.md 未声明「外部桥接非第一选择」（库内优先被削弱）')
else:
    bad('缺 library/external-bridge.md（外部桥接无成文规则）')

# ---------- 2. 平台表：≥10 个入口 ----------
if os.path.isfile('references/external-sources.md'):
    s = rd('references/external-sources.md')
    urls = set(re.findall(r'https?://[A-Za-z0-9\-._~:/?#\[\]@!$&()*+,;=%]+', s))
    plat = set()
    for u in urls:
        m = re.match(r'https?://([a-z0-9.-]+)', u)
        if m:
            h = m.group(1).lower()
            if 'github.com' in h:
                mm = re.match(r'https?://github\.com/([^/]+)', u)
                if mm:
                    plat.add('github:' + mm.group(1))
            else:
                plat.add(h.replace('www.', ''))
    if len(plat) < 10:
        bad('external-sources.md 平台数 = %d（要求 ≥10）' % len(plat))
    else:
        ok('平台入口数 = %d（≥10）' % len(plat))
    # 许可红线成文
    for w in ('GPL', 'AGPL', 'CC-BY-NC', '禁止'):
        if w not in s:
            warn('external-sources.md 未见许可红线词 %s' % w)
else:
    bad('缺 references/external-sources.md（无 12 平台入口表）')

# ---------- 3. 2 级：每域都要有「外部承接」 ----------
dom_dirs = sorted(d for d in os.listdir('domains')
                  if os.path.isdir(os.path.join('domains', d)))
n_ok = n_none = n_todo = 0
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
    if not m:
        bad('%s 缺「## 外部承接」段（外部桥接断链）' % p)
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    has_cand = '已核验候选' in body
    has_none = ('无合规且适配' in body) or ('无外部承接' in body)
    has_todo = '尚未完成外部候选复核' in body
    if not (has_cand or has_none or has_todo):
        bad('%s 的「外部承接」段既无候选也未声明「无候选」（口径缺失）' % p)
        continue
    if has_todo:
        n_todo += 1
    elif has_none:
        n_none += 1
        if '回落' not in body and '纯提示词' not in body:
            bad('%s 声明无候选但未写明回落路径' % p)
    else:
        n_ok += 1
        if not repos_in(body):
            bad('%s 声明有候选但未给 `owner/repo` 仓库标识' % p)
    # 许可门禁：出现 GPL/AGPL/CC-BY-NC 时必须标「仅外部调用」
    if re.search(r'GPL|AGPL|CC-BY-NC', body) and '仅外部调用' not in body:
        bad('%s 的候选含 GPL/AGPL/CC-BY-NC 但未标「仅外部调用」' % p)
ok('外部承接：有候选 %d 域 / 已复核无候选 %d 域 / 待复核 %d 域' % (n_ok, n_none, n_todo))

# ---------- 4. 3 级：92 个 skill 的降级段必须是三档 ----------
sk = sorted(glob_sk := [p.replace(os.sep, '/') for p in
                        __import__('glob').glob('domains/*/skills/local/*/SKILL.md')])
bad3 = []
for p in sk:
    t = rd(p)
    m = re.search(r'^##\s*失败与降级[^\n]*$', t, re.M)
    if not m:
        bad3.append((p, '缺段'))
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    miss = []
    if 'external-bridge.md' not in body:
        miss.append('未接 external-bridge.md')
    if '纯提示词模式' not in body:
        miss.append('未保留档 3（纯提示词）')
    if '降级承接' not in body:
        miss.append('未保留档 1（同域降级承接）')
    if miss:
        bad3.append((p, '/'.join(miss)))
if bad3:
    for p, why in bad3[:8]:
        bad('%s 降级段不全：%s' % (p, why))
    if len(bad3) > 8:
        bad('（另有 %d 个 skill 同型问题）' % (len(bad3) - 8))
else:
    ok('%d 个库内 skill 的降级段均为三档' % len(sk))

# ---------- 5. 登记一致性 + 可达性声明 ----------
POOL = set()
if os.path.isfile('references/external-sources.md'):
    dec = rd('references/external-sources.md')
    if '实测' not in dec:
        warn('external-sources.md 未登记「实测」结论（无法判断是否核验过）')
    if '200' not in dec:
        warn('external-sources.md 未登记可达性实测值')
    POOL = repos_in(dec)
    if len(POOL) < 20:
        bad('已核验仓库池过小（%d 个，期望 ≥20）→ 登记面不足' % len(POOL))
    else:
        ok('已核验仓库池 = %d 个' % len(POOL))

if POOL:
    miss = []
    for d in dom_dirs:
        p = 'domains/%s/_domain.md' % d
        if not os.path.isfile(p):
            continue
        t = rd(p)
        m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
        if not m:
            continue
        nxt = re.search(r'^##\s', t[m.end():], re.M)
        body = t[m.end():][:nxt.start() if nxt else len(t)]
        for r in repos_in(body):
            if r not in POOL:
                miss.append('%s -> %s' % (d, r))
    if miss:
        for x in miss[:8]:
            bad('引用了未登记的候选仓库（疑编造）：%s' % x)
        if len(miss) > 8:
            bad('（另有 %d 处同型问题）' % (len(miss) - 8))
    else:
        ok('2 级引用的候选仓库全部已在池中登记（零编造）')


# ---------- 6. 指定检索平台：数量 2–3 且必须在 20 个平台之内 ----------
PLATSET = set()
if os.path.isfile('references/external-sources.md'):
    for m in re.finditer(r'https?://([a-z0-9.-]+)', rd('references/external-sources.md')):
        h = m.group(1).lower().replace('www.', '')
        PLATSET.add(h)
    PLATSET.discard('github.com')

n_pl = {}
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
    if not m:
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    mm = re.search(r'\*\*指定检索平台[^\n]*', body)
    if not mm:
        bad('%s 未指定检索平台（命中规则无法执行）' % p)
        continue
    pl = re.findall(r'`([a-z0-9.-]+)`', mm.group(0))
    n_pl[d] = pl
    if not (2 <= len(pl) <= 3):
        bad('%s 指定平台 %d 个（要求 2–3）' % (p, len(pl)))
    for x in pl:
        if x.replace('www.', '') not in PLATSET:
            bad('%s 指定了未登记的平台 `%s`（疑编造平台）' % (p, x))
if n_pl:
    ok('指定检索平台：%d 个域，均为 2–3 个且已在平台表登记' % len(n_pl))

# ---------- 6b. 平台检索式必须在位（否则检索必 0 命中）----------
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
    if not m:
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    if '**平台检索式' not in body:
        bad('%s 未给「平台检索式」（中文长句拿去检索会 0 命中）' % p)
ok('平台检索式检查完成')

# ---------- 6c. 适配词表必须在位（否则自检第 5 项等于默认通过 → 假命中）----------
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
    if not m:
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    if '**适配词表' not in body:
        bad('%s 未给「适配词表」（自检第 5 项将退化为默认通过 → 假命中）' % p)
        continue
    mm = re.search(r'\*\*适配词表[^\n]*', body)
    if '不适用' not in mm.group(0):
        w = re.findall(r'`([a-z0-9 -]+)`', mm.group(0))
        if len(w) < 3:
            bad('%s 适配词表仅 %d 词（要求 ≥3）' % (p, len(w)))
ok('适配词表检查完成')

# ---------- 6d. 全局反向词表必须在位（否则正向词会偶然命中 → 假命中）----------
if os.path.isfile('references/external-sources.md'):
    _dec = rd('references/external-sources.md')
    if '反向词表' not in _dec:
        bad('external-sources.md 缺「全局反向词表」（假命中闸门缺失）')
    else:
        _m = re.search(r'^##\s*四、全局反向词表(.*?)(?=^##\s)', _dec, re.M | re.S)
        _w = re.findall(r'`([a-z]+)`', _m.group(1)) if _m else []
        if len(_w) < 8:
            bad('全局反向词表仅 %d 词（要求 ≥8）' % len(_w))
        else:
            ok('全局反向词表 = %d 词' % len(_w))

# ---------- 7. 敏感域必须声明禁外接 ----------
for d in ('F3-wellbeing', 'F5-health'):
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    if '禁外接' not in t and '不外接' not in t:
        bad('%s 未声明「敏感域禁外接」（红线缺口）' % p)
    else:
        ok('%s 已声明禁外接' % d)

# ---------- 8. 无许可候选必须标 ⛔ ----------
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\s*外部承接[^\n]*$', t, re.M)
    if not m:
        continue
    nxt = re.search(r'^##\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    if '未声明' in body and '⛔' not in body:
        bad('%s 含「未声明」许可的候选但未标 ⛔ 不入围' % p)
ok('许可标注检查完成')

print('=' * 68)
for m in OK:
    print('  OK   %s' % m)
for m in WARN:
    print('  WARN %s' % m)
for m in FAIL:
    print('  FAIL %s' % m)
print('=' * 68)
print('结果: OK %d ｜ WARN %d ｜ FAIL %d' % (len(OK), len(WARN), len(FAIL)))
sys.exit(1 if FAIL else 0)
