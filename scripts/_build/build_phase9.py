#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.5 · 正则校正层（build_phase9.py）

第 6 轮终验暴露的最后一类问题：前几层用**精确字符串**替换，
一旦原文没有反引号/括号/空格就漏改。本层改用**正则灵活匹配**。
"""
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

def files(pats=("**/*.md", "**/*.yaml", "**/*.html", "**/*.json", ".codebuddy-plugin/*.json")):
    out = []
    for pat in pats:
        for p in glob.glob(os.path.join(OUT, pat), recursive=True):
            r = os.path.relpath(p, OUT).replace("\\", "/")
            if "/_build/" in r or "__pycache__" in r:
                continue
            out.append(r)
    return sorted(set(out))

n = 0
SKIP = ("references/review-report-v2.2.md", "references/review-report-v2.3.md",
        "references/需求确认书-v2三级结构.md")

RULES = [
    # ① config 键引用：允许有无反引号
    (re.compile(r"config\.yaml[`\s]*的[`\s]*clarify\.(weights|threshold|ask_priority)"),
     r"config.yaml 的 `library.clarity.\1`"),
    (re.compile(r"`config\.yaml`[`\s]*的[`\s]*`clarify\.(weights|threshold|ask_priority)`"),
     r"`config.yaml` 的 `library.clarity.\1`"),
    # ② 「16 域 / 12 域」→ 19 域（任意写法）
    (re.compile(r"覆盖 \*\*(?:16|12) 域\*\*"), "覆盖 **19 域**"),
    (re.compile(r"（(?:16|12) 域）"), "（覆盖 19 域）"),
    (re.compile(r"(?<![0-9])(?:16|12)\s*域(?![0-9])"), "19 域"),
    # ③ 旧版本号（任意上下文）
    (re.compile(r"（v2\.(?:0|1|2|3|4)）"), "（v%s）" % VER),
    (re.compile(r"v2\.(?:0|1|2|3|4)(?=[\s｜，。）]|$)"), "v%s" % VER),
    # ④ 「见上节」但红线在下文
    (re.compile(r"见上节 `## ⚠️ 红线`"), "见下文 `## ⚠️ 红线` 节"),
    (re.compile(r"（见上节 `## ⚠️ 红线`）"), "（见下文 `## ⚠️ 红线` 节）"),
    # ⑤ 子目录相对路径兜底
    (re.compile(r"(?<!/)\.\./external\.md"), "../../external.md"),
]

for rel in files():
    if rel in SKIP: continue
    s = R(rel)
    if s is None: continue
    o = s
    for rx, rep in RULES:
        s = rx.sub(rep, s)
    if s != o:
        W(rel, s); n += 1

# ⑥ 局部修补（S6 追问与假设冲突、commands 阈值示例、memory.md 引用）
def patch(rel, pairs):
    global n
    s = R(rel)
    if s is None: return
    o = s
    for a, b in pairs: s = s.replace(a, b)
    if s != o:
        W(rel, s); n += 1

patch("domains/S6-language/skills/local/lang-drill/SKILL.md", [
    ("**澄清判定**：弱项未知 → 追问 1 问后放行",
     "**澄清判定**：`O/T/D` 齐全（要冲 500 = 产出明确）→ 依 `clarity.md` §5 例外 2 **不追问**；弱项缺失属 `B`（可选槽），不作追问理由"),
])
patch("commands/qihang.md", [
    ("`U > 0.30` → 追问（最多 3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。",
     "`U > 0.30` **且关键槽位 O/T/D 有缺失** → 追问（≤3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。\n"
     "　（关键槽位齐全时直接放行，见 `library/clarity.md` §5 例外 2 与 §8 例 A。）"),
])
patch("domains/F4-money-safety/_domain.md", [
    ("并按 `library/memory.md` §4 红线排除敏感字段后写入",
     "并按 `library/memory.md` §4「禁止写入的域与内容」排除金额与债务后写入"),
])
patch("domains/F6-service/_domain.md", [
    ("并按 `library/memory.md` §4 红线排除敏感字段后写入",
     "并按 `library/memory.md` §4「禁止写入的域与内容」排除伤病记录后写入"),
])

print("阶段 9（正则校正）完成：改动 %d 个文件" % n)
print("  config 键引用 · 域数统一 19 · 版本正则统一 · 见下文章节 · 相对路径兜底 · S6/commands/memory 局部修补")
