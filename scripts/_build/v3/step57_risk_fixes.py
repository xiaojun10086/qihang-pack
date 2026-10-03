# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 20 层 · 风险自检修复（v3.2.5 → v3.2.6）】
# 依据：`巡检报告/风险自检-2026-10-03.md` 的 R-1…R-7。本层固化**产品文件**侧的修复；
#      构建侧（release_branch.py 的 EXCL、发布口径）由该脚本自身承载，不在本层。
# 用法：python scripts/_build/v3/step57_risk_fixes.py [仓库根]
# 幂等：插入/改写均带**哨兵**（幂等判据不看整块内容）；版本号用**全部替换**。
#
# 本轮产品侧改动：
#   R-2  `.gitignore` 增补 `.learnbuddy/`（记忆不跟踪）—— 防本机路径再次入库
#   R-4  `INSTALL.md` §六 增「校内站点协议」行（如实登记 http 站点，提示网络环境）
#   R-5  `INSTALL.md` §六 「私密站」行明确标注**可选功能**（与「零外部依赖」口径对齐）
#   R-2' `.gitattributes` 注释纠错：原文写「本文件不随包分发」与事实矛盾
#        （它**必须**随包：用户 clone 后要靠它锁 LF。实测移出后交付树 160 文件变 CRLF）
#   P    修订号 3.2.5 → 3.2.6（92 库内 skill + 根 SKILL.md + plugin.json + config.yaml + output-spec）
# -------------------------------------------------------------------------------
import os, io, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD, NEW = '3.2.5', '3.2.6'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r' % (rel, sent[:40])); continue
        if b in t:
            print('  [SAME] %s :: %r' % (rel, a[:40])); continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:40])); continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:40]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


# ---------------------------------------------------------------- R-1 附带：记忆不跟踪
print('== R-1) .gitignore 增补 .learnbuddy/ ==')
edit('.gitignore', [
    ('# 构建缓存', '# 项目记忆（含本机路径等信息）—— **不随包分发、永不入库**。\n'
     '# 2026-10-03 起由「跟踪」改为「不跟踪」：此前它被跟踪并推送到公开仓库，导致本机路径外泄。\n'
     '.learnbuddy/\n'
     '\n'
     '# 构建缓存',
     '永不入库'),
])

# ---------------------------------------------------------------- R-4 / R-5：INSTALL §六
print('== R-4/R-5) INSTALL.md §六 前置条件 ==')
edit('INSTALL.md', [
    ('| 网络 | 库内 skill 全程离线可用 |\n'
     '| 私密站（需登录） | 需 `agent-browser` 或同类浏览器自动化；'
     '**必须用独立 Profile**（见 `references/dlut-login-sites.md` §0.1） |',
     '| 网络 | 库内 skill 全程离线可用（**核心能力不触网**） |\n'
     '| 私密站（需登录）· **可选功能** | **属可选增强：不装也不影响核心能力**。'
     '需 `agent-browser` 或同类浏览器自动化（`npm i -g agent-browser`）；'
     '**必须用独立 Profile**（见 `references/dlut-login-sites.md` §0.1） |\n'
     '| 校内站点协议 | 部分校内系统**仅提供 `http://`**（教务 / 财务 / 缴费 / 信息服务等，'
     '域名均为 `*.dlut.edu.cn`）→ **访问时注意网络环境**；本包**不改写**站点协议，只如实登记 |',
     '可选功能'),
])

# ---------------------------------------------------------------- R-2'：.gitattributes 注释纠错
print('== R-2\') .gitattributes 注释纠错 ==')
edit('.gitattributes', [
    # (a) 去掉过期的「两处记忆必须同源」推理（两目录线已退役），改为口径正确的后果说明
    ('#   2) `.learnbuddy/memory/*.md` 变 CRLF → 与交付副本（LF）**不再逐字节一致**，\n'
     '#      违反「两处记忆必须同源」铁律（副本不含 .learnbuddy，不会自动跟随）。',
     '#   2) 文档与规则文件变 CRLF → 与仓库基线不再逐字节一致，比对与 diff 全乱。'),
    # (b) 纠错：「本文件不随包分发」与事实相反 —— 它**必须**随包（用户 clone 后要靠它锁 LF）
    ('# 故对代码与文档显式锁定 LF；`.gitattributes` 本身不随包分发。',
     '# 故对代码与文档显式锁定 LF。\n'
     '# ⚠️ **本文件随包分发**（交付树必需）：用户 clone 后同样要靠它保证 LF；\n'
     '#    实测把它移出交付树 → 交付包 160 个文件变 CRLF、`*.sh` 直接不可执行。'),
], )

# ---------------------------------------------------------------- 构建侧文档里的计数同步
print('== 计数同步）_build/README.md 与 release_branch.py 的 174 → 173 ==')
for rel in ('scripts/_build/README.md', 'scripts/_build/v3/release/release_branch.py'):
    n = replace_all(rel, '= **174 文件**', '= **173 文件**')
    n += replace_all(rel, '当前 174', '当前 173')
    n += replace_all(rel, '交付 174 文件', '交付 173 文件')
    print('  %s：%d 处' % (rel, n))

# ---------------------------------------------------------------- P：修订号 3.2.5 → 3.2.6
print('== P) 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        if replace_all('domains/%s/skills/local/%s/SKILL.md' % (d, s),
                       'version: %s' % OLD, 'version: %s' % NEW):
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD, 'version: %s' % NEW),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD, '"version": "%s"' % NEW),
        ('config.yaml', 'version: %s' % OLD, 'version: %s' % NEW),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD, '**修订号 = `%s`**' % NEW),
        ('library/output-spec.md', '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD,
         '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
        ('scripts/_build/README.md', '3.2.4 → 3.2.5', '3.2.5 → 3.2.6'),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s :: %r ×%d' % ('OK' if k else '--', rel, a[:44], k))

print('done')
