#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」发布副本构建器（开发侧工具，随生成器一起**不交付**）

把开发仓库 `qihang-pack/`（含生成器、过程文档、AI 工作记忆）导出为
**只含交付物**的 `qihang-pack-release/`，并做字段清理与断链检查。

───────────────────────────────────────────────────────────────────────
一、导出集合怎么定 —— **唯一真相源 = git + .gitignore**（v2.11 起）
───────────────────────────────────────────────────────────────────────
    应交付 = git ls-files --cached --others --exclude-standard
             ∩ 磁盘实际存在
             − scripts/_build/            （开发期生成器）
             − .gitignore / .gitattributes（版本控制元数据）

  · `--cached`：已跟踪文件。工作区未提交的改动**照样导出**（copy2 取磁盘现状），
    所以导出的是「当前磁盘状态」，不是某次 commit 的快照。
  · `--others --exclude-standard`：**未跟踪但未被忽略**的新文件。这一步同时解决两件事：
      ① 8 份过程文档只登记在 `.gitignore` 里 → 自动落选，**不需要第二份硬编码清单**；
      ② 刚写好、还没 `git add` 的新文件（如新增的声明文件）**不会漏导出**。
    旧版把「哪些不进交付物」写成了第二份硬编码清单（`EXCLUDED_REFERENCES` /
    `DROP_DIRS`），实测会漂移 —— 新增声明文件时就漏加过。
  · **必须与磁盘取交集**：git 索引里可能仍有「已从磁盘删除但还没 commit」的路径。
    实测 `library/SKILL.md`（v2.11 退役）仍在索引中，直接 `copy2` 会 FileNotFoundError。
  · `-z` 分隔：让 git 用 NUL 分隔并**关闭路径转义**，否则非 ASCII 路径会变成
    `"references/\\351\\234\\200..."` 这种八进制串，解析必然出错。

───────────────────────────────────────────────────────────────────────
二、为什么不删目标目录（环境约束，勿改）
───────────────────────────────────────────────────────────────────────
本机 safe-delete 把「递归删除整棵目录树」当成**批量删除**拦截（实测 132 文件 > 阈值 50 →
SAFE_DELETE_BULK_CONFIRM_REQUIRED）。因此这里**不做删除，只覆盖写入**；导出集是确定性的，
但**覆盖式导出不会清掉「上一版有、这一版没有」的文件** —— 那类陈旧文件由 `prune_stale()`
显式**移出**到 `%TEMP%/qihang-release-retired/<本次运行>/`（移动而非删除，可回滚；
超过 20 个则只报不动，交人工）。
**请勿在此文件中引入任何递归删除调用** —— `scripts/audit.sh` 会扫描，
且该检查**不区分代码与注释**（本文件第一版就是在文档串里写了那个 API 名而被判失败）。

用法：
    python scripts/_build/make_release.py                 # → 默认 ../qihang-pack-release
    python scripts/_build/make_release.py <目标目录>
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
# HERE = <repo>/scripts/_build  →  上溯两级 = 仓库根
SRC = os.path.dirname(os.path.dirname(HERE))
DEFAULT_DST = os.path.join(os.path.dirname(SRC), 'qihang-pack-release')

# 开发期生成器目录（不交付；本工具自身也在其中）
BUILD_DIR = 'scripts/_build'
# 版本控制元数据（不交付：使用者自行 `git init`）
ROOT_META = frozenset(['.gitignore', '.gitattributes'])
# 环境噪声：既不交付，也不参与断链判定（否则 `__pycache__/x.pyc` 会污染清单）
NOISE_DIRS = frozenset(['.git', '.idea', '.learnbuddy', '__pycache__'])
DROP_SUFFIX = ('.pyc',)
# 单次自动清理的陈旧文件上限：超过就只报不删，交人工确认（避免误删大批文件）
MAX_PRUNE = 20

DST = DEFAULT_DST
REPORT = []   # 会写进 MANIFEST「已做的字段清理」
DRIFT = []    # 工具与树状态不一致（未命中等）——打印告警，**不进 MANIFEST**


# ═══════════════════════════════════════════════════════════════════
# 0. 导出集合推导
# ═══════════════════════════════════════════════════════════════════

def git_visible():
    """仓库的「git 可见文件」全集（含未跟踪且未被忽略的新文件）。

    这就是「什么该进交付物」的单一真相源：排除项写在 `.gitignore`，不在这里。
    """
    r = subprocess.run(
        ['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
        cwd=SRC, capture_output=True)
    if r.returncode != 0:
        raise SystemExit('git ls-files 失败（本工具需在 git 工作区中运行）：\n'
                         + r.stderr.decode('utf-8', 'replace'))
    out = r.stdout.decode('utf-8', 'replace')
    return [x.replace('\\', '/') for x in out.split('\0') if x.strip()]


def export_set():
    """应交付文件（仓库相对路径）。返回 (files, missing_in_disk)。

    ⚠️ 光靠 git 不够：`.learnbuddy/`（AI 工作记忆）**是被 git 跟踪的**且不在
    `.gitignore` 里（它只是「不交付」，不是「不进版本控制」）。实测第一版因此把
    2 份记忆日志打进了交付物。→ 这里必须再按 NOISE_DIRS 过滤一层。
    这是「环境/内部目录」维度，与「内容排除清单」不是一回事，故不违反单一真相源。
    """
    files, missing = [], []
    for rel in git_visible():
        if rel.startswith(BUILD_DIR + '/') or rel in ROOT_META:
            continue
        if any(p in NOISE_DIRS for p in rel.split('/')[:-1]) or rel.endswith(DROP_SUFFIX):
            continue
        if not os.path.isfile(os.path.join(SRC, rel)):
            missing.append(rel)       # 索引有、磁盘无（退役后未 commit）
            continue
        files.append(rel)
    return sorted(files), sorted(missing)


def excluded_set(delivered):
    """仓库里**存在但不进交付物**的文件（用于断链改写与清单说明）。

    由「磁盘实测 − 导出集」反推，而不是另写一份清单 —— 这是本文件的核心不变式：
    **任何时刻只有一份排除清单，就是 .gitignore。**
    """
    d = set(delivered)
    out = []
    for base, dirs, fns in os.walk(SRC):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if fn.endswith(DROP_SUFFIX):
                continue
            rel = os.path.relpath(os.path.join(base, fn), SRC).replace('\\', '/')
            if rel not in d:
                out.append(rel)
    return sorted(out)


DELIVERED, MISSING_IN_DISK = export_set()
EXCLUDED = excluded_set(DELIVERED)
# 断链改写用的「过程文档」清单：直接从排除集里取 references/ 下的项 → 等价于
# 「.gitignore 里 references/*.md 那几行」，但拿到的是**实际文件名**，无需解析 glob。
EXCLUDED_REFERENCES = [x for x in EXCLUDED if x.startswith('references/')]
_EXCL_NAMES = sorted(os.path.basename(x) for x in EXCLUDED_REFERENCES)
# 目录树里对生成器目录的登记（整行删除用）
_EXCL_DIR_HINTS = ('_build/', 'build_phase', 'build_qihang_v2', 'make_release')


# ═══════════════════════════════════════════════════════════════════
# 1. 基础 IO
# ═══════════════════════════════════════════════════════════════════

def rel_path(p):
    return os.path.relpath(p, DST).replace('\\', '/')


def rd(p):
    with open(os.path.join(DST, p), 'r', encoding='utf-8') as f:
        return f.read()


def wr(p, s):
    with open(os.path.join(DST, p), 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def report(msg):
    REPORT.append(msg)
    print('  ' + msg)


def drift(msg):
    DRIFT.append(msg)
    print('  ! ' + msg)


# ═══════════════════════════════════════════════════════════════════
# 2. 导出
# ═══════════════════════════════════════════════════════════════════

def copy_tree():
    """原地覆盖式导出（**不删除目标目录**；理由见文件头 §二）。"""
    n = 0
    for rel in DELIVERED:
        dst = os.path.join(DST, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(os.path.join(SRC, rel), dst)
        n += 1
    # ⚠️ 只报**目录名**，不报绝对路径：该字符串会写进 MANIFEST 随包交付，
    #    写成 `C:\Users\<用户名>\...` 等于把本机内部路径泄给收包人。
    report('导出交付物 %d 个文件 → %s/' % (n, os.path.basename(os.path.normpath(DST))))
    return n


def _soft(name):
    """把「陈旧文件路径」写成**不会被解析成交叉引用**的形式。

    ⚠️ 实测事故：移出报告里直接写 `library/SKILL.md`，该串被写进 MANIFEST 后
    立刻被 `aligncheck.py`（G 组交叉引用）与 `selfcheck.sh` [4] 判为失效引用 —— 
    于是「清理干净的副本」自检反而挂了。两份校验器的正则都排除**反引号**，
    故这里拆成 `` `dir/` 下 `base` `` 与 `` `/` 下 `file` ``（路径被空格+反引号打断）。
    """
    d, b = os.path.split(name)
    return ('`%s/` 下 `%s`' % (d, b)) if d else ('`./` 下 `%s`' % b)


def report_stale():
    """列出目标目录里「不属于导出集」的文件（**只报，不动**）。

    `MANIFEST.md` 不算陈旧：它由 `write_manifest()` 每轮**重写**，属导出集的一部分。
    """
    keep = set(DELIVERED) | {'MANIFEST.md'}
    stale = []
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            r = rel_path(os.path.join(base, fn))
            if r not in keep:
                stale.append(r)
    return sorted(stale)


def prune_stale():
    """把陈旧文件**移出**目标目录（移到 `%TEMP%/qihang-release-retired/<本次运行>/`，不删）。

    ⚠️ 为什么必须有这一步：本工具是**原地覆盖**（不做递归删除，理由见文件头 §二），
    所以「上一版导出过、这一版已不在导出集」的文件会**静默留在交付物里**。
    实测就踩过：v2.10 的发布副本里留着已退役的 `library/` 下那份同名入口文件
    （正是「同名双入口」缺陷本身）—— 不清掉就等于把已修好的缺陷重新发出去。
    只在**文件**粒度操作，绝不删目录；超过 MAX_PRUNE 则只报不动，交人工。
    """
    stale = report_stale()
    if not stale:
        return []
    if len(stale) > MAX_PRUNE:
        print('  ⚠️ 陈旧文件 %d 个 > 上限 %d —— **未自动清理**，请人工确认后处理：'
              % (len(stale), MAX_PRUNE))
        for x in stale[:25]:
            print('      ' + x)
        return []
    base = os.path.join(tempfile.gettempdir(), 'qihang-release-retired')
    os.makedirs(base, exist_ok=True)
    dest_root = tempfile.mkdtemp(prefix='run-', dir=base)
    moved = []
    for r in stale:
        src = os.path.join(DST, r)
        if not os.path.isfile(src):
            continue
        dst = os.path.join(dest_root, r)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
        moved.append(r)
    if moved:
        report('已移出不属于导出集的陈旧文件 %d 个（未删除，可回滚）：%s'
               % (len(moved), '、'.join(_soft(x) for x in moved[:10])))
        print('      回滚点：%s' % dest_root.replace('\\', '/'))
    return moved


# ═══════════════════════════════════════════════════════════════════
# 3. 清理：断链引用
# ═══════════════════════════════════════════════════════════════════

def fix_refs():
    """断链引用清理：删掉目录树里的登记行、改写句子里的提及。"""
    removed, changed = 0, 0
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if not fn.endswith(('.md', '.html', '.sh', '.py', '.yaml', '.json')):
                continue
            p = rel_path(os.path.join(base, fn))
            if p == 'MANIFEST.md':
                continue
            t = o = rd(p)
            # ① 目录树行：整行只登记被排除文件 → 删行
            lines = []
            for ln in t.split('\n'):
                s = ln.strip()
                if s.startswith(('│', '├', '└', '    ')) and (
                        any(x in ln for x in _EXCL_NAMES)
                        or any(x in ln for x in _EXCL_DIR_HINTS)):
                    removed += 1
                    continue
                lines.append(ln)
            t = '\n'.join(lines)
            # ② 整段「开发侧过程文档 N 份」描述块（v2.11 PROJECT.md 目录树里的写法）
            #    形如：`│   （开发侧过程文档 8 份 …，见 .gitignore）` + 后续若干 `│` 行
            t2 = re.sub(r'^│[^\n]*开发侧过程文档[^\n]*\n(?:│[^\n]*\n)*', '', t, flags=re.M)
            if t2 != t:
                # 删完常留一条孤零零的 `│` 分隔线，一并收掉
                t2 = re.sub(r'^│[ \t]*\n(?=├)', '', t2, flags=re.M)
                t = t2
            # ③ 句子级提及：把「（见 `references/某报告.md`）」这类括注去掉
            t = re.sub(r'（见 `?references/(?:' + '|'.join(
                re.escape(os.path.splitext(n)[0]) for n in _EXCL_NAMES) + r')`?[^）]*）', '', t)
            # ④ 行内裸引用 → 统一话术
            t = re.sub(r'`references/(?:' + '|'.join(
                re.escape(n) for n in _EXCL_NAMES) + r')`',
                '内部过程报告（未随包交付）', t)
            if t != o:
                wr(p, t)
                changed += 1
    report('目录树/引用清理：删除 %d 行登记项，改写 %d 个文件' % (removed, changed))


def fix_selfcheck_deps():
    """selfcheck.sh 的发布期适配（**发布期补丁，不回写仓库**）。

    ① 「必备文件」清单里若还留着未交付的报告，移除；
    ② `[8b]` 末条断言看的是 `.gitignore` 的排除项数，而 `.gitignore` **不随包交付**
       → 副本里必须降级为「本副本已由发布器完成剔除，该断言不适用」，
       否则副本自检永远 FAIL（这是 v2.11 引入 `[8b]` 后暴露的发布期缺口）。
    """
    p = 'scripts/selfcheck.sh'
    if not os.path.exists(os.path.join(DST, p)):
        return
    t = o = rd(p)
    # ① 旧版遗留的必备文件精简（v2.11 的 REQ 已不再列这些文件，规则保留以兼容旧树）
    t = t.replace('references/acceptance-v2.md ', '')
    t = t.replace(' references/validation-report.md', '')
    # ② [8b] .gitignore 断言 → 副本内降级
    old_g = ('_gi=$(grep -c \'^references/.*[.]md$\' .gitignore 2>/dev/null); _gi=${_gi:-0}\n'
             '[ "$_gi" -ge 8 ] && ok "开发侧过程文档已由 .gitignore 排除（$_gi 项）" \\\n'
             '  || bad "gitignore 排除不足（$_gi 项，期望 ≥8）"')
    new_g = ('# v2.11 发布副本：.gitignore 不随包交付，排除已在导出阶段完成 —— 断言降级为说明项\n'
             'if [ -f .gitignore ]; then\n'
             '  _gi=$(grep -c \'^references/.*[.]md$\' .gitignore); _gi=${_gi:-0}\n'
             '  [ "$_gi" -ge 8 ] && ok "开发侧过程文档已由 .gitignore 排除（$_gi 项）" \\\n'
             '    || bad "gitignore 排除不足（$_gi 项，期望 ≥8）"\n'
             'else\n'
             '  ok "发布副本：无 .gitignore（过程文档已在导出阶段剔除）"\n'
             'fi')
    if old_g in t:
        t = t.replace(old_g, new_g)
    if t != o:
        wr(p, t)
        report('selfcheck.sh：发布期适配（必备清单 + [8b] .gitignore 断言降级）')
    else:
        drift('selfcheck.sh：发布期适配未命中（[8b] 断言文本已变）')


# ═══════════════════════════════════════════════════════════════════
# 4. 清理：字段
# ═══════════════════════════════════════════════════════════════════

def fix_fields():
    """字段清理：占位值、进度标记、文档内版本标注。"""
    # 1) config.yaml 占位值
    p = 'config.yaml'
    t = rd(p)
    if '待填写' in t:
        t = t.replace('  college: 待填写          # 例：计算机科学与技术学院',
                      '  college: 计算机科学与技术学院   # 示例值：请改成你所在学院')
        wr(p, t)
        report('config.yaml：college 占位值「待填写」→ 示例值')
    # 2) ROADMAP 进度标记
    p = 'ROADMAP.md'
    t = o = rd(p)
    t = t.replace('| **6** | 试点与迭代（可选） | 真实新生试用 | ⬜ 未启动 |',
                  '| **6** | 试点与迭代（可选） | 真实新生试用 | 不在本次交付范围 |')
    t = t.replace('| 22 项未核实清单补齐 | ⏳ 转后续人工 |',
                  '| 22 项未核实清单补齐 | 需校园网或人工核验 |')
    t = t.replace('6. ⏳ **22 项「未核实清单」URL** 未补齐', '6. **22 项「未核实清单」URL** 待补齐')
    t = t.replace('| 跨会话实跑验证 | ⏳ 转阶段 5 |', '| 跨会话实跑验证 | 转阶段 5 验证 |')
    t = t.replace('| 跨会话记忆实跑 | ⏳ 需真实使用 2 次以上（唯一未闭环项） |',
                  '| 跨会话记忆实跑 | 需真实使用 2 次以上 |')
    t = t.replace('## 阶段 6 · 试点与迭代（可选）⬜', '## 阶段 6 · 试点与迭代（可选）')
    # 版本沿革里的「（N 文件，生成器驱动）」——副本不含生成器，且文件数口径不同 → 去掉括注
    t = re.sub(r'（\d+\s*文件，生成器驱动）', '', t)
    if t != o:
        wr(p, t)
        report('ROADMAP.md：进度类字段已改写（未启动 / 转后续人工 / 生成器口径）')
    # 3) 文档内版本/流程标注
    targets = ['library/output-spec.md', 'library/clarity.md', 'library/domain-review-cases.md',
               'library/output-checklist.md', 'library/login-policy.md', 'domains/_registry.md']
    n = 0
    for p in targets:
        if not os.path.exists(os.path.join(DST, p)):
            continue
        t = o = rd(p)
        t = re.sub(r'（v2\.\d+(?:\.\d+)?[^）]{0,24}）(?=\s*$)', '', t, flags=re.M)
        t = re.sub(r'^> \*\*v2\.\d+[^\n]*\n(?:>[^\n]*\n)*\n?', '', t, flags=re.M)
        if t != o:
            wr(p, t)
            n += 1
    report('文档内版本/流程标注：清理 %d 个文件' % n)


def fix_internal_refs():
    """精确改写「只对开发仓库成立」的引用与内部流程字样。"""
    rules = [
        # PROJECT：验收行不再指向未交付的报告
        ('PROJECT.md',
         '`e2e-scenarios.md` 3 条路径 + 开发侧验收报告（15 项通过 14 项）',
         '`e2e-scenarios.md` 3 条端到端路径'),
        ('PROJECT.md', '（生成器驱动 · 19 域', '（19 域'),
        # README：复用表不再指向未交付的生成器
        ('README.md',
         '| 加/改域 | `scripts/_build/build_qihang_v2.py` 的 `DOMAINS` → 重跑 | 改数据即可 |',
         '| 加/改域 | 需在**开发仓库**修改 `DOMAINS` 后重建（生成工具不随交付包提供） | — |'),
        # ROADMAP
        ('ROADMAP.md', '文档/脚本/生成器全量对齐', '文档与脚本全量对齐'),
        # CHANGELOG：`历史文档`，其版本沿革叙述保留；但**路径式**引用必须改掉，
        # 否则副本里 `scripts/_build/README.md` 不存在 → selfcheck [4] 报失效引用。
        ('CHANGELOG.md', '（见 `scripts/_build/README.md`）', '（见开发仓库的生成器链说明）'),
        # 域总表 / 比对矩阵：去掉「生成自某脚本」的维护性标注
        ('domains/_registry.md',
         '> 共 **19 个域 / 38 个库内 skill（每域 2 个）** ｜ 生成自 `scripts/_build/build_qihang_v2.py`，扩库层 `build_phase13.py`',
         '> 共 **19 个域 / 38 个库内 skill（每域 2 个）**'),
        ('references/skill-matrix-v3.md',
         '> 生成：`scripts/_build/build_phase14.py` ｜ 基准日 **2026-10-02**',
         '> 基准日 **2026-10-02**'),
        # audit.sh：去掉对未交付生成器目录的指引
        ('scripts/audit.sh',
         '# rmtree / rm -rf 单独说明：正式生成器须有护栏；旧位置的残留副本属陈旧文件',
         '# rmtree / rm -rf 单独说明：可执行文件里出现递归删除时必须带护栏'),
        ('scripts/audit.sh',
         '      ok "生成器含 rmtree 但已加「拒绝危险路径」护栏（$f）"',
         '      ok "含递归删除但已加「拒绝危险路径」护栏（$f）"'),
        ('scripts/audit.sh',
         '      bad "含 rmtree 且无护栏：$f —— 若位于 scripts/ 根目录，属陈旧副本，请删除（正式生成器在 scripts/_build/）"',
         '      bad "含递归删除且无护栏：$f"'),
        # selfcheck.sh：陈旧文件清单（gen 目录不交付 → 相关条目整条去掉）
        ('scripts/selfcheck.sh', 'scripts/_build/__pycache__', ''),
        ('scripts/selfcheck.sh',
         'scripts/build_qihang_v2.py scripts/build_phase1.py scripts/build_phase2.py"', '"'),
        ('scripts/selfcheck.sh', ' 2>/dev/null | grep -v _build | grep -v review-report',
         ' 2>/dev/null | grep -v clarity.md'),
        # 内部流程字样
        ('references/dlut-site-profiles.md', '（本轮普查新增）', '（普查新增）'),
        ('references/dlut-url-verification.md', '（本轮新发现）', '（复核新发现）'),
        ('references/dlut-url-verification.md', '### 本轮新增结论（已回写信息库）', '### 复核新增结论（已回写信息库）'),
        ('references/skill-matrix-v3.md', '（本轮实抓复核）', '（实抓复核）'),
    ]
    n = 0
    for p, a, b in rules:
        fp = os.path.join(DST, p)
        if not os.path.exists(fp):
            drift('改写跳过（文件不存在）：%s' % p)
            continue
        t = rd(p)
        if a not in t:
            drift('改写未命中：%s :: %s' % (p, a[:40]))
            continue
        wr(p, t.replace(a, b))
        n += 1
    # 全局：交付物里不再出现「本轮」
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if not fn.endswith(('.md', '.html')):
                continue
            p = rel_path(os.path.join(base, fn))
            if p == 'MANIFEST.md':
                continue
            t = rd(p)
            if '本轮' in t:
                wr(p, t.replace('本轮', '本次'))
                n += 1
    report('内部引用/流程字样改写：%d 处' % n)


def scrub_local_paths():
    """把交付物里的**本机绝对路径**归一化为环境变量写法（发布期擦洗，不回写仓库）。

    为什么必须做：`references/dlut-login-sites.md` §0.1 记录了「agent-browser 默认复用
    真实 Chrome profile」这一实测结论，其中带上了本机路径
    `C:\\Users\\<作者用户名>\\AppData\\Local\\Google\\Chrome\\User Data`。
    该段文本由**历史层 `build_phase17.py` 拥有**（不可改历史层；且全新链重跑会重新写入），
    所以在仓库里改成通用写法不可复现 → 只能在导出时擦掉。
    收包人不需要（也不应）知道作者的本机用户名与目录结构。
    """
    # ⚠️ 替换串必须是**函数**：写成字符串时 `re.sub` 会把末尾的反斜杠当转义序列
    #   → `re.PatternError: bad escape (end of pattern)`（实测踩过）。
    pats = [
        (re.compile(r'[A-Za-z]:\\Users\\[A-Za-z0-9_.\-]+\\AppData\\Local\\'),
         lambda m: '%LOCALAPPDATA%\\'),
        (re.compile(r'[A-Za-z]:\\Users\\[A-Za-z0-9_.\-]+\\AppData\\Roaming\\'),
         lambda m: '%APPDATA%\\'),
        (re.compile(r'[A-Za-z]:\\Users\\[A-Za-z0-9_.\-]+\\'),
         lambda m: '%USERPROFILE%\\'),
    ]
    n = 0
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if not fn.endswith(('.md', '.html', '.sh', '.py', '.yaml', '.json', '.txt')):
                continue
            p = rel_path(os.path.join(base, fn))
            if p == 'MANIFEST.md':
                continue
            t = o = rd(p)
            for rx, rep_ in pats:
                t = rx.sub(rep_, t)
            if t != o:
                wr(p, t)
                n += 1
    if n:
        # 注意：字面量里的 `%` 与 `%`-格式化冲突（实测 `TypeError: not enough arguments`），
        # 故这里用字符串拼接而不是 `%` 格式化。
        report('本机绝对路径归一化：' + str(n) + ' 个文件（%USERPROFILE% / %LOCALAPPDATA%）')
    return n


def fix_line_count_claim():
    """PROJECT.md 的文件总数刷新为**副本实测值**。

    ⚠️ 口径：`scripts/aligncheck.py` 的 `walk_files()` 会数到 `MANIFEST.md`
    （它只排除 .git/.idea/.learnbuddy/__pycache__ 与过程文档）。而本函数在
    `write_manifest()` **之前**执行，所以必须 **+1** 预算 MANIFEST，否则副本里
    aligncheck 必然报「声明 ≠ 实测」。

    ⚠️ 必须**排除已存在的根级 MANIFEST.md** 再 +1：否则「往已有副本再导一次」
    （最常见的维护动作）会把它数一遍、又 +1 → 声明值比实测多 1，副本自检直接挂。
    实测：第二遍导出声明 136、实测 135。

    返回 (交付文件数, 声明值)。
    """
    delivered = 0
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if fn == 'MANIFEST.md' and os.path.normcase(os.path.abspath(base)) \
                    == os.path.normcase(os.path.abspath(DST)):
                continue
            delivered += 1
    n = delivered + 1          # +1 = 待写入的 MANIFEST.md
    p = 'PROJECT.md'
    t = rd(p)
    t2 = re.sub(r'\*\*(?:\d{2,4}\+\s*文件|\d{2,4}\s*个文件)\*\*',
                '**%d 个文件**' % n, t)
    if t2 != t:
        wr(p, t2)
    report('PROJECT.md：文件总数刷新为 %d（副本实测 %d + MANIFEST）' % (n, delivered))
    return delivered, n


# ═══════════════════════════════════════════════════════════════════
# 5. 校验与清单
# ═══════════════════════════════════════════════════════════════════

def dangling_check():
    """交付物里是否还残留对「已排除文件」的引用。

    判据分两档（**不要合成一档**）：
      · 文档（.md/.html）：**裸文件名**也算引用 —— 读者看到 `` `validation-report.md` ``
        就会去找它；
      · 脚本（.sh/.py/.yaml/.json）：只认**路径式**引用（`references/xxx.md`、
        `scripts/_build/…`）。脚本里出现裸文件名往往是**常量表**，不是引用 ——
        实测 `scripts/aligncheck.py` 的 `DEV_ONLY_DOCS` 集合就是故意列出这 8 个名字，
        合成一档会恒定误报 8 处。
    另：`CHANGELOG.md` 是标注了「历史文档」的**已发生变更记录**，其中提到的
    生成器文件名是历史事实而非可访问路径，故豁免目录提示词扫描。
    """
    left = []
    for base, dirs, fns in os.walk(DST):
        dirs[:] = [x for x in dirs if x not in NOISE_DIRS]
        for fn in fns:
            if not fn.endswith(('.md', '.html', '.sh', '.py', '.yaml', '.json')):
                continue
            p = rel_path(os.path.join(base, fn))
            if p == 'MANIFEST.md':
                continue
            t = rd(p)
            is_doc = fn.endswith(('.md', '.html'))
            pats = list(_EXCL_DIR_HINTS) + (_EXCL_NAMES if is_doc else [])
            if p == 'CHANGELOG.md':
                # 历史文档：版本沿革里提到的生成器文件名是历史事实
                pats = [x for x in pats if x not in _EXCL_DIR_HINTS]
            for x in pats:
                if x in t:
                    left.append('%s ← %s' % (p, x))
    if left:
        report('⚠️ 仍有 %d 处断链引用：' % len(left))
        for x in left[:25]:
            print('      ' + x)
    else:
        report('✅ 无断链引用')
    return left


def write_manifest(total):
    n_build = len([x for x in EXCLUDED if x.startswith(BUILD_DIR + '/')])
    n_refs = len(EXCLUDED_REFERENCES)
    lines = [
        '# 「启航」学伴包 · 发布副本说明（MANIFEST）',
        '',
        '> 本目录是**只含交付物**的发布副本，由开发仓库的 `make_release.py` 导出。',
        '> 开发仓库另含生成器与过程文档；本副本不含它们。',
        '',
        '## 一、交付内容（%d 个文件）' % total,
        '',
        '| 目录 | 内容 |',
        '|---|---|',
        '| `SKILL.md` / `INSTALL.md` / `README.md` / `PROJECT.md` / `ROADMAP.md` | 入口、安装、说明、路线 |',
        '| `CHANGELOG.md` / `LICENSE` / `THIRD_PARTY_NOTICES.md` | 变更记录、许可、第三方归属 |',
        '| `config.yaml` | 学校绑定 + 学期配置 + 域开关 |',
        '| `.codebuddy-plugin/plugin.json` | 插件清单 |',
        '| `library/` | 1 级 skill 库（入口 README + 7 份规则文件） |',
        '| `domains/` | 19 个域 + 38 个库内 skill |',
        '| `commands/` | 21 张域入口卡 |',
        '| `references/` | DUT 信息库、平台适配、库外比对矩阵、端到端演示等 |',
        '| `scripts/` | 管理脚本 + 私密站只读脚本 + 4 个自检/审计/回归/对齐脚本 |',
        '| `qihang-scenario-design.html` | 赛道二场景设计书 |',
        '',
        '## 二、本次**未**包含（已在导出阶段剔除）',
        '',
        '| 类别 | 具体 | 理由 |',
        '|---|---|---|',
        '| 内部过程报告（%d 份） | `validation-report`、`acceptance-v2`、`review-report-v2.2/2.3/2.4`、'
        '`stress-test-v3`、`alignment-audit-v3`、`需求确认书-v2三级结构` | AI 自审过程产物，非产品本身 |' % n_refs,
        '| 开发期生成器（%d 个） | `scripts/_build/`（含本发布器自身） | 仅供维护者改数据重建，运行不需要 |' % n_build,
        '| IDE / 缓存 / 临时 | `.idea/`、`__pycache__`、`*.pyc`、`.selfcheck.tmp*` | 环境残留 |',
        '| AI 工作记忆 | `.learnbuddy/` | 内部工作日志与约定 |',
        '| 版本控制元数据 | `.git/`、`.gitignore`、`.gitattributes` | 提交时由使用者自行初始化 |',
        '',
        '## 三、已做的字段清理',
        '',
    ]
    for x in REPORT:
        lines.append('- ' + x)
    lines += [
        '',
        '## 四、注意',
        '',
        '- 交付物内所有对上述剔除文件的引用已一并改写；脚本不再依赖它们。',
        '- 自检脚本 `scripts/selfcheck.sh` 的「必备文件」清单已同步更新；',
        '  其 `[8b]` 中依赖 `.gitignore` 的排除项断言在副本内已降级为说明项。',
        '- 如需自行维护本包（改域、重建），请回到**开发仓库**使用 `scripts/_build/`。',
        '- DUT 信息库中标 ⚠️ 的条目**未经核验**，请勿直接使用。',
        '',
    ]
    wr('MANIFEST.md', '\n'.join(lines))
    report('已写出 MANIFEST.md')


# ═══════════════════════════════════════════════════════════════════
# 6. 主流程
# ═══════════════════════════════════════════════════════════════════

def main():
    global DST
    if len(sys.argv) > 1:
        DST = os.path.abspath(sys.argv[1])

    # ---- 护栏 ----
    if os.path.normcase(os.path.abspath(DST)) == os.path.normcase(SRC):
        raise SystemExit('拒绝执行：目标目录 == 源仓库（%s）' % SRC)
    try:
        if os.path.commonpath([os.path.abspath(DST), SRC]) == SRC:
            raise SystemExit('拒绝执行：目标目录在源仓库内部（%s）' % DST)
    except ValueError:
        pass   # 跨盘符，必然不同路径
    if os.path.exists(DST) and not os.path.isdir(DST):
        raise SystemExit('拒绝执行：目标路径不是目录（%s）' % DST)

    print('=' * 68)
    print('「启航」发布副本构建器')
    print('=' * 68)
    print('  源仓库  : %s' % SRC)
    print('  目标目录: %s' % DST)
    print('  导出集合: git ls-files（--cached --others --exclude-standard）∩ 磁盘')
    print('  应交付  : %d 个文件' % len(DELIVERED))
    print('  已排除  : %d 个文件（含过程文档 %d · 生成器 %d）'
          % (len(EXCLUDED), len(EXCLUDED_REFERENCES),
             len([x for x in EXCLUDED if x.startswith(BUILD_DIR + '/')])))
    if MISSING_IN_DISK:
        print('  索引残留（磁盘已删，自动跳过）: %s' % ', '.join(MISSING_IN_DISK))
    print('-' * 68)

    os.makedirs(DST, exist_ok=True)
    copy_tree()
    prune_stale()
    fix_refs()
    fix_selfcheck_deps()
    fix_fields()
    fix_internal_refs()
    scrub_local_paths()
    total, declared = fix_line_count_claim()
    left = dangling_check()
    write_manifest(total)

    print('=' * 68)
    if DRIFT:
        print('工具与树状态不一致 %d 处（不写入 MANIFEST，需维护者跟进）：' % len(DRIFT))
        for x in DRIFT:
            print('  ! ' + x)
    print('完成：交付 %d 个文件（+MANIFEST → 声明 %d）→ %s' % (total, declared, DST))
    if left:
        print('仍有 %d 处断链引用，需继续处理' % len(left))
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
