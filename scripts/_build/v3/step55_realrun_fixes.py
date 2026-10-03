# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 18 层 · 真实问题 5×5 轮归因修复】
# 依据：5 个子代理 × 5 轮「真实问题 → 真实结果 → 结果检索 → 优化返回 → bug」共 25 轮
#       的一手回报。**每条都回原始文件核对过**，只修「包的错」。
# 用法：python scripts/_build/v3/step55_realrun_fixes.py [仓库根]
# 幂等：全部为「整行替换」，替换后旧串不再是新串的子串 → 重跑 MISS（无重复插入风险）。
#
# 本轮确认并修复（10 处）：
#  F1  `output-spec` §1【假设】块残留断句「其余（」+ 错位行（上轮修复留下的残片）
#  F2  `clarity` §3.1 例 A 标「复述档」但 `C = 0.689 < 0.70`，与档位区间字面冲突（未注明「澄清门已放行」）
#  F3  `tool-setup` 示例：「依例外 2 放行后**追问**」自相矛盾（例外 2 = 关键槽齐全 → 不追问）
#  F4  `submit-kit` 示例：「依例外 2 放行…后按红线拒绝」混用（红线优先，不该引例外 2）
#  F5  `campus-desk` 未收录话术写 `www.dlut.edu.cn`，缺 `https://`（与 SKILL.md 硬规则 2 的固定话术不一致）
#  F6  `grad-plan` 示例把**未核验**的「专业前 20%」写成「硬门槛」→ 违反 DUT 不编造铁律（最高优先）
#  F7  `S6` 域触发词缺「四级 / 六级 / 听力」（用户说「六级听力」时域内无触发词，直连会漏）
#  F8  `argument-slides` 把需登录的「大工金课平台」列在**公开**绑定点
#  F9  `R5` 域把「查重系统」列在「私密站（需登录，见 login-sites）」，但 login-sites 无该条
#  F10 `lab-report` IMRAD 字数分配合计 100% 但只列 4 节，而执行步骤含「结论」节（结论无份额）
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OLD, NEW, PKG = '3.2.3', '3.2.4', '3.2'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for a, b in pairs:
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:52])); continue
        t = t.replace(a, b, 1); print('  [OK]   %s :: %r' % (rel, a[:52]))
    if t != o:
        write(rel, t)


# ---- F1：output-spec §1【假设】块断句归一（去掉残留「其余（」并回正语序）
print('== F1) output-spec §1【假设】块 ==')
edit('library/output-spec.md', [
    ('【假设】  出现条件：① 3 轮未澄清仍推进，或 ② 依 `clarity.md` §5 例外 **3 / 5 / 6** 直接推进、\n'
     '          ⚠️ **`clarity.md` §3.1 需求确定门的「复述档」不计入本字段** —— 复述并入【结论】首行的前置短句；\n'
     '          本字段只表示「**代替用户补齐了对象或产出**」，两者不要混用。\n'
     '          其余（\n'
     '          且**代替用户补齐了对象或产出**时',
     '【假设】  出现条件：① 3 轮未澄清仍推进，或 ② 依 `clarity.md` §5 例外 **3 / 5 / 6** 直接推进、\n'
     '          且**代替用户补齐了对象或产出**时\n'
     '          ⚠️ **`clarity.md` §3.1 需求确定门的「复述档」不计入本字段** —— 复述并入【结论】首行的前置短句；\n'
     '          本字段只表示「**代替用户补齐了对象或产出**」，两者不要混用。'),
])

# ---- F2：clarity 例 A 档位注明
print('== F2) clarity §3.1 例 A 档位 ==')
edit('library/clarity.md', [
    ('| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689` | 放行（例外 2） | **复述档**（一句话复述并入【结论】首行） |',
     '| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689`（数�值 <0.70，**但澄清门已放行 → 按复述档处理**，见下方前置约定 ②） | 放行（例外 2） | **复述档**（一句话复述并入【结论】首行） |'),
])

# ---- F3 / F4：示例澄清判定自相矛盾
print('== F3/F4) tool-setup / submit-kit 示例澄清判定 ==')
edit('domains/R3-research-tools/skills/local/tool-setup/SKILL.md', [
    ('**澄清判定**：关键槽「环境 / 报错原文」缺失 → 依 `clarity.md` §5 例外 2 放行后**追问**',
     '**澄清判定**：关键槽「环境 / 报错原文」缺失 → **追问 1 问**（例外 2 不适用：例外 2 的前提是关键槽齐全；本例属关键槽缺）'),
])
edit('domains/R4-publication/skills/local/submit-kit/SKILL.md', [
    ('**澄清判定**：命中本域红线（代投稿）→ 依 `clarity.md` §5 例外 2 放行域锁定后按红线拒绝',
     '**澄清判定**：命中本域红线（代投稿）→ **红线优先**（`clarity.md` §5 例外 4；不适用例外 2），直接拒绝 + 给合规替代'),
])

# ---- F5：未收录固定话术补 https://
print('== F5) campus-desk 未收录话术 ==')
edit('domains/F1-campus-affairs/skills/local/campus-desk/SKILL.md', [
    ('5. 未收录则固定回复：信息库未收录，建议访问 www.dlut.edu.cn 核实',
     '5. 未收录则固定回复：信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实'),
])

# ---- F6：grad-plan 去掉未核验「硬门槛」
print('== F6) grad-plan 未核验事实 ==')
edit('domains/F7-further-study/skills/local/grad-plan/SKILL.md', [
    ('【结果】① 大一：把绩点打进专业前 20%（这是硬门槛）',
     '【结果】① 大一：把绩点打进专业前 20%（**以所在学院当年推免章程为准；本包未收录具体分数线 / 排名要求**）'),
])

# ---- F7：S6 触发词补 四级 / 六级 / 听力
print('== F7) S6 触发词 ==')
edit('domains/S6-language/_domain.md', [
    ('`英语` ｜ `四六级` ｜ `雅思` ｜ `托福` ｜ `口语` ｜ `翻译` ｜ `单词` ｜ `作文批改`',
     '`英语` ｜ `四六级` ｜ `四级` ｜ `六级` ｜ `听力` ｜ `雅思` ｜ `托福` ｜ `口语` ｜ `翻译` ｜ `单词` ｜ `作文批改`'),
])

# ---- F8：argument-slides 需登录平台标注
print('== F8) argument-slides 绑定点 ==')
edit('domains/S5-academic-writing/skills/local/argument-slides/SKILL.md', [
    ('- 数字书院 / 大工金课平台（课程展示要求） https://dlut.fanya.chaoxing.com/',
     '- 数字书院 / 大工金课平台（课程展示要求；**需登录，见 `references/dlut-login-sites.md`**） https://dlut.fanya.chaoxing.com/'),
])

# ---- F9：R5 私密站条目与 login-sites 对齐（改未收录口径）
print('== F9) R5 私密站条目 ==')
edit('domains/R5-integrity/_domain.md', [
    ('- 查重系统（图书馆/研究生院入口）',
     '- 查重系统（图书馆 / 研究生院入口；**本包未收录具体入口，以官方页面为准，勿代查重**）'),
])

# ---- F10：lab-report IMRAD 字数含结论
print('== F10) lab-report 字数分配 ==')
edit('domains/S3-assignment/skills/local/lab-report/SKILL.md', [
    ('**IMRAD 字数分配**：引言 15% · 方法 25% · 结果 35% · 讨论 25%。',
     '**IMRAD 字数分配**：引言 15% · 方法 25% · 结果 35% · **讨论与结论 25%**（结论节含在此份额内，合计 100%）。'),
])

# ---- 版本号 3.2.3 → 3.2.4
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
    ("if pv != '%s':" % OLD, "if pv != '%s':" % NEW),
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
