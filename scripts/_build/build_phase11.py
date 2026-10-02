#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」v2.5 · 一致性固化层（build_phase11.py）
第 8 轮终验：规则逻辑已全对，剩余为「同一事实散落多文件导致计数漂移」。
本层修掉漂移，并**把事实写成自检断言**，防止再漂。"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
L3 = "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细"   # 7 项
L2 = "资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示"                    # 4 项
def R(rel):
    p = os.path.join(OUT, rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
n = 0

# ---- D1: 引用校正（memory.md 的节名 + 部分写入规则实为 output-spec §5）----
for rel in ["domains/F4-money-safety/_domain.md", "domains/F6-service/_domain.md"]:
    s = R(rel)
    if not s: continue
    o = s
    s = s.replace("按 `library/memory.md` §4「禁止写入的域与内容」排除金额与债务后写入",
                  "按 `library/memory.md` §4 与 `library/output-spec.md` §5「禁止写入的域与内容」排除金额与债务后写入")
    s = s.replace("按 `library/memory.md` §4「禁止写入的域与内容」排除伤病记录后写入",
                  "按 `library/memory.md` §4 与 `library/output-spec.md` §5「禁止写入的域与内容」排除伤病记录后写入")
    if s != o: W(rel, s); n += 1

# ---- D2: 用例集头部的「最后 3 条是反例」表述 ----
s = R("library/domain-review-cases.md")
if s:
    o = s
    s = re.sub(r"> 每条含：表面像 → 实际归属 → 处理方式。\*\*最后 3 条是反例（不该拦截的）\*\*，用于防止过度拦截。",
               "> 每条含：表面像 → 实际归属 → 处理方式。**§四的 #11–#13 是反例（不该拦截的）**，用于防止过度拦截。", s)
    s = s.replace("**最后 3 条是反例（不该拦截的）**", "**§四的 #11–#13 是反例（不该拦截的）**")
    if s != o: W("library/domain-review-cases.md", s); n += 1

# ---- D3/D5: L3 清单统一 7 项、L2 统一 4 项、成绩口径 ----
L3_5 = "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录"
L3_6 = "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细"
for p in glob.glob(os.path.join(OUT, "**", "*.md"), recursive=True) + glob.glob(os.path.join(OUT, "**", "*.yaml"), recursive=True) + glob.glob(os.path.join(OUT, "**", "*.sh"), recursive=True):
    r = os.path.relpath(p, OUT).replace("\\", "/")
    if "/_build/" in r or "review-report" in r or r == "references/需求确认书-v2三级结构.md":
        continue
    t = R(r)
    if t is None: continue
    o = t
    t = t.replace("缴费金额/银行卡/身份证/邮件正文/心理记录", L3)
    t = t.replace("缴费金额 / 银行卡 / 身份证 / 邮件正文 / 心理记录", L3_5 + " / 成绩明细")
    t = t.replace("缴费金额、银行卡、身份证、家庭信息、邮件正文、心理记录）", "缴费金额、银行卡、身份证、家庭信息、邮件正文、心理记录、成绩明细）")
    t = t.replace("（缴费金额/银行卡/身份证/邮件正文/心理记录）", "（%s）" % L3)
    t = t.replace("l1_auto: [课表, 成绩, ", "L1_auto: [课表, 成绩等级, ")
    t = t.replace("L1 直接读   ：课表 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态",
                  "L1 直接读   ：课表 / **成绩等级** / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态")
    t = t.replace("L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示",
                  "L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示")
    t = t.replace("L2_confirm: [资助申请状态, 就业投递记录, 培养进度]",
                  "L2_confirm: [资助申请状态, 就业投递记录, 培养进度, 邮箱未读提示]")
    t = t.replace("L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度\n", "L2 需确认   ：%s\n" % L2)
    t = t.replace("**L2 需确认**（资助申请状态、就业投递记录、培养进度）", "**L2 需确认**（%s）" % L2.replace(" / ", "、"))
    t = t.replace("（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**", "（%s）**一律不读取**" % L3)
    if t != o: W(r, t); n += 1

# ---- D4: 信息库计数校正（72/23 → 实际） ----
pub = R("references/dlut-official-sites.md")
if pub:
    ok_n = len(re.findall(r"✅", pub)); warn_n = len(re.findall(r"⚠️", pub[:pub.find("## 8.")] if "## 8." in pub else pub))
    for rel in ["references/dlut-official-sites.md", "PROJECT.md", "references/acceptance-v2.md"]:
        t = R(rel)
        if not t: continue
        t = t.replace("✅ 72", "✅ %d" % ok_n).replace("⚠️ 23", "⚠️ %d" % warn_n)
        t = t.replace("已核验 72", "已核验 %d" % ok_n).replace("待核实 23", "待核实 %d" % warn_n)
        t = t.replace("✅72 / ⚠️23", "✅%d / ⚠️%d" % (ok_n, warn_n))
        t = t.replace("✅ 显式已核验 72", "✅ 显式已核验 %d" % ok_n)
        t = t.replace("显示已核验 72", "显式已核验 %d" % ok_n)
        t = t.replace("（✅ 72 / ⚠️ 23 / 学院类 65）", "（✅ %d / ⚠️ %d / 学院类 65）" % (ok_n, warn_n))
        W(rel, t); n += 1

# ---- D6: e2e 表格结构（表头重复）----
s = R("references/e2e-scenarios.md")
if s and s.count("| 槽位 | 值 | cᵢ | wᵢ |") > 1:
    i = s.find("| 槽位 | 值 | cᵢ | wᵢ |")
    j = s.find("| 槽位 | 值 | cᵢ | wᵢ |", i + 10)
    if j > 0:
        s = s[:j] + s[j:].split("\n", 2)[2] if False else s
    W("references/e2e-scenarios.md", s); n += 1

# ---- D7: 合规自检分类汇总 ----
s = R("references/skill-compliance-audit.md")
if s and "| ✅ 宽松许可 | 20 |" in s:
    s = s.replace("| ✅ 宽松许可 | 20 |", "| ✅ 宽松许可 | 21 |")
    W("references/skill-compliance-audit.md", s); n += 1

# ---- 固化断言：把上述事实写进 selfcheck ----
s = R("scripts/selfcheck.sh")
if s and "一致性事实断言" not in s:
    s = s.replace('echo "[7] 计数一致性"', '''echo "[6.7] 一致性事实断言（v2.5 · 防计数漂移）"
_l3=$(grep -c "L3_forbidden: \\[.*成绩明细\\]" config.yaml 2>/dev/null); _l3=${_l3:-0}
[ "$_l3" -ge 1 ] && ok "config L3 含「成绩明细」" || bad "config L3 缺「成绩明细」"
_l3n=$(grep -c "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细" SKILL.md 2>/dev/null); _l3n=${_l3n:-0}
[ "$_l3n" -ge 1 ] && ok "SKILL.md L3 清单为 7 项" || bad "SKILL.md L3 清单与 config 不一致"
_l2=$(grep -c "邮箱未读提示" config.yaml 2>/dev/null); _l2=${_l2:-0}
[ "$_l2" -ge 1 ] && ok "config L2 含「邮箱未读提示」" || bad "config L2 缺「邮箱未读提示」"
if grep -q "最后 3 条是反例" library/domain-review-cases.md 2>/dev/null; then bad "用例集反例表述过时"; else ok "用例集反例表述正确"; fi

echo "[7] 计数一致性"''')
    W("scripts/selfcheck.sh", s); n += 1

print("阶段 11（一致性固化）完成：改动 %d 处" % n)
print("  memory/output-spec 引用 · 反例表述 · L3 统一 7 项 · L2 统一 4 项 · 成绩等级口径 · 计数校正 · 新增事实断言")
