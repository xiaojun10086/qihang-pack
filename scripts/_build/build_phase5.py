#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.4 · 「连小理 = LearnBuddy」定位校正层（build_phase5.py）

背景：包内此前把「连小理」当作与 LearnBuddy 并列的独立平台（赛道平台），属定位错误。
事实：**连小理就是 LearnBuddy**（LearnBuddy 在赛道二场景中的产品名），二者不是两个平台。
本层把全部引用合并为同一平台，并删除重复的独立平台行/节。

顺序：v2 → extras → phase1 → phase2 → phase3 → phase4 → **phase5** → selfcheck
"""
import os, sys, io, re, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"

def R(rel):
    p = os.path.join(OUT, rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)

# 统一称谓：LearnBuddy（连小理）
CANON = "LearnBuddy（连小理）"

REPL = [
    # ---- 平台并列写法：合并为一个 ----
    ("适配：连小理 / Claude Code / Codex / Cursor / Copilot",
     "适配：**LearnBuddy（= 连小理）** / Claude Code / Codex / Cursor / Copilot"),
    ("**其他平台**（Codex / Gemini CLI / Cursor / Copilot / 连小理）见",
     "**其他平台**（Codex / Gemini CLI / Cursor / Copilot）见"),
    ("+ Claude Code / Codex / Gemini CLI / Cursor / Copilot / 连小理",
     "+ Claude Code / Codex / Gemini CLI / Cursor / Copilot"),
    # ---- 赛道平台行：改名为同平台 ----
    ("| 连小理（赛道平台） | 平台内挂载 | 平台决定 | 自然语言 | 平台决定 | 🟡 结构已对齐 |",
     "| **连小理**（= LearnBuddy，赛道二场景名） | 见上（同一平台） | 同 LearnBuddy | 同 LearnBuddy | 同 LearnBuddy | ✅ 一等公民 |"),
    ("| 连小理                        | 平台挂载                              | 自然语言     | 平台决定                                                   | 🟡 结构已对齐 |",
     "| **连小理**（= LearnBuddy）      | 同 LearnBuddy（同一平台）              | 自然语言     | 同 LearnBuddy                                              | ✅ 一等公民   |"),
    ("| 连小理 | 🟡 结构已对齐 |",
     "| **连小理**（= LearnBuddy） | ✅ 一等公民（同一平台，非独立适配） |"),
    # ---- HTML 表述 ----
    ("依托平台：<b>连小理</b>（大连理工大学 × 腾讯）",
     "依托平台：<b>LearnBuddy</b>（赛道二场景名「连小理」，大连理工大学 × 腾讯）"),
    ("<b>新场景拓展</b> —— 连小理现有能力以单点问答为主；",
     "<b>新场景拓展</b> —— LearnBuddy 现有能力以单点问答为主；"),
    ("连小理现有能力以单点问答为主",
     "LearnBuddy 现有能力以单点问答为主"),
    # ---- 泛化兜底 ----
    ("连小理（赛道平台）", "连小理（= LearnBuddy）"),
    ("适配：连小理", "适配：LearnBuddy（= 连小理）"),
    ("/ 连小理", ""),          # 清掉并列尾巴
    ("、连小理", ""),
    ("连小理 / ", ""),
]

# INSTALL.md：把独立的「连小理」小节合并进 LearnBuddy 小节
INSTALL_OLD_SEC = re.compile(r"## 五、连小理（赛道平台）\n\n.*?(?=\n## |\Z)", re.S)
INSTALL_MERGE = """## 五、赛道二提交物（依托平台 = LearnBuddy，产品名「连小理」）

> **连小理就是 LearnBuddy**，不是两个平台 —— 本包在赛道二中的场景名即「连小理」。

1. 提交 **`qihang-scenario-design.html`**（场景设计书，五要素齐备，约 1900 字）
2. 平台侧挂载：`domains/_registry.md`（域总表）+ `library/` 规则 + `references/dlut-*.md`（信息库）
3. 场景与结构见 `PROJECT.md`

安装与使用**完全按第一节（LearnBuddy / WorkBuddy）**即可，无需另做适配。

"""

# platforms.md：删除独立的「连小理」小节
PLAT_OLD_SEC = re.compile(r"\| \*\*连小理\*\* \| 把 `domains/_registry\.md`.*?\n", re.S)

def canon_all():
    n = 0
    files = glob.glob(os.path.join(OUT, "**", "*.md"), recursive=True) + \
            glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True) + \
            glob.glob(os.path.join(OUT, "**", "*.yaml"), recursive=True)
    for p in files:
        if "/_build/" in p or "__pycache__" in p or p.endswith(".selfcheck.tmp"):
            continue
        rel = os.path.relpath(p, OUT)
        s = R(rel)
        if s is None or "连小理" not in s:
            continue
        o = s
        # 先做文件特化替换
        if rel == "INSTALL.md":
            s = INSTALL_OLD_SEC.sub(INSTALL_MERGE, s)
        if rel == "references/platforms.md":
            s = PLAT_OLD_SEC.sub("", s)
        for a, b in REPL:
            s = s.replace(a, b)
        # 兜底：剩余「连小理」一律标注等同
        s = re.sub(r"(?<!（)连小理(?!）)", CANON, s)
        s = s.replace("LearnBuddy（连小理）（= LearnBuddy）", CANON)
        s = s.replace("LearnBuddy（连小理）LearnBuddy（连小理）", CANON)
        s = s.replace("（LearnBuddy（连小理））", "（连小理）")
        if s != o:
            W(rel, s); n += 1
    return n

def fix_canon_forms():
    """收敛各种混写形式为统一写法"""
    n = 0
    for p in glob.glob(os.path.join(OUT, "**", "*.md"), recursive=True) + \
             glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        if "/_build/" in p or "__pycache__" in p:
            continue
        rel = os.path.relpath(p, OUT); s = R(rel)
        if not s or "连小理" not in s:
            continue
        o = s
        for a, b in [
            ("LearnBuddy（连小理）（= LearnBuddy）", CANON),
            ("LearnBuddy（连小理） = LearnBuddy", CANON),
            ("**LearnBuddy（连小理）**（= 连小理）", "**" + CANON + "**"),
            ("LearnBuddy（连小理） / Claude Code", CANON + " / Claude Code"),
            ("（连小理）（连小理）", "（连小理）"),
            ("连小理（连小理）", "连小理"),
            # ---- 兜底替换的过度应用：精确回收 ----
            ("产品名「LearnBuddy（连小理）」", "产品名「连小理」"),
            ("**LearnBuddy（连小理）就是 LearnBuddy**", "**连小理就是 LearnBuddy**"),
            ("场景名即「LearnBuddy（连小理）」", "场景名即「连小理」"),
            ("赛道二场景名「LearnBuddy（连小理）」", "赛道二场景名「连小理」"),
            ("**LearnBuddy（连小理）**（= LearnBuddy，赛道二场景名）", "**连小理**（= LearnBuddy，赛道二场景名）"),
            ("**LearnBuddy（连小理）**（= LearnBuddy）", "**连小理**（= LearnBuddy）"),
            ("| **LearnBuddy（连小理）** |", "| **连小理**（= LearnBuddy） |"),
            ("LearnBuddy（连小理）（= LearnBuddy，赛道二场景名）", "连小理（= LearnBuddy，赛道二场景名）"),
        ]:
            s = s.replace(a, b)
        if s != o:
            W(rel, s); n += 1
    return n

def main():
    a = canon_all()
    b = fix_canon_forms()
    print("阶段 5（连小理 = LearnBuddy 定位校正）：改动 %d 个文件" % (a + b))
    # 校验：不应再出现把两者并列的写法
    left = []
    for p in glob.glob(os.path.join(OUT, "**", "*.md"), recursive=True) + \
             glob.glob(os.path.join(OUT, "**", "*.html"), recursive=True):
        if "/_build/" in p:
            continue
        s = io.open(p, encoding="utf-8").read()
        for bad in ("连小理（赛道平台）", "/ 连小理", "、连小理", "连小理 / Claude"):
            if bad in s:
                left.append((os.path.relpath(p, OUT), bad))
    if left:
        print("  ⚠ 仍需人工确认：")
        for f, b in left:
            print("    %s : %s" % (f, b))
    else:
        print("  ✅ 已无「把连小理当作独立平台」的并列写法")

if __name__ == "__main__":
    main()
