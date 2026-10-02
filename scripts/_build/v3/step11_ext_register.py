# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 3 层 · 改造 skill 登记】12 个 MIT 派生（改造）skill 登记进 _domain.md；标题统一「唯一通道」；F7 触发词消歧
# 原名 qihang_v3_step2.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
import os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

# 域目录名 → (新skill名, 一句话定位)
NEW = {
    'S1-course-qa':        ('socratic-qa', '不直接给答案，用五类渐进提问引导自悟；卡壳 3 轮自动降级分步讲解'),
    'S2-lecture-notes':    ('link-notes', '用双链、标签层级与嵌入引用把讲义、错题、概念连成知识网络'),
    'S3-assignment':       ('imrad-scaffold', '课程论文 / 毕设的 IMRAD 四节骨架 + 对抗性自审；想法与数据由用户提供，正文不代写'),
    'S4-exam-prep':        ('faster-cycle', '忘/练/态/教/恒/复六步循环 + 四种学习模式，以教学回讲为核心留存手段'),
    'S5-academic-writing': ('argument-slides', '每页标题写结论（行动标题）+ 幽灵测试 + 一页一论据的论证式演示结构'),
    'S6-language':         ('ielts-coach', '摸底三问 + 算分公式 + 80/20 时间分配 + 分数换算表的雅思应考策略'),
    'F2-focus':            ('deep-work', '深浅分类 + 时间块（≥90 分钟、日上限 4 小时）+ 浅工作两批 + 收尾仪式'),
    'F8-career':           ('resume-tailor', '完全真实前提下的简历岗位定向重排：概要镜像 JD、技能重排、一岗一版本'),
    'R1-literature':       ('lit-fetch', '分层检索 + 合法全文路线（开放获取优先，绝不绕付费墙）+ 去重与状态记录'),
    'R2-experiment-data':  ('stats-workflow', '先框问题再碰数据、前提必查必报、效应量与 p 值并重的六步统计纪律'),
    'R3-research-tools':   ('code-mentor', '使命驱动 + 最近发展区选题 + 检索练习，一课一得的编程私教'),
    'R4-publication':      ('defense-qa', '幽灵测试 + 三问自审 + 预设评委问题清单，把被质询变成可排练的环节'),
}

for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    if not d[0] in 'SFR' or not d[1].isdigit():
        continue
    p = os.path.join(ROOT, 'domains', d, '_domain.md')
    if not os.path.exists(p):
        continue
    t = open(p, encoding='utf-8', newline='').read()
    orig = t

    # 1) 标题统一:库内唯一通道
    t = t.replace('## 库内 skill（优先使用，无需安装）', '## 库内 skill（唯一通道，无需安装）')

    # 2) 插入新 skill 条目(在「## DUT 绑定点」之前)
    if d in NEW:
        name, desc = NEW[d]
        if ('**`%s`**' % name) in t:
            continue          # 幂等：已登记过则跳过
        # 来源标注:大部分为 MIT 改造,S5/R4 为专有许可证思路参考
        src = {
            'S5-academic-writing': '思路参考 Gabberflast/academic-pptx-skill（专有许可证，零内容摘录）',
            'R4-publication': '思路参考 Gabberflast/academic-pptx-skill（专有许可证，零内容摘录）',
        }.get(d, '改造自外部 MIT 最优解 + DUT 特化')
        entry = ('\n- **`%s`** — （%s）\n  %s\n' % (name, src, desc))
        t = re.sub(r'\n(?=## DUT 绑定点)', entry + '\n', t, count=1)
        # 3) 执行顺序步骤 3 补引用
        t = re.sub(r'（首选 `([a-z-]+)`；不满足时用同域备选 `([a-z-]+)`）',
                   lambda m: '（首选 `%s`；备选 `%s`；特色 `%s`）' % (m.group(1), m.group(2), name), t, count=1)

    if t != orig:
        open(p, 'w', encoding='utf-8', newline='').write(t)
        print('updated:', d)

# 4) F7 触发词消歧注（**幂等**：原版 new 含 old，二次运行会把注重复追加一次）
p = os.path.join(ROOT, 'domains', 'F7-further-study', '_domain.md')
t = open(p, encoding='utf-8', newline='').read()
if '「导师」词面与 `R6` 共享' in t:
    print('跳过（F7 消歧注已存在）')
else:
    t2 = t.replace('`保研` ｜ `考研` ｜ `留学` ｜ `申博` ｜ `导师` ｜ `推免` ｜ `夏令营` ｜ `绩点`',
                   '`保研` ｜ `考研` ｜ `留学` ｜ `申博` ｜ `导师` ｜ `推免` ｜ `夏令营` ｜ `绩点`\n\n> 「导师」词面与 `R6` 共享：**查公开资料 → `R6`**；**选导师 / 套磁规划 → 本域**（见 `_registry.md` 消歧）')
    if t2 != t:
        open(p, 'w', encoding='utf-8', newline='').write(t2)
        print('updated: F7 消歧注')
