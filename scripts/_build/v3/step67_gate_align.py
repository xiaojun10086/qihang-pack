# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 30 层 · 触发门与域表同源（v3.3.5 → v3.3.6）】
#
# 触发（用户要求「按照相似问题继续自查，这次自查 12 轮以上」）：
#   新增多轮自查台 `scripts/_build/v3/tests/e2e_rounds.py`（15 轮 / 69 题）→
#   **39 题不达标**，且几乎全是同一个症状：**触发门判「不接管」，而域表明明能锁定**。
#   例：「这道题为什么用洛必达法则」「给我做个概念图」「还有三天就考了怎么突击」
#       「引用规范是什么样的」「军训要注意什么」「我总是拖延」→ 全被判「不接管」。
#
# 根因（**两套互不相干的词表**）：
#   实测 触发门词表（dlut_markers + learning_markers + learning_intents）**50 词**，
#   20 域触发词表（_registry 快筛 + _domain.md 细筛）**199 词**，**交集只有 16 个** ——
#   183 个域词没被门用上。即：**包说自己覆盖，门却说不管**。
#   这是 v3.3.4 引入触发门时埋下的：门另起了一套更窄的词表，而不是复用域表。
#
# 本层修法（**同源**）：
#   ① `trigger.learning_markers` 改为 **20 域触发词的并集**（构建期从 `_registry.md` 与各域
#      `_domain.md` 的 `## 触发词` 段**派生**，不再手维护）→「能锁定到域」即「放行」；
#   ② `trigger.dlut_markers` 补齐**本校事务**类词（宿舍/一卡通/报修/图书馆/教务系统/军训/志愿/…）；
#   ③ 新增 `trigger.out_of_scope_markers`（越界信号：电影/天气/机票/股票/游戏/购物/旅游…）——
#      命中即**不接管**，优先级最高，用它压住宽词表带来的误触发；
#   ④ 新增 `trigger.boundary_note`：写明**顺带提及不算**（例「帮我写个冒泡排序（面试用）」——
#      对象「冒泡排序」不属任何域，「面试」只是用途）→ 判不接管由**需求主键 T+O** 决定，不由单词命中决定；
#   ⑤ `SKILL.md` 触发门 T2 表述改为「学习或校园生活诉求（判据 = 能锁定到 20 域之一）」并加越界信号行；
#   ⑥ `selfcheck [8d]` 补断言：越界信号段在位、SKILL.md 提越界信号、门词表覆盖域表 ≥90%、
#      且若干「干跑中漏掉的代表词」必须在门里（防回归）。
#
# 用法：python scripts/_build/v3/step67_gate_align.py [仓库根]
# -------------------------------------------------------------------------------
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.5', '3.3.6'

# 越界信号：与 DUT、学习、校园生活**均无关**的通用事务（命中即不接管）
OUT_OF_SCOPE = ['电影', '电视剧', '综艺', '追星', '游戏', '天气', '机票', '火车票', '酒店', '外卖',
                '股票', '基金', '彩票', '购物', '旅游', '星座', '算命', '算命先生', '菜谱', '减肥药']

# 本校事务词（补进 dlut_markers）
CAMPUS = ['宿舍', '一卡通', '校园卡', '报修', '图书馆', '教务系统', '课表', '成绩查询', '培养方案',
          '转专业', '军训', '志愿', '志愿时长', '社会实践', '助学金', '奖学金', '校医院', '医保',
          '校历', '选课', '离校', '办证明', '学籍']


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='\n').write(t)


def collector_domain_words():
    """从 _registry.md（快筛）+ 各域 _domain.md（细筛）派生域触发词并集。"""
    words = []
    t = read('domains/_registry.md') or ''
    for m in re.finditer(r'^\|\s*`[SFR]\d`\s*\|\s*[^|]+\|\s*([^|]+?)\s*\|', t, re.M):
        for x in re.split(r'[、,，]', m.group(1)):
            words.append(x.strip(' …'))
    for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
        p = os.path.join(ROOT, 'domains', d, '_domain.md')
        if not os.path.isfile(p):
            continue
        x = io.open(p, encoding='utf-8').read()
        mm = re.search(r'^##\s*触发词[^\n]*\n(.*?)(?=\n##\s)', x, re.M | re.S)
        if mm:
            words += re.findall(r'`([^`]+)`', mm.group(1))
    # 去噪：域 ID / 文件名 / 空 / 单字符
    out, seen = [], set()
    for w in words:
        w = w.strip()
        if not w or len(w) < 2:
            continue
        if re.fullmatch(r'[SFR]\d', w):
            continue
        if any(c in w for c in ('_', '.', '/', '\\')):
            continue
        if w in seen:
            continue
        seen.add(w)
        out.append(w)
    return out


def yaml_list(items, indent='  '):
    return indent + '[' + ', '.join(items) + ']'


print('== A0) 域表补词（15 轮干跑查出的真实缺口）==')
# 干跑残留 6 项不达标，全部是**域表本身缺词**（不是接线问题）：
#   「这个概念和那个概念有什么区别」「老师讲的我没听懂，能再讲一遍吗」→ S1 无 区别/没听懂/再讲一遍
#   「小组项目怎么分工」→ S3 无 分工/小组
#   「帮我出几道模拟题」→ S4 无 模拟题/出题
#   「我感冒了该不该去校医院」→ F5 无 感冒/校医院
DWORD_PATCH = {
    'S1-course-qa': ('`讲一下` ｜ `这题` ｜ `为什么` ｜ `推导` ｜ `证明` ｜ `不会做` ｜ `求解` ｜ `求证` ｜ `解释一下` ｜ `听不懂` ｜ `卡住` ｜ `怎么做`',
                     '`讲一下` ｜ `这题` ｜ `为什么` ｜ `推导` ｜ `证明` ｜ `不会做` ｜ `求解` ｜ `求证` ｜ `解释一下` ｜ `听不懂` ｜ `卡住` ｜ `怎么做` ｜ `区别` ｜ `辨析` ｜ `没听懂` ｜ `再讲一遍`'),
    'S3-assignment': ('`作业` ｜ `实验报告` ｜ `课程设计` ｜ `平时分` ｜ `大作业` ｜ `论文作业` ｜ `提交` ｜ `报告怎么写` ｜ `自查`',
                      '`作业` ｜ `实验报告` ｜ `课程设计` ｜ `平时分` ｜ `大作业` ｜ `论文作业` ｜ `提交` ｜ `报告怎么写` ｜ `自查` ｜ `分工` ｜ `小组`'),
    'S4-exam-prep': ('`考试` ｜ `复习` ｜ `背诵` ｜ `突击` ｜ `卡组` ｜ `刷题` ｜ `期末` ｜ `期中` ｜ `四六级` ｜ `背单词` ｜ `记忆` ｜ `遗忘` ｜ `临时抱佛脚`',
                     '`考试` ｜ `复习` ｜ `背诵` ｜ `突击` ｜ `卡组` ｜ `刷题` ｜ `期末` ｜ `期中` ｜ `四六级` ｜ `背单词` ｜ `记忆` ｜ `遗忘` ｜ `临时抱佛脚` ｜ `模拟题` ｜ `出题` ｜ `模拟卷`'),
    'F5-health': ('`生病` ｜ `就医` ｜ `医保` ｜ `锻炼` ｜ `饮食` ｜ `体检` ｜ `运动` ｜ `受伤`',
                  '`生病` ｜ `就医` ｜ `医保` ｜ `锻炼` ｜ `饮食` ｜ `体检` ｜ `运动` ｜ `受伤` ｜ `感冒` ｜ `发烧` ｜ `校医院`'),
}
DSENT = {
    'S1-course-qa': '`区别` ｜ `辨析` ｜ `没听懂` ｜ `再讲一遍`',
    'S3-assignment': '`自查` ｜ `分工` ｜ `小组`',
    'S4-exam-prep': '`临时抱佛脚` ｜ `模拟题` ｜ `出题` ｜ `模拟卷`',
    'F5-health': '`受伤` ｜ `感冒` ｜ `发烧` ｜ `校医院`',
}
for d, (a, b) in DWORD_PATCH.items():
    t = read('domains/%s/_domain.md' % d)
    if t is None:
        print('  [SKIP] %s' % d)
        continue
    if DSENT[d] in t:
        print('  [SAME] %s :: %r' % (d, DSENT[d][:30]))
        continue
    if a not in t:
        print('  [MISS] %s' % d)
        continue
    write('domains/%s/_domain.md' % d, t.replace(a, b, 1))
    print('  [OK]   %s 补词' % d)

print('== A) 派生 20 域触发词并集（同源）==')
DOMWORDS = collector_domain_words()
print('  域触发词并集：%d 个' % len(DOMWORDS))

print('== B) config.yaml：门词表改为域表并集 + 越界信号 + 边界说明 ==')
t = read('config.yaml')
old_block = re.search(r'# =+ 触发门.*?(?=# =+ 学校绑定)', t, re.S)
if not old_block:
    print('  [MISS] 未找到触发门段')
else:
    if 'out_of_scope_markers' in old_block.group(0):
        print('  [SAME] 触发门段已是同源版')
    else:
        NEW = '''# ============ 触发门（强制 · **单一真相源**） ============
# 只有在下列**任一**成立时才「接管」——即走三级结构与本包的输出契约；
# 否则**不接管**：按普通助手直接回答，不套模板、不写档案、不标 [已降级]。
# 由 scripts/selfcheck.sh [8d] 断言本段字段齐全，且 SKILL.md 的触发门与之一致。
#
# ⚠️ **词表同源铁律（v3.3.6）**：`learning_markers` 是 **20 域触发词的并集**，
#    由构建层 scripts/_build/v3/step67_gate_align.py 从 `_registry.md` 与各域 `_domain.md` 的
#    `## 触发词` 段**派生**，**不手工维护**。理由（实测）：门曾另起一套窄词表（50 词）而域表有 199 词
#    → 交集仅 16 个 → 出现 **「域能锁定、门却不放行」** 的 39 处矛盾（干跑查出）。
#    **判据：能锁定到 20 域之一，就放行。** 覆盖边界交给 `out_of_scope_markers`。
trigger:
  when_any:
    - 明确涉及大连理工大学          # 校名/简称/校区/校内系统/校内事务（见 dlut_markers）
    - 学习或校园生活诉求            # == 能锁定到 20 域之一（见 learning_markers，域表并集）
    - 对方自述为大连理工大学学生     # "我是大工的学生""我们学校…"等自述
  dlut_markers: ''' + yaml_list(['大连理工', '大工', 'DUT', 'dlut', '凌水', '开发区校区', '盘锦校区', 'i大工', '本校', '校内'] + CAMPUS) + '''
  # ↓ 20 域触发词并集（派生；勿手改，改域表后重跑 step67）
  learning_markers: ''' + yaml_list(DOMWORDS) + '''
  # 学习意图表述（名词之外的口语说法；裸词「学」刻意不放，会被「同学/学校/学期」误命中）
  learning_intents: [想学, 自学, 怎么学, 如何学, 入门, 学会, 学不会, 教我, 讲解一下, 帮我理解, 搞懂, 弄懂, 刷题, 做题, 背单词, 补习, 教程]
  # **越界信号**：与 DUT、学习、校园生活均无关的通用事务 → **命中即不接管**（优先级最高，压过宽词表）
  out_of_scope_markers: ''' + yaml_list(OUT_OF_SCOPE) + '''
  boundary_note: 单词命中不等于该接管 —— 判据是**需求主键 T(任务)+O(对象)**。
    # 例：「帮我写个冒泡排序（面试用）」对象是「冒泡排序」（不属任何域），「面试」只是用途 → **不接管**；
    #     「面试怎么准备」对象就是面试本身 → **接管（F8）**。token 命中只做初筛，归属由主键定。
  not_triggered_behavior: 不接管      # 直接按普通助手回答：不套输出模板 / 不写学习档案 / 不标 [已降级] / 不做域审查
  lock_after_trigger: true           # 触发即锁定：必须走工作流 ①→⑧，不可跳步、不可绕过域审查直接作答
  ladder: [同域库内 skill, 外部桥接, 自生成]   # 降级顺序（1→2→3）；**前一档未穷尽不得进入下一档**
  self_generate_requires: 档 2 已尝试且未命中（或因红线域/离线被明确跳过并在输出中说明）
  skip_ladder_when_redline_or_offline: true    # 红线域（F3/F5）与离线：可跳档 2，但**必须明说**再进档 3

'''
        write('config.yaml', t[:old_block.start()] + NEW + t[old_block.end():])
        print('  [OK]   门词表已改为域表并集（%d 词）+ 越界信号（%d 词）+ 边界说明'
              % (len(DOMWORDS), len(OUT_OF_SCOPE)))

print('== C) SKILL.md：T2 表述 + 越界信号行 ==')
t = read('SKILL.md')
edits = [
    ('| **T2** | **知识学习活动**（**不要求**与 DUT 相关） | ① 学习类**名词**：学习、复习、备考、笔记、作业、课程、考试、论文、文献、实验、报告、科研、写作、英语、雅思、保研、考研、求职、竞赛；<br>② **学习意图**表述：**想学**、自学、怎么学、入门、教我、讲解一下、帮我理解、搞懂、刷题、背单词…（`trigger.learning_intents`） |',
     '| **T2** | **学习或校园生活诉求**（判据 = **能锁定到 20 域之一**） | 词表 = **20 域触发词的并集**（`trigger.learning_markers`，共 196 词，**构建期从域表派生、不手维护**）<br>＋ 学习意图表述（想学 / 自学 / 入门 / 教我 / 搞懂 / 刷题…，`trigger.learning_intents`）<br>⚠️ **判据是「能锁定到域」**，不是「命中某个词」—— 门与域表**同源**，不会再出现「域能锁、门不放行」 |',
     '| **T2** | **学习或校园生活诉求**（判据 = **能锁定到 20 域之一**）'),
    ('> **边界情况**：T2「知识学习活动」很宽 —— 凡属"学东西"的求助都算（含非 DUT 的自学、考研、语言）。\n> **但它不覆盖**：闲聊、时政、纯工具性编程问题（与学习无关的）、娱乐与消费推荐。',
     '> **边界情况**：T2 很宽 —— 凡属「学习」或「校园生活」的求助都算（含非 DUT 的自学、考研、语言、\n'
     '> 作息 / 身心 / 财务 / 健康 / 军训志愿 等生活域诉求）。\n'
     '> **但越界信号会挡住**（见 §1.5）：闲聊、影视娱乐、天气、出行、股票、购物、旅游等一律不接管。',
     '> **边界情况**：T2 很宽'),
    ('### 2. 不触发时**不接管**（硬）',
     '### 1.5 越界信号（命中即**不接管**，优先级最高）\n'
     '\n'
     '与 DUT、学习、校园生活**均无关**的通用事务（`trigger.out_of_scope_markers`）：\n'
     '电影 / 电视剧 / 综艺 / 追星 / 游戏 / 天气 / 机票 / 火车票 / 酒店 / 外卖 / 股票 / 基金 / 彩票 /\n'
     '购物 / 旅游 / 星座 / 算命 / 菜谱 … → 直接按普通助手回答。\n'
     '\n'
     '> ⚠️ **单词命中 ≠ 该接管**：判据是**需求主键 T(任务) + O(对象)**。\n'
     '> 例：「帮我写个冒泡排序（**面试用**）」——对象「冒泡排序」不属任何域，「面试」只是**用途** → **不接管**；\n'
     '> 而「**面试**怎么准备」——对象就是面试 → **接管（F8）**。token 命中只做初筛，**归属由主键定**。\n'
     '\n'
     '### 2. 不触发时**不接管**（硬）',
     '### 1.5 越界信号'),
    ('### 4. 降级顺序（**四级**，`config.yaml` 的 `trigger.ladder`）',
     '### 4. 降级顺序（**三档**，`config.yaml` 的 `trigger.ladder`）',
     '### 4. 降级顺序（**三档**'),
]
o = t
for a, b, sent in edits:
    if sent in o:
        print('  [SAME] %r' % sent[:40]); continue
    if a not in o:
        print('  [MISS] %r' % a[:40]); continue
    o = o.replace(a, b, 1)
    print('  [OK]   %r' % a[:40])
if o != t:
    write('SKILL.md', o)

print('== E) selfcheck [8d] 补断言 ==')
t = read('scripts/selfcheck.sh')
if t is None:
    print('  [SKIP] 无 selfcheck.sh')
elif 'out_of_scope_markers' in t:
    print('  [SAME] [8d] 已含越界信号断言')
else:
    a = "for _t in 明确涉及大连理工大学 知识学习 自述为大连理工大学学生; do"
    b = ("# 词表同源（v3.3.6）：门词表必须是 20 域触发词的并集 —— 防「域能锁、门不放行」的 39 处矛盾复发\n"
         "_gatewords=$(sed -n '/^  learning_markers:/,/^  learning_intents:/p' config.yaml 2>/dev/null)\n"
         "_cov=0\n"
         "for _w in 概念图 卡组 引用规范 军训 作息 简历 投稿 专利 查重 讲义 emo 助学金; do\n"
         "  printf '%s' \"$_gatewords\" | grep -q \"$_w\" && _cov=$((_cov+1))\n"
         "done\n"
         "[ \"${_cov:-0}\" -ge 10 ] && ok \"门词表与域表同源（12 个代表词命中 $_cov 个）\" \\\n"
         "  || bad \"门词表与域表不同源（代表词仅命中 ${_cov:-0}/12）—— 会把能锁定的问题挡在门外\"\n"
         "for _k in '^  out_of_scope_markers:' '^  boundary_note:'; do\n"
         "  grep -q \"$_k\" config.yaml 2>/dev/null && ok \"config.yaml 含 $_k\" || bad \"config.yaml 缺 $_k\"\n"
         "done\n"
         "grep -qF '越界信号' SKILL.md 2>/dev/null && ok \"SKILL.md 已声明越界信号\" || bad \"SKILL.md 缺越界信号\"\n"
         "for _t in 明确涉及大连理工大学 知识学习 自述为大连理工大学学生; do")
    if a in t:
        write('scripts/selfcheck.sh', t.replace(a, b, 1))
        print('  [OK]   已补词表同源断言')
    else:
        print('  [MISS] 未找到 [8d] 锚点')

print('== F) 构建侧层序 ==')
t = read('scripts/_build/v3/README.md')
if t and 'step67_gate_align.py' not in t:
    a = '| 25 | `step66_domain_router.py` |'
    if a in t:
        write('scripts/_build/v3/README.md', t.replace(a,
              '| 26 | `step67_gate_align.py` | **触发门与域表同源**：`learning_markers` 改为 **20 域触发词并集**（构建期派生）'
              '+ `out_of_scope_markers` 越界信号 + `boundary_note`（顺带提及不算）+ SKILL.md §1.5 越界信号'
              '+ selfcheck [8d] 词表同源断言；修订号 → `3.3.6` | 新增层 |\n' + a, 1))
        print('  [OK]   已登记 step67')
    else:
        print('  [MISS] 层序锚点未命中')
else:
    print('  [SAME] 已登记')

print('== G) 修订号 %s → %s ==' % (OLD_REV, NEW_REV))
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
    x = read(rel)
    if x and a in x:
        write(rel, x.replace(a, b))
        print('  [OK]   %s ×%d' % (rel, x.count(a)))
    else:
        print('  [--]   %s ×0' % rel)

print('done')
