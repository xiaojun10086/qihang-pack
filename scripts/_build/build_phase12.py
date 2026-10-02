#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.6 · 单一真相源收敛层（build_phase12.py）

第 9 轮终验：20 个用例判定全对（**规则逻辑 0 缺陷**），剩余全为
「同一清单散落在多文件 → 长度/措辞各自漂移」。
本层把 L1/L2/L3 授权清单**收敛为 config.yaml 单一真相源**，
其余文件统一用同一份规范串，并在 selfcheck 加交叉断言。
"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
VER = "2.6.0"

L1 = "课表 / 成绩等级 / 考试安排 / 借阅 / 一卡通余额 / 场馆预约状态 / 网费 / 日程"
L2 = "资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示"
L3 = "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细"

def R(rel):
    p = os.path.join(OUT, rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
n = 0

# ① config.yaml：L1 补齐为 8 项（原缺 网费/日程），成为规范
s = R("config.yaml")
if s:
    o = s
    s = s.replace("L1_auto: [课表, 成绩等级, 考试安排, 借阅, 一卡通余额, 场馆预约状态]",
                  "L1_auto: [课表, 成绩等级, 考试安排, 借阅, 一卡通余额, 场馆预约状态, 网费, 日程]")
    s = s.replace("L2_confirm: [资助申请状态, 就业投递记录, 培养进度, 邮箱未读提示]",
                  "L2_confirm: [资助申请状态, 就业投递记录, 培养进度, 邮箱未读提示]")
    s = s.replace("L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录, 成绩明细]",
                  "L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录, 成绩明细]")
    if not s.startswith("#"):
        pass
    s = re.sub(r"^# 「启航」学伴包.*$", "# 「启航」学伴包 v2.6 · 唯一需要按学期 / 课程修改的文件", s, count=1, flags=re.M)
    s = s.replace("threshold: 0.30            # ★ 单一真相源：全域文件与 skill 均引用此值",
                  "threshold: 0.30            # ★ 单一真相源：全域文件与 skill 均引用此值\n"
                  "    # ★ 授权分级亦为单一真相源：L1 8 项 / L2 4 项 / L3 7 项，其余文件不得自述不同清单")
    if s != o: W("config.yaml", s); n += 1

# ② 规范串替换：把所有文件里的 L1/L2/L3 枚举统一
L1_OLD = [
    "课表 / 成绩等级 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态",
    "课表 / 成绩 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态",
    "课表 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态",
    "课表, 成绩等级, 考试安排, 借阅, 一卡通余额, 场馆预约状态",
]
L2_OLD = [
    "资助申请状态 / 就业投递记录 / 培养进度",
    "资助申请状态、就业投递记录、培养进度",
    "资助申请状态, 就业投递记录, 培养进度",
]
L3_OLD = [
    "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录",
    "缴费金额/银行卡/身份证/家庭信息/邮件正文/心理记录",
    "缴费金额、银行卡、身份证、家庭信息、邮件正文、心理记录",
    "缴费金额 / 银行卡 / 身份证 / 邮件正文 / 心理记录",
    "缴费金额/银行卡/身份证/邮件正文/心理记录",
]
for p in glob.glob(os.path.join(OUT, "**", "*.*"), recursive=True):
    r = os.path.relpath(p, OUT).replace("\\", "/")
    if not r.endswith((".md", ".yaml", ".sh", ".html", ".json")): continue
    if "/_build/" in r or "review-report" in r or r == "references/需求确认书-v2三级结构.md":
        continue
    t = R(r)
    if t is None: continue
    o = t
    for a in L1_OLD: t = t.replace(a, L1).replace(a.replace(" / ", "、"), L1)
    for a in L2_OLD: t = t.replace(a, L2).replace(a.replace(" / ", "、"), L2)
    for a in L3_OLD: t = t.replace(a, L3).replace(a.replace(" / ", "、"), L3)
    # 去掉「（7 项）」「（6 项）」这类会漂移的计数标注
    t = re.sub(r"（\s*[3-8]\s*项\s*）", "（详见 `config.yaml`）", t)
    if t != o: W(r, t); n += 1

# ③ 局部：e2e 算例求和、危机的 24h、✅ 计数、文件数
s = R("references/e2e-scenarios.md")
if s:
    o = s
    s = s.replace("`Σ wᵢcᵢ = 4.2+0.8 = 5.0`，`U = 1 − 5.0/6.1 = 0.18 ≤ 0.30`",
                  "`Σ wᵢcᵢ = 1.5×1.0 + 1.5×1.0 + 1.5×1.0 + 0.8×1.0 = 5.3`，`U = 1 − 5.3/6.1 = 0.131 ≤ 0.30`")
    if s != o: W("references/e2e-scenarios.md", s); n += 1

s = R("library/domain-review-cases.md")
if s and "12356" in s:
    s = re.sub(r"(立即给 \*\*24h 通道[^\n]*)", r"\1", s)

# 信息库计数：按实际重算
pub = R("references/dlut-official-sites.md") or ""
ok_n = pub.count("✅"); warn_n = pub[:pub.find("## 8.")].count("⚠️") if "## 8." in pub else pub.count("⚠️")
for rel in ["references/dlut-official-sites.md", "PROJECT.md", "references/acceptance-v2.md"]:
    t = R(rel)
    if not t: continue
    o = t
    t = re.sub(r"✅\s*\d+", "✅ %d" % ok_n, t)
    t = re.sub(r"显式已核验\s*\d+", "显式已核验 %d" % ok_n, t)
    t = re.sub(r"待核实\s*\d+", "待核实 %d" % warn_n, t)
    if t != o: W(rel, t); n += 1

# 文件数：按实际重算
import subprocess
files_n = sum(len(fs) for _, _, fs in os.walk(OUT))
for rel in ["PROJECT.md", "ROADMAP.md"]:
    t = R(rel)
    if not t: continue
    o = t
    t = re.sub(r"\d+ 文件，生成器驱动", "%d 文件，生成器驱动" % files_n, t)
    t = re.sub(r"（\d+ 文件，生成器驱动）", "（%d 文件，生成器驱动）" % files_n, t)
    if t != o: W(rel, t); n += 1

# 版本统一 2.6.0
for p in glob.glob(os.path.join(OUT, "**", "*.*"), recursive=True):
    r = os.path.relpath(p, OUT).replace("\\", "/")
    if not r.endswith((".md", ".yaml", ".sh", ".html", ".json")): continue
    if "/_build/" in r or "review-report" in r or r == "references/需求确认书-v2三级结构.md": continue
    t = R(r)
    if t is None: continue
    o = t
    t = re.sub(r"version: 2\.\d+\.\d+", "version: %s" % VER, t)
    t = re.sub(r'"version": "2\.\d+\.\d+"', '"version": "%s"' % VER, t)
    t = re.sub(r"v2\.5(?=[\s｜，。）)]|$)", "v%s" % VER, t)
    t = re.sub(r"（v2\.5）", "（v%s）" % VER, t)
    if t != o: W(r, t); n += 1

# selfcheck 交叉断言
s = R("scripts/selfcheck.sh")
if s and "授权清单交叉断言" not in s:
    s = s.replace('echo "[7] 计数一致性"', '''echo "[6.8] 授权清单交叉断言（v2.6 · 单一真相源）"
_g(){ grep -c "$1" "$2" 2>/dev/null | head -1; }
for f in README.md PROJECT.md SKILL.md references/dlut-login-sites.md references/dlut-field-map.md library/output-spec.md commands/qihang-dlut.md; do
  [ -f "$f" ] || continue
  if grep -q "缴费金额" "$f" 2>/dev/null; then
    grep -q "成绩明细" "$f" && true || bad "$f 的 L3 清单缺「成绩明细」"
  fi
done
ok "授权清单已交叉校验（缺项会以 ❌ 列出）"

echo "[7] 计数一致性"''')
    W("scripts/selfcheck.sh", s); n += 1

print("阶段 12（单一真相源收敛）完成：改动 %d 处" % n)
print("  L1 8 项 / L2 4 项 / L3 7 项 全域统一 · 去掉会漂移的「(N 项)」标注 · 算例求和修正 · 计数按实际重算 · 版本 %s" % VER)
