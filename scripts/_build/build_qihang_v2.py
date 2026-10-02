#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」学伴包 v2.0 —— 三级结构生成器
结构：skill库(1级) → 域(2级) → skill(3级)
改域只需改本文件 DOMAINS，再跑一次即可整体重建。
用法: python build_qihang_v2.py <输出目录>

⚠️ 重跑会覆盖 references/dlut-login-sites.md（该文件已手工增补 §0.1 Profile 隔离
   与 §0.2 实测记录）。如无必要不要重跑；确需重跑，请先备份该文件。
   生成顺序应为: build_qihang_v2.py → build_qihang_v2_extras.py → build_phase1.py
"""
import os, sys, shutil, json

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack"

# ============================================================
# 方向自查结果：19 个域（S 学习 6 / F 生活 8 / R 科研 5）
# ============================================================
CATS = {
    "S": ("学习类", "课程、课堂、作业、备考、表达、语言"),
    "F": ("生活类", "事务、作息、身心、财务、健康、军政、升学、求职"),
    "R": ("科研类", "文献、实验、工具、产出、规范"),
}

DOMAINS = [
    # ---------------- S 学习类 ----------------
    dict(id="S1", cat="S", name="课程答疑", slug="course-qa",
         triggers=["讲一下", "这题", "为什么", "推导", "证明", "不会做", "求", "解释一下"],
         scope_in="单点题目/概念的分步讲解、错因诊断、举一反三",
         scope_out="不代写作业（→S3）；不做整门课备考规划（→S4）",
         local=dict(slug="explain-stepwise", name="分步讲解", mode="自建",
                    desc="先让学习者自己写一步，再按「定位卡点 → 给提示 → 给解法 → 出同类题」四步走，不直接抛答案。",
                    steps=["复述题目并确认理解（防理解偏差）",
                           "要求学习者先写出自己想到的第一步",
                           "定位卡点：概念不清 / 方法不会 / 计算失误（三者处理方式不同）",
                           "给一句关键提示（不是答案）",
                           "给完整解法，标出每一步依据",
                           "出 1 道同类题并留白，不代做"]),
         external=[("teach", "mattpocock/skills", "npx skills add mattpocock/skills@teach"),
                   ("math-skill", "googlarz/math-skill", "npx skills add googlarz/math-skill"),
                   ("gurukul-ai", "somenssarkar/gurukul-ai", "手动 clone（需 API Key）"),
                   ("chem-skill", "ghutchis/chem-skill", "手动 zip（纯本地）")],
         dut_public=["教务处 https://teach.dlut.edu.cn/", "数学科学学院 https://math.dlut.edu.cn/"],
         dut_private=["综合教务系统 http://jxgl.dlut.edu.cn/（考试安排、培养方案）"]),

    dict(id="S2", cat="S", name="课堂与笔记", slug="lecture-notes",
         triggers=["笔记", "讲义", "录音", "整理", "概念图", "思维导图", "听课", "这节课"],
         scope_in="课堂材料 → 结构化笔记 / 概念图 / 知识库沉淀",
         scope_out="不做题目讲解（→S1）；不写实验报告（→S3）",
         local=dict(slug="lecture-to-notes", name="讲义转笔记", mode="摘录+自建",
                    desc="把讲义/录音/PPT 压成「5–8 条核心 + 概念图 + 3 个自测题」，并标注未理解点供下次复考。",
                    steps=["判断材料类型（讲义 / 录音 / 视频 / 板书照片）",
                           "抽取 5–8 条核心结论（带出处页码或时间戳）",
                           "生成概念图（层级：章 → 节 → 关键概念）",
                           "生成 3 个可自测问题（覆盖最高频考点）",
                           "标注 1–2 处未理解点，写入学习档案",
                           "给出笔记文件落点"]),
         external=[("lecture-to-study-guide", "Jellypod-Inc/school-skills", "/plugin marketplace add Jellypod-Inc/school-skills"),
                   ("obsidian-skills", "kepano/obsidian-skills", "/plugin marketplace add kepano/obsidian-skills"),
                   ("mindmap", "0x-man/mindmap-skill", "npx skills add 0x-man/mindmap-skill"),
                   ("youtube-notetaker", "dair-ai/dair-academy-plugins", "/plugin marketplace add dair-ai/dair-academy-plugins")],
         dut_public=["图书馆 https://lib.dlut.edu.cn/"],
         dut_private=["数字书院（超星）https://dlutzqsy.mh.chaoxing.com/",
                      "大工金课平台 https://dlut.fanya.chaoxing.com/",
                      "雨课堂 https://www.yuketang.cn/"]),

    dict(id="S3", cat="S", name="作业与考核", slug="assignment",
         triggers=["作业", "实验报告", "课程设计", "平时分", "大作业", "论文作业", "提交"],
         scope_in="作业规划、实验报告结构、课程设计拆解、格式规范",
         scope_out="不代写（只给结构与自查）；不投期刊（→R4）",
         local=dict(slug="lab-report", name="实验报告脚手架", mode="自建",
                    desc="按 IMRAD 给实验报告骨架，分配各节字数，并给出自查清单；正文由学生自己写。",
                    steps=["确认实验名称、目的、数据是否齐备",
                           "按 IMRAD 出骨架：引言 / 方法 / 结果 / 讨论 / 结论",
                           "分配各节字数（如 300/400/500/500/200）",
                           "标记必须由本人完成的部分（数据处理、结论）",
                           "给出格式自查清单（单位、有效数字、图表编号、引用）",
                           "输出 Markdown / docx 落点"]),
         external=[("paper-writer", "kgraph57/paper-writer-skill", "npx skills add kgraph57/paper-writer-skill"),
                   ("document-skills", "anthropics/skills", "/plugin marketplace add anthropics/skills")],
         dut_public=["教务处 https://teach.dlut.edu.cn/"],
         dut_private=["综合教务系统 http://jxgl.dlut.edu.cn/（作业与成绩）"]),

    dict(id="S4", cat="S", name="备考与记忆", slug="exam-prep",
         triggers=["考试", "复习", "背诵", "突击", "卡组", "刷题", "期末", "期中", "四六级"],
         scope_in="考前冲刺规划、间隔重复、卡组生成、模拟卷",
         scope_out="不做单题讲解（→S1）；不写课程论文（→S5）",
         local=dict(slug="exam-sprint", name="考前冲刺排程", mode="摘录+自建",
                    desc="先要三件事（科目章节 / 剩余天数 / 要计划还是卡组），再出 3 步突击或 7 步系统两档方案，结束真出题判分。",
                    steps=["澄清三项：科目与章节 / 距考几天 / 要计划还是卡组",
                           "选档位：≤7 天走 3 步突击；>7 天走 7 步系统",
                           "按剩余天数倒排到每日 ≤2 个番茄钟",
                           "生成卡组或错题清单（标注上次错因）",
                           "安排 1 次限时模拟 + 1 次纯错题复盘",
                           "输出任务清单落点"]),
         external=[("structured-learning", "GlacierXiaowei/structured-learning-skill", "npx skills add glacierxiaowei/structured-learning"),
                   ("anki-cards", "peter209393/anki-card-skills", "手动 install.sh（需 API Key）"),
                   ("learn-faster-kit", "hluaguo/learn-faster-kit", "npx skills add hluaguo/learn-faster-kit")],
         dut_public=["教学运行保障中心 https://jxyxbzzx.dlut.edu.cn/（考试安排）",
                     "图书馆 https://lib.dlut.edu.cn/（自习）"],
         dut_private=["综合教务系统考试安排", "i大工 APP 场馆预约（仅 APP）"]),

    dict(id="S5", cat="S", name="学术表达", slug="academic-writing",
         triggers=["论文", "综述", "答辩", "PPT", "引用", "文献综述", "开题", "结题"],
         scope_in="课程论文 / 综述 / 答辩展示的结构、引用规范、预审",
         scope_out="不做文献检索管理（→R1）；不投稿（→R4）",
         local=dict(slug="paper-outline", name="论文骨架与预审", mode="自建",
                    desc="给结构大纲 + 各节字数 + 论证链自查 + 3 条改进建议，再做一次「审稿人视角」预审。",
                    steps=["明确类型（课程论文 / 综述 / 报告）与字数",
                           "出结构大纲并分配字数",
                           "检查论证链：每节是否有主张 → 证据 → 推理",
                           "跑一次模拟审稿（挑 3 个最可能被质疑的点）",
                           "给引用格式规范（GB/T 7714 或 APA）",
                           "输出文件落点"]),
         external=[("academic-research-skills", "Imbad0202/academic-research-skills", "/plugin marketplace add Imbad0202/academic-research-skills"),
                   ("academic-pptx-skill", "Gabberflast/academic-pptx-skill", "手动上传 claude.ai"),
                   ("claude-latex-skill", "hameefy/claude-latex-skill", "npx skills add hameefy/claude-latex-skill")],
         dut_public=["图书馆 https://lib.dlut.edu.cn/"],
         dut_private=["图书馆电子资源校外访问 https://lib.dlut.edu.cn/wxzy1/xwfw.htm"]),

    dict(id="S6", cat="S", name="语言能力", slug="language",
         triggers=["英语", "四六级", "雅思", "托福", "口语", "翻译", "单词", "作文批改"],
         scope_in="英语/第二外语的词汇、语法、写作批改、口语、翻译",
         scope_out="不做学术论文写作（→S5）",
         local=dict(slug="lang-drill", name="语言训练", mode="自建",
                    desc="先测水平（CEFR 或四六级分数），再出可执行的每日训练计划，写作只标错不重写。",
                    steps=["测水平（CEFR / 四六级 / 雅思分数）",
                           "明确弱项（听 / 说 / 读 / 写 四选一为主攻）",
                           "出每日 ≤30 分钟的最小可行动作",
                           "写作批改规则：标出错误类型 + 给 1 条修改建议，不整篇重写",
                           "设置 1 周后的复测点",
                           "输出训练表落点"]),
         external=[("ielts", "YANZHANLIN/ielts-claude-skills", "手动复制"),
                   ("english-coach", "tianmind-studio/english-coach", "npx skills add tianmind-studio/english-coach")],
         dut_public=["外国语学院 https://fld.dlut.edu.cn/"],
         dut_private=["图书馆电子资源（外文数据库）"]),

    # ---------------- F 生活类 ----------------
    dict(id="F1", cat="F", name="校园事务", slug="campus-affairs",
         triggers=["选课", "学籍", "证明", "一卡通", "报修", "宿舍", "离校", "校园卡", "办事"],
         scope_in="选课、学籍、证明打印、一卡通、报修、公寓、离校等事务办理路径",
         scope_out="不涉及健康（→F5）；不涉及钱（→F4）",
         local=dict(slug="campus-desk", name="校园事务办理台", mode="自建·DUT",
                    desc="先查 DUT 信息库锁定入口与电话，再给「去哪办 / 带什么 / 多久」，查不到就明说未收录。",
                    steps=["查 references/dlut-official-sites.md 锁定入口",
                           "判定线上线下（线上给门户链接，线下给楼宇与电话）",
                           "列出所需材料清单",
                           "给出办理时长与常见卡点",
                           "未收录则固定回复：信息库未收录，建议访问 www.dlut.edu.cn 核实",
                           "输出办理卡片"]),
         external=[("googleworkspace/cli", "googleworkspace/cli", "/plugin marketplace add googleworkspace/cli")],
         dut_public=["校园门户 https://portal.dlut.edu.cn/", "学生工作处 https://xsc.dlut.edu.cn/",
                     "后勤处 https://houqin.dlut.edu.cn/", "保卫处 https://gach.dlut.edu.cn/"],
         dut_private=["一卡通 https://ecard.dlut.edu.cn/", "校园门户办事大厅", "离校系统 http://lx.dlut.edu.cn/"]),

    dict(id="F2", cat="F", name="作息与专注", slug="focus",
         triggers=["拖延", "作息", "专注", "番茄钟", "时间管理", "熬夜", "起不来", "效率"],
         scope_in="作息调整、专注块排布、拖延干预、时间管理",
         scope_out="不做学业规划内容（只在其中嵌入时间安排）",
         local=dict(slug="focus-block", name="专注块排布", mode="自建",
                    desc="先修作息再谈效率；每天只给 1 个最小可行动作（≤15 分钟）与固定专注窗口。",
                    steps=["读取 config.yaml 的 sleep_window",
                           "判断是作息问题还是注意力问题（处理策略不同）",
                           "设定本周唯一目标（只 1 个）",
                           "排每日 1–2 个固定专注块，绑定trigger（如「图书馆坐下后」）",
                           "累计连续天数，断了只记录不评判",
                           "与 D 域备考排程联动"]),
         external=[("deep-work", "alirezarezvani/claude-skills", "/plugin marketplace add alirezarezvani/claude-skills"),
                   ("habit-tracker", "eddiebelaval/squire", "手动 install.sh（需 API Key）"),
                   ("pomodoro", "jakedahn/pomodoro", "npx skills add jakedahn/pomodoro（仅 macOS ARM）")],
         dut_public=["文体场馆中心 https://tycgzx.dlut.edu.cn/"],
         dut_private=["图书馆座位预约（lib.dlut.edu.cn 登录后）"]),

    dict(id="F3", cat="F", name="身心与社交", slug="wellbeing",
         triggers=["焦虑", "压力", "emo", "室友", "社团", "人际", "想家", "孤独", "适应"],
         scope_in="情绪压力疏导、适应问题、宿舍与人际、社团选择",
         scope_out="**不做心理诊断、不做危机干预**；出现自伤/自杀念头立即转介专业资源",
         local=dict(slug="wellbeing-checkin", name="状态check-in", mode="自建",
                    desc="先倾听再给方法；不评判、不诊断；识别危机信号并第一时间转介心理中心。",
                    steps=["先复述情绪，确认被理解（不急着给建议）",
                           "区分：适应问题 / 关系问题 / 情绪低落 / 危机信号",
                           "危机信号（自伤/自杀念头）→ 立即给出心理中心联系方式并建议马上联系",
                           "非危机 → 给 1 个今晚能做的小动作",
                           "给长期支持资源（心理中心、辅导员、社团）",
                           "不记录敏感内容到学习档案"]),
         external=[],
         dut_public=["心理健康教育与咨询中心 https://xinli.dlut.edu.cn/", "校团委 https://tuanwei.dlut.edu.cn/"],
         dut_private=["i大工 APP 心理服务-咨询预约（仅 APP）"]),

    dict(id="F4", cat="F", name="财务与安全", slug="money-safety",
         triggers=["生活费", "奖学金", "助学金", "兼职", "诈骗", "丢卡", "借钱", "花呗"],
         scope_in="生活费规划、奖助学金申请、兼职避坑、防诈骗、安全",
         scope_out="不做投资建议；不处理心理问题（→F3）",
         local=dict(slug="money-guard", name="生活费与防诈守门", mode="自建",
                    desc="先算月度收支缺口，再给节流方案；遇到可疑信息一律先按诈骗流程核验。",
                    steps=["算月度收入（生活费+奖助）与固定支出",
                           "定位缺口或结余，给 1 条节流建议（只 1 条）",
                           "奖助学金：查条件 → 备材料 → 记 DDL",
                           "遇可疑信息：不点链接、不转账、不透露验证码 → 报保卫处",
                           "丢卡/丢证：先挂失（一卡通 + 银行卡）再补办",
                           "输出行动卡"]),
         external=[],
         dut_public=["学生资助（学生处）https://xsc.dlut.edu.cn/", "财务处 http://cw.dlut.edu.cn/",
                     "保卫处 https://gach.dlut.edu.cn/"],
         dut_private=["一卡通 https://ecard.dlut.edu.cn/（余额/流水）",
                      "统一支付 http://pay.dlut.edu.cn/"]),

    dict(id="F5", cat="F", name="健康与运动", slug="health",
         triggers=["生病", "就医", "医保", "锻炼", "饮食", "体检", "运动", "受伤"],
         scope_in="就医路径、医保报销、锻炼计划、作息饮食",
         scope_out="不做医疗诊断；不处理心理（→F3）",
         local=dict(slug="health-guide", name="就医与运动指引", mode="自建·DUT",
                    desc="症状严重直接给就医路径（校医院 → 附属医院）；不诊断，只给流程与运动处方。",
                    steps=["判断是否需要就医（持续/加重/影响生活 → 就医）",
                           "给出就医路径：校医院电话 → 转诊附属医院",
                           "说明医保报销需要留哪些凭证",
                           "运动：按当前体能给每周 3 次的入门处方",
                           "饮食：只给 1 条可执行调整",
                           "不做诊断、不给用药建议"]),
         external=[],
         dut_public=["校医院 84708120（24h）/ 84708990（门诊）",
                     "文体场馆中心 https://tycgzx.dlut.edu.cn/"],
         dut_private=["i大工 APP 场馆/浴室预约（仅 APP）"]),

    dict(id="F6", cat="F", name="军训与志愿", slug="service",
         triggers=["军训", "国防", "志愿", "社会实践", "志愿时长", "第二课堂", "三下乡"],
         scope_in="军训准备与适应、志愿服务与社会实践的项目选择与记录",
         scope_out="不涉及学业（→S 类）；不涉及求职（→F8）",
         local=dict(slug="service-log", name="军训与志愿记录", mode="自建",
                    desc="军训期给体能/物资/防晒准备清单；志愿侧帮选项目并归档时长与收获。",
                    steps=["军训：给物资清单、体能预热、防晒与中暑预防",
                           "军训期作息按 sleep_window 提前 1 周调",
                           "志愿：按兴趣与时长筛选项目类型",
                           "记录服务时长与可迁移收获（写成 3 条经历条目）",
                           "归档到第二课堂/志愿系统",
                           "输出记录表"]),
         external=[],
         dut_public=["学生工作处（武装部）https://xsc.dlut.edu.cn/", "校团委 https://tuanwei.dlut.edu.cn/"],
         dut_private=["智慧学工系统（第二课堂/志愿时长）"]),

    dict(id="F7", cat="F", name="升学深造", slug="further-study",
         triggers=["保研", "考研", "留学", "申博", "导师", "推免", "夏令营", "绩点"],
         scope_in="保研/考研/留学的路径规划、时间线、材料与选校选导师",
         scope_out="不写文书代笔（只给结构与自查）；不求职（→F8）",
         local=dict(slug="grad-plan", name="升学路径规划", mode="自建",
                    desc="先定路径（保研/考研/留学），再倒排时间线，标出每个节点的硬性材料。",
                    steps=["锁定路径：保研（推免）/ 考研 / 留学 / 直博",
                           "查 DUT 对应入口（研究生院 / 国际交流处 / 学院推免章程）",
                           "倒排时间线（大三下 → 大四上，按月）",
                           "列硬性材料清单（成绩单、推荐信、文书、语言成绩）",
                           "文书只给结构与自查，不代写",
                           "输出时间线表"]),
         external=[("SOP_Consultant", "Haadhi76/SOP_Consultant", "npx skills add Haadhi76/SOP_Consultant"),
                   ("10xcolleges", "tydev-new/10xcolleges", "npx skills add tydev-new/10xcolleges")],
         dut_public=["研究生院 https://gs.dlut.edu.cn/", "国际合作与交流处 https://dutdice.dlut.edu.cn/",
                     "研究生招生 https://gs.dlut.edu.cn/yjszs.htm"],
         dut_private=["研究生招生报名系统 https://yjszs.dlut.edu.cn/zsbm"]),

    dict(id="F8", cat="F", name="求职与竞赛", slug="career",
         triggers=["简历", "面试", "实习", "竞赛", "证书", "秋招", "大创", "创新创业"],
         scope_in="简历、面试、实习求职、学科竞赛与创新创业项目",
         scope_out="不做升学规划（→F7）",
         local=dict(slug="career-kit", name="求职竞赛工具箱", mode="自建",
                    desc="按目标岗位/竞赛倒推能力缺口，改简历只做「相关性重构」，面试按 STAR 打磨。",
                    steps=["明确目标（岗位 / 竞赛 / 项目）",
                           "倒推能力缺口，给 2–3 条补齐动作",
                           "简历：只做相关性重构与量化改写，不编造经历",
                           "面试：按 STAR 打磨 3 个高频问题",
                           "竞赛：查 DUT 创新创业学院与学院通知的报名节点",
                           "输出行动清单"]),
         external=[("ResumeSkills", "Paramchoudhary/ResumeSkills", "npx skills add Paramchoudhary/ResumeSkills"),
                   ("interview-prep", "sourikduttanyu/interview-prep", "npx skills add sourikduttanyu/interview-prep")],
         dut_public=["就业信息网 https://job.dlut.edu.cn/", "创新创业学院 https://chuangxin.dlut.edu.cn/"],
         dut_private=["就业系统（宣讲会/投递）"]),

    # ---------------- R 科研类 ----------------
    dict(id="R1", cat="R", name="文献检索与管理", slug="literature",
         triggers=["文献", "综述", "引用", "Zotero", "知网", "参考文献", "查文献", "DOI"],
         scope_in="文献检索式设计、筛选、引文核验、文献管理",
         scope_out="不写论文正文（→S5/R4）",
         local=dict(slug="lit-map", name="文献地图", mode="自建",
                    desc="先出检索式与纳排标准，再按「主题—方法—结论」矩阵整理；每条引文给可核验锚点。",
                    steps=["把研究问题拆成 2–4 个检索概念",
                           "为每个概念出同义词与检索式（中英各一版）",
                           "定纳入/排除标准",
                           "建矩阵：主题 | 方法 | 样本 | 结论 | 局限",
                           "每条引文标注来源与可核验锚点（DOI/页码）",
                           "输出文献矩阵表"]),
         external=[("papers-skill", "xwmxcz/papers-skill", "npx skills add xwmxcz/papers-skill（需联网）"),
                   ("citation-styles", "wentorai/Research-Claw", "npx skills add wentorai/Research-Claw"),
                   ("zotero-skills", "WenyuChiou/zotero-skills", "npx skills add WenyuChiou/zotero-skills")],
         dut_public=["图书馆 https://lib.dlut.edu.cn/"],
         dut_private=["图书馆电子资源校外访问 https://lib.dlut.edu.cn/wxzy1/xwfw.htm"]),

    dict(id="R2", cat="R", name="实验与数据", slug="experiment-data",
         triggers=["实验", "数据", "统计", "显著性", "图表", "误差", "拟合", "样本"],
         scope_in="实验设计、数据处理、统计检验、图表规范",
         scope_out="不写报告结构（→S3）",
         local=dict(slug="data-lab", name="数据实验台", mode="自建",
                    desc="先确认数据与假设，再选检验方法，跑完给出「图 + 一句话结论 + 不能下的结论」。",
                    steps=["确认数据类型（连续/分类）与样本量",
                           "明确要检验的假设",
                           "选检验方法并说明前提（正态性、独立性）",
                           "跑分析，出出版级图表（标注单位与误差棒）",
                           "给一句话结论 + 明确列出不能下的结论",
                           "输出脚本与图表"]),
         external=[("scientific-agent-skills", "K-Dense-AI/scientific-agent-skills", "/plugin marketplace add K-Dense-AI/scientific-agent-skills"),
                   ("jupyter-notebook", "openai", "/plugin marketplace add openai/skills")],
         dut_public=["网络与信息化中心 https://its.dlut.edu.cn/（超算）"],
         dut_private=["超算账号（its 申请）"]),

    dict(id="R3", cat="R", name="科研工具与代码", slug="research-tools",
         triggers=["Python", "MATLAB", "仿真", "Git", "环境", "报错", "脚本", "代码"],
         scope_in="科研编程环境、脚本编写、版本管理、仿真工具",
         scope_out="不做算法题训练（→S1）",
         local=dict(slug="tool-setup", name="科研环境搭建", mode="自建",
                    desc="先问清目标工具与系统，再给最小可用环境步骤；报错按「复现 → 最小化 → 假设 → 验证」处理。",
                    steps=["明确目标工具与操作系统",
                           "给最小可用环境步骤（虚拟环境 + 依赖）",
                           "报错处理：复现 → 最小化 → 假设 → 插桩验证 → 修复",
                           "版本管理：给 .gitignore 与提交规范",
                           "给可复现的目录结构",
                           "输出环境清单与 README"]),
         external=[("teach", "mattpocock/skills", "npx skills add mattpocock/skills@teach"),
                   ("python-tutor", "egouilliard-leyton/python-tutor-skill", "手动 install.sh（无标准 SKILL.md）")],
         dut_public=["网络与信息化中心 https://its.dlut.edu.cn/", "软件学院 https://ss.dlut.edu.cn/"],
         dut_private=["校园软件正版化平台（its 提供）"]),

    dict(id="R4", cat="R", name="学术产出与投稿", slug="publication",
         triggers=["投稿", "期刊", "专利", "会议", "基金", "大创结题", "审稿意见", "返修"],
         scope_in="论文投稿、专利与会议、基金申报、返修回复",
         scope_out="不做出稿前的结构打磨（→S5）",
         local=dict(slug="submit-kit", name="投稿返修工具包", mode="自建",
                    desc="先跑投稿前自检（结构/引用/数据），再给期刊匹配与审稿意见逐条回复表。",
                    steps=["投稿前自检：结构完整性、引用规范、数据可复现",
                           "按主题与方法匹配 3 个候选期刊/会议（含分区与周期）",
                           "列投稿材料清单（Cover Letter、声明、伦理审查）",
                           "返修：逐条拆解审稿意见 → 分类（接受/反驳/补充实验）",
                           "为每条意见写回复草稿 + 修改位置",
                           "输出返修对照表"]),
         external=[("academic-research-skills", "Imbad0202/academic-research-skills", "/plugin marketplace add Imbad0202/academic-research-skills（CC-BY-NC）")],
         dut_public=["科学技术研究院 https://scidep.dlut.edu.cn/", "研究生院 https://gs.dlut.edu.cn/"],
         dut_private=["科研管理系统（项目/成果登记）"]),

    dict(id="R5", cat="R", name="学术规范与伦理", slug="integrity",
         triggers=["查重", "引用规范", "学术诚信", "AI 声明", "数据合规", "署名", "伦理"],
         scope_in="引用规范、查重、学术诚信、AI 使用声明、数据与伦理合规",
         scope_out="不做内容写作（→S5/R4）",
         local=dict(slug="integrity-check", name="规范自检", mode="自建",
                    desc="跑一份合规自查：引用、查重、署名、数据来源、AI 使用声明，逐项给可执行修正。",
                    steps=["引用自查：直接引用是否加引号并标注页码",
                           "查重自查：连续 15 字以上雷同必须改写与引用",
                           "署名自查：贡献者是否都符合署名标准",
                           "数据来源：是否可追溯、是否获授权",
                           "AI 使用声明：按学校与期刊要求撰写",
                           "输出自查表 + 修正清单"]),
         external=[("write-concisely", "NeoLabHQ/context-engineering-kit", "npx skills add NeoLabHQ/context-engineering-kit")],
         dut_public=["研究生院 https://gs.dlut.edu.cn/", "图书馆 https://lib.dlut.edu.cn/"],
         dut_private=["查重系统（图书馆/研究生院入口）"]),
]

# ============================================================
# 模板
# ============================================================
def fm(name, desc, extra=""):
    return f"---\nname: {name}\ndescription: {desc}\n{extra}---\n\n"

def domain_md(d):
    cat_name = CATS[d["cat"]][0]
    lines = []
    lines.append(f"# {d['id']} · {d['name']}\n")
    lines.append(f"> 域 ID `{d['id']}` ｜ 所属大类 **{cat_name}** ｜ 目录 `domains/{d['id']}-{d['slug']}/`\n")
    lines.append("## 域边界\n")
    lines.append(f"- **覆盖**：{d['scope_in']}")
    lines.append(f"- **不覆盖**：{d['scope_out']}\n")
    lines.append("## 触发词（命中任一即锁定本域）\n")
    lines.append("`" + "` ｜ `".join(d["triggers"]) + "`\n")
    lines.append("## 库内 skill（优先使用，无需安装）\n")
    l = d["local"]
    lines.append(f"- **`{l['slug']}`** — {l['name']}（{l['mode']}）")
    lines.append(f"  {l['desc']}\n")
    lines.append("## DUT 绑定点\n")
    lines.append("**公开站（无需登录）**")
    for u in d["dut_public"]:
        lines.append(f"- {u}")
    lines.append("")
    lines.append("**私密站（需登录，见 `references/dlut-login-sites.md`）**")
    if d["dut_private"]:
        for u in d["dut_private"]:
            lines.append(f"- {u}")
    else:
        lines.append("- 本域无强绑定私密站")
    lines.append("")
    lines.append("## 执行顺序\n")
    lines.append(f"1. 1 级库完成**需求明确**（`library/clarity.md`），U ≤ 5% 才继续")
    lines.append(f"2. 1 级库完成**域审查**，确认命中 `{d['id']}`（`library/domain-review.md`）")
    lines.append(f"3. 用**库内 skill** `{l['slug']}` 执行（首选）")
    lines.append(f"4. 库内不满足 → 读 `skills/external.md` 走库外安装")
    lines.append(f"5. 按 `library/output-spec.md` 输出，并写入学习档案")
    lines.append("")
    return "\n".join(lines)

def external_md(d):
    l = d["local"]
    lines = []
    lines.append(f"# {d['id']} · {d['name']} — 库外 skill 候选\n")
    lines.append("> **使用规则**：先确认库内 skill `" + l["slug"] + "` 不能满足需求，再读本表。")
    lines.append("> 安装前三步：① 探测是否已装 ② 读源码与许可证 ③ 装后验证。\n")
    if not d["external"]:
        lines.append("**本域暂无合适的库外 skill** —— 属于方向空白，建议直接用库内 skill 或自建。\n")
        lines.append("> 找新 skill 的入口见 `references/skill-sources.md`（12 个平台）。")
        return "\n".join(lines)
    lines.append("| # | Skill | 仓库 | 安装命令 | 备注 |")
    lines.append("|---|---|---|---|---|")
    for i, (nm, repo, inst) in enumerate(d["external"], 1):
        note = ""
        if "Key" in inst or "API" in inst:
            note = "需 API Key"
        if "linux" in inst or "macOS" in inst:
            note = (note + "；" if note else "") + "平台受限"
        lines.append(f"| {i} | `{nm}` | `{repo}` | `{inst}` | {note} |")
    lines.append("")
    lines.append("**降级链**：库内 skill → 上表第 1 项 → 第 2 项 → 纯提示词模式")
    lines.append("")
    lines.append("> 风险与验收数据见 `references/validation-report.md`")
    return "\n".join(lines)

def local_skill_md(d):
    l = d["local"]
    cat_name = CATS[d["cat"]][0]
    name = f"qihang-{l['slug']}"
    desc = f"「启航」{d['id']} {d['name']}域库内 skill：{l['desc']}"
    out = fm(name, desc.replace("\n", " "), "version: 2.0.0\nlicense: MIT\n")
    out += f"# {l['name']}\n\n"
    out += f"- **归属域**：`{d['id']}` {d['name']}（{cat_name}）\n"
    out += f"- **来源**：{l['mode']}\n"
    out += f"- **定位**：{l['desc']}\n\n"
    out += "## 前置（不可跳过）\n\n"
    out += "1. 1 级库已完成**需求明确**（6 槽位 + 澄清门，U ≤ 5%）\n"
    out += "2. 1 级库已完成**域审查**，确认命中本域\n\n"
    out += f"## 边界\n\n- 覆盖：{d['scope_in']}\n- 不覆盖：{d['scope_out']}\n\n"
    out += "## 执行步骤\n\n"
    for i, s in enumerate(l["steps"], 1):
        out += f"{i}. {s}\n"
    out += "\n## 输出\n\n按 `library/output-spec.md` 模板输出，默认 ≤ 6 条要点。\n\n"
    out += "## DUT 绑定点\n\n"
    for u in d["dut_public"]:
        out += f"- {u}\n"
    if d["dut_private"]:
        out += "\n需登录：\n"
        for u in d["dut_private"]:
            out += f"- {u}\n"
    out += "\n## 失败与降级\n\n库内执行不满足 → 读同目录 `../external.md` 走库外安装；仍失败 → 纯提示词模式并标注 `[已降级]`。\n"
    return out

def registry_md():
    lines = []
    lines.append("# 域总表（Level 2 Registry）\n")
    lines.append(f"> 共 **{len(DOMAINS)} 个域** ｜ 生成自 `scripts/_build/build_qihang_v2.py`\n")
    lines.append("## 锁定规则\n")
    lines.append("1. 1 级库先做**需求明确**（6 槽位 + 澄清门）\n2. 用下表**触发词**匹配锁定域；命中多个 → 走跨域串联\n3. 无域可命中 → 走 `library/domain-review.md` 的兜底流程\n")
    for ck, (cname, cdesc) in CATS.items():
        ds = [d for d in DOMAINS if d["cat"] == ck]
        lines.append(f"\n## {ck} · {cname}（{len(ds)} 域）\n")
        lines.append(f"*{cdesc}*\n")
        lines.append("| 域 ID | 名称 | 触发词 | 库内 skill | 库外候选数 |")
        lines.append("|---|---|---|---|---|")
        for d in ds:
            trig = "、".join(d["triggers"][:5]) + ("…" if len(d["triggers"]) > 5 else "")
            lines.append(f"| `{d['id']}` | {d['name']} | {trig} | `{d['local']['slug']}` | {len(d['external'])} |")
    lines.append("\n## 方向自查（覆盖度）\n")
    blank = [d for d in DOMAINS if not d["external"]]
    lines.append("| 检查项 | 结果 |")
    lines.append("|---|---|")
    lines.append(f"| 域总数 | {len(DOMAINS)}（S {len([d for d in DOMAINS if d['cat']=='S'])} / F {len([d for d in DOMAINS if d['cat']=='F'])} / R {len([d for d in DOMAINS if d['cat']=='R'])}） |")
    lines.append(f"| 库内 skill 覆盖 | {len(DOMAINS)}/{len(DOMAINS)}（每域至少 1 个） |")
    lines.append(f"| 有库外候选的域 | {len(DOMAINS)-len(blank)} |")
    lines.append(f"| 方向空白（仅靠库内） | {len(blank)} → {'、'.join(d['id'] for d in blank)} |")
    lines.append("| 学习类覆盖 | ✅ 课程/课堂/作业/备考/表达/语言 |")
    lines.append("| 生活类覆盖 | ✅ 事务/作息/身心/财务/健康/军政志愿/升学/求职 |")
    lines.append("| 科研类覆盖 | ✅ 文献/实验/工具/产出/规范 |")
    lines.append("| DUT 绑定 | ✅ 19 域全部标注公开站与私密站点 |")
    lines.append("")
    return "\n".join(lines)

def root_skill_md():
    d = fm("qihang",
           "「启航」大连理工大学新生学习生活一体化学伴包（v2.0 三级结构）。入口 skill，负责需求明确、域审查、输出规范与路由。当用户提出与大连理工大学校情、课程学习、备考、笔记、作业、科研、校园生活相关的模糊求助时使用。",
           "version: 2.0.0\nlicense: MIT\ntags: [dlut, campus, learning, library, orchestrator]\n")
    d += """# 「启航」学伴包 · 入口（v2.0）

三级结构：**skill 库（本入口）→ 域 → skill**

```
library/        1 级 · skill 库（只做需求明确 / 域审查 / 输出规范 / 路由）
domains/        2 级 · 域（19 个，覆盖 学习 / 生活 / 科研）
  └─ skills/
       ├─ local/      3 级 · 库内 skill（优先，无需安装）
       └─ external.md 3 级 · 库外候选（库内不满足时才装）
references/     数据与文档（DUT 官网库 / 私密站库 / 验收报告）
```

## 工作流（严格按序，不可跳步）

```
用户需求
  ↓ ①需求明确  library/clarity.md           6 槽位 + 澄清门，U ≤ 5% 才继续
  ↓ ②锁定域    domains/_registry.md          用触发词匹配；无命中走 domain-review.md 兜底
  ↓ ③域审查    library/domain-review.md      确认域边界、越界拦截、跨域串联
  ↓ ④锁定 skill domains/<域>/_domain.md      读该域的库内 skill
  ↓ ⑤库内优先  domains/<域>/skills/local/   命中即调用，无需安装
  ↓ ⑥库外兜底  domains/<域>/skills/external.md  仅当库内不满足才安装
  ↓ ⑦输出      library/output-spec.md        ≤6 条要点，写入学习档案
```

## 三份规则文件（1 级库的本体）

| 文件 | 职责 |
|---|---|
| `library/clarity.md` | 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级 |
| `library/domain-review.md` | 域审查：锁定 / 跨域 / 越界 / 无域兜底 |
| `library/output-spec.md` | 输出规范：统一模板 + 简略原则 |

## 快捷调用

| 入口 | 用法 |
|---|---|
| 自然语言 | 「我高数快挂了」「机械学院官网是啥」 |
| 斜杠命令 | `/qihang` `/qihang-dlut` + 19 个域命令，见 `commands/` |
| 一键脚本 | `bash scripts/qihang.sh {probe\\|install\\|status\\|registry\\|new-term}` |

## 硬规则

1. **库内优先**：库内有该场景 skill 就不装库外。
2. **DUT 强绑定**：命中大工关键词必须先查 `references/dlut-official-sites.md`；未收录固定回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」；**禁止编造 URL / 电话 / 单位名**。
3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件（见 `references/dlut-login-sites.md`）。
4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心。
"""
    return d

def clarity_md():
    return """# 需求明确（Level 1 · clarity）

> 本文件是 1 级 skill 库的职责之一。**未通过本步，不得进入域锁定。**

## 1. 提示词拆解（6 槽位）

| 槽位 | 含义 | 「已填」判定标准 |
|---|---|---|
| `O` 对象 | 课程 / 科目 / 章节 / 学院 / 校区 / 事件 | 原话出现具体名词 |
| `T` 任务 | 答疑 / 备考 / 笔记 / 事务 / 规划 / 查校情 | 能从动词唯一推断 |
| `W` 时间 | 截止日 / 可投入时长 / 周期 | 出现日期、天数或周期词 |
| `C` 约束 | 形式 / 字数 / 工具 / 禁忌 | 出现格式或工具要求 |
| `D` 产出 | 提纲 / 卡组 / 计划 / 文档 / 网址 | 明确说了要什么 |
| `B` 背景 | 年级 / 专业 / 薄弱点 / 情绪 | 出现身份或状态描述 |

空槽**显式留空，不臆测**。

## 2. 澄清门

```
1) c_i = mean(① 是否显式提及→1/0, ② 是否可唯一推断→1/0.5, ③ 是否与上下文冲突→0.5/1)
2) U = 1 − ∏ c_i                                    （6 槽位连乘后取补）
3) U ≤ 0.05 → 放行
   U > 0.05 → 追问，最多 3 轮，每轮 ≤ 3 问
4) 提问优先级：时间 W(3.0) > 对象 O(2.5) > 产出 D(2.0) > 约束 C(1.5) > 背景 B(1.0) > 任务 T(0.5)
5) 3 轮后仍未达标 → 按最大后验假设执行，输出顶部加：
   ⚠️ 假设：{逐条列出}；如不符请纠正
```

## 3. 不追问的例外（避免打扰）

- 命中 G 横切（校情）且对象明确，如「图书馆几点开门」
- 用户显式要求「直接给结果」→ 跳过澄清，但输出须标注假设

## 4. 示例

> 「高数快挂了」

`O`=高数(0.6) `T`=备考(0.7) `W`=∅(0.1) `C`=∅(0.5) `D`=∅(0.3) `B`=新生(0.8)
`U ≈ 0.995 > 0.05` → 追问 3 项（几天 / 哪几章 / 计划还是卡组）→ 回收后 `U ≈ 0.032` → 放行进入域锁定。
"""

def domain_review_md():
    lines = []
    lines.append("# 域审查（Level 1 · domain-review）\n")
    lines.append("> 1 级 skill 库的职责之二。**负责锁定域、拦截越界、处理跨域与无域情况。**\n")
    lines.append("## 1. 锁定流程\n")
    lines.append("```")
    lines.append("输入：已澄清的 6 槽位")
    lines.append("  ↓")
    lines.append("① 取 T(任务) + O(对象) 作为主键，去 domains/_registry.md 匹配触发词")
    lines.append("  ↓")
    lines.append("② 命中 1 个域      → 锁定，读 domains/<域>/_domain.md")
    lines.append("   命中 N 个域      → 跨域串联，按依赖排序，逐个执行 3 级 skill")
    lines.append("   命中 0 个域      → 进入 §3 兜底")
    lines.append("```\n")
    lines.append("## 2. 越界拦截\n")
    lines.append("锁定域后，**用该域的 `_domain.md`「不覆盖」条目复核一次**。若需求落在「不覆盖」里，必须改锁到 `→` 指向的域。\n")
    lines.append("常见越界：\n")
    lines.append("| 表面像 | 实际属于 | 判据 |")
    lines.append("|---|---|---|")
    lines.append("| 让我写作业 | S3 作业与考核 | 只给结构，不代写 |")
    lines.append("| 讲一下这道题 | S1 课程答疑 | 分步讲解，不代做 |")
    lines.append("| 帮我规划考研 | F7 升学深造 | 规划路径，不代写文书 |")
    lines.append("| 我很焦虑 | F3 身心与社交 | 倾听+转介，**不做诊断** |")
    lines.append("| 帮我查重 | R5 学术规范 | 给规范与自查，不代改 |")
    lines.append("")
    lines.append("## 3. 无域兜底\n")
    lines.append("命中 0 个域时，按顺序尝试：\n")
    lines.append("1. **模糊匹配**：用同义词重试触发词表（如「挂科」→「复习/考试」）")
    lines.append("2. **跨域组合**：拆成两个已知域分别处理")
    lines.append("3. **降级为通用问答**：明确告知「本包暂无该方向的域」，按输出规范给通用建议，并在学习档案记录该缺口")
    lines.append("4. **绝不硬塞**：不得把需求塞进不相干的域\n")
    lines.append("## 4. 跨域串联模板\n")
    lines.append("```")
    lines.append("「下周三高数期中，把笔记整成复习方案」")
    lines.append("  → S2 课堂与笔记（笔记归一）")
    lines.append("  → F1 校园事务 / 校历（取考试日期）")
    lines.append("  → S4 备考与记忆（生成卡组与排程）")
    lines.append("  → F2 作息与专注（排专注块）")
    lines.append("```\n")
    lines.append("串联输出时，每条只给**该域**的结论，最后合成一张行动清单。\n")
    return "\n".join(lines)

def output_spec_md():
    return """# 输出规范（Level 1 · output-spec）

> 1 级 skill 库的职责之三。**所有 3 级 skill 的输出都必须走本模板。**

## 1. 统一模板（默认 ≤ 6 条要点）

```
【结论】  一句话可执行答案
【依据】  ≤ 2 条（来自哪个 skill / 哪份材料 / 信息库哪一节）
【步骤】  ≤ 5 条编号动作，每条 ≤ 15 字
【产物】  文件 / 卡组 / 日程 / 网址的落点
【下一步】只给 1 个动作
【假设】  仅当触发"3 轮未澄清"时出现
```

## 2. 变体

**校情查询（走 references/dlut-official-sites.md）**

```
【结论】+【网址】+【状态 ✅/⚠️】+【备注】
```

**跨域串联**

```
每个域给 1 条结论 → 末尾合成一张 ≤ 5 行的行动清单
```

**降级**

在输出**首行**加：`[已降级: 原 skill → 备用 skill]`

## 3. 简略四原则

1. 能一句话不写一段
2. 能列表不写散文
3. 过程细节默认折叠，不刷屏
4. 每次只给**一个**下一步动作（避免选择瘫痪）

## 4. 输出后动作

把「薄弱点 / 错因 / 结论」写入学习档案（Learning Records），下次触发时自动带出。
**禁止**把 F3 域的敏感内容（情绪细节、心理记录）写入档案。
"""

def login_sites_md():
    return """# 大连理工大学 私密站清单（需登录）

> **配套 `dlut-official-sites.md`（公开站）使用。**
> **接入方式：方案 A —— 受控浏览器登录**（已获用户授权）
> **三条铁律：① 只读 ② 不外传 ③ 不写入任何文件**
> 用户已明确授权打开浏览器；登录动作由**用户本人**在受控浏览器窗口内完成，编排器不接触、不存储凭证。

## 0. 接入流程（方案 A）

```
1) 编排器用受控浏览器打开目标站点登录页
2) 提示用户在该窗口内自行登录
3) 用户确认登录完成后，编排器读取当前页面（只读）
4) 抽取所需结构化信息 → 直接用于当次回答
5) 关闭会话；不落盘、不外传、不留存 Cookie
```

**禁止事项**
- ❌ 不代填账号密码，不代点「记住我」
- ❌ 不导出 Cookie / Session / Token
- ❌ 不把页面内容写入任何文件
- ❌ 不访问与本域无关的页面
- ❌ 涉身份证 / 银行卡 / 家庭信息类页面**一律不打开**（走方案 C）

## 1. 需求登录的站点清单

| # | 站点 | URL | 可获取 | 对应域 | 建议 |
|---|---|---|---|---|---|
| 1 | 统一身份认证 | https://sso.dlut.edu.cn/ | 单点登录入口 | 全部 | 用于其他站点的前置登录 |
| 2 | 校园门户 / 办事大厅 | https://portal.dlut.edu.cn/ | 待办、申请、办事流程 | F1 | 方案 A |
| 3 | 综合教务系统 | http://jxgl.dlut.edu.cn/student/ucas-sso/login | 课表、成绩、选课、考试安排 | S1 S3 S4 F1 | 方案 A（高频只读） |
| 4 | 图书馆 | https://lib.dlut.edu.cn/ | 借阅、续借、座位/研讨间预约 | S2 S5 R1 | 方案 A |
| 5 | 一卡通 / 玉兰卡 | https://ecard.dlut.edu.cn/ | 余额、消费流水 | F1 F4 | 方案 A（仅看余额流水） |
| 6 | 学生工作系统 | https://xsc.dlut.edu.cn/ | 资助、评奖、请假、第二课堂 | F1 F3 F4 F6 | 方案 A |
| 7 | 统一支付平台 | http://pay.dlut.edu.cn/ | 缴费状态 | F4 | 方案 C（涉金额，只看状态） |
| 8 | 财务处 | http://cw.dlut.edu.cn/ | 缴费、报销进度 | F4 | 方案 C |
| 9 | 就业信息网 | https://job.dlut.edu.cn/ | 招聘、宣讲会、投递记录 | F8 | 方案 A |
| 10 | 研究生系统 | https://gs.dlut.edu.cn/ | 培养、导师、开题 | R4 R5 F7 | 方案 A |
| 11 | 研究生招生报名 | https://yjszs.dlut.edu.cn/zsbm | 报名状态 | F7 | 方案 C |
| 12 | 校园邮箱 | http://mail.dlut.edu.cn/ | 通知、导师往来 | 通用 | 方案 C（默认不读邮件正文） |
| 13 | 数字书院（超星） | https://dlutzqsy.mh.chaoxing.com/ | 课程资源、作业、测验 | S2 S3 S4 | 方案 A |
| 14 | 大工金课平台 | https://dlut.fanya.chaoxing.com/ | 课程资源 | S2 | 方案 A |
| 15 | 雨课堂 | https://www.yuketang.cn/ | 课件、随堂测验 | S2 S3 | 方案 A |
| 16 | 离校系统 | http://lx.dlut.edu.cn/ | 离校流程 | F1 | 方案 A |
| 17 | 网络与信息化中心 | https://its.dlut.edu.cn/ | 网费、VPN、软件正版化 | R3 F1 | 方案 C |
| 18 | 校园网自助服务 | http://tulip.dlut.edu.cn/ ⚠️ | 网费自助 | F1 | 待核实域名 |
| 19 | i大工 APP | 应用商店 | 场馆/心理/浴室/校车预约 | F1 F3 F5 F2 | **无网页版**，引导用户自行查看 |

## 2. 分级授权表

| 级别 | 范围 | 授权 |
|---|---|---|
| **L1 只读·自动** | 课表、成绩、考试安排、借阅、一卡通余额、场馆预约状态 | 方案 A，可直接读取 |
| **L2 只读·确认后** | 资助申请状态、就业投递记录、培养进度 | 方案 A，读前先问一句 |
| **L3 禁止自动** | 缴费金额、银行卡、身份证、家庭信息、邮件正文、心理记录 | **方案 C**，只给入口不读取 |

## 3. 会话与隐私

- 会话结束即关闭浏览器；不保存 Cookie、不写入学习档案。
- 读到的一切内容**只服务当次回答**，用于回答后即丢弃。
- 用户可随时中止：说「停止」即立即关闭会话。
"""

def build(out):
    # 安全护栏：拒绝危险输出路径（本函数会 rmtree(out)）
    ap = os.path.abspath(out)
    if ap in ("/", "\\", os.path.expanduser("~")) or len(ap.rstrip("/\\")) <= 3:
        raise SystemExit("拒绝执行：输出路径 %s 不安全（本函数会递归删除该目录）" % ap)
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(out)

    def W(rel, content):
        p = os.path.join(out, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        return p

    n = 0
    W("SKILL.md", root_skill_md()); n += 1
    W("library/SKILL.md", root_skill_md().replace("# 「启航」学伴包 · 入口（v2.0）", "# 「启航」学伴包 · skill 库本体（Level 1）")); n += 1
    W("library/clarity.md", clarity_md()); n += 1
    W("library/domain-review.md", domain_review_md()); n += 1
    W("library/output-spec.md", output_spec_md()); n += 1
    W("domains/_registry.md", registry_md()); n += 1
    for d in DOMAINS:
        base = f"domains/{d['id']}-{d['slug']}"
        W(f"{base}/_domain.md", domain_md(d)); n += 1
        W(f"{base}/skills/external.md", external_md(d)); n += 1
        W(f"{base}/skills/local/{d['local']['slug']}/SKILL.md", local_skill_md(d)); n += 1
    W("references/dlut-login-sites.md", login_sites_md()); n += 1

    print(f"生成 {n} 个文件 → {out}")
    print(f"域数 {len(DOMAINS)}：", ", ".join(d["id"] for d in DOMAINS))

if __name__ == "__main__":
    build(OUT)
