#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""负向自测：把「断言是否真的会 FAIL」变成可重复验证（防断言静默空转）。

为什么要有它：自检全绿只证明「断言集通过」，不证明「断言集有效」。开发期多次出现
「注入缺陷后校验器毫无反应」（断言恒真）= 最危险的一类错。本脚本把多类注入固化成常驻测试。

在**临时树**上跑（按交付口径复制：排除 .git / _build / .learnbuddy / __pycache__ / .idea），
逐类注入 → 跑对应校验器 → 断言**必须 FAIL** → 打印捕获率。真实树**只读**，不写任何文件。

用法：python scripts/negative_test.py [源树] [--with-regress]
判据：捕获率 100% → rc 0；否则 rc 1。
"""
import os, re, sys, io, shutil, tempfile, subprocess

# ⚠️ 实测坑（Windows）：默认 stdout 编码是 GBK，打印 ✅/❌ 直接 UnicodeEncodeError 崩掉
# （rc=1，且崩在结果行，看起来像「负向自测失败」）。与 checkall.py 同一口径强制 UTF-8。
for _s in ('stdout', 'stderr'):
    _f = getattr(sys, _s, None)
    if hasattr(_f, 'reconfigure'):
        _f.reconfigure(encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
SRC = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..'))
WITH_REGRESS = '--with-regress' in sys.argv
PY = sys.executable or 'python'
IGNORE = shutil.ignore_patterns('.git', '_build', '.learnbuddy', '__pycache__', '.idea')


def bash_bin():
    for c in (os.environ.get('BASH'), os.environ.get('EXEPATH'),
              r'C:\Program Files\Git\bin\bash.exe',
              r'C:\Program Files (x86)\Git\bin\bash.exe',
              r'C:\Program Files\Git\usr\bin\bash.exe'):
        if c and os.path.isfile(c):
            return c
    w = shutil.which('bash')
    return w if (w and 'system32' not in w.lower()) else None


BASH = bash_bin()


def run(tree, cmd):
    # ⚠️ 在 Python 里直接调 `bash` 会落到 WSL（System32\bash.exe）→ 秒退零输出。
    env = dict(os.environ)
    env['PYTHONIOENCODING'] = 'utf-8'
    argv = list(cmd)
    if argv[0] == '@bash':
        argv = ([BASH] + argv[1:]) if BASH else None
    elif argv[0] == '@py':
        argv = [PY] + argv[1:]
    if argv is None:
        return 127, '（未找到 Git Bash —— 环境项，跳过该用例）'
    r = subprocess.run(argv, cwd=tree, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    return r.returncode, r.stdout.decode('utf-8', 'replace')


def first_skill(tree):
    base = os.path.join(tree, 'domains')
    for d in sorted(os.listdir(base)):
        loc = os.path.join(base, d, 'skills', 'local')
        if not os.path.isdir(loc):
            continue
        for s in sorted(os.listdir(loc)):
            p = os.path.join(loc, s, 'SKILL.md')
            if os.path.isfile(p):
                return p
    return None


def inject_redline(tree):
    p = first_skill(tree)
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'(## ⚠️ 红线[^\n]*\n)(.*?)(?=\n## )', t, re.S)
    return [p], t[:m.end(2)] + '\n- **负向测试注入**：本条为注入项，不属于域红线' + t[m.end(2):]


def inject_fake_fallback(tree):
    p = first_skill(tree)
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(用同域库内 `)[a-z0-9-]+(` 降级承接)', r'\1no-such-skill-xyz\2', t)


def inject_three_digit_display(tree):
    p = os.path.join(tree, 'README.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(学伴包 v)(\d+\.\d+)(\s|$)', r'\1\2.9\3', t, count=1)


def inject_dup_row(tree):
    p = os.path.join(tree, 'SKILL.md')
    t = io.open(p, encoding='utf-8').read()
    row = '| `library/skill-evolution.md` |'
    for ln in t.splitlines():
        if ln.startswith(row):
            return [p], t.replace(ln, ln + '\n' + ln, 1)
    return [p], t


def inject_duplicate_step_number(tree):
    """把 S1 的 `0. **先判红线**` 再补一行 —— 复现曾长期存活的真实缺陷。

    与 inject_dup_row 的差别：那条注入的是**表格行**（B 组「连续重复行」能抓）；
    这条注入的第二行措辞与首行**不同**（真实缺陷就是这样：两行都编号 0 但文字不一），
    所以 B 组抓不到，只有 F 组的步骤号结构断言能抓
    （「先判红线」断言用 re.search，存在即过，对重复行完全无感）。
    """
    p = os.path.join(tree, 'domains', 'S1-course-qa', '_domain.md')
    t = io.open(p, encoding='utf-8').read()
    for ln in t.splitlines():
        if re.match(r'^0\.\s*\*\*先判红线\*\*', ln):
            return [p], t.replace(ln, ln + '\n0. **先判红线**（重复插入的第二步）', 1)
    return [p], t


def inject_build_path(tree):
    p = os.path.join(tree, 'library', 'skill-evolution.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t + '\n> 负向测试注入：生成器见 scripts/_build/v3/rebuild.py（本行应触发失效引用）\n'


def inject_no_isolation(tree):
    """移除一次性 Profile 创建，模拟固定 / 持久化 Profile 回归。
    期望：selfcheck [7c] 断言 FAIL（证明该断言不是装饰）。"""
    p = os.path.join(tree, 'scripts', 'dlut-read.sh')
    t = io.open(p, encoding='utf-8').read()
    out, skipping = [], False
    for ln in t.split('\n'):
        if 'PROFILE_DIR="$(mktemp -d' in ln:
            continue
        out.append(ln)
    return [p], '\n'.join(out)


def inject_no_gate(tree):
    """把 SKILL.md 的触发门整段删掉 → selfcheck [8d] 应 FAIL（防触发门被静默移除）。"""
    p = os.path.join(tree, 'SKILL.md')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('## 触发门与接管边界', '## （已移除）', 1)
    return [p], t


def inject_missing_course_gate_marker(tree):
    """Drop one course marker from the gate; runcheck must detect the broken route chain."""
    p = os.path.join(tree, 'config.yaml')
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'^(  learning_markers:\s*\[)(.*?)(\])\s*$', t, re.M)
    if not m:
        return [p], t
    words = [x.strip() for x in m.group(2).split(',')]
    if '整门课' not in words:
        return [p], t
    words.remove('整门课')
    return [p], t[:m.start()] + m.group(1) + ', '.join(words) + m.group(3) + t[m.end():]


def inject_missing_learning_detail_contract(tree):
    """Remove the learning-detail standard; runcheck must reject the short-answer regression."""
    p = os.path.join(tree, 'library', 'output-spec.md')
    t = io.open(p, encoding='utf-8').read()
    start = t.find('### 1.3.1 学习内容详细模式')
    end = t.find('\n## 2. 变体', start)
    if start < 0 or end < 0:
        return [p], t
    return [p], t[:start] + t[end:]


def inject_identity_lock(tree):
    """Reintroduce a forced persona declaration; selfcheck [8c] must reject it."""
    p = os.path.join(tree, 'INSTALL.md')
    t = io.open(p, encoding='utf-8').read()
    declaration = '我是连小理' + '智能学伴『启航』'
    t = t.replace('## 七、安装后行为约定', '## 七、安装后行为约定\n\n' + declaration, 1)
    return [p], t


def inject_fake_platform(tree):
    """把某域「指定检索平台」改成不存在的平台 → extskill 应 FAIL（防编造平台）。"""
    p = os.path.join(tree, 'domains', 'S4-exam-prep', '_domain.md')
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'(?ms)^##\s*外部承接[^\n]*\n(.*?)(?=^##\s|\Z)', t)
    if not m:
        return [p], t
    body = m.group(1)
    changed, n = re.subn(
        r'(?m)^(\*\*指定检索平台[^\n]*：).*?$',
        r'\1 `no-such-platform.example` ｜ `also-fake.example`（共 2 个）',
        body, count=1)
    if not n:
        return [p], t
    return [p], t[:m.start(1)] + changed + t[m.end(1):]


def inject_bridge_broken(tree):
    """把某个 3 级 skill 的降级段改回「两档」（去掉外部桥接）→ extskill 应 FAIL。"""
    import glob as _g
    for p in sorted(_g.glob(os.path.join(tree, 'domains/*/skills/local/*/SKILL.md'))):
        t = io.open(p, encoding='utf-8').read()
        m = re.search(r'(?ms)^##\s*失败与降级[^\n]*\n(.*?)(?=^##\s|\Z)', t)
        if not m or 'library/external-bridge.md' not in m.group(1):
            continue
        body = m.group(1)
        if '纯提示词模式' not in body:
            continue
        broken = body.replace('纯提示词模式', '自生成模式', 1)
        return [p], t[:m.start(1)] + broken + t[m.end(1):]
    p = sorted(_g.glob(os.path.join(tree, 'domains/*/skills/local/*/SKILL.md')))[0]
    return [p], io.open(p, encoding='utf-8').read()


def inject_url_boundary(tree):
    """把一条 URL 与紧随其后的中文说明贴在一起（模拟「依据里的链接被渲染器吞掉」）。
    期望：aligncheck 的 URL 边界断言 FAIL。"""
    p = os.path.join(tree, 'domains', 'F4-money-safety', '_domain.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t + '\n- 负向测试注入：https://www.dlut.edu.cn/（URL 紧贴中文，应触发 URL 边界断言）\n'


def inject_missing_fallback(tree):
    p = os.path.join(tree, 'library', 'general-fallback.md')
    return [p], None        # 特殊：移走文件


def inject_stale_file_count(tree):
    """把 README 的「交付树 N 个文件」改成过期数字 → aligncheck Q 组应 FAIL。"""
    p = os.path.join(tree, 'README.md')
    t = io.open(p, encoding='utf-8').read()
    m = re.search(r'(交付树[^\n]{0,14}?)(\d{2,4})(\s*个文件)', t)
    if not m:
        return [p], t
    return [p], t[:m.start(2)] + str(int(m.group(2)) - 3) + t[m.end(2):]


def inject_stale_platform_count(tree):
    """把 `domains/_registry.md` 的平台目录数改回旧口径 12 → aligncheck 应 FAIL。"""
    p = os.path.join(tree, 'domains', '_registry.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'\d{1,3}(\s*个平台目录)', r'12\1', t, count=1)


def inject_gate_list_short(tree):
    """把 qihang.sh status 的 1 级清单删掉一项 → aligncheck 应 FAIL（防清单静默漏列）。"""
    p = os.path.join(tree, 'scripts', 'qihang.sh')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('library/external-bridge.md ', '', 1)


def inject_marker_word_dropped(tree):
    """从 learning_markers 里删一个域触发词 → aligncheck 应 FAIL（词表同源铁律）。"""
    p = os.path.join(tree, 'config.yaml')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(, 作文批改)(\])', r'\2', t, count=1)


def inject_platform_line_removed(tree):
    """删掉某域「指定检索平台」行 → extskill 覆盖率断言应 FAIL（防域被静默跳过）。"""
    p = os.path.join(tree, 'domains', 'R3-research-tools', '_domain.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(?m)^\*\*指定检索平台[^\n]*\n', '', t, count=1)


def inject_exempt_decl_removed(tree):
    """删掉 external-sources.md §一 的「例外」声明 → extskill 应 FAIL（豁免不可无声明放行）。"""
    p = os.path.join(tree, 'references', 'external-sources.md')
    t = io.open(p, encoding='utf-8').read()
    lines = [l for l in t.split('\n')
             if not (l.lstrip().startswith('>') and '例外' in l)]
    return [p], '\n'.join(lines)


def inject_url_count_drift(tree):
    """把 §11.2 的「唯一外链」改成旧值 138 → aligncheck 应 FAIL（外链计数不可漂移）。"""
    p = os.path.join(tree, 'references', 'dlut-url-verification.md')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('唯一外链 148 条', '唯一外链 138 条', 1)
    return [p], t


def inject_cross_file_url_count_drift(tree):
    """把引用方的「148 条外链」改成旧值 138 → aligncheck 应 FAIL（引用方不可漂移）。

    与 inject_url_count_drift 是同一根因的两半：那条改的是**本源文件**的声明，
    这条改的是**引用方**（official-sites.md）转述的数字。原断言只扫本源文件，
    所以引用方写旧值能长期存活。
    """
    p = os.path.join(tree, 'references', 'dlut-official-sites.md')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('148 条外链', '138 条外链', 1)
    return [p], t


def inject_delivery_line_wording_drift(tree):
    """把某 skill 的标准交付校验句退回旧措辞「7 项校验」→ aligncheck 应 FAIL（模板句措辞唯一）。"""
    p = first_skill(tree)
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('` 的 7 项硬校验。', '` 的 7 项校验。', 1)


def inject_section_ref_dotted_drift(tree):
    """把 `output-spec.md` §2.1 改成不存在的 §2.9 → aligncheck 应 FAIL（节号引用须含子节号）。"""
    p = os.path.join(tree, 'library', 'output-checklist.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('`output-spec.md` §2.1', '`output-spec.md` §2.9', 1)


def _first_selfbuilt_skill(tree):
    import glob as _g
    for p in sorted(_g.glob(os.path.join(tree, 'domains/*/skills/local/*/SKILL.md'))):
        if '- **来源**：自建\n' in io.open(p, encoding='utf-8').read():
            return p
    return None


def inject_source_label_hybrid(tree):
    """把某 skill 的「**来源**：自建」退回 v2 混血标签「摘录+自建」→ aligncheck D2 应 FAIL。
    历史缺陷：`lecture-to-notes` / `exam-sprint` 曾长期如此，且 6 个校验器全绿。"""
    p = _first_selfbuilt_skill(tree)
    if not p:
        return [first_skill(tree)], io.open(first_skill(tree), encoding='utf-8').read()
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('- **来源**：自建\n', '- **来源**：摘录+自建\n', 1)


def inject_source_repo_unregistered(tree):
    """把某 skill 的来源标签点名一个未登记仓库 → aligncheck D2 应 FAIL（台账交叉核对非空转）。"""
    p = _first_selfbuilt_skill(tree)
    if not p:
        return [first_skill(tree)], io.open(first_skill(tree), encoding='utf-8').read()
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace(
        '- **来源**：自建\n',
        '- **来源**：改造自 `evilcorp/no-such-repo`（MIT）· 骨架提取重写 + DUT 特化\n', 1)


def inject_domain_source_label_drift(tree):
    """只改 `_domain.md` 一侧的括注（SKILL.md 仍为「自建」）→ aligncheck D2 应 FAIL（两处须同源）。"""
    import glob as _g
    for p in sorted(_g.glob(os.path.join(tree, 'domains/*/_domain.md'))):
        t = io.open(p, encoding='utf-8').read()
        if '（自建）' in t:
            return [p], t.replace('（自建）', '（摘录+自建）', 1)
    p = sorted(_g.glob(os.path.join(tree, 'domains/*/_domain.md')))[0]
    return [p], io.open(p, encoding='utf-8').read()


def inject_oos_overlap(tree):
    """把裸词「基金」塞回 `out_of_scope_markers` → aligncheck U 应 FAIL。

    这是本仓真实发布过的路由缺陷：越界表声明「优先级最高，压过宽词表」，
    而「基金」同时是 R4 的合法触发词 → 越界硬停吞掉 R4 的 grant-apply，使其永不可达。
    """
    p = os.path.join(tree, 'config.yaml')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(out_of_scope_markers:\s*\[)', r'\g<1>基金, ', t, count=1)


def inject_oos_skill_md_skew(tree):
    """只在 SKILL.md §1.5 内联列举里加一个越界词（config.yaml 不动）→ aligncheck U 应 FAIL（两处须同步）。"""
    p = os.path.join(tree, 'SKILL.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], re.sub(r'(股票 / 彩票 / )', r'\g<1>刷剧 / ', t, count=1)


def inject_experience_pointer_removed(tree):
    """删掉 output-spec.md 的一处前台渲染口径指针 → aligncheck X 组应 FAIL。"""
    p = os.path.join(tree, 'library', 'output-spec.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('`library/experience.md`', '`experience.md`', 1)


def inject_restate_no_ambiguity(tree):
    """B2 回归：复述档退回「档位驱动」，删掉实质歧义判据。"""
    p = os.path.join(tree, 'library', 'clarity.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('实质歧义', '档位条件')


def inject_memory_no_fixed_reply(tree):
    """B3 回归：§3.2 续接固定回话被改写（唯一副本失效）。"""
    p = os.path.join(tree, 'library', 'memory.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('不得假称记得', '尽量不要说得太肯定')


def inject_login_no_handback(tree):
    """C2 回归：登录后不再交还（删掉交还三步与固定一句话）。"""
    p = os.path.join(tree, 'library', 'login-policy.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('交还三步', '权限说明').replace(
        '不想登录也告诉我，我给通用流程', '需重新授权后继续')


def inject_oos_priority_supreme(tree):
    """C1 回归：越界表改回「优先级最高」（单词命中即终判）。"""
    p = os.path.join(tree, 'config.yaml')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('arbitration:', 'x_arbitration:')
    return [p], t.replace('命中只做初筛，归属由下面的仲裁顺序定',
                          '命中即不接管（优先级最高，压过宽词表）')


def inject_experience_no_metrics(tree):
    """C3 回归：§7 体验层自检指标被删除（体验层重新退化为零指标层）。"""
    p = os.path.join(tree, 'library', 'experience.md')
    t = io.open(p, encoding='utf-8').read()
    i = t.find('## 7. 体验层自检指标')
    return [p], (t[:i] if i >= 0 else t)


def inject_entry_phrase_drift(tree):
    """改掉 README.md 的一个起始句型（与唯一副本分叉）→ aligncheck X 组应 FAIL。"""
    p = os.path.join(tree, 'README.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('「安排一周备考计划」', '「给我排一个复习节奏」', 1)


def main():
    base = os.path.join(tempfile.gettempdir(), 'qihang_negtest_%d' % int(__import__('time').time()))
    shutil.copytree(SRC, base, ignore=IGNORE)
    print('负向自测 · 临时树：%s' % base)
    print('=' * 76)
    cases = [
        ('同域红线漂移（注入一条不属于域红线的红线）', inject_redline,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('伪降级目标（no-such-skill-xyz）', inject_fake_fallback,
         ['@py', 'scripts/runcheck.py', '.'], 'runcheck'),
        ('包版本展示位写成三位', inject_three_digit_display,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('生成器段重复插入（同一行两份）', inject_dup_row,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('执行顺序步骤号重复（S1 再补一行 `0. 先判红线`）', inject_duplicate_step_number,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck F 步骤号'),
        ('URL 紧贴中文（依据里的链接会被渲染器吞掉）', inject_url_boundary,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck F2'),
        ('外部桥接接线被破坏（降级段退回两档）', inject_bridge_broken,
         ['@py', 'scripts/extskill.py', '.'], 'extskill 三档断言'),
        ('指定检索平台被改成不存在的平台', inject_fake_platform,
         ['@py', 'scripts/extskill.py', '.'], 'extskill 平台登记断言'),
        ('身份声明回归', inject_identity_lock,
         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8c] 身份声明删除'),
        ('触发门被移除（SKILL.md 少了触发门小节）', inject_no_gate,
         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8d] 触发门'),
        ('整门课词未进入触发门', inject_missing_course_gate_marker,
         ['@py', 'scripts/runcheck.py', '.'], 'runcheck 课程路由完整性'),
        ('学习详度规则被移除', inject_missing_learning_detail_contract,
         ['@py', 'scripts/runcheck.py', '.'], 'runcheck 学习内容完整性'),
        ('隔离校验缺失（--profile 可被 daemon 静默忽略）', inject_no_isolation,
         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [7c]'),
        ('规则文件引用生成器路径（副本必判失效引用）', inject_build_path,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),
        ('交付树文件数声明过期（173 vs 176）', inject_stale_file_count,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 交付树文件数'),
        ('平台目录数退回旧口径 12', inject_stale_platform_count,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 平台数'),
        ('status 1 级清单漏列 library 文件', inject_gate_list_short,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 1 级清单'),
        ('learning_markers 漏掉域触发词', inject_marker_word_dropped,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 词表同源'),
        ('某域「指定检索平台」行被删', inject_platform_line_removed,
         ['@py', 'scripts/extskill.py', '.'], 'extskill 平台覆盖率'),
        ('豁免声明被删（R6 无声明放行）', inject_exempt_decl_removed,
         ['@py', 'scripts/extskill.py', '.'], 'extskill 豁免白名单'),
        ('外链计数漂移（148 条被改回 138 条）', inject_url_count_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 外链计数'),
        ('跨文件引用过期（引用方 148 条外链改回 138）', inject_cross_file_url_count_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 外链引用'),
        ('模板交付句措辞漂移（硬校验 → 校验）', inject_delivery_line_wording_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 模板句唯一'),
        ('子节号引用漂移（output-spec §2.1 → §2.9）', inject_section_ref_dotted_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck 节号引用'),
        ('来源标签退回混血口径（自建 → 摘录+自建）', inject_source_label_hybrid,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck D2 来源口径'),
        ('来源点名未登记仓库（evilcorp/no-such-repo）', inject_source_repo_unregistered,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck D2 台账交叉核对'),
        ('仅 _domain.md 一侧改括注（与 SKILL.md 不同源）', inject_domain_source_label_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck D2 两处同源'),
        ('越界表与接管词表冲突（「基金」塞回越界表）', inject_oos_overlap,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck U 越界表互斥'),
        ('SKILL.md §1.5 越界词与 config 不同步', inject_oos_skill_md_skew,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck U 越界表同步'),
        ('前台渲染口径指针被删（契约层不再顺链到呈现层）', inject_experience_pointer_removed,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck X 呈现层指针'),
        ('入口文案分叉（README 起始句型与唯一副本不一致）', inject_entry_phrase_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck X 起始句型唯一副本'),
        ('澄清门复述档失去歧义判据（B2）', inject_restate_no_ambiguity,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 澄清门实质歧义'),
        ('续接固定回话被改写（B3）', inject_memory_no_fixed_reply,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 记忆口径单源'),
        ('登录后不再交还（C2）', inject_login_no_handback,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 登录交还三步'),
        ('越界表改回优先级最高（C1）', inject_oos_priority_supreme,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 越界仲裁顺序'),
        ('体验层自检指标被删除（C3）', inject_experience_no_metrics,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 体验层自检指标'),
    ]
    if WITH_REGRESS:
        cases.append(('移走零命中兜底框架', inject_missing_fallback,
                      ['@bash', 'scripts/regress.sh', '1'], 'regress [5]'))

    caught = 0
    for name, fn, cmd, which in cases:
        paths, newt = fn(base)
        backups = {}
        for p in paths:
            if os.path.isfile(p):
                backups[p] = io.open(p, 'rb').read()
        if newt is None:
            shutil.move(paths[0], paths[0] + '.moved')
        else:
            for p in paths:
                io.open(p, 'w', encoding='utf-8', newline='').write(newt)
        rc, out = run(base, cmd)
        hit = (rc != 0) or ('FAIL' in out and 'FAIL 0' not in out)
        print('%-46s → %-12s %s' % (name, which, '✅ 捕获' if hit else '❌ 漏网（断言可能空转）'))
        if hit:
            caught += 1
        # 还原
        for p, b in backups.items():
            io.open(p, 'wb').write(b)
        if newt is None and os.path.exists(paths[0] + '.moved'):
            shutil.move(paths[0] + '.moved', paths[0])
    print('=' * 76)
    print('捕获率 %d/%d' % (caught, len(cases)))
    print('结论：%s' % ('✅ 断言非空转' if caught == len(cases) else '❌ 存在空转断言，须修断言'))
    sys.exit(0 if caught == len(cases) else 1)


if __name__ == '__main__':
    main()
