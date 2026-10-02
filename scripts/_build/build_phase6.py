#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.4 · 残留清扫层（build_phase6.py）

来源：第 3 轮盲测。核心教训——build_phase4 的 glob 只覆盖顶层 `*.md`，
**漏了 `commands/` 与 `references/`**，导致「已修复」实际未闭环。
本层用**全递归 glob + 明确的排除清单**重做，并补齐其余残留。

顺序：v2 → extras → phase1 → phase2 → phase3 → phase4 → phase5 → **phase6** → selfcheck
"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
VER = "2.4.0"
NCASES = 22

# 允许保留旧阈值表述的文件（历史文档 / 复核报告里「引述问题」）
EXEMPT = [
    "references/review-report-v2.2.md",   # 报告里引述旧公式作为「问题现象」
    "references/review-report-v2.3.md",
    "references/需求确认书-v2三级结构.md",  # 已加历史文档横幅
    "library/clarity.md",                  # 对照说明「为什么不用 ∏cᵢ」
]

def allfiles(pats=("**/*.md", "**/*.yaml", "**/*.html", "**/*.json")):
    out = []
    for pat in pats:
        for p in glob.glob(os.path.join(OUT, pat), recursive=True):
            r = os.path.relpath(p, OUT).replace("\\", "/")
            if "/_build/" in r or "__pycache__" in r or r.endswith(".selfcheck.tmp"):
                continue
            out.append(r)
    return sorted(set(out))

def R(rel):
    p = os.path.join(OUT, rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)

def edit(rel, pairs, count=0):
    s = R(rel)
    if s is None: return 0
    o = s
    for a, b in pairs:
        s = s.replace(a, b)
    if s != o:
        W(rel, s); return 1
    return 0

n = 0

# ============================================================
# 1. 阈值全局同步（正确覆盖 commands/ references/）
# ============================================================
TH = [("U ≤ 5% 才继续", "U ≤ 0.30 才继续"), ("U ≤ 5%）", "U ≤ 0.30）"),
      ("U ≤ 5%", "U ≤ 0.30"), ("U > 5%", "U > 0.30"),
      ("`U = 1 − ∏cᵢ`", "`U = 1 − Σ(wᵢcᵢ)/Σwᵢ`"),
      ("U = 1 − ∏cᵢ", "U = 1 − Σ(wᵢcᵢ)/Σwᵢ"),
      ("threshold: 0.05", "threshold: 0.30")]
for rel in allfiles():
    if rel in EXEMPT: continue
    if edit(rel, TH): n += 1

# ============================================================
# 2. 计数 / 版本 / 平台称谓
# ============================================================
CNT = [("14 条用例", "%d 条用例" % NCASES), ("14 条越界用例", "%d 条越界用例" % NCASES),
       ("14 条（含 3 反例）", "%d 条（含 3 反例）" % NCASES),
       ("14 条判定", "%d 条判定" % NCASES), ("14 条", "%d 条" % NCASES),
       ("13 条用例", "%d 条用例" % NCASES),
       ("12 域", "16 域"), ("扩展到 **12 域**", "覆盖 **16 域**"),
       ("version: 2.3.0", "version: %s" % VER), ("version: 2.2.0", "version: %s" % VER),
       ("version: 2.1.0", "version: %s" % VER), ("version: 2.0.0", "version: %s" % VER),
       ("学伴包 v2.3", "学伴包 v2.4"), ("学伴包 v2.2", "学伴包 v2.4"),
       ("学伴包 v2.1", "学伴包 v2.4"), ("学伴包 v2.0", "学伴包 v2.4"),
       ("v2.3 修订", "v2.4 修订"), ("入口（v2.3）", "入口（v2.4）"),
       ("当前状态（v2.0）", "当前状态（v2.4）"),
       ("# 「启航」学伴包 v2.0", "# 「启航」学伴包 v2.4"),
       ("项目文档（v2.0）", "项目文档（v2.4）"),
       ("（95 文件，生成器驱动）", "（119 文件，生成器驱动）"),
       ("95 文件", "119 文件")]
for rel in allfiles():
    if rel.startswith("references/review-report"): continue
    if edit(rel, CNT): n += 1

# ============================================================
# 3. 「成绩」分级口径统一（config 与 dlut-read.sh 矛盾）
# ============================================================
n += edit("config.yaml", [
    ("L1_auto: [课表, 成绩, 考试安排, 借阅, 一卡通余额, 场馆预约状态]",
     "L1_auto: [课表, 成绩等级, 考试安排, 借阅, 一卡通余额, 场馆预约状态]"),
    ("L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录]",
     "L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录, 成绩明细]"),
])
n += edit("scripts/dlut-read.sh", [
    ("缴费|金额|银行卡|身份证|邮件正文|心理记录|成绩|简历)",
     "缴费|金额|银行卡|身份证|邮件正文|心理记录|成绩明细|简历)"),
    ("|成绩明细)$", "|成绩明细)$"),
])

# ============================================================
# 4. F2 残留的旧域命名「D 域」
# ============================================================
for rel in ["domains/F2-focus/skills/local/focus-block/SKILL.md",
            "domains/F2-focus/_domain.md"]:
    n += edit(rel, [("与 D 域备考排程联动", "与 `S4` 备考排程联动"),
                    ("D 域", "`S4`"), ("D 域", "`S4`")])

# ============================================================
# 5. 红线补强：S2/S3 代操作 + §7 限域
# ============================================================
n += edit("domains/S2-lecture-notes/_domain.md", [
    ("- 产出若用于**提交**，须改锁 `S3`；本域只做自用笔记",
     "- 产出若用于**提交**，须改锁 `S3`；本域只做自用笔记\n- **不代操作教学平台**（不代提交作业、不代上传超星/雨课堂）"),
])
n += edit("domains/S3-assignment/_domain.md", [
    ("- **不编造实验数据** —— 属学术不端，须改锁并提示 `R5`",
     "- **不编造实验数据** —— 属学术不端，须改锁并提示 `R5`\n- **不代操作教学平台**（不代提交作业/报告）"),
])
n += edit("domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md", [
    ("- **不代做**：只给讲解与同类题，**不产出可直接提交的答案**",
     "- 产出若用于**提交**，须改锁 `S3`\n- **不代操作教学平台**（不代提交作业）"),
])
n += edit("domains/S3-assignment/skills/local/lab-report/SKILL.md", [
    ("- **不代写正文**（只给 IMRAD 骨架与自查）",
     "- **不代写正文**（只给 IMRAD 骨架与自查）\n- **不代操作教学平台**（不代提交）"),
])
# §7 正面清单限域
n += edit("library/output-spec.md", [
    ("| 「给我完整解法，我自己对着学」 | ✅ 放行 | 自学场景；红线只禁「可直接提交的答案」 |",
     "| 「给我完整解法，我自己对着学」 | ✅ 放行（**限 S1/S4 单题**） | 自学场景；S5 论文/R1 引文不适用，仍按红线处理 |"),
    ("| 「我的报告结构搭得对吗」 | ✅ 放行 | 自查合规；红线只禁「代写正文」 |",
     "| 「我的报告结构搭得对吗」 | ✅ 放行 | 自查合规；红线只禁「代写正文」 |\n"
     "| 「PPT 帮我搭个框架」 | ✅ 放行 | 结构合规；正文内容仍须本人写 |"),
])

# ============================================================
# 6. S6 示例与澄清门例外冲突 + F1 边界表述
# ============================================================
n += edit("domains/S6-language/skills/local/lang-drill/SKILL.md", [
    ("【待补】你还没说哪一项最差", "【假设】按「听力最弱」推进（O/T/D 齐全，依 `clarity.md` §5 例外 2 不追问）"),
])
n += edit("domains/F1-campus-affairs/_domain.md", [
    ("不涉及钱（→F4）", "不涉及**资金处置**（缴费/报销/止损 → `F4`）；网费与学费的**入口与流程**属本域"),
])

# ============================================================
# 7. 消歧表补 3 组
# ============================================================
n += edit("domains/_registry.md", [
    ("| **论文** | S5 / R4 | 课程论文 → `S5`；期刊投稿与返修 → `R4` |",
     "| **论文** | S5 / R4 | 课程论文 → `S5`；期刊投稿与返修 → `R4` |\n"
     "| **PPT / 板书** | S2 / S5 | 课堂笔记用途 → `S2`；学术汇报用途 → `S5` |\n"
     "| **作业题 / 原题** | S1 / S3 | 求讲解 → `S1`；求产出可提交答案 → `S3`（红线） |\n"
     "| **翻译 / 润色** | S6 / S5 / R4 | 语言学习 → `S6`；论文表达 → `S5`；投稿前 → `R4` |"),
])

# ============================================================
# 8. output-checklist 标题与域数对齐，补 S6/F2/R3
# ============================================================
n += edit("library/output-checklist.md", [
    ("## 二、域专属附加校验（12 域）", "## 二、域专属附加校验（16 域）"),
    ("| **R4/R5** | 未代投稿；未代改以规避查重；未隐藏 AI 使用痕迹 |",
     "| **R4/R5** | 未代投稿；未代改以规避查重；未隐藏 AI 使用痕迹 |\n"
     "| **S6** | 作文只标错未重写；未代写课程作业 |\n"
     "| **F2** | 未代做学业规划（应改锁 S4） |\n"
     "| **R3** | 未代做课业代码；未代操作教务系统 |"),
])

# ============================================================
# 9. PROJECT.md L3 清单补「家庭信息」+ 平台行去重
# ============================================================
n += edit("PROJECT.md", [
    ("L3 级（缴费金额 / 银行卡 / 身份证 / 邮件正文 / 心理记录）**一律不读取**",
     "L3 级（缴费金额 / 银行卡 / 身份证 / **家庭信息** / 邮件正文 / 心理记录）**一律不读取**"),
])

# ============================================================
# 10. selfcheck 增加阈值与旧域名词断言
# ============================================================
s = R("scripts/selfcheck.sh")
if s and "阈值一致性" not in s:
    s = s.replace('echo "[7] 计数一致性"', '''echo "[6.5] 阈值与旧域名一致性（v2.4 新增）"
_bad_th=$(grep -rlE "U (≤|<=) 5%|threshold: 0\\.05" --include='*.md' --include='*.yaml' \\
  . 2>/dev/null | grep -v _build | grep -v 'review-report' | grep -v '需求确认书' | grep -v 'clarity.md' | wc -l | tr -d ' ')
[ "$_bad_th" -eq 0 ] && ok "无旧阈值残留" || bad "$_bad_th 个文件仍有旧阈值"
_old_dom=$(grep -rlnE '\\bD 域\\b|[（(]A[-–]F 域' domains/ library/ SKILL.md 2>/dev/null | wc -l | tr -d ' ')
[ "$_old_dom" -eq 0 ] && ok "无 v1.1 旧域名残留" || bad "$_old_dom 个文件含旧域名"
_cases=$(grep -c '^| [0-9]* |' library/domain-review-cases.md 2>/dev/null || echo 0)
if grep -q "14 条" library/domain-review.md 2>/dev/null; then bad "用例计数仍是 14"; else ok "用例计数一致"; fi

echo "[7] 计数一致性"''')
    W("scripts/selfcheck.sh", s); n += 1

print("阶段 6（残留清扫）完成：改动 %d 处" % n)
print("  修复：阈值(全覆盖 commands/+references/) · 计数 %d · 版本 %s · 成绩分级统一" % (NCASES, VER))
print("        F2 旧域名 · S2/S3 代操作红线 · §7 限域 · S6/F1 表述 · 消歧补 3 组 · checklist 16 域 · selfcheck 断言")
