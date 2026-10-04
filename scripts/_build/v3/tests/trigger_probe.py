#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""触发门 + 降级档序 · **真机演练**（build 侧工具，不随包分发）。

为什么要有它：`selfcheck [8d]` 只证明「文本在位」，**证明不了流程真的成立**。
本脚本把三件事真跑一遍：
  ① **触发门**：从 `config.yaml` 的 `trigger` 段取标记词，对样例输入判「接管 / 不接管」。
     越界信号（`out_of_scope_markers`）**优先级最高，命中即不接管**；token 级探测判不了的样例
     （多义词，如「面试用」）**如实移交主键 T+O 判定**，**绝不用改写输入的方式伪造结论**；
  ② **越界表不变式**：越界表与三张接管词表**零交集**、表内无冗余子串项、各域触发词不被硬停吞掉
     （本项曾缺失 → R4 `grant-apply` 被「基金」硬停吞掉、永不可达而无人报警）；
  ③ **档序**：对接管的输入走 档1 同域库内 → 档2 外部桥接（可 live 真检索）→ 档3 自生成，
     并**断言档 3 绝不早于档 2**（即"外源检索不成功才能自行生成"）。

用法：
    python scripts/_build/v3/tests/trigger_probe.py [仓库根] [--live]
"""
import io
import glob
import json
import os
import re
import ssl
import sys
import urllib.parse
import urllib.request

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
LIVE = '--live' in sys.argv
CTX = ssl._create_unverified_context()
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 HeadlessChrome/154.0.0.0 Safari/537.36"
REDLINE = ('F3-wellbeing', 'F5-health')

# 样例输入：[原话, 期望（接管 / 不接管 / 主键）]
# 「主键」= token 级探测**判不了**，须由主键 T(任务)+O(对象) 定归属 —— 如实移交，不伪造结论。
CASES = [
    ('我是大工2026级新生，想规划一下考研', '接管'),
    ('帮我复习一下高数，快考试了', '接管'),
    ('大工图书馆几点开门？', '接管'),
    ('帮我找找有没有现成的文献管理工具', '接管'),
    ('我最近想学 Python，从哪儿开始', '接管'),
    ('帮我写基金申请书，先给个框架', '接管'),      # 回归：曾因越界表含「基金」而永不可达
    ('帮我写个冒泡排序（面试用）', '主键'),        # 初筛命中「面试」，归属须主键 T+O 判定
    ('推荐几部电影看看', '不接管'),                # 越界表命中
    ('北京明天天气怎么样', '不接管'),              # 越界表命中
]
COURSE_ROUTE_CASES = [
    '请帮我规划整门课的学习顺序',
    '我想按这本书从零入门',
    '我想从零学一门课',
    '我想系统学一门课程',
    '请逐章讲解整本教材',
]

SELF_ID = re.compile(r'(我是|我就是|咱是|我也是|我们学校|我们大工|我校).{0,12}(大工|大连理工|DUT|凌水|盘锦校区|开发区校区)')


def rd(p):
    with io.open(os.path.join(ROOT, p), 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def rd_abs(p):
    with io.open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def yaml_list(text, key):
    m = re.search(r'^\s*' + key + r':\s*\[(.*?)\]', text, re.M)
    if not m:
        return []
    return [x.strip() for x in m.group(1).split(',') if x.strip()]


def get(url, timeout=20):
    o = urllib.request.build_opener(urllib.request.HTTPSHandler(context=CTX))
    o.addheaders = [("User-Agent", UA), ("Accept", "application/vnd.github+json")]
    try:
        r = o.open(url, timeout=timeout)
        return r.status, r.read(200000)
    except Exception as e:
        return None, str(e)[:70]


def main():
    cfg = rd('config.yaml')
    dlut = yaml_list(cfg, 'dlut_markers')
    learn = yaml_list(cfg, 'learning_markers')
    intent = yaml_list(cfg, 'learning_intents')
    oos = yaml_list(cfg, 'out_of_scope_markers')
    print('真相源 config.yaml trigger：dlut_markers %d 个 ｜ learning_markers %d 个 ｜ learning_intents %d 个'
          ' ｜ out_of_scope_markers %d 个'
          % (len(dlut), len(learn), len(intent), len(oos)))
    print('=' * 96)
    route = build_route()
    print('路由表：由 domains/*/_domain.md 的 `## 触发词` 派生（不再硬编码），共 %d 域' % len(route))
    print('=' * 96)

    ok_rows, bad, defer = [], [], []
    for text, expect in CASES:
        # 越界信号优先级最高：命中即不接管（config.yaml 声明「压过宽词表」）
        hit_o = [m for m in oos if m in text]
        hit_d = [m for m in dlut if m in text]
        hit_l = [m for m in learn if m in text]
        hit_i = [m for m in intent if m in text]
        hit_s = bool(SELF_ID.search(text))
        triggered = (not hit_o) and bool(hit_d or hit_l or hit_i or hit_s)
        got = '接管' if triggered else '不接管'
        why = []
        if hit_o:
            why.append('越界:' + '/'.join(hit_o[:2]))
        if hit_s:
            why.append('T3自述')
        if hit_d:
            why.append('T1:' + '/'.join(hit_d[:2]))
        if hit_l:
            why.append('T2词:' + '/'.join(hit_l[:2]))
        if hit_i:
            why.append('T2意图:' + '/'.join(hit_i[:2]))
        if expect == '主键':
            # 旧版用 re.sub 把「（面试用）」从输入里删掉，硬凑出「不接管」—— 那是自欺。
            # 这里如实移交，并断言公开口径已写明，防再次靠改写输入制造绿灯。
            if hit_o:
                bad.append((text, '主键移交（越界表不得拦下）', '越界表命中 ' + '/'.join(hit_o)))
            elif not (hit_l or hit_i):
                bad.append((text, '主键移交（须有初筛命中）', '无 token 命中，不该进主键判定'))
            elif '需求主键' not in cfg:
                bad.append((text, '主键移交（口径须公开）', 'config.yaml 未声明需求主键 T+O'))
            else:
                defer.append(text)
            print('%s %-30s → %-4s  [%s]' % ('⚠️', text[:30], '主键',
                                            'token 初筛命中 ' + '/'.join((hit_l + hit_i)[:2])
                                            + '，归属由主键 T+O 定'))
            ok_rows.append((text, False))   # 真值待主键判定，不参与档序演练
            continue
        mark = '✅' if got == expect else '❌'
        if got != expect:
            bad.append((text, expect, got))
        print('%s %-30s → %-4s  [%s]' % (mark, text[:30], got, ' ｜ '.join(why) or '三条件均不成立'))
        ok_rows.append((text, triggered))

    # ---- 越界表不变式（真机断言）----
    # 为什么加：越界表声明「优先级最高，压过宽词表」，而「基金」曾同时进 R4 触发词与越界表
    # → R4 的 grant-apply 被硬停吞掉、永不可达，当时**没有任何校验器会响**。
    inv = []
    for nm, lst in (('learning_markers', learn), ('dlut_markers', dlut),
                    ('learning_intents', intent)):
        cl = sorted(set(oos) & set(lst))
        if cl:
            inv.append('out_of_scope_markers ∩ %s = %s（越界硬停会吞掉合法域路由）'
                       % (nm, '、'.join(cl)))
    dup = sorted({b for a in oos for b in oos if a != b and a in b})
    if dup:
        inv.append('越界表含冗余子串项（子串匹配下恒被更长项覆盖）：%s' % '、'.join(dup))
    for d, kw in route:
        if kw and not [w for w in kw if w not in oos]:
            inv.append('域 %s 的全部触发词都在越界表内 → 该域永不可达' % d)
    print()
    print('越界表不变式（互斥 / 无冗余 / 各域可达）：%s'
          % ('✅ 全部成立' if not inv else '❌ %d 项违反' % len(inv)))
    for x in inv:
        print('   ❌ %s' % x)

    route_bad = []
    for text in COURSE_ROUTE_CASES:
        got = pick_domain(text, route)
        if got != 'S4-exam-prep':
            route_bad.append((text, 'S4-exam-prep', got))
        print('%s %-30s → %s  [课程级路由]'
              % ('✅' if got == 'S4-exam-prep' else '❌', text[:30], got))

    print()
    print('=' * 96)
    print('档序演练（只对「接管」的样例）：档1 同域库内 → 档2 外部桥接 → 档3 自生成')
    print('=' * 96)
    order_violation = []
    for text, triggered in ok_rows:
        if not triggered:
            continue
        dom = pick_domain(text, route)
        if dom is None:
            print('  %-28s → 未命中任何域触发词（token 级不可路由）' % text[:28])
            continue
        skills = local_skills(dom)
        rung, detail = ladder(dom, text, skills)
        print('  %-28s → %s' % (text[:28], detail))
        if rung == 3 and not ladder_ok(dom, text, skills):
            order_violation.append((text, detail))

    # ---- 档序三场景：把整条链跑穿（含 档2 真检索 / 档3 自生成）----
    print('=' * 96)
    print('档序三场景（强制走穿）：L1 档1 命中 ｜ L2 档1 落空 → 档2 命中 ｜ L3 档1 落空 → 档2 未命中 → 档3')
    print('=' * 96)
    trail = ladder_trail('S1-course-qa', '帮我复习高数', has_local=True)
    print('  L1 %s' % trail)
    trail2 = ladder_trail('R4-publication', '帮我写一篇顶会论文的 rebuttal', has_local=False)
    print('  L2 %s' % trail2)
    trail3 = ladder_trail('R6-info-retrieval', '帮我找找有没有现成的课程表导出脚本', has_local=False)
    print('  L3 %s' % trail3)
    # 断言：档 3 只可能出现在「档2 已尝试」之后
    for name, tr in (('L1', trail), ('L2', trail2), ('L3', trail3)):
        if '档3' in tr and '档2' not in tr:
            order_violation.append((name, tr))

    print()
    print('=' * 96)
    _decided = len(CASES) - len(defer)
    print('触发门判定：%d/%d 符合预期 ｜ %d 例如实移交主键 T+O 判定'
          % (_decided - len(bad), _decided, len(defer)))
    for t, e, g in bad:
        print('   ❌ %r 期望 %s 实得 %s' % (t, e, g))
    for t in defer:
        print('   ⚠️ %r 由主键 T+O 定归属（token 级探测不适用）' % t)
    print('越界表不变式：%s' % ('✅ 互斥 / 无冗余 / 各域可达' if not inv else '❌ %d 项违反' % len(inv)))
    for x in inv:
        print('   ❌ %s' % x)
    print('课程级路由：%d/%d 命中 S4' % (len(COURSE_ROUTE_CASES) - len(route_bad),
                                      len(COURSE_ROUTE_CASES)))
    for t, e, g in route_bad:
        print('   ❌ %r 期望 %s 实得 %s' % (t, e, g))
    print('档序违规（档 3 早于档 2）：%d 例' % len(order_violation))
    for t, d in order_violation:
        print('   ❌', t, d)
    _ok = not bad and not inv and not route_bad and not order_violation
    print('结论：%s' % ('✅ 触发门、越界表不变式、课程级路由与档序均成立'
                       if _ok else '❌ 有问题'))
    if not _ok:
        raise SystemExit(1)


def ladder_trail(dom, text, has_local):
    """强制走穿档序，返回轨迹字符串。has_local=False 用于模拟「档1 无对口 skill」。"""
    steps = []
    if has_local:
        steps.append('档1 同域库内命中（%s）' % dom)
        return ' → '.join(steps) + ' → 承接（不进入档 2/3）'
    steps.append('档1 无对口（%s）' % dom)
    q = recipe(dom)
    if not q:
        steps.append('档2 跳过（本域禁外接）')
        steps.append('档3 自生成')
        return ' → '.join(steps)
    if not LIVE:
        steps.append('档2 外源检索（静态，未真查，query=%r）' % q)
        steps.append('档3 自生成（因档2 未命中）')
        return ' → '.join(steps)
    s, b = get('https://api.github.com/search/repositories?q=%s&per_page=1'
               % urllib.parse.quote_plus(q))
    n = json.loads(b.decode()).get('total_count', 0) if s == 200 else 0
    if n > 0:
        steps.append('档2 外源检索命中（query=%r，total=%d）' % (q, n))
        return ' → '.join(steps) + ' → 外接（不进入档 3）'
    steps.append('档2 外源检索未命中（query=%r）' % q)
    steps.append('档3 自生成')
    return ' → '.join(steps)


# ---- 域路由：由真实 `domains/*/_domain.md` 的 `## 触发词` 派生（不再硬编码 8 域）----
def build_route():
    """返回 [(域目录名, [触发词…])]，覆盖全部 20 域。"""
    route = []
    for p in sorted(glob.glob(os.path.join(ROOT, 'domains', '*', '_domain.md'))):
        m = re.search(r'^##\s*触发词[^\n]*\n(.*?)(?=^##\s)', rd_abs(p), re.M | re.S)
        if not m:
            continue
        # 段内反引号也可能包着域代号 / 路径，不是触发词
        kw = [w for w in re.findall(r'`([^`]+)`', m.group(1))
              if not re.fullmatch(r'[A-Z]\d', w) and '/' not in w and '.' not in w]
        if kw:
            route.append((os.path.basename(os.path.dirname(p)), kw))
    return route


def pick_domain(text, route):
    """最长匹配优先（更具体的词胜出）；无命中返回 None（token 级不可路由，不编造归属）。"""
    low = text.lower()
    best, blen = None, 0
    for dom, kw in route:
        for k in kw:
            if len(k) > blen and k.lower() in low:
                best, blen = dom, len(k)
    return best


def local_skills(dom):
    p = os.path.join(ROOT, 'domains', dom, 'skills', 'local')
    return sorted(os.listdir(p)) if os.path.isdir(p) else []


def recipe(dom):
    try:
        t = rd('domains/%s/_domain.md' % dom)
    except Exception:
        return None
    m = re.search(r'\*\*平台检索式[^\n]*', t)
    if not m or '不适用' in m.group(0):
        return None
    mm = re.findall(r'`([^`]+)`', m.group(0))
    return mm[0] if mm else None


def ladder(dom, text, skills):
    """返回 (落点档位, 说明)。档 1 = 同域库内命中；否则档 2 真检索；未命中才档 3。"""
    if skills:
        return 1, '档1 同域库内命中（%s，%d 个候选）→ 承接' % (dom, len(skills))
    q = recipe(dom)
    if not q:
        return 3, '档2 跳过（本域禁外接/无检索式）→ 档3 自生成'
    if not LIVE:
        return 2, '档2 外源检索（静态演练，未真查）'
    s, b = get('https://api.github.com/search/repositories?q=%s&per_page=1'
               % urllib.parse.quote_plus(q))
    if s == 200 and json.loads(b.decode()).get('total_count', 0) > 0:
        return 2, '档2 外源检索命中（query=%r）→ 外接' % q
    return 3, '档2 外源检索未命中（query=%r）→ 档3 自生成' % q


def ladder_ok(dom, text, skills):
    """档 3 是否合法：必须是「档 1 无候选 且 档 2 已尝试未命中」或「本域禁外接」。"""
    if dom in REDLINE or not recipe(dom):
        return True
    return not skills


if __name__ == '__main__':
    main()
