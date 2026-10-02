#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.5 · 决定性收尾层（build_phase7.py）

来源：第 4 轮盲测。修掉前几层因「替换模式太窄」而漏掉的残留：
  · 阈值变体（`>5%` / `&gt;5%` / `U ≈ 0.05`）—— 逐行按上下文判定，不再靠固定串
  · **19 个库内 skill 的 `../external.md` 路径错误**（应为 `../../external.md`）
  · 版本号全域统一 + 其它零散不一致

顺序：v2 → extras → phase1 → phase2 → phase3 → phase4 → phase5 → phase6 → **phase7** → selfcheck
"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
VER = "2.5.0"

EXEMPT = ["references/review-report-v2.2.md", "references/review-report-v2.3.md",
          "references/需求确认书-v2三级结构.md"]

def allfiles():
    out = []
    for pat in ("**/*.md", "**/*.yaml", "**/*.html", "**/*.json",
                # ★ glob 默认不遍历「点目录」，需显式补上
                ".codebuddy-plugin/*.json", ".*/**/*.json"):
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

n = 0

# ============================================================
# 1. 阈值：逐行按上下文替换（覆盖所有变体）
# ============================================================
CTX = ("U ", "U=", "U≈", "U ≈", "U≤", "U ≥", "不确定", "threshold", "阈值", "追问", "澄清门")
def fix_threshold_line(line):
    if "5%" not in line and "0.05" not in line:
        return line
    if not any(c in line for c in CTX):
        return line
    line = line.replace("&gt;5%", "&gt; 0.30").replace(">5%", "> 0.30")
    line = line.replace("≤5%", "≤ 0.30").replace("≤ 5%", "≤ 0.30")
    line = line.replace("阈值 5%", "阈值 0.30").replace("threshold: 0.05", "threshold: 0.30")
    line = line.replace("U ≈ 0.05", "U ≈ 0.30").replace("U≈0.05", "U≈0.30")
    line = re.sub(r"(?<![0-9.])5%", "0.30", line)
    return line

for rel in allfiles():
    if rel in EXEMPT: continue
    s = R(rel)
    if s is None: continue
    lines = s.split("\n")
    out = [fix_threshold_line(l) for l in lines]
    if out != lines:
        W(rel, "\n".join(out)); n += 1

# ============================================================
# 2. ★ 19 个库内 skill 的相对路径错误
#    external.md 在 skills/ 下，skill 在 skills/local/<name>/ 下 → 需上两级
# ============================================================
for p in glob.glob(os.path.join(OUT, "domains", "*", "skills", "local", "*", "SKILL.md")):
    rel = os.path.relpath(p, OUT); s = R(rel)
    if s is None: continue
    o = s
    s = s.replace("读同目录 `../external.md`", "读上一级 `../../external.md`")
    s = s.replace("读同目录 `../external.md`", "读上一级 `../../external.md`")
    s = s.replace("`../external.md`", "`../../external.md`")
    if s != o:
        W(rel, s); n += 1

# ============================================================
# 3. S2/S3 库内 skill 红线补齐（第 6 层替换串未命中）
# ============================================================
s2r = R("domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md")
if s2r and "不代操作教学平台" not in s2r:
    if "## ⚠️ 红线" in s2r:
        s2r = s2r.replace("## ⚠️ 红线（不得绕过）\n\n",
                          "## ⚠️ 红线（不得绕过）\n\n- **不代操作教学平台**（不代提交作业、不代上传超星/雨课堂）\n", 1)
        W("domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md", s2r); n += 1
s3r = R("domains/S3-assignment/skills/local/lab-report/SKILL.md")
if s3r and "不代操作教学平台" not in s3r:
    if "## ⚠️ 红线" in s3r:
        s3r = s3r.replace("## ⚠️ 红线（不得绕过）\n\n",
                          "## ⚠️ 红线（不得绕过）\n\n- **不代操作教学平台**（不代提交作业/报告）\n", 1)
        W("domains/S3-assignment/skills/local/lab-report/SKILL.md", s3r); n += 1

# ============================================================
# 4. 版本统一 + 零散不一致
# ============================================================
PLAIN = [
    ('"version": "2.1.0"', '"version": "%s"' % VER),
    ('"version": "2.0.0"', '"version": "%s"' % VER),
    ('"version": "2.3.0"', '"version": "%s"' % VER),
    ('"version": "2.4.0"', '"version": "%s"' % VER),
    ("」v2.1 ｜", "」v2.5 ｜"),
    ("学伴包 v2.1", "学伴包 v2.5"),
    # ROADMAP 的历史版本表述 → 改为结构描述（不留版本号，避免与当前版本混淆）
    ("设计书已对齐 v2.0（19 域三级结构）", "设计书已对齐结构（19 域三级结构）"),
    ("同步赛道二设计书到 v2.0", "同步赛道二设计书到当前结构"),
    ("现有 html 仍是 v1.1 的 7 域版本", "现有 html 曾为 v1.1 的 7 域版本"),
    ("与仓库实际一致（19 域", "与仓库实际一致（19 域"),
    ("版本 v2.0 ｜ 更新", "版本 v%s ｜ 更新" % VER.split(".")[0]),
    ("## 7. 当前状态（v2.1）", "## 7. 当前状态（v2.5）"),
    ("## 7. 当前状态（v2.0）", "## 7. 当前状态（v2.5）"),
    ("## 7. 当前状态（v2.4）", "## 7. 当前状态（v2.5）"),
    # 「三件事」vs「四件事」
    ("**只做三件事**：①需求明确 ②域审查 ③输出规范",
     "**只做四件事**：①需求明确 ②域审查 ③输出规范 ④记忆归档"),
    ("只做三件事", "只做四件事"),
    ("（只做 需求明确 / 域审查 / 输出规范 / 记忆）", "（只做 需求明确 / 域审查 / 输出规范 / 记忆归档）"),
    # checklist 域数
    ("## 二、域专属附加校验（16 域）", "## 二、域专属附加校验（覆盖 19 域）"),
    ("## 二、域专属附加校验（12 域）", "## 二、域专属附加校验（覆盖 19 域）"),
    # 【假设】触发条件统一
    ("【假设】  仅当触发\"3 轮未澄清\"时出现",
     "【假设】  出现条件：① 3 轮未澄清，或 ② 依 `clarity.md` §5 例外（关键槽齐/紧急豁免）直接推进时"),
    ("【假设】  仅当触发“3 轮未澄清”时出现",
     "【假设】  出现条件：① 3 轮未澄清，或 ② 依 `clarity.md` §5 例外（关键槽齐/紧急豁免）直接推进时"),
    # 消歧补「背单词」「求」
    ("| **翻译 / 润色** | S6 / S5 / R4 | 语言学习 → `S6`；论文表达 → `S5`；投稿前 → `R4` |",
     "| **翻译 / 润色** | S6 / S5 / R4 | 语言学习 → `S6`；论文表达 → `S5`；投稿前 → `R4` |\n"
     "| **背单词 / 记忆法** | S4 / S6 | 应试备考 → `S4`；语言能力长期提升 → `S6` |\n"
     "| **「求」类动词** | S1 | 「求推荐/求资源」不是 S1；仅「求解/求证」才属 `S1` |"),
]
for rel in allfiles():
    if rel.startswith("references/review-report"): continue
    s = R(rel)
    if s is None: continue
    o = s
    for a, b in PLAIN:
        s = s.replace(a, b)
    if s != o:
        W(rel, s); n += 1

# ============================================================
# 5. clarity.md 例 A 的口径说明（消除「阈值 vs 例外」的表面冲突）
# ============================================================
s = R("library/clarity.md")
if s and "例 A 的口径说明" not in s:
    s = s.replace("> **为什么不是 ∏cᵢ**",
        """### 例 A 的口径说明（v2.5）

`U = 0.311` 略高于阈值 0.30，但**最终判「放行」** —— 这不是矛盾，而是**两层判定**：

1. **第一层（必要性）**：`O` `T` `D` 三关键槽位**齐全** → 具备放行条件
2. **第二层（补充性）**：算得的 `U` 用于**判断次要槽位缺失是否影响执行**
   —— `U` 略高但缺口都在 `W/C/B`，不影响本次答疑 → 仍放行

**简记：关键槽齐 = 放行；关键槽缺 = 追问，`U` 只用于缺哪个槽时的取舍。**

> **为什么不是 ∏cᵢ**""", 1)
    W("library/clarity.md", s); n += 1

# ============================================================
# 6. selfcheck 阈值断言加强（覆盖所有变体）
# ============================================================
s = R("scripts/selfcheck.sh")
if s and "_bad_th=$(grep -rlE" in s:
    s = s.replace(
        '_bad_th=$(grep -rlE "U (≤|<=) 5%|threshold: 0\\.05" --include=\'*.md\' --include=\'*.yaml\' \\\n  . 2>/dev/null',
        '_bad_th=$(grep -rlE "5%|threshold: 0\\.05|U ≈ 0\\.05" --include=\'*.md\' --include=\'*.yaml\' --include=\'*.html\' \\\n  . 2>/dev/null')
    W("scripts/selfcheck.sh", s); n += 1

print("阶段 7（决定性收尾）完成：改动 %d 处" % n)
print("  阈值变体(>5%%/&gt;5%%/≈0.05) · **19 个 skill 的 ../../external.md 路径** · 版本 %s" % VER)
print("  S2/S3 skill 红线 · 只做四件事 · checklist 19 域 · 【假设】触发条件 · 消歧补 2 组 · clarity 例A 口径")
