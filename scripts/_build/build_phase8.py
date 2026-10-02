#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.5 · 最终去重与统一层（build_phase8.py）

第 5 轮终验暴露的根因：**分层补丁只「加」不「去重」**，导致
  · 红线条目在域文件/skill 中重复甚至互相冲突
  · 版本号在不同书写格式下未同步（`version: X` vs `"version": "X"` vs `vX`）
  · 配置键引用写错（`clarify.*` 实为 `library.clarity.*`）

本层做**去重 + 全格式统一 + 引用校正**，并给 selfcheck 加去重断言。
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

n = 0
RED_HEAD = r"## ⚠️ (?:红线（不得绕过）|安全护栏与红线（不得绕过）|安全护栏（本域专属，不得绕过）)"

def dedupe_redlines(rel):
    """合并同一文件内所有红线段，条目去重（保持首次出现顺序）"""
    s = R(rel)
    if s is None: return 0
    blocks = re.findall(RED_HEAD + r"\n\n((?:- [^\n]*\n)+)", s)
    if not blocks:
        return 0
    items, seen = [], set()
    for b in blocks:
        for line in b.splitlines():
            k = line.strip()
            if k and k not in seen:
                seen.add(k); items.append(k)
    merged = "## ⚠️ 红线（不得绕过）\n\n" + "\n".join(items) + "\n\n"
    s2 = re.sub(RED_HEAD + r"\n\n(?:- [^\n]*\n)+\n?", "", s)
    if "## 输出" in s2:
        s2 = s2.replace("## 输出", merged + "## 输出", 1)
    else:
        s2 = s2.rstrip() + "\n\n" + merged
    # 只在「真的减少或改变」时写回
    if s2 != s:
        W(rel, s2); return 1
    return 0

def dedupe_all_redlines():
    k = 0
    for p in glob.glob(os.path.join(OUT, "domains", "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, OUT)
        k += dedupe_redlines(rel)
    return k
n += dedupe_all_redlines()

# ---- 全格式版本统一 ----
def allfiles():
    out = []
    for pat in ("**/*.md", "**/*.yaml", "**/*.html", "**/*.json",
                ".codebuddy-plugin/*.json"):
        for p in glob.glob(os.path.join(OUT, pat), recursive=True):
            r = os.path.relpath(p, OUT).replace("\\", "/")
            if "/_build/" in r or "__pycache__" in r:
                continue
            out.append(r)
    return sorted(set(out))

for rel in allfiles():
    if rel.startswith("references/review-report") or rel == "references/需求确认书-v2三级结构.md":
        continue
    s = R(rel)
    if s is None: continue
    o = s
    for a, b in [
        ("version: 2.4.0", "version: %s" % VER),
        ("version: 2.3.0", "version: %s" % VER),
        ("version: 2.2.0", "version: %s" % VER),
        ("version: 2.1.0", "version: %s" % VER),
        ('"version": "2.4.0"', '"version": "%s"' % VER),
        ('"version": "2.3.0"', '"version": "%s"' % VER),
        ("学伴包 v2.4", "学伴包 v2.5"),
        ("学伴包 v2.5 三级结构", "学伴包 v2.5 三级结构"),
        ("（v2.4 新增）", "（v2.5 新增）"),
        ("（v2.4 修订）", "（v2.5 修订）"),
        # 配置键引用校正
        ("`config.yaml` 的 `clarify.threshold`", "`config.yaml` 的 `library.clarity.threshold`"),
        ("`config.yaml` 的 `clarify.weights`", "`config.yaml` 的 `library.clarity.weights`"),
        ("`config.yaml` 的 `clarify.ask_priority`", "`config.yaml` 的 `library.clarity.ask_priority`"),
        ("`config.yaml` 的 `clarify.", "`config.yaml` 的 `library.clarify."),
        # checklist 域数
        ("## 二、域专属附加校验（16 域）", "## 二、域专属附加校验（覆盖 19 域）"),
        # 红线总览 F2 归属
        ("| **代操作** | F1 F2 F4 R3 R4 |", "| **代操作** | F1 F4 R3 R4 |"),
        ("- **不为学业规划代劳**（→`S4`）", "- **不为学业规划代劳**（→`S4`，属职责边界非系统操作）"),
    ]:
        s = s.replace(a, b)
    if s != o:
        W(rel, s); n += 1

# ---- F1 skill 与域文件的「钱」表述统一 ----
n += 1 if (lambda: (W("domains/F1-campus-affairs/skills/local/campus-desk/SKILL.md",
    (R("domains/F1-campus-affairs/skills/local/campus-desk/SKILL.md") or "")
    .replace("不涉及钱（→F4）", "不涉及**资金处置**（缴费/报销/止损 → `F4`）；网费与学费的**入口与流程**属本域")
    .replace("不涉及健康（→F5）；不涉及钱（→F4）", "不涉及健康（→`F5`）；不涉及**资金处置**（→`F4`）")
)) and True)() else 0

# ---- 危机用例输出补 24h 热线 ----
s = R("library/domain-review-cases.md")
if s and "12356" not in s:
    s = s.replace("立即给心理中心（https://xinli.dlut.edu.cn/）与 i大工 APP 预约入口，建议马上联系辅导员",
                  "立即给 **24h 通道**（全国心理援助热线 12356 / 北京 010-82951332）与心理中心 https://xinli.dlut.edu.cn/；"
                  "**若已有具体计划 → 110 / 120**；停止其他一切建议")
    W("library/domain-review-cases.md", s); n += 1

# ---- 消歧表去重行 ----
s = R("domains/_registry.md")
if s:
    lines = s.split("\n"); seen, out = set(), []
    for l in lines:
        if l.startswith("| **") and l in seen:
            continue
        if l.startswith("| **"):
            seen.add(l)
        out.append(l)
    if out != lines:
        W("domains/_registry.md", "\n".join(out)); n += 1

# ---- 设计书版本标注 ----
s = R("qihang-scenario-design.html")
if s:
    o = s
    s = s.replace("（v2.0）", "（v2.5）").replace("v2.0 三级结构", "v2.5 三级结构")
    if s != o:
        W("qihang-scenario-design.html", s); n += 1

# ---- selfcheck 加「红线去重」断言 ----
s = R("scripts/selfcheck.sh")
if s and "红线去重" not in s:
    s = s.replace('echo "[7] 计数一致性"', '''echo "[6.6] 红线去重与版本一致性（v2.5 新增）"
_dup=0
for f in $(find domains -name '*.md' -not -path '*/dev/*' 2>/dev/null); do
  _c=$(grep -c '^## ⚠️ 红线（不得绕过）' "$f" 2>/dev/null || echo 0)
  [ "${_c:-0}" -gt 1 ] && { bad "红线段重复: $f（$_c 段）"; _dup=$((_dup+1)); }
done
[ "$_dup" -eq 0 ] && ok "无重复红线段"
# 红线条目内部去重检查
_dupitem=0
for f in $(find domains -name 'SKILL.md' -path '*skills/local*' 2>/dev/null); do
  _d=$(grep -E '^- ' "$f" 2>/dev/null | sort | uniq -d | wc -l | tr -d ' ')
  [ "${_d:-0}" -gt 0 ] && { bad "红线条目重复: $f（$_d 条）"; _dupitem=$((_dupitem+1)); }
done
[ "$_dupitem" -eq 0 ] && ok "红线条目无重复"
_vs=$(grep -rhoE 'version: [0-9.]+' --include='SKILL.md' . 2>/dev/null | sort -u | tr '\\n' ' ')
echo "   ℹ 库内 skill 版本: $_vs"

echo "[7] 计数一致性"''')
    W("scripts/selfcheck.sh", s); n += 1

def dedupe_bullets_global():
    """同一文件内，完全相同的 `- ` 条目只保留首次出现（覆盖「安全护栏」与「红线」跨段重复）"""
    k = 0
    for p in glob.glob(os.path.join(OUT, "domains", "**", "*.md"), recursive=True):
        rel = os.path.relpath(p, OUT)
        s = R(rel)
        if s is None: continue
        lines = s.split("\n")
        seen, out, changed = set(), [], False
        for l in lines:
            if l.startswith("- ") and len(l.strip()) > 8:
                if l in seen:
                    changed = True
                    continue
                seen.add(l)
            out.append(l)
        if changed:
            W(rel, "\n".join(out)); k += 1
    return k
n += dedupe_bullets_global()

print("阶段 8（最终去重与统一）完成：改动 %d 处" % n)
print("  红线去重 · 全格式版本统一 %s · config 键引用校正 · checklist 19 域 · 危机用例补 24h · 消歧去重 · selfcheck 去重断言" % VER)
