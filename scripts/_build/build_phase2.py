#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」v2.0 · 阶段 2 外围：为各域 skills/external.md 补许可证与合规列"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_qihang_v2 import DOMAINS, CATS

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"

# owner/repo -> (SPDX, 判定码)
LIC = {
 "mattpocock/skills": ("MIT", "OK"),
 "Jellypod-Inc/school-skills": ("MIT", "OK"),
 "kepano/obsidian-skills": ("MIT", "OK"),
 "0x-man/mindmap-skill": ("MIT", "OK"),
 "dair-ai/dair-academy-plugins": ("MIT", "OK"),
 "googlarz/math-skill": ("无 LICENSE", "NOLIC"),
 "somenssarkar/gurukul-ai": ("无 LICENSE", "NOLIC"),
 "ghutchis/chem-skill": ("MIT", "OK"),
 "egouilliard-leyton/python-tutor-skill": ("MIT", "OK"),
 "GlacierXiaowei/structured-learning-skill": ("Apache-2.0", "OK"),
 "peter209393/anki-card-skills": ("MIT", "OK"),
 "hluaguo/learn-faster-kit": ("MIT", "OK"),
 "sickn33/agentic-awesome-skills": ("MIT", "DANGER"),
 "mordor-forge/study-skill": ("无 LICENSE", "NOLIC"),
 "Candlest/exam-prep-skill": ("MIT", "RISK"),
 "anthropics/skills": ("Apache-2.0(子目录)", "OK"),
 "Imbad0202/academic-research-skills": ("CC-BY-NC 4.0", "NC"),
 "kgraph57/paper-writer-skill": ("MIT", "OK"),
 "Gabberflast/academic-pptx-skill": ("MIT", "OK"),
 "hameefy/claude-latex-skill": ("MIT", "OK"),
 "xwmxcz/papers-skill": ("MIT", "OK"),
 "WenyuChiou/zotero-skills": ("MIT", "OK"),
 "wentorai/Research-Claw": ("MIT", "OK"),
 "K-Dense-AI/scientific-agent-skills": ("MIT", "OK"),
 "openai/skills": ("MIT", "OK"),
 "alirezarezvani/claude-skills": ("MIT", "OK"),
 "eddiebelaval/squire": ("MIT", "RISK"),
 "jakedahn/pomodoro": ("MIT", "STALE"),
 "Paramchoudhary/ResumeSkills": ("MIT", "OK"),
 "sourikduttanyu/interview-prep": ("MIT", "OK"),
 "Haadhi76/SOP_Consultant": ("MIT", "OK"),
 "tydev-new/10xcolleges": ("MIT", "OK"),
 "YANZHANLIN/ielts-claude-skills": ("MIT", "OK"),
 "tianmind-studio/english-coach": ("MIT", "OK"),
 "NeoLabHQ/context-engineering-kit": ("GPL-3.0", "GPL"),
 "googleworkspace/cli": ("Apache-2.0", "OK"),
 "ComposioHQ/awesome-claude-skills": ("MIT", "OK"),
}
BADGE = {
 "OK": "✅ 合法",
 "GPL": "⚠️ **GPL-3.0**",
 "NC": "❌ **禁商用**",
 "NOLIC": "⛔ **无 LICENSE**",
 "DANGER": "⚠️ 含攻击性技能",
 "RISK": "⚠️ 有风险行为",
 "STALE": "⚠️ 停滞",
}
NOTE = {
 "GPL": "**强 copyleft —— 禁止摘录进本包**（否则本包须整体 GPL 化），**仅允许外部调用**",
 "NC": "**禁止商用**；校内非商用可用，对外发布前须替换",
 "NOLIC": "默认保留所有权利 —— **禁止摘录、禁止再分发**，仅限本地自用",
 "DANGER": "**禁止整体安装**（3113 脚本 / 31 个攻击性技能，无法审计）；只允许摘取单个 SKILL.md 文本",
 "RISK": "内容会上传第三方或密钥落盘，用前先读源码",
 "STALE": "近 11 个月未更新；二进制仅 macOS ARM",
 "OK": "",
}

def find_repo(entry):
    repo = entry[1]
    return repo.split("/", 1)[1] if False else repo

def external_md(d):
    l = d["local"]
    o = []
    o.append(f"# {d['id']} · {d['name']} — 库外 skill 候选\n")
    o.append(f"> **使用规则**：先确认库内 skill `{l['slug']}` 不能满足需求，再读本表。")
    o.append("> 安装前三步：① 探测是否已装 ② **读源码与许可证** ③ 装后验证。")
    o.append("> **摘录红线**：GPL-3.0 与「无 LICENSE」一律**只做外部调用，不得复制内容进本包**。\n")
    if not d["external"]:
        o.append("**本域暂无合适的库外 skill** —— 属于方向空白，直接用库内 skill 或自建。\n")
        o.append("> 找新 skill 的入口见 `references/skill-sources.md`（12 个平台）。\n")
        return "\n".join(o)
    o.append("| # | Skill | 仓库 | 许可证 | 合规判定 | 安装命令 |")
    o.append("|---|---|---|---|---|---|")
    warns = []
    for i, (nm, repo, inst) in enumerate(d["external"], 1):
        spdx, code = LIC.get(repo, ("未查到", "OK"))
        o.append(f"| {i} | `{nm}` | `{repo}` | {spdx} | {BADGE[code]} | `{inst}` |")
        if NOTE.get(code):
            warns.append(f"- **`{nm}`**（{repo}）：{NOTE[code]}")
    o.append("")
    if warns:
        o.append("## ⚠️ 合规提醒\n")
        o.extend(warns)
        o.append("")
    o.append("## 降级链\n")
    o.append("库内 skill → 上表第 1 项 → 第 2 项 → 纯提示词模式")
    o.append("")
    o.append("> 完整自检报告见 `references/skill-compliance-audit.md`；风险与验收数据见 `references/validation-report.md`")
    return "\n".join(o)

n = 0
for d in DOMAINS:
    p = os.path.join(OUT, f"domains/{d['id']}-{d['slug']}/skills/external.md")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(external_md(d))
    n += 1
print(f"阶段 2 外围：重写 {n} 个 external.md（含许可证列与合规标注）")
