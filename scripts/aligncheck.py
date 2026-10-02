#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」全量对齐审计（aligncheck）
==================================

用途：**打开每一个文件**做机器可判定的一致性检查，用于「对齐 + 可行性验证」。
与另外三个脚本的分工：
  selfcheck.sh   结构/计数（bash，轻量）
  audit.sh       安全/合规/门禁（bash）
  regress.sh     行为回归（bash，澄清门算例与 L3 门禁矩阵）
  aligncheck.py  **全量文件级对齐 + skill 可行性契约**（本脚本，Python）

用法:
  python scripts/aligncheck.py .            # 单轮
  python scripts/aligncheck.py . 5          # 连跑 5 轮（校验确定性）

检查项（14 组）：
  A 文件清单 / 可读性 / 空文件 / 编码 / BOM / 行尾
  B **重复内容检测**（连续重复行、重复小节、重复表格行 —— 抓生成器重复插入）
  C config.yaml：YAML 结构、列表无重复项、阈值与权重与文档一致
  D SKILL.md 契约：frontmatter / 归属域 / 必需小节 / 步骤数 / 示例三要素 / 输出字段
  E external.md 契约：表格列数一致、评分在值域、最优解唯一或声明无
  F _domain.md 契约：必需小节 / 库内 skill 实体存在 / 「不覆盖→X域」指向存在
  G 交叉引用：文档里写的路径真实存在
  H 计数与版本：registry 候选数、skill 数、版本号全域唯一
  I commands/*.md：入口可用、引用路径存在
  J .codebuddy-plugin/plugin.json：JSON 合法、版本一致
  K HTML：主要标签配平、引用的文档存在
  L 澄清门算例：文档中出现的 U 值可复算
  M 红线一致性：域 ↔ 库内 skill 逐条（含顺序）
  N 无临时/备份残留文件
"""
import os, re, sys, json, glob, io, hashlib, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].isdigit() else '.')
ROUNDS = 1
for a in sys.argv[1:]:
    if a.isdigit():
        ROUNDS = max(1, int(a))
os.chdir(ROOT)

FIND = []      # (级别, 文件, 说明)
def bad(f, m): FIND.append(('FAIL', f, m))
def warn(f, m): FIND.append(('WARN', f, m))
def rd(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()

def walk_files():
    out = []
    for base, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            out.append(os.path.join(base, fn).replace('\\', '/')[2:])
    return sorted(out)

FILES = walk_files()
MD = [f for f in FILES if f.endswith('.md')]
SKILLS = [f for f in FILES if f.endswith('SKILL.md')]
LOCAL = [f for f in SKILLS if '/skills/local/' in f]
EXTERNAL = [f for f in FILES if f.endswith('skills/external.md')]
DOMAIN = [f for f in FILES if f.endswith('/_domain.md')]
DOMS = sorted(d for d in os.listdir('domains') if os.path.isdir(os.path.join('domains', d)))

def run_round(r):
    del FIND[:]
    print('=' * 64)
    print('全量对齐审计 · 第 %d 轮 ｜ 文件总数 %d ｜ SKILL.md %d ｜ 库内 %d ｜ 域 %d'
          % (r, len(FILES), len(SKILLS), len(LOCAL), len(DOMAIN)))

    # ---------- A 文件清单 / 可读性 ----------
    for f in FILES:
        try:
            raw = open(f, 'rb').read()
        except Exception as e:
            bad(f, '无法读取: %s' % e); continue
        if len(raw) == 0:
            bad(f, '空文件')
        if raw.startswith(b'\xef\xbb\xbf'):
            warn(f, '含 UTF-8 BOM')
        if f.endswith('.md'):
            try:
                raw.decode('utf-8')
            except UnicodeDecodeError:
                bad(f, '非 UTF-8 编码')
            if b'\r\n' in raw:
                warn(f, '含 CRLF 行尾')

    # ---------- B 重复内容检测（抓生成器重复插入） ----------
    # .learnbuddy/memory/ 是**追加式日志**，同名小标题属正常，故排除在「重复标题」检查之外
    LOGDIR = '.learnbuddy/'
    for f in MD:
        lines = rd(f).splitlines()
        # B1 连续重复行
        for i in range(1, len(lines)):
            a, b = lines[i - 1].strip(), lines[i].strip()
            if a and a == b and len(a) > 12:
                bad(f, '第 %d/%d 行**连续重复**: %s' % (i, i + 1, a[:56]))
        # B2 重复三级标题（日志文件除外）
        if not f.startswith(LOGDIR):
            h3 = [l.strip() for l in lines if l.startswith('### ')]
            for t, c in collections.Counter(h3).items():
                if c > 1:
                    bad(f, '三级标题重复 %d 次: %s' % (c, t[:48]))
        # B3 重复表格数据行：**同一张表内**重复 = FAIL；跨表重复 = WARN（交叉登记，需人判）
        blocks, cur = [], []
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith('|') and not set(s) <= set('|-: '):
                nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
                is_header = bool(re.match(r'^\|[\s\-:|]+\|$', nxt))
                data_bearing = ('http' in s) or bool(re.search(r'\d', s)) or ('`' in s)
                if not is_header and data_bearing:
                    cur.append(s)
                continue
            if cur:
                blocks.append(cur); cur = []
        if cur:
            blocks.append(cur)
        allrows = [r for b in blocks for r in b]
        for t, c in collections.Counter(allrows).items():
            if c < 2 or t.count('|') < 3:
                continue
            in_same = max((sum(1 for r in b if r == t) for b in blocks), default=0)
            if in_same > 1:
                bad(f, '同一张表内数据行重复 %d 次: %s' % (in_same, t[:52]))
            else:
                warn(f, '跨表重复 %d 次（交叉登记，请人工确认）: %s' % (c, t[:52]))

    # ---------- C config.yaml ----------
    cfg = rd('config.yaml')
    if 'threshold: 0.30' not in cfg:
        bad('config.yaml', '未声明 threshold: 0.30')
    if not re.search(r'weights:\s*\{O:\s*1\.5,\s*T:\s*1\.5,\s*D:\s*1\.5,\s*W:\s*0\.8,\s*C:\s*0\.6,\s*B:\s*0\.2\}', cfg):
        bad('config.yaml', 'weights 与 clarity.md 不一致（应为 O/T/D=1.5 W=0.8 C=0.6 B=0.2）')
    for key in ('L1_auto', 'L2_confirm', 'L3_forbidden'):
        m = re.search(r'%s:\s*\[([^\]]*)\]' % key, cfg)
        if not m:
            bad('config.yaml', '缺 %s' % key); continue
        items = [x.strip() for x in m.group(1).split(',')]
        dup = [x for x, c in collections.Counter(items).items() if c > 1]
        if dup:
            bad('config.yaml', '%s 含重复项: %s' % (key, dup))
    if '成绩明细' not in cfg or '邮箱未读提示' not in cfg:
        bad('config.yaml', 'L3/L2 关键项缺失')

    # ---------- D SKILL.md 契约 ----------
    NEED = ['## 前置', '## 边界', '## 执行步骤', '## 可执行示例', '## ⚠️ 红线', '## 输出', '## DUT 绑定点', '## 失败与降级']
    for f in SKILLS:
        t = rd(f)
        fm = re.match(r'^---\n(.*?)\n---\n', t, re.S)
        if not fm:
            bad(f, '缺 frontmatter'); continue
        head = fm.group(1)
        for k in ('name:', 'description:', 'version:', 'license:'):
            if k not in head:
                bad(f, 'frontmatter 缺 %s' % k)
        vm = re.search(r'version:\s*([\d.]+)', head)
        if vm and vm.group(1) != '2.9.0':
            bad(f, '版本号 %s（期望 2.9.0）' % vm.group(1))
        if '/skills/local/' in f:
            for h in NEED:
                if h not in t:
                    bad(f, '缺必需小节 %s' % h)
            steps = re.search(r'## 执行步骤\n(.*?)(?=\n## )', t, re.S)
            n = len(re.findall(r'^\d+\. ', steps.group(1), re.M)) if steps else 0
            if n < 3:
                bad(f, '执行步骤仅 %d 步（期望 ≥3）' % n)
            for k in ('**输入**', '**澄清判定**', '**输出**'):
                if k not in t:
                    bad(f, '可执行示例缺 %s' % k)
            for k in ('【结论】', '【下一步】'):
                if k not in t:
                    bad(f, '示例输出缺 %s' % k)
            # 归属域
            did = f.split('/')[1].split('-')[0]
            m = re.search(r'归属域\*\*[：:]\s*`?([SFR]\d)`?', t)
            if not m:
                bad(f, '缺「归属域」')
            elif m.group(1) != did:
                bad(f, '归属域写 %s，实际属 %s' % (m.group(1), did))
            for ref in ('library/output-spec.md', 'library/output-checklist.md', '../../external.md'):
                if ref not in t:
                    warn(f, '未引用 %s' % ref)

    # ---------- E external.md 契约 ----------
    for f in EXTERNAL:
        t = rd(f)
        for h in ('## 一、候选比对', '## 二、评分口径', '## 三、最优解', '## 四、降级链'):
            if h not in t:
                bad(f, '缺小节 %s' % h)
        if 'DUT 落地评估' not in t:
            bad(f, '缺 DUT 落地评估')
        # 表格列数一致
        tbl = [l for l in t.splitlines() if re.match(r'^\|\s*\d+\s*\|', l)]
        if tbl:
            cols = [l.count('|') for l in tbl]
            if len(set(cols)) != 1:
                bad(f, '候选表列数不一致: %s' % sorted(set(cols)))
        nbest = t.count('✅ **最优解**')
        if nbest > 1:
            bad(f, '最优解标记 %d 个（应 ≤1）' % nbest)
        declared_none = ('无（纯自建）' in t) or ('无合规且适配 DUT' in t) or ('无合规库外首选' in t)
        if not declared_none and nbest == 0:
            warn(f, '既无最优解标记、也未声明「无」')
        for m in re.finditer(r'\|\s*(\d\.\d{2})\s*\|\s*(?:✅|⛔|⚠️|备选)', t):
            v = float(m.group(1))
            if not (0 <= v <= 5):
                bad(f, '综合分越界 %s' % v)

    # ---------- F _domain.md 契约 ----------
    for f in DOMAIN:
        t = rd(f)
        for h in ('## 域边界', '## 触发词', '## 库内 skill', '## DUT 绑定点', '## 执行顺序', '## ⚠️ 红线'):
            if h not in t:
                bad(f, '缺小节 %s' % h)
        if '## ⚠️ 红线' not in t:
            bad(f, '缺红线段')
        m = re.search(r'^##\s*⚠️\s*红线[^\n]*$', t, re.M)
        n = re.search(r'^##\s', t[m.end():], re.M)
        body = t[m.end():][:n.start() if n else len(t)]
        if len([l for l in body.splitlines() if l.startswith('- ')]) < 1:
            bad(f, '红线段为空')
        # 库内 skill 声明 vs 实体
        sec = re.search(r'##\s*库内 skill[^\n]*\n(.*?)(?=\n## )', t, re.S)
        decl = re.findall(r'`([\w-]+)`', sec.group(1)) if sec else []
        d = f.rsplit('/', 1)[0]
        real = sorted(x for x in os.listdir(os.path.join(d, 'skills', 'local'))
                      if os.path.isdir(os.path.join(d, 'skills', 'local', x)))
        if sorted(decl) != sorted(real):
            bad(f, '声明库内 skill %s ≠ 实体 %s' % (sorted(decl), sorted(real)))
        # 不覆盖 →X域 指向存在
        for x in re.findall(r'→\s*`?([SFR]\d)`?', t):
            if not any(dd.startswith(x + '-') for dd in DOMS):
                bad(f, '「不覆盖 →%s」指向不存在的域' % x)
        # 执行顺序必须「先判红线」
        if not re.search(r'0\.\s*\*\*先判红线\*\*', t):
            bad(f, '执行顺序未前置「先判红线」')

    # ---------- G 交叉引用 ----------
    pat = re.compile(r'(?:\.\./)*(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*`]+\.(?:md|sh|py|json)')
    seen = set()
    for f in MD:
        t = rd(f)
        for m in pat.finditer(t):
            p = m.group(0)
            cand = [p, os.path.normpath(os.path.join(os.path.dirname(f), p)).replace('\\', '/')]
            key = (f, p)
            if key in seen: continue
            seen.add(key)
            if not any(x in p for x in ('<', '>')):
                alive = any(os.path.exists(c) for c in cand)
                if '+' in p or '*' in p: continue
                if not alive:
                    bad(f, '失效引用 → %s' % p)

    # ---------- H 计数与版本 ----------
    reg = rd('domains/_registry.md')
    for line in reg.splitlines():
        m = re.match(r'^\|\s*`([SFR]\d)`\s*\|([^|]*)\|([^|]*)\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|', line)
        if not m: continue
        did, n = m.group(1), int(m.group(5))
        d = [x for x in DOMS if x.startswith(did + '-')][0]
        ex = rd('domains/%s/skills/external.md' % d)
        a = len([l for l in ex.splitlines() if re.match(r'^\|\s*\d+\s*\|', l)])
        if a != n:
            bad('domains/_registry.md', '%s 候选数记 %d，实际 %d' % (did, n, a))
    # 版本号：只认 **frontmatter 内**的 version（避免把报告正文里的引文当声明）
    vers = set()
    for f in FILES:
        if not f.endswith('.md'):
            continue
        t = rd(f)
        fm = re.match(r'^---\n(.*?)\n---', t, re.S)
        if not fm:
            continue
        m = re.search(r'^version:\s*([\d.]+)', fm.group(1), re.M)
        if m:
            vers.add(m.group(1))
    if vers - {'2.9.0'}:
        bad('（frontmatter）', '版本号不唯一: %s' % sorted(vers))
    # 插件清单（JSON 风格，易与 YAML 风格一起被漏改）
    try:
        pv = json.loads(rd('.codebuddy-plugin/plugin.json')).get('version')
        if pv != '2.9.0':
            bad('.codebuddy-plugin/plugin.json', 'version = %s（期望 2.9.0）' % pv)
    except Exception:
        pass
    # 当前状态/提交物 的版本声明（易漂移点，显式点名）
    for f, pat_ in (('PROJECT.md', r'##\s*7\.\s*当前状态（v([\d.]+)）'),
                    ('qihang-scenario-design.html', r'<title>[^<]*（v([\d.]+)）')):
        t = rd(f)
        m = re.search(pat_, t)
        if m and m.group(1) != '2.9.0':
            bad(f, '版本声明 %s（期望 2.9.0）' % m.group(1))

    # ---------- I commands ----------
    for f in sorted(glob.glob('commands/*.md')):
        f = f.replace('\\', '/')
        t = rd(f)
        if not t.startswith('---'):
            warn(f, '无 frontmatter（slash 命令通常需要）')
        for p in re.findall(r'(?:domains|library|references|scripts)/[^ )），、；;"“”<>*`]+', t):
            if not os.path.exists(p) and '<' not in p and '+' not in p:
                bad(f, '引用不存在: %s' % p)

    # ---------- J plugin.json ----------
    try:
        pj = json.loads(rd('.codebuddy-plugin/plugin.json'))
        v = json.dumps(pj)
        if '2.9.0' not in v:
            warn('.codebuddy-plugin/plugin.json', '未声明版本 2.9.0')
    except Exception as e:
        bad('.codebuddy-plugin/plugin.json', 'JSON 无法解析: %s' % e)

    # ---------- K HTML ----------
    for f in FILES:
        if f.endswith('.html'):
            t = rd(f)
            for tag in ('html', 'head', 'body'):
                o = len(re.findall(r'<%s[\s>]' % tag, t, re.I))
                c = len(re.findall(r'</%s>' % tag, t, re.I))
                if o != c:
                    warn(f, '<%s> 开合不配平（%d/%d）' % (tag, o, c))
            for p in re.findall(r'(?:references|domains|library)/[^ )），、；;"“”<>*]+\.(?:md|html)', t):
                if not os.path.exists(p):
                    bad(f, '引用不存在: %s' % p)

    # ---------- L 澄清门算例复算 ----------
    W = {'O': 1.5, 'T': 1.5, 'D': 1.5, 'W': 0.8, 'C': 0.6, 'B': 0.2}
    SW = sum(W.values())
    def U(v):
        return 1 - sum(W[k] * v.get(k, 0) for k in W) / SW
    CASES = [((1, 1, 0.8, 0, 0, 0), 0.311), ((1, 1, 1, 1, 0, 0), None), ((1, 1, 0.5, 0, 0, 0), None)]
    v0 = {'O': 1, 'T': 1, 'D': 0.8}
    if abs(U(v0) - 0.311) > 0.002:
        bad('library/clarity.md', '例 A 的 U=%.4f 与文档 0.311 不符' % U(v0))
    for pat_ in [r'U\s*=\s*1\s*[−-]\s*([\d.]+)\s*/\s*6\.1\s*=\s*([\d.]+)']:
        for f in MD:
            for m in re.finditer(pat_, rd(f)):
                num, doc = float(m.group(1)), float(m.group(2))
                calc = round(1 - num / 6.1, 3)
                if abs(calc - doc) > 0.002:
                    bad(f, 'U 值复算不符: 文档 %s，复算 %.3f（%s/6.1）' % (doc, calc, num))

    # ---------- M 红线一致性 ----------
    def sig(t):
        m = re.search(r'^##\s*⚠️\s*红线[^\n]*$', t, re.M)
        if not m: return None
        rest = t[m.end():]
        n2 = re.search(r'^##\s', rest, re.M)
        body = rest[:n2.start()] if n2 else rest
        return [l.rstrip() for l in body.splitlines() if l.startswith('- ')]
    for d in DOMS:
        dm = 'domains/%s/_domain.md' % d
        ref = sig(rd(dm))
        for s in sorted(glob.glob('domains/%s/skills/local/*/SKILL.md' % d)):
            s = s.replace('\\', '/')
            s2 = sig(rd(s))
            if s2 != ref:
                bad(s, '红线与域文件不一致（域 %d 条 / skill %d 条）' % (len(ref or []), len(s2 or [])))

    # ---------- N 残留文件 ----------
    for f in FILES:
        base = os.path.basename(f)
        if (base.endswith(('.tmp', '.bak', '~')) or base.startswith('.selfcheck.tmp')
                or re.search(r'\.bak\.\d{8,}', base)):
            bad(f, '临时/备份文件残留')

    # ---------- O 库内 skill 可行性（能不能真的照着做） ----------
    import difflib
    titles = {}
    for f in LOCAL:
        t = rd(f)
        body = t.split('---\n', 2)[-1]
        tm = re.search(r'^#\s*(.+)$', body, re.M)
        title = tm.group(1).strip() if tm else '(无标题)'
        titles.setdefault(title, []).append(f)
        # O1 步骤可执行性
        steps = re.search(r'## 执行步骤\n(.*?)(?=\n## )', t, re.S)
        items = [x.strip() for x in re.findall(r'^\d+\.\s*(.+)$', steps.group(1), re.M)] if steps else []
        if not items:
            bad(f, '执行步骤为空')
        for s in items:
            if len(s) < 5:
                bad(f, '步骤过短、不可执行: %r' % s)
        if len(items) > 9:
            warn(f, '步骤 %d 步（偏多，执行成本高）' % len(items))
        # O2 示例可复现性
        m = re.search(r'\*\*输入\*\*\n\n>\s*(.+)', t)
        if not m:
            bad(f, '示例缺「输入」原文')
        elif len(m.group(1).strip()) < 5:
            bad(f, '示例输入过短、不可复现: %r' % m.group(1))
        # O3 澄清判定必须给出结论（放行/追问）
        mc = re.search(r'\*\*澄清判定\*\*[：:]\s*(.+)', t)
        if not mc:
            bad(f, '示例缺「澄清判定」')
        elif not re.search(r'放行|追问|U\s*[≤>]', mc.group(1)):
            bad(f, '澄清判定未给出明确结论: %r' % mc.group(1)[:40])
        # O4 红线含禁止语
        red = sig(t) or []
        if red and not any(re.search(r'不|禁|须|拒绝|不得', l) for l in red):
            bad(f, '红线条目未含禁止语（形同虚设）')
        # O5 分工表 + 降级标注
        if '与同域其他库内 skill 的分工' not in t:
            warn(f, '缺「与同域其他库内 skill 的分工」表（路由判定无依据）')
        if '[已降级]' not in t:
            warn(f, '未声明降级标注 [已降级]')
        # O6 示例输出按 output-spec 校验（**变体无关**，只查规格真约束）
        ob = re.search(r'\*\*输出\*\*\n\n```\n(.*?)```', t, re.S)
        if not ob:
            bad(f, '示例缺「输出」代码块')
        else:
            o = ob.group(1)
            labels = re.findall(r'^【([^】]+)】', o, re.M)
            if '结论' not in labels:
                bad(f, '示例输出缺【结论】（结论未前置）')
            if '下一步' not in labels:
                bad(f, '示例输出缺【下一步】（应只给 1 个动作）')
            # output-spec §1.1：除【结论】外 ≤ 6 条
            extra = [x for x in labels if x != '结论']
            if len(extra) > 6:
                bad(f, '示例输出要点 %d 条（>6，违反 output-spec §1.1）: %s' % (len(extra), extra))
            if not ('步骤' in labels or '网址' in labels):
                bad(f, '示例输出既无【步骤】也无【网址】（内容不足）')

    # O7 跨域标题唯一（重名会导致路由歧义）
    for title, fs in titles.items():
        if len(fs) > 1:
            bad('（全域）', '库内 skill 标题重名「%s」: %s' % (title, fs))
    # O8 同域两条 skill 定位不得高度相似（否则用户无法选择）
    for d in DOMS:
        fs = sorted(glob.glob('domains/%s/skills/local/*/SKILL.md' % d))
        if len(fs) < 2:
            continue
        pos = []
        for f_ in fs:
            m = re.search(r'\*\*定位\*\*[：:]\s*(.+)', rd(f_.replace('\\', '/')))
            pos.append(m.group(1).strip() if m else '')
        r = difflib.SequenceMatcher(None, pos[0], pos[1]).ratio()
        if r > 0.60:
            bad(fs[0].replace('\\', '/'), '同域两条 skill 定位相似度 %.2f（路由歧义）' % r)

    # ---------- P 三级路由链可解 ----------
    for d in DOMS:
        dm_p = 'domains/%s/_domain.md' % d
        dm = rd(dm_p)
        sec = re.search(r'## 触发词[^\n]*\n(.*?)(?=\n## )', dm, re.S)
        trig = re.findall(r'`([^`]+)`', sec.group(1)) if sec else []
        if len(trig) < 3:
            bad(dm_p, '触发词仅 %d 个（路由命中率不足）' % len(trig))
        local_dirs = sorted(x for x in os.listdir('domains/%s/skills/local' % d)
                            if os.path.isdir('domains/%s/skills/local/%s' % (d, x)))
        order = re.search(r'## 执行顺序\n(.*?)(?=\n## )', dm, re.S)
        o = order.group(1) if order else ''
        for lx in local_dirs:
            if lx not in o:
                bad(dm_p, '执行顺序未引用库内 skill `%s`（路由断链）' % lx)
        if 'skills/external.md' not in o:
            bad(dm_p, '执行顺序未给出库外兜底路径')
        if 'library/output-spec.md' not in o:
            bad(dm_p, '执行顺序未接输出规范')
    # P2 一级库链完整（SKILL.md 声明的规则文件必须都在）
    root_skill = rd('SKILL.md')
    for rf in re.findall(r'`(library/[\w-]+\.md)`', root_skill):
        if not os.path.exists(rf):
            bad('SKILL.md', '声明的规则文件不存在: %s' % rf)

    # ---------- Q 文档声明数 == 实测数（防计数漂移再次发生） ----------
    _rows = [(i, l) for i, l in enumerate(rd('references/dlut-official-sites.md').splitlines())
             if l.startswith('|')]
    _sep = {i for i, l in _rows if set(l) <= set('|-: ')}
    _hdr = {i - 1 for i in _sep}
    _data = [l for i, l in _rows if i not in _sep and i not in _hdr]
    ROWS = len(_rows)
    ENTRIES = len(_data)
    OK_N = len([l for l in _data if '✅' in l])
    WARN_N = len([l for l in _data if '⚠️' in l])
    # v2.9.2 全量扫描：不再用**文件名白名单**（旧版只查 7 个文件，ROADMAP / references
    # 全在射程外）。改为「全量扫描 + 内容标记豁免」，豁免必须**写在文件里**：
    #   · 文件级：前 20 行含「历史文档」→ 整文件豁免
    #   · 行级  ：该行或其前 2 行含「历史口径」→ 该处豁免
    # 另：分项口径（已核验 / 待核实 / 未标注）用**派生值**断言，杜绝「72/23/65 加不到 139」。
    UNMARKED = ENTRIES - OK_N - WARN_N
    _SUBSET = re.compile(r'待核实|未核实|已核验|未标注|学院类|清单|小节')
    for f in [x for x in (MD + [y for y in FILES if y.endswith('.html')])]:
        if not os.path.exists(f):
            continue
        t = rd(f)
        lines = t.split('\n')
        if any('历史文档' in l for l in lines[:20]):
            continue

        def _exempt(i, _ls=lines):
            return any('历史口径' in _ls[j] for j in range(max(0, i - 2), i + 1))

        for i, ln in enumerate(lines):
            if _exempt(i):
                continue
            for pat, exp, nm in (
                (r'(\d{2,4})\s*条\s*表格行', ROWS, '表格行'),
                (r'表格行\s*[:：]?\s*\*{0,2}(\d{2,4})', ROWS, '表格行'),
                (r'表格总行数[:：]\s*\*{0,2}(\d{2,4})', ROWS, '表格行'),
                (r'(\d{2,4})\s*条\s*条目', ENTRIES, '条目'),
                (r'数据条目\s*[:：]?\s*\*{0,2}(\d{2,4})', ENTRIES, '条目'),
            ):
                for m in re.finditer(pat, ln):
                    v = int(next(g for g in m.groups() if g))
                    if v != exp:
                        bad(f, '%s声明 %d ≠ 实测 %d（行 %d：%s）'
                            % (nm, v, exp, i + 1, ln.strip()[:60]))
            for pat, exp, nm in (
                (r'已核验\s*[:：]?\s*\*{0,2}(\d{1,3})\s*条', OK_N, '已核验'),
                (r'待核实\s*[:：]?\s*\*{0,2}(\d{1,3})\s*条', WARN_N, '待核实'),
                (r'未标注\s*[:：]?\s*\*{0,2}(\d{1,3})\s*条', UNMARKED, '未标注'),
            ):
                for m in re.finditer(pat, ln):
                    if int(m.group(1)) != exp:
                        bad(f, '%s声明 %s ≠ 实测 %d（行 %d：%s）'
                            % (nm, m.group(1), exp, i + 1, ln.strip()[:60]))
            # 总量口径：提到「公开站 / 信息库」且**不是**分项小节的句子，
            # 其中的「N 条」必须等于表格行数或条目数。
            if re.search(r'公开站|信息库|official-sites', ln) and not _SUBSET.search(ln):
                for m in re.finditer(r'(\d{2,4})\s*条', ln):
                    v = int(m.group(1))
                    if v not in (ROWS, ENTRIES):
                        bad(f, '公开站总量 %d ≠ 实测（表格行 %d / 条目 %d）（行 %d：%s）'
                            % (v, ROWS, ENTRIES, i + 1, ln.strip()[:60]))
            for m in re.finditer(r'✅\s*(\d{1,3})\s*/\s*⚠️\s*(\d{1,3})', ln):
                if int(m.group(1)) != OK_N or int(m.group(2)) != WARN_N:
                    bad(f, '✅/⚠️ 声明 %s/%s ≠ 实测(表内) %d/%d（行 %d）'
                        % (m.group(1), m.group(2), OK_N, WARN_N, i + 1))

    # §8 未核实清单：标题声明的项数 == 清单实际项数；各处引用的项数也必须一致
    if os.path.exists('references/dlut-official-sites.md'):
        _st = rd('references/dlut-official-sites.md')
        _h = re.search(r'^## 8\.\s*([^\n]+)$', _st, re.M)
        _b = re.search(r'^## 8\.[^\n]*\n\n([^\n]+)$', _st, re.M)
        if _h and _b:
            _d = re.search(r'共\s*(\d+)\s*条', _h.group(1))
            _items = [x for x in re.split(r'[·｜|]', _b.group(1)) if x.strip()]
            _n8 = len(_items)
            if _d and int(_d.group(1)) != _n8:
                bad('references/dlut-official-sites.md',
                    '§8 未核实清单声明 %s 条 ≠ 实际 %d 项' % (_d.group(1), _n8))
            for _f2 in [x for x in MD if '未核实清单' in rd(x)]:
                _l2 = rd(_f2).split('\n')
                if any('历史文档' in l for l in _l2[:20]):
                    continue
                for _m2 in re.finditer(r'(\d{1,3})\s*项\s*[「]?未核实清单', rd(_f2)):
                    if int(_m2.group(1)) != _n8:
                        bad(_f2, '「未核实清单」项数 %s ≠ 实测 %d'
                            % (_m2.group(1), _n8))
                for _m2 in re.finditer(r'未核实清单[」\*]{0,4}\s*(\d{1,3})\s*[项条]', rd(_f2)):
                    if int(_m2.group(1)) != _n8:
                        bad(_f2, '「未核实清单」项数 %s ≠ 实测 %d'
                            % (_m2.group(1), _n8))

    # 文件总数声明（口径：不含 .git/.idea/.learnbuddy）
    _pt = rd('PROJECT.md') if os.path.exists('PROJECT.md') else ''
    for m in re.finditer(r'\*\*(\d{2,4})\s*个文件\*\*', _pt):
        if int(m.group(1)) != len(FILES):
            bad('PROJECT.md', '文件总数声明 %s ≠ 实测 %d'
                % (m.group(1), len(FILES)))

    # ---------- 汇总 ----------
    nf = sum(1 for x in FIND if x[0] == 'FAIL')
    nw = sum(1 for x in FIND if x[0] == 'WARN')
    print('-' * 64)
    for lv, f, m in FIND:
        print('  %-4s %s :: %s' % (lv, f, m))
    print('-' * 64)
    print('第 %d 轮：FAIL %d ｜ WARN %d' % (r, nf, nw))
    return nf, nw, list(FIND)

if __name__ == '__main__':
    hist = []
    for r in range(1, ROUNDS + 1):
        nf, nw, finds = run_round(r)
        hist.append((nf, nw))
    print('=' * 64)
    if ROUNDS > 1:
        print('多轮汇总：' + ' ｜ '.join('R%d FAIL=%d WARN=%d' % (i + 1, a, b) for i, (a, b) in enumerate(hist)))
        if len(set(hist)) == 1:
            print('结论：%d 轮结果完全一致（确定性成立）' % ROUNDS)
        else:
            print('结论：⚠️ 各轮结果不一致，存在非确定性！')
    tot = hist[-1][0]
    print('最终：FAIL %d ｜ WARN %d ｜ %s' % (tot, hist[-1][1], '全部通过' if tot == 0 else '需修复'))
    sys.exit(0 if tot == 0 else 1)
