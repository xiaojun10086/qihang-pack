# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 14 层 · 版本号与计数级联】统一版本口径 + library 计数 9 → 10
# 用法：python scripts/_build/v3/step51_version_bump.py [仓库根]
# 幂等：在已达本层的树上重跑为 MISS（无害），不产生二次改写。
#
# ★ 版本号口径（v3.2 起统一，改版本必须四处同改）★
#   · **包版本 = 3.2**（两位）—— 用于**包名与展示位**：README 标题 / 包根 SKILL.md 标题 /
#     `qihang.sh` 状态行 / `config.yaml` 首行注释 / 记忆与文档里的「包版本」。
#   · **修订号 = 3.2.0**（三位）—— 用于**机器可读字段与校验断言**：92 个库内 SKILL.md frontmatter、
#     包根 SKILL.md frontmatter、`.codebuddy-plugin/plugin.json`、`config.yaml` 的 `version:`、
#     `scripts/aligncheck.py` 的期望值。
#   · 两者**同一条线**：修订号 = 包版本 + `.0`（3.2 → 3.2.0）。**不得再出现第二个版本数字**
#     （原 `library/output-spec.md` 的独立「输出标准修订 v3.1.0」已并入 `3.2.0`）。
# 历史陈述不追改：`自 v3.0.0 起…`（skill-compliance-audit / THIRD_PARTY_NOTICES）描述的是当时的变更。
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OLD = '3.0.0'                       # 起始版本号（v3.0.0 树）
PKG = '3.2'                         # 包版本（两位 · 展示位）
REV = '3.2.0'                       # 修订号（三位 · 字段与断言）
MID = '3.2.0'                       # 中间态：曾把展示位也写成三位，需归一回两位


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


# ------------------------------------------------ 1) 92 个库内 SKILL.md（修订号）
print('== 1) 库内 SKILL.md frontmatter 修订号 → %s ==' % REV)
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
            write(rel, t.replace('version: %s' % OLD, 'version: %s' % REV))
            n += 1
print('  改写 %d 个（应为 92）' % n)

# ------------------------------------------------ 2) 包根 SKILL.md（字段三位 + 标题两位）
print('== 2) 包根 SKILL.md ==')
edit('SKILL.md', [
    ('version: %s' % OLD, 'version: %s' % REV),
    ('# 「启航」学伴包 · 入口（v%s）' % MID, '# 「启航」学伴包 · 入口（v%s）' % PKG),
    ('# 「启航」学伴包 · 入口（v%s）' % OLD, '# 「启航」学伴包 · 入口（v%s）' % PKG),
])

# ------------------------------------------------ 3) 其余机器字段（修订号三位）
print('== 3) 其余机器字段 ==')
edit('.codebuddy-plugin/plugin.json', [('"version": "%s"' % OLD, '"version": "%s"' % REV)])
# config.yaml：头部注释块用**整体归一**（不用「插入型替换」）。
# 教训：本层第一版用 `replace(锚点, 锚点+新块)` —— 新串包含旧串 → 每跑一次多插一份，
# 实测把 `version:` 插成两个（YAML 重复键）。这正是本包铁律「追加型替换必须加完成判据」的复发。
CFG_HEAD_TMPL = ('# 「启航」学伴包 v%s · 唯一需要按学期 / 课程修改的文件\n'
                 '# 新学期执行 `bash scripts/qihang.sh new-term` 会先备份再提示重置。\n'
                 '# version 字段 = **修订号**（三位，与 frontmatter / plugin.json 一致）；\n'
                 '# 包版本为两位形态（见 README 标题）。改版本时两处同改。\n'
                 'version: %s\n\n')
_cfg = read('config.yaml')
if _cfg is None:
    print('  [SKIP] config.yaml（不存在）')
else:
    _i = _cfg.find('# ============ 学校绑定')
    # ⚠️ 必须**保留文件里既有的修订号**：本层是「头部整体归一」，若把版本硬写成自己的 `REV`，
    # 后续层（step52/step53…）升过的更高修订号会被**改回去** → 链第 1 遍变更 1 个文件
    # （实测：3.2.2 被改回 3.2.1）。归一的是**格式**，不是**版本值**。
    _vm = re.search(r'^version:\s*([\d.]+)', _cfg, re.M)
    _ver = _vm.group(1) if _vm else REV
    _head = CFG_HEAD_TMPL % (PKG, _ver)
    if _i < 0:
        print('  [MISS] config.yaml :: 未找到「学校绑定」锚点')
    elif _cfg[:_i] != _head:
        write('config.yaml', _head + _cfg[_i:])
        print('  [OK]   config.yaml :: 头部归一（单一个 version 键，保留修订号 %s）' % _ver)
    else:
        print('  [SAME] config.yaml :: 头部已归一')

# aligncheck 的期望值（三处断言 + 两处提示语）
edit('scripts/aligncheck.py', [
    ("if vm and vm.group(1) != '%s':" % OLD, "if vm and vm.group(1) != '%s':" % REV),
    ("bad(f, '版本号 %%s（期望 %s）' %% vm.group(1))" % OLD, "bad(f, '版本号 %%s（期望 %s）' %% vm.group(1))" % REV),
    ("if vers - {'%s'}:" % OLD, "if vers - {'%s'}:" % REV),
    ("if pv != '%s':" % OLD, "if pv != '%s':" % REV),
    ("bad('.codebuddy-plugin/plugin.json', 'version = %%s（期望 %s）' %% pv)" % OLD,
     "bad('.codebuddy-plugin/plugin.json', 'version = %%s（期望 %s）' %% pv)" % REV),
    ("if m and m.group(1) != '%s':" % OLD, "if m and m.group(1) != '%s':" % REV),
    ("bad(_vf, '版本声明 %%s（期望 %s）' %% m.group(1))" % OLD,
     "bad(_vf, '版本声明 %%s（期望 %s）' %% m.group(1))" % REV),
    ("if '%s' not in v:" % OLD, "if '%s' not in v:" % REV),
    ("warn('.codebuddy-plugin/plugin.json', '未声明版本 %s')" % OLD,
     "warn('.codebuddy-plugin/plugin.json', '未声明版本 %s')" % REV),
])

# ------------------------------------------------ 4) 展示位归一为两位包版本
print('== 4) 展示位归一：三位 → 两位包版本 %s ==' % PKG)
edit('README.md', [
    ('# 「启航」新生学习生活一体化学伴包 v%s' % MID, '# 「启航」新生学习生活一体化学伴包 v%s' % PKG),
    ('# 「启航」新生学习生活一体化学伴包 v%s' % OLD, '# 「启航」新生学习生活一体化学伴包 v%s' % PKG),
])
edit('scripts/qihang.sh', [
    ('# 「启航」学伴包 v%s · 三级结构管理脚本' % MID, '# 「启航」学伴包 v%s · 三级结构管理脚本' % PKG),
    ('# 「启航」学伴包 v%s · 三级结构管理脚本' % OLD, '# 「启航」学伴包 v%s · 三级结构管理脚本' % PKG),
    ('echo "「启航」学伴包 v%s · 状态"' % MID, 'echo "「启航」学伴包 v%s · 状态"' % PKG),
    ('echo "「启航」学伴包 v%s · 状态"' % OLD, 'echo "「启航」学伴包 v%s · 状态"' % PKG),
])

# ------------------------------------------------ 5) output-spec：口径统一
print('== 5) library/output-spec.md：修订号并入 %s ==' % REV)
edit('library/output-spec.md', [
    ('> **输出标准修订 v3.1.0** —— 此号**仅标识本规范的第 2 次重设计**，**与包版本互不相同源**（**包版本 = 3.2.0**）。\n'
     '> ⚠️ 两个版本号**不同源**：`3.1.0` 指本规范的修订序号，`3.2.0` 指整个学伴包的版本；引述时请写明限定词，勿简写成「v3.1」。',
     '> **版本口径（v3.2 起统一）**：**包版本 = `3.2`**（两位 —— 用于包名与展示位）｜**修订号 = `3.2.0`**（三位 —— 用于 frontmatter / `plugin.json` / 校验断言）。\n'
     '> 本规范**不另设修订号**，随包版本同一条线：包 `3.2` 对应修订 `3.2.0`。\n'
     '> 此前写作「输出标准修订 v3.1.0」的独立号**已并入 `3.2.0`**，勿再引用 v3.1。'),
])

# ------------------------------------------------ 6) library 计数 9 → 10
print('== 6) library 文件数 9 → 10 ==')
edit('scripts/selfcheck.sh', [
    ('[ "${libn:-0}" -eq 9 ] && ok "library 文件数 = 9" || warn "library 文件数 = $libn（期望 9）"',
     '[ "${libn:-0}" -eq 10 ] && ok "library 文件数 = 10" || warn "library 文件数 = $libn（期望 10）"'),
])
edit('scripts/regress.sh', [
    ('_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 9',
     '_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 10'),
])
edit('INSTALL.md', [
    ('**期望**：`[1级]` 逐行列出 **8 个** library 文件',
     '**期望**：`[1级]` 逐行列出 **9 个** library 文件'),
], quiet=True)

# ------------------------------------------------ 7) aligncheck：固化版本口径断言
print('== 7) scripts/aligncheck.py：版本口径一致性断言（包版本两位 / 修订号三位）==')
CONSIST = """    # 版本号口径（v3.2 起统一）：包版本 = 两位（3.2）｜修订号 = 三位（3.2.0）
    # 展示位写三位 = 口径漂移（正是「包版本与修订号不统一」的复发点），故在此硬断言。
    _rfm = re.match(r'^---\\n(.*?)\\n---', rd('SKILL.md'), re.S)
    _rev = None
    if _rfm:
        _m = re.search(r'^version:\\s*([\\d.]+)', _rfm.group(1), re.M)
        if _m:
            _rev = _m.group(1)
    if _rev:
        _pkg = '.'.join(_rev.split('.')[:2])
        for _f, _pat in (('README.md', r'学伴包 v([\\d.]+)'),
                         ('SKILL.md', r'入口（v([\\d.]+)）'),
                         ('scripts/qihang.sh', r'学伴包 v([\\d.]+)')):
            _h = re.search(_pat, rd(_f))
            if not _h:
                warn(_f, '未找到包版本展示位（期望两位形态 v%s）' % _pkg)
            elif _h.group(1) != _pkg:
                bad(_f, '包版本展示 %s（应为两位 v%s；三位 %s 只用于修订号）'
                    % (_h.group(1), _pkg, _rev))
"""
edit('scripts/aligncheck.py', [
    ("    _vf = 'qihang-scenario-design.html'\n"
     "    if os.path.exists(_vf):\n"
     "        m = re.search(r'<title>[^<]*（v([\\d.]+)）', rd(_vf))\n"
     "        if m and m.group(1) != '%s':\n"
     "            bad(_vf, '版本声明 %%s（期望 %s）' %% m.group(1))" % (REV, REV),
     "    _vf = 'qihang-scenario-design.html'\n"
     "    if os.path.exists(_vf):\n"
     "        m = re.search(r'<title>[^<]*（v([\\d.]+)）', rd(_vf))\n"
     "        if m and m.group(1) not in ('%s', '%s'):\n"
     "            bad(_vf, '版本声明 %%s（期望包版本 %s 或修订号 %s）' %% (m.group(1), '%s', '%s'))\n"
     % (PKG, REV, PKG, REV, PKG, REV) + CONSIST),
])

print('done')
