#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」v2.3 · 全局一致性同步层（build_phase4.py）

来源：第二轮 3 路回归复核。核心发现——v2.2 的修复**只落在单文件**，
导致「0.30 与 5% 并存」「权重双口径」，P0-1 实际未闭环。
本层做全局收口：单一真相源 + 消除残留 + 幂等去重。

顺序：v2 → extras → phase1 → phase2 → phase3 → **phase4** → selfcheck
"""
import os, sys, re, io, glob

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
VER = "2.3.0"

def path(rel): return os.path.join(OUT, rel)
def R(rel):
    p = path(rel)
    return io.open(p, encoding="utf-8").read() if os.path.exists(p) else None
def W(rel, s):
    p = path(rel)
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
def alltext(patterns):
    out = []
    for pat in patterns:
        for p in glob.glob(os.path.join(OUT, pat), recursive=True):
            if "/_build/" in p or "__pycache__" in p:
                continue
            out.append(p)
    return sorted(set(out))

# ============================================================
# A. 单一真相源：阈值与权重
# ============================================================
THRESHOLD = "0.30"
WEIGHTS   = "O=1.5  T=1.5  D=1.5   W=0.8  C=0.6   B=0.2"

THRESH_REPL = [
    ("U ≤ 5% 才继续", "U ≤ 0.30 才继续"),
    ("U ≤ 5%）",      "U ≤ 0.30）"),
    ("U ≤ 5%",        "U ≤ 0.30"),
    ("U > 5%",        "U > 0.30"),
    ("U >  5%",       "U > 0.30"),
    ("不确定度 > 5%",  "不确定度 > 0.30"),
    ("不确定度高于 5%", "不确定度高于 0.30"),
    ("不确定度高于5%",  "不确定度高于 0.30"),
    ("阈值 5%",        "阈值 0.30"),
    ("threshold: 0.05", "threshold: 0.30"),
    ("threshold: 0.05 ", "threshold: 0.30 "),
]

def sync_threshold():
    n = 0
    for p in alltext(["*.md", "*.yaml", "*.json", "domains/**/*.md", "library/*.md"]):
        s = R(os.path.relpath(p, OUT))
        if s is None: continue
        o = s
        for a, b in THRESH_REPL:
            s = s.replace(a, b)
        if s != o:
            W(os.path.relpath(p, OUT), s); n += 1
    return n

# ============================================================
# B. config.yaml 对齐（权重 / 敏感域 / 版本）
# ============================================================
def fix_config():
    s = R("config.yaml")
    if not s: return 0
    n = 0
    if "weights: {W: 3.0" in s:
        s = s.replace(
            "threshold: 0.05",
            "threshold: 0.30            # ★ 单一真相源：全域文件与 skill 均引用此值")
        s = s.replace(
            "weights: {W: 3.0, O: 2.5, D: 2.0, C: 1.5, B: 1.0, T: 0.5}",
            'weights: {O: 1.5, T: 1.5, D: 1.5, W: 0.8, C: 0.6, B: 0.2}\n'
            '    ask_priority: {W: 3.0, O: 2.5, D: 2.0, C: 1.5, B: 1.0, T: 0.5}')
        n += 1
    if "never_write_sensitive: [F3]" in s:
        s = s.replace("never_write_sensitive: [F3]  # 不写入档案的敏感域",
                      "never_write_sensitive: [F3, F5]   # 整域不写入档案（F3 身心 / F5 健康）\n"
                      "    partial_write_sensitive: [F4, F6] # 排除敏感字段后写入（金额债务 / 伤病）")
        n += 1
    W("config.yaml", s)
    return n

# ============================================================
# C. clarity.md：权重与优先级口径分离
# ============================================================
def fix_clarity():
    s = R("library/clarity.md")
    if not s: return 0
    n = 0
    if "权重：O=1.5" not in s:
        s = re.sub(r"权重：.*?（与 config\.yaml 的 clarify\.weights 一致；关键槽位权重更高）",
                   "**权重（单一真相源＝`config.yaml` 的 `clarify.weights`）**：%s" % WEIGHTS + "\n（关键槽位权重更高，故 O/T/D 齐全即可放行）",
                   s, flags=re.S)
        n += 1
    # §4 优先级明确标注为「优先级分」而非权重
    s = s.replace(
        "`时间 W(3.0) > 对象 O(2.5) > 产出 D(2.0) > 约束 C(1.5) > 背景 B(1.0) > 任务 T(0.5)`",
        "`时间 W(3.0) > 对象 O(2.5) > 产出 D(2.0) > 约束 C(1.5) > 背景 B(1.0) > 任务 T(0.5)`\n\n"
        "> ⚠️ 上表是**追问优先级分**（决定「先问哪个」），**不是** §3 的公式权重，两者不要混用。\n"
        "> 优先级分来自 `config.yaml` 的 `clarify.ask_priority`。")
    # 阈值标注单一真相源
    s = s.replace("阈值：U ≤ 0.30 → 放行", "阈值（单一真相源＝`config.yaml` 的 `clarify.threshold`）：U ≤ 0.30 → 放行")
    # 示例重算保证与权重自洽
    s = re.sub(r"`Σ wᵢcᵢ = 1\.5\+1\.5\+1\.2 = 4\.2` ｜ `Σ wᵢ = 1\.5\+1\.5\+1\.5\+0\.8\+0\.6\+0\.2 = 6\.1`\n`U = 1 − 4\.2/6\.1 = 0\.311`",
               "`Σ wᵢcᵢ = 1.5×1.0 + 1.5×1.0 + 1.5×0.8 = 4.2`\n"
               "`Σ wᵢ = 1.5+1.5+1.5+0.8+0.6+0.2 = 6.1`\n"
               "`U = 1 − 4.2/6.1 = 0.311`", s)
    W("library/clarity.md", s)
    return n

# ============================================================
# D. 域文件：执行顺序前置「判红线」
# ============================================================
EXEC_OLD = re.compile(
    r"## 执行顺序\n\n"
    r"1\. 1 级库完成\*\*需求明确\*\*（`library/clarity\.md`），U ≤ 0\.30 才继续\n"
    r"2\. 1 级库完成\*\*域审查\*\*，确认命中 `([^`]+)`（`library/domain-review\.md`）\n"
    r"3\. 用\*\*库内 skill\*\* `([^`]+)` 执行（首选）\n"
    r"4\. 库内不满足 → 读 `skills/external\.md` 走库外安装\n"
    r"5\. 按 `library/output-spec\.md` 输出，([^\n]*)\n")

def fix_exec_order():
    n = 0
    for p in glob.glob(os.path.join(OUT, "domains", "*", "_domain.md")):
        rel = os.path.relpath(p, OUT)
        s = R(rel)
        if not s or "0. **先判红线**" in s: continue
        m = EXEC_OLD.search(s)
        if not m: continue
        did, slug, tail = m.group(1), m.group(2), m.group(3)
        new = (
            "## 执行顺序\n\n"
            "0. **先判红线**（见上节 `## ⚠️ 红线`）—— 命中则**拒绝并给合规替代**，**不追问**\n"
            "1. 1 级库完成**需求明确**（`library/clarity.md`），U ≤ 0.30 才继续\n"
            "2. 1 级库完成**域审查**，确认命中 `%s`（`library/domain-review.md`）\n"
            "3. 用**库内 skill** `%s` 执行（首选）\n"
            "4. 库内不满足 → 读 `skills/external.md` 走库外安装\n"
            "5. 按 `library/output-spec.md` 输出，%s\n" % (did, slug, tail))
        s = s[:m.start()] + new + s[m.end():]
        W(rel, s); n += 1
    return n

# ============================================================
# E. phase3 幂等修复：去重红线块
# ============================================================
def dedupe_redlines():
    n = 0
    for p in glob.glob(os.path.join(OUT, "domains", "*", "skills", "local", "*", "SKILL.md")):
        rel = os.path.relpath(p, OUT)
        s = R(rel)
        if not s: continue
        # 合并多个「## ⚠️ 红线（不得绕过）」小节为 1 个，条目去重
        blocks = re.findall(r"## ⚠️ 红线（不得绕过）\n\n((?:- [^\n]*\n)+)", s)
        if len(blocks) <= 1:
            continue
        items, seen = [], set()
        for b in blocks:
            for line in b.splitlines():
                k = line.strip()
                if k and k not in seen:
                    seen.add(k); items.append(k)
        s = re.sub(r"## ⚠️ 红线（不得绕过）\n\n(?:- [^\n]*\n)+\n?", "", s)
        s = s.replace("## 输出", "## ⚠️ 红线（不得绕过）\n\n" + "\n".join(items) + "\n\n## 输出", 1)
        W(rel, s); n += 1
    return n

# ============================================================
# F. F3 补 24h 通道
# ============================================================
F3_OLD = "- **危机信号**（自伤/自杀念头、持续失眠、情绪失控）→ **立即转介并停止其他一切建议**"
F3_NEW = ("- **危机信号**（自伤/自杀念头、持续失眠、情绪失控）→ **立即转介并停止其他一切建议**，"
          "并给 **24h 可用通道**：**全国心理援助热线 12356** / 北京 010-82951332\n"
          "- **若已有具体计划（备药、选定地点、写告别留言）→ 立即拨打 110 或 120**，"
          "不得只给非 24h 的校内资源")

def fix_f3():
    n = 0
    for rel in ["domains/F3-wellbeing/_domain.md",
                "domains/F3-wellbeing/skills/local/wellbeing-checkin/SKILL.md"]:
        s = R(rel)
        if not s or "12356" in s: continue
        if F3_OLD in s:
            s = s.replace(F3_OLD, F3_NEW); W(rel, s); n += 1
    return n

# ============================================================
# G. R3 排错循环统一为 5 步
# ============================================================
def fix_r3():
    n = 0
    for rel in ["domains/R3-research-tools/_domain.md",
                "domains/R3-research-tools/skills/local/tool-setup/SKILL.md"]:
        s = R(rel)
        if not s: continue
        o = s
        s = s.replace("复现 → 最小化 → 假设 → 验证", "复现 → 最小化 → 假设 → 插桩验证 → 修复")
        s = s.replace("复现 → 最小化 → 假设 → 插桩验证 → 修复 → 修复", "复现 → 最小化 → 假设 → 插桩验证 → 修复")
        s = s.replace("复现 → 最小化 → 假设 → 验证 → 修复", "复现 → 最小化 → 假设 → 插桩验证 → 修复")
        if s != o:
            W(rel, s); n += 1
    return n

# ============================================================
# H. output-spec 口径统一 + 过度拦截正面清单
# ============================================================
def fix_spec():
    s = R("library/output-spec.md")
    if not s: return 0
    n = 0
    s = s.replace(
        "**跨域串联**\n```\n每个域给 1 条结论（≤4 域）→ 末尾 1 张行动清单（≤5 行）\n上界 = 域数 + 1；超过 6 条时，把清单压缩进【步骤】的 5 个子项\n```\n"
        "> 4 域 + 清单 = 5 条 ≤ 6 ✅；5 域起必须压缩。",
        "**跨域串联**\n```\n每个域给 1 条结论（计入要点数）→ 末尾 1 张行动清单\n上界 = 域数 + 1 ≤ 6  →  域数上限 = 5\n```\n"
        "> **口径统一**：跨域时**各域结论计入要点数**（与 §1.1「除【结论】外的字段行」一致 ——\n"
        "> 此处每个域的结论即该域的【结论】字段，合并展示时计入）。4 域 + 清单 = 5 条 ✅；\n"
        "> **5 域须压缩**：把最弱的 1 条结论并入行动清单。")
    if n or True:
        if "## 7. 合规正面清单" not in s:
            s += """

---

## 7. 合规正面清单（v2.3 新增 · 防过度拦截）

> 红线只写「不能做什么」会导致误拦合规请求。以下为**明确放行**的请求类型。

| 请求 | 是否合规 | 依据 |
|---|---|---|
| 「给我完整解法，我自己对着学」 | ✅ 放行 | 自学场景；红线只禁「可直接提交的答案」 |
| 「我的报告结构搭得对吗」 | ✅ 放行 | 自查合规；红线只禁「代写正文」 |
| 「帮我核验这 5 条引文字段是否自洽」 | ✅ 放行 | 核验≠补全；红线只禁「未核验的引文」 |
| 「帮我看看效应量怎么算」 | ✅ 放行 | 统计方法咨询合规；红线只禁「造假与选择性报告」 |
| 「帮我逐条回复返修意见」 | ✅ 放行 | 返修辅助合规；红线只禁「代投稿」 |
| 「帮我改简历措辞」 | ✅ 放行 | 措辞优化合规；红线只禁「编造经历」 |
| 「网费还剩多少」 | ✅ 放行（L1） | L1 可读；只有「缴费金额明细」属 L3 |
| 「历年真题在教务处哪里下」 | ✅ 放行 | 公开资料路径；红线只禁「买卖答案」 |
| 「排这周复习时间表」 | ✅ 放行 | 时间安排≠学业规划代劳 |
| 「最近老失眠」（无危机信号） | ✅ 放行于 F3 | 红线只在**出现危机信号**时升级，不逢情绪就转心理 |

**判定口诀**：**给路径 / 给结构 / 给规范 → 放行；代产出 / 代操作 / 造数据 → 拦截。**
"""
            n += 1
    W("library/output-spec.md", s)
    return n

# ============================================================
# I. 计数与版本刷新 + 红线总览补 F2
# ============================================================
def fix_counts_and_version():
    n = 0
    cases = R("library/domain-review-cases.md")
    ncases = 0
    if cases:
        ncases = len(re.findall(r"^\|\s*\d+\s*\|", cases, flags=re.M))
        if "条用例" in cases:
            pass
    for rel in ["SKILL.md", "README.md", "PROJECT.md", "ROADMAP.md",
                "library/SKILL.md", "library/domain-review.md",
                "library/domain-review-cases.md", "library/output-checklist.md",
                "references/acceptance-v2.md"]:
        s = R(rel)
        if not s: continue
        o = s
        s = s.replace("14 条用例（含 3 反例）", "%d 条用例" % ncases)
        s = s.replace("14 条用例（含 3 条反例）", "%d 条用例" % ncases)
        s = s.replace("越界用例集（14 条，含 3 反例）", "越界用例集（%d 条）" % ncases)
        s = s.replace("14 条，含 3 条反例", "%d 条" % ncases)
        s = s.replace("（14 条，含 3 反例）", "（%d 条）" % ncases)
        s = s.replace("13 条", "%d 条" % ncases)
        s = s.replace("域专属校验从 4 域扩展到 **12 域**", "域专属附加校验覆盖 **16 域**")
        s = s.replace("从 4 域扩展到 **12 域**", "覆盖 **16 域**")
        s = s.replace("version: 2.1.0", "version: %s" % VER)
        s = s.replace("version: 2.2.0", "version: %s" % VER)
        s = s.replace("version: 2.0.0", "version: %s" % VER)
        s = s.replace("学伴包 v2.1", "学伴包 v2.3")
        s = s.replace("学伴包 v2.2", "学伴包 v2.3")
        s = s.replace("入口（v2.1）", "入口（v2.3）")
        s = s.replace("当前状态（v2.0）", "当前状态（v2.3）")
        s = s.replace("# 输出规范（Level 1 · output-spec）", "# 输出规范（Level 1 · output-spec）")
        if s != o:
            W(rel, s); n += 1
    # 库内 skill 版本
    for p in glob.glob(os.path.join(OUT, "domains", "*", "skills", "local", "*", "SKILL.md")):
        rel = os.path.relpath(p, OUT); s = R(rel)
        if s and "version: 2.1.0" in s:
            W(rel, s.replace("version: 2.1.0", "version: %s" % VER)); n += 1
    # 红线总览补 F2
    s = R("SKILL.md")
    if s and "红线总览" in s and "F2" not in s.split("红线总览")[1][:1200]:
        s = s.replace("| **代操作** | F1 F4 R3 R4 |",
                      "| **代操作** | F1 F2 F4 R3 R4 |")
        s = s.replace("**不为学业规划代劳**", "**不为学业规划代劳**")
        s = s.replace("- **L3 禁读**", "- **L3 禁读**")
        s = s.replace("| **L3 禁读** | 私密站 |",
                      "| **L3 禁读** | 私密站 |")
        s = s.replace("| **安全兜底** | F3 F4 F5 F6 |",
                      "| **安全兜底** | F2 F3 F4 F5 F6 |")
        W("SKILL.md", s); n += 1
    return n, ncases

def main():
    tot = 0
    a = sync_threshold(); tot += a
    b = fix_config();     tot += b
    c = fix_clarity();    tot += c
    d = fix_exec_order(); tot += d
    e = dedupe_redlines();tot += e
    f = fix_f3();         tot += f
    g = fix_r3();         tot += g
    h = fix_spec();       tot += h
    i, ncases = fix_counts_and_version(); tot += i
    print("阶段 4（全局一致性同步）完成：改动 %d 处" % tot)
    print("  A 阈值同步 %d 文件 ｜ B config 对齐 ｜ C clarity 权重 ｜ D 执行顺序前置红线 %d 域" % (a, d))
    print("  E 红线去重 %d ｜ F F3 补 24h %d ｜ G R3 统一 %d ｜ H 正面清单 ｜ I 计数/版本" % (e, f, g))
    print("  越界用例实际条数：%d" % ncases)

if __name__ == "__main__":
    main()
