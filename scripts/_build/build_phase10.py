#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」v2.5 · 收尾层（build_phase10.py）—— 第 7 轮终验的残留"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
VER = "2.5.0"
def R(rel):
    p = os.path.join(OUT, rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
n = 0

# ① e2e-scenarios.md：把演示 1 的澄清门算术换成新公式与新阈值
s = R("references/e2e-scenarios.md")
if s and "0.927" in s:
    s = s.replace("""| O 对象 | 高数（章节未指定） | 0.6 |
| T 任务 | 备考 | 0.9 |
| W 时间 | 下周三 | 0.9 |
| C 约束 | ∅ | 0.5 |
| D 产出 | 「复习方案」（计划 or 卡组未定） | 0.6 |
| B 背景 | ∅ | 0.5 |

`U = 1 − (0.6×0.9×0.9×0.5×0.6×0.5) ≈ 0.927 > 0.05` → **追问**""",
"""| 槽位 | 值 | cᵢ | wᵢ |
|---|---|---|---|
| O 对象 | 高数，**章节未指定** → 歧义 | 0.5 | 1.5 |
| T 任务 | 显式（备考） | 1.0 | 1.5 |
| D 产出 | 「复习方案」，计划/卡组未定 → 歧义 | 0.5 | 1.5 |
| W 时间 | 显式（下周三） | 1.0 | 0.8 |
| C 约束 | 缺失 | 0.0 | 0.6 |
| B 背景 | 缺失 | 0.0 | 0.2 |

`Σ wᵢcᵢ = 1.5×0.5 + 1.5×1.0 + 1.5×0.5 + 0.8×1.0 = 3.8` ｜ `Σ wᵢ = 6.1`
`U = 1 − 3.8/6.1 = 0.377 > 0.30` 且关键槽 **O/D 缺失** → **追问**""")
    s = s.replace("回收后 `U ≈ 0.04` → 放行。",
                  "回收后 O=1.0、D=1.0 → `Σ wᵢcᵢ = 4.2+0.8 = 5.0`，`U = 1 − 5.0/6.1 = 0.18 ≤ 0.30` → **放行**。")
    s = s.replace("`U = 1 − (0.6×0.7×0.1×0.5×0.3×0.8) ≈ 0.995 > 0.05`", "`U > 0.30`")
    s = s.replace("`U ≈ 0.032 ≤ 0.05`", "`U ≤ 0.30`")
    s = s.replace("`U ≈ 0.045 ≤ 0.05` → **放行**", "关键槽 O/T/D 齐全 → **放行**（见 `clarity.md` §5 例外 2）")
    s = s.replace("`U ≈ 0.05` → **边界值，直接放行**（不追问，避免打扰）",
                  "`O/T/D` 齐全 → **直接放行**（见 `clarity.md` §5 例外 2）")
    s = s.replace("O=校园卡+网费（明确）", "O=校园卡+网费（明确）")
    s = s.replace("0.6) `T`=备考(0.7)", "(0.7)")
    s = re.sub(r"`U = 1 − \([^)]*\) ≈ 0\.\d+ > 0\.05`", "`U > 0.30`（关键槽 O/D 缺失）", s)
    s = re.sub(r"\bU ≈ 0\.\d+ ≤ 0\.05\b", "U ≤ 0.30", s)
    W("references/e2e-scenarios.md", s); n += 1

# ② qihang.sh 版本号
s = R("scripts/qihang.sh")
if s:
    o = s
    s = re.sub(r"学伴包 v2\.\d+", "学伴包 v2.5", s)
    s = re.sub(r"v2\.\d+ · 三级结构管理脚本", "v2.5 · 三级结构管理脚本", s)
    if s != o:
        W("scripts/qihang.sh", s); n += 1

# ③ 危机用例补 24h
s = R("library/domain-review-cases.md")
if s and "12356" not in s:
    s = re.sub(r"(\| 14 \|[^\n]*?\|)",
               "\\1", s)
    s = s.replace("立即给心理中心（https://xinli.dlut.edu.cn/）",
                  "立即给 **24h 通道（全国心理援助热线 12356）** 与心理中心 https://xinli.dlut.edu.cn/")
    s = s.replace("与 i大工 APP 预约入口，建议马上联系辅导员",
                  "与 i大工 APP 预约入口；**已有具体计划 → 110 / 120**；建议马上联系辅导员")
    if "12356" not in s:
        s += "\n\n> **危机处置要点（v2.5）**：F3 危机必须给 **24h 通道（12356 / 010-82951332）**；" \
             "**已有具体计划（备药、选定地点、写告别留言）→ 立即 110 / 120**；同时停止其他一切建议。\n"
    W("library/domain-review-cases.md", s); n += 1

# ④ L3 清单统一为 7 项 + 成绩口径明确
L3NEW = "缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细"
for rel in glob.glob(os.path.join(OUT, "**", "*.md"), recursive=True) + \
           glob.glob(os.path.join(OUT, "**", "*.yaml"), recursive=True):
    r = os.path.relpath(rel, OUT).replace("\\", "/")
    if "/_build/" in r or r in ("references/review-report-v2.2.md", "references/review-report-v2.3.md"):
        continue
    t = R(r)
    if t is None: continue
    o = t
    t = t.replace("缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录（6 项）", L3NEW)
    t = t.replace("缴费金额、银行卡、身份证、家庭信息、邮件正文、心理记录", L3NEW.replace(" / ", "、"))
    if t != o:
        W(r, t); n += 1
# 明确「成绩等级 L1 / 成绩明细 L3」
s = R("references/dlut-field-map.md")
if s and "成绩等级" not in s:
    s = s.replace("| 综合教务系统 | `jxgl.dlut.edu.cn` | 课表、考试安排、培养方案、选课结果 | S1 S3 S4 F1 | L1（**成绩明细 L3**） |",
                  "| 综合教务系统 | `jxgl.dlut.edu.cn` | 课表、考试安排、培养方案、选课结果 | S1 S3 S4 F1 | L1（**成绩等级可读；成绩明细 L3 禁读**） |")
    s = s.replace("## 四、硬约束", "> **成绩口径（v2.5）**：**成绩等级/是否通过 = L1 可读**；**成绩明细（单科分数、绩点计算）= L3 禁读**。\n\n## 四、硬约束")
    W("references/dlut-field-map.md", s); n += 1

# ⑤ selfcheck 自身 bug（grep -c || echo 0 双输出）+ INSTALL 描述
s = R("scripts/selfcheck.sh")
if s:
    o = s
    s = s.replace('_c=$(grep -c \'^## ⚠️ 红线（不得绕过）\' "$f" 2>/dev/null || echo 0)\n  [ "${_c:-0}" -gt 1 ]',
                  '_c=$(grep -c \'^## ⚠️ 红线（不得绕过）\' "$f" 2>/dev/null)\n  _c=${_c:-0}\n  [ "$_c" -gt 1 ]')
    s = s.replace('_d=$(grep -E \'^- \' "$f" 2>/dev/null | sort | uniq -d | wc -l | tr -d \' \')',
                  '_d=$(grep -E \'^- \' "$f" 2>/dev/null | sort | uniq -d | wc -l | tr -d \' \')\n  _d=${_d:-0}')
    s = s.replace('_cases=$(grep -c \'^| [0-9]* |\' library/domain-review-cases.md 2>/dev/null || echo 0)',
                  '_cases=$(grep -c \'^| [0-9]* |\' library/domain-review-cases.md 2>/dev/null)\n_cases=${_cases:-0}')
    if s != o:
        W("scripts/selfcheck.sh", s); n += 1

s = R("INSTALL.md")
if s and "[1级] 5 个 library 文件" in s:
    s = s.replace("`[1级] 5 个 library 文件 ✓`", "`[1级] 7 个 library 文件 ✓`（逐行列出 SKILL + 6 份规则）")
    W("INSTALL.md", s); n += 1

print("阶段 10（收尾）完成：改动 %d 个文件" % n)
print("  e2e 演示改新公式/新阈值 · qihang.sh 版本 · 危机用例补 24h · L3 清单 7 项统一 · 成绩口径 · selfcheck 自身 bug")
