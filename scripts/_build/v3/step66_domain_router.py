# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 29 层 · 域锁定的「两级匹配」接线（v3.3.4 → v3.3.5）】
#
# 触发（用户要求「自检查，模拟一些问题，看是否踩中，skill 调用情况与结果输出情况」）：
#   新增规则干跑器 `scripts/_build/v3/tests/e2e_sim.py`，用包内表当尺子逐题走链路 →
#   立刻暴露 **域锁定漏命中**：
#     ·「大工图书馆几点开门？」「大工教务系统怎么进？」→ **0 域命中**，掉进 §3 无域兜底；
#     ·「帮我降重…」→ 0 命中（R5 触发词只有「查重」，没有「降重」）；
#     ·「我不想活了」→ 0 命中（F3 触发词无危机词）。
#
# 根因（**不是词不够，而是接线没接上**）：
#   `library/domain-review.md` §1① 只让人去 `domains/_registry.md` 的「触发词」列匹配，
#   而那一列每域只有 **5–6 个示意词（带 `…`）**；真正的**权威词表**在各域
#   `_domain.md` 的 `## 触发词（命中任一即锁定本域）` 段（每域 **8–13 个词**，更细更贴）。
#   实测：「教务」本就在 F1 的域文件里、「课表/成绩」本就在 R6 的域文件里 —— **却因为只查快筛层而判「无域」**。
#
# 本层修法：
#   ① `domain-review.md` §1① 改为**两级匹配**（`_registry.md` 快筛 → 逐域 `_domain.md` 细筛，未中才进兜底）；
#   ② `_registry.md` 触发词列加头注，标明「本列是示意词，权威词表在各域 `_domain.md`」；
#   ③ 补最少的必要词：F1 +图书馆/教务系统/课表/成绩查询；R6 +课表/成绩；R5 +降重；
#      F3 +危机词（不想活/轻生/自杀，**红线词**，保危机路径可达）；F6 补到 8 词；
#   ④ `selfcheck [8e]`：每域细筛词表 ≥8 词、两级匹配已声明、8 个高频校情词可达、F3 含危机词。
#
# 用法：python scripts/_build/v3/step66_domain_router.py [仓库根]
# -------------------------------------------------------------------------------
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.4', '3.3.5'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='\n').write(t)


def edit(rel, pairs):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel)
        return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r' % (rel, sent[:44]))
            continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:44]))
            continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:44]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


# =============================================================== A) 两级匹配接线
print('== A) domain-review §1① 改为两级匹配（核心修复）==')
edit('library/domain-review.md', [
    ('① 取 T(任务) + O(对象) 作为主键，去 domains/_registry.md 匹配触发词',
     '① 取 T(任务) + O(对象) 作为主键，做**两级匹配**（**v3.3.5 修正**）：\n'
     '   a) **快筛**：`domains/_registry.md` 的「触发词」列 —— 每域只有 **5–6 个示意词**，用于快速定向；\n'
     '   b) **细筛（快筛未中必做，权威层）**：逐个读 `domains/<域>/_domain.md` 的\n'
     '      `## 触发词（命中任一即锁定本域）` 段（每域 **8–13 个词**）与 `## 域边界` 的「覆盖」行。\n'
     '   > ⚠️ **只查 `_registry.md` 就判「无域」是错的** —— 它只是示意层。实测「教务」就在 `F1` 的域文件里、\n'
     '   > 「课表 / 成绩」就在 `R6` 的域文件里，却因只查快筛层而掉进无域兜底。**细筛层才是权威。**',
     '**两级匹配**（**v3.3.5 修正**）'),
])

# =============================================================== B) registry 头注
print('== B) _registry.md 触发词列加头注 ==')
edit('domains/_registry.md', [
    ('| 域 ID | 名称 | 触发词 | 库内 skill |',
     '| 域 ID | 名称 | 触发词（**示意层**） | 库内 skill |',
     '触发词（**示意层**）'),
])
edit('domains/_registry.md', [
    ('2. 用下表**触发词**匹配锁定域；命中多个 → 走跨域串联',
     '2. 用下表**触发词**匹配锁定域；命中多个 → 走跨域串联\n'
     '   > ⚠️ **本列只是「示意层」**（每域 5–6 个词，带 `…`）。**权威词表在各域 `_domain.md` 的\n'
     '   > `## 触发词（命中任一即锁定本域）` 段**（每域 8–13 个词）—— **快筛未中必须细筛**，\n'
     '   > 见 `library/domain-review.md` §1①。只查本表就判「无域」会漏锁（实测过）。',
     '本列只是「示意层」'),
])

# =============================================================== C) 补必要词
print('== C) 补高频缺失词（最小集）==')
WORD_PATCH = {
    'F1-campus-affairs': ('`选课` ｜ `学籍` ｜ `证明` ｜ `一卡通` ｜ `报修` ｜ `宿舍` ｜ `离校` ｜ `校园卡` ｜ `办事` ｜ `网费` ｜ `学费` ｜ `缴费入口` ｜ `报名时间`',
                          '`选课` ｜ `学籍` ｜ `证明` ｜ `一卡通` ｜ `报修` ｜ `宿舍` ｜ `离校` ｜ `校园卡` ｜ `办事` ｜ `网费` ｜ `学费` ｜ `缴费入口` ｜ `报名时间` ｜ `图书馆` ｜ `教务系统` ｜ `课表` ｜ `成绩查询`'),
    'R6-info-retrieval': ('`导师信息` ｜ `老师是谁` ｜ `教师主页` ｜ `联系方式` ｜ `部门电话` ｜ `通知` ｜ `公告` ｜ `信息公开` ｜ `官网是什么` ｜ `查电话`',
                          '`导师信息` ｜ `老师是谁` ｜ `教师主页` ｜ `联系方式` ｜ `部门电话` ｜ `通知` ｜ `公告` ｜ `信息公开` ｜ `官网是什么` ｜ `查电话` ｜ `课表` ｜ `成绩` ｜ `培养方案`'),
    'R5-integrity': ('`查重` ｜ `引用规范` ｜ `学术诚信` ｜ `AI 声明` ｜ `数据合规` ｜ `署名` ｜ `伦理` ｜ `AI 使用`',
                     '`查重` ｜ `降重` ｜ `引用规范` ｜ `学术诚信` ｜ `AI 声明` ｜ `数据合规` ｜ `署名` ｜ `伦理` ｜ `AI 使用`'),
    'F3-wellbeing': ('`焦虑` ｜ `压力` ｜ `emo` ｜ `室友` ｜ `社团` ｜ `人际` ｜ `想家` ｜ `孤独` ｜ `适应`',
                     '`焦虑` ｜ `压力` ｜ `emo` ｜ `室友` ｜ `社团` ｜ `人际` ｜ `想家` ｜ `孤独` ｜ `适应` ｜ `不想活` ｜ `轻生` ｜ `自杀`'),
    # F6 原本只有 7 词（低于 [8e] 的 ≥8 下限）→ 补 1 个真实常用说法
    'F6-service': ('`军训` ｜ `国防` ｜ `志愿` ｜ `社会实践` ｜ `志愿时长` ｜ `第二课堂` ｜ `三下乡`',
                   '`军训` ｜ `国防` ｜ `志愿` ｜ `社会实践` ｜ `志愿时长` ｜ `第二课堂` ｜ `三下乡` ｜ `志愿者`'),
}
# 哨兵必须只在打完补丁后才存在。首版用「词表最后一项」当哨兵 → R5 的 AI 使用 / F3 的自杀
# 在文件正文里本来就有 → 误判「已应用」而静默跳过（实测踩到）。改为显式哨兵。
SENT = {
    'F1-campus-affairs': '`图书馆` ｜ `教务系统`',
    'R6-info-retrieval': '`课表` ｜ `成绩` ｜ `培养方案`',
    'R5-integrity': '`查重` ｜ `降重`',
    'F3-wellbeing': '`适应` ｜ `不想活` ｜ `轻生` ｜ `自杀`',
    'F6-service': '`三下乡` ｜ `志愿者`',
}
for d, (a, b) in WORD_PATCH.items():
    edit('domains/%s/_domain.md' % d, [(a, b, SENT[d])])

# registry 快筛层同步（让常见词在快筛就能定向）
edit('domains/_registry.md', [
    ('| `F1` | 校园事务 | 选课、学籍、证明、一卡通、报修… |',
     '| `F1` | 校园事务 | 选课、学籍、证明、一卡通、报修、图书馆、教务系统… |',
     '图书馆、教务系统'),
    ('| `F3` | 身心与社交 | 焦虑、压力、emo、室友、社团… |',
     '| `F3` | 身心与社交 | 焦虑、压力、emo、室友、社团、不想活… |',
     '不想活'),
    ('| `R5` | 学术规范与伦理 | 查重、引用规范、学术诚信、AI 声明、数据合规… |',
     '| `R5` | 学术规范与伦理 | 查重、降重、引用规范、学术诚信、AI 声明、数据合规… |',
     '查重、降重'),
    ('| `R6` | 信息搜集与输出 | 导师信息、教师主页、联系方式、通知、公告、信息公开… |',
     '| `R6` | 信息搜集与输出 | 导师信息、教师主页、联系方式、课表、成绩、通知、公告… |',
     '课表、成绩'),
])

# =============================================================== D) selfcheck [8e]
print('== D) selfcheck.sh 新增 [8e] 域锁定两级匹配与覆盖度 ==')
S8E = '''# ---------- 8e. 域锁定：两级匹配接线 + 触发词覆盖度（v3.3.5） ----------
# 事故驱动：规则干跑实测「图书馆 / 教务 / 课表 / 成绩 / 降重 / 不想活」全部 **0 域命中**，
#   因为它们只出现在各域 `_domain.md` 的**细筛词表**里，而路由当时**只查 `_registry.md` 的示意层**。
#   本段把「细筛层必须接线」和「高频校情词必须可达」都钉成断言。
echo "[8e] 域锁定两级匹配与覆盖度"
if grep -q '两级匹配' library/domain-review.md 2>/dev/null; then
  ok "domain-review 已声明「两级匹配」"
else bad "domain-review 未声明两级匹配（只查 _registry 会漏锁）"; fi
if grep -q '_domain.md' library/domain-review.md 2>/dev/null; then
  ok "domain-review 已指向 _domain.md 细筛层"
else bad "domain-review 未指向 _domain.md 细筛层"; fi
if grep -q '示意层' domains/_registry.md 2>/dev/null; then
  ok "_registry.md 已标明触发词列是示意层"
else bad "_registry.md 未标明示意层（易被当成权威表）"; fi
_alltrig=$(cat domains/*/_domain.md 2>/dev/null)
_thin=0
for _d in domains/*/; do
  _t=$(sed -n '/^## *触发词/,/^## /p' "$_d/_domain.md" 2>/dev/null | grep -o '`[^`]*`' | wc -l | tr -d ' ')
  if [ "${_t:-0}" -lt 8 ]; then _thin=$((_thin+1)); bad "$(basename "$_d") 细筛触发词仅 ${_t} 个（要求 ≥8）"; fi
done
[ "${_thin:-0}" -eq 0 ] && ok "20 域细筛触发词均 ≥8 个"
for _w in 图书馆 教务 课表 成绩 一卡通 宿舍 选课 报修; do
  if printf '%s' "$_alltrig" | grep -q "$_w"; then ok "高频校情词可达：$_w"
  else bad "高频校情词不可达：$_w（会掉进无域兜底）"; fi
done
if sed -n '/^## *触发词/,/^## /p' domains/F3-wellbeing/_domain.md 2>/dev/null | grep -qE '不想活|轻生|自杀'; then
  ok "F3 细筛含危机词（危机路径可达）"
else bad "F3 细筛缺危机词（危机信号可能落进无域兜底）"; fi

'''
t = read('scripts/selfcheck.sh')
if t is None:
    print('  [SKIP] 无 scripts/selfcheck.sh')
elif '[8e] 域锁定两级匹配' in t:
    print('  [SAME] [8e] 段已在位')
else:
    A = '# ---------- 9. 库内唯一通道（纯 DUT 特化库） ----------'
    if A in t:
        write('scripts/selfcheck.sh', t.replace(A, S8E + A, 1))
        print('  [OK]   已插入 [8e] 段')
    else:
        print('  [MISS] 未找到 [9] 锚点')

# =============================================================== E) 构建侧层序
edit('scripts/_build/v3/README.md', [
    ('| 24 | `step65_trigger_gate.py` |',
     '| 25 | `step66_domain_router.py` | **域锁定两级匹配接线**：`domain-review` §1① 改为「`_registry.md` 快筛 → 逐域 `_domain.md` 细筛」'
     '（实测漏锁：图书馆/教务/课表/成绩/降重/不想活 全部 0 命中）· `_registry.md` 标明示意层 · '
     '补 F1/R5/R6/F3 细筛词 · selfcheck `[8e]`（每域 ≥8 词 + 8 个高频校情词可达 + F3 含危机词）；修订号 → `3.3.5` | 新增层 |\n'
     '| 24 | `step65_trigger_gate.py` |',
     'step66_domain_router.py'),
])

# =============================================================== F) 版本
print('== F) 修订号 %s → %s ==' % (OLD_REV, NEW_REV))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        x = read(rel)
        if x and 'version: %s' % OLD_REV in x:
            write(rel, x.replace('version: %s' % OLD_REV, 'version: %s' % NEW_REV))
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD_REV, '"version": "%s"' % NEW_REV),
        ('config.yaml', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD_REV, '**修订号 = `%s`**' % NEW_REV),
        ('library/output-spec.md', '如 `3.3.0` → `%s`）' % OLD_REV, '如 `3.3.0` → `%s`）' % NEW_REV),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

print('done')
