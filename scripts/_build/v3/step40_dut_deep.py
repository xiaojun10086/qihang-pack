# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 8 层 · DUT 特化加深】给 9 个 MIT 派生（改造）skill 的方法库末尾补一段具体 DUT 绑定点
# 原名 gen_dut_deep.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""改造（MIT 派生）skill 的 DUT 特化加深：在「方法库 · 判定细则」末尾补一段具体 DUT 绑定点。"""
import os, io, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

DEEP = {
 'deep-work': '**DUT 特化**：专注窗口直接对接 DUT 作息——按教学周节次（早八 / 上午 / 下午大节）切块，深度块避开排在早八与连堂课；自习落点优先图书馆伯川馆 / 令希馆开放时段，体育与场馆预约须走 i大工 APP（无网页版）。',
 'resume-tailor': '**DUT 特化**：岗位口径对齐 DUT 就业信息网的校招节奏（秋招 9–11 月、春招 3–5 月），简历版式按学校就业指导中心通行要求（一页、倒序、量化成果），校内竞赛与项目经历按 DUT 赛事名称规范书写。',
 'lit-fetch': '**DUT 特化**：合法获取优先走 DUT 图书馆订阅库与文献传递服务；校外访问用 WebVPN 登录图书馆电子资源入口；开发区 / 盘锦校区学生对应分馆服务，馆际互借走本校图书馆服务台。',
 'socratic-qa': '**DUT 特化**：追问语料取材于 DUT 课程常见卡点（数学分析、大学物理、专业基础课），每次追问回扣培养方案对应能力点，使「自己发现答案」的过程同时对齐课程考核要求。',
 'link-notes': '**DUT 特化**：节点与标签结构对接 DUT 课程教学大纲的章节—知识点层级，双链命名与课程名 / 章节号一致，复习时可按课程与教师授课顺序回溯，直接对齐期中期末考核范围。',
 'imrad-scaffold': '**DUT 特化**：骨架对接 DUT 学位论文与课程设计格式要求（章节编号、图表题注、公式编号、参考文献 GB/T 7714），并提供 DUT 毕业设计系统提交前的自查项。',
 'faster-cycle': '**DUT 特化**：以 DUT 学期与课程进度组织循环；只按用户提供或核验过的教学周、期中/期末安排分档。信息不足时用相对周次，不推断具体日期；把「教学回讲」放在课程推进期间，并按实际考试安排调整回顾节奏。',
 'ielts-coach': '**DUT 特化**：备考周期对接 DUT 出国交流、公派与学分互认项目的语言成绩提交节点（可向国际合作与交流处与学院外事秘书确认），并区分校内语言班与自主备考两条路线。',
 'argument-slides': '**DUT 特化**：论证结构对接 DUT 开题 / 中期 / 学位答辩与课程汇报的规定模板与时间限制，视觉模板一律沿用学校或课程指定样式，不另造配色。',
}


def rd(p):
    with io.open(p, 'r', encoding='utf-8') as f:
        return f.read()


def wr(p, t):
    with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
        f.write(t)


done = []
for n, line in DEEP.items():
    hits = []
    for dp, dns, fns in os.walk(os.path.join(ROOT, 'domains')):
        if 'SKILL.md' in fns and os.path.basename(dp) == n:
            hits.append(os.path.join(dp, 'SKILL.md'))
    if len(hits) != 1:
        print('!! 未唯一命中', n, len(hits))
        continue
    p = hits[0]
    t = rd(p)
    if 'DUT 特化' in t.split('## 方法库 · 判定细则')[1].split('## 可执行示例')[0]:
        print('跳过（方法库已有 DUT 特化）：', n)
        continue
    assert t.count('\n## 可执行示例\n') == 1, n
    t = t.replace('\n## 可执行示例\n', '\n' + line + '\n\n## 可执行示例\n', 1)
    wr(p, t)
    done.append(n)

print('DUT 特化加深：%d 个  %s' % (len(done), ','.join(done)))
