# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 17 层 · 60 子代理盲跑归因修复】
# 依据：20 域 × 3 轮 = 60 个子代理盲跑（轮1 正常 / 轮2 边界歧义 / 轮3 红线越界）的返回值，
#       疑似项已回原始文件复核，只修「包的错」（代理侧问题不改）。
# 用法：python scripts/_build/v3/step54_blindrun_fixes.py [仓库根]
# 幂等：完成判据判定（已改则 MISS/SAME）。
#
# 确认的 5 处「包的错」：
#  D1 【假设】口径冲突（6 个域独立复现）：`output-spec` 说【假设】只在「3 轮未澄清」或「例外 3/5/6」出现、
#     「例外 2 不产生【假设】」；而 `clarity` §3.1 要求复述档「落【假设】」—— 而复述档的典型情形
#     （关键槽齐全、缺口全在 W/C/B）正是例外 2 → 二文件互斥。
#     → 修法：复述**改载于【结论】首行的前置短句**（不新增字段、不占【假设】），两文件口径对齐。
#  D2 澄清门「追问」与「复述档」的优先级未写明（S3 实测 C=0.77 却必须追问）。
#  D3 命中红线时「需求确定门」三种标注并存（不适用 / 追问档 / 确定档）→ 未写明「红线短路」。
#  D4 追问变体缺明文：不得同时出现【结论】（R3 实测出现【结论】+【还需确认】同现）。
#  D5 域红线体系漏洞：总览写「隐私（F4 F5 全包）」+ 代理靠总览拦住了 F3 的第三方聊天记录外传，
#     但 **F3 域文件与 F4 域文件的红线段都没有「第三方隐私不外传」条**（F5 有）→ 遗漏。补条并同步该域全部 skill。
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OLD, NEW, PKG = '3.2.2', '3.2.3', '3.2'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs, quiet=False):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for a, b in pairs:
        if a not in t:
            if not quiet:
                print('  [MISS] %s :: %r' % (rel, a[:56]))
            continue
        t = t.replace(a, b)
        if not quiet:
            print('  [OK]   %s :: %r' % (rel, a[:56]))
    if t != o:
        write(rel, t)


def edit_once(rel, marker, pairs, quiet=False):
    """**完成判据**：只有 marker 不在文件里才执行 pairs。

    ⚠️ 本层第 1 版对「锚点 + 新块」用裸 `edit()`，而新块**包含**锚点
    → 每跑一次多插一份（实测 output-spec 出现 3 份、regress 2 份、clarity 2 份）。
    这是本项目第 5 次踩「追加型替换」同型坑，故本层的插入型改动一律走 edit_once。"""
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    if marker in t:
        print('  [SAME] %s :: 已在位（%s）' % (rel, marker[:22])); return
    edit(rel, pairs, quiet=quiet)


# ---------------------------------------------------------------- D1 / D2 / D3
print('== D1/D2/D3) library/clarity.md §3.1 ==')
# ⚠️ 完成判据：该块已在位则跳过（追加型替换第 5 次复发的教训：锚点是新文本的子串时，
#    再跑一次就会插第二份）。
_cl_now = read('library/clarity.md') or ''
_cl_pairs = [
    # D1：复述载体改为【结论】首行前置短句（不再用【假设】）
    ('3. 复述落在输出的 **【假设】** 字段（`library/output-spec.md` 已有该字段）→ **不新增输出字段、不改输出硬契约**，也不出现内部名或过程叙述。',
     '3. 复述**并入【结论】首行的前置短句**（形如「按你给的 ⟨引用原话里的词⟩ —— ⟨结论⟩」）：'
     '**不新增输出字段、不改输出硬契约**，也不出现内部名或过程叙述。\n'
     '   > ⚠️ **不要用【假设】承载复述** —— 该字段的触发条件另有规定（见 `library/output-spec.md` §1.3），'
     '两者口径已对齐：复述是「先说清我理解的是什么」，【假设】是「代替用户补了对象或产出」。'),
    # D1 映射表措辞
    ('| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689` | 放行（例外 2） | **复述档**（一句话复述 + 落【假设】） |',
     '| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689` | 放行（例外 2） | **复述档**（一句话复述并入【结论】首行） |'),
    # D1 示例句
    ('> **注意例 A**：澄清门判「放行」（关键槽齐全），而 `C = 0.689 < 0.70` —— 此时**只复述、不追问**，',
     '> **注意例 A**：澄清门判「放行」（关键槽齐全），而 `C = 0.689 < 0.70` —— 此时**只复述、不追问**（复述并入【结论】首行），'),
    # D2 + D3：三条前置约定
    ('| **追问档** | `C < 0.70` | **仅当澄清门本就要追问时才追问**（判定不变）；若澄清门已放行（如例 A：关键槽齐全、仅次要槽缺）→ 按**复述档**处理，**不得新增追问** |',
     '| **追问档** | `C < 0.70` | **仅当澄清门本就要追问时才追问**（判定不变）；若澄清门已放行（如例 A：关键槽齐全、仅次要槽缺）→ 按**复述档**处理，**不得新增追问** |\n'
     '\n'
     '**三条前置约定（判定顺序在本门之前，实测易错，故写明）**：\n'
     '\n'
     '1. **红线优先 → 本门短路**：命中红线时**不计算 `C`、不标注档位**（记「**不适用**」），仍按 §7 直接拒绝 + 给合规替代。\n'
     '2. **先问后述**：澄清门判「**追问**」时，本门**不再复述** —— 追问已要求用户补充；复述档**只在澄清门已放行时**生效。\n'
     '3. **例外 6 视为达标**：通用知识型免复述（不因 `C` 未达 0.95 而要求确认）。'),
]
if '三条前置约定' in _cl_now:
    print('  [SAME] clarity §3.1 三条前置约定已在位')
else:
    edit('library/clarity.md', _cl_pairs)

# ---------------------------------------------------------------- D1 / D4
print('== D1/D4) library/output-spec.md ==')
edit_once('library/output-spec.md', '复述档」不计入本字段', [
    ('【假设】  出现条件：① 3 轮未澄清仍推进，或 ② 依 `clarity.md` §5 例外 **3 / 5 / 6** 直接推进、',
     '【假设】  出现条件：① 3 轮未澄清仍推进，或 ② 依 `clarity.md` §5 例外 **3 / 5 / 6** 直接推进、\n'
     '          ⚠️ **`clarity.md` §3.1 需求确定门的「复述档」不计入本字段** —— 复述并入【结论】首行的前置短句；\n'
     '          本字段只表示「**代替用户补齐了对象或产出**」，两者不要混用。\n'
     '          其余（'),
])
edit_once('library/output-spec.md', '追问变体的硬约束', [
    ('【还需确认】① … ② … ③ …（≤3 问，按 时间>对象>产出>约束>背景>任务 排序）',
     '【还需确认】① … ② … ③ …（≤3 问，按 时间>对象>产出>约束>背景>任务 排序）\n'
     '\n'
     '> **追问变体的硬约束**：**首节必须是【还需确认】**，且**不得同时出现【结论】** ——\n'
     '> 澄清门判「追问」时**不产出结论**（先问清再答）；若已有可先给的信息，放进【依据】，不要另起【结论】。'),
])

# ---------------------------------------------------------------- D1：regress [9] 断言同步
print('== D1) scripts/regress.sh [9] 断言同步 ==')
edit('scripts/regress.sh', [
    ("for _t in '一句话' '不得新增' '【假设】'; do",
     "for _t in '一句话' '不得新增' '【结论】首行的前置短句'; do"),
])
# [9] 追加：三条前置约定必须明文（防本轮 D2/D3 复发）—— 走 edit_once（完成判据）
edit_once('scripts/regress.sh', '前置约定已声明', [
    ('  grep -qF \'可复现自检问\' "$_cl" 2>/dev/null && _ok "已给出可复现自检问" || _fail "缺可复现自检问"',
     '  grep -qF \'可复现自检问\' "$_cl" 2>/dev/null && _ok "已给出可复现自检问" || _fail "缺可复现自检问"\n'
     '  # 三条前置约定（红线短路 / 先问后述 / 例外 6 免复述）必须明文\n'
     '  for _p in \'本门短路\' \'先问后述\' \'例外 6 视为达标\'; do\n'
     '    if grep -qF "$_p" "$_cl" 2>/dev/null; then _ok "前置约定已声明：$_p"\n'
     '    else _fail "前置约定缺：$_p"; fi\n'
     '  done'),
])

# ---------------------------------------------------------------- D5：F3 / F4 域红线补条 + 同步该域全部 skill
print('== D5) F3 / F4 域红线补「第三方隐私」条并同步该域全部 skill ==')
PRIV_F3 = '- **第三方隐私不外传**：不分析、不外传他人的聊天记录 / 健康状况 / 家庭与财务状况；遇「发到群里评理」这类请求 → 拒绝外传，改给**沟通话术**'
PRIV_F4 = '- **第三方隐私不外传**：不分析、不外传他人的财务与身份信息（含银行卡、身份证、家庭信息）；遇「帮我查这个卡号是谁的」这类请求 → 拒绝，改给**防诈与止损路径**'


def add_redline(dom, line):
    rel = 'domains/%s/_domain.md' % dom
    t = read(rel)
    if t is None:
        print('  [SKIP] %s' % rel); return
    if '第三方隐私不外传' in t:
        print('  [SAME] %s :: 隐私红线已在位' % rel); return
    m = re.search(r'(?ms)^(## ⚠️ 红线[^\n]*\n)(.*?)(?=^## |\Z)', t)
    if not m:
        print('  [MISS] %s :: 未找到红线段' % rel); return
    body = m.group(2).rstrip('\n')
    write(rel, t[:m.start(2)] + body + '\n' + line + '\n\n' + t[m.end(2):])
    print('  [OK]   %s :: 已补第三方隐私条' % rel)


def redsync(dom):
    """用域 `## ⚠️ 红线` 的 body 覆盖同域所有库内 skill 的对应段（保留 skill 自己的 header 行）。"""
    dt = read('domains/%s/_domain.md' % dom)
    m = re.search(r'(?ms)^(## ⚠️ 红线[^\n]*\n)(.*?)(?=^## |\Z)', dt)
    body = m.group(2).strip('\n')
    n = 0
    loc = os.path.join(ROOT, 'domains', dom, 'skills', 'local')
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (dom, s)
        t = read(rel)
        if t is None:
            continue
        sm = re.search(r'(?ms)^(## ⚠️ 红线[^\n]*\n)(.*?)(?=^## |\Z)', t)
        if not sm or sm.group(2).strip('\n') == body:
            continue
        write(rel, t[:sm.start(2)] + body + '\n\n' + t[sm.end(2):])
        n += 1
    print('  [OK]   %s :: 同步 %d 个 skill 的红线段' % (dom, n))


add_redline('F3-wellbeing', PRIV_F3)
add_redline('F4-money-safety', PRIV_F4)
redsync('F3-wellbeing')
redsync('F4-money-safety')

# ---------------------------------------------------------------- D3（盲跑另发现）：F8 示例与消歧表冲突
print('== D3) F8 interview-drill：裸「面试」示例与 `_registry.md` 消歧表对齐 ==')
edit('domains/F8-career/skills/local/interview-drill/SKILL.md', [
    ('> 下周有个面试，帮我练一下', '> 下周有个企业校招面试，帮我练一下'),
])
edit_once('domains/F8-career/skills/local/interview-drill/SKILL.md', '裸「面试」', [
    ('- 不覆盖：简历措辞（→`resume-tailor`）；编造经历（见红线）；升学面试（→`F7`）',
     '- 不覆盖：简历措辞（→`resume-tailor`）；编造经历（见红线）；升学面试（→`F7`）\n'
     '- **裸「面试」= 歧义**：须先 1 问区分升学 / 求职（消歧表见 `domains/_registry.md`），'
     '不得默认按求职直接演练'),
])

# ---------------------------------------------------------------- 版本号 3.2.2 → 3.2.3
print('== 版本号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        t = read(rel)
        if t is None:
            continue
        if 'version: %s' % OLD in t:
            write(rel, t.replace('version: %s' % OLD, 'version: %s' % NEW)); n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
edit('SKILL.md', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('.codebuddy-plugin/plugin.json', [('"version": "%s"' % OLD, '"version": "%s"' % NEW)])
edit('config.yaml', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('scripts/aligncheck.py', [
    ("!= '%s':" % OLD, "!= '%s':" % NEW),
    ("（期望 %s）' %% vm.group(1))" % OLD, "（期望 %s）' %% vm.group(1))" % NEW),
    ("vers - {'%s'}" % OLD, "vers - {'%s'}" % NEW),
    ("（期望 %s）' %% pv)" % OLD, "（期望 %s）' %% pv)" % NEW),
    ("not in ('%s', '%s')" % (PKG, OLD), "not in ('%s', '%s')" % (PKG, NEW)),
    ("m.group(1), '%s', '%s'))" % (PKG, OLD), "m.group(1), '%s', '%s'))" % (PKG, NEW)),
    ("期望包版本 %s 或修订号 %s" % (PKG, OLD), "期望包版本 %s 或修订号 %s" % (PKG, NEW)),
    ("'%s' not in v:" % OLD, "'%s' not in v:" % NEW),
    ("未声明版本 %s" % OLD, "未声明版本 %s" % NEW),
    ("修订号 = 三位（%s）" % OLD, "修订号 = 三位（%s）" % NEW),
])
edit('library/output-spec.md', [
    ('｜**修订号 = `%s`**（三位' % OLD, '｜**修订号 = `%s`**（三位' % NEW),
    ('（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD, '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
])

print('done')
