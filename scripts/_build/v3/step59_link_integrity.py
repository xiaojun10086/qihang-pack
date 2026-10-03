# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 22 层 · 链接可用性修复（v3.2.7 → v3.2.8）】
#
# 触发：用户实测反馈「给依据时的链接进不去」。逐项复现后确认**两个独立根因**：
#
#   缺陷 1【URL 紧贴中文】48 处 —— 写法为 `https://ecard.dlut.edu.cn/（余额/流水）`，
#     中间**没有空白**。聊天/编辑器自动链接会把中文说明一并吞进 href
#     （GFM 的 autolink 只在空白处收尾，全角括号不在其收尾标点集里）
#     → 生成的链接变成 `…/（余额/流水）` → 点开 404 = 「进不去」。
#
#   缺陷 2【仅 HTTP 站点被原样给出】35 处（jxgl 20 / lx 10 / map 5）——
#     实测这三个站**只服务 http**，`https://` 版本直接 **ECONNREFUSED**；
#     而浏览器「始终使用安全连接」等策略会把 http 自动升级为 https → 连接被拒。
#
# 修法（本层）：
#   A. **通用归一**：所有「URL 紧贴非空白字符」处插入一个空格（幂等，可复跑）。
#   B. **表册标注**：`jxgl / lx / map` 三行标 `仅 HTTP`，并新增「链接打不开怎么办（四步）」。
#   C. **输出契约**：`library/output-spec.md` 增「链接呈现规范」（URL 必须独占边界 + 访问条件标注）。
#   D. **防回归断言**：`scripts/aligncheck.py` 新增 URL 边界检查（命中即 FAIL）。
#   E. **负向自测**：`scripts/negative_test.py` 新增第 7 类注入（破坏 URL 边界 → 断言必须 FAIL）。
#   F. 修订号 3.2.7 → 3.2.8。
# 用法：python scripts/_build/v3/step59_link_integrity.py [仓库根]
# -------------------------------------------------------------------------------
import glob, io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD, NEW = '3.2.7', '3.2.8'

# URL 允许字符：ASCII 非空白，且**排除中文与中文标点、反引号、星号、尖括号、引号**
# （排除反引号/星号是为了不把 Markdown 标记吃进来；排除中文是为了能检出「紧贴」）
URLTOK = re.compile(r'https?://[^\s\u4e00-\u9fff\u3000-\u303f\uff00-\uffef`*<>"\']+')
TRAIL = ')]}>,.;:。，、；：）】》'
CJK = re.compile(r'[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]')


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(t)


def fix_line(line):
    """返回 (新行, 修复处数)。"""
    out, last, n = [], 0, 0
    for m in URLTOK.finditer(line):
        core = m.group(0).rstrip(TRAIL)
        if not core:
            continue
        tail_pos = m.start() + len(core)
        nxt = line[tail_pos:tail_pos + 1]
        bad = (tail_pos < m.end()) or (nxt and CJK.match(nxt))
        if not bad:
            continue
        out.append(line[last:tail_pos]); out.append(' ')
        last = tail_pos
        n += 1
    out.append(line[last:])
    return ''.join(out), n


print('== A) URL 边界归一（URL 与后续非空白字符之间插空格）==')
FILES = []
for pat in ('references/*.md', 'library/*.md', 'domains/*/_domain.md',
            'domains/*/skills/local/*/SKILL.md', 'commands/*.md'):
    FILES += glob.glob(os.path.join(ROOT, pat))
FILES += [os.path.join(ROOT, x) for x in ('SKILL.md', 'INSTALL.md', 'README.md', 'THIRD_PARTY_NOTICES.md')]
total, touched = 0, 0
for p in sorted(set(FILES)):
    if not os.path.isfile(p):
        continue
    t = io.open(p, 'r', encoding='utf-8').read()
    lines = t.split('\n')
    n = 0
    for i, l in enumerate(lines):
        nl, k = fix_line(l)
        if k:
            lines[i] = nl
            n += k
    if n:
        io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
        touched += 1
        total += n
        print('  [OK]   %-58s 修复 %d 处' % (os.path.relpath(p, ROOT).replace('\\', '/'), n))
print('  合计：%d 个文件 / %d 处（幂等：再跑应为 0）' % (touched, total))

print('== B) 表册：仅 HTTP 标注 + 链接排查话术 ==')
edit_pairs = [
    ('| 3 | 综合教学管理系统 | http://jxgl.dlut.edu.cn/student/home | ✅ **登录后实测可达**（含 学生信息 / 常用服务 / 所有服务） |',
     '| 3 | 综合教学管理系统 | http://jxgl.dlut.edu.cn/student/home | ✅ 可达（需登录）· **仅 HTTP**（https 实测连接被拒，勿手动改 https）；含 学生信息 / 常用服务 / 所有服务 |'),
    ('| 校园地图系统 | http://map.dlut.edu.cn/ | ✅ 可按楼宇查单位 |',
     '| 校园地图系统 | http://map.dlut.edu.cn/ | ✅ 可按楼宇查单位；**仅 HTTP**（https 实测超时，勿手动改 https） |'),
    ('| 离校系统 | http://lx.dlut.edu.cn/ | ✅ |',
     '| 离校系统 | http://lx.dlut.edu.cn/ | ✅ 可达（需登录）· **仅 HTTP**（https 实测连接被拒，勿手动改 https） |'),
]
t = read('references/dlut-official-sites.md')
if t is None:
    print('  [SKIP] 无 references/dlut-official-sites.md')
else:
    for a, b in edit_pairs:
        if b in t:
            print('  [SAME] %r' % a[:34]); continue
        if a not in t:
            print('  [MISS] %r' % a[:34]); continue
        t = t.replace(a, b, 1); print('  [OK]   %r' % a[:34])
    BLOCK = """
## 0.1 链接打不开怎么办（四步，2026-10-03 实测新增）

> 依据里的链接点不开是**已复现的真实缺陷**，按下面四步排查，**禁止臆造替代链接**：

1. **确认链接边界**：复制时不要把后面的中文说明一起带走（本表已保证 URL 与说明之间有空格；
   若你手抄过，务必只取到域名与路径为止）。
2. **若浏览器把 `http://` 自动升级成 `https://` 而打不开**：本站 `jxgl` / `lx` / `map` **只支持 http**
   （实测 `https://` 连接被拒）。请手动改回 `http://`，或从 `portal.dlut.edu.cn` 办事大厅进入。
3. **提示登录 / 只看到登录页**：先走统一身份认证 `https://sso.dlut.edu.cn/`，再从小事大厅进入对应业务。
4. **校外打不开（仅校园网）**：走 `https://webvpn.dlut.edu.cn/`；
   仍不可用则按固定话术回复「信息库未收录 / 该入口受限，建议访问 `https://www.dlut.edu.cn/` 核实」。

---
"""
    if '## 0.1 链接打不开怎么办' in t:
        print('  [SAME] 排查话术已存在')
    else:
        anchor = '| 备用 | i大工 APP | 应用商店搜「i大工」 | ✅ 场馆/心理/浴室预约等**仅 APP** |\n'
        if anchor in t:
            t = t.replace(anchor, anchor + BLOCK, 1)
            print('  [OK]   已插入「链接打不开怎么办（四步）」')
        else:
            print('  [MISS] 未找到 §0 表格锚点')
    write('references/dlut-official-sites.md', t)

print('== C) 输出契约：链接呈现规范 ==')
t = read('library/output-spec.md')
if t is None:
    print('  [SKIP] 无 library/output-spec.md')
elif '## 链接呈现规范' in t:
    print('  [SAME] 链接呈现规范已存在')
else:
    write('library/output-spec.md', t.rstrip('\n') + """

---

## 链接呈现规范（2026-10-03 新增 · 依据字段专用）

> 触发原因：实测「给依据时的链接进不去」。**根因是排版** —— URL 紧贴中文说明时，
> 渲染器会把中文一并算进链接地址，点开即 404。以下三条**必须遵守**：

1. **URL 必须独占边界**：URL 前后一律留**空格**，不得紧贴中文或中文标点。
   - ✅ `依据：https://ecard.dlut.edu.cn/ （余额与流水）`
   - ❌ 写完 URL 直接把中文说明接上、中间不留空格 —— 渲染器会把说明一起算进链接地址
2. **必须标注访问条件**：需登录标 `需登录`；只支持 http 的标 `仅 HTTP`（勿手动改 https）；
   仅校园网的标 `仅校园网（走 WebVPN）`。**不得把受限入口写成"可直接打开"**。
3. **打不开时给排查路径，不给替代链接**：按 `references/dlut-official-sites.md` §0.1 的四步排查回复；
   **禁止**臆造 URL、禁止凭模型记忆补链接。本包未收录时，固定回复
   「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」。
""")
    print('  [OK]   已追加「链接呈现规范」')

print('== D) aligncheck：URL 边界断言 ==')
t = read('scripts/aligncheck.py')
if t is None:
    print('  [SKIP] 无 scripts/aligncheck.py')
elif 'URL 紧贴中文/标点' in t:
    print('  [SAME] 断言已存在')
else:
    ANCHOR = '    # ---------- G 交叉引用 ----------'
    BLOCK = """    # ---------- F2 URL 呈现边界（2026-10-03 实测缺陷）----------
    # 触发原因：依据里的 URL 紧贴中文说明时，渲染器会把中文吞进 href → 点开 404。
    # 判据：URL 之后**要么是空白/表格竖线/行尾，要么先补一个空格**；URL 末尾不得紧跟收尾标点。
    _trail = ')]}>,.;:。，、；：）】》'
    _badurl = 0
    for _f in MD:
        for _i, _ln in enumerate(rd(_f).split('\\n'), 1):
            for _m in re.finditer(r'https?://[^\\s\\u4e00-\\u9fff\\u3000-\\u303f\\uff00-\\uffef`*<>"\\']+', _ln):
                _core = _m.group(0).rstrip(_trail)
                if not _core:
                    continue
                _tp = _m.start() + len(_core)
                _nx = _ln[_tp:_tp + 1]
                if _tp < _m.end() or (_nx and re.match(r'[\\u4e00-\\u9fff\\u3000-\\u303f\\uff00-\\uffef]', _nx)):
                    _badurl += 1
                    if _badurl <= 6:
                        bad(_f, 'URL 与后续中文/标点之间缺空白（第 %d 行）→ 渲染时会被吞进链接' % _i)
    if _badurl:
        bad('（URL 边界）', '共 %d 处 URL 紧贴中文/标点，须在 URL 后补空格' % _badurl)

"""
    if ANCHOR in t:
        write('scripts/aligncheck.py', t.replace(ANCHOR, BLOCK + ANCHOR, 1))
        print('  [OK]   已插入 F2 URL 边界断言')
    else:
        print('  [MISS] 未找到 G 组锚点')

print('== E) negative_test：第 7 类注入 ==')
t = read('scripts/negative_test.py')
if t is None:
    print('  [SKIP] 无 scripts/negative_test.py')
elif 'inject_url_boundary' in t:
    print('  [SAME] 注入项已存在')
else:
    A1 = 'def inject_missing_fallback(tree):'
    B1 = """def inject_url_boundary(tree):
    \"\"\"把一条 URL 与紧随其后的中文说明贴在一起（模拟「依据里的链接被渲染器吞掉」）。
    期望：aligncheck 的 URL 边界断言 FAIL。\"\"\"
    p = os.path.join(tree, 'domains', 'F4-money-safety', '_domain.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t + '\\n- 负向测试注入：https://www.dlut.edu.cn/（URL 紧贴中文，应触发 URL 边界断言）\\n'


def inject_missing_fallback(tree):"""
    A2 = "        ('隔离校验缺失（--profile 可被 daemon 静默忽略）', inject_no_isolation,"
    B2 = ("        ('URL 紧贴中文（依据里的链接会被渲染器吞掉）', inject_url_boundary,\n"
          "         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck F2'),\n"
          "        ('隔离校验缺失（--profile 可被 daemon 静默忽略）', inject_no_isolation,")
    ok = True
    for a, b in ((A1, B1), (A2, B2)):
        if a not in t:
            print('  [MISS] %r' % a[:36]); ok = False
    if ok:
        for a, b in ((A1, B1), (A2, B2)):
            t = t.replace(a, b, 1)
        write('scripts/negative_test.py', t)
        print('  [OK]   已加第 7 类注入')

print('== F) 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        x = read(rel)
        if x and 'version: %s' % OLD in x:
            write(rel, x.replace('version: %s' % OLD, 'version: %s' % NEW)); n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD, 'version: %s' % NEW),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD, '"version": "%s"' % NEW),
        ('config.yaml', 'version: %s' % OLD, 'version: %s' % NEW),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD, '**修订号 = `%s`**' % NEW),
        ('library/output-spec.md', '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD,
         '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
):
    x = read(rel)
    k = 0
    if x and a in x:
        write(rel, x.replace(a, b)); k = x.count(a)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

print('done')
