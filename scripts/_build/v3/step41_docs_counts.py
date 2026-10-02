# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.0.0 生成链 · 第 9 层 · 文档计数级联】文档口径级联：52 个库内 skill → 92 ｜ 每域 2–3 → 4–5 ｜ 自建 40 → 自建 80
# 原名 gen_docs_counts.py（v3.0.0 期间的一次性脚本，本次收编入库，语义未改）
# 用法：python scripts/_build/v3/<file> [仓库根]        默认 = 仓库根
# 在已达 92 的树上重跑全部为 MISS（无害）
# 幂等：在已达 v3.0.0 的树上重跑应零变更（见同目录 README.md）
# -------------------------------------------------------------------------------
"""文档计数级联：52 → 92 ｜ 每域 2–3 → 4–5 ｜ 自建 40 → 自建 80。"""
import io, os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
FILES = [
    'INSTALL.md',
    'README.md',
    'THIRD_PARTY_NOTICES.md',
    'references/platforms.md',
    'references/skill-compliance-audit.md',
    'references/skill-selection-matrix.md',
]
# 有序替换（长的先替换，避免子串互相吃掉）
RULES = [
    ('所有能力由 `domains/*/skills/local/` 下的 **52 个库内 skill** 承接',
     '所有能力由 `domains/*/skills/local/` 下的 **92 个库内 skill** 承接'),
    ('| 来源 | 自建 40 个 + 由 MIT/Apache 许可外部最优解「骨架提取 + 重写」12 个 |',
     '| 来源 | 自建 80 个 + 由 MIT/Apache 许可外部最优解「骨架提取 + 重写」12 个 |'),
    ('`[2级] 20 个域 / **52 个**库内 skill`',
     '`[2级] 20 个域 / **92 个**库内 skill`'),
    ('（52 个，零外部依赖）', '（92 个，零外部依赖）'),
    ('20 域 × **52 个库内 skill**（每域 2–3 个）= **自建 40 + 改造 12**',
     '20 域 × **92 个库内 skill**（每域 4–5 个）= **自建 80 + 改造 12**'),
    ('库内 52 个 skill 均可离线直接使用', '库内 92 个 skill 均可离线直接使用'),
    ('`domains/*/skills/local/` 下 **52 个**（自建 40 + 由 MIT/Apache 许可外部最优解重写 12）',
     '`domains/*/skills/local/` 下 **92 个**（自建 80 + 由 MIT/Apache 许可外部最优解重写 12）'),
    ('对象：本包 **52 个库内 skill** 的来源素材', '对象：本包 **92 个库内 skill** 的来源素材'),
    ('| 库内 skill 总数 | **52 个**（每域 2–3 个） |', '| 库内 skill 总数 | **92 个**（每域 4–5 个） |'),
    ('- 库内 **52 个 skill** = **自建 40 个** + **由外部开源最优解「骨架提取 + 重写」而来 12 个**。',
     '- 库内 **92 个 skill** = **自建 80 个** + **由外部开源最优解「骨架提取 + 重写」而来 12 个**。'),
    ('## 4. 优化基线（现有 52 个 skill 一并执行）',
     '## 4. 优化基线（现有 52 个 skill 已一并执行：方法库 + 第二示例 + DUT 特化加深）'),
]

for rel in FILES:
    p = os.path.join(ROOT, rel)
    with io.open(p, 'r', encoding='utf-8') as f:
        t = f.read()
    orig = t
    hits = []
    for a, b in RULES:
        if a in t:
            t = t.replace(a, b)
            hits.append(a[:28])
    if t != orig:
        with io.open(p, 'w', encoding='utf-8', newline='\n') as f:
            f.write(t)
    print('%-46s 改动 %d 处 %s' % (rel, len(hits), hits if hits else '（无）'))
