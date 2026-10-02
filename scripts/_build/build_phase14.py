#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」build_phase14 —— 库外候选「多源比对 + 选优」层

把 19 个域的 `skills/external.md` 从「单候选清单」升级为
「多平台候选 × 四维评分 × 最优解 × 降级链」，并汇总生成 `references/skill-matrix-v3.md`。

数据来源：GitHub API 实抓（2026-10-02），字段 stars / license / pushed_at / archived / size。
评分口径见本文件 SCORE_SPEC，并在产物中同步展示，保证可复算。
四维中「合规 / 可用 / 社区」由数据算出，「适配」为人工判定（ADAPT 表，逐条给出理由）。

用法: python scripts/_build/build_phase14.py .
"""
import os, re, sys, datetime

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
REF_DATE = datetime.date(2026, 10, 2)
STALE_DAYS = 180

# ------------------------------------------------------------------ 实测元数据
# repo: (stars, license_spdx, pushed_at, size_kb, flags)
# flags: 'key'=需 API Key/联网才能用, 'big'=仓库 >100MB, 'arch'=已归档
META = {
 'mattpocock/skills':                       (273959, 'MIT',        '2026-09-29', 1795, ''),
 'anthropics/skills':                       (179334, 'NOASSERTION', '2026-09-29', 5170, ''),
 'Imbad0202/academic-research-skills':      (50096,  'NOASSERTION', '2026-10-02', 23549, 'key'),
 'kepano/obsidian-skills':                  (49077,  'MIT',         '2026-09-15', 44,   ''),
 'K-Dense-AI/scientific-agent-skills':      (47304,  'MIT',         '2026-10-01', 472781, 'big'),
 'googleworkspace/cli':                     (31231,  'Apache-2.0',  '2026-09-24', 10777, ''),
 'alirezarezvani/claude-skills':            (27194,  'MIT',         '2026-08-30', 22632, ''),
 'openai/skills':                           (27841,  'NOASSERTION', '2026-09-08', 2528, ''),
 'obra/superpowers':                        (294023, 'MIT',         '2026-09-27', 7549, ''),
 'Paramchoudhary/ResumeSkills':             (2509,   'MIT',         '2026-06-19', 178,  ''),
 'NeoLabHQ/context-engineering-kit':        (1738,   'GPL-3.0',     '2026-08-26', 11332, ''),
 'bevibing/tutor-skills':                   (1313,   'MIT',         '2026-02-28', 25,   ''),
 'Gabberflast/academic-pptx-skill':         (1100,   'MIT',         '2026-07-14', 210,  ''),
 'wentorai/Research-Claw':                  (855,    'NOASSERTION', '2026-08-20', 15947, ''),
 'GarethManning/education-agent-skills':    (817,    'NOASSERTION', '2026-08-28', 2396, ''),
 'dair-ai/dair-academy-plugins':            (615,    'MIT',         '2026-07-21', 151,  ''),
 'hluaguo/learn-faster-kit':                (380,    'MIT',         '2026-08-04', 142,  ''),
 'bevibing/socrates-skill':                 (326,    'MIT',         '2026-04-02', 5,    ''),
 'YANZHANLIN/ielts-claude-skills':          (307,    'MIT',         '2026-07-20', 11,   ''),
 'vishalsachdev/canvas-mcp':                (270,    'MIT',         '2026-10-02', 4967, ''),
 'Lucaswangzcx/literature-downloader-skill':(230,    'MIT',         '2026-04-27', 46,   ''),
 'K-Dense-AI/scientific-agents':            (192,    'MIT',         '2026-09-29', 16761, ''),
 'flysheep-ai/education-skills':            (106,    'MIT',         '2026-01-30', 68,   ''),
 'kgraph57/paper-writer-skill':             (58,     'MIT',         '2026-08-12', 567,  ''),
 'jakedahn/pomodoro':                       (56,     'MIT',         '2025-10-23', 30780, 'big'),
 'WenyuChiou/zotero-skills':                (55,     'MIT',         '2026-10-01', 244,  ''),
 'cabbage2000-lab/paper-tutor-skills':      (33,     'NOASSERTION', '2026-08-04', 1633, ''),
 'eddiebelaval/squire':                     (21,     'MIT',         '2026-08-16', 17082, 'key'),
 'lowwwbank/anything-to-course':            (18,     'MIT',         '2026-07-07', 491,  ''),
 'tianmind-studio/english-coach':           (17,     'MIT',         '2026-09-24', 6477, ''),
 '0x-man/mindmap-skill':                    (16,     'MIT',         '2026-09-28', 201,  ''),
 'JEFF7712/claude-tutor':                   (16,     'MIT',         '2026-06-25', 67,   ''),
 'hameefy/claude-latex-skill':              (10,     'MIT',         '2026-05-12', 91,   ''),
 'googlarz/math-skill':                     (9,      'NOASSERTION', '2026-03-22', 42,   ''),
 'Jellypod-Inc/school-skills':              (6,      'MIT',         '2026-04-15', 520,  ''),
 'ghutchis/chem-skill':                     (4,      'MIT',         '2025-12-28', 177,  ''),
 'Haadhi76/SOP_Consultant':                 (4,      'MIT',         '2026-06-15', 169,  ''),
 'GlacierXiaowei/structured-learning-skill':(3,      'Apache-2.0',  '2026-03-27', 21,   ''),
 'tydev-new/10xcolleges':                   (2,      'MIT',         '2026-09-22', 750,  ''),
 'egouilliard-leyton/python-tutor-skill':   (1,      'MIT',         '2026-03-30', 124,  ''),
 'xwmxcz/papers-skill':                     (1,      'MIT',         '2026-06-11', 10,   ''),
 'peter209393/anki-card-skills':            (0,      'MIT',         '2026-09-27', 77,   'key'),
 'somenssarkar/gurukul-ai':                 (0,      'NOASSERTION', '2026-02-21', 192,  'key'),
 'sourikduttanyu/interview-prep':           (0,      'MIT',         '2026-04-15', 15,   ''),
}

# ------------------------------------------------------------------ 域名 / 库内 skill
DOMAINS = {
 'S1': ('S1-course-qa', '课程答疑', 'explain-stepwise', 'error-diagnose'),
 'S2': ('S2-lecture-notes', '课堂与笔记', 'lecture-to-notes', 'note-normalize'),
 'S3': ('S3-assignment', '作业与考核', 'lab-report', 'assignment-plan'),
 'S4': ('S4-exam-prep', '备考与记忆', 'exam-sprint', 'recall-schedule'),
 'S5': ('S5-academic-writing', '学术表达', 'paper-outline', 'cite-normalize'),
 'S6': ('S6-language', '语言能力', 'lang-drill', 'pronounce-drill'),
 'F1': ('F1-campus-affairs', '校园事务', 'campus-desk', 'campus-proof-guide'),
 'F2': ('F2-focus', '作息与专注', 'focus-block', 'task-decompose'),
 'F3': ('F3-wellbeing', '身心与社交', 'wellbeing-checkin', 'peer-talk-script'),
 'F4': ('F4-money-safety', '财务与安全', 'money-guard', 'budget-plan'),
 'F5': ('F5-health', '健康与运动', 'health-guide', 'clinic-path'),
 'F6': ('F6-service', '军训与志愿', 'service-log', 'volunteer-hours'),
 'F7': ('F7-further-study', '升学深造', 'grad-plan', 'grad-calendar'),
 'F8': ('F8-career', '求职与竞赛', 'career-kit', 'competition-pick'),
 'R1': ('R1-literature', '文献检索与管理', 'lit-map', 'citation-verify'),
 'R2': ('R2-experiment-data', '实验与数据', 'data-lab', 'stats-guard'),
 'R3': ('R3-research-tools', '科研工具与代码', 'tool-setup', 'repro-env'),
 'R4': ('R4-publication', '学术产出与投稿', 'submit-kit', 'rebuttal-structure'),
 'R5': ('R5-integrity', '学术规范与伦理', 'integrity-check', 'ai-disclosure'),
}

# ------------------------------------------------------------------ 候选表
# did: [(skill, repo, adapt(0-5), 适配理由, 备注/告警)]
CAND = {
 'S1': [
   ('socrates-skill', 'bevibing/socrates-skill', 5, '苏格拉底式追问，与「不直接抛答案」完全同构', ''),
   ('tutor-skills',   'bevibing/tutor-skills',   4, '把 PDF/讲义转成讲解材料，可补 S1 材料侧', '偏笔记向，题目讲解仍靠库内'),
   ('math-skill',     'googlarz/math-skill',     4, '学科数学专项，题型贴合高数/线代', '⛔ 无 LICENSE'),
   ('chem-skill',     'ghutchis/chem-skill',     3, '化学专项，可补理科答疑', '⚠️ 2025-12 后未更新'),
   ('teach',          'mattpocock/skills',       3, '通用教学法，工程向非学科向', ''),
   ('gurukul-ai',     'somenssarkar/gurukul-ai', 1, '面向 Grade 7，与大学课程错位', '⛔ 无 LICENSE，且需 API Key'),
 ],
 'S2': [
   ('tutor-skills',    'bevibing/tutor-skills',        5, 'PDF/文档 → Obsidian 结构化笔记，正中本域', ''),
   ('obsidian-skills', 'kepano/obsidian-skills',       4, '知识库侧最强、零脚本、无依赖', ''),
   ('mindmap',         '0x-man/mindmap-skill',         4, '概念图产出，与笔记归一互补', ''),
   ('lecture-to-study-guide', 'Jellypod-Inc/school-skills', 4, '课堂材料 → 学案，教育场景原生', '--force 会覆盖已有文件'),
   ('youtube-notetaker', 'dair-ai/dair-academy-plugins', 3, '录播课转笔记', ''),
   ('anything-to-course', 'lowwwbank/anything-to-course', 3, '任意材料 → 学习课，可做复习侧', ''),
 ],
 'S3': [
   ('canvas-mcp',    'vishalsachdev/canvas-mcp', 4, 'LMS 作业/成绩工作流，最贴近「作业管理」', '⚠️ 仅 Canvas LMS，非大工系统'),
   ('paper-writer',  'kgraph57/paper-writer-skill', 3, '本地 pandoc 出报告骨架', ''),
   ('document-skills', 'anthropics/skills',      3, 'docx/pdf/pptx 文档处理底座', '⚠️ 仓库根目录未声明总许可证'),
 ],
 'S4': [
   ('structured-learning', 'GlacierXiaowei/structured-learning-skill', 4, '结构化学习法，已实测装通', ''),
   ('learn-faster-kit',    'hluaguo/learn-faster-kit', 4, '学习法工具包，中文友好', ''),
   ('anki-cards',          'peter209393/anki-card-skills', 4, '卡组生成，与本域卡组排程同构', '⚠️ 需 API Key'),
   ('anything-to-course',  'lowwwbank/anything-to-course', 3, '材料 → 课程，可做系统复习', ''),
 ],
 'S5': [
   ('academic-research-skills', 'Imbad0202/academic-research-skills', 4, '研究写作全链路，覆盖面最广', '⚠️ 许可证：仓库未声明，包内原判 CC-BY-NC，须按最保守处置'),
   ('academic-pptx-skill',      'Gabberflast/academic-pptx-skill',    4, '学术汇报 PPT，零脚本', ''),
   ('claude-latex-skill',       'hameefy/claude-latex-skill',         3, 'LaTeX 排版，论文/公式场景', '⚠️ 5 个月未更新'),
   ('paper-tutor-skills',       'cabbage2000-lab/paper-tutor-skills', 3, '中文科研写作套件，选题→成文', '⛔ 许可证未声明'),
 ],
 'S6': [
   ('ielts',        'YANZHANLIN/ielts-claude-skills', 5, '雅思四科，直接对应四六级/留学语言需求', '完整版 v3 为付费'),
   ('english-coach', 'tianmind-studio/english-coach', 4, '英语口语陪练，中文场景友好', ''),
   ('education-skills', 'flysheep-ai/education-skills', 3, '中文教育 skill 集合，语言类可挑', ''),
 ],
 'F1': [
   ('googleworkspace/cli', 'googleworkspace/cli', 3, '通用办公自动化（日历/任务/文档）', '⚠️ 非校务系统，仅做通用替代'),
   ('canvas-mcp',          'vishalsachdev/canvas-mcp', 3, '教学平台事务（作业/公告）', '⚠️ 仅 Canvas LMS'),
 ],
 'F2': [
   ('deep-work',    'alirezarezvani/claude-skills', 4, '深度工作法，与专注块同构', '⚠️ 仓库含大量无关 skill，只取单个'),
   ('habit-tracker', 'eddiebelaval/squire', 3, '习惯打卡', '⚠️ 密钥可能明文落盘，用前读源码'),
   ('pomodoro',     'jakedahn/pomodoro', 3, '番茄钟', '⚠️ 停滞 11 个月；二进制仅 macOS ARM'),
 ],
 'F3': [],
 'F4': [],
 'F5': [],
 'F6': [],
 'F7': [
   ('SOP_Consultant', 'Haadhi76/SOP_Consultant', 4, '文书结构咨询，与 F7 文书只给结构一致', ''),
   ('10xcolleges',    'tydev-new/10xcolleges',   3, '美国选校侧，仅作信息参考', '⚠️ 海外口径，与国内保研/考研不同'),
   ('paper-tutor-skills', 'cabbage2000-lab/paper-tutor-skills', 2, '科研路径规划可借', '⛔ 许可证未声明'),
 ],
 'F8': [
   ('ResumeSkills',  'Paramchoudhary/ResumeSkills',   5, '26 个简历/面试 skill，实测全部装通', ''),
   ('interview-prep', 'sourikduttanyu/interview-prep', 3, '面试题库', '⚠️ 0★，内容量小'),
 ],
 'R1': [
   ('literature-downloader-skill', 'Lucaswangzcx/literature-downloader-skill', 5, '中文、检索 + 合法全文获取，正中本域', ''),
   ('zotero-skills',  'WenyuChiou/zotero-skills', 5, 'Zotero 工作流，文献管理主线', ''),
   ('paper-tutor-skills', 'cabbage2000-lab/paper-tutor-skills', 4, '中文研究生选题→检索→成文', '⛔ 许可证未声明'),
   ('papers-skill',   'xwmxcz/papers-skill', 3, '轻量检索', '⚠️ 1★，代码量仅 10KB'),
   ('citation-styles', 'wentorai/Research-Claw', 3, '引用格式', '⚠️ 原标 MIT，实测 GitHub API 为「未声明」，已改判'),
 ],
 'R2': [
   ('scientific-agent-skills', 'K-Dense-AI/scientific-agent-skills', 4, '学科科研 skill 大合集，覆盖广', '⚠️ 仓库 472MB，安装慢'),
   ('scientific-agents',       'K-Dense-AI/scientific-agents',       4, '科研推理 AGENTS 画像，方法侧补充', ''),
   ('jupyter-notebook',        'openai/skills',                      3, 'Notebook 工作流', '⚠️ 仓库根目录未声明总许可证，原表仓库名有误已修正'),
 ],
 'R3': [
   ('superpowers',  'obra/superpowers', 3, '工程方法论底座（TDD/调试/评审）', '⚠️ 面向软件开发，非科研专用'),
   ('teach',        'mattpocock/skills', 3, '工程教学法，可做代码学习引导', ''),
   ('python-tutor', 'egouilliard-leyton/python-tutor-skill', 3, 'Python 教学', '⚠️ 1★；无标准 SKILL.md，需手动装'),
 ],
 'R4': [
   ('academic-research-skills', 'Imbad0202/academic-research-skills', 4, '投稿全链路（匹配/返修）', '⚠️ 许可证须按最保守处置；需 API Key'),
   ('paper-tutor-skills',       'cabbage2000-lab/paper-tutor-skills', 3, '中文投稿辅导', '⛔ 许可证未声明'),
   ('academic-pptx-skill',      'Gabberflast/academic-pptx-skill',    3, '会议汇报 PPT', ''),
 ],
 'R5': [
   ('write-concisely', 'NeoLabHQ/context-engineering-kit', 3, '写作规范侧，可做表达自查', '⚠️ GPL-3.0：只可外部调用，禁止摘录'),
 ],
}

# ------------------------------------------------------------------ DUT 落地适配（人工判定）
# 键 (did, skill) -> (dut 0-5, 理由)
# 「场景适配」问的是"这 skill 干不干这事"；「DUT 适配」问的是
# "DUT 本科新生的真实环境（中文语境 / 超星·雨课堂·自建教务 / 国内升学与校招 / 无 Google 账号）
#   下这东西用得上吗"。两者常不一致 —— 后者才是"适配大学生活吗"的答案。
# 未列出的候选默认 dut = adapt。
DUT_FIT = {
 ('F1', 'googleworkspace/cli'):     (1, 'Google 生态：DUT 学生无 Google 账号/校园 Gmail，日历-文档链路在国内校园跑不通'),
 ('F1', 'canvas-mcp'):              (1, 'Canvas LMS：DUT 用超星学习通 / 雨课堂 / 自建教务，平台错位'),
 ('S3', 'canvas-mcp'):              (1, '同上：与 DUT 作业提交平台不同，无法直连'),
 ('S3', 'document-skills'):         (3, 'docx/pdf 处理通用，但只是底层工具，不解作业场景'),
 ('S3', 'paper-writer'):            (3, '本地 pandoc 出骨架，可用；非 DUT 专用模板'),
 ('F7', 'SOP_Consultant'):          (2, 'SOP 为北美研究生申请文书；DUT 主流路径是保研/考研，文书形态不同'),
 ('F7', '10xcolleges'):             (1, '美国选校数据，与国内升学体系无交集'),
 ('F7', 'paper-tutor-skills'):      (2, '面向研究生科研；本科新生路径规划用不上（且许可证未声明）'),
 ('S5', 'paper-tutor-skills'):      (2, '同上'),
 ('R4', 'paper-tutor-skills'):      (2, '同上'),
 ('R1', 'paper-tutor-skills'):      (2, '研究生向；本科新生文献需求靠库内 lit-map 已够'),
 ('R1', 'citation-styles'):         (3, '引用格式通用，但中文 GB/T 7714 需自配'),
 ('R1', 'papers-skill'):            (3, '轻量检索；中文库（知网/万方）覆盖弱'),
 ('R2', 'scientific-agent-skills'): (3, '偏生物信息/计算化学；本科基础实验课用不上'),
 ('R2', 'scientific-agents'):       (3, '同上'),
 ('R2', 'jupyter-notebook'):        (3, 'Notebook 通用；非 DUT 实验台配置'),
 ('R3', 'superpowers'):             (2, '软件开发方法论（TDD/评审），不是科研工具链'),
 ('S4', 'anki-cards'):              (3, '需 API Key；DUT 学生更常用手动 Anki / 纸质卡'),
 ('S4', 'anything-to-course'):      (3, '英文材料 → 课程；中文教材支持需自试'),
 ('S2', 'youtube-notetaker'):       (2, '英文 YouTube 课程场景；DUT 主要用中文录播/雨课堂回放'),
 ('S2', 'lecture-to-study-guide'):  (2, 'IB/IGCSE 课堂语境，与大学课堂材料形态不同'),
 ('S2', 'anything-to-course'):      (3, '通用材料转换，中文可用'),
 ('S5', 'claude-latex-skill'):      (3, 'DUT 课程作业/报告多为 Word；理工科毕业论文 LaTeX 有用'),
 ('S5', 'academic-research-skills'):(2, '英文科研写作链路 + 需 API Key，本科新生阶段偏重'),
 ('R4', 'academic-research-skills'):(2, '同上'),
 ('F8', 'ResumeSkills'):            (3, '北美求职语境（英文简历/ATS）；DUT 校招走中文简历 + 国内流程'),
 ('F8', 'interview-prep'):          (2, '0★、题库偏海外技术面，与国内校招面试差异大'),
 ('R4', 'academic-pptx-skill'):     (3, '学术汇报 PPT 通用；中文模板与答辩要求需自建'),
 ('S5', 'academic-pptx-skill'):     (3, '同上'),
 ('S6', 'ielts'):                   (4, '雅思为主；四六级需自行裁剪，但语言训练骨架可直接用'),
 ('S6', 'education-skills'):        (3, '中文教育集合，需挑拣后使用'),
 ('R1', 'literature-downloader-skill'): (5, '中文、检索 + 合法全文获取，与 DUT 知网/万方环境一致'),
 ('R1', 'zotero-skills'):           (5, 'Zotero 是国内高校主流文献管理工具'),
 ('S4', 'structured-learning'):     (4, '中文、已实测装通'),
 ('S4', 'learn-faster-kit'):        (4, '中文友好，学习法通用'),
 ('S1', 'socrates-skill'):          (4, '引导式教学与「不直接抛答案」同构；指令为英文，需接受'),
 ('S2', 'tutor-skills'):            (4, 'PDF/文档 → 结构化笔记，材料形态通用'),
 ('S2', 'obsidian-skills'):         (4, 'Obsidian 在国内学生中普及度高，零依赖'),
 ('S2', 'mindmap'):                 (4, '概念图产出与语言无关'),
 ('F2', 'deep-work'):               (4, '专注法通用，无地域依赖'),
 ('F2', 'habit-tracker'):           (2, '密钥可能明文落盘；打卡类也可用手机自带工具'),
 ('F2', 'pomodoro'):                (2, '二进制仅 macOS ARM；Windows 用户用不了'),
 ('S1', 'teach'):                   (2, '工程向教学法（TDD/PR 流程），与大学课程答疑场景错位'),
 ('R3', 'teach'):                   (4, '工程教学法用于代码学习引导，场景吻合'),
 ('S1', 'chem-skill'):              (3, '化学专项；非化学专业用不上，且已 9 个月未更新'),
 ('S1', 'math-skill'):              (3, '数学专项贴合 DUT 高数/线代，但许可证缺失不可用'),
 ('S1', 'gurukul-ai'):              (1, '面向 Grade 7 中学教育，与大学完全错位'),
 ('S1', 'tutor-skills'):            (3, '偏材料整理，题目讲解仍靠库内'),
 ('R3', 'python-tutor'):            (3, 'Python 教学；1★、无标准 SKILL.md'),
 ('R3', 'superpowers'):             (2, '同前：软件开发方法论'),
 ('R5', 'write-concisely'):         (3, '写作规范通用；GPL 只能外部调用'),
}

# ------------------------------------------------------------------ 评分
LOOSE = {'MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'CC0-1.0', 'ISC', 'MPL-2.0'}
NONCOMM = {'CC-BY-NC-4.0', 'CC-BY-NC-SA-4.0'}
COPYLEFT = {'GPL-3.0', 'GPL-2.0', 'AGPL-3.0', 'LGPL-3.0'}

# 评分权重：**适配优先**（本包明确不信「唯星数论」，见 skill-sources.md 关键结论）
W_COMPAT, W_USABLE, W_COMMUNITY, W_FIT = 0.25, 0.15, 0.15, 0.45
WEIGHTS_TXT = '0.25×合规 + 0.15×可用 + 0.15×社区 + **0.45×适配**'

def days_stale(push):
    y, m, d = (int(x) for x in push.split('-'))
    return (REF_DATE - datetime.date(y, m, d)).days

def score(repo, adapt):
    stars, lic, push, size, flags = META[repo]
    if lic in LOOSE:      g = 5
    elif lic in COPYLEFT: g = 2
    elif lic in NONCOMM:  g = 2
    else:                 g = 0                      # NOASSERTION / 无 LICENSE
    if 'arch' in flags:
        a = 0
    else:
        a = 5
        if days_stale(push) > STALE_DAYS: a -= 2
        if 'key' in flags: a -= 2
        if 'big' in flags: a -= 1
        a = max(0, a)
    c = 5 if stars >= 100000 else 4 if stars >= 10000 else 3 if stars >= 1000 \
        else 2 if stars >= 100 else 1 if stars >= 10 else 0
    total = round(W_COMPAT * g + W_USABLE * a + W_COMMUNITY * c + W_FIT * adapt, 2)
    return g, a, c, adapt, total

GATE = {0: '⛔ 许可证缺失，不入围', 2: '⚠️ 仅外部调用 / 限非商用'}
LIC_CN = {'NOASSERTION': '未声明', 'NONE': '无 LICENSE'}

def lic_cn(lic):
    return LIC_CN.get(lic, lic)

def verdict(rows):
    """返回 (每行结论列表, 最优解行 or None)
    门禁：合规必须 = 5；且 **DUT 适配 ≥ 3**（否则"能跑但不适配校园"，不能当最优解）。
    同级先比综合分、再比 DUT 适配、最后比星数。
    """
    elig = [r for r in rows if r['g'] == 5 and r['dut'] >= 3]
    best = max(elig, key=lambda r: (r['total'], r['dut'], r['stars'])) if elig else None
    out = []
    for r in rows:
        if r['g'] == 0:                       out.append(GATE[0])
        elif r['g'] == 2:                     out.append(GATE[2])
        elif r['dut'] < 3:                    out.append('⚠️ **不适配 DUT**（场景搭但环境错位）')
        elif r is best:                       out.append('✅ **最优解**')
        else:                                 out.append('备选')
    return out, best

MISS_NOTE = {
 'F3': ('情绪/心理支持', '心理支持类 skill 有**临床风险**，开源社区无可信实现；'
        '已复核 `GarethManning/education-agent-skills`（817★）——**教师侧**教学技能，非学生心理支持，适配度 0；'
        '故本域**只走库内自建 skill**，并强制危机转介红线。'),
 'F4': ('个人财务/反诈', '检索 `claude skill finance|budget|scam` 返回的均为 **awesome-list 清单**或通用 AI 助手，'
        '非可执行 skill；且理财建议涉合规风险，**不引入外部依赖**。'),
 'F5': ('健康/就医', '`AgenticHealthAI` 等为**清单仓库**（无声明许可证）；临床类 skill 存在诊断越界风险，'
        '本域坚持「不给诊断、只给路径」的库内实现。'),
 'F6': ('军训/志愿', '垂类过窄，12 平台均无对应实现（检索 total 中有效命中 0）；'
        '本域为**纯自建域**。'),
 'R5': ('学术诚信/AI 声明', '诚信类 skill 存在「帮规避查重」的**反向风险**，开源实现不可信；'
        '故除下方 GPL 候选（仅外部调用）外，全部走库内自建。'),
}

# ------------------------------------------------------------------ 产物
HEAD = '''# {did} · {dname} — 库外 skill 候选（多源比对 v3）

> **使用规则**：先确认库内 skill 不能满足需求，再读本表。**库内优先是硬规则**（见 `SKILL.md` 硬规则 1）。
> **数据来源**：GitHub API 实抓 **2026-10-02**（stars / license / pushed_at / archived / size）；
> 平台侧复核见 `references/skill-sources.md`，全量矩阵见 `references/skill-matrix-v3.md`。
> **摘录红线**：**GPL-3.0 / AGPL / CC-BY-NC / 无 LICENSE** 一律**只做外部调用，不得复制内容进本包**。

## 一、候选比对（按综合分降序）

> **两个「适配」不一样**：
> **场景适配** = 这个 skill 干不干这件事；**DUT 适配** = 在 DUT 本科新生的真实环境
> （中文语境 / 超星·雨课堂·自建教务 / 国内升学与校招 / 无 Google 账号 / Windows 为主）里用不用得上。
> **只有 DUT 适配 ≥ 3 的候选才有资格当最优解。**

| # | 候选 | 仓库 | ★ | 许可证 | 最近推送 | 合规 | 可用 | 社区 | 场景适配 | DUT 适配 | 综合分 | 结论 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
'''

SCORE_SPEC = '''
## 二、评分口径（可复算）

```
合规 = 5（MIT/Apache/BSD/CC0/ISC）  2（GPL/AGPL/LGPL 或 CC-BY-NC）  0（无 LICENSE / API 未识别）
可用 = 5 基准；已归档 → 0；最近推送 > 180 天 −2；需 API Key/联网 −2；仓库 > 100MB −1（下限 0）
社区 = 5（★≥100k）4（★≥10k）3（★≥1k）2（★≥100）1（★≥10）0（★<10）
适配 = 0–5，**人工判定**：是否直接覆盖本域核心动作（逐条理由见 §1.1）
DUT适配 = 0–5，**人工判定**：在 DUT 本科新生真实环境是否可用（中文/超星·雨课堂/国内升学与校招/无 Google 账号/Windows）
         （逐条理由见 §1.2；未特别标注者默认与「场景适配」同值）

综合分 = {W}   （满分 5.00）
并列时先比「适配」、再比星数（**适配优先** —— 本包不采信「唯星数论」，见 `skill-sources.md` 关键结论）
基准日 = 2026-10-02 ｜ 陈旧阈值 = 180 天
```

**门禁**：`合规 = 0` 的候选**不得**作为最优解（许可证缺失 → 禁止摘录、禁止再分发）；`合规 = 2` 只能外部调用。
'''


def build_external(did, slug, dname, first, second):
    rowsk = []
    for (skill, repo, adapt, reason, note) in CAND[did]:
        g, a, c, ad, total = score(repo, adapt)
        dut, dut_reason = DUT_FIT.get((did, skill), (ad, '与「场景适配」同值（未发现环境错位）'))
        rowsk.append(dict(skill=skill, repo=repo, adapt=ad, reason=reason, note=note,
                          dut=dut, dut_reason=dut_reason,
                          g=g, a=a, c=c, total=total, stars=META[repo][0],
                          lic=META[repo][1], push=META[repo][2]))
    rowsk.sort(key=lambda r: (-r['total'], -r['dut'], -r['stars']))
    verdicts, best = verdict(rowsk)

    s = HEAD.format(did=did, dname=dname)
    for i, r in enumerate(rowsk, 1):
        s += '| %d | `%s` | `%s` | %d | %s | %s | %d | %d | %d | %d | %d | **%.2f** | %s |\n' % (
            i, r['skill'], r['repo'], r['stars'], lic_cn(r['lic']), r['push'],
            r['g'], r['a'], r['c'], r['adapt'], r['dut'], r['total'], verdicts[i - 1])
    s += SCORE_SPEC.format(W=WEIGHTS_TXT)
    s += '\n### 1.1 场景适配逐条理由\n\n| 候选 | 场景适配 | 理由 | 备注 |\n|---|---|---|---|\n'
    for r in rowsk:
        s += '| `%s` | %d | %s | %s |\n' % (r['skill'], r['adapt'], r['reason'], r['note'] or '—')
    s += '\n### 1.2 DUT 落地评估\n\n'
    weak = [r for r in rowsk if r['dut'] < 3]
    s += ('**本域无「场景搭但环境错位」的候选。**\n\n' if not weak else '')
    if weak:
        s += '| 候选 | DUT 适配 | 环境错位点 |\n|---|---|---|\n'
        for r in weak:
            s += '| `%s` | %d | %s |\n' % (r['skill'], r['dut'], r['dut_reason'])
        s += '\n> 这些候选**不得作为最优解**：能跑通，但在大工的真实环境里用不上或不合规。\n\n'

    # ---- 最优解
    s += '\n## 三、最优解\n\n'
    if best:
        s += ('**库外首选：`%s`（`%s`）** —— 综合分 %.2f ｜ DUT 适配 %d/5，%s。\n\n'
              % (best['skill'], best['repo'], best['total'], best['dut'], best['dut_reason']))
        s += ('> 但**首选仍是库内**：`%s` / `%s` 零安装、零外发、红线已内置。'
              '只有库内不覆盖该细分场景时才动库外。\n\n' % (first, second))
    else:
        s += ('**无合规且适配 DUT 的库外首选** —— 本域不存在「许可证清楚 + 场景适配 + 环境可用」三满足的候选。\n\n'
              '**结论：本域只用库内 `%s` / `%s`。**\n\n' % (first, second))

    # ---- 不选与理由
    rejects = [r for r in rowsk if r['g'] == 0]
    if rejects:
        s += '### 3.1 明确排除\n\n'
        for r in rejects:
            s += ('- ⛔ `%s`（`%s`）：**许可证缺失/未声明** → 禁止摘录、禁止再分发，仅可本地自用。%s\n'
                  % (r['skill'], r['repo'], r['note']))
        s += '\n'
    if did in MISS_NOTE:
        head, txt = MISS_NOTE[did]
        s += '### 3.2 方向空白的复核说明\n\n%s\n\n' % txt

    # ---- 降级链
    chain = ['库内 `%s`' % first, '库内 `%s`' % second]
    if best:
        chain.append('库外 `%s`（`%s`）' % (best['skill'], best['repo']))
    chain.append('纯提示词模式（标注 `[已降级]`）')
    s += '## 四、降级链\n\n' + ' → '.join(chain) + '\n\n'
    s += '> 触发条件见 `library/output-spec.md` §2.1；降级时输出**首行**必须带 `[已降级: 原 → 备]`。\n\n'

    # ---- 合规提醒（去重：已在 §3.1 排除项 / §1.2 环境错位项 中的不再重复）
    warns = [r for r in rowsk if r['note'] and r['g'] != 0 and r['dut'] >= 3]
    if warns:
        s += '## 五、合规与风险提醒\n\n'
        for r in warns:
            s += '- **`%s`**（`%s`）：%s\n' % (r['skill'], r['repo'], r['note'])
        s += '\n'
    s += '> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`。\n'
    return s, rowsk, best


def main():
    allrows = {}
    for did, (slug, dname, first, second) in DOMAINS.items():
        txt, rowsk, best = build_external(did, slug, dname, first, second)
        p = os.path.join(ROOT, 'domains', slug, 'skills', 'external.md')
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(txt)
        allrows[did] = (rowsk, best, dname, first, second)
        print('  [%s] %d 候选 → 最优解 %s' % (did, len(rowsk), best['skill'] if best else '（无）'))

    # ---------------- 汇总矩阵 ----------------
    m = ['# 库外 Skill 多源比对矩阵 v3',
         '',
         '> 生成：`scripts/_build/build_phase14.py` ｜ 基准日 **2026-10-02**',
         '> 数据：GitHub API 实抓（stars / license / pushed_at / archived / size）+ 12 平台可达性实测',
         '> 评分口径与门禁见各域 `skills/external.md` §二；本表为全量汇总。',
         '',
         '## 一、19 域最优解一览',
         '',
         '| 域 | 名称 | 库外候选数 | 库外最优解（合规 ∩ DUT≥3） | 综合分 | DUT 适配 | 库内首选（永远优先） | 库内备选 |',
         '|---|---|---|---|---|---|---|---|']
    for did, (slug, dname, first, second) in DOMAINS.items():
        rowsk, best, _, _, _ = allrows[did]
        m.append('| `%s` | %s | %d | %s | %s | %s | `%s` | `%s` |' % (
            did, dname, len(rowsk),
            ('`%s`（`%s`）' % (best['skill'], best['repo'])) if best else '**无（纯自建）**',
            ('**%.2f**' % best['total']) if best else '—',
            ('%d' % best['dut']) if best else '—', first, second))

    n_best = sum(1 for v in allrows.values() if v[1])
    n_cand = sum(len(v[0]) for v in allrows.values())
    n_repo = len({r['repo'] for v in allrows.values() for r in v[0]})
    n_block = sum(1 for v in allrows.values() for r in v[0] if r['g'] == 0)
    n_callonly = sum(1 for v in allrows.values() for r in v[0] if r['g'] == 2)
    n_weak = sum(1 for v in allrows.values() for r in v[0] if r['dut'] < 3)
    n_fit5 = sum(1 for v in allrows.values() for r in v[0] if r['dut'] >= 4)
    m += ['',
          '**汇总**：19 域中 **%d 域有合规库外最优解**，**%d 域为纯自建**；'
          '候选行 **%d 条**，涉及 **%d 个仓库**；其中 **%d 条因许可证缺失被排除**、**%d 条仅可外部调用**。'
          % (n_best, 19 - n_best, n_cand, n_repo, n_block, n_callonly),
          '',
          '### 「适配 DUT 大学生活吗」的量化答案',
          '',
          '| 口径 | 条数 | 占候选总数 |',
          '|---|---|---|',
          '| **DUT 适配 ≥ 4**（推荐直接用） | %d | %d%% |' % (n_fit5, round(100 * n_fit5 / n_cand)),
          '| DUT 适配 3（可用，需改造） | %d | %d%% |' % (sum(1 for v in allrows.values() for r in v[0] if r['dut'] == 3), round(100 * sum(1 for v in allrows.values() for r in v[0] if r['dut'] == 3) / n_cand)),
          '| **DUT 适配 ≤ 2（环境错位，不作最优解）** | %d | %d%% |' % (n_weak, round(100 * n_weak / n_cand)),
          '',
          '**结论**：库外候选整体只是「通用底座 + 少量中文垂类」，**真正开箱贴合 DUT 本科新生日常的比例不高**；'
          '大工的适配度主要由**库内 38 个自建 skill + DUT 站点强绑定**承担，库外仅作降级增强。',
          '',
          '### 环境错位清单（DUT ≤ 2，共 %d 条）' % n_weak,
          '',
          '| 域 | 候选 | DUT | 错位点 |',
          '|---|---|---|---|']
    for did, (slug, dname, first, second) in DOMAINS.items():
        for r in allrows[did][0]:
            if r['dut'] < 3:
                m.append('| `%s` | `%s`（`%s`） | %d | %s |' % (did, r['skill'], r['repo'], r['dut'], r['dut_reason']))
    m += ['',
          '## 二、许可证分布（本轮实抓复核）',
          '',
          '| 判定 | 数量 | 处置 |',
          '|---|---|---|',
          '| ✅ 宽松许可（MIT/Apache/BSD/CC0） | %d | 可外部调用，其中经核验的可摘录 |' % sum(1 for v in allrows.values() for r in v[0] if r['g'] == 5),
          '| ⚠️ 强 copyleft / 禁商用 | %d | **只做外部调用，禁止摘录进包** |' % n_callonly,
          '| ⛔ 无 LICENSE / API 未识别 | %d | **禁止摘录、禁止再分发** |' % n_block,
          '',
          '## 三、与 v2.6 相比的修正',
          '',
          '| # | v2.6 原判 | 本轮实测 | 处置 |',
          '|---|---|---|---|',
          '| 1 | `wentorai/Research-Claw` 标 MIT ✅ | GitHub API 返回 **未声明**（NOASSERTION） | 改判「许可证未声明」，降权并标注 |',
          '| 2 | `Imbad0202/academic-research-skills` 标 CC-BY-NC 4.0 | GitHub API 返回 **未声明** | 按**最保守**处置（视同禁商用 + 禁摘录） |',
          '| 3 | `anthropics/skills` 标 Apache-2.0(子目录) | 仓库**根目录**未声明总许可证 | 标注「子目录许可，根目录未声明」 |',
          '| 4 | R2 候选仓库名写作 `openai`，许可证「未查到」却判 ✅ 合法 | 实为 **`openai/skills`**（27,841★），根目录未声明 | **修正仓库名**，合规改判为 0（不入围） |',
          '| 5 | `GlacierXiaowei` 安装命令写作 `structured-learning` | 实际仓库名 `structured-learning-skill` | 修正安装命令 |',
          '| 6 | 教育垂类「只有 mattpocock/teach 入榜」 | 新发现 `bevibing/tutor-skills` 1,313★、`GarethManning/education-agent-skills` 817★、`bevibing/socrates-skill` 326★、`Lucaswangzcx/literature-downloader-skill` 230★ | **结论过时**，已补入候选表 |',
          '',
          '## 四、新增收录（v2.6 未收录）',
          '',
          '| 仓库 | ★ | 许可证 | 收录域 |',
          '|---|---|---|---|']
    NEW = [('bevibing/socrates-skill', 'S1'), ('bevibing/tutor-skills', 'S2'),
           ('vishalsachdev/canvas-mcp', 'S3 · F1'), ('Lucaswangzcx/literature-downloader-skill', 'R1'),
           ('WenyuChiou/zotero-skills', 'R1'), ('cabbage2000-lab/paper-tutor-skills', 'R1 · S5 · R4'),
           ('lowwwbank/anything-to-course', 'S2 · S4'), ('flysheep-ai/education-skills', 'S6'),
           ('obra/superpowers', 'R3'), ('K-Dense-AI/scientific-agents', 'R2'),
           ('openai/skills', 'R2')]
    for r, d in NEW:
        if r in META:
            m.append('| `%s` | %d | %s | %s |' % (r, META[r][0], META[r][1], d))
    m += ['',
          '## 五、方法论（下一轮沿用）',
          '',
          '1. **先过门禁再看分**：许可证不清 → 直接出局，评分不参与排序。',
          '2. **适配度权重最高（0.35）**：星多但场景不搭的（如通用办公套件之于校务）不给高分。',
          '3. **库内优先不可动摇**：库外仅在「库内不覆盖该细分场景」时启用，且必须走降级链。',
          '4. **平台可达性也是事实**：12 平台中本机实测仅 4 个可达（见 `skill-sources.md`），'
          '故「多源比对」以 **GitHub API 可核验数据**为主干，平台侧作为发现渠道。',
          '']
    with open(os.path.join(ROOT, 'references', 'skill-matrix-v3.md'), 'w',
              encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(m))
    print('\n生成 references/skill-matrix-v3.md')

    # ---------------- 回写 domains/_registry.md 的「库外候选数」列 ----------------
    reg_p = os.path.join(ROOT, 'domains', '_registry.md')
    with open(reg_p, 'r', encoding='utf-8') as f:
        reg = f.read()
    reg0 = reg
    for did in DOMAINS:
        n = len(allrows[did][0])
        reg = re.sub(r'(\|\s*`' + did + r'`\s*\|[^|]*\|[^|]*\|[^|]*\|\s*)\d+(\s*\|)',
                     lambda m: m.group(1) + str(n) + m.group(2), reg)
    if reg != reg0:
        with open(reg_p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(reg)
        print('已同步 _registry.md 的库外候选数（19 域）')
    print('汇总：%d 域有库外最优解 / 19；候选 %d 条 / %d 仓库' % (n_best, n_cand, n_repo))


if __name__ == '__main__':
    main()
