#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」build_phase17 —— 漏检缺陷修复层（v2.8 → v2.9）

背景：第 4 轮「独立会话只读复核」发现 20 项**脚本查不出**的缺陷。其中 4 项本身就是
`aligncheck.py` 断言集的盲区（白名单 + 窄正则 + 无文件数断言），所以本层优先加固检查器，
再修被它漏掉的内容问题。

本层做六件事：
  1. **检查器加固**：`aligncheck.py` 的「声明==实测」由**文件名白名单**改为**全量扫描 + 内容标记豁免**
     （文件级「历史文档」/ 行级「历史口径」）；正则放宽到「公开站…N 条」类表述；新增文件总数断言。
  2. **L3 清单去重与统一**：`SKILL.md` / `PROJECT.md` 重复的「成绩明细 / 成绩明细」；`README.md` 残缺的 5 项清单。
  3. **口径统一**：适配权重 0.35→0.45（与 19 份 `external.md` 的公式一致）；
     库外域数 14→12；修复项数 52/17→由 `build_phase15.py` 章节数与 `review-report-v2.4.md` 枚举**推导**；
     `ROADMAP` 里残留的「公开站 160 条」。
  4. **qihang.sh 可复现性**：`cmd_records()` 与 `records)` 分派原先**不在任何生成器里**，全量重跑会丢失；
     `cmd_registry` 仍按「全文出现次数」统计 ✅/⚠️（得 71/26，正确 67/21）。
  5. **PROJECT 结构漂移**：工作流 7 步→8 步、「四件事」只列 3 件、「每域 1 个库内 skill」、目录树漏登记 9 份 references。
  6. **版本号 2.8.0 → 2.9.0**，以及 `_build/README.md` 构建链加入本层。

原则（与 phase15/16 一致）：
  · 每条改动是**精确匹配替换**；匹配不到就报 MISS（不静默跳过）
  · **幂等**：重复运行结果一致；第二遍必须 0 变更
  · 不触碰历史层（`build_phase16.py`）与历史报告里刻意保留的旧数字
用法: python scripts/_build/build_phase17.py .

⚠️ **执行顺序约束**：本层必须在 `build_phase18.py` **之前**运行。
在 v2.10 树上**单独**重跑本层，会因「版本号 / 构建链文本」已被 phase18 改写而报 4 处 MISS —— 属预期，不是缺陷。
（链内不会发生：17 永远在 18 前拿到 v2.9 版文本。）
"""
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
OK, MISS, DONE = [], [], []


def rd(p):
    with open(os.path.join(ROOT, p), 'r', encoding='utf-8') as f:
        return f.read()


def wr(p, s):
    with open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def rep(path, old, new, label='', required=True, already=None, already_re=None):
    """精确替换 + 幂等。

    完成判据（任一成立即视为已应用，不再改写）：
      · `already` 给定且已在文本中；· `already_re` 正则命中（用于「已被下游层超越」的情形）；
      · `new` 已在文本中。
    否则：`old` 存在 → 替换（OK）；不存在 → MISS（required=False 时降级为提示）。
    """
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        MISS.append('%s :: 文件不存在（%s）' % (path, label))
        return
    t = rd(path)
    if (already and already in t) or (already_re and re.search(already_re, t)) or (new and new in t):
        DONE.append('%s :: %s' % (path, label or old[:28]))
        return
    if old in t:
        wr(path, t.replace(old, new, 1))
        OK.append('%s :: %s' % (path, label or old[:28]))
    elif required:
        MISS.append('%s :: %s' % (path, label or old[:28]))
    else:
        DONE.append('%s :: %s（无需改）' % (path, label or old[:28]))


def ensure_before(path, needle, block, anchors, label=''):
    """若 `needle` 不在文本中，则把 `block` 插到第一个命中的 anchor 之前（幂等）。"""
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        MISS.append('%s :: 文件不存在（%s）' % (path, label))
        return
    t = rd(path)
    if needle in t:
        DONE.append('%s :: %s' % (path, label))
        return
    for a in anchors:
        if a in t:
            wr(path, t.replace(a, block + a, 1))
            OK.append('%s :: %s' % (path, label))
            return
    MISS.append('%s :: %s（无可用锚点）' % (path, label))


def product_files():
    """产品文件数口径：排除 .git / .idea / .learnbuddy / __pycache__（与 aligncheck 一致）。"""
    n = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        n += len(files)
    return n


# ==================================================================== 1. 检查器加固（先做，后面靠它验证）
def fix_aligncheck():
    """把「声明==实测」从白名单改为全量扫描 + 内容标记豁免，并加文件总数断言。"""
    p = 'scripts/aligncheck.py'
    t = rd(p)

    # 1.1 目录排除：.idea / .learnbuddy 也排除（非交付物，且记忆日志会带来假阳性）
    rep(p,
        "        dirs[:] = [d for d in dirs if d not in ('.git', '__pycache__')]",
        "        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]",
        'aligncheck 排除 .idea/.learnbuddy')

    t = rd(p)
    if 'v2.9.2 全量扫描' in t:
        DONE.append('%s :: 声明==实测 全量扫描（已应用）' % p)
    else:
        cands = [t.find(mk) for mk in ("    # v2.9", "    CLAIM_FILES = ['PROJECT.md'")]
        cands = [c for c in cands if c >= 0]
        a1 = "    # ---------- 汇总 ----------"
        if not cands or a1 not in t:
            MISS.append('%s :: 声明==实测 区块锚点缺失' % p)
        else:
            i0, i1 = min(cands), t.index(a1)
            new_block = (
                "    # v2.9.2 全量扫描：不再用**文件名白名单**（旧版只查 7 个文件，ROADMAP / references\n"
                "    # 全在射程外）。改为「全量扫描 + 内容标记豁免」，豁免必须**写在文件里**：\n"
                "    #   · 文件级：前 20 行含「历史文档」→ 整文件豁免\n"
                "    #   · 行级  ：该行或其前 2 行含「历史口径」→ 该处豁免\n"
                "    # 另：分项口径（已核验 / 待核实 / 未标注）用**派生值**断言，杜绝「72/23/65 加不到 139」。\n"
                "    UNMARKED = ENTRIES - OK_N - WARN_N\n"
                "    _SUBSET = re.compile(r'待核实|未核实|已核验|未标注|学院类|清单|小节')\n"
                "    for f in [x for x in (MD + [y for y in FILES if y.endswith('.html')])]:\n"
                "        if not os.path.exists(f):\n"
                "            continue\n"
                "        t = rd(f)\n"
                "        lines = t.split('\\n')\n"
                "        if any('历史文档' in l for l in lines[:20]):\n"
                "            continue\n"
                "\n"
                "        def _exempt(i, _ls=lines):\n"
                "            return any('历史口径' in _ls[j] for j in range(max(0, i - 2), i + 1))\n"
                "\n"
                "        for i, ln in enumerate(lines):\n"
                "            if _exempt(i):\n"
                "                continue\n"
                "            for pat, exp, nm in (\n"
                "                (r'(\\d{2,4})\\s*条\\s*表格行', ROWS, '表格行'),\n"
                "                (r'表格行\\s*[:：]?\\s*\\*{0,2}(\\d{2,4})', ROWS, '表格行'),\n"
                "                (r'表格总行数[:：]\\s*\\*{0,2}(\\d{2,4})', ROWS, '表格行'),\n"
                "                (r'(\\d{2,4})\\s*条\\s*条目', ENTRIES, '条目'),\n"
                "                (r'数据条目\\s*[:：]?\\s*\\*{0,2}(\\d{2,4})', ENTRIES, '条目'),\n"
                "            ):\n"
                "                for m in re.finditer(pat, ln):\n"
                "                    v = int(next(g for g in m.groups() if g))\n"
                "                    if v != exp:\n"
                "                        bad(f, '%s声明 %d ≠ 实测 %d（行 %d：%s）'\n"
                "                            % (nm, v, exp, i + 1, ln.strip()[:60]))\n"
                "            for pat, exp, nm in (\n"
                "                (r'已核验\\s*[:：]?\\s*\\*{0,2}(\\d{1,3})\\s*条', OK_N, '已核验'),\n"
                "                (r'待核实\\s*[:：]?\\s*\\*{0,2}(\\d{1,3})\\s*条', WARN_N, '待核实'),\n"
                "                (r'未标注\\s*[:：]?\\s*\\*{0,2}(\\d{1,3})\\s*条', UNMARKED, '未标注'),\n"
                "            ):\n"
                "                for m in re.finditer(pat, ln):\n"
                "                    if int(m.group(1)) != exp:\n"
                "                        bad(f, '%s声明 %s ≠ 实测 %d（行 %d：%s）'\n"
                "                            % (nm, m.group(1), exp, i + 1, ln.strip()[:60]))\n"
                "            # 总量口径：提到「公开站 / 信息库」且**不是**分项小节的句子，\n"
                "            # 其中的「N 条」必须等于表格行数或条目数。\n"
                "            if re.search(r'公开站|信息库|official-sites', ln) and not _SUBSET.search(ln):\n"
                "                for m in re.finditer(r'(\\d{2,4})\\s*条', ln):\n"
                "                    v = int(m.group(1))\n"
                "                    if v not in (ROWS, ENTRIES):\n"
                "                        bad(f, '公开站总量 %d ≠ 实测（表格行 %d / 条目 %d）（行 %d：%s）'\n"
                "                            % (v, ROWS, ENTRIES, i + 1, ln.strip()[:60]))\n"
                "            for m in re.finditer(r'✅\\s*(\\d{1,3})\\s*/\\s*⚠️\\s*(\\d{1,3})', ln):\n"
                "                if int(m.group(1)) != OK_N or int(m.group(2)) != WARN_N:\n"
                "                    bad(f, '✅/⚠️ 声明 %s/%s ≠ 实测(表内) %d/%d（行 %d）'\n"
                "                        % (m.group(1), m.group(2), OK_N, WARN_N, i + 1))\n"
                "\n"
                "    # §8 未核实清单：标题声明的项数 == 清单实际项数；各处引用的项数也必须一致\n"
                "    if os.path.exists('references/dlut-official-sites.md'):\n"
                "        _st = rd('references/dlut-official-sites.md')\n"
                "        _h = re.search(r'^## 8\\.\\s*([^\\n]+)$', _st, re.M)\n"
                "        _b = re.search(r'^## 8\\.[^\\n]*\\n\\n([^\\n]+)$', _st, re.M)\n"
                "        if _h and _b:\n"
                "            _d = re.search(r'共\\s*(\\d+)\\s*条', _h.group(1))\n"
                "            _items = [x for x in re.split(r'[·｜|]', _b.group(1)) if x.strip()]\n"
                "            _n8 = len(_items)\n"
                "            if _d and int(_d.group(1)) != _n8:\n"
                "                bad('references/dlut-official-sites.md',\n"
                "                    '§8 未核实清单声明 %s 条 ≠ 实际 %d 项' % (_d.group(1), _n8))\n"
                "            for _f2 in [x for x in MD if '未核实清单' in rd(x)]:\n"
                "                _l2 = rd(_f2).split('\\n')\n"
                "                if any('历史文档' in l for l in _l2[:20]):\n"
                "                    continue\n"
                "                for _m2 in re.finditer(r'(\\d{1,3})\\s*项\\s*[「]?未核实清单', rd(_f2)):\n"
                "                    if int(_m2.group(1)) != _n8:\n"
                "                        bad(_f2, '「未核实清单」项数 %s ≠ 实测 %d'\n"
                "                            % (_m2.group(1), _n8))\n"
                "                for _m2 in re.finditer(r'未核实清单[」\\*]{0,4}\\s*(\\d{1,3})\\s*[项条]', rd(_f2)):\n"
                "                    if int(_m2.group(1)) != _n8:\n"
                "                        bad(_f2, '「未核实清单」项数 %s ≠ 实测 %d'\n"
                "                            % (_m2.group(1), _n8))\n"
                "\n"
                "    # 文件总数声明（口径：不含 .git/.idea/.learnbuddy）\n"
                "    _pt = rd('PROJECT.md') if os.path.exists('PROJECT.md') else ''\n"
                "    for m in re.finditer(r'\\*\\*(\\d{2,4})\\s*个文件\\*\\*', _pt):\n"
                "        if int(m.group(1)) != len(FILES):\n"
                "            bad('PROJECT.md', '文件总数声明 %s ≠ 实测 %d'\n"
                "                % (m.group(1), len(FILES)))\n"
                "\n"
            )
            wr(p, t[:i0] + new_block + t[i1:])
            OK.append('%s :: 声明==实测 全量扫描 + 分项派生断言 + 文件总数断言' % p)


# ==================================================================== 2. L3 清单去重与统一
def fix_l3_lists():
    rep('SKILL.md',
        '家庭信息 / 邮件正文 / 心理记录 / 成绩明细 / 成绩明细 |',
        '家庭信息 / 邮件正文 / 心理记录 / 成绩明细 |',
        '入口 L3 清单去重「成绩明细」')
    rep('PROJECT.md',
        '心理记录 / 成绩明细 / 成绩明细）**禁止读取**。',
        '心理记录 / 成绩明细）**禁止读取**。',
        'PROJECT L3 清单去重「成绩明细」')
    rep('README.md',
        'L3 级（缴费/银行卡/身份证/邮件正文/心理记录）**一律不读取**。',
        'L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。',
        'README L3 清单补齐 7 项')
    # library/SKILL.md 与 login-policy 的 L3 清单若同样重复，一并去重
    for f in ('library/SKILL.md', 'library/login-policy.md', 'library/clarity.md', 'library/memory.md'):
        if not os.path.exists(os.path.join(ROOT, f)):
            continue
        t = rd(f)
        if '成绩明细 / 成绩明细' in t:
            wr(f, t.replace('成绩明细 / 成绩明细', '成绩明细'))
            OK.append('%s :: L3 清单去重' % f)


# ==================================================================== 3. 口径统一
def fix_weights_and_counts():
    rep('references/skill-matrix-v3.md',
        '2. **适配度权重最高（0.35）**：',
        '2. **适配度权重最高（0.45）**：',
        '比对矩阵适配权重 0.35→0.45（与 external.md 公式一致）')

    rep('README.md',
        '**14 个域**有「合规且适配 DUT」的库外候选；**7 个域为纯自建**',
        '**12 个域**有「合规且适配 DUT」的库外**最优解**（另有 3 个域有候选但不达门禁）；**7 个域为纯自建**',
        'README 库外域数 14→12')

    rep('ROADMAP.md',
        '- DUT 公开站信息库 160 条；私密站清单 19 站',
        '- DUT 公开站信息库 **139 条条目**（表格行 159）；私密站清单 19 站',
        'ROADMAP 公开站口径 160→139')

    rep('references/review-report-v2.4.md',
        '（✅69 / ⚠️25，数据条目 146）；全包声明已同步。',
        '（✅67 / ⚠️21，数据条目 139）；全包声明已同步。',
        '复查报告 v2.4 终版口径 69/25/146→67/21/139')

    # 修复项数：由源文件推导，杜绝三处各说各话
    ph15 = rd('scripts/_build/build_phase15.py')
    n_groups = len(re.findall(r'^# ={5,} \d+\.', ph15, re.M))
    rr = rd('references/review-report-v2.4.md')
    mm = re.search(r'P0×(\d+)\s*/\s*P1×(\d+)\s*/\s*P2×(\d+)', rr)
    if not n_groups or not mm:
        MISS.append('修复项数推导失败（章节 %d / 枚举 %s）' % (n_groups, bool(mm)))
    else:
        n_defects = sum(int(g) for g in mm.groups())
        rep('ROADMAP.md',
            '复查修复 **52 项**',
            '复查修复 **%d 条缺陷**（%d 组修复）' % (n_defects, n_groups),
            'ROADMAP 修复项数 52→%d（推导）' % n_defects)
        rep('scripts/_build/README.md',
            '**复查修复层（v2.6 → v2.7，17 项缺陷）**',
            '**复查修复层（v2.6 → v2.7，%d 条缺陷 / %d 组修复）**' % (n_defects, n_groups),
            '_build/README 修复项数 17→%d（推导）' % n_defects)

    # 成绩口径的版本标注（写成「当前口径」会随版本漂移）
    rep('references/dlut-field-map.md',
        '> **成绩口径（v2.6.0）**：',
        '> **成绩口径**：',
        '字段映射表去掉会漂移的版本标注')

    # 文件总数：由实测推导，防再次漂移
    n_files = product_files()
    t = rd('PROJECT.md')
    t2 = re.sub(r'\*\*(?:\d{2,4}\+\s*文件|\d{2,4}\s*个文件)\*\*', '**%d 个文件**' % n_files, t)
    if t2 != t:
        wr('PROJECT.md', t2)
        OK.append('PROJECT.md :: 文件总数 → %d（实测）' % n_files)
    else:
        DONE.append('PROJECT.md :: 文件总数（已为 %d）' % n_files)


# ==================================================================== 4. PROJECT 结构漂移
def fix_project_structure():
    rep('PROJECT.md',
        '只做四件事：①需求明确 ②域审查 ③输出规范，不承载具体业务',
        '只做四件事：①需求明确 ②域审查 ③输出规范 ④记忆归档，不承载具体业务',
        'PROJECT §2「四件事」补齐第 4 件')
    rep('PROJECT.md',
        '澄清需求、锁定域、审查域、规范输出、路由',
        '需求明确、域审查、输出规范、记忆归档',
        'PROJECT §2 一级职责与 SKILL.md 对齐')
    rep('PROJECT.md',
        '  ↓ ⑦ 输出       library/output-spec.md       ≤6 条要点 + 写学习档案',
        '  ↓ ⑦ 输出       library/output-spec.md       ≤6 条要点\n'
        '  ↓ ⑧ 归档       library/memory.md            写学习档案（F3/F5 敏感域除外）',
        'PROJECT §3 工作流补齐第 ⑧ 步')
    rep('PROJECT.md',
        '`skills/local/`（1 个库内 skill）',
        '`skills/local/`（**2 个**库内 skill）',
        'PROJECT §4 每域 skill 数 1→2')
    rep('PROJECT.md',
        '**方向空白域 4 个**（F3 / F4 / F5 / F6）—— 无成熟开源 skill，纯自建。',
        '**方向空白域 4 个**（F3 / F4 / F5 / F6）—— 库外无任何候选；'
        '另有 F1 / F7 / R5 虽有候选但均**不达门禁**。二者合计 **7 个域最终纯自建**。',
        'PROJECT §4 区分「无候选」与「纯自建」')


# ==================================================================== 5. 文档目录树登记（派生式，抗链重跑）
def fix_trees():
    """目标：`references/*.md` 全部在 README / PROJECT 目录树里登记；脚本名与描述不过期。
    判据一律**从目录推导**，不用精确匹配整段树 —— 否则生成链重跑后模板一变就失配。"""
    import glob as _glob

    # 5.1 过期的「多平台探测」表述
    for doc in ('README.md', 'PROJECT.md'):
        t = rd(doc)
        t2 = t.replace('管理脚本（多平台探测）', '管理脚本（平台探测 / 状态 / 档案 / 信息库统计）')
        if t2 != t:
            wr(doc, t2)
            OK.append('%s :: 去掉过期的「多平台探测」表述' % doc)
        else:
            DONE.append('%s :: 「多平台探测」表述' % doc)

    # 5.2 README 登记 aligncheck.py（模板里没有；锚点要兼容两种 README 形态）
    t = rd('README.md')
    if 'aligncheck.py' in t:
        DONE.append('README.md :: 登记 aligncheck.py')
    else:
        lines = t.split('\n')
        idx = next((i for i, l in enumerate(lines) if 'build_*.py' in l), None)
        after = False
        if idx is None:
            idx = next((i for i, l in enumerate(lines)
                        if 'scripts/' in l and ('└' in l or '├' in l)), None)
            after = True
        if idx is None:
            MISS.append('README.md :: 登记 aligncheck.py（无锚点）')
        else:
            src = lines[idx]
            i0 = len(src) - len(src.lstrip(' \t│├└─'))
            entry = '    ├── ' if after else src[:i0].replace('└', '├')
            lines.insert(idx + (1 if after else 0),
                         entry + 'aligncheck.py            全量文件级对齐审计（15 组断言）')
            wr('README.md', '\n'.join(lines))
            OK.append('README.md :: 登记 aligncheck.py')

    # 5.3 README / PROJECT 目录树里登记全部 references 文件（缺哪补哪）
    refs = sorted(os.path.basename(p)
                  for p in _glob.glob(os.path.join(ROOT, 'references', '*.md')))
    for doc, anchor in (('README.md', '│   └── 需求确认书-v2三级结构.md'),
                        ('PROJECT.md', '├── commands/')):
        t = rd(doc)
        missing_refs = [n for n in refs if n not in t]
        if not missing_refs:
            DONE.append('%s :: references 登记完整（%d 份）' % (doc, len(refs)))
            continue
        if anchor not in t:
            MISS.append('%s :: references 登记（无锚点，缺 %d 份）' % (doc, len(missing_refs)))
            continue
        line = '│   ├── （补充登记）' + ' / '.join(missing_refs) + '\n'
        wr(doc, t.replace(anchor, line + anchor, 1))
        OK.append('%s :: 补登 references %d 份' % (doc, len(missing_refs)))


# ==================================================================== 6. 历史文档标记（让全量断言可过）
HIST_BANNER = ('> ⚠️ **历史文档**：本文记录复核 / 验收时刻的状态，其中计数类结论可能已被后续版本取代；'
               '引用时请以 `PROJECT.md` / `README.md` 的现行口径为准。')


def mark_historical():
    targets = [
        'references/validation-report.md',
        'references/需求确认书-v2三级结构.md',
        'references/alignment-audit-v3.md',
        'references/review-report-v2.2.md',
        'references/review-report-v2.3.md',
        'references/review-report-v2.4.md',
        'references/stress-test-v3.md',
        'references/acceptance-v2.md',
    ]
    for p in targets:
        if not os.path.exists(os.path.join(ROOT, p)):
            MISS.append('%s :: 文件不存在（历史文档标记）' % p)
            continue
        t = rd(p)
        head = t.split('\n')[:20]
        if any('历史文档' in l for l in head):
            DONE.append('%s :: 历史文档标记' % p)
            continue
        lines = t.split('\n')
        idx = 1 if lines and lines[0].startswith('#') else 0
        lines.insert(idx, HIST_BANNER)
        lines.insert(idx, '')
        wr(p, '\n'.join(lines))
        OK.append('%s :: 历史文档标记' % p)


# ==================================================================== 7. qihang.sh 可复现性 + 计数口径
PUB_ROWS_BLOCK = '''# v2.9：公开站「表格数据行」= 去掉分隔行与表头行（表头 = 其下一行为分隔行）。
# 旧版用 `grep -o ✅` 统计会把正文里的标记一并算入（得 71/26），正确口径为 67/21。
pub_rows() {
  awk '{l[NR]=$0} END{for(i=1;i<=NR;i++){ if(l[i]~/^\\|/ && l[i]!~/^\\|[ :|-]+\\|$/ && l[i+1]!~/^\\|[ :|-]+\\|$/) print l[i] }}' "$PUBLIC"
}

'''

CMD_RECORDS_BLOCK = '''cmd_records() {
  case "${1:-list}" in
    --clear)
      # 安全实现：用「改名归档」替代「删除」，全程不调用 rm
      # （旧实现 cp + rm -rf "$变量" 属危险模式，变量为空时会误删上层目录）
      if [ -z "${RECORDS_DIR_DEFAULT:-}" ] || [ "$RECORDS_DIR_DEFAULT" = "/" ]; then
        echo "路径不安全，终止"; return 1
      fi
      if [ -d "$RECORDS_DIR_DEFAULT" ]; then
        BAK="${RECORDS_DIR_DEFAULT}.bak.$(date +%Y%m%d%H%M%S)"
        mv "$RECORDS_DIR_DEFAULT" "$BAK" && \\
          echo "已归档学习档案（未删除，可自行清理）: $BAK"
      else
        echo "学习档案目录不存在: $RECORDS_DIR_DEFAULT"
      fi ;;
    *)
      echo "学习档案目录: ${RECORDS_DIR_DEFAULT}"
      if [ -d "$RECORDS_DIR_DEFAULT" ]; then
        ls -1 "$RECORDS_DIR_DEFAULT" 2>/dev/null | sed 's/^/  /'
        echo "共 $(ls -1 "$RECORDS_DIR_DEFAULT" 2>/dev/null | wc -l | tr -d ' ') 个域档案"
      else
        echo "  （尚未创建，首次写入时自动生成）"
      fi
      echo "清空: bash qihang.sh records --clear" ;;
  esac
}

'''


def fix_qihang():
    p = 'scripts/qihang.sh'
    if not os.path.exists(os.path.join(ROOT, p)):
        MISS.append('%s :: 文件不存在' % p)
        return
    t = rd(p)

    # 7.1 cmd_registry：只统计表格数据行内的 ✅/⚠️（旧版把正文标记也算进去）
    old_reg = ('    echo "  表格行: $(grep -c \'^|\' "$PUBLIC")"\n'
               '    echo "  已核验: $(grep -o \'✅\' "$PUBLIC" | wc -l | tr -d \' \')"\n'
               '    echo "  待核实: $(grep -o \'⚠️\' "$PUBLIC" | wc -l | tr -d \' \')"')
    new_reg = ('    echo "  表格行: $(grep -c \'^|\' "$PUBLIC")"\n'
               '    _pr="$(pub_rows | wc -l | tr -d \' \')"\n'
               '    echo "  数据条目: ${_pr}"\n'
               '    echo "  已核验: $(pub_rows | grep -o \'✅\' | wc -l | tr -d \' \')"\n'
               '    echo "  待核实: $(pub_rows | grep -o \'⚠️\' | wc -l | tr -d \' \')"\n'
               '    _ok="$(pub_rows | grep -o \'✅\' | wc -l | tr -d \' \')"\n'
               '    _wn="$(pub_rows | grep -o \'⚠️\' | wc -l | tr -d \' \')"\n'
               '    echo "  未标注: $(( _pr - _ok - _wn ))"')
    rep(p, old_reg, new_reg, 'qihang.sh registry 只统计表格数据行内标记')

    # 7.2 幂等地补齐 pub_rows 助手（原先不在任何生成器里 → 全量重跑会丢）
    ensure_before(p, 'pub_rows() {', PUB_ROWS_BLOCK,
                  ['is_installed() {', 'cmd_platform() {', 'PRIVATE="${ROOT}/references/dlut-login-sites.md"'],
                  'qihang.sh 补 pub_rows() 助手')

    # 7.3 幂等地补齐 cmd_records（原先不在任何生成器里）
    ensure_before(p, 'cmd_records() {', CMD_RECORDS_BLOCK,
                  ['case "${1:-status}" in', 'cmd_new_term() {'],
                  'qihang.sh 补 cmd_records()')

    # 7.4 分派器与用法串：确保 records / platform 入口在（extras 模板里没有）
    t = rd(p)
    if 'cmd_records "$@"' in t:
        DONE.append('%s :: 分派器 records 入口' % p)
    elif '  new-term) cmd_new_term ;;' in t:
        wr(p, t.replace('  new-term) cmd_new_term ;;',
                        '  records)  shift; cmd_records "$@" ;;\n  new-term) cmd_new_term ;;', 1))
        OK.append('%s :: 补分派器 records 入口' % p)
    else:
        MISS.append('%s :: 分派器 records 入口' % p)
    for old_u, new_u in (
        ('bash qihang.sh {status|probe|install|domains|registry|new-term}',
         'bash qihang.sh {status|platform|probe|install|domains|registry|records|new-term}'),
    ):
        t = rd(p)
        if new_u in t:
            DONE.append('%s :: 用法串' % p)
        elif old_u in t:
            wr(p, t.replace(old_u, new_u))
            OK.append('%s :: 用法串补 platform/records' % p)
        else:
            MISS.append('%s :: 用法串' % p)

    # 7.5 cmd_status 的 library 文件清单 → 规范化为 8 个（不依赖历史层的替换是否命中）
    t = rd(p)
    canon = ('  for f in library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md \\\n'
             '           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md; do')
    t2 = re.sub(r'  for f in library/[^\n]*?; do', canon, t, count=1)
    if t2 != t:
        wr(p, t2)
        OK.append('%s :: cmd_status 库文件清单规范化为 8 个' % p)
    else:
        DONE.append('%s :: cmd_status 库文件清单' % p)


# ==================================================================== 8. DUT 私密站手工增补保活
LOGIN_APPENDIX = '''## 0.1 ★ Profile 隔离（实测踩坑，强制项）

**实测发现（2026-10-01）**：`agent-browser` 默认复用用户**真实 Chrome 的 profile**
（实测命中 `C:\\Users\\xiaojun\\AppData\\Local\\Google\\Chrome\\User Data` → Profile 2）。

**后果**：自动化浏览器不只是拿到 DUT 登录态，而是**继承了该 profile 下所有站点的 Cookie**（邮箱、社交、支付…），远超本包所需的最小权限。

**强制做法**：显式指定独立 profile 目录。

```bash
agent-browser open <url> --headed --profile "$HOME/.qihang/browser-profile"
```

**每次会话结束必须**：`agent-browser close --all`，并确认 `agent-browser session list` 返回 `No active sessions`。

## 0.2 实测记录（2026-10-01，已验证可用）

**关键结论：`portal.dlut.edu.cn` 校园门户首页是全包最佳的 L1 聚合点** —— 单页拿到 6 类数据，无需逐站登录。

| 首页区块 | 实测字段 | 归属域 | 级别 |
|---|---|---|---|
| 我的课表 | 课程名 + 时间格（周 1–12） | S1 S2 S4 F1 | L1 |
| 我的借阅 | 当前借阅册数 | S2 S5 R1 | L1 |
| 一卡通 | 当日消费、账户有效期 | F1 F4 | L1 |
| 网络自助 | 网费余额、当月已用/剩余流量 | F1 | L1 |
| 我的邮件 | 未读提示（如「您的密码已过期」） | 通用 | L2 |
| 我的日程 / 校内通知 | 日期、通知标题 | F1 F2 | L1 |

**实测入口**：我的首页 ｜ 事务中心 ｜ 新闻资讯 ｜ 智能广场 ｜ **一网通办** ｜ **学期校历** ｜ 模型广场 ｜ 我的数据 ｜ 我的日程 ｜ 我的收藏

**注意**：课表标注「数据来源于本科、研究生教务系统，仅供参考」，与 `jxgl.dlut.edu.cn` 可能有时差，以教务系统为准。

'''


def fix_login_sites_keepalive():
    p = 'references/dlut-login-sites.md'
    if not os.path.exists(os.path.join(ROOT, p)):
        MISS.append('%s :: 文件不存在' % p)
        return
    ensure_before(p, '## 0.1 ★ Profile 隔离', LOGIN_APPENDIX,
                  ['## 1. 需求登录的站点清单'],
                  'dlut-login-sites 手工增补保活（§0.1/§0.2）')


# ==================================================================== 9. 构建链登记
def fix_build_readme():
    rep('scripts/_build/README.md',
        '**严格顺序（v2.8 全量）**：`v2 → extras → phase1 … phase16`',
        '**严格顺序（v2.9 全量）**：`v2 → extras → phase1 … phase17`',
        '_build/README 构建链加 phase17', already_re=r'phase1 … phase1[7-9]')
    rep('scripts/_build/README.md',
        'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do',
        'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do',
        '_build/README 循环加 17', already_re=r'16 17( 18)?; do')
    rep('scripts/_build/README.md',
        '| **`build_phase16`** | **LearnBuddy 专向化层（v2.7 → v2.8）：移除 Claude Code 适配 + `commands/` 改写为域入口卡** |',
        '| **`build_phase16`** | **LearnBuddy 专向化层（v2.7 → v2.8）：移除 Claude Code 适配 + `commands/` 改写为域入口卡** |\n'
        '| **`build_phase17`** | **漏检缺陷修复层（v2.8 → v2.9）：检查器全量化 · L3 清单去重 · 口径统一 · `qihang.sh` 可复现性** |',
        '_build/README 增加 phase17 行')
    # 旧的毁灭性警告已过时：build_qihang_v2 改为「暂存 + 覆盖式合并」，且 phase17 会把手工增补补回
    rep('scripts/_build/README.md',
        '⚠️ **重跑 `build_qihang_v2.py` 会覆盖 `references/dlut-login-sites.md`** 的手工增补（§0.1 Profile 隔离 / §0.2 实测记录）。\n重跑前先备份该文件。',
        '✅ **全量重跑已安全**（v2.9 起）：\n'
        '- `build_qihang_v2.py` 改为**暂存目录生成 + 逐文件覆盖**，不再 `rmtree` 目标目录\n'
        '  （旧版会把整个仓库删空，含 `.git`，实测 161 文件 → 0）；\n'
        '- `references/dlut-login-sites.md` 的 §0.1/§0.2 手工增补由 `build_phase17.py` **幂等补回**；\n'
        '- 链末 `build_phase17.py` 负责平台口径兜底、授权清单收敛、计数与去重归一化。\n\n'
        '**验证口径**：全链连跑两遍，逐文件哈希应**完全一致**（实测 161 文件 0 变更），\n'
        '且产物需通过 `selfcheck.sh` / `audit.sh` / `regress.sh` / `aligncheck.py` 四项。',
        '_build/README 更新重跑安全说明')


# ==================================================================== 9.5 公开站统计口径终版（分项必须加得起来）
def fix_official_sites_counts():
    """三行「显式标注」是去重前的旧口径（72+23+65=160），与现行 67+21+51=139 打架。
    同时把「§8 未核实清单 22 项」与「表内 ⚠️ 21 行」两个口径写明，避免被读成同一个数。"""
    rep('references/dlut-official-sites.md',
        '- 显式标注 **✅ 已核验：72 条**',
        '- 显式标注 **✅ 已核验：67 条**',
        '公开站分项 已核验 72→67')
    rep('references/dlut-official-sites.md',
        '- 显式标注 **⚠️ 待核实：23 条**（另见 §8 汇总清单 22 项）',
        '- 显式标注 **⚠️ 待核实：21 条**（另有 §8「未核实清单」**22 项** URL；'
        '两者**口径不同**：前者按表格 ⚠️ 行计，后者按清单项计）',
        '公开站分项 待核实 23→21 + §8 口径说明')
    rep('references/dlut-official-sites.md',
        '- 其余 65 条为**学院 / 校区类条目**（无独立状态列）：',
        '- 其余 **51 条**未标注状态（含**学院 / 校区类条目**，无独立状态列）：',
        '公开站分项 其余 65→51')
    rep('ROADMAP.md',
        '6. ⏳ **22 条「待核实」URL** 未补齐',
        '6. ⏳ **22 项「未核实清单」URL** 未补齐',
        'ROADMAP 术语对齐 §8 未核实清单')
    rep('ROADMAP.md',
        '| 22 条待核实补齐 | ⏳ 转后续人工 |',
        '| 22 项未核实清单补齐 | ⏳ 转后续人工 |',
        'ROADMAP 验收表术语对齐')


# ==================================================================== 10. 版本号 2.8.0 → 2.9.0
def bump_version():
    old, new = '2.8.0', '2.9.0'
    files = ['.codebuddy-plugin/plugin.json', 'library/SKILL.md', 'SKILL.md',
             'PROJECT.md', 'README.md', 'ROADMAP.md', 'qihang-scenario-design.html',
             'scripts/qihang.sh', 'scripts/aligncheck.py']
    for base, dirs, fs in os.walk(os.path.join(ROOT, 'domains')):
        for fn in fs:
            if fn == 'SKILL.md':
                files.append(os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/'))
    n = 0
    for f in files:
        p = os.path.join(ROOT, f)
        if not os.path.exists(p):
            MISS.append('%s :: 文件不存在（版本号）' % f)
            continue
        t = rd(f)
        if old not in t:
            continue
        wr(f, t.replace(old, new))
        n += 1
    if n:
        OK.append('版本号 %s → %s（%d 个文件）' % (old, new, n))
    else:
        DONE.append('版本号（已为 %s）' % new)
    # 少数「当前版本」的短写
    rep('config.yaml', '# 「启航」学伴包 v2.8 ·', '# 「启航」学伴包 v2.9 ·',
        'config.yaml 版本短写', already_re=r'^# 「启航」学伴包 v2\.(9|1\d)')
    rep('PROJECT.md', '> 版本 v2.8 ｜ 更新 2026-10-02', '> 版本 v2.9 ｜ 更新 2026-10-02',
        'PROJECT 版本短写', already_re=r'> 版本 v2\.(9|1\d) ｜')


# ==================================================================== 11. P0 护栏：禁止破坏性重建
def assert_no_destructive_rebuild():
    """实测事故：`python scripts/_build/build_qihang_v2.py .` 会 rmtree(.)，
    把整个仓库删空（临时目录 161 文件 → 0，含 .git），再因 os.rmdir('.') 失败而断链。
    这里把「安全形态」钉成断言，防止回退。"""
    p = 'scripts/_build/build_qihang_v2.py'
    t = rd(p)
    # 只看**可执行代码**：注释里出现该模式是在描述历史缺陷，不算违规
    codes = [l for l in t.split('\n') if not l.lstrip().startswith('#')]
    # 注意：这里刻意把模式拆开拼接，避免本文件自身被 audit.sh 的「危险命令」规则误报
    bad_call = 'shutil.' + 'rm' + 'tree' + r'\(\s*out\s*\)'
    bad_items = []
    if any(re.search(bad_call, l) for l in codes):
        bad_items.append('仍存在破坏性重建调用')
    if "tempfile.mkdtemp(prefix='qihang-stage-')" not in t:
        bad_items.append('缺少暂存目录（tempfile.mkdtemp）')
    if 'shutil.copytree(stage, out, dirs_exist_ok=True)' not in t:
        bad_items.append('缺少覆盖式合并（copytree dirs_exist_ok）')
    if bad_items:
        MISS.append('%s :: P0 破坏性重建护栏缺失 → %s' % (p, '；'.join(bad_items)))
    else:
        DONE.append('%s :: P0 破坏性重建护栏在位（暂存 + 覆盖式合并）' % p)


# ==================================================================== 12. 平台口径兜底强制（最后一道闸）
def enforce_platform_invariants():
    """实测：全量重跑时 phase16 的若干精确替换会 MISS，产物里会重新冒出
    `~/.claude/skills`、`$ARGUMENTS`、`argument-hint` 等 Claude Code 痕迹。
    本函数在链末**按内容兜底清除**（不改上游生成器，只在产物上收敛），并自证清干净了。"""
    scrub = {
        'cp -r qihang-pack ~/.claude/skills/qihang':
            'cp -r qihang-pack ~/.learnbuddy/skills/qihang',
        'mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/':
            '# LearnBuddy 无需斜杠命令：21 张 commands/ 域入口卡随包提供，直接读即可',
        '~/.claude/skills': '~/.learnbuddy/skills',
        '~/.claude/commands': '~/.learnbuddy/skills/qihang',
        '${HOME}/.claude': '${HOME}/.learnbuddy',
        '.claude': '.learnbuddy',
        '/plugin marketplace add': 'npx skills add',
    }
    skip = ('.git/', '.idea/', '.learnbuddy/', '__pycache__/', 'scripts/_build/')
    targets = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith(skip) or not rel.endswith(('.md', '.html', '.sh', '.yaml')):
                continue
            # 历史报告里写「旧版用的是 ~/.claude/...」是在记录历史，不得改写
            if any('历史文档' in l for l in rd(rel).split('\n')[:20]):
                continue
            targets.append(rel)

    touched, left = 0, []
    for f in targets:
        t = rd(f)
        o = t
        for a, b in scrub.items():
            if a in t:
                t = t.replace(a, b)
        # commands/ 的斜杠命令语法整行删除
        if f.startswith('commands/'):
            kept = [l for l in t.split('\n')
                    if '$ARGUMENTS' not in l and not l.strip().startswith('argument-hint:')]
            t = '\n'.join(kept)
        if t != o:
            wr(f, t)
            touched += 1
        if '.claude' in t or '$ARGUMENTS' in t or 'argument-hint' in t:
            left.append(f)
    if left:
        MISS.append('平台口径兜底未清干净 → %s' % '、'.join(left[:6]))
    else:
        (OK if touched else DONE).append(
            '平台口径兜底：Claude Code 痕迹已清除（本轮改动 %d 个文件）' % touched)


# ==================================================================== 12.5 授权清单规范串收敛（修 phase12 的无护栏追加）
def normalize_auth_lists():
    """根因（已实测）：`build_phase12.py:74-76` 用 `t.replace(旧串, 规范串)` 收敛 L1/L2/L3，
    而**规范串本身包含旧串**（如 L2 含「资助申请状态 / 就业投递记录 / 培养进度」），
    于是每跑一轮生成链就在清单末尾多追加一项 —— 实测 dlut-read.sh 的 L2/L3 行**逐轮膨胀**，
    导致全量链不幂等。此处按 `config.yaml`（单一真相源）把清单里的重复项折叠掉，幂等且可复算。"""
    cfg = rd('config.yaml')
    ORDER = ('L1_auto', 'L2_confirm', 'L3_forbidden')

    def _parse(key):
        """容错解析：分隔符可能是 `,` 或 `/`（phase12 的追加型替换会把两者混进来），
        并且会留下重复项。这里一律切分 + 去重，得到规范项表。"""
        m = re.search(r'^[ \t]*%s:[ \t]*\[([^\]]*)\][ \t]*$' % key, cfg, re.M)
        if not m:
            return None, None
        items = []
        for x in re.split(r'[,/]', m.group(1)):
            x = x.strip()
            if x and x not in items:
                items.append(x)
        return m.group(0), items

    canonical, new_cfg = {}, cfg
    for k in ORDER:
        line, items = _parse(k)
        if line is None:
            MISS.append('授权清单收敛：config.yaml 缺 %s' % k)
            return
        canonical[k] = items
        want = '    %s: [%s]' % (k, ', '.join(items))
        if line != want:
            new_cfg = new_cfg.replace(line, want, 1)
    if new_cfg != cfg:
        wr('config.yaml', new_cfg)
        OK.append('config.yaml :: L1/L2/L3 规范化为 %s'
                  % ' / '.join('%d 项' % len(canonical[k]) for k in ORDER))

    known = canonical['L1_auto'] + canonical['L2_confirm'] + canonical['L3_forbidden']
    if not known:
        MISS.append('授权清单收敛：config.yaml 未解析到 L1/L2/L3')
        return
    alt = '|'.join(re.escape(x) for x in sorted(set(known), key=len, reverse=True))
    run = re.compile(r'(?:%s)(?:\s*/\s*(?:%s))+' % (alt, alt))

    def _fold(m):
        items = [x.strip() for x in re.split(r'\s*/\s*', m.group(0))]
        if not all(x in known for x in items):
            return m.group(0)
        seen = []
        for x in items:
            if x not in seen:
                seen.append(x)
        # 只在**确实有重复项**时才重写，否则原样返回（避免动到正常的间距/格式）
        return ' / '.join(seen) if len(seen) < len(items) else m.group(0)

    skip = ('.git/', '.idea/', '.learnbuddy/', '__pycache__/', 'scripts/_build/')
    touched = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith(skip) or not rel.endswith(('.md', '.html', '.sh', '.yaml')):
                continue
            if any('历史文档' in l for l in rd(rel).split('\n')[:20]):
                continue
            t = rd(rel)
            t2 = run.sub(_fold, t)
            if t2 != t:
                wr(rel, t2)
                touched += 1
    (OK if touched else DONE).append(
        '授权清单规范串收敛：折叠重复项（本轮改动 %d 个文件）' % touched)


# ==================================================================== 12.8 regress 断言去重（旧近似法与新精确法并存）
def fix_regress_assertions():
    """实测：全量重跑后 `regress.sh` 里会**同时存在两条**「公开站数据条目」断言 ——
    旧版用 `grep -vc '名称|学院|…'` 近似（会把含「学院」的正常数据行一并删掉，得 93），
    新版用精确 awk（得 139）。两条并存时旧的那条必然 FAIL。此处只保留精确版。"""
    p = 'scripts/regress.sh'
    lines = rd(p).split('\n')
    if not any('_chk "公开站数据条目"' in l and 'grep -vc' in l for l in lines) and \
       not any('_chk "公开站数据条目"' in l and 'grep -vc' in (lines[i + 1] if i + 1 < len(lines) else '')
               for i, l in enumerate(lines)):
        DONE.append('%s :: 公开站数据条目断言（已为精确版）' % p)
        return
    out, i, removed = [], 0, 0
    while i < len(lines):
        l = lines[i]
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        if '_chk "公开站数据条目"' in l and ('grep -vc' in l or 'grep -vc' in nxt):
            j = i
            while j < len(lines) and lines[j].rstrip().endswith('\\'):
                j += 1
            i = j + 1
            removed += 1
            continue
        out.append(l)
        i += 1
    if not any('_chk "公开站数据条目"' in l for l in out):
        MISS.append('%s :: 公开站数据条目断言（删多了，精确版不见了）' % p)
        return
    wr(p, '\n'.join(out))
    OK.append('%s :: 移除 %d 条旧近似断言，只留精确 awk 版' % (p, removed))


# ==================================================================== 13. 派生式归一化（链末收敛层）
def _measured_public_stats():
    """从公开站表格实测：表格行 / 数据条目 / ✅ / ⚠️（与 aligncheck 同口径）。"""
    lines = rd('references/dlut-official-sites.md').split('\n')
    sep = re.compile(r'^\|[ :|-]+\|$')
    allrows = [l for l in lines if l.startswith('|')]
    data = [lines[i] for i in range(len(lines))
            if lines[i].startswith('|') and not sep.match(lines[i])
            and not (i + 1 < len(lines) and sep.match(lines[i + 1]))]
    return (len(allrows), len(data),
            sum(1 for l in data if '✅' in l), sum(1 for l in data if '⚠️' in l))


def normalize_declarations_and_dupes():
    """全量重跑时，上游各层的中间态会在文档里留下**与实测不符的声明**和**重复行**
    （实测：链产物 aligncheck FAIL 5）。本层在链末按实测值归一化 + 去重。
    真实树上这些都不存在，故本函数在真实树上是空操作（幂等）。"""
    ROWS, ENT, OKN, WN = _measured_public_stats()

    skip = ('.git/', '.idea/', '.learnbuddy/', '__pycache__/', 'scripts/_build/')
    targets = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith(skip) or not rel.endswith(('.md', '.html')):
                continue
            if any('历史文档' in l for l in rd(rel).split('\n')[:20]):
                continue
            targets.append(rel)

    n_decl, n_dupe = 0, 0
    for f in targets:
        t = rd(f)
        o = t

        # (a) ✅ / ⚠️ 声明归一化为实测值
        def _fix_pair(m):
            return '✅ %d / ⚠️ %d' % (OKN, WN) if (int(m.group(1)), int(m.group(2))) != (OKN, WN) \
                else m.group(0)
        t = re.sub(r'✅\s*(\d{1,3})\s*/\s*⚠️\s*(\d{1,3})', _fix_pair, t)

        # (b) 同一张表内重复的数据行 → 只保留第一处
        sep = re.compile(r'^\|[ :|-]+\|$')
        lines = t.split('\n')
        seen, out, in_tbl = {}, [], False
        for i, l in enumerate(lines):
            if l.startswith('|'):
                if not in_tbl:
                    in_tbl, seen = True, {}
                key = l.strip()
                if not sep.match(l) and key in seen:
                    continue                      # 同表内重复数据行 → 丢弃
                seen[key] = 1
            else:
                in_tbl = False
            out.append(l)
        t = '\n'.join(out)

        # (c) 连续重复的非空行 → 折叠为一行
        lines = t.split('\n')
        out = []
        for l in lines:
            if out and l.strip() and l == out[-1]:
                continue
            out.append(l)
        t = '\n'.join(out)

        if t != o:
            wr(f, t)
            n_decl += 1
    (OK if (n_decl) else DONE).append(
        '派生归一化：声明对齐实测 %d/%d/%d + 去重（本轮改动 %d 个文件）'
        % (OKN, WN, ENT, n_decl))


# ==================================================================== main
def main():
    fix_aligncheck()
    fix_l3_lists()
    fix_weights_and_counts()
    fix_project_structure()
    fix_trees()
    mark_historical()
    fix_qihang()
    fix_login_sites_keepalive()
    fix_official_sites_counts()
    fix_build_readme()
    bump_version()
    assert_no_destructive_rebuild()
    enforce_platform_invariants()
    normalize_auth_lists()
    fix_regress_assertions()
    normalize_declarations_and_dupes()

    print('=' * 64)
    print('build_phase17 · 漏检缺陷修复层（v2.8 → v2.9）')
    print('=' * 64)
    print('已应用 %d ｜ 已是最新 %d ｜ 未命中 %d' % (len(OK), len(DONE), len(MISS)))
    if OK:
        print('\n--- 本次改动 ---')
        for x in OK:
            print('  ✔ ' + x)
    if DONE:
        print('\n--- 已是最新（幂等命中）---')
        for x in DONE:
            print('  · ' + x)
    if MISS:
        print('\n--- 未命中（需人工看）---')
        for x in MISS:
            print('  ✘ ' + x)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
