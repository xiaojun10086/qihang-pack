#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部桥接 · **真机演练**（build 侧工具，不随包分发）。

为什么要有它：`scripts/extskill.py` 只做**静态**接线检查（文件对不对、登记一致不一致），
它**证明不了**「按域指定的 2–3 个平台真的能检索、命中判定真的能执行」。
本脚本把流程**真跑一遍**：读指定平台 → 走真实检索通道 → 对命中候选跑五步自检 → 打印档位结论。

判定链（与 `library/external-bridge.md` 完全一致）：
    红线域（F3/F5）→ 直接档 3（禁外接，不检索）
    否则 → 在**指定平台**内检索 → 过五步自检 → 命中则档 2，未命中则档 3

用法：
    python scripts/_build/v3/tests/bridge_probe.py [仓库根] [--live]
    --live：真的发检索请求（默认只做静态演练 + 平台可达性）
"""
import io
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG and not ARG[0].startswith('-') \
    else os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
LIVE = '--live' in sys.argv
ONLY = set()
if '--only' in sys.argv:
    ONLY = set(x.strip() for x in sys.argv[sys.argv.index('--only') + 1].split(','))
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) HeadlessChrome/154.0.0.0 Safari/537.36")
CTX = ssl._create_unverified_context()
REDLINE = ('F3-wellbeing', 'F5-health')
PERMISSIVE = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'CC0-1.0', 'ISC'}
COPYLEFT = {'GPL-3.0', 'AGPL-3.0', 'LGPL-3.0', 'CC-BY-NC-4.0'}

# 域 → 检索词（演练用；实际运行时由 _domain.md 的「检索词」行给出）
QUERY = {
    'S6-language': 'claude skill english ielts tutor',
    'S1-course-qa': 'claude skill socratic tutor',
    'R1-literature': 'agent skill literature review paper',
    'F6-service': 'agent skill volunteering service hours log',
    'F4-money-safety': 'claude skill budget scam guard student',
}


def recipe(dom):
    """从 _domain.md 读「平台检索式（英文，≤3 词）」—— 演练直接照抄，不另编。"""
    t = rd('domains/%s/_domain.md' % dom)
    m = re.search(r'\*\*平台检索式[^\n]*', t)
    if not m:
        return None
    if '不适用' in m.group(0):
        return 'REDLINE'
    mm = re.findall(r'`([^`]+)`', m.group(0))
    return mm[0] if mm else None


def rd(p):
    with io.open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def get(url, timeout=25):
    o = urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX))
    o.addheaders = [("User-Agent", UA), ("Accept", "application/vnd.github+json")]
    try:
        r = o.open(url, timeout=timeout)
        return r.status, r.read(200000)
    except Exception as e:
        return None, str(e)[:80]


def designated(dom):
    t = rd('domains/%s/_domain.md' % dom)
    m = re.search(r'\*\*指定检索平台[^\n]*', t)
    return re.findall(r'`([a-z0-9.\-]+)`', m.group(0)) if m else []


def gh_search(q, n=5):
    s, b = get('https://api.github.com/search/repositories?q=%s&sort=stars&per_page=%d'
               % (urllib.parse.quote_plus(q), n))
    if s != 200:
        return None, str(b)
    return json.loads(b.decode())['items'], None


def adapt_words(dom):
    """从 _domain.md 读「适配词表」—— 自检第 5(a) 项的可执行判据。"""
    t = rd('domains/%s/_domain.md' % dom)
    m = re.search(r'\*\*适配词表[^\n]*', t)
    if not m:
        return []
    if '不适用' in m.group(0):
        return []
    return [w.lower() for w in re.findall(r'`([^`]+)`', m.group(0))]


NEG_WORDS = ['medical', 'clinical', 'patient', 'segmentation', 'diagnosis',
             'blockchain', 'crypto', 'trading', 'stock', 'forex',
             'game', 'gaming', 'gacha',
             'dating', 'ecommerce', 'shop', 'ads', 'marketing', 'seo',
             'codebase', 'repository', 'refactor', 'leetcode']


def selfcheck5(it, words):
    """五步自检（**可执行子集**：数据量 / 许可 / 可用性 / 脚本与指令风险 / 适配度）。"""
    lic = (it.get('license') or {}).get('spdx_id') or 'NONE'
    stars = it.get('stargazers_count', 0)
    arch = it.get('archived', False)
    pushed = (it.get('pushed_at') or '')[:10]
    out = []
    out.append(('数据量', stars >= 100, '★%d（门槛 ≥100）' % stars))
    if lic in PERMISSIVE:
        out.append(('许可', True, lic))
    elif lic in COPYLEFT:
        out.append(('许可', True, '%s（仅外部调用）' % lic))
    else:
        out.append(('许可', False, lic))
    out.append(('可用性', not arch, 'archived=%s ｜ pushed=%s' % (arch, pushed)))
    out.append(('脚本与指令风险', True, '需读 scripts/ 与正文（演练不代判，默认通过）'))
    blob = ((it.get('name') or '') + ' ' + (it.get('description') or '') + ' '
            + ' '.join(it.get('topics') or [])).lower()
    hits = [w for w in words if w in blob]
    neg = [w for w in NEG_WORDS if w in blob]
    okfit = bool(hits) and not neg
    why = ('正向命中 %s' % (', '.join(hits) or '无'))
    if neg:
        why += ' ｜ 反向命中 %s' % ', '.join(neg)
    out.append(('适配度', okfit, why))
    return out, lic


def main():
    doms = sorted(d for d in os.listdir(os.path.join(ROOT, 'domains'))
                  if os.path.isdir(os.path.join(ROOT, 'domains', d)))
    print('目标树：%s' % ROOT)
    print('模式：%s' % ('LIVE（真发检索请求）' if LIVE else '静态（只演练判定链）'))
    print('=' * 92)
    rows = []
    for d in doms:
        pl = designated(d)
        if d in REDLINE:
            rows.append((d, len(pl), '红线域 → 禁外接', '档 3（不检索）'))
            continue
        if not pl:
            rows.append((d, 0, '未指定平台', '!! 接线缺失'))
            continue
        if not LIVE:
            rows.append((d, len(pl), ' | '.join(pl[:2]) + '…', '（静态通过，未真查）'))
            continue
        q = recipe(d)
        if q == 'REDLINE' or not q:
            rows.append((d, len(pl), ' | '.join(pl[:2]) + '…', '检索式缺失 → 档 3'))
            continue
        if ONLY and d not in ONLY:
            rows.append((d, len(pl), ' | '.join(pl[:2]) + '…', '（静态通过，未真查）'))
            continue
        items, err = gh_search(q)
        if items is None:
            rows.append((d, len(pl), ' | '.join(pl), '检索失败：%s → 档 3' % err[:40]))
            continue
        hit = None
        words = adapt_words(d)
        for it in items:
            chk, lic = selfcheck5(it, words)
            bad = [c for c in chk if not c[1]]
            print('  [候选] %-42s ★%-7s %-12s %s'
                  % (it['full_name'], it['stargazers_count'], lic,
                     '通过' if not bad else '淘汰(%s: %s)' % (bad[0][0], bad[0][2][:26])))
            if not bad and hit is None:
                hit = it
        if hit:
            rows.append((d, len(pl), ' | '.join(pl),
                         '命中 → 档 2 · %s（★%d, %s）'
                         % (hit['full_name'], hit['stargazers_count'],
                            (hit.get('license') or {}).get('spdx_id'))))
        else:
            rows.append((d, len(pl), ' | '.join(pl), '指定平台内未命中 → 档 3（无 skill 流程）'))

    print()
    print('%-20s %-4s %-46s %s' % ('域', '平台', '指定平台', '演练结论'))
    print('-' * 132)
    for d, n, pl, v in rows:
        print('%-20s %-4d %-46s %s' % (d, n, pl[:46], v))
    print()
    n2 = sum(1 for r in rows if '档 2' in r[3])
    n3 = sum(1 for r in rows if '档 3' in r[3] and '未命中' in r[3])
    nr = sum(1 for r in rows if '档 3（不检索）' in r[3])
    ns = sum(1 for r in rows if '静态' in r[3])
    print('结论分布：档 2（命中）%d ｜ 档 3（未命中回落）%d ｜ 红线禁外接 %d ｜ 未真查 %d'
          % (n2, n3, nr, ns))


if __name__ == '__main__':
    main()
