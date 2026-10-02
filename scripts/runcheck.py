# -*- coding: utf-8 -*-
"""
「启航」三级结构 · 运行性检查器（runcheck）
=========================================
把每个域的「三级结构」**真正跑一遍**：触发词 → 域 → 库内 skill → 输出，逐级确认返回结果可解。

与其余四脚本的分工：
  selfcheck.sh  结构/计数（静态）
  audit.sh      安全/合规/门禁
  regress.sh    澄清门算例 / L3 门禁矩阵（行为）
  aligncheck.py 全量文件级对齐（静态契约）
  runcheck.py   **端到端运行性**：每域多触发词跑完整三级链，校验每级返回结果与最终输出合规格

检查项：
  L1  需求明确 + 域审查 两步已接入（运行前置不可跳）
  L2  注册表路由可解：registry 行在位 / 触发词 ⊆ 域文件 / 每个触发词命中自身 /
      跨域共享词有裁决 / 声明 skill == 实体目录
  L2b 域执行顺序：先判红线前置为第 0 步 / 覆盖全部库内 skill / 接输出规范 / 无库外通道
  L3  逐 skill：归属域 / 前置 / 步骤可跑 / 示例可复现 / **输出形态硬契约**（结论前置 ·
      恰好 1 个【下一步】· ≤6 条 · 有实质字段 · **零内部名泄漏** · 降级标注只写能力级）/
      网址入库 / 红线可拦且与域一致 / **降级目标指名同域真实 skill** / 分工表引用可解析

用法:
  python scripts/runcheck.py .            # 1 轮
  python scripts/runcheck.py . 5          # 5 轮（校验确定性）
  python scripts/runcheck.py . 3 S1 R6    # 只跑指定域

复用适配点（换项目时只改这几处）:
  ① 域目录命名      默认 domains/<域ID>-<slug>/，域 ID 取目录名 '-' 前一段（如 S1）
  ② 触发词位置      默认 domain 文件 `## 触发词` 段；**只取列表行**，`>` 注释行必须排除
  ③ registry 触发词 默认 `_registry.md` 表格第 3 列，是**缩写摘要**（「、」分隔 + 「…」截断）
  ④ 官方站库        默认 references/dlut-official-sites.md（输出 URL 合规校验源）
  ⑤ 输出小节标签    默认 【结论】【依据】【结果】【建议】【下一步】【假设】
                    （口径唯一真相源 = library/output-spec.md §0–§2；改规范必同步本文件
                     的「输出形态硬契约」段 + aligncheck.py 的 O6/T 组 + regress.sh 的 [7] 段）
"""
import os, re, sys, io, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
ROOT = '.'
ROUNDS = 1
ONLY = []
for a in sys.argv[1:]:
    if a.isdigit():
        ROUNDS = max(1, int(a))
    elif os.path.isdir(a) and a not in ('.',):
        ROOT = a
    elif re.match(r'^[A-Za-z]\d$', a):
        ONLY.append(a.upper())
os.chdir(ROOT)

FIND = []
def bad(f, m): FIND.append(('FAIL', f, m))
def warn(f, m): FIND.append(('WARN', f, m))
def rd(p):
    with open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()

DOMS = sorted(d for d in os.listdir('domains') if os.path.isdir(os.path.join('domains', d)))
DEVS = [d.split('-')[0].upper() for d in DOMS]

# ---------- 官方站库（供输出的 URL 合规校验） ----------
SITE_URLS = set()
if os.path.exists('references/dlut-official-sites.md'):
    for m in re.finditer(r'https?://[\w./?=&%#-]+', rd('references/dlut-official-sites.md')):
        u = m.group(0).rstrip('.,)（）、；;')
        if 'dlut.edu.cn' in u:
            SITE_URLS.add(u)
            mm = re.match(r'(https?://[\w.-]+\.dlut\.edu\.cn)/?', u)
            if mm:
                SITE_URLS.add(mm.group(1) + '/')

def url_in_lib(u):
    if u in SITE_URLS:
        return True
    if any(u.startswith(s) for s in SITE_URLS):
        return True
    mm = re.match(r'(https?://[\w.-]+\.dlut\.edu\.cn)', u)
    return bool(mm and any(s.startswith(mm.group(1)) for s in SITE_URLS))

SIG = re.compile(r'^##\s*⚠️\s*红线[^\n]*$', re.M)

def section(text, title_re):
    m = re.search(title_re, text, re.M)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r'^##\s', rest, re.M)
    return rest[:n.start()] if n else rest

def red_lines(text):
    m = SIG.search(text)
    if not m:
        return None
    rest = text[m.end():]
    n = re.search(r'^##\s', rest, re.M)
    body = rest[:n.start()] if n else rest
    return [l.rstrip() for l in body.splitlines() if l.startswith('- ')]

# 触发词列表：只取「列表段落」里的反引号词，**排除** `>` 引用注释（消歧说明）
# 修正点（实测）：F7/R6 的注释里出现 `R6` / `F7` / `_registry.md`，
# 原实现把它们当触发词 → 18 条伪 FAIL。
def trigger_words(text):
    sec = section(text, r'^##\s*触发词[^\n]*$') or ''
    out = []
    for line in sec.splitlines():
        s = line.strip()
        if not s or s.startswith('>') or s.startswith('- ') or s.startswith('|'):
            continue
        out += re.findall(r'`([^`]+)`', s)
    return out

def local_skills(ddir):
    p = '%s/skills/local' % ddir
    if not os.path.isdir(p):
        return []
    return sorted(x for x in os.listdir(p) if os.path.isdir('%s/%s' % (p, x)))


# ---------- 输出形态硬契约：内部名禁止词表 ----------
# 口径唯一真相源 = library/output-spec.md §1.2。**三处必须同源**：
# 本文件的 internal_leaks() / aligncheck.py 的 T 组 / regress.sh 的 [7] 段。
# 违反后果：用户看到的是内部机器名而非「结果与建议」，即违背 output-spec 铁律 2。
ALL_SKILLS = sorted({s for d in DOMS for s in local_skills('domains/%s' % d)})
FILE_INTERNAL = ['output-spec', 'output-checklist', 'general-fallback', 'domain-review-cases',
                 'clarity', 'domain-review', 'memory', 'login-policy', '_registry', '_domain',
                 'SKILL', 'config.yaml', 'dlut-read.sh', 'qihang.sh',
                 'selfcheck.sh', 'audit.sh', 'regress.sh', 'aligncheck.py', 'runcheck.py']
# 注：`README` 不入表 —— 它既是库内文件名，也是学生自己要产出的交付物名
#     （如「→ 产出：env/requirements.txt+README」），入表会误伤合规输出。
PROC_INTERNAL = ['库内 skill', '库外通道', '库外', '域审查', '需求明确', '归属域', '降级承接', '红线']
CODE_RE = re.compile(r'(?<![A-Za-z0-9_])([SFR][1-8])(?![A-Za-z0-9_])')
# 交付物路径 / URL 里的同名片段**不算**泄漏：如「→ 产出：submit/ai-disclosure.md」
# 里的 ai-disclosure 是文件名，用户读到的是「产出了哪个文件」，不是内部机器名。
_FILE_TOKEN = re.compile(r'(?:https?://\S+|[\w./-]+\.(?:md|json|ya?ml|sh|py|html?|csv|'
                         r'xlsx?|pptx?|docx?|txt|pdf|ipynb|js|ts)\b)')


def internal_leaks(o):
    """返回输出块里泄漏的内部名（已剔除路径/URL 里的同名片段）。"""
    s = _FILE_TOKEN.sub(' ▒ ', o)
    out = []
    for nm in ALL_SKILLS + FILE_INTERNAL:
        if re.search(r'(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_-])' % re.escape(nm), s):
            out.append(nm)
    for nm in PROC_INTERNAL:
        if nm in s:
            out.append(nm)
    out += [m.group(1) for m in CODE_RE.finditer(s)]
    return sorted(set(out))


def check_output_block(o):
    """输出形态硬契约（output-spec §0–§2）。返回 (FAIL 列表, WARN 列表)。"""
    F, W = [], []
    labels = re.findall(r'^【([^】]+)】', o, re.M)
    if not labels:
        return ['输出块无【】小节 → 不合输出规范'], []
    if labels[0] != '结论':
        F.append('输出未「结论前置」（首节为【%s】）' % labels[0])
    if len([x for x in labels if '下一步' in x]) != 1:
        F.append('【下一步】应恰好 1 个，实为 %d 个' % len([x for x in labels if '下一步' in x]))
    extra = [x for x in labels if x != '结论']
    if len(extra) > 6:
        F.append('输出要点 %d 条（>6，违 output-spec §1.1）' % len(extra))
    if not any(x in labels for x in ('结果', '网址', '替代方案', '还需确认')):
        F.append('输出无实质内容字段（须有【结果】/校情【网址】/红线【替代方案】/追问【还需确认】）')
    lk = internal_leaks(o)
    if lk:
        F.append('输出块泄漏内部名 %d 处: %s' % (len(lk), '、'.join(lk[:6])))
    if re.search(r'\[已降级\s*[:：]', o):
        F.append('降级标注用旧格式「[已降级: X → Y]」（须写 [已降级] 由「能力」改为「能力」）')
    for mm in re.finditer(r'\[已降级\][^\n]*', o):
        if not re.match(r'\[已降级\]\s*由「[^」]+」改为「[^」]+」', mm.group(0)):
            F.append('降级标注格式不合规: %s' % mm.group(0)[:46])
    return F, W


def run_round(r):
    del FIND[:]
    print('=' * 70)
    print('运行性检查 · 第 %d 轮 ｜ 域 %d ｜ 目标域 %s'
          % (r, len(DOMS), ', '.join(ONLY) if ONLY else '全部'))

    # ---------- 载入 registry ----------
    # 触发词列是**缩写摘要**（用「、」分隔并以「…」截断，不带反引号），
    # 域文件才是**权威全量**（反引号列表）→ 断言只能是 registry ⊆ 域文件，不能要求集合相等。
    reg = rd('domains/_registry.md')
    ROW = {}
    for line in reg.splitlines():
        m = re.match(r'^\|\s*`([A-Za-z]\d)`\s*\|([^|]*)\|([^|]*)\|\s*([^|]+?)\s*\|\s*$', line)
        if m:
            raw = m.group(3).replace('…', '').replace('...', '')
            toks = [x.strip() for x in re.split(r'[、｜|]', raw) if x.strip()]
            ROW[m.group(1).upper()] = {
                'name': m.group(2).strip(),
                'trig': toks,
                'skills': sorted(re.findall(r'`([\w-]+)`', m.group(4))),
            }
    for did in ROW:
        if did not in DEVS:
            bad('domains/_registry.md', 'registry 登记了不存在的域 `%s`' % did)

    # ---------- 全域触发词表（跨域共享判定用，以域文件为权威） ----------
    DMTRIG = {did: trigger_words(rd('domains/%s/_domain.md' % d)) for did, d in zip(DEVS, DOMS)}
    TRIG = collections.defaultdict(set)
    for k, vs in DMTRIG.items():
        for t in vs:
            TRIG[t].add(k)
    dis = reg[reg.find('## 触发词消歧'):] if '## 触发词消歧' in reg else ''

    n_chain = 0
    for did, d in zip(DEVS, DOMS):
        if ONLY and did not in ONLY:
            continue
        ddir = 'domains/%s' % d
        dmf = '%s/_domain.md' % ddir
        dmt = rd(dmf)
        dm_trig = DMTRIG[did]

        # ===== 级别 1：需求明确（澄清门字段可解） =====
        order = section(dmt, r'^##\s*执行顺序[^\n]*$') or ''
        if 'clarity.md' not in order:
            bad(dmf, '执行顺序未接 1 级「需求明确」(library/clarity.md)')
        if 'domain-review.md' not in order:
            bad(dmf, '执行顺序未接 1 级「域审查」(library/domain-review.md)')

        # ===== 级别 2：锁定域（路由可解） =====
        if did not in ROW:
            bad('domains/_registry.md', '%s 未在 registry 登记（路由不可解）' % did)
        else:
            row = ROW[did]
            # L2-1 registry 触发词必须是域文件触发词的子集（registry 是缩写摘要）
            miss = [t for t in row['trig'] if t not in dm_trig]
            if miss:
                bad('domains/_registry.md',
                    '%s 触发词与域文件不一致：registry 多出 %s（registry %d / 域 %d）'
                    % (did, miss, len(row['trig']), len(dm_trig)))
            if len(dm_trig) < 3:
                bad(dmf, '触发词仅 %d 个（路由命中率不足，期望 ≥3）' % len(dm_trig))
            # L2-2 每个触发词必须命中本域；跨域共享词必须有消歧裁决
            for t in dm_trig:
                hits = sorted(TRIG.get(t, set()))
                if did not in hits:
                    bad('domains/_registry.md', '%s 的触发词「%s」未命中自身' % (did, t))
                if len(hits) > 1:
                    if not (t in dis and all(h in dis for h in hits)):
                        warn(dmf, '触发词「%s」被 %s 共享但消歧节未完整登记' % (t, hits))
            n_chain += 1

            # L2-3 声明 skill == 实体目录
            real = local_skills(ddir)
            if not real:
                bad(ddir, '缺 skills/local 目录或为空'); continue
            if row['skills'] != real:
                bad('domains/_registry.md', '%s 声明 skill %s ≠ 实体 %s'
                    % (did, row['skills'], real))

        # ===== 级别 2b：域骨架与执行顺序可跑 =====
        for h in ('## 域边界', '## 触发词', '## 库内 skill', '## DUT 绑定点',
                  '## 执行顺序', '## ⚠️ 红线'):
            if h not in dmt:
                bad(dmf, '缺小节 %s' % h)
        if not re.search(r'0\.\s*\*\*先判红线\*\*', order):
            bad(dmf, '执行顺序未把「先判红线」前置为第 0 步')
        localds = local_skills(ddir)
        for lx in localds:
            if lx not in order:
                bad(dmf, '执行顺序未引用库内 skill `%s`（运行链断）' % lx)
        if 'library/output-spec.md' not in order:
            bad(dmf, '执行顺序未接输出规范 library/output-spec.md')
        if '库外' in order or 'external.md' in order:
            bad(dmf, '执行顺序仍含库外通道（应为库内唯一）')

        # ===== 级别 3：逐 skill 跑 =====
        d_red = red_lines(dmt) or []
        for sd in localds:
            sp = '%s/skills/local/%s/SKILL.md' % (ddir, sd)
            if not os.path.exists(sp):
                bad(sp, 'SKILL.md 缺失'); continue
            st = rd(sp)

            # L3-1 归属域可解
            m = re.search(r'归属域\*\*[：:]\s*`?([A-Za-z]\d)`?', st)
            if not m:
                bad(sp, '缺「归属域」→ 锁定域不可解')
            elif m.group(1).upper() != did:
                bad(sp, '归属域写 %s，实际属 %s' % (m.group(1), did))

            # L3-2 前置声明 1 级两步已过（运行前置不可跳）
            pre = section(st, r'^##\s*前置[^\n]*$') or ''
            if '需求明确' not in pre and 'clarity' not in pre:
                bad(sp, '前置未声明「需求明确」已完成')
            if '域审查' not in pre and 'domain-review' not in pre:
                bad(sp, '前置未声明「域审查」已完成')

            # L3-3 执行步骤可跑
            steps = section(st, r'^##\s*执行步骤[^\n]*$') or ''
            items = [x.strip() for x in re.findall(r'^\s*\d+\.\s*(.+)$', steps, re.M)]
            if len(items) < 3:
                bad(sp, '执行步骤仅 %d 步（运行链过短，期望 ≥3）' % len(items))
            for it in items:
                if len(it) < 5:
                    bad(sp, '步骤过短不可执行: %r' % it)

            # L3-4 可执行示例（输入 / 澄清判定）
            mi = re.search(r'\*\*输入\*\*\s*\n\s*\n\s*>?\s*(.+)', st)
            if not mi:
                bad(sp, '示例缺「输入」→ 无法复现运行')
            elif len(mi.group(1).strip()) < 5:
                bad(sp, '示例输入过短不可复现: %r' % mi.group(1)[:30])
            mc = re.search(r'\*\*澄清判定\*\*[：:]\s*(.+)', st)
            if not mc:
                bad(sp, '示例缺「澄清判定」→ 级别1 结论不可解')
            else:
                verdict = mc.group(1)
                if not re.search(r'放行|追问', verdict):
                    bad(sp, '澄清判定未给结论（放行/追问）: %r' % verdict[:40])
                mu = re.search(r'U\s*[=≤<]\s*([\d.]+)', verdict)
                if mu and not re.search(r'例外|追问|问后|/\s*6\.1', verdict):
                    warn(sp, '澄清判定给 U=%s 但未附依据' % mu.group(1))

            # L3-5 输出形态硬契约（口径真相源 = library/output-spec.md §0–§2）
            ob = re.search(r'\*\*输出\*\*\s*\n\s*\n\s*```\s*\n(.*?)```', st, re.S)
            if not ob:
                bad(sp, '示例缺「输出」代码块 → 级别3 返回结果为空')
            else:
                o = ob.group(1)
                for _m in check_output_block(o)[0]:
                    bad(sp, _m)
                # L3-6 输出里的 dlut URL 必须已在官方站库登记
                for u in re.findall(r'https?://[\w./?=&%#-]+', o):
                    u2 = u.rstrip('.,)（）、；;')
                    if 'dlut.edu.cn' in u2 and not url_in_lib(u2):
                        bad(sp, '输出引用了未入库的 DUT 网址: %s' % u2)

            # L3-7 红线可拦 + 与域一致
            red = red_lines(st) or []
            if not red:
                bad(sp, '红线段缺失/为空 → 拦不住')
            elif not any(re.search(r'不|禁|须|拒绝|不得', l) for l in red):
                bad(sp, '红线条目无禁止语（形同虚设）')
            if d_red and red != d_red:
                bad(sp, '红线与域文件不一致（域 %d 条 / skill %d 条）' % (len(d_red), len(red)))

            # L3-8 失败与降级：降级目标必须**指名**同域另一真实 skill
            # 三个可指名的位置都要校验，缺一不可：① 「`X` 降级承接」的承接目标；
            # ② 「[已降级: 本 → X]」的箭头目标。任一指向非本域真实 skill → 运行链断。
            # （实测踩过：只做「段内存在某个合法 skill 名」的宽松判定，
            #   把承接目标改成不存在的名字时仍会通过 —— 因为箭头注释里还留着合法名。）
            fb = section(st, r'^##\s*失败与降级[^\n]*$') or ''
            if '库外' in fb or 'external.md' in fb:
                bad(sp, '失败与降级仍指向库外通道')
            if len(localds) > 1:
                tgt = []
                m3 = re.search(r'`([\w-]+)`\s*降级承接', fb)
                if m3:
                    tgt.append(m3.group(1))
                for m2 in re.finditer(r'\[已降级[:：][^\]]*?→\s*`?([\w-]+)`?\s*\]', fb):
                    tgt.append(m2.group(1))
                if not tgt:
                    tgt = [x for x in re.findall(r'`([\w-]+)`', fb) if x in localds]
                badt = sorted(set(x for x in tgt if x not in localds or x == sd))
                if not tgt:
                    bad(sp, '失败与降级未指定同域降级目标（无法降级运行）')
                elif badt:
                    bad(sp, '失败与降级目标 `%s` 不是本域其他真实 skill（无法降级运行）'
                        % '`/`'.join(badt))

            # L3-9 分工表：同域/跨域引用可解析
            duty = section(st, r'^##\s*与同域其他库内 skill 的分工[^\n]*$') or ''
            for ref in re.findall(r'`([\w-]+)`', duty):
                if ref in localds or ref == sd:
                    continue
                if re.search(r'`[A-Za-z]\d`[^\n|]*`%s`' % re.escape(ref), duty):
                    continue
            for did_ref in re.findall(r'`([A-Za-z]\d)`', duty):
                if did_ref.upper() not in ROW:
                    bad(sp, '分工表引用了不存在的域 `%s`' % did_ref)

            # L3-10 降级标注写法存在
            if '[已降级' not in st:
                warn(sp, '未声明 [已降级] 标注（降级时输出不合规）')

    nf = sum(1 for x in FIND if x[0] == 'FAIL')
    nw = sum(1 for x in FIND if x[0] == 'WARN')
    print('  运行链解得域数: %d ｜ 检查项失败: %d' % (n_chain, nf))
    print('-' * 70)
    for lv, f, m in FIND:
        print('  %-4s %s :: %s' % (lv, f, m))
    print('-' * 70)
    print('第 %d 轮：FAIL %d ｜ WARN %d' % (r, nf, nw))
    return nf, nw, list(FIND)


if __name__ == '__main__':
    hist = []
    for r in range(1, ROUNDS + 1):
        nf, nw, _ = run_round(r)
        hist.append((nf, nw))
    print('=' * 70)
    if ROUNDS > 1:
        print('多轮汇总：' + ' ｜ '.join('R%d FAIL=%d WARN=%d' % (i + 1, a, b)
                                        for i, (a, b) in enumerate(hist)))
        print('结论：%s' % ('%d 轮结果完全一致（确定性成立）' % ROUNDS
                          if len(set(hist)) == 1 else '⚠️ 各轮结果不一致，存在非确定性！'))
    tot = hist[-1][0]
    print('最终：FAIL %d ｜ WARN %d ｜ %s'
          % (tot, hist[-1][1], '运行链全部可解' if tot == 0 else '存在不可解运行链'))
    sys.exit(0 if tot == 0 else 1)
