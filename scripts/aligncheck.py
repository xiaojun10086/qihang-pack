#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」全量对齐审计（aligncheck）
==================================

用途：**打开每一个文件**做机器可判定的一致性检查，用于「对齐 + 可行性验证」。
与其余四个脚本的分工：
  selfcheck.sh   结构/计数（bash，轻量）
  audit.sh       安全/合规/门禁（bash）
  regress.sh     行为回归（bash，澄清门算例与 L3 门禁矩阵）
  aligncheck.py  **全量文件级对齐 + skill 可行性契约**（本脚本，Python）
  runcheck.py    静态路由、skill 文档、示例与输出契约检查（不调用目标平台）

用法:
  python scripts/aligncheck.py .            # 单轮
  python scripts/aligncheck.py . 5          # 连跑 5 轮（校验确定性）

检查项（21 组：A–D、F–Q、S–U、X、Y）：
  A 文件清单 / 可读性 / 空文件 / 编码 / BOM / 行尾
  B **重复内容检测**（连续重复行、重复小节、重复表格行 —— 抓生成器重复插入）
  C config.yaml：YAML 结构、列表无重复项、阈值与权重与文档一致
  D SKILL.md 契约：frontmatter / 归属域 / 必需小节 / 步骤数 / 示例三要素 / 输出字段 /
    输出段须含库内规范引用 + 标准交付校验句（措辞唯一）
  D2 来源标签 ↔ 第三方台账：`**来源**` 口径唯一（自建系 / 改造自 / 方法论思路参考）；
    点名 `owner/repo` ⇒ 须逐条登记于 THIRD_PARTY_NOTICES.md §三（恰好 12 条）；
    `_domain.md` 括注与 SKILL.md 的自建/外部归属须一致
  F _domain.md 契约：必需小节 / 库内 skill 实体存在 / 「不覆盖→X域」指向存在 /
    执行顺序步骤号 0 起连续无重复
  G 交叉引用：文档里写的路径真实存在；节号引用 `X.md` §N(.M) 须落在目标真实编号内
  H 计数与版本：registry 声明 skill 数 == 实体、版本号全域唯一（含插件清单）
  I commands/*.md：入口可用、引用路径存在
  J .codebuddy-plugin/plugin.json：JSON 合法、版本一致
  K HTML：主要标签配平、引用的文档存在
  L 澄清门算例：文档中出现的 U 值可复算；L2 示例「澄清判定」的 U 断言须附依据；
    L3 阈值不得被当作**唯一**放行条件（须引 §5 例外 / 阈值真相源 / 「追问 N 问后」）
  M 红线一致性：域 ↔ 库内 skill 逐条（含顺序）
  N 无临时/备份残留文件
  O 库内 skill 可行性（O1–O9）：必需小节 / 步骤可执行 / 示例可复现 / 输出合规格 /
    O7 标题跨域唯一 · O8 同域定位不相似 · O9 目录名跨域唯一
  P 三级路由链可解：触发词数 / 执行顺序覆盖库内 skill、输出规范（库内唯一通道）
  Q 文档声明数 == 实测数：表格行 / 条目 / ✅⚠️ 分项 / §8 项数 / 文件总数
  S 小节正文非空（空壳标题）：正文完全为空 → FAIL；仅 <8 字 → WARN
  T **输出形态硬契约**：全量输出块零内部名（域代号 / skill 名 / 脚本与库文件名 / 流程词 /
    「红线」）/ 结论前置 / 恰好 1 个【下一步】/ 降级标注只写能力级
  U 触发门越界表不变式：`out_of_scope_markers` 与接管词表（`learning_markers` / `dlut_markers` /
    `learning_intents`）**零交集** / 表内无互为子串的冗余项 / SKILL.md §1.5 内联列举 ⊆ 越界表 /
    「需求主键」「优先级最高」双处声明
  X 学生呈现层：`library/experience.md` 在位（白名单 / 禁止物 / 翻译规则 / 三视图 / 反例 / 起始句型）·
    1 级清单三处同步 · 输出契约两处指针在位 · 四处入口文案与唯一副本逐条一致 · 组数声明同源
  Y 体验层闭环：澄清门实质歧义驱动（免白复述）· 记忆口径单源（续接固定回话）· 越界仲裁顺序（初筛→终判）·
    登录交还三步（交还优先于权限叙事）· 体验层自检指标表（零用户数据 / 默认不记录）
"""
import os, re, sys, json, glob, io, hashlib, collections, subprocess

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

# 库内 skill「## 输出」段的标准交付校验句 —— **唯一权威表述**。
# 真相源：`library/output-spec.md` §4「交付前校验（强制）」+ `library/output-checklist.md` §一。
# 为什么断言：曾出现「7 项校验」与「7 项硬校验」两版并存（48 / 44 分裂）而全部校验器仍为绿 ——
# 模板句措辞漂移属校验盲区，只能靠精确断言兜住。
CANON_DELIVERY_LINE = '交付前须过 `library/output-checklist.md` 的 7 项硬校验。'

# ---------- 版本号：**单一真相源 = config.yaml**（v3.2.5 起，勿再写死字面量）----------
# 为什么改：修订号字面量曾硬编码在 101 个文件 / 120 处，其中本文件 10 处；
# 两次迭代各因「同一字面量多处出现、只换首处」而报出自相矛盾的 FAIL。
# 现在改版本只需改 config.yaml 一处 + 生成器全量替换，断言强度不变。
_cv = re.search(r'^version:\s*([\d.]+)', rd('config.yaml'), re.M) if os.path.isfile('config.yaml') else None
REV = _cv.group(1) if _cv else ''      # 修订号（三位，用于字段与断言）
PKG = '.'.join(REV.split('.')[:2])          # 包版本（两位，用于展示位）

# 评审 / 审计 / 验收 / 需求书等过程文档不属交付物，统计时应一并排除。
DEV_ONLY_DOCS = {
    'validation-report.md', 'acceptance-v2.md',
    'review-report-v2.2.md', 'review-report-v2.3.md', 'review-report-v2.4.md',
    'stress-test-v3.md', 'alignment-audit-v3.md', '需求确认书-v2三级结构.md',
}
# 开发侧版本控制元数据：release 树里没有（`.gitattributes` 有，故不在此列）。
DELIV_EXCLUDE_FILES = {'.gitignore'}


def walk_files():
    out = []
    for base, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            if fn in DEV_ONLY_DOCS:
                continue
            out.append(os.path.join(base, fn).replace('\\', '/')[2:])
    return sorted(out)

FILES = walk_files()
MD = [f for f in FILES if f.endswith('.md')]
# 「活文档」= MD 去掉开发期生成器目录 `scripts/_build/`。
# `_build/v3/README.md` 是**历史变更记录**（如「step62：平台 12 → 20」「12 平台入口表」），
# 描述的是当时的状态，不是当下的声明 —— 拿它去对当下的实测数会误判。
# 且 `_build` 不随包交付（release 树无此目录），用户永远看不到。
LIVE_MD = [f for f in MD if not f.startswith('scripts/_build/')]
SKILLS = [f for f in FILES if f.endswith('SKILL.md')]
LOCAL = [f for f in SKILLS if '/skills/local/' in f]
DOMAIN = [f for f in FILES if f.endswith('/_domain.md')]
DOMS = sorted(d for d in os.listdir('domains') if os.path.isdir(os.path.join('domains', d)))

# ---------- 输出形态硬契约：内部名禁止词表 ----------
# 口径唯一真相源 = library/output-spec.md §1.2。**三处必须同源**：
# 本文件的 T 组 / runcheck.py 的 internal_leaks() / regress.sh 的 [7] 段。
ALL_SKILLS = sorted({f.split('/skills/local/')[1].split('/')[0] for f in LOCAL})
FILE_INTERNAL = ['output-spec', 'output-checklist', 'general-fallback', 'domain-review-cases',
                 'clarity', 'domain-review', 'memory', 'login-policy', '_registry', '_domain',
                 'SKILL', 'config.yaml', 'dlut-read.sh', 'qihang.sh',
                 'selfcheck.sh', 'audit.sh', 'regress.sh', 'aligncheck.py', 'runcheck.py']
PROC_INTERNAL = ['库内 skill', '库外通道', '库外', '域审查', '需求明确', '归属域', '降级承接', '红线']
CODE_RE = re.compile(r'(?<![A-Za-z0-9_])([SFR][1-8])(?![A-Za-z0-9_])')
# 交付物路径 / URL 里的同名片段不算泄漏（如「→ 产出：submit/ai-disclosure.md」）
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


def section(text, title_re):
    match = re.search(title_re, text, re.M)
    if not match:
        return None
    rest = text[match.end():]
    end = re.search(r'^##\s', rest, re.M)
    return rest[:end.start()] if end else rest


def output_blocks(t):
    """取出 SKILL.md 里全部 `**输出**` 代码块。"""
    return re.findall(r'\*\*输出\*\*\s*\n\s*\n\s*```\s*\n(.*?)```', t, re.S)

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
    for _key in ('campus', 'college', 'grade', 'term', 'sleep_window'):
        if not re.search(r'^\s*%s:\s*null\s*(?:#.*)?$' % _key, cfg, re.M):
            bad('config.yaml', '%s 默认值必须为 null，避免把示例当成用户事实' % _key)
    for _key in ('courses', 'exam_weeks'):
        if not re.search(r'^\s*%s:\s*\[\]\s*(?:#.*)?$' % _key, cfg, re.M):
            bad('config.yaml', '%s 默认必须为空，避免把示例当成用户事实' % _key)
    _output_spec = rd('library/output-spec.md')
    if ('默认不读取或写入学习档案' not in _output_spec
            or '仅当用户明确要求延续或保存时' not in _output_spec):
        bad('library/output-spec.md', '档案写入必须默认关闭并以用户明确授权为前提')
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

    # ---------- C2 域与 skill 覆盖/摘要的双向路由对齐 ----------
    for d in DOMS:
        dm_path = 'domains/%s/_domain.md' % d
        dm_text = rd(dm_path)
        boundary = section(dm_text, r'^##\s*域边界[^\n]*$') or ''
        domain_cover = re.search(r'^\s*-\s*\*\*覆盖\*\*[：:]\s*(.+)$', boundary, re.M)
        if not domain_cover:
            bad(dm_path, '域边界缺少可核验的「覆盖」声明')
            continue
        skill_sec = section(dm_text, r'^##\s*库内 skill[^\n]*$') or ''
        skill_dirs = sorted(x for x in os.listdir('domains/%s/skills/local' % d)
                            if os.path.isdir('domains/%s/skills/local/%s' % (d, x)))
        for skill_name in skill_dirs:
            skill_path = 'domains/%s/skills/local/%s/SKILL.md' % (d, skill_name)
            skill_text = rd(skill_path)
            cover = re.search(r'^\s*-\s*\*\*?覆盖\*\*?[：:]\s*(.+)$', skill_text, re.M)
            if not cover:
                cover = re.search(r'^\s*-\s*覆盖[：:]\s*(.+)$', skill_text, re.M)
            if not cover:
                bad(skill_path, '缺少可供域对齐的「覆盖」能力声明')
                continue
            entry = re.search(
                r'^\s*-\s+\*\*`%s`\*\*[^\n]*(?:\n[ \t]+[^\n]+)?'
                % re.escape(skill_name), skill_sec, re.M)
            if not entry:
                bad(dm_path, 'skill `%s` 缺少可读摘要行' % skill_name)

    _s4_cover = re.search(r'^\s*-\s*\*\*覆盖\*\*[：:]\s*(.+)$',
                          section(rd('domains/S4-exam-prep/_domain.md'),
                                  r'^##\s*域边界[^\n]*$') or '', re.M)
    _faster = rd('domains/S4-exam-prep/skills/local/faster-cycle/SKILL.md')
    _s4_summary = section(rd('domains/S4-exam-prep/_domain.md'),
                          r'^##\s*库内 skill[^\n]*$') or ''
    _faster_summary = re.search(r'^\s*-\s+\*\*`faster-cycle`\*\*[^\n]*(?:\n[ \t]+[^\n]+)?',
                                _s4_summary, re.M)
    if (not _s4_cover or '完整学习循环' not in _s4_cover.group(1)
            or '完整学习循环' not in _faster
            or not _faster_summary or '完整学习循环' not in _faster_summary.group(0)):
        bad('domains/S4-exam-prep/_domain.md',
            '整门课/从零入门能力必须同时出现在 S4 覆盖声明、faster-cycle 覆盖和摘要')

    _clarity = rd('library/clarity.md')
    _ask_section = section(_clarity, r'^##\s*4\.\s*追问优先级[^\n]*$') or ''
    _b_row = re.search(r'^\|\s*`B`\s*\|([^|]+)\|([^|]+)\|', _ask_section, re.M)
    _course_steps = section(_faster, r'^##\s*执行步骤[^\n]*$') or ''
    if (not _b_row or '条件可问' not in _b_row.group(1)
            or not all(x in _course_steps for x in ('当前基础', '讲解路线', '诊断题'))):
        bad('library/clarity.md',
            'B 槽可问性必须允许课程 skill 在基础影响讲解路线时询问或诊断')

    _exceptions = section(_clarity, r'^##\s*5\.\s*不追问的例外[^\n]*$') or ''
    _general_exception = re.search(r'(?ms)^6\.\s*\*\*通用知识型\*\*.*?(?=^\s*>|^##|\Z)',
                                   _exceptions)
    if not _general_exception or '不豁免域路由与库内 skill 选择' not in _general_exception.group(0):
        bad('library/clarity.md', '例外 6 必须明确只豁免追问、不豁免域路由')

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
        if vm and vm.group(1) != REV:
            bad(f, '版本号 %s（期望 %s）' % (vm.group(1), REV))
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
            m = re.search(r'归属域\*\*[：:]\s*`?([A-Za-z]\d)`?', t)
            if not m:
                bad(f, '缺「归属域」')
            elif m.group(1) != did:
                bad(f, '归属域写 %s，实际属 %s' % (m.group(1), did))
            for ref in ('library/output-spec.md', 'library/output-checklist.md'):
                if ref not in t:
                    bad(f, '未引用 %s' % ref)
            if t.count(CANON_DELIVERY_LINE) != 1:
                bad(f, '标准交付校验句出现 %d 次（应恰好 1 次）：%s'
                    % (t.count(CANON_DELIVERY_LINE), CANON_DELIVERY_LINE))

    # ---------- D2 来源标签 ↔ 第三方台账（2026-10-04 实测缺陷）----------
    # 为什么断言：`lecture-to-notes` / `exam-sprint` 曾写 `**来源**：摘录+自建`（v2 遗留标签），
    # 与 THIRD_PARTY_NOTICES.md §一「其余 80 个为自建」+ §三「未吸收（v2 摘录，v3 改自建）」
    # 直接矛盾，而当时 6 个校验器全绿 —— 来源口径属校验盲区，只能靠精确断言兜住。
    # 口径（SKILL.md 与 _domain.md 两处必须同源，任一侧单独改动即 FAIL）：
    #   ① `**来源**` 前缀只能是 `自建` / `改造自` / `方法论思路参考`（挡住「摘录+自建」类混血标签）；
    #   ② 点名了 `owner/repo` ⇒ (域, skill, repo) 须逐条登记于 §三，且 §三 恰好 12 条；
    #   ③ 未点名仓库 ⇒ 不得出现在 §三；
    #   ④ `_domain.md` 行尾括注：SKILL.md 属自建系须以 `自建` 开头，属外部系不得以 `自建` 开头。
    SRC_PREFIX = ('自建', '改造自', '方法论思路参考')
    # 库内文档路径（`references/x.md`、`library/y.md`）形似 `owner/repo`，须排除，
    # 否则「自建 · DUT 特化（数据基础：`references/dlut-official-sites.md`）」会被误判为外部来源。
    REPO_RE = re.compile(r'`([A-Za-z0-9][A-Za-z0-9_.\-]*/[A-Za-z0-9][A-Za-z0-9_.\-]*)`')
    NOT_REPO = re.compile(r'^(references|library|domains|scripts|commands|\.)|\.(md|py|sh|json|ya?ml|txt|html?|csv)$')
    def repos_in(s):
        return [x for x in REPO_RE.findall(s) if not NOT_REPO.search(x)]
    _led = set()
    if os.path.isfile('THIRD_PARTY_NOTICES.md'):
        _s3 = re.search(r'(?ms)^##\s*三、.*?(?=^##\s)', rd('THIRD_PARTY_NOTICES.md'))
        if not _s3:
            bad('THIRD_PARTY_NOTICES.md', '缺「## 三、」已吸收来源台账段')
        else:
            _led = set(re.findall(
                r'\|\s*`([A-Za-z]\d)/([A-Za-z0-9_-]+)`\s*\|\s*`([A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+)`',
                _s3.group(0)))
            if len(_led) != 12:
                bad('THIRD_PARTY_NOTICES.md', '§三 台账登记 %d 条（期望 12）' % len(_led))
    SRC = {}      # (域, skill) -> (标签, 是否点名仓库)
    for f in LOCAL:
        did = f.split('/')[1].split('-')[0]
        slug = f.split('/skills/local/')[1].split('/')[0]
        m = re.search(r'-\s*\*\*来源\*\*[：:]\s*(.+)', rd(f))
        if not m:
            bad(f, '缺「**来源**」标注'); continue
        lab = m.group(1).strip()
        repo = repos_in(lab)
        SRC[(did, slug)] = (lab, bool(repo))
        if not lab.startswith(SRC_PREFIX):
            bad(f, '来源标签「%s」不在合法口径（自建 / 改造自 / 方法论思路参考）' % lab)
        if repo:
            for rp in repo:
                if (did, slug, rp) not in _led:
                    bad(f, '来源点名 `%s`，但 §三 未登记「%s/%s ↔ 该仓库」' % (rp, did, slug))
        elif (did, slug) in {(d, s) for d, s, _ in _led}:
            bad(f, '已在 §三 登记外部来源，但「来源」标签未点名仓库')
    for f in DOMAIN:
        did = f.split('/')[1].split('-')[0]
        for ln in rd(f).splitlines():
            b = re.match(r'-\s*\*\*`([A-Za-z0-9_-]+)`\*\*', ln.strip())
            if not b or (did, b.group(1)) not in SRC:
                continue
            ext = SRC[(did, b.group(1))][1]
            pm = re.search(r'[（(]([^）)]*)[）)]\s*$', ln.strip())
            dom = pm.group(1) if pm else ''
            if ext and dom.startswith('自建'):
                bad(f, '`%s` 在 SKILL.md 标为外部来源，此处括注却写「%s」' % (b.group(1), dom))
            if not ext and not dom.startswith('自建'):
                bad(f, '`%s` 在 SKILL.md 标为自建，此处括注为「%s」（应以「自建」开头）'
                    % (b.group(1), dom or '（无）'))

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
        for x in re.findall(r'→\s*`?([A-Za-z]\d)`?', t):
            if not any(dd.startswith(x + '-') for dd in DOMS):
                bad(f, '「不覆盖 →%s」指向不存在的域' % x)
        # 执行顺序必须「先判红线」
        if not re.search(r'0\.\s*\*\*先判红线\*\*', t):
            bad(f, '执行顺序未前置「先判红线」')
        # 执行顺序步骤号必须「0 起、连续、无重复」。
        # 防复发：S1 的 `0. **先判红线**` 曾连写两行，而上面这句与 runcheck 的同名断言
        # 都用 re.search（存在即过），重复行因此长期存活 —— 序号结构本身从未被校验。
        _ord = re.search(r'^##\s*执行顺序[^\n]*\n(.*?)(?=\n## |\Z)', t, re.S | re.M)
        _nums = [int(x) for x in re.findall(r'^(\d{1,2})\.\s', _ord.group(1), re.M)] if _ord else []
        _dup = sorted(set(x for x in _nums if _nums.count(x) > 1))
        if _dup:
            bad(f, '执行顺序步骤号重复 %s（同一序号出现多次，列表结构已损坏）' % _dup)
        elif _nums != list(range(len(_nums))):
            bad(f, '执行顺序步骤号不连续 %s（应为 0..%d）' % (_nums, len(_nums) - 1))

    # ---------- F2 URL 呈现边界（2026-10-03 实测缺陷）----------
    # 触发原因：依据里的 URL 紧贴中文说明时，渲染器会把中文吞进 href → 点开 404。
    # 判据：URL 之后**要么是空白/表格竖线/行尾，要么先补一个空格**；URL 末尾不得紧跟收尾标点。
    _trail = ')]}>,.;:。，、；：）】》'
    _badurl = 0
    for _f in MD:
        for _i, _ln in enumerate(rd(_f).split('\n'), 1):
            for _m in re.finditer(r'https?://[^\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef`*<>"\']+', _ln):
                _core = _m.group(0).rstrip(_trail)
                if not _core:
                    continue
                _tp = _m.start() + len(_core)
                _nx = _ln[_tp:_tp + 1]
                if _tp < _m.end() or (_nx and re.match(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]', _nx)):
                    _badurl += 1
                    if _badurl <= 6:
                        bad(_f, 'URL 与后续中文/标点之间缺空白（第 %d 行）→ 渲染时会被吞进链接' % _i)
    if _badurl:
        bad('（URL 边界）', '共 %d 处 URL 紧贴中文/标点，须在 URL 后补空格' % _badurl)

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

    # ---------- G2 节号引用（`X.md` §N / §N.M）必须指向目标文件真实存在的编号小节 ----------
    # 防复发：output-spec.md 曾写 `output-checklist.md` §6，而该文件只有 §一/二/三 +
    # 「7 项通用硬校验」的第 6 项 —— 节号漂移不会被路径检查捕获（文件确实存在）。
    # 口径保守：仅当目标文件确实含「## N.」或「### N.M」形式的编号标题时才校验；用 §一/§二 这类
    # 中文编号指向中文节的不做名校验（不同文件编号风格不统一，易假阳性）。
    # ⚠️ 2026-10-03 修正断言空转：原正则只取 `\d+`，`§3.6` 被截成 `3` —— 3 存在即永不报警；
    #    且 `heads` 只扫 `##`，`### 1.3` 这类三级小节从未进入允许集。现两级都收。
    _secpat = re.compile(r'`([\w./-]+\.md)`\s*§\s*(\d+(?:\.\d+)*)')
    for f in MD:
        for m in _secpat.finditer(rd(f)):
            tgt = m.group(1)
            cand = [tgt, os.path.normpath(os.path.join(os.path.dirname(f), tgt)).replace('\\', '/')]
            real = next((c for c in cand if os.path.exists(c)), None)
            if not real:
                continue
            # H2 写「## N. 标题」，H3/H4 写「### N.M 标题」—— 尾点只属顶层编号，故 `\.?` 可选。
            heads = re.findall(r'^#{2,4}\s+(\d+(?:\.\d+)*)(?:\.|\s|$)', rd(real), re.M)
            if heads and m.group(2) not in heads:
                _hs = sorted(set(heads), key=lambda s: [int(x) for x in s.split('.')])
                bad(f, '节号引用 `%s` §%s 越界（该文件仅有 §%s）'
                    % (tgt, m.group(2), '/§'.join(_hs)))

    # ---------- H 计数与版本 ----------
    reg = rd('domains/_registry.md')
    # H1 registry 声明的「域数 / 库内 skill 数」必须等于实测
    _mh = re.search(r'共\s*\*{0,2}(\d+)\s*个域\s*/\s*(\d+)\s*个库内\s*skill', reg)
    if _mh:
        if int(_mh.group(1)) != len(DOMS):
            bad('domains/_registry.md', '声明域数 %s ≠ 实测 %d' % (_mh.group(1), len(DOMS)))
        if int(_mh.group(2)) != len(LOCAL):
            bad('domains/_registry.md', '声明库内 skill 数 %s ≠ 实测 %d' % (_mh.group(2), len(LOCAL)))
    else:
        bad('domains/_registry.md', '未声明「共 N 个域 / M 个库内 skill」')
    # H2 每行 registry 的 skill 列表 == 该域 skills/local/ 实体目录
    for line in reg.splitlines():
        # 列：| 域ID | 名称 | 触发词 | 库内 skill 列表 |
        m = re.match(r'^\|\s*`([A-Za-z]\d)`\s*\|([^|]*)\|([^|]*)\|\s*([^|]+?)\s*\|\s*$', line)
        if not m:
            continue
        did, cell = m.group(1), m.group(4)
        dm = [x for x in DOMS if x.startswith(did + '-')]
        if not dm:
            bad('domains/_registry.md', '未知域 ID: %s（不在 %d 域目录中）' % (did, len(DOMS)))
            continue
        d = dm[0]
        decl = sorted(re.findall(r'`([\w-]+)`', cell))
        real = sorted(x for x in os.listdir('domains/%s/skills/local' % d)
                      if os.path.isdir('domains/%s/skills/local/%s' % (d, x)))
        if decl != real:
            bad('domains/_registry.md', '%s 声明 skill %s ≠ 实体 %s' % (did, decl, real))
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
    if vers - {REV}:
        bad('（frontmatter）', '版本号不唯一: %s' % sorted(vers))
    # 插件清单（JSON 风格，易与 YAML 风格一起被漏改）
    try:
        pv = json.loads(rd('.codebuddy-plugin/plugin.json')).get('version')
        if pv != REV:
            bad('.codebuddy-plugin/plugin.json', 'version = %s（期望 %s）' % (pv, REV))
    except Exception:
        pass
    # 提交物的版本声明（易漂移点，显式点名）
    # 注意：场景设计书（HTML）属过程文档，发布副本在导出阶段已剔除，不存在属正常，须跳过而非崩溃。
    _vf = 'qihang-scenario-design.html'
    if os.path.exists(_vf):
        m = re.search(r'<title>[^<]*（v([\d.]+)）', rd(_vf))
        if m and m.group(1) not in (PKG, REV):
            bad(_vf, '版本声明 %s（期望包版本 %s 或修订号 %s）' % (m.group(1), PKG, REV))
    # 版本号口径（v3.2 起统一）：包版本 = 两位（前两位）｜修订号 = 三位（见 config.yaml）
    # 展示位写三位 = 口径漂移（正是「包版本与修订号不统一」的复发点），故在此硬断言。
    _rfm = re.match(r'^---\n(.*?)\n---', rd('SKILL.md'), re.S)
    _rev = None
    if _rfm:
        _m = re.search(r'^version:\s*([\d.]+)', _rfm.group(1), re.M)
        if _m:
            _rev = _m.group(1)
    if _rev:
        _pkg = '.'.join(_rev.split('.')[:2])
        for _f, _pat in (('README.md', r'学伴包 v([\d.]+)'),
                         ('SKILL.md', r'入口（v([\d.]+)）'),
                         ('scripts/qihang.sh', r'学伴包 v([\d.]+)')):
            _h = re.search(_pat, rd(_f))
            if not _h:
                warn(_f, '未找到包版本展示位（期望两位形态 v%s）' % _pkg)
            elif _h.group(1) != _pkg:
                bad(_f, '包版本展示 %s（应为两位 v%s；三位 %s 只用于修订号）'
                    % (_h.group(1), _pkg, _rev))



    # ---------- I commands ----------
    for f in sorted(glob.glob('commands/*.md')):
        f = f.replace('\\', '/')
        t = rd(f)
        if not t.startswith('---'):
            warn(f, '无 frontmatter（slash 命令通常需要）')
        if re.fullmatch(r'commands/qihang-[sfr]\d\.md', f):
            if '12 平台' in t or '检索 12' in t:
                bad(f, '域入口卡仍保留旧的全量平台检索口径')
            if '输出与归档' in t or '按 `library/memory.md` 归档' in t:
                bad(f, '域入口卡仍要求默认归档学习档案')
            if ('输出与保存' in t and '仅用户明确要求保存时' not in t
                    and '不写入任何记忆层' not in t):
                bad(f, '域入口卡的保存动作缺少用户明确授权条件')
        for p in re.findall(r'(?:domains|library|references|scripts)/[^ )），、；;"“”<>*`]+', t):
            if not os.path.exists(p) and '<' not in p and '+' not in p:
                bad(f, '引用不存在: %s' % p)

    # ---------- J plugin.json ----------
    try:
        pj = json.loads(rd('.codebuddy-plugin/plugin.json'))
        v = json.dumps(pj)
        if REV not in v:
            warn('.codebuddy-plugin/plugin.json', '未声明版本 %s' % REV)
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
    # 需求确定门（`library/clarity.md` §3.1）：`C = 1 − U` 的算例与阈值必须与 `config.yaml` 同源
    _cl = rd('library/clarity.md')
    _C = 1 - U(v0)
    if abs(_C - 0.689) > 0.002:
        bad('library/clarity.md', '例 A 的 C = 1 − U = %.4f 与文档 0.689 不符（需求确定门算例）' % _C)
    _ct = re.search(r'confirm_threshold:\s*([\d.]+)', rd('config.yaml'))
    _rf = re.search(r'restate_floor:\s*([\d.]+)', rd('config.yaml'))
    if _ct and _ct.group(1) not in _cl:
        bad('library/clarity.md', 'confirm_threshold=%s 未在 §3.1 声明（阈值未同源）' % _ct.group(1))
    if _rf and _rf.group(1) not in _cl:
        bad('library/clarity.md', 'restate_floor=%s 未在 §3.1 声明（阈值未同源）' % _rf.group(1))
    if '复述档' not in _cl or '确定档' not in _cl or '追问档' not in _cl:
        bad('library/clarity.md', '§3.1 未声明三档（确定档 / 复述档 / 追问档）')
    if '例 D' not in _cl or '0.816' not in _cl:
        bad('library/clarity.md', '§3.1 缺需求确定门算例（例 D / 例 E）')
    for pat_ in [r'U\s*=\s*1\s*[−-]\s*([\d.]+)\s*/\s*6\.1\s*=\s*([\d.]+)']:
        for f in MD:
            for m in re.finditer(pat_, rd(f)):
                num, doc = float(m.group(1)), float(m.group(2))
                calc = round(1 - num / 6.1, 3)
                if abs(calc - doc) > 0.002:
                    bad(f, 'U 值复算不符: 文档 %s，复算 %.3f（%s/6.1）' % (doc, calc, num))

    # ---------- L2 示例「澄清判定」的 U 断言必须可判定 ----------
    # 防复发：示例曾出现「U ≤ 0.30」而按公式实为 0.311（关键槽齐全例 A 的同形输入）。
    # 示例未列槽位表、无法直接复算，故改为**依据断言**：凡以 `U ≤` 给出结论，
    # 必须同时给出判定依据 —— 引 §5 例外 / 「追问 N 问后」/ 分母 6.1。
    # 注意：「无需追问」里的「追问」不是依据，故要求 `追问\s*\d` 或 `问后` 这种**有追问轮次**的写法。
    for f in LOCAL:
        t2 = rd(f)
        mc2 = re.search(r'\*\*澄清判定\*\*[：:][^\n]*', t2)
        if mc2 and re.search(r'U\s*[≤<]', mc2.group(0)):
            if not re.search(r'例外|追问\s*\d|问后|/\s*6\.1', mc2.group(0)):
                bad(f, '澄清判定给 U 数值结论但无依据（须引 §5 例外 / 「追问 N 问后」/ 分母 6.1）')

    # ---------- L3 阈值不得被当作**唯一**放行条件 ----------
    # 防复发：各 _domain.md 与各库内 skill 曾统一写「U ≤ 0.30 才继续」／
    # 「（6 槽位 + 澄清门，U ≤ 0.30）」，与 clarity.md §3 直接冲突 ——
    # 关键槽 O/T/D 齐全且不歧义时，U > 0.30 也应放行（§5 例外 2，见 §6 例 A）。
    # 规则：凡出现 `U ≤ 0.30` 的行，必须同时给出「它不是唯一条件」的依据 ——
    #       引 §5 例外 / 注明自己是阈值真相源 / 或标注是「追问 N 问后」才降到 0.30。
    _L3_OK = re.compile(r'例外|§5|阈值|真相源|追问\s*\d|问后|/\s*6\.1')
    for f in MD:
        for _i3, _ln3 in enumerate(rd(f).split('\n')):
            if re.search(r'U\s*[≤<]\s*0\.30', _ln3) and not _L3_OK.search(_ln3):
                bad(f, '第 %d 行把阈值当唯一放行条件（须引 §5 例外 / 注明为阈值真相源 / '
                       '标注「追问 N 问后」）: %s' % (_i3 + 1, _ln3.strip()[:60]))

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
        _domain_text = rd(dm)
        if ('检索 12 平台' in _domain_text or '检索 **12 个平台**' in _domain_text
                or '（12 平台检索 +' in _domain_text):
            bad(dm, '域说明仍保留旧的全量平台检索口径')
        _domain_execution = re.search(r'^## 执行顺序\n(.*?)(?=\n## |\Z)', _domain_text, re.S)
        _domain_steps = _domain_execution.group(1).splitlines() if _domain_execution else []
        if any(line.startswith('4.') and 'library/output-spec.md' in line
               and ('写入学习档案' in line or '按 `library/memory.md`' in line)
               and '仅用户明确要求保存时' not in line
               and '始终不得保存' not in line
               for line in _domain_steps):
            bad(dm, '域说明仍要求默认写入学习档案')
        _domain_id = d.split('-', 1)[0].lower()
        _command_text = rd('commands/qihang-%s.md' % _domain_id)
        if _command_text:
            _domain_memory_line = next((line for line in _domain_text.splitlines()
                                        if line.startswith('4.') and 'library/output-spec.md' in line), None)
            _command_memory_line = next((line for line in _command_text.splitlines()
                                         if line.startswith('4.') and 'library/output-spec.md' in line), None)
            if _domain_memory_line and _command_memory_line and _domain_memory_line != _command_memory_line:
                bad(dm, '域说明保存策略与对应入口卡不一致')
            _domain_bridge_line = next((line for line in _domain_text.splitlines()
                                        if line.startswith('6.') and '外部桥接' in line), None)
            _command_bridge_line = next((line for line in _command_text.splitlines()
                                         if line.startswith('6.') and '外部桥接' in line), None)
            if _domain_bridge_line and _command_bridge_line and _domain_bridge_line != _command_bridge_line:
                bad(dm, '域说明外部桥接策略与对应入口卡不一致')
        if d.startswith(('F3-', 'F5-')) and '外部桥接（按需）' in _domain_text:
            bad(dm, 'F3/F5 敏感域不得启用外部桥接')
        ref = sig(_domain_text)
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
        if '12 平台检索' in t or '学习档案记「缺口」' in t:
            bad(f, 'skill 仍包含全平台检索或默认归档缺口的旧口径')
        if f.startswith(('domains/F3-', 'domains/F5-')) and 'library/external-bridge.md' in t:
            bad(f, 'F3/F5 敏感域 skill 不得外接')
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
        # 口径真相源 = library/output-spec.md §0–§2，与 runcheck.py 的 L3-5 同源。
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
            if not any(x in labels for x in ('结果', '网址', '替代方案', '还需确认')):
                bad(f, '示例输出无实质内容字段（须有【结果】/校情【网址】/红线【替代方案】/追问【还需确认】）')
            lk = internal_leaks(o)
            if lk:
                bad(f, '示例输出泄漏内部名 %d 处: %s' % (len(lk), '、'.join(lk[:6])))
            if re.search(r'\[已降级\s*[:：]', o):
                bad(f, '降级标注用旧格式「[已降级: X → Y]」（须写 [已降级] 由「能力」改为「能力」）')

    # O7 跨域标题唯一（重名会导致路由歧义）
    for title, fs in titles.items():
        if len(fs) > 1:
            bad('（全域）', '库内 skill 标题重名「%s」: %s' % (title, fs))
    # O8 同域多条 skill 定位不得高度相似（否则用户无法选择）—— 全对比较
    for d in DOMS:
        fs = sorted(glob.glob('domains/%s/skills/local/*/SKILL.md' % d))
        if len(fs) < 2:
            continue
        pos = []
        for f_ in fs:
            m = re.search(r'\*\*定位\*\*[：:]\s*(.+)', rd(f_.replace('\\', '/')))
            pos.append(m.group(1).strip() if m else '')
        _n = len(fs)
        for _i in range(_n):
            for _j in range(_i + 1, _n):
                sim = difflib.SequenceMatcher(None, pos[_i], pos[_j]).ratio()
                if sim > 0.60:
                    bad(fs[_i].replace('\\', '/'),
                        '同域 skill 定位与 %s 相似度 %.2f（路由歧义）'
                        % (os.path.basename(os.path.dirname(fs[_j])), sim))

    # O9 库内 skill 目录名不得跨域重复（同名会导致路由判定与安装路径冲突）
    _name_map = collections.defaultdict(list)
    for _f in LOCAL:
        _sd = _f.split('/skills/local/')[1].split('/')[0]
        _name_map[_sd].append(_f)
    for _nm, _fs in sorted(_name_map.items()):
        if len(_fs) > 1:
            bad('（全域）', '库内 skill 目录名跨域重复「%s」: %s' % (_nm, _fs))

    # S 小节正文非空（防空壳标题：只有标题、正文缺失 —— 读者无法据以执行）
    # 两个例外不算空壳：① 容器标题（下面直接跟更深一级子节，如 ## 2 → ### 2.1）；
    #                   ② 代码块里的示例标题（非真实小节），因此先屏蔽 ``` 围栏区间。
    for _f in [x for x in MD if x.startswith('library/') or x.endswith('/_domain.md')]:
        _t = rd(_f)
        _fence = [(m.start(), m.end()) for m in re.finditer(r'```.*?```', _t, re.S)]

        def _in_fence(_p, _sp=_fence):
            return any(_a <= _p < _b for _a, _b in _sp)

        _hs = [(m.start(), len(m.group(1)), m.group(2).strip(), m.end())
               for m in re.finditer(r'^(#{2,3})\s+([^\n]+)', _t, re.M)]
        for _i, (_st, _lv, _title, _en) in enumerate(_hs):
            if _in_fence(_st):
                continue
            _nxt = _hs[_i + 1] if _i + 1 < len(_hs) else None
            if _nxt and _nxt[1] > _lv and not _in_fence(_nxt[0]):
                continue  # 容器标题：由下层子节承载正文
            _body = _t[_en:(_nxt[0] if _nxt else len(_t))]
            _n = len(re.sub(r'[\s>*\-|`#]+', '', _body))
            if _n == 0:
                bad(_f, '小节「%s」正文完全为空（空壳标题）' % _title[:32])
            elif _n < 8:
                warn(_f, '小节「%s」正文仅 %d 字（偏短，请确认非空壳）' % (_title[:32], _n))

    # ---------- P 三级路由链可解（库内唯一通道） ----------
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
        if 'library/output-spec.md' not in o:
            bad(dm_p, '执行顺序未接输出规范')
        # 库内唯一通道：执行顺序不得再给出库外兜底路径
        if 'external.md' in o or '库外' in o:
            bad(dm_p, '执行顺序仍含库外通道表述（应为库内唯一）')
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
    # 全量扫描：不再用**文件名白名单**（旧版只查 7 个文件，部分目录
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
            # 「N 项待人工补」= §8 未核实清单（同一口径的另一种写法）
            for _f2 in [x for x in LIVE_MD if '待人工补' in rd(x)]:
                for _m2 in re.finditer(r'(\d{1,3})\s*项待人工补', rd(_f2)):
                    if int(_m2.group(1)) != _n8:
                        bad(_f2, '「待人工补」项数 %s ≠ §8 未核实清单实测 %d'
                            % (_m2.group(1), _n8))

    # 站点画像数：`dlut-site-profiles.md` 表头声明「N 个站点」== §一 表格数据行数；
    # 其他文档写「N 站画像」也必须同源。
    # 为什么加：README 长期写「19 站画像」而文件自身声明 18 —— 四个校验器全绿，无人断言。
    _sp = 'references/dlut-site-profiles.md'
    if os.path.exists(_sp):
        _stp = rd(_sp)
        _dm = re.search(r'(\d{1,3})\s*个站点', _stp)
        _s1 = section(_stp, r'^## 一、')
        _nsp = None
        if _s1 is not None:
            _r1 = [l for l in _s1.splitlines() if l.startswith('|')]
            _sep1 = {i for i, l in enumerate(_r1) if set(l.strip()) <= set('|-: ')}
            _nsp = len([l for i, l in enumerate(_r1)
                        if i not in _sep1 and (i - 1) not in _sep1])
        if _dm and _nsp is not None and int(_dm.group(1)) != _nsp:
            bad(_sp, '站点画像声明 %s 个站点 ≠ §一 表格实测 %d 行'
                % (_dm.group(1), _nsp))
        if _nsp is not None:
            for _f4 in LIVE_MD:
                if not os.path.exists(_f4):
                    continue
                for _m4 in re.finditer(r'(\d{1,3})\s*站画像', rd(_f4)):
                    if int(_m4.group(1)) != _nsp:
                        bad(_f4, '「站画像」声明 %s ≠ 实测 %d'
                            % (_m4.group(1), _nsp))

    # 交付树文件总数：README 声明的「release 分支 = 纯净交付树（N 个文件）」必须等于交付集实际文件数。
    # 交付集口径 = 排除 .git/.idea/.learnbuddy/__pycache__/_build 与过程文档（与负向自测的复制口径一致）。
    # 另排除开发侧版本控制元数据 `.gitignore`（release 树无此文件，实测 `git ls-tree release` 176 项）。
    # ⚠️ `.gitattributes` **不排除** —— 它确实在 release 树里（与 main 同 blob），算进去才与
    # 「release 分支 = 纯净交付树（176 个文件）」同解；把它一并排除会得到 175，反而与事实不符。
    # 为什么加：该计数曾长期停留在 173（实际 176），而四个校验器全绿。
    # 为什么不用 git 当唯一真值：负向自测在**无 .git 的临时树**上跑，只认 git 的断言在负向测试里会空转。
    _deliv = 0
    for _b5, _d5, _fs5 in os.walk('.'):
        _d5[:] = [d for d in _d5 if d not in ('.git', '.idea', '.learnbuddy', '__pycache__', '_build')]
        _deliv += len([f for f in _fs5
                       if f not in DEV_ONLY_DOCS and f not in DELIV_EXCLUDE_FILES])
    if _deliv:
        for _f5 in LIVE_MD:
            if not os.path.exists(_f5):
                continue
            for _m5 in re.finditer(r'交付树[^\n]{0,14}?(\d{2,4})\s*个文件', rd(_f5)):
                if int(_m5.group(1)) != _deliv:
                    bad(_f5, '交付树文件总数声明 %s ≠ 交付集实测 %d'
                        % (_m5.group(1), _deliv))
    # 有 .git 时再交叉核验一次：工作树交付集必须与 release ref 一致（防「本地多塞了文件」）。
    if os.path.isdir('.git') and _deliv:
        try:
            _rel = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'release'],
                                  capture_output=True, text=True, timeout=60)
        except Exception:
            _rel = None
        if _rel is not None and _rel.returncode == 0:
            _nr = len([x for x in _rel.stdout.splitlines() if x.strip()])
            if _nr != _deliv:
                bad('README.md', '交付集文件数 %d ≠ release ref %d（工作树与 release 不一致）'
                    % (_deliv, _nr))

    # qihang.sh status 的 1 级清单 == library/ 实际文件（INSTALL.md 声明「逐行列出 11 个」）
    # 为什么加：实测该循环漏列 external-bridge.md / general-fallback.md（9/11），
    # 而 selfcheck 只断言 library 文件数 = 11，不断言「被列出的」是不是同一批。
    if os.path.exists('scripts/qihang.sh'):
        _qs = rd('scripts/qihang.sh')
        _blk = re.search(r'\[1级\] skill 库"(.*?); do', _qs, re.S)
        if _blk:
            _listed = set(re.findall(r'library/([\w-]+\.md)', _blk.group(1)))
            _actual = {f.split('/')[-1] for f in FILES
                       if f.startswith('library/') and f.endswith('.md')}
            _miss = sorted(_actual - _listed)
            if _miss:
                bad('scripts/qihang.sh', 'status 的 1 级清单漏列 %d 个 library 文件: %s'
                    % (len(_miss), '、'.join(_miss)))

    # 外部平台目录数：`references/external-sources.md` 的编号入口行数 == 各处声明数。
    # 为什么加：`domains/_registry.md` 长期写「12 个平台目录」（v3.3.1 已扩到 20 个），
    # 且 aligncheck 只在 `_domain.md` 里拦「检索 12 平台」旧口径，总表这一处是射程外。
    _es = 'references/external-sources.md'
    if os.path.exists(_es):
        # 只数**入口表**（表头 `| # | 平台 | 检索入口 | …`）的数据行 —— 文件内其他表也有编号行，
        # 全局数「编号行」会得到 58 这类假值（实测踩过）。
        _esl = rd(_es).splitlines()
        _npl = 0
        for _i6, _l6 in enumerate(_esl):
            if _l6.startswith('|') and '平台' in _l6 and '检索入口' in _l6:
                for _l6b in _esl[_i6 + 1:]:
                    if not _l6b.startswith('|'):
                        break
                    if set(_l6b.strip()) <= set('|-: '):
                        continue
                    _npl += 1
                break
        if _npl:
            for _f6 in LIVE_MD:
                if not os.path.exists(_f6):
                    continue
                _t6 = rd(_f6)
                for _pat6 in (r'(?<![\d\u2013\u2014-])(\d{1,3})\s*个平台(?:目录|入口)',
                              r'(?<![\d\u2013\u2014-])(\d{1,3})\s*平台'):
                    for _m6 in re.finditer(_pat6, _t6):
                        if int(_m6.group(1)) != _npl:
                            bad(_f6, '平台数声明 %s ≠ external-sources.md 实测 %d'
                                % (_m6.group(1), _npl))
                for _l6 in _t6.splitlines():
                    if '平台' not in _l6:
                        continue
                    for _m6 in re.finditer(r'(?<![\d\u2013\u2014-])(\d{1,3})\s*个入口', _l6):
                        if int(_m6.group(1)) != _npl:
                            bad(_f6, '平台入口数声明 %s ≠ external-sources.md 实测 %d'
                                % (_m6.group(1), _npl))

    # §11.2 外链口径计数：`dlut-url-verification.md` 声明的「唯一外链 N 条 / 出现 M 处」
    # 与「DUT 域内 N 条 / M 处」必须等于按 §11.7 ① 口径在交付集上的实测值。
    # 为什么加：该行长期写「138 条 / 654 处」，无口径、复现命令还指向从未交付的 `urlcheck.py`，
    # 四个校验器全绿 —— 数字对不上也没人发现。口径 = `https?://` 匹配 + http→https + 去尾斜杠。
    _uv = 'references/dlut-url-verification.md'
    if os.path.exists(_uv):
        _occ = collections.Counter()
        for _b8, _d8, _fs8 in os.walk('.'):
            _d8[:] = [d for d in _d8
                      if d not in ('.git', '.idea', '.learnbuddy', '__pycache__', '_build')]
            for _f8 in _fs8:
                if _f8 in DEV_ONLY_DOCS or _f8 in DELIV_EXCLUDE_FILES:
                    continue
                _p8 = os.path.join(_b8, _f8)
                try:
                    _t8 = rd(_p8)
                except Exception:
                    continue
                for _m8 in re.finditer(r'https?://[^\s`"\u3000）)】|>,;]+', _t8):
                    _u8 = _m8.group(0)
                    if _u8.startswith('http:'):
                        _u8 = 'https' + _u8[4:]
                    _occ[_u8.rstrip('/').rstrip('。').rstrip('、')] += 1
        _dut8 = {u: v for u, v in _occ.items() if 'dlut' in u}
        _uvt = rd(_uv)
        for _m8 in re.finditer(r'唯一外链\s*(\d{1,4})\s*条\s*/\s*出现\s*(\d{1,4})\s*处', _uvt):
            if int(_m8.group(1)) != len(_occ):
                bad(_uv, '「唯一外链」声明 %s ≠ §11.7 口径实测 %d'
                    % (_m8.group(1), len(_occ)))
            if int(_m8.group(2)) != sum(_occ.values()):
                bad(_uv, '「外链出现」声明 %s ≠ §11.7 口径实测 %d'
                    % (_m8.group(2), sum(_occ.values())))
        for _m8 in re.finditer(r'DUT 域内\s*(\d{1,4})\s*条\s*/\s*(\d{1,4})\s*处', _uvt):
            if int(_m8.group(1)) != len(_dut8):
                bad(_uv, '「DUT 域内外链」声明 %s ≠ 实测 %d'
                    % (_m8.group(1), len(_dut8)))
            if int(_m8.group(2)) != sum(_dut8.values()):
                bad(_uv, '「DUT 域内外链出现」声明 %s ≠ 实测 %d'
                    % (_m8.group(2), sum(_dut8.values())))

        # 跨文件计数引用：**任何**引用「N 条外链」的活文档都必须等于同一实测值。
        # 为什么加：`dlut-official-sites.md` 长期引「138 条外链」，而 138 正是本源文件 §11.2
        # 已明确标注「已被推翻」的初版口径。上面几个断言只扫**本源文件**，守护不到**引用方**，
        # 于是过期引用在四个校验器全绿的情况下存活 —— 与「唯一外链」那条是同一根因的另一半。
        # 口径同 §11.2：归一化（http→https、去尾斜杠）后的不同 URL 数。
        # 只扫 `LIVE_MD`（活文档）：本源文件是历史口径的**合法登记处**（§11.2/§11.3 必须引用旧值），
        # 且其自身已有更严格断言；校验器源码（*.py/*.sh）含该模式字符串与注入用例字面量，
        # 纳入扫描会自触。
        for _f9 in LIVE_MD:
            if _f9 == _uv:
                continue
            try:
                _t9 = rd(_f9)
            except Exception:
                continue
            for _m9 in re.finditer(r'(\d{1,4})\s*条外链', _t9):
                if int(_m9.group(1)) != len(_occ):
                    bad(_f9, '「%s 条外链」引用过期 ≠ §11.2 口径实测 %d'
                        % (_m9.group(1), len(_occ)))

    # 触发门词表同源（config.yaml「词表同源铁律」）：`learning_markers` 必须**逐词等于**
    # 20 域 `## 触发词` 段的并集，且文档里「共 N 词」必须等于该词数。
    # 为什么加：SKILL.md 长期写「共 196 词」（实测 219），而四个校验器全绿 —— 词表规模无人断言。
    _mlm = re.search(r'^\s*learning_markers:\s*\[(.*?)\]\s*$', cfg, re.M | re.S)
    if _mlm:
        _lmw = [x.strip() for x in _mlm.group(1).split(',') if x.strip()]
        if len(set(_lmw)) != len(_lmw):
            bad('config.yaml', 'learning_markers 含重复项')
        _uw = []
        for d in DOMS:
            _dt = rd('domains/%s/_domain.md' % d)
            _sec = section(_dt, r'^##\s*触发词')
            if _sec is None:
                bad('domains/%s/_domain.md' % d, '缺 `## 触发词` 段（触发门并集无法派生）')
                continue
            for _w in re.findall(r'`([^`]+)`', _sec):
                # 段内的反引号也可能包着路径 / 域代号（如 `R6`、`_registry.md`），不是触发词
                if re.fullmatch(r'[A-Z]\d', _w) or '/' in _w or '.' in _w:
                    continue
                _uw.append(_w)
        _miss = sorted(set(_uw) - set(_lmw))
        _extra = sorted(set(_lmw) - set(_uw))
        if _miss:
            bad('config.yaml', 'learning_markers 漏掉 %d 个域触发词: %s'
                % (len(_miss), '、'.join(_miss[:8])))
        if _extra:
            bad('config.yaml', 'learning_markers 多出 %d 个非域触发词: %s'
                % (len(_extra), '、'.join(_extra[:8])))
        _nlm = len(set(_lmw))
        for _f7 in LIVE_MD:
            if not os.path.exists(_f7):
                continue
            for _l7 in rd(_f7).splitlines():
                if 'learning_markers' not in _l7:
                    continue
                for _m7 in re.finditer(r'共\s*(\d{1,3})\s*词', _l7):
                    if int(_m7.group(1)) != _nlm:
                        bad(_f7, 'learning_markers 词数声明 %s ≠ 实测 %d'
                            % (_m7.group(1), _nlm))

    # ---------- U 触发门：越界表不变式 ----------
    # 为什么加：「基金」同时进 learning_markers（派生自 R4 `## 触发词`）与 out_of_scope_markers，
    # 而越界表声明「优先级最高，压过宽词表」→ R4 的 grant-apply 永不可达，而四个校验器全绿。
    # 越界表是**手工维护的硬停表**，接管词表是**派生表**；硬停必须与派生表零交集，
    # 否则硬停会静默吞掉合法域路由（多义词归**需求主键 T+O** 判定，不入本表）。
    def _yaml_words(key):
        _m = re.search(r'^\s*' + key + r':\s*\[(.*?)\]\s*$', cfg, re.M | re.S)
        return [x.strip() for x in _m.group(1).split(',') if x.strip()] if _m else None

    _oos = _yaml_words('out_of_scope_markers')
    if _oos is None:
        bad('config.yaml', '缺 out_of_scope_markers（越界信号无法校验）')
    elif not _oos:
        bad('config.yaml', 'out_of_scope_markers 为空（越界信号失效）')
    else:
        if len(set(_oos)) != len(_oos):
            bad('config.yaml', 'out_of_scope_markers 含重复项')
        _takeover = (set(_lmw) if _mlm else set()) \
            | set(_yaml_words('dlut_markers') or []) \
            | set(_yaml_words('learning_intents') or [])
        _clash = sorted(set(_oos) & _takeover)
        if _clash:
            bad('config.yaml', '越界词与接管词冲突 %d 个（越界为初筛，冲突即吞掉域路由）: %s'
                % (len(_clash), '、'.join(_clash)))
        _dup = sorted({b for a in _oos for b in _oos if a != b and a in b})
        if _dup:
            bad('config.yaml', '越界表含冗余子串项（子串匹配下恒被更长项覆盖）: %s'
                % '、'.join(_dup))
        _sk = rd('SKILL.md')
        _s15 = section(_sk, r'^###\s*1\.5\s*越界信号[^\n]*$')
        if _s15 is None:
            bad('SKILL.md', '缺 §1.5 越界信号段')
        else:
            # 列举形如「电影 / 电视剧 / … / 菜谱 … → 直接按普通助手回答。」
            _inline, _seen = [], False
            for _ln in _s15.splitlines():
                if 'out_of_scope_markers' in _ln:
                    _seen = True
                    continue
                if not _seen:
                    continue
                if '→' in _ln:
                    _inline += _ln.split('→')[0].split('/')
                    break
                if '/' in _ln:
                    _inline += _ln.split('/')
            _inline = [x.replace('…', '').strip() for x in _inline]
            _inline = [x for x in _inline if x]
            if not _inline:
                bad('SKILL.md', '§1.5 未能解析出内联越界词（列举格式已变）')
            _ex_inline = sorted(set(_inline) - set(_oos))
            if _ex_inline:
                bad('SKILL.md', '§1.5 内联越界词不在 config.yaml 越界表内: %s'
                    % '、'.join(_ex_inline))
        # 判据双处声明：单词命中≠接管（主键 T+O）；越界只做初筛、归属按仲裁顺序
        for _f8, _t8, _needs in (('config.yaml', cfg, ('需求主键', '仲裁顺序')),
                                 ('SKILL.md', _sk, ('归属由主键定', '仲裁顺序'))):
            for _n8 in _needs:
                if _n8 not in _t8:
                    bad(_f8, '触发门判据缺「%s」（单词命中≠接管 / 越界按仲裁顺序）' % _n8)
        # 越界词只做初筛：仲裁顺序唯一副本在位，且不再自称「优先级最高」
        if not re.search(r'^\s*arbitration:', cfg, re.M):
            bad('config.yaml', '缺 trigger.arbitration（越界仲裁顺序唯一副本）')
        if '优先级最高' in cfg or '优先级最高' in _sk:
            bad('config.yaml', '越界表仍自称「优先级最高」（应为初筛，归属由主键终判）')
        if '初筛' not in _sk or '初筛' not in rd('library/domain-review.md'):
            bad('SKILL.md', '越界初筛语义未在 SKILL.md / domain-review.md 双处声明')

    # ---------- T 输出形态硬契约（全量输出块零内部名） ----------
    # 与 runcheck.py 的 L3-5 的差别：runcheck 只校验**首块**（正常路径示例），
    # 本组扫**全部**输出块（含边界 / 降级 / 拒绝示例），确保任何示例都不泄内部名。
    n_blk = 0
    for f in LOCAL:
        t = rd(f)
        for o in output_blocks(t):
            n_blk += 1
            lk = internal_leaks(o)
            if lk:
                bad(f, '输出块泄漏内部名 %d 处: %s' % (len(lk), '、'.join(lk[:6])))
            labels = re.findall(r'^【([^】]+)】', o, re.M)
            if labels and labels[0] != '结论' and '还需确认' not in labels[0]:
                bad(f, '输出块未「结论前置」（首节为【%s】）' % labels[0])
            if len([x for x in labels if '下一步' in x]) != 1:
                bad(f, '输出块【下一步】应恰好 1 个，实为 %d 个'
                    % len([x for x in labels if '下一步' in x]))
            if len([x for x in labels if x != '结论']) > 6:
                bad(f, '输出块要点 %d 条（>6，违 output-spec §1.1）' % len([x for x in labels if x != '结论']))
    if n_blk == 0:
        bad('（全域）', '未检出任何输出块（output-spec 契约无法落地）')

    # ---------- X 学生呈现层（体验层）----------
    # 防复发：92 个库内 skill 的输出块同时承担契约与渲染两职，前台白名单 / 禁止物 / 翻译规则
    # 无唯一副本、无断言 —— 体验层曾是全包唯一的「零断言层」。X 组把它钉住。
    XPATH = 'library/experience.md'
    if not os.path.exists(XPATH):
        bad('README.md', '缺少学生呈现层规则 %s（前台白名单 / 禁止物 / 翻译规则无唯一副本）' % XPATH)
    else:
        _xt = rd(XPATH)
        _xsec = (('白名单', r'^##\s*1[.、]?\s*前台白名单'),
                 ('禁止物', r'^##\s*2[.、]?\s*前台禁止物'),
                 ('翻译规则', r'^##\s*3[.、]?\s*翻译规则'),
                 ('三视图', r'^##\s*4[.、]?\s*三视图'),
                 ('反例', r'^##\s*5[.、]?\s*反例'),
                 ('起始句型', r'^##\s*6[.、]?\s*起始句型'))
        for _xk, _xpat in _xsec:
            if not re.search(_xpat, _xt, re.M):
                bad(XPATH, '缺小节「%s」（体验层六要素之一）' % _xk)
        if not _xt.startswith('#'):
            bad(XPATH, '首行不是标题（1 级规则文件不应含 frontmatter）')

        # 1 级清单三处必须同步（status 清单用全路径，库导航与规则文件表用文件名）
        if XPATH not in rd('scripts/qihang.sh'):
            bad('scripts/qihang.sh', 'cmd_status 的 [1级] 清单漏列 %s' % XPATH)
        _xname = os.path.basename(XPATH)
        if _xname not in rd('library/README.md'):
            bad('library/README.md', '1 级库导航漏列 %s' % XPATH)
        if _xname not in rd('SKILL.md'):
            bad('SKILL.md', '1 级规则文件表漏列 %s' % XPATH)

        # 输出契约两处指针必须指向唯一副本（渲染层规则可被 92 个 skill 顺链读到）
        _xops = rd('library/output-spec.md')
        if _xops.count(XPATH) != 2:
            bad('library/output-spec.md',
                '前台渲染口径指针应为 2 处（§1.4 降级标注 + 链接呈现规范外接标注），实测 %d'
                % _xops.count(XPATH))

        # 入口文案唯一副本：四处呈现位必须逐条含全部起始句型
        _xm = re.search(r'^##\s*6[.、]?\s*起始句型[^\n]*\n(.*?)(?=^##\s|\Z)', _xt, re.M | re.S)
        _xcanon = list(dict.fromkeys(re.findall(r'「([^」\n]+)」', _xm.group(1)))) if _xm else []
        if len(_xcanon) < 5:
            bad(XPATH, '起始句型清单少于 5 条（实测 %d，唯一副本失效）' % len(_xcanon))
        for _xf, _xlbl in (('README.md', 'README §2.1'),
                           ('SKILL.md', 'SKILL.md 统一快速入口'),
                           ('commands/qihang.md', '入口卡'),
                           ('scripts/qihang.sh', 'qihang.sh cmd_quick')):
            _xft = rd(_xf)
            _xmiss = [c for c in _xcanon if ('「%s」' % c) not in _xft]
            if _xmiss:
                bad(_xf, '%s 的起始句型与唯一副本不一致（缺 %s）' % (_xlbl, ' / '.join(_xmiss)))

        # 组数声明同源（防止新增组后文档计数漂移）
        _xngroups = 21
        if ('%d 组断言' % _xngroups) not in rd('README.md') or \
           ('%d 组断言' % _xngroups) not in rd('INSTALL.md'):
            warn('README.md', 'aligncheck 组数声明与实现不一致（期望「%d 组断言」）' % _xngroups)

    # ---------- Y 体验层闭环（B2/B3/C1/C2/C3）----------
    # 体验层的五条规则各自「只有一个副本 + 至少一处断言」，防止再次退化成零断言层。
    _cf = rd('config.yaml')
    _cl = rd('library/clarity.md')
    _mm = rd('library/memory.md')
    _lp = rd('library/login-policy.md')
    _sk = rd('SKILL.md')
    _xt = rd(XPATH)

    # [Y1] B2 澄清门：复述档必须是「实质歧义驱动」，且降级路径写清
    if '实质歧义' not in _cl:
        bad('library/clarity.md', '复述档未声明「实质歧义」判据（会退化为白复述）')
    if '无实质歧义' not in _cl or '免复述' not in _cl:
        bad('library/clarity.md', '复述档缺少「无实质歧义 → 直接执行（免复述）」降级路径')
    if '实质歧义' not in _cf:
        bad('config.yaml', '澄清门阈值注释未同步「实质歧义」语义')
    _y1 = section(_cl, r'^###\s*3\.1\s')
    if not _y1 or '**确定档**（降级）' not in _y1:
        bad('library/clarity.md', '§3.1 关系表缺少「确定档（降级）」一行')
    if not _y1 or '复述档的四条硬规格' not in _y1:
        bad('library/clarity.md', '§3.1 未把复述规格升级为「四条（含实质歧义）」')

    # [Y2] B3 记忆口径：续接固定回话唯一副本 + 三处同源
    _y2 = section(_mm, r'^###\s*3\.2\s*[^\n]*续接')
    if '续接固定回话' not in _mm:
        bad('library/memory.md', '缺少 §3.2「续接固定回话」唯一副本')
    if not _y2 or '不得假称记得' not in _y2:
        bad('library/memory.md', '§3.2 缺少「不得假称记得」硬约束')
    if not _y2 or '两条出路' not in _y2:
        bad('library/memory.md', '§3.2 缺少「必须给出两条出路」硬约束')
    if '`library/memory.md` §3.2' not in _sk:
        bad('SKILL.md', '会话连续性段落未指向 `library/memory.md` §3.2（口径未同源）')

    # [Y3] C1 越界仲裁：初筛 → 终判，且「优先级最高」已彻底退场
    if '仲裁顺序' not in _cf or '仲裁顺序' not in _sk:
        bad('config.yaml', '越界「仲裁顺序」未在 config.yaml / SKILL.md 双处声明')
    if '优先级最高' in _cf or '优先级最高' in _sk:
        bad('SKILL.md', '越界表仍自称「优先级最高」（应降级为初筛）')
    if not re.search(r'^\s*arbitration:', _cf, re.M):
        bad('config.yaml', '缺少 trigger.arbitration 键')
    _y3 = section(rd('library/domain-review.md'), r'^###\s*2\.1\s')
    if not _y3 or '初筛' not in _y3 or '终判' not in _y3:
        bad('library/domain-review.md', '§2.1 未声明「初筛 → 终判」仲裁语义')

    # [Y4] C2 登录交还：三步 + 固定一句话 + 交还优先于权限叙事
    if '交还三步' not in _lp:
        bad('library/login-policy.md', '缺少「交还三步」')
    if '看完了' not in _lp:
        bad('library/login-policy.md', '缺少交还固定一句话（唯一副本）')
    if '不想登录也告诉我，我给通用流程' not in _lp:
        bad('library/login-policy.md', '交还固定一句话措辞被改写（唯一副本失效）')
    if '交还话术**优先于**权限与安全叙事' not in _lp:
        bad('library/login-policy.md', '缺少「交还优先于权限叙事」的顺序声明')
    if '交还' not in section(_sk, r'^##\s*硬规则'):
        bad('SKILL.md', '硬规则未声明「看完之后的交还」')

    # [Y5] C3 体验层自检指标：5 项静态指标 + 零数据承诺 + 断言源交叉在位
    _y5 = section(_xt, r'^##\s*7[.、]?\s*体验层自检指标')
    if not _y5:
        bad(XPATH, '缺少 §7「体验层自检指标」')
    for _m in ('呈现层零内部名', '入口文案单源', '澄清门歧义驱动', '越界仲裁单点', '交还与记忆口径'):
        if _m not in _y5:
            bad(XPATH, '§7 指标表缺项：%s' % _m)
    if '零用户数据' not in _y5 or '默认不记录' not in _y5:
        bad(XPATH, '§7 未声明「零用户数据 / 默认不记录」')
    _y5src = rd('scripts/aligncheck.py') + rd('scripts/regress.sh')
    for _k in ('输出块泄漏内部名', '的起始句型与唯一副本不一致', '实质歧义', '仲裁顺序', '续接固定回话'):
        if _k not in _y5src:
            bad(XPATH, '§7 指标断言的断言源不成立（缺 %s）' % _k)

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
