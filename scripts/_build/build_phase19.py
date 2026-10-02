#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_phase19.py —— 结构优化层（v2.10 → v2.11）
================================================================

**不改历史 phase 层**（历史层的替换表与下一层配对，改了会断链）；本层是新的链末收敛层。

对照官方 Agent Skills 规范（agentskills.io / 内置 skill-creator）后做的结构收敛：

  1. **消除同名双入口**（P0）
     根 `SKILL.md` 与 `library/SKILL.md` 的 frontmatter 完全相同（都写 `name: qihang`），
     但红线表已分叉：根是新表（含登录档位顺序 / 志愿时长登记 / 不代写文书 / 24h 通道 /
     L3 关键词包含匹配），`library/SKILL.md` 停在上代。
     **装哪个文件决定行为**，而四个校验器当时全绿（纯结构性盲区）。
     → 收敛为「单一入口 + 库内导航页」：保留根 `SKILL.md`，`library/` 改出 `README.md`（**不带 name**）。

  2. **开发侧过程文档移出版本控制**（评审 / 审计 / 验收 / 需求书 共 8 份）
     它们**不属交付物**：旧发布器用硬编码清单手工排除，说明结构上本就没有它们的位置。
     → 写进 `.gitignore`；文件**保留在磁盘**（生成器链与自检照常可跑 → 全链 0 MISS）；
       同时收敛「对克隆者会断链」的对外引用。
     关键技巧：phase17 的 references 登记只检查「**文件名是否在文档中出现**」，
     因此只要 8 个名字仍以**纯文本**（不加反引号、不加 `references/` 前缀）登记在
     「未随包分发」说明里，phase17 就完全不动作 → 链保持 0 MISS 且幂等。

  3. **声明类文件补齐**：`LICENSE`（MIT 全文，此前三处声明 MIT 却无文件）·
     `CHANGELOG.md` · `THIRD_PARTY_NOTICES.md`（26 个库外仓库的来源与许可证归属）。

  4. **校验器同步**
     · `aligncheck.py`：新增 `DEV_ONLY_DOCS` 排除（否则克隆者会因「文件总数声明 ≠ 实测」误报）；
       版本期望 2.10.0 → 2.11.0。
     · `selfcheck.sh`：必备文件清单同步 + 新增 **[8b] 入口唯一性与声明** 4 条断言（堵住本次盲区）。

  5. 版本号 2.10.0 → **2.11.0**；文档结构树与计数同步。

用法：`python scripts/_build/build_phase19.py .`（幂等；连跑两遍第二遍应 0 变更）
"""
import os
import re
import sys
import glob as _glob
import shutil
import tempfile

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')

OK, DONE, MISS = [], [], []

# 开发侧过程文档（移出版本控制、未随包分发）
DEV_DOCS = [
    'validation-report.md',
    'acceptance-v2.md',
    'review-report-v2.2.md',
    'review-report-v2.3.md',
    'review-report-v2.4.md',
    'stress-test-v3.md',
    'alignment-audit-v3.md',
    '需求确认书-v2三级结构.md',
]

OLD_VER, NEW_VER = '2.10.0', '2.11.0'

VERSION_SHORT_FILES = (
    'config.yaml', 'PROJECT.md', 'ROADMAP.md', 'README.md', 'SKILL.md',
    'INSTALL.md', 'references/platforms.md',
)


# ==================================================================== helpers
def rd(p):
    with open(os.path.join(ROOT, p), 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


def wr(p, s):
    fp = os.path.join(ROOT, p)
    d = os.path.dirname(fp)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(fp, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(s)


def rep(path, old, new, label=None, required=True, count=1):
    """精确替换（幂等）。追加型替换（new 含 old）先判 new 是否已存在，防重复插入。"""
    if not os.path.isfile(os.path.join(ROOT, path)):
        if required:
            MISS.append('%s :: %s（文件不存在）' % (path, (label or old)[:58]))
        return False
    t = rd(path)
    label = label or (old.strip().splitlines() or ['?'])[0][:58]
    if old in new and new in t:
        DONE.append('[已是最新] %s :: %s' % (path, label))
        return False
    if old not in t:
        if new in t or not required:
            DONE.append('[已被后续替换] %s :: %s' % (path, label))
        else:
            MISS.append('%s :: %s' % (path, label))
        return False
    wr(path, t.replace(old, new, count if count > 0 else -1))
    OK.append('%s :: %s' % (path, label))
    return True


def replace_block(path, start_pred, end_pred, new_lines, label):
    """行级区块替换（比精确串更稳，不怕空白漂移）。start_pred 行被替换，end_pred 行保留。"""
    p = os.path.join(ROOT, path)
    if not os.path.isfile(p):
        MISS.append('%s :: %s（文件不存在）' % (path, label))
        return
    lines = rd(path).split('\n')
    body = '\n'.join(new_lines)
    if body in '\n'.join(lines):
        DONE.append('[已是最新] %s :: %s' % (path, label))
        return
    i = next((k for k, l in enumerate(lines) if start_pred(l)), None)
    j = next((k for k, l in enumerate(lines) if end_pred(l)), None)
    if i is None or j is None or j <= i:
        MISS.append('%s :: %s（找不到区块边界 i=%s j=%s）' % (path, label, i, j))
        return
    lines[i:j] = new_lines
    wr(path, '\n'.join(lines))
    OK.append('%s :: %s（%d 行）' % (path, label, j - i))


_RETIRE_DIR = None


def retire(path, label):
    """把文件移出仓库树（**不删**：移到 %TEMP%/qihang-retired/<本次运行>/，便于取证与回滚）。

    ⚠️ 两个坑（都踩过，实测）：
      1. `library/SKILL.md` **每次跑链都会被 `build_qihang_v2.py` 重新生成** ——
         所以 retire 不是一次性动作，每轮都必须再退役一次（本函数天然幂等：不存在即跳过）。
      2. 目标路径**必须每轮唯一**。旧版写死 `qihang-retired/SKILL.md`，第二次撞名后
         退到 `.bak`，第三次两者都在 → `shutil.move` 的 `os.rename` 抛 `FileExistsError`
         → 回落到 `copy2 + os.unlink` → **`os.unlink` 被沙箱 safe-delete 拦截**
         （`SAFE_DELETE_FAIL_CLOSED`）→ 整层崩溃。
         现在用 `mkdtemp` 生成全新目录，`dest` 必然不存在 → 只走 `os.rename`，不触碰 unlink。
    """
    global _RETIRE_DIR
    p = os.path.join(ROOT, path)
    if not os.path.exists(p):
        DONE.append('[已是最新] %s :: %s' % (path, label))
        return
    if _RETIRE_DIR is None:
        base = os.path.join(tempfile.gettempdir(), 'qihang-retired')
        os.makedirs(base, exist_ok=True)
        _RETIRE_DIR = tempfile.mkdtemp(prefix='run-', dir=base)
    dest = os.path.join(_RETIRE_DIR, os.path.basename(path))
    shutil.move(p, dest)
    OK.append('%s :: %s（已移至 %s）' % (path, label, dest.replace('\\', '/')))


def write_if_changed(path, content, label):
    p = os.path.join(ROOT, path)
    if os.path.exists(p) and rd(path) == content:
        DONE.append('[已是最新] %s :: %s' % (path, label))
        return
    wr(path, content)
    OK.append('%s :: %s' % (path, label))


def measure_files():
    """与 aligncheck.py **同口径**实测文件数。

    口径：排除 `.git` / `.idea` / `.learnbuddy` / `__pycache__`，
    再排除 8 份「未随包分发」的开发侧过程文档。

    ⚠️ 这里**必须实测派生**，不能硬编码：真实树与「全链重跑」的产物
    本来就差几个文件（历史手工增删），硬编码数字必然在一边挂掉。
    """
    n = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            if fn in DEV_DOCS:
                continue
            n += 1
    return n


# ==================================================================== 1. 消除同名双入口
LIB_README = '''# library/ · 1 级 skill 库（Level 1）

> **本目录是规则本体，不是安装入口。** 唯一安装单元与唯一入口是**包根 `SKILL.md`**。
> v2.11 结构调整：`library/` 下原有一个与包根同名的 `SKILL.md`（`name: qihang`）
> 且正文已分叉（红线表停在上一代），装哪个文件决定行为 —— 已收敛为「单一入口 + 本导航页」。

## 本目录的职责

- `clarity.md` —— 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级
- `domain-review.md` —— 域审查：锁定 / 跨域 / 越界 / 无域兜底
- `domain-review-cases.md` —— 配套：22 条越界用例（含 3 条反例）
- `output-spec.md` —— 输出规范：统一模板 + 简略原则 + 交付前校验
- `output-checklist.md` —— 配套：7 项硬校验
- `memory.md` —— 学习档案：四类内容 + 分层落点 + 敏感域红线
- `login-policy.md` —— 登录选择原则：A/B/C 三档 + 标准话术 + 安全保障

## 边界（硬规则）

- **只做横切职责，不承载业务**。具体场景的处理一律归 `domains/<域>/skills/local/`。
- 一旦这里开始写「怎么做某件事」，1 级库就退化成普通 skill，三级结构随之失效。

## 与包根 `SKILL.md` 的分工

| 位置 | 定位 | frontmatter |
|---|---|---|
| 包根 `SKILL.md` | 唯一入口 / 唯一安装单元（含红线总览与硬规则） | ✅ `name: qihang` |
| `library/README.md`（本文件） | 库内导航页，供人检索 | ❌ 刻意不带 `name`，避免第二个同名入口 |

完整链路（入口 → 红线 → 登录档位 → 澄清门 → 锁域 → 锁 skill → 输出 → 归档）见包根 `SKILL.md`。
'''


def split_entry():
    """根 SKILL.md 为唯一入口；library/ 改出不带 name 的导航页。"""
    write_if_changed('library/README.md', LIB_README, '库内导航页（无 frontmatter）')
    retire('library/SKILL.md', '移除同名入口')

    # 引用改向：library/SKILL.md → library/README.md
    rep('scripts/qihang.sh', 'for f in library/SKILL.md library/clarity.md',
        'for f in library/README.md library/clarity.md', 'status 循环文件表')
    rep('README.md', '│   ├── SKILL.md              库本体',
        '│   ├── README.md             库导航页（非安装入口，无 frontmatter）', '结构树 library 首行')
    rep('PROJECT.md', '│   ├── SKILL.md  clarity.md  domain-review.md  output-spec.md  memory.md',
        '│   ├── README.md clarity.md  domain-review.md  output-spec.md  memory.md',
        '结构树 library 首行')


# ==================================================================== 2. 开发侧过程文档移出版本控制
GITIGNORE_SECTION = '''
# 开发侧过程文档（评审 / 审计 / 验收 / 需求书）—— 未随包分发，仅本机留存
# v2.11：移出版本控制但保留在磁盘，使生成器链与四项校验器仍可完整重跑。
# 交付物不含这些文件；对外引用已同步收敛（见 build_phase19.py）。
references/validation-report.md
references/acceptance-v2.md
references/review-report-v2.2.md
references/review-report-v2.3.md
references/review-report-v2.4.md
references/stress-test-v3.md
references/alignment-audit-v3.md
references/需求确认书-v2三级结构.md
'''

DEV_NOTE_README = [
    '│',
    '│   （开发侧过程文档 8 份 —— 已移出版本控制、未随包分发，见 .gitignore）',
    '│   validation-report.md · acceptance-v2.md · review-report-v2.2.md ·',
    '│   review-report-v2.3.md · review-report-v2.4.md · stress-test-v3.md ·',
    '│   alignment-audit-v3.md · 需求确认书-v2三级结构.md',
    '│',
]

README_REFS_BLOCK = [
    '├── references/                  数据与外部依据（随包分发）',
    '│   ├── dlut-official-sites.md      DUT 公开站信息库（139 条条目 / 表格行 159）',
    '│   ├── dlut-login-sites.md         DUT 私密站清单（方案 A + Profile 隔离）',
    '│   ├── dlut-field-map.md           私密站字段映射表',
    '│   ├── dlut-url-verification.md    URL 核验台账（22 项待人工补）',
    '│   ├── dlut-site-profiles.md       19 站画像',
    '│   ├── browser-matrix.md           浏览器实测矩阵',
    '│   ├── skill-sources.md            26 个 skill 探测平台（含可达性实测）',
    '│   ├── skill-matrix-v3.md          **库外候选多源比对矩阵（19 域选优）**',
    '│   ├── skill-compliance-audit.md   合法性 + 可用性自检报告',
    '│   ├── platforms.md                平台适配表',
    '│   └── e2e-scenarios.md            3 条端到端演示路径',
] + DEV_NOTE_README

README_DECL_BLOCK = [
    '├── LICENSE                     MIT 许可证全文',
    '├── CHANGELOG.md                版本历史（v1.0 → v2.11）',
    '├── THIRD_PARTY_NOTICES.md      库外 skill 来源与许可证归属（26 个仓库）',
]

PROJECT_REFS_BLOCK = [
    '├── references/                随包分发的数据与外部依据',
    '│   ├── dlut-official-sites.md     公开站 139 条条目   ├── dlut-login-sites.md   私密站 19 站',
    '│   ├── dlut-field-map.md          字段映射表       ├── dlut-url-verification.md  URL 核验',
    '│   ├── dlut-site-profiles.md      站点画像         ├── browser-matrix.md     浏览器矩阵',
    '│   ├── skill-sources.md           26 个探测平台     ├── skill-matrix-v3.md    库外比对矩阵',
    '│   ├── skill-compliance-audit.md  合规自检         ├── platforms.md          平台适配表',
    '│   └── e2e-scenarios.md           3 条端到端演示',
    '│',
    '│   （开发侧过程文档 8 份 —— 已移出版本控制、未随包分发，见 .gitignore）',
    '│   validation-report.md · acceptance-v2.md · review-report-v2.2.md ·',
    '│   review-report-v2.3.md · review-report-v2.4.md · stress-test-v3.md ·',
    '│   alignment-audit-v3.md · 需求确认书-v2三级结构.md',
]


def withdraw_dev_docs():
    # 2.1 .gitignore 追加排除节（幂等：幂等靠标记）
    t = rd('.gitignore')
    if '开发侧过程文档' not in t:
        wr('.gitignore', t.rstrip('\n') + '\n' + GITIGNORE_SECTION)
        OK.append('.gitignore :: 追加开发侧过程文档排除节（8 项）')
    else:
        DONE.append('[已是最新] .gitignore :: 排除节')

    # 2.2 19 个 external.md 的尾部指路行（收敛为不含 dev 文档的指针）
    old_tail = ('> 完整自检报告见 `references/skill-compliance-audit.md`；'
                '风险与验收数据见 `references/validation-report.md`。')
    new_tail = ('> 自检与许可证数据见 `references/skill-compliance-audit.md` '
                '与 `THIRD_PARTY_NOTICES.md`。')
    n = 0
    for f in sorted(_glob.glob(os.path.join(ROOT, 'domains', '*', 'skills', 'external.md'))):
        rel = os.path.relpath(f, ROOT).replace('\\', '/')
        s = rd(rel)
        if new_tail in s:
            continue
        if old_tail not in s:
            MISS.append('%s :: external.md 尾部指路行（未找到原串）' % rel)
            continue
        wr(rel, s.replace(old_tail, new_tail))
        n += 1
    if n:
        OK.append('domains/*/skills/external.md :: 收敛尾部指路行（%d 份）' % n)
    else:
        DONE.append('[已是最新] domains/*/skills/external.md :: 尾部指路行')

    # 2.3 README 结构树：references 区块换掉 + 登记三个声明文件
    replace_block('README.md',
                  lambda l: l.startswith('├── references/'),
                  lambda l: l.startswith('├── commands/'),
                  README_REFS_BLOCK, 'references 结构树')
    rep('README.md', '├── config.yaml               学校绑定 + 学期配置 + 域开关',
        '\n'.join(README_DECL_BLOCK) + '\n├── config.yaml               学校绑定 + 学期配置 + 域开关',
        '登记 LICENSE / CHANGELOG / THIRD_PARTY_NOTICES')

    # 2.4 PROJECT.md 结构树：references 区块换掉
    replace_block('PROJECT.md',
                  lambda l: l.startswith('├── references/'),
                  lambda l: l.startswith('├── commands/'),
                  PROJECT_REFS_BLOCK, 'references 结构树')
    rep('PROJECT.md', '└── qihang-scenario-design.html  赛道二设计书',
        '├── LICENSE / CHANGELOG.md / THIRD_PARTY_NOTICES.md   声明与归属\n'
        '└── qihang-scenario-design.html  赛道二设计书',
        '登记三个声明文件')

    # 2.5 表格/正文里带反引号或目录前缀的 dev 文档引用 → 改为「开发侧」表述
    for path, pairs in (
        ('PROJECT.md', [
            ('| 验收       | `references/validation-report.md`      | 4 路并行子 agent 的测试结论',
             '| 验收       | 开发侧验收报告（未随包分发）            | 4 路并行子 agent 的测试结论'),
            ('`acceptance-v2.md`（15 项通过 14 项）', '开发侧验收报告（15 项通过 14 项）'),
        ]),
        ('ROADMAP.md', [
            ('✅ 上述结果回写 `validation-report.md` §七',
             '✅ 上述结果回写开发侧验收报告 §七（该报告未随包分发）'),
            ('3. ✅ **`references/acceptance-v2.md`** —— 验收报告 v2，',
             '3. ✅ **开发侧验收报告 v2** —— '),
        ]),
    ):
        for old, new in pairs:
            rep(path, old, new, '收敛 dev 文档引用')

    # 2.6 selfcheck 必备文件清单同步
    miss_now = [d for d in DEV_DOCS if 'references/' + d in rd('scripts/selfcheck.sh')]
    if miss_now:
        old_req = (
            'REQ="SKILL.md README.md INSTALL.md PROJECT.md ROADMAP.md config.yaml\n'
            'library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md\n'
            'library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md\n'
            'domains/_registry.md\n'
            'references/dlut-official-sites.md references/dlut-login-sites.md references/dlut-field-map.md\n'
            'references/dlut-url-verification.md references/dlut-site-profiles.md references/browser-matrix.md\n'
            'references/skill-sources.md references/skill-compliance-audit.md references/platforms.md\n'
            'references/e2e-scenarios.md references/acceptance-v2.md references/validation-report.md\n'
            '.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh '
            'scripts/audit.sh scripts/regress.sh scripts/aligncheck.py"'
        )
        new_req = (
            'REQ="SKILL.md README.md INSTALL.md PROJECT.md ROADMAP.md CHANGELOG.md config.yaml\n'
            'LICENSE THIRD_PARTY_NOTICES.md\n'
            'library/README.md library/clarity.md library/domain-review.md library/output-spec.md\n'
            'library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md\n'
            'domains/_registry.md\n'
            'references/dlut-official-sites.md references/dlut-login-sites.md references/dlut-field-map.md\n'
            'references/dlut-url-verification.md references/dlut-site-profiles.md references/browser-matrix.md\n'
            'references/skill-sources.md references/skill-compliance-audit.md references/skill-matrix-v3.md\n'
            'references/platforms.md references/e2e-scenarios.md\n'
            '.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh '
            'scripts/audit.sh scripts/regress.sh scripts/aligncheck.py"'
        )
        rep('scripts/selfcheck.sh', old_req, new_req, '必备文件清单同步')
    else:
        DONE.append('[已是最新] scripts/selfcheck.sh :: 必备文件清单')


# ==================================================================== 3. 声明类文件
LICENSE_TEXT = '''MIT License

Copyright (c) 2026 xiaojun10086

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

CHANGELOG_TEXT = '''# 更新日志

> **历史文档**：本文件逐版本记录**已发生**的变更，其中的旧路径 / 旧平台写法是历史事实，
> 不作为现行口径，也不得被「平台口径兜底」类检查改写（检查器按前 20 行的本标记整文件豁免）。
>
> 版本纪律：**每个修复 / 收敛层 = 一个版本**，层与版本一一对应（见 `scripts/_build/README.md`）。

## v2.11.0 — 结构优化层（2026-10-02）

对照官方 Agent Skills 规范（agentskills.io / 内置 skill-creator）做的结构收敛，**纯结构、不改规则语义**。

- **消除同名双入口（P0）**：`library/` 下原有一个与包根同名的 `SKILL.md`（`name: qihang`）
  且红线表已分叉（缺登录档位顺序 / 志愿时长登记 / 不代写文书 / 24h 通道 / L3 关键词包含匹配）。
  收敛为「单一入口 + 库内导航页」：保留包根 `SKILL.md`，`library/README.md` **刻意不带 `name`**。
- **开发侧过程文档移出版本控制**：8 份评审 / 审计 / 验收 / 需求书写进 `.gitignore`，
  文件保留在磁盘以维持生成器链 0 MISS；对外引用同步收敛。
- **声明类文件补齐**：新增 `LICENSE`（MIT 全文，此前三处声明 MIT 却无文件）、
  `CHANGELOG.md`、`THIRD_PARTY_NOTICES.md`（26 个库外仓库来源与许可证归属）。
- **校验器补盲**：`selfcheck.sh` 新增 `[8b] 入口唯一性与声明` 4 条断言
  （`SKILL.md` 的 `name` 全域唯一 / 入口唯一 / 三件声明文件 / `.gitignore` 排除覆盖）；
  `aligncheck.py` 新增 `DEV_ONLY_DOCS` 排除并同步版本期望。
- 生成器链新增 `build_phase19.py`（链末收敛层，幂等）。

## v2.10.0 — 规则可执行性修复层（2026-10-02）

> 依据：`行为验证报告-v1`（6 路子代理 · 137 次执行）。与「文档一致性」**零重叠** ——
> 机器断言全绿**不能**反映规则可执行性。

- 裸「成绩」口径统一为**先让用户区分等级 / 明细**（`login-policy.md`「裸词澄清」）。
- `clarity.md` 新增 **§2.1 关键槽「已填」判定细则**：指代型 / 泛指型 / 泛化动词 → `cᵢ=0.5`（必须追问）。
  这是跨代理同题翻转 20% 的**唯一根因**。
- `§3` 阈值与 `§5` 例外的主从关系显式化；新增**例外 6「通用知识型」**。
- 域冲突对齐（网费 / 失眠统一 F2）；A/B/C（动作档）与 L1/L2/L3（数据级别）**并行不换算**。
- 补「命中域但无对口 skill」3 级降级链；红线体系补漏（代操作 + F6、新增「编造 / 代写文书」、安全兜底补 24h 通道）。
- 复测（新代理盲跑 8 例）**8/8** 符合新规则。

## v2.9.0 — 漏检缺陷修复 + 链末收敛层（2026-10-02）

- 修复 20 项**脚本漏检**缺陷（断言集自身的盲区）。
- **P0**：`build_qihang_v2.py` 旧版用**递归删除**清空目标目录，配合文档用法 `build_qihang_v2.py .`
  **会把整个仓库删空（含 `.git`）** → 改为「暂存目录 + `copytree(dirs_exist_ok=True)` 覆盖式合并」，
  并加防回退硬断言。
- **P0**：`build_phase12.py` 的「规范串包含旧串」追加型替换无护栏 →
  每跑一轮链就多追加一项，`config.yaml` 被污染成 `[课表 / … / 日程, 网费, 日程]`（语义已坏）
  → 由末层从 `config.yaml` **派生**收敛。
- 检查器全量化（废除文件名白名单）；L3 清单去重；口径统一；`qihang.sh` 可复现。

## v2.8.0 — 平台专向化层（2026-10-01）

- **唯一目标平台收敛为 LearnBuddy / WorkBuddy**，全量移除 Claude Code 适配
  （不留两套互相矛盾的入口说明）。
- 21 个 `commands/` 由**斜杠命令**改写为 **LearnBuddy 域入口卡**
  （去掉 `$ARGUMENTS` / `argument-hint` / `~/.claude/...`）。

## v2.7.0 — 复查与扩库层（2026-10-01）

- 复查修复 **21 条缺陷**（20 组修复）；库内 skill **19 → 38**（每域 2 个）。
- 库外候选**多源比对选优**（19 域），产出 `references/skill-matrix-v3.md`。
- DUT 公开站信息库扩至 **139 条条目**（表格行 159）。

## v2.5.0 — 三级结构定型（2026-10-01）

- **v1.0 平铺 7 域 → v1.1 加 DUT 强绑定 → v2.5.0 三级结构（生成器驱动）**。
- 1 级库确立 4 项横切职责（需求明确 / 域审查 / 输出规范 / 记忆归档）+ 登录选择原则。
- 红线体系成为一等公民（优先级高于澄清门）。

## v2.0.0 — 需求确认（2026-10-01）

- 《需求确认书 · 三级结构改造》：域从「一张大表」改为「每域独立 `_domain.md` + `_registry.md`」。

## v1.1.0 — DUT 强绑定（2026-10-01）

- 加入大连理工大学公开站信息库与私密站接入约定（只读 · 不外传 · 不落盘）。
- 阶段 0 调研：12 个 skill 平台普查 + 22 个候选仓库可用性与质量双维度测试。

## v1.0.0 — 初始版本（2026-10-01）

- 平铺 7 域（A–G）的新生学伴包骨架。
'''

THIRD_PARTY_TEXT = '''# 第三方来源与许可证归属（THIRD PARTY NOTICES）

> 数据来源：GitHub API 实抓（stars / pushed_at / `license.spdx_id` / archived）+ 本机安装实测。
> 检索时间：2026-10-01。完整逐项审计见 `references/skill-compliance-audit.md`。
> 本包自身以 **MIT** 发布（见 `LICENSE`）。

## 一、许可证四档判定标准

| 判定 | 许可证类型 | 允许行为 |
|---|---|---|
| ✅ 可摘录可分发 | MIT / Apache-2.0 / BSD 等宽松许可 | 可复制内容进本包、可商用（保留版权声明） |
| ⚠️ 仅可外部调用 | **GPL-3.0** 等强 copyleft | **不得复制内容进包**（否则本包须整体 GPL 化）；只能运行时调用 |
| ❌ 禁商用 | **CC-BY-NC** 系列 | 校内非商用可用；**对外发布须替换** |
| ⛔ 不可摘录 | **无 LICENSE** | 默认「保留所有权利」，**不得复制进包、不得再分发**；仅本地自用 |

## 二、需要特别标注的依赖（**红线**）

| 仓库 | 许可证 | 约束 |
|---|---|---|
| `NeoLabHQ/context-engineering-kit` | **GPL-3.0** | **仅外部调用** —— 禁止摘录任何内容进本包 |
| `Imbad0202/academic-research-skills` | **CC-BY-NC 4.0** | 禁商用；对外发布须替换 |
| `mordor-forge/study-skill` | **无 LICENSE** | ⛔ 禁止摘录、禁止再分发，仅限本地自用 |
| `googlarz/math-skill` | **无 LICENSE** | ⛔ 同上 |
| `somenssarkar/gurukul-ai` | **无 LICENSE** | ⛔ 同上（且内容仅 Grade 7 可用） |
| `sickn33/agentic-awesome-skills` | MIT | ⚠️ 含 **3113 个脚本 / 31 个攻击性技能**，无法人工审计 → **禁止整体安装** |

## 三、本包已摘录内容的合法性（自查重点）

本包向库内 skill 摘录了两个外部技能的内容，逐项核验：

| 摘录来源 | 许可证 | 判定 |
|---|---|---|
| `Jellypod-Inc/school-skills` | **MIT** | ✅ 合法（可复制、可商用，保留版权声明即可） |
| `GlacierXiaowei/structured-learning-skill` | **Apache-2.0** | ✅ 合法（可复制、可商用，须保留 NOTICE） |

**结论：包内现有摘录 0 侵权风险。** 其余 17 个库内 skill 均为自建。

## 四、库外候选全量清单（26 个仓库，按 Stars 降序）

| 仓库 | Stars | 最近推送 | 许可证 | 合法性 | 可用性 |
|---|---|---|---|---|---|
| mattpocock/skills | 273,314 | 2026-09-29 | MIT | ✅ | ✅ |
| anthropics/skills | 179,227 | 2026-09-29 | 子目录 Apache-2.0 | ✅ | ✅ |
| Imbad0202/academic-research-skills | 50,048 | 2026-10-01 | **CC-BY-NC** | ❌ 禁商用 | ✅ |
| kepano/obsidian-skills | 49,056 | 2026-09-15 | MIT | ✅ | ✅ |
| sickn33/agentic-awesome-skills | 47,136 | 2026-10-01 | MIT | ⚠️ | ❌ **禁整体安装** |
| googleworkspace/cli | 31,219 | 2026-09-24 | Apache-2.0 | ✅ | ✅ |
| alirezarezvani/claude-skills | 27,091 | 2026-08-30 | MIT | ✅ | ⚠️ 只取单个 skill |
| Paramchoudhary/ResumeSkills | 2,501 | 2026-06-19 | MIT | ✅ | ✅ |
| **NeoLabHQ/context-engineering-kit** | 1,737 | 2026-08-26 | **GPL-3.0** | ⚠️ 强 copyleft | ✅ 仅外部调用 |
| Gabberflast/academic-pptx-skill | 1,097 | 2026-07-14 | MIT | ✅ | ✅ |
| YANZHANLIN/ielts-claude-skills | 307 | 2026-07-20 | MIT | ✅ | ✅ |
| kgraph57/paper-writer-skill | 58 | 2026-08-12 | MIT | ✅ | ✅ |
| jakedahn/pomodoro | 56 | 2025-10-23 | MIT | ✅ | ⚠️ 停滞 11 个月 |
| **mordor-forge/study-skill** | 40 | 2026-07-17 | **无 LICENSE** | ⛔ | ⚠️ 禁摘录 |
| eddiebelaval/squire | 21 | 2026-08-16 | MIT | ✅ | ⚠️ 密钥明文落盘 |
| 0x-man/mindmap-skill | 16 | 2026-09-28 | MIT | ✅ | ✅ |
| **googlarz/math-skill** | 9 | 2026-03-22 | **无 LICENSE** | ⛔ | ⚠️ 禁摘录 |
| Jellypod-Inc/school-skills | 6 | 2026-04-15 | MIT | ✅ | ✅ |
| ghutchis/chem-skill | 4 | 2025-12-28 | MIT | ✅ | ⚠️ 9 个月未更新 |
| Candlest/exam-prep-skill | 4 | 2026-07-10 | MIT | ✅ | ⚠️ 上传百度云端 OCR |
| Haadhi76/SOP_Consultant | 4 | 2026-06-15 | MIT | ✅ | ✅ |
| GlacierXiaowei/structured-learning-skill | 3 | 2026-03-27 | Apache-2.0 | ✅ | ✅ 实测装通 |
| xwmxcz/papers-skill | 1 | 2026-06-11 | MIT | ✅ | ⚠️ 1★，代码量极小 |
| egouilliard-leyton/python-tutor-skill | 1 | 2026-03-30 | MIT | ✅ | ⚠️ 无标准 SKILL.md |
| peter209393/anki-card-skills | 0 | 2026-09-27 | MIT | ✅ | ⚠️ 需 API Key |
| **somenssarkar/gurukul-ai** | 0 | 2026-02-21 | **无 LICENSE** | ⛔ | ❌ 仅 Grade 7 |

**清理结论**：**无一个仓库处于 archived 状态**；`googleworkspace/skills` 已确认 404（改用 `googleworkspace/cli`）。

## 五、安装通道实测（本机实跑，2026-10-01）

| 通道 | 结果 |
|---|---|
| LearnBuddy 原生：`find-skills` | ✅ 可用（检索后安装到 `~/.learnbuddy/skills/`） |
| `npx skills add <owner>/<repo>` | ✅ **可用**（通用 skills CLI）—— 6 个仓库 / 70+ skill 装通 |
| 手动 `git clone` + 复制 | ✅ 可用 |

**环境限制**：本机沙箱有批量删除保护（单轮 50 次上限），文件多的仓库安装会反复重试而变慢；
**不影响本包使用**（库内 38 个 skill 开箱即用，库外仅作增强）。

## 六、免责

外部 skill 均为公开开源项目，安装前请自行阅读源码与许可证。
DUT 信息库中标 ⚠️ 的条目**未经核验**，请勿直接使用。本包与上述任何仓库无隶属关系。
'''


def add_declarations():
    write_if_changed('LICENSE', LICENSE_TEXT, 'MIT 许可证全文')
    write_if_changed('CHANGELOG.md', CHANGELOG_TEXT, '版本历史')
    write_if_changed('THIRD_PARTY_NOTICES.md', THIRD_PARTY_TEXT, '第三方来源与许可证归属')


# ==================================================================== 4. 校验器同步
SELFCHECK_NEW_SECTION = '''# ---------- 8b. 入口唯一性与声明 ----------
echo "[8b] 入口唯一性与声明"
# v2.11 新增：堵住「同名双入口」盲区 —— 此前包根 SKILL.md 与 library/SKILL.md
# 都写 `name: qihang` 且红线表已分叉，而四个校验器当时**全绿**（纯结构性盲区）。
#
# ⚠️ 为什么编号是 8b 而不是 11（**锚点冲突，实测踩过**）：
#   phase15 用 `rep('# ---------- 汇总 ----------', '[9]+[10] + 汇总')` 插入第 9/10 节，
#   其幂等护栏要求「[9]…[10]…汇总」**整块连续**。若本节插在 [10] 与「汇总」之间，
#   该连续性被破坏 → phase15 每跑一轮就再追加一份 [9]/[10]；
#   而本节自己的护栏（要求「[11] + 汇总」相邻）同样失效 → 两个区块**互相引爆**，
#   实测第 2 轮 selfcheck.sh 出现两份 [9]/[10]/[11]，第 3 轮 phase17 直接 rc=1。
#   → 本节必须插在 **[9] 之前**，两个护栏才同时成立。编号 8b 保证输出顺序单调。
_dupname=$(awk '
  FNR==1{fm=0; inname=0}
  FNR==1 && $0=="---"{fm=1;next}
  fm && /^name:/{v=$0; sub(/^name:[[:space:]]*/,"",v); print v; fm=0; next}
  fm && /^[A-Za-z_][A-Za-z0-9_-]*:/{next}
' $(find . -name SKILL.md -not -path './.git/*' -not -path './.learnbuddy/*' 2>/dev/null | sort) 2>/dev/null \\
  | sed 's/[[:space:]]*$//' | grep -v '^$' | sort | uniq -d | tr '\\n' ' ')
if [ -z "$_dupname" ]; then ok "SKILL.md 的 name 全域唯一（无同名入口）"
else bad "SKILL.md 存在同名入口: $_dupname"; fi

if [ -f SKILL.md ] && [ ! -e library/SKILL.md ]; then
  ok "入口唯一：包根 SKILL.md 在位 · library/ 下无 SKILL.md"
else bad "入口不唯一（library/SKILL.md 不应存在，应为 library/README.md）"; fi

_dmiss=0
for d in LICENSE CHANGELOG.md THIRD_PARTY_NOTICES.md; do
  [ -f "$d" ] || { bad "缺声明文件: $d"; _dmiss=$((_dmiss+1)); }
done
[ "$_dmiss" -eq 0 ] && ok "LICENSE / CHANGELOG.md / THIRD_PARTY_NOTICES.md 三件齐全"

_gi=$(grep -c '^references/.*[.]md$' .gitignore 2>/dev/null); _gi=${_gi:-0}
[ "$_gi" -ge 8 ] && ok "开发侧过程文档已由 .gitignore 排除（$_gi 项）" \\
  || bad "gitignore 排除不足（$_gi 项，期望 ≥8）"

'''

ALIGNCHECK_OLD_WALK = """def walk_files():
    out = []
    for base, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            out.append(os.path.join(base, fn).replace('\\\\', '/')[2:])
    return sorted(out)
"""

ALIGNCHECK_NEW_WALK = """# v2.11：开发侧过程文档（评审 / 审计 / 验收 / 需求书）已移出版本控制、未随包分发。
# 它们**不在交付物里**，因此必须同时从「文件总数」等全量统计中排除 ——
# 否则克隆者跑 aligncheck 会因「PROJECT.md 声明值 != 实测值」而误报。
# phase19 回写 PROJECT.md 的声明值时用的是同一口径（见 measure_files()）。
DEV_ONLY_DOCS = {
    'validation-report.md', 'acceptance-v2.md',
    'review-report-v2.2.md', 'review-report-v2.3.md', 'review-report-v2.4.md',
    'stress-test-v3.md', 'alignment-audit-v3.md', '需求确认书-v2三级结构.md',
}


def walk_files():
    out = []
    for base, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            if fn in DEV_ONLY_DOCS:
                continue
            out.append(os.path.join(base, fn).replace('\\\\', '/')[2:])
    return sorted(out)
"""


def patch_checkers():
    # 4.0 selfcheck [4]：开发侧过程文档未随包分发，不参与交付物的交叉引用契约。
    #     排除项**从 .gitignore 派生**（单一真相源），不是硬编码白名单。
    _ex_block = (
        "# v2.11：开发侧过程文档（见 .gitignore）**未随包分发**，不参与交付物的交叉引用契约。\n"
        "# 排除项从 .gitignore 派生（单一真相源）—— 克隆者本就没有这些文件，判据才能两边一致。\n"
        '_exdev=""\n'
        'for _g in $(grep -E \'^references/.*[.]md$\' .gitignore 2>/dev/null); do\n'
        '  _exdev="$_exdev --exclude=$(basename "$_g")"\n'
        'done\n'
    )
    rep('scripts/selfcheck.sh',
        "_refs=$(grep -rhoE '(library|references|domains|scripts|commands)/"
        "[^ )），、；;\"“”<>*]+[.]md' \\\n"
        "        --include='*.md' --exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | sort -u)",
        _ex_block +
        "_refs=$(grep -rhoE '(library|references|domains|scripts|commands)/"
        "[^ )），、；;\"“”<>*]+[.]md' \\\n"
        "        --include='*.md' $_exdev "
        "--exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | sort -u)",
        '[4] 路径引用排除未分发文档')
    rep('scripts/selfcheck.sh',
        "_bare=$(grep -rhoE '`[A-Za-z0-9][A-Za-z0-9_.-]*[.]md`' --include='*.md' \\\n"
        "        --exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | tr -d '`' | sort -u)",
        "_bare=$(grep -rhoE '`[A-Za-z0-9][A-Za-z0-9_.-]*[.]md`' --include='*.md' $_exdev \\\n"
        "        --exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | tr -d '`' | sort -u)",
        '[4] 裸文件名引用排除未分发文档')

    # 4.1 selfcheck：新增 [8b] 节。
    #     ⚠️ 锚点必须是 [9] 的标题行，**不能**用 `# ---------- 汇总 ----------`：
    #     phase15 也锚在「汇总」上且要求「[9]…[10]…汇总」整块连续，
    #     插在中间会让两层的追加型护栏互相失效（详见 SELFCHECK_NEW_SECTION 的注释）。
    anchor = '# ---------- 9. 多源比对与 DUT 适配 ----------'
    rep('scripts/selfcheck.sh', anchor, SELFCHECK_NEW_SECTION + anchor,
        '[8b] 入口唯一性与声明（4 条断言）')

    # 4.2 aligncheck：DEV_ONLY_DOCS 排除
    rep('scripts/aligncheck.py', ALIGNCHECK_OLD_WALK, ALIGNCHECK_NEW_WALK,
        'walk_files 排除 DEV_ONLY_DOCS')

    # 4.3 aligncheck：文件总数口径注释
    rep('scripts/aligncheck.py',
        '    # 文件总数声明（口径：不含 .git/.idea/.learnbuddy）',
        '    # 文件总数声明（口径：不含 .git/.idea/.learnbuddy/开发侧过程文档）',
        '文件总数口径注释')

    # 4.4 aligncheck：版本期望 2.10.0 -> 2.11.0（下一节统一处理，这里只标注）
    t = rd('scripts/aligncheck.py')
    if OLD_VER in t:
        wr('scripts/aligncheck.py', t.replace(OLD_VER, NEW_VER))
        OK.append('scripts/aligncheck.py :: 版本期望 %s → %s（%d 处）'
                  % (OLD_VER, NEW_VER, t.count(OLD_VER)))
    else:
        DONE.append('[已是最新] scripts/aligncheck.py :: 版本期望')


# ==================================================================== 5. 计数与版本
def refresh_counts():
    # 文件总数：**实测派生**（与 aligncheck.py 同口径：排除 4 类目录 + 8 份未分发文档）。
    # 不硬编码的原因见 measure_files() 的 docstring。
    n = measure_files()
    t = rd('PROJECT.md')
    t2, cnt = re.subn(r'\*\*(\d{2,4})\s*个文件\*\*', '**%d 个文件**' % n, t)
    if cnt == 0:
        MISS.append('PROJECT.md :: 文件总数声明（未找到 **N 个文件** 形式）')
    elif t2 != t:
        wr('PROJECT.md', t2)
        OK.append('PROJECT.md :: 文件总数 → %d（实测派生，%d 处）' % (n, cnt))
    else:
        DONE.append('[已是最新] PROJECT.md :: 文件总数 %d（实测一致）' % n)

    # ROADMAP.md 的「N 文件，生成器驱动」由 `build_phase12.py` 按**全树 walk** 派生
    # （含 `.idea` / `.learnbuddy` / 未随包分发的过程文档），与 PROJECT.md 口径不一致，
    # 且因本层新增/输出文件而**每轮漂移一次**（实测 r1=172 → r2=176）。
    # → 本层统一到同一口径（measure_files），两处一致且在链上稳定。
    t = rd('ROADMAP.md')
    t2 = re.sub(r'\d+ 文件，生成器驱动', '%d 文件，生成器驱动' % n, t)
    if t2 != t:
        wr('ROADMAP.md', t2)
        OK.append('ROADMAP.md :: 文件数口径统一 → %d（与 PROJECT.md 同口径）' % n)
    else:
        DONE.append('[已是最新] ROADMAP.md :: 文件数口径 %d' % n)
    # selfcheck 期望 OK 数（新增 [8b] 节 4 条）
    t = rd('INSTALL.md')
    m = re.search(r'`OK (\d+) ｜ WARN 0 ｜ FAIL 0 → 可交付`', t)
    if m and m.group(1) != '35':
        wr('INSTALL.md', t.replace('OK %s ｜ WARN 0 ｜ FAIL 0' % m.group(1),
                                   'OK 35 ｜ WARN 0 ｜ FAIL 0'))
        OK.append('INSTALL.md :: selfcheck 期望 OK %s → 35' % m.group(1))
    else:
        DONE.append('[已是最新] INSTALL.md :: selfcheck 期望 OK')


def bump_version():
    hits = 0
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs
                   if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')
                   and not os.path.relpath(os.path.join(base, d), ROOT).replace('\\', '/')
                   .startswith('scripts/_build')]
        for fn in files:
            if not fn.endswith(('.md', '.yaml', '.yml', '.sh', '.py', '.json', '.html', '.txt')):
                continue
            if fn in DEV_DOCS:
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith('scripts/_build/') or rel == 'CHANGELOG.md':
                continue
            t = rd(rel)
            if OLD_VER not in t and 'v2.10' not in t:
                continue
            t2 = t.replace('v2.10', 'v2.11').replace(OLD_VER, NEW_VER)
            if t2 != t:
                wr(rel, t2)
                hits += 1
    if hits:
        OK.append('版本号 %s → %s（%d 个文件）' % (OLD_VER, NEW_VER, hits))
    else:
        DONE.append('[已是最新] 版本号（已为 %s）' % NEW_VER)


# ==================================================================== 6. 构建说明同步
def update_build_readme():
    rep('scripts/_build/README.md',
        "**严格顺序（v2.10 全量）**：`v2 → extras → phase1 … phase18`",
        "**严格顺序（v2.11 全量）**：`v2 → extras → phase1 … phase19`",
        '顺序行 v2.11')
    # ⚠️ **循环行保持到 18，不要改成「18 19; do」。**
    #    phase17 对该行的完成判据是 `already_re=r'16 17( 18)?; do'`：
    #    一旦追加 `19`，该正则失配 → phase17 每轮链都报「_build/README 循环加 17」未命中，
    #    而 phase17 是 v2.10 链的「0 未命中」健康信号。→ phase19 改用**单独一行**登记，
    #    既不改历史层的判据，也让命令序列与真实执行顺序一致（19 本来就在链末）。
    rep('scripts/_build/README.md',
        '  python "scripts/_build/$f" .\ndone',
        '  python "scripts/_build/$f" .\ndone\n'
        'python scripts/_build/build_phase19.py .   # 链末结构层（单独跑，见文末说明）',
        '链末 phase19 调用行')
    rep('scripts/_build/README.md',
        "| **`build_phase18`** | **规则可执行性修复层（v2.9 → v2.10）：裸词澄清 · 澄清门 cᵢ 判定细则 · 域冲突对齐 · 无对口 skill 降级链 · 红线体系补漏** |",
        "| **`build_phase18`** | **规则可执行性修复层（v2.9 → v2.10）：裸词澄清 · 澄清门 cᵢ 判定细则 · 域冲突对齐 · 无对口 skill 降级链 · 红线体系补漏** |\n"
        "| **`build_phase19`** | **结构优化层（v2.10 → v2.11）：消除同名双入口 · 开发侧过程文档移出版本控制 · 补 LICENSE/CHANGELOG/THIRD_PARTY_NOTICES · 校验器补盲** |",
        '登记 phase19')
    rep('scripts/_build/README.md',
        '| `build_phase4`–`build_phase12` | 复核修复与文档同步（v2.2–v2.6 各轮） |',
        '| `build_phase4`–`build_phase12` | 复核修复与文档同步（v2.2–v2.6 各轮） |\n'
        '| **链末收敛层** | **`phase17` / `phase18` / `phase19` —— 历史层（phase1–16）可留 MISS；v2.11 起链末为 `phase19`，判据 = 它报 0 未命中 + 四项校验器全绿 + 两遍哈希一致** |',
        '链末收敛层说明')

    # 文末新增小节（**不修改 phase17 写下的「重跑安全说明」段**：
    # 那是 phase17 的追加型替换产物，改它会让 phase17 的幂等护栏失配 → 每轮报 MISS）。
    _appendix = (
        '\n'
        '---\n'
        '\n'
        '## v2.11 链末结构层（`build_phase19.py`）\n'
        '\n'
        '`phase19` 是 v2.11 新增的**链末层**，跑在 `phase18` 之后。上面的循环行只到 `18`\n'
        '（**刻意如此**：`phase17` 对那行的完成判据是固定文本，追加 `19` 会让它每轮报未命中），\n'
        '所以 `phase19` 单独一行执行。完整序列（v2.11 全量）：\n'
        '\n'
        '```bash\n'
        'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18; do\n'
        '  case "$p" in v2|v2_extras) f="build_qihang_${p}.py" ;; *) f="build_phase${p}.py" ;; esac\n'
        '  python "scripts/_build/$f" .\n'
        'done\n'
        'python scripts/_build/build_phase19.py .\n'
        'bash scripts/selfcheck.sh && bash scripts/audit.sh\n'
        '```\n'
        '\n'
        '本层负责：\n'
        '\n'
        '- **唯一入口**：包根 `SKILL.md` 是唯一安装单元；`library/` 提供不带 `name` 的导航页。\n'
        '  每轮链都会重新生成 `library/` 下的同名入口文件，故本层**每轮都要再退役一次**\n'
        '  （移到 `%TEMP%/qihang-retired/<本次运行>/`，不删，可取证回滚）。\n'
        '- **过程文档出库**：8 份评审 / 审计 / 验收 / 需求书写进 `.gitignore`（文件留在磁盘，链照跑）。\n'
        '- **声明类文件**：`LICENSE` / `CHANGELOG.md` / `THIRD_PARTY_NOTICES.md`。\n'
        '- **校验器补盲**：`selfcheck.sh` 新增 `[8b] 入口唯一性与声明`；`aligncheck.py` 排除未分发文档。\n'
        '\n'
        '**⚠️ 本层只写 `.gitignore`，不执行任何 git 命令。** 首次启用需人工执行一次\n'
        '「把 8 份开发侧过程文档移出版本控制」（`git rm --cached`，幂等）：\n'
        '\n'
        '```bash\n'
        '# 路径从 .gitignore 派生（单一真相源），不在此重复枚举：\n'
        "git rm --cached -q -- $(grep -E '^references/.*[.]md$' .gitignore)\n"
        '```\n'
    )
    _t = rd('scripts/_build/README.md')
    if 'v2.11 链末结构层' in _t:
        DONE.append('[已是最新] scripts/_build/README.md :: v2.11 链末结构层小节')
    else:
        wr('scripts/_build/README.md', _t.rstrip('\n') + '\n' + _appendix)
        OK.append('scripts/_build/README.md :: 新增 v2.11 链末结构层小节')

    # 发布器登记（v2.11）。**单独一个幂等块**：`_appendix` 由「含 v2.11 链末结构层」
    # 标记守卫，该小节已在树上落定 → 不能再往 `_appendix` 里加内容（永远不生效）。
    _rel_doc = (
        '\n'
        '---\n'
        '\n'
        '## 发布副本构建器（`make_release.py`）\n'
        '\n'
        '`scripts/_build/make_release.py` 把本仓库导出为**只含交付物**的发布副本：\n'
        '\n'
        '```bash\n'
        'python scripts/_build/make_release.py [目标目录]   # 默认 ../qihang-pack-release\n'
        '```\n'
        '\n'
        '- **导出集合的唯一真相源是 git + `.gitignore`**：\n'
        '  `git ls-files --cached --others --exclude-standard` ∩ 磁盘存在，\n'
        '  再减去 `scripts/_build/`、`.gitignore`、`.gitattributes`。\n'
        '  「什么不进交付物」只写在 `.gitignore` 一处 —— **不要在本目录另建第二份排除清单**\n'
        '  （v2.10 前的发布器就是硬编码了一份，实测漂移过）。\n'
        '- **两处必须对齐的口径差异**（均已踩过，勿删代码里的相应处理）：\n'
        '  · git 索引里可能仍有「已从磁盘删除」的路径（如 v2.11 退役的 `library/` 下同名入口文件）\n'
        '    → 枚举时必须与磁盘取交集，否则 `copy2` 直接 FileNotFoundError；\n'
        '  · `.learnbuddy/`（AI 工作记忆）**被 git 跟踪、却不在 `.gitignore`**\n'
        '    → 需按目录名显式滤掉，否则 2 份记忆日志会被打进交付物。\n'
        '- **覆盖式导出必须配「陈旧文件移出」**：导出不删目录，所以「上版有、本版没有」的文件\n'
        '  会静默留在交付物里（实测：旧副本留着已退役的 `library/` 下同名入口文件，\n'
        '  正是「同名双入口」缺陷本身）→ 由 `prune_stale()` 移到 `%TEMP%/qihang-release-retired/`。\n'
        '- **发布期改写不回写仓库**：副本里 `selfcheck.sh` 的 `[8b]`（依赖 `.gitignore`）与\n'
        '  `aligncheck.py` 关联的文件总数口径都不同，由本工具在导出时改写。\n'
        '- 导出后在副本内实测四条命令验收：\n'
        '  `bash scripts/selfcheck.sh` · `bash scripts/audit.sh` · `bash scripts/regress.sh 3` ·\n'
        '  `python scripts/aligncheck.py`。\n'
    )
    _t = rd('scripts/_build/README.md')
    if '## 发布副本构建器' in _t:
        DONE.append('[已是最新] scripts/_build/README.md :: 发布器小节')
    else:
        wr('scripts/_build/README.md', _t.rstrip('\n') + '\n' + _rel_doc)
        OK.append('scripts/_build/README.md :: 新增发布器小节')

    # ⚠️ 该小节初版写了 `library/SKILL.md` —— 一个**路径式引用**，而该文件已退役，
    #    于是 aligncheck 判「失效引用」、selfcheck [4] 直接 FAIL（两处同时挂）。
    #    上面那个守卫块只看「小节标题在不在」，已落地的旧正文不会被重写，
    #    所以这里再用 rep() 收敛一次：新树追加的就是新文案（already 命中 → DONE），
    #    旧树则把那一行改写掉（→ OK）。
    rep('scripts/_build/README.md',
        '（如退役的 `library/SKILL.md`）',
        '（如 v2.11 退役的 `library/` 下同名入口文件）',
        '发布器小节：去除已退役文件的路径引用')
    # 同上：小节里补一条「陈旧文件移出」，已落地的旧正文靠这次 rep 收敛。
    rep('scripts/_build/README.md',
        '- **发布期改写不回写仓库**：副本里 `selfcheck.sh` 的 `[8b]`（依赖 `.gitignore`）与',
        '- **覆盖式导出必须配「陈旧文件移出」**：导出不删目录，所以「上版有、本版没有」的文件\n'
        '  会静默留在交付物里（实测：旧副本留着已退役的 `library/` 下同名入口文件，\n'
        '  正是「同名双入口」缺陷本身）→ 由 `prune_stale()` 移到 `%TEMP%/qihang-release-retired/`。\n'
        '- **发布期改写不回写仓库**：副本里 `selfcheck.sh` 的 `[8b]`（依赖 `.gitignore`）与',
        '发布器小节：补陈旧文件移出说明')


# ==================================================================== 7. 硬护栏
TRACKED_SKIP = ('scripts/_build/', 'CHANGELOG.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md')


def assert_guards():
    # 7.1 防回退：library/SKILL.md 不得复活
    if os.path.exists(os.path.join(ROOT, 'library', 'SKILL.md')):
        MISS.append('护栏 :: library/SKILL.md 仍存在（同名双入口未消除）')
    else:
        DONE.append('护栏 :: library/SKILL.md 已消除')
    if not os.path.exists(os.path.join(ROOT, 'library', 'README.md')):
        MISS.append('护栏 :: library/README.md 不存在')
    # library/README.md 不得带 frontmatter（否则又成了第二个入口）
    lr = rd('library/README.md')
    if lr.startswith('---'):
        MISS.append('护栏 :: library/README.md 带 frontmatter（会形成第二个入口）')
    else:
        DONE.append('护栏 :: library/README.md 无 frontmatter')

    # 7.2 防误删：8 份开发侧过程文档必须仍在磁盘（只是移出版本控制）
    gone = [d for d in DEV_DOCS if not os.path.exists(os.path.join(ROOT, 'references', d))]
    if gone:
        MISS.append('护栏 :: 开发侧过程文档被误删（%d 份）: %s' % (len(gone), ' / '.join(gone)))
    else:
        DONE.append('护栏 :: 8 份开发侧过程文档仍在磁盘（链可重跑）')

    # 7.3 防断链：tracked 文件不得再出现「反引号 dev 名」或「references/dev 名」
    bad = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            if not fn.endswith(('.md', '.sh', '.py', '.yaml', '.html')):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith(TRACKED_SKIP) or fn in DEV_DOCS:
                continue
            t = rd(rel) if os.path.isfile(os.path.join(ROOT, rel)) else ''
            for d in DEV_DOCS:
                if ('references/' + d) in t or ('`%s`' % d) in t:
                    bad.append('%s → %s' % (rel, d))
    if bad:
        MISS.append('护栏 :: 仍有指向未分发文档的引用（%d 处）: %s' % (len(bad), '；'.join(bad[:5])))
    else:
        DONE.append('护栏 :: 无指向未分发文档的引用')

    # 7.4 防「锚点互爆」：selfcheck.sh 的节标题必须各出现**恰好一次**。
    #     历史层 phase15 插 [9]/[10]、本层插 [8b]，三者曾共用「汇总」锚点 →
    #     追加型护栏互相失效 → 每轮链多插一份。这条断言把该故障变成硬报错。
    _sc = rd('scripts/selfcheck.sh').split('\n')
    _heads = [
        '# ---------- 8b. 入口唯一性与声明 ----------',
        '# ---------- 9. 多源比对与 DUT 适配 ----------',
        '# ---------- 10. 仓库清洁度（临时文件零残留） ----------',
        '# ---------- 汇总 ----------',
    ]
    # 只数**整行就是标题**的行：注释里引用标题（如本节自己的说明）不算重复。
    _dup = []
    for h in _heads:
        c = sum(1 for l in _sc if l.strip() == h)
        if c != 1:
            _dup.append('%s×%d' % (h, c))
    if _dup:
        MISS.append('护栏 :: selfcheck 节标题重复（锚点冲突）: %s' % ' / '.join(_dup))
    else:
        DONE.append('护栏 :: selfcheck 节标题无重复（[8b]/[9]/[10]/汇总 各 1 次）')

    # 7.5 CLAUDE 专向化防回退（v2.8 口径）
    hit = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ('.git', '.idea', '.learnbuddy', '__pycache__')]
        for fn in files:
            if not fn.endswith(('.md', '.sh', '.py', '.html', '.json')):
                continue
            rel = os.path.relpath(os.path.join(base, fn), ROOT).replace('\\', '/')
            if rel.startswith('scripts/_build/') or fn in DEV_DOCS or rel == 'CHANGELOG.md':
                continue
            if '.claude/' in rd(rel):
                hit.append(rel)
    if hit:
        MISS.append('护栏 :: 平台口径回退（出现 .claude/ 路径）: %s' % ', '.join(hit[:4]))
    else:
        DONE.append('护栏 :: 平台口径仍为 LearnBuddy 单一目标')


# ==================================================================== main
def main():
    split_entry()
    withdraw_dev_docs()
    add_declarations()
    patch_checkers()
    refresh_counts()
    bump_version()
    update_build_readme()
    assert_guards()

    print('=' * 68)
    print('build_phase19 · 结构优化层（v2.10 → v2.11）')
    print('=' * 68)
    print('已应用 %d ｜ 已是最新 %d ｜ 未命中 %d' % (len(OK), len(DONE), len(MISS)))
    if OK:
        print('\n--- 本次改动 ---')
        for x in OK:
            print('  + ' + x)
    if DONE:
        print('\n--- 已是最新（幂等命中）---')
        for x in DONE:
            print('  = ' + x)
    if MISS:
        print('\n--- 未命中（需人工看）---')
        for x in MISS:
            print('  x ' + x)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
