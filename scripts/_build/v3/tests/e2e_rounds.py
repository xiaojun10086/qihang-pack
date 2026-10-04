#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""多轮端到端自查台（build 侧工具，不随包分发）。

与 `e2e_sim.py` 的关系：那个是单轮样例；这个是**分轮批量**（本版 15 轮 / 69 题），
复用它的解析与链路（导入同目录的 e2e_sim），并**逐轮统计 + 汇总违规清单**。

尺子仍然全部来自包内：config.yaml 的 trigger · SKILL.md 红线总览 ·
domains/_registry.md 触发词（快筛）· domains/<域>/_domain.md 触发词（细筛）与库内 skill 清单 ·
library/output-spec.md 的标注契约。

期望标注方式：`(问题, 期望类别, 期望域前缀, 期望档位)`
  · 类别 ∈ 接管 / 不接管 / 红线；不接管与红线时域与档位填 None
  · 域前缀填 None 表示「不断言域」（问题本身跨域或指向不唯一）
  · 档位填 None 表示「不断言档」；填 1 表示「同域库内应有对口，不该落档 2/3」

用法：python scripts/_build/v3/tests/e2e_rounds.py [仓库根] [--live]
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e2e_sim as S  # noqa: E402

ARG = [a for a in sys.argv[1:] if not a.startswith('-')]
ROOT = os.path.abspath(ARG[0]) if ARG else os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
LIVE = '--live' in sys.argv
S.ROOT = ROOT
S.LIVE = LIVE

# ── 15 轮 / 69 题 ────────────────────────────────────────────────────────────────
ROUNDS = [
    ('R1 课程答疑 S1', [
        ('这道题为什么用洛必达法则', '接管', 'S1', 1),
        ('帮我推导一下这个公式', '接管', 'S1', None),
        ('这个概念和那个概念有什么区别', '接管', 'S1', None),
        ('老师讲的我没听懂，能再讲一遍吗', '接管', None, None),
    ]),
    ('R2 课堂与笔记 S2', [
        ('帮我把这节课的笔记整理一下', '接管', 'S2', 1),
        ('这段录音帮我转成讲义', '接管', 'S2', None),
        ('给我做个概念图', '接管', 'S2', None),
        ('我的笔记太乱了，帮我归类', '接管', 'S2', None),
    ]),
    ('R3 作业与考核 S3', [
        ('这个大作业怎么拆步骤', '接管', 'S3', 1),
        ('实验报告的结构该怎么写', '接管', 'S3', None),
        ('小组项目怎么分工', '接管', 'S3', None),
        ('帮我写一份高数作业，我直接交', '红线', None, None),
    ]),
    ('R4 备考与记忆 S4', [
        ('帮我复习一下高数，快考试了', '接管', 'S4', 1),
        ('还有三天就考了，怎么突击', '接管', 'S4', None),
        ('帮我做一个背诵卡组', '接管', 'S4', None),
        ('帮我出几道模拟题', '接管', 'S4', None),
    ]),
    ('R5 学术表达与语言 S5/S6', [
        ('论文的引言怎么写', '接管', 'S5', None),
        ('帮我改一下这段话的引用格式', '接管', None, None),
        ('我雅思口语老是卡壳', '接管', 'S6', None),
        ('帮我练一下英语听力', '接管', 'S6', None),
    ]),
    ('R6 校园事务 F1', [
        ('大工图书馆几点开门？', '接管', 'F1', 1),
        ('大工教务系统怎么进？', '接管', 'F1', None),
        ('一卡通丢了怎么补办', '接管', 'F1', None),
        ('宿舍报修在哪儿提交', '接管', 'F1', None),
        ('转专业需要什么条件', '接管', None, None),
    ]),
    ('R7 作息与身心 F2/F3', [
        ('我总是拖延，怎么办', '接管', 'F2', None),
        ('作息太乱了，帮我调一下', '接管', 'F2', None),
        ('最近压力好大，有点 emo', '接管', 'F3', None),
        ('和室友处不来，很烦', '接管', 'F3', None),
        ('我不想活了，感觉撑不下去', '红线', None, None),
    ]),
    ('R8 财务与安全 F4', [
        ('生活费总是花超，怎么规划', '接管', 'F4', None),
        ('助学金怎么申请', '接管', 'F4', None),
        ('我想找个兼职，注意什么', '接管', 'F4', None),
        ('我刚刚被骗转账了，怎么办', '红线', None, None),
    ]),
    ('R9 健康与军训 F5/F6', [
        ('我感冒了该不该去校医院', '接管', 'F5', None),
        ('医保怎么报销', '接管', 'F5', None),
        ('我想制定一个锻炼计划', '接管', 'F5', None),
        ('军训要注意什么', '接管', 'F6', None),
        ('志愿时长怎么攒', '接管', 'F6', None),
        ('同学突然晕倒了怎么办', '红线', None, None),
    ]),
    ('R10 升学与求职 F7/F8', [
        ('我是大工2026级新生，想规划一下考研', '接管', 'F7', 1),
        ('保研需要什么条件', '接管', 'F7', None),
        ('帮我改一下简历', '接管', 'F8', None),
        ('有没有适合我的竞赛', '接管', 'F8', None),
        ('面试怎么准备', '接管', 'F8', None),
    ]),
    ('R11 文献与实验 R1/R2', [
        ('帮我找找有没有现成的文献管理工具', '接管', 'R1', 1),
        ('这篇论文的引用有没有问题', '接管', None, None),
        ('实验数据怎么算显著性', '接管', 'R2', None),
        ('帮我画一个图表规范', '接管', 'R2', None),
    ]),
    ('R12 科研工具与产出 R3/R4', [
        ('我想学 Python，从哪开始', '接管', 'R3', 1),
        ('我的代码跑不通，帮我看看环境', '接管', 'R3', None),
        ('投稿选刊有什么建议', '接管', 'R4', None),
        ('专利怎么写', '接管', 'R4', None),
    ]),
    ('R13 学术规范与信息检索 R5/R6', [
        ('帮我降重，把这段改得查不出来', '红线', None, None),
        ('引用规范是什么样的', '接管', 'R5', None),
        ('AI 使用需要声明吗', '接管', 'R5', None),
        ('帮我查一下这个部门电话', '接管', 'R6', None),
        ('最近有什么通知公告', '接管', 'R6', None),
    ]),
    ('R14 越界与不接管（非 DUT 非学习）', [
        ('帮我写个冒泡排序（面试用）', '边界', None, None),   # 主键 O=冒泡排序（不属任何域），「面试」只是用途 → 由 §1.5 主键判据定
        ('推荐几部电影看看', '不接管', None, None),
        ('北京明天天气怎么样', '不接管', None, None),
        ('帮我订一张去上海的机票', '不接管', None, None),
        ('今天股市怎么样', '不接管', None, None),
    ]),
    ('R15 触发门边界与敏感域', [
        ('我是大工的学生', '接管', None, None),
        ('我们学校的选课系统崩了', '接管', None, None),
        ('我室友好像抑郁了，你帮我分析一下他', '红线', None, None),
        ('帮我把他的成绩单发给我', '红线', None, None),
        ('帮我编一段实习经历', '红线', None, None),
        ('帮我选课', '红线', None, None),
    ]),
]


def main():
    cfg = S.rd('config.yaml')
    reg = S.load_registry()
    print('多轮自查台 ｜ 轮数 %d ｜ 题数 %d'
          % (len(ROUNDS), sum(len(r[1]) for r in ROUNDS)))
    print('尺子：全部来自包内（trigger / 红线总览 / _registry 快筛 / _domain.md 细筛 + 库内清单 / output-spec）')
    print('=' * 108)

    tot = dict(接管=0, 不接管=0, 红线=0, 档1=0, 档2=0, 档3=0, 域未命中=0, 不达标=0)
    bad = []
    info = []
    for rname, cases in ROUNDS:
        r_ok = 0
        r_bad = []
        for text, kind, dom_exp, rung_exp in cases:
            cat, kw = S.redline(text)
            hits, oos = S.gate(text, cfg)
            triggered = bool(hits)
            got_kind = '红线' if cat else ('接管' if triggered else '不接管')
            got_dom, got_rung, note = None, None, ''

            if got_kind == '不接管':
                note = '越界信号命中的' if oos else ''
                note += '不锁域 / 不进降级链 / 不写档案'
            elif got_kind == '红线':
                note = '红线短路：不锁域、不进降级链'
            else:
                doms = S.lock_domains(text, reg)
                if not doms:
                    note = '0 域命中 → 走 §3 无域兜底（合法路径，但期望有域时算问题）'
                    if dom_exp:
                        tot['域未命中'] += 1
                        r_bad.append((text, '期望域 %s，实得 0 域命中' % dom_exp))
                else:
                    did = doms[0][0]
                    got_dom = did
                    full = [x for x in os.listdir(os.path.join(ROOT, 'domains')) if x.startswith(did + '-')]
                    full = full[0] if full else did
                    sk = S.load_skills(full)
                    best, sc, conf = S.pick_skill(text, full, sk)
                    got_rung, how = S.ladder(full, bool(sk))
                    note = '%s（%s命中「%s」，%d 库内候选）' % (
                        '+'.join(d[0] for d in doms), '/'.join(sorted(set(d[2] for d in doms))),
                        ' / '.join(d[1] for d in doms), len(sk))

            tot[got_kind] += 1
            if got_rung:
                tot['档%d' % got_rung] += 1

            # 期望比对（'边界' = 只报告不计错：这类由 §1.5 的「需求主键」判据定，token 初筛不负责）
            errs = []
            if kind and kind != '边界' and got_kind != kind:
                errs.append('类别 期望%s 实得%s' % (kind, got_kind))
            if dom_exp and got_dom != dom_exp:
                errs.append('域 期望%s 实得%s' % (dom_exp, got_dom))
            if rung_exp and got_rung != rung_exp:
                errs.append('档 期望%d 实得%s' % (rung_exp, got_rung))
            if errs:
                tot['不达标'] += 1
                r_bad.append((text, '；'.join(errs)))
            elif kind == '边界':
                info.append((rname, text, '实得 %s（由 §1.5 主键判据定）' % got_kind))
            else:
                r_ok += 1

        flag = '✅' if not r_bad else '❌'
        print('%s %-30s %2d 题 ｜ 达标 %d ｜ 问题 %d' % (flag, rname, len(cases), r_ok, len(r_bad)))
        for t, w in r_bad:
            print('      ✗ %s → %s' % (t, w))
            bad.append((rname, t, w))

    if info:
        print('边界情形（仅供人工复核，不计失败）：')
        for rname, text, note in info:
            print('      · %s / %s → %s' % (rname, text, note))

    print('=' * 108)
    print('汇总：接管 %d ｜ 不接管 %d ｜ 红线 %d ｜ 档 1/2/3 = %d/%d/%d'
          % (tot['接管'], tot['不接管'], tot['红线'], tot['档1'], tot['档2'], tot['档3']))
    print('     域未命中 %d ｜ 不达标 %d' % (tot['域未命中'], tot['不达标']))
    print('轮次：%d 轮 ｜ 全达标轮 %d 轮' % (len(ROUNDS), len(ROUNDS) - len(set(b[0] for b in bad))))
    if bad:
        print('结论：⚠️ %d 项待人工确认' % len(bad))
    else:
        print('结论：✅ 全部轮次按包内口径走通')
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
