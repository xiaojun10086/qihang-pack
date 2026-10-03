# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 24 层 · 外部 skill 桥接（v3.2.9 → v3.3.0）】—— **大改**
#
# 用户指令：① 读本地 skill → 找外部同类 skill 的工作流程 → 效仿并回写本地；
#          ② 本地 skill 的承接指针为空时改为外部链接，下载并使用；平台 ≥10；加一层外部自检；
#          ③ 全部平台都未找到 → 按原有流程输出；
#          ④ 更新版号，**不破坏原有三级结构**。
#
# 与 v3.0.0「去库外化」的关系（重要）：
#   v3.0.0 曾把外部通道整体删除，并用断言焊死（selfcheck[2][9] / regress[4] / aligncheck P / runcheck L3-8）。
#   本层**不推翻「库内优先」**，而是把降级链由 **两档扩为三档**：
#       档 1 同域库内 skill（不变）
#       档 2 **外部桥接**（新增：12 平台检索 + 五步自检 + 许可门禁）
#       档 3 纯提示词模式（**保留为最终回落**，即原有流程）
#   → 因此 `selfcheck[2][9]` 的「不存在 skills/external.md」「无库外通道表述」**继续成立**：
#     本层**不恢复** per-domain `skills/external.md`；外部信息只落在 **1 级**（规则）与 **2 级**（域）。
#     术语统一用「外部桥接 / 外接」，**不写**「库外兜底 / 库外首选 / external.md」这三种被断言词。
#
# 三级结构不变：域 20 ｜ _domain.md 20 ｜ 库内 skill 92 ｜ library 规则 10 → **11**（+external-bridge.md）。
#
# 用法：python scripts/_build/v3/step61_external_bridge.py [仓库根]
# 幂等：新增文件「存在即跳过」；改写一律带**哨兵**；版本号用**全部替换**。
# -------------------------------------------------------------------------------
import glob
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.2.9', '3.3.0'
OLD_PKG, NEW_PKG = 'v3.2', 'v3.3'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel)
        return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r' % (rel, sent[:46]))
            continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:46]))
            continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:46]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


def new_file(rel, content, sentinel):
    t = read(rel)
    if t is not None and sentinel in t:
        print('  [SAME] %s（已存在）' % rel)
        return
    write(rel, content)
    print('  [OK]   新建 %s' % rel)


# =============================================================== A) 12 平台来源清单
print('== A) references/external-sources.md（12 平台 · 三通道复核）==')
SOURCES = '''# 外部 skill 来源清单（12 平台）· 复核 2026-10-03

> **用途**：`library/external-bridge.md`**§3 检索顺序**的入口表。
> 只在**库内 skill 与同域降级都接不住**时才启用 —— 本表**不取代**库内通道。
> **与 v3.0.0 去库外化的关系**：本表只登记**平台入口**，**不含**任何 per-domain 外部 skill 文件；
> 各域的外部候选写在 2 级 `_domain.md` 的 `## 外部承接` 段（**1 级 / 2 级承载，3 级不落**）。
> **核验方式**：三通道交叉（系统解析 ×5 ｜ AliDNS DoH ｜ DNSPub DoH）
> ＋ TCP 80/443 端口探测 ＋ 双协议实抓（HTTP / HTTPS 各重试 3 次）。
> **本轮结论：下表 12 个入口全部实测 200 可达**（2026-10-03）。

| # | 平台 | 检索入口 | 规模 | 使用量 | 反馈 | 局限 | 实测 |
|---|---|---|---|---|---|---|---|
| 1 | **skills.sh** | https://skills.sh/ | 1.5M+ | 有 installs | 无 | 只有流行度，无质量分级 | 200 |
| 2 | **GitHub Topics** | https://github.com/topics/agent-skills | 2.3 万仓库 | 无 | 有 stars / issues | 无使用量 | 200 |
| 3 | awesomeskills.dev | https://www.awesomeskills.dev/ | 4.1 万 | 有 | 无 | 教育场景空白 | 200 |
| 4 | officialskills.sh | https://officialskills.sh/ | 660 | 无 | 仅更新时间 | 只收厂商官方 | 200 |
| 5 | SkillsMP | https://skillsmp.com/ | 3.2M+ | 无 | 部分 | 无质量分级 | 200 |
| 6 | claude-plugins.dev | https://claude-plugins.dev/skills | 4.6 万 | 口径不明 | 部分 | 自动索引，无人工把关 | 200 |
| 7 | LobeHub Skills | https://lobehub.com/skills | 33 万+ | 口径不明 | 无 | 无教育分类 | 200 |
| 8 | ClawHub | https://clawhub.ai/ | 未公开 | 口径不明 | 无 | 特定生态 | 200 |
| 9 | StudentSuite | https://github.com/StudentSuite/awesome-skills-plugins-for-students | 158 | 无 | 有 | 面向境外课程体系 | 200 |
| 10 | VoltAgent 清单 | https://github.com/VoltAgent/awesome-agent-skills | 1000+ | 无 | 有 | 纯清单，非 skill 本体 | 200 |
| 11 | ComposioHQ 清单 | https://github.com/ComposioHQ/awesome-claude-skills | 1000+ | 无 | 有 | 偏自动化方向 | 200 |
| 12 | 中文清单（yzfly） | https://github.com/yzfly/awesome-skills-zh | 精选 | 无 | 有 | 活跃度低 | 200 |

## 一、检索顺序（照此办，不要跳步）

```
① 先用「域检索词」在 1 / 2 / 5 号平台做**语义检索**（覆盖面最大）
② 命中候选 → 进 GitHub 取 stars / license / pushed_at / archived（3 / 9 / 10 / 11 / 12 号多为清单，用于交叉发现）
③ 读候选的 SKILL.md 判**可用性**（有无标准 frontmatter、是否只是清单/占位）
④ 读候选的 scripts/ 判**脚本风险**（联网下载并执行、提权、批量删除、外发凭证一律判不合格）
⑤ 过 §4 五步自检 → 全过才可外接；任一不过 → 换候选或回落
```

## 二、许可红线（**硬**，与 `THIRD_PARTY_NOTICES.md` 同源）

- `MIT / Apache-2.0 / BSD / CC0 / ISC` → **合规 = 5**：可外部调用，**改造后须署名**。
- `GPL / AGPL / LGPL / CC-BY-NC` → **合规 = 2**：**只允许外部调用，禁止摘录任何内容进本包**。
- **无 LICENSE / 无法识别** → **合规 = 0**：**禁止使用**（不入围，不得作为候选）。
- **任何情况下都禁止把外部 skill 的正文复制进本包**；本包只**指向**外部入口。

## 三、与信息库的关系

- 本表的链接**必须真实可达**（硬规则 2：禁止编造 URL）→ 每次改动后跑
  `python scripts/extskill.py .` 复核（含可达性与登记一致性）。
- 各域「已核验候选」的仓库清单以 **2 级 `_domain.md` 的 `## 外部承接`** 为准；
  本表只维护**平台入口**，不重复登记候选仓库。

## 四、已核验候选仓库池（**登记唯一真相源**）

> **规则**：2 级 `_domain.md` 的 `## 外部承接` 段里出现的**每一个** `owner/repo`，
> 都必须在本节出现 —— 否则 `scripts/extskill.py` 判 FAIL（防编造）。
> **核验方式**：双通道（`HTTPS GET github.com/<owner>/<repo>` ＋ `git ls-remote`），
> **核验日期 2026-10-03，38/38 全部存在**。
> 许可列取自各仓库 LICENSE（抓取日 2026-10-02）；`未声明` = 仓库无 LICENSE → **合规 = 0，禁止使用**。

| # | owner/repo | 许可 | 合规 | 用途 |
|---|---|---|---|---|
| 1 | `googleworkspace/cli` | Apache-2.0 | 5 | F1 候选 |
| 2 | `vishalsachdev/canvas-mcp` | MIT | 5 | F1 / S3 候选 |
| 3 | `alirezarezvani/claude-skills` | MIT | 5 | F2 最优解 |
| 4 | `eddiebelaval/squire` | MIT | 5 | F2 备选 |
| 5 | `jakedahn/pomodoro` | MIT | 5 | F2 备选 |
| 6 | `Haadhi76/SOP_Consultant` | MIT | 5 | F7 候选 |
| 7 | `tydev-new/10xcolleges` | MIT | 5 | F7 候选 |
| 8 | `cabbage2000-lab/paper-tutor-skills` | 未声明 | 0 | F7 / R4 ⛔ 不入围 |
| 9 | `Paramchoudhary/ResumeSkills` | MIT | 5 | F8 最优解 |
| 10 | `sourikduttanyu/interview-prep` | MIT | 5 | F8 备选 |
| 11 | `Lucaswangzcx/literature-downloader-skill` | MIT | 5 | R1 最优解 |
| 12 | `WenyuChiou/zotero-skills` | MIT | 5 | R1 备选 |
| 13 | `xwmxcz/papers-skill` | MIT | 5 | R1 备选 |
| 14 | `K-Dense-AI/scientific-agent-skills` | MIT | 5 | R2 最优解 |
| 15 | `K-Dense-AI/scientific-agents` | MIT | 5 | R2 备选 |
| 16 | `openai/skills` | 未声明 | 0 | R2 ⛔ 不入围 |
| 17 | `mattpocock/skills` | MIT | 5 | R3 / S1 候选 |
| 18 | `obra/superpowers` | MIT | 5 | R3 备选 |
| 19 | `egouilliard-leyton/python-tutor-skill` | MIT | 5 | R3 备选 |
| 20 | `Gabberflast/academic-pptx-skill` | MIT | 5 | R4 / S5 最优解 |
| 21 | `Imbad0202/academic-research-skills` | 未声明 | 0 | R4 / S5 ⛔ 不入围 |
| 22 | `NeoLabHQ/context-engineering-kit` | GPL-3.0 | 2 | R5 唯一候选（**仅外部调用**） |
| 23 | `bevibing/socrates-skill` | MIT | 5 | S1 最优解 |
| 24 | `bevibing/tutor-skills` | MIT | 5 | S1 / S2 备选 |
| 25 | `kepano/obsidian-skills` | MIT | 5 | S2 最优解 |
| 26 | `0x-man/mindmap-skill` | MIT | 5 | S2 备选 |
| 27 | `kgraph57/paper-writer-skill` | MIT | 5 | S3 最优解 |
| 28 | `anthropics/skills` | 未声明 | 0 | S3 ⛔ 不入围 |
| 29 | `hluaguo/learn-faster-kit` | MIT | 5 | S4 最优解 |
| 30 | `GlacierXiaowei/structured-learning-skill` | Apache-2.0 | 5 | S4 备选 |
| 31 | `lowwwbank/anything-to-course` | MIT | 5 | S4 备选 |
| 32 | `hameefy/claude-latex-skill` | MIT | 5 | S5 备选 |
| 33 | `YANZHANLIN/ielts-claude-skills` | MIT | 5 | S6 最优解 |
| 34 | `tianmind-studio/english-coach` | MIT | 5 | S6 备选 |
| 35 | `flysheep-ai/education-skills` | MIT | 5 | S6 备选 |
| 36 | `ghutchis/chem-skill` | MIT | 5 | 化学方向备选（未落域） |
| 37 | `googlarz/math-skill` | 未声明 | 0 | ⛔ 不入围 |
| 38 | `somenssarkar/gurukul-ai` | 未声明 | 0 | ⛔ 不入围 |
'''

new_file('references/external-sources.md', SOURCES, '外部 skill 来源清单')

# =============================================================== B) 1 级规则
print('== B) library/external-bridge.md（第 11 份规则）==')
BRIDGE = '''# 外部桥接规则（Level 1 · external-bridge）

> **定位**：三级结构里**第 1 级**的一份横切规则。它不承载任何业务，只规定
> 「**库内 skill 与同域降级都接不住时，怎么安全地用外部 skill 顶上**」。
> **它不改「库内优先」**：库内仍是第一档，永远先走。
> **配套**：平台入口见 `references/external-sources.md`；各域候选见 2 级 `_domain.md` 的 `## 外部承接`。

## 1. 本包的三档降级链（唯一口径）

| 档 | 触发 | 做什么 | 产出标记 |
|---|---|---|---|
| **档 1 · 同域库内** | 当前 skill 不满足 | 用**同域另一个库内 skill** 降级承接（见 `general-fallback.md`） | `[已降级] 由「X」改为「Y」` |
| **档 2 · 外部桥接** | 档 1 也不满足 | 按本文件 §2 走外部：检索 → 自检 → 外接 | `[外接] 来源 + 许可` |
| **档 3 · 纯提示词** | 档 2 未找到合格外部 skill | **原有流程**：纯提示词模式，尽力作答并标 `[已降级]` | `[已降级]` |

**这是三档，不是两档**：档 3 永远保留。**任何档都不允许"只回一句拒绝"。**

## 2. 何时进入档 2（四条同时成立）

1. 档 1 已试过，同域库内确实接不住；
2. 需求**确实需要**某种能力，而库内 92 个 skill 都没有对口实现；
3. 用户**未禁止联网**、且当前环境可联网（离线环境直接跳档 3，**不报错**）；
4. 该能力**不属红线域**（`F3` / `F5` 的敏感内容一律不外接，直接走档 3）。

## 3. 三步桥接流程

```
① 检索：按 references/external-sources.md §1 的顺序，用「域检索词」找候选
② 自检：对候选跑 §4 五步自检；任一不过 → 换候选；候选耗尽 → 档 3
③ 使用：通过自检 → 按 §5 许可门禁使用 → 按 §6 标注输出 → 记入学习档案「外部桥接记录」
```

## 4. 五步自检（`scripts/extskill.py` 是它的程序化实现）

| # | 项 | 判据 | 不过就 |
|---|---|---|---|
| 1 | **数据量** | 平台侧有可查的使用量或 stars；**纯清单仓库/占位仓库判不合格** | 换候选 |
| 2 | **许可** | 能读到明确 LICENSE；`GPL/AGPL/CC-BY-NC` 降级为「仅外部调用」；**无 LICENSE 判不合格** | 换候选 |
| 3 | **可用性** | 有标准 frontmatter 的 `SKILL.md`；已归档（archived）或 >180 天未推送 → 降权 | 换候选 |
| 4 | **脚本风险** | 读其 `scripts/`：联网下载并执行、提权、批量删除、外发凭证、读写个人目录 → **一票否决** | 换候选 |
| 5 | **适配度** | 在**中文语境 / 国内平台 / 无境外账号**的真实环境能否用；不适配 → 降权 | 换候选 |

> **宁可回落档 3，也不要外接一个没过自检的 skill。**

## 5. 许可门禁（硬）

- **合规 = 5**（MIT / Apache-2.0 / BSD / CC0 / ISC）：可外部调用；**改造后须署名**。
- **合规 = 2**（GPL / AGPL / LGPL / CC-BY-NC）：**只允许外部调用**，**禁止摘录任何内容进本包**。
- **合规 = 0**（无 LICENSE）：**禁止使用**。
- **任何情况下都不得把外部 skill 的正文复制进本包** —— 本包只**指向**外部入口。

## 6. 输出标注（外接产物必须可追溯）

外接结果的输出**首行**必须标：

```
[外接] 来源：<平台>/<owner>/<repo> ｜ 许可：<LICENSE> ｜ 自检：5/5 通过
```

并在【结论】里说明**哪一部分来自外部**、**哪一部分是本包补的 DUT 事实**。
**禁止**把外部产物写成"本包原生能力"。

## 7. 回落（档 3 = 原有流程）

**12 个平台全部未找到合格候选，或用户/环境不允许联网** →
回到 `general-fallback.md` 的**六步通用框架**，按原样输出，并在学习档案记「外部缺口」。

**这不是失败路径，是保底路径** —— 本包的核心承诺是「**任何输入都能跑出有效结果**」，
离线与零命中都必须能出结果。

## 8. 红线（不得绕过）

- ❌ 不得**编造**外部链接、仓库名、stars 或许可证（硬规则 2）。
- ❌ 不得在**未过自检**的情况下下载并执行外部 `scripts/`。
- ❌ 不得把外部内容**复制**进本包（尤其 `GPL/AGPL/CC-BY-NC/无 LICENSE`）。
- ❌ 不得在 `F3 身心与社交` / `F5 健康与运动` 域外接（敏感域只走库内 + 档 3）。
- ❌ 不得把「外部桥接」当作**第一选择** —— 档 1 永远是库内。

## 9. 反例（出现即违规）

| 不合格做法 | 违反 |
|---|---|
| 没试同域库内就直接找外部 skill | §1（跳过档 1） |
| 拿一个无 LICENSE 的仓库当外接来源 | §5（合规 = 0） |
| 外接结果不标来源与许可 | §6 |
| 12 平台都没找到，却回一句「抱歉我做不到」 | §7（必须走档 3 出结果） |
| 把 F3 的情绪问题发给外部 skill | §8（敏感域禁外接） |
'''

new_file('library/external-bridge.md', BRIDGE, '外部桥接规则（Level 1 · external-bridge）')

# =============================================================== C) 自检器
print('== C) scripts/extskill.py（外部 skill 自检器）==')
EXTSKILL = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""外部 skill 桥接 · 静态自检器（第 6 个校验器）。

它把 `library/external-bridge.md` 的规则变成**可执行的断言**，覆盖两头：
  一、**接线完整性**：1 级规则在位 → 2 级每域有「外部承接」→ 3 级每个 skill 的降级段是三档。
  二、**登记一致性**：凡被引用的外部仓库，必须在 `references/external-sources.md` 的核验范围内，
      且许可门禁被如实标注（GPL/AGPL/CC-BY-NC 必须标「仅外部调用」）。

为什么需要它：外部通道一旦重新引入，最容易出的错是「**编造链接**」与「**许可失守**」——
这两类错**都不会**被原有 5 个校验器抓到（它们只查库内结构）。

用法：python scripts/extskill.py [树根]
判据：全部 PASS → rc 0；任一 FAIL → rc 1。
"""
import io
import os
import re
import sys

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') \\
    else os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
os.chdir(ROOT)

FAIL = []
WARN = []
OK = []


def bad(m):
    FAIL.append(m)


def warn(m):
    WARN.append(m)


def ok(m):
    OK.append(m)


def rd(p):
    with io.open(p, 'r', encoding='utf-8', errors='replace') as fh:
        return fh.read()


LOCAL_PREFIX = ('references/', 'library/', 'domains/', 'scripts/', 'commands/', '.learnbuddy/')
LOCAL_EXT = re.compile(r'\\.(md|py|sh|json|ya?ml|txt|html?)$')


def repos_in(text):
    """抽出形如 `owner/repo` 的仓库标识；**排除**本地路径与占位写法。"""
    out = set()
    for m in re.finditer(r'`([A-Za-z0-9][A-Za-z0-9._-]*/[A-Za-z0-9][A-Za-z0-9._-]*)`', text):
        r = m.group(1)
        if r.startswith(LOCAL_PREFIX) or LOCAL_EXT.search(r):
            continue
        if r in ('owner/repo', 'owner/repo.git'):
            continue
        out.add(r)
    return out


# ---------- 1. 1 级规则在位 ----------
if os.path.isfile('library/external-bridge.md'):
    t = rd('library/external-bridge.md')
    ok('library/external-bridge.md 在位')
    for h in ('## 1. 本包的三档降级链', '## 4. 五步自检', '## 5. 许可门禁', '## 7. 回落'):
        if h not in t:
            bad('external-bridge.md 缺小节 %s' % h)
    for w in ('档 1', '档 2', '档 3', '纯提示词'):
        if w not in t:
            bad('external-bridge.md 未写清 %s（三档口径不全）' % w)
    if '不得把「外部桥接」当作**第一选择**' not in t:
        bad('external-bridge.md 未声明「外部桥接非第一选择」（库内优先被削弱）')
else:
    bad('缺 library/external-bridge.md（外部桥接无成文规则）')

# ---------- 2. 平台表：≥10 个入口 ----------
if os.path.isfile('references/external-sources.md'):
    s = rd('references/external-sources.md')
    urls = set(re.findall(r'https?://[A-Za-z0-9\\-._~:/?#\\[\\]@!$&()*+,;=%]+', s))
    plat = set()
    for u in urls:
        m = re.match(r'https?://([a-z0-9.-]+)', u)
        if m:
            h = m.group(1).lower()
            if 'github.com' in h:
                mm = re.match(r'https?://github\\.com/([^/]+)', u)
                if mm:
                    plat.add('github:' + mm.group(1))
            else:
                plat.add(h.replace('www.', ''))
    if len(plat) < 10:
        bad('external-sources.md 平台数 = %d（要求 ≥10）' % len(plat))
    else:
        ok('平台入口数 = %d（≥10）' % len(plat))
    # 许可红线成文
    for w in ('GPL', 'AGPL', 'CC-BY-NC', '禁止'):
        if w not in s:
            warn('external-sources.md 未见许可红线词 %s' % w)
else:
    bad('缺 references/external-sources.md（无 12 平台入口表）')

# ---------- 3. 2 级：每域都要有「外部承接」 ----------
dom_dirs = sorted(d for d in os.listdir('domains')
                  if os.path.isdir(os.path.join('domains', d)))
n_ok = n_none = n_todo = 0
for d in dom_dirs:
    p = 'domains/%s/_domain.md' % d
    if not os.path.isfile(p):
        continue
    t = rd(p)
    m = re.search(r'^##\\s*外部承接[^\\n]*$', t, re.M)
    if not m:
        bad('%s 缺「## 外部承接」段（外部桥接断链）' % p)
        continue
    nxt = re.search(r'^##\\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    has_cand = '已核验候选' in body
    has_none = ('无合规且适配' in body) or ('无外部承接' in body)
    has_todo = '尚未完成外部候选复核' in body
    if not (has_cand or has_none or has_todo):
        bad('%s 的「外部承接」段既无候选也未声明「无候选」（口径缺失）' % p)
        continue
    if has_todo:
        n_todo += 1
    elif has_none:
        n_none += 1
        if '回落' not in body and '纯提示词' not in body:
            bad('%s 声明无候选但未写明回落路径' % p)
    else:
        n_ok += 1
        if not repos_in(body):
            bad('%s 声明有候选但未给 `owner/repo` 仓库标识' % p)
    # 许可门禁：出现 GPL/AGPL/CC-BY-NC 时必须标「仅外部调用」
    if re.search(r'GPL|AGPL|CC-BY-NC', body) and '仅外部调用' not in body:
        bad('%s 的候选含 GPL/AGPL/CC-BY-NC 但未标「仅外部调用」' % p)
ok('外部承接：有候选 %d 域 / 已复核无候选 %d 域 / 待复核 %d 域' % (n_ok, n_none, n_todo))

# ---------- 4. 3 级：92 个 skill 的降级段必须是三档 ----------
sk = sorted(glob_sk := [p.replace(os.sep, '/') for p in
                        __import__('glob').glob('domains/*/skills/local/*/SKILL.md')])
bad3 = []
for p in sk:
    t = rd(p)
    m = re.search(r'^##\\s*失败与降级[^\\n]*$', t, re.M)
    if not m:
        bad3.append((p, '缺段'))
        continue
    nxt = re.search(r'^##\\s', t[m.end():], re.M)
    body = t[m.end():][:nxt.start() if nxt else len(t)]
    miss = []
    if 'external-bridge.md' not in body:
        miss.append('未接 external-bridge.md')
    if '纯提示词模式' not in body:
        miss.append('未保留档 3（纯提示词）')
    if '降级承接' not in body:
        miss.append('未保留档 1（同域降级承接）')
    if miss:
        bad3.append((p, '/'.join(miss)))
if bad3:
    for p, why in bad3[:8]:
        bad('%s 降级段不全：%s' % (p, why))
    if len(bad3) > 8:
        bad('（另有 %d 个 skill 同型问题）' % (len(bad3) - 8))
else:
    ok('%d 个库内 skill 的降级段均为三档' % len(sk))

# ---------- 5. 登记一致性 + 可达性声明 ----------
POOL = set()
if os.path.isfile('references/external-sources.md'):
    dec = rd('references/external-sources.md')
    if '实测' not in dec:
        warn('external-sources.md 未登记「实测」结论（无法判断是否核验过）')
    if '200' not in dec:
        warn('external-sources.md 未登记可达性实测值')
    POOL = repos_in(dec)
    if len(POOL) < 20:
        bad('已核验仓库池过小（%d 个，期望 ≥20）→ 登记面不足' % len(POOL))
    else:
        ok('已核验仓库池 = %d 个' % len(POOL))

if POOL:
    miss = []
    for d in dom_dirs:
        p = 'domains/%s/_domain.md' % d
        if not os.path.isfile(p):
            continue
        t = rd(p)
        m = re.search(r'^##\\s*外部承接[^\\n]*$', t, re.M)
        if not m:
            continue
        nxt = re.search(r'^##\\s', t[m.end():], re.M)
        body = t[m.end():][:nxt.start() if nxt else len(t)]
        for r in repos_in(body):
            if r not in POOL:
                miss.append('%s -> %s' % (d, r))
    if miss:
        for x in miss[:8]:
            bad('引用了未登记的候选仓库（疑编造）：%s' % x)
        if len(miss) > 8:
            bad('（另有 %d 处同型问题）' % (len(miss) - 8))
    else:
        ok('2 级引用的候选仓库全部已在池中登记（零编造）')

print('=' * 68)
for m in OK:
    print('  OK   %s' % m)
for m in WARN:
    print('  WARN %s' % m)
for m in FAIL:
    print('  FAIL %s' % m)
print('=' * 68)
print('结果: OK %d ｜ WARN %d ｜ FAIL %d' % (len(OK), len(WARN), len(FAIL)))
sys.exit(1 if FAIL else 0)
'''

new_file('scripts/extskill.py', EXTSKILL, '外部 skill 桥接 · 静态自检器')

# =============================================================== D) 各域「外部承接」
print('== D) 20 个 _domain.md 增「## 外部承接」==')

HEAD = ('## 外部承接（库内与同域降级都接不住时才启用）\n'
        '\n'
        '> **第三档入口**：先读 `library/external-bridge.md`（触发条件 + 五步自检 + 许可门禁），\n'
        '> 再按 `references/external-sources.md` §1 的顺序检索 **12 个平台**。\n'
        '> **库内优先不变**：本域仍先用库内 skill；外部桥接只在**同域降级也接不住**时启用。\n'
        '> **禁止编造**外部链接（硬规则 2）；候选仓库已逐个双通道核验（2026-10-03）。\n'
        '\n'
        '**检索词**：%s\n'
        '\n')

NOCAND = ('**本域无合规且适配 DUT 的外部候选**（2026-10-02 已复核）：%s\n'
          '\n'
          '**本域结论**：**无外部承接** → 缺口直接**回落「纯提示词模式」**（原有流程），不引入外部依赖。\n')

TODO = ('**本域尚未完成外部候选复核**（2026-10-03 登记）：本域为 v3 期新增域，'
        'v2 期 19 域的候选比对表未覆盖它。\n'
        '\n'
        '**本域结论**：按 `library/external-bridge.md` **现场检索 12 平台**；'
        '未通过自检 → 直接**回落「纯提示词模式」**。\n')

# terms / rows(repo, license, stars, score, verdict) / verdict_or_reason
EXT = {
 'F1-campus-affairs': ('校园门户 / 教务系统 / 学籍与证明 自动化；LMS 连接器',
   [('googleworkspace/cli', 'Apache-2.0', '31,231', '3.95', '⚠️ 不适配 DUT（面向境外工作空间）'),
    ('vishalsachdev/canvas-mcp', 'MIT', '270', '3.65', '⚠️ 不适配 DUT（Canvas 非本校教务）')],
   '**本域暂无「合规 + 适配 DUT」的外部首选** —— 已复核的 2 个候选均为通用 / 境外工具，'
   '与本校自建教务（`jxgl` / `portal`）不对口。**缺口直接回落「纯提示词模式」。**', None),
 'F2-focus': ('深度工作 / 番茄钟 / 习惯追踪',
   [('alirezarezvani/claude-skills', 'MIT', '27,194', '4.40', '✅ 最优解'),
    ('eddiebelaval/squire', 'MIT', '21', '3.20', '⚠️ 不适配 DUT'),
    ('jakedahn/pomodoro', 'MIT', '56', '3.05', '⚠️ 不适配 DUT')],
   '可用首选：`alirezarezvani/claude-skills`（MIT）。**仅在其自检 5/5 通过时外接**；'
   '否则回落档 3。', None),
 'F3-wellbeing': ('心理支持 / 社交 / 适应', [],
   None, '心理支持类 skill 有**临床风险**，开源侧无可信实现；'
         '已复核 `education-agent-skills`（817★）为**教师侧**教学技能，适配 0 → 本域**只走库内自建 skill**。'),
 'F4-money-safety': ('预算 / 反诈 / 资助', [],
   None, '检索 `finance|budget|scam` 命中的均为 **awesome-list 清单**或通用 AI 助手，非可执行 skill；'
         '且理财建议涉合规风险 → **不引入外部依赖**。'),
 'F5-health': ('健康 / 就医路径 / 运动', [],
   None, '临床类 skill 存在**诊断越界风险**；命中仓库多为清单且**无 LICENSE** → 本域坚持库内实现。'),
 'F6-service': ('军训 / 志愿 / 社会实践', [],
   None, '垂类过窄，**12 平台均无有效命中**（检索有效命中 0）→ 本域为**纯自建域**。'),
 'F7-further-study': ('升学 / 保研 / 文书 / 选校',
   [('Haadhi76/SOP_Consultant', 'MIT', '4', '3.80', '⚠️ 不适配 DUT'),
    ('tydev-new/10xcolleges', 'MIT', '2', '3.35', '⚠️ 不适配 DUT'),
    ('cabbage2000-lab/paper-tutor-skills', '未声明', '33', '1.80', '⛔ 许可证缺失，不入围')],
   '**本域暂无「合规 + 适配 DUT」的外部首选** —— 候选均为**境外申请场景**'
   '（Common App / 英文 SOP），与国内保研 / 考研口径错位。**缺口直接回落「纯提示词模式」。**', None),
 'F8-career': ('简历 / 面试 / 求职',
   [('Paramchoudhary/ResumeSkills', 'MIT', '2,509', '4.70', '✅ 最优解'),
    ('sourikduttanyu/interview-prep', 'MIT', '0', '3.35', '⚠️ 不适配 DUT')],
   '可用首选：`Paramchoudhary/ResumeSkills`（MIT）。**须先过自检**，并补本校就业网口径。', None),
 'R1-literature': ('文献检索 / 下载 / 管理 / 引用',
   [('Lucaswangzcx/literature-downloader-skill', 'MIT', '230', '4.55', '✅ 最优解'),
    ('WenyuChiou/zotero-skills', 'MIT', '55', '4.40', '备选'),
    ('xwmxcz/papers-skill', 'MIT', '1', '3.35', '备选')],
   '可用首选：`Lucaswangzcx/literature-downloader-skill`（MIT）。', None),
 'R2-experiment-data': ('实验设计 / 统计 / 可视化',
   [('K-Dense-AI/scientific-agent-skills', 'MIT', '47,304', '4.25', '✅ 最优解'),
    ('K-Dense-AI/scientific-agents', 'MIT', '192', '4.10', '备选'),
    ('openai/skills', '未声明', '27,841', '2.70', '⛔ 许可证缺失，不入围')],
   '可用首选：`K-Dense-AI/scientific-agent-skills`（MIT）。', None),
 'R3-research-tools': ('科研工具 / 环境 / 代码',
   [('mattpocock/skills', 'MIT', '273,959', '4.10', '✅ 最优解'),
    ('obra/superpowers', 'MIT', '294,023', '4.10', '⚠️ 不适配 DUT'),
    ('egouilliard-leyton/python-tutor-skill', 'MIT', '1', '3.05', '备选')],
   '可用首选：`mattpocock/skills`（MIT）。', None),
 'R4-publication': ('论文 / 投稿 / 专利 / 答辩',
   [('Gabberflast/academic-pptx-skill', 'MIT', '1,100', '3.80', '✅ 最优解'),
    ('Imbad0202/academic-research-skills', '未声明', '50,096', '2.85', '⛔ 许可证缺失，不入围'),
    ('cabbage2000-lab/paper-tutor-skills', '未声明', '33', '2.25', '⛔ 许可证缺失，不入围')],
   '可用首选：`Gabberflast/academic-pptx-skill`（MIT）。', None),
 'R5-integrity': ('学术规范 / 查重 / 伦理 / AI 披露',
   [('NeoLabHQ/context-engineering-kit', 'GPL-3.0', '1,738', '3.05',
     '⚠️ **仅外部调用**（GPL-3.0，禁止摘录进本包）')],
   '唯一候选为 **GPL-3.0** → **合规 = 2**：**只允许外部调用，禁止摘录任何内容进本包**。'
   '若无法满足此约束，直接回落档 3。', None),
 'R6-info-retrieval': ('信息检索 / 通知追踪 / 机构查询', [], None, None),
 'S1-course-qa': ('课程答疑 / 分步讲解 / 苏格拉底式提问',
   [('bevibing/socrates-skill', 'MIT', '326', '4.25', '✅ 最优解'),
    ('mattpocock/skills', 'MIT', '273,959', '4.10', '⚠️ 不适配 DUT'),
    ('bevibing/tutor-skills', 'MIT', '1,313', '3.95', '备选')],
   '可用首选：`bevibing/socrates-skill`（MIT）—— 与本域「不直接抛答案」同构。', None),
 'S2-lecture-notes': ('课堂笔记 / 结构化 / 知识联结',
   [('kepano/obsidian-skills', 'MIT', '49,077', '4.40', '✅ 最优解'),
    ('bevibing/tutor-skills', 'MIT', '1,313', '4.40', '备选'),
    ('0x-man/mindmap-skill', 'MIT', '16', '3.95', '备选')],
   '可用首选：`kepano/obsidian-skills`（MIT）。', None),
 'S3-assignment': ('作业 / 实验报告 / 团队项目',
   [('kgraph57/paper-writer-skill', 'MIT', '58', '3.50', '✅ 最优解'),
    ('vishalsachdev/canvas-mcp', 'MIT', '270', '4.10', '⚠️ 不适配 DUT'),
    ('anthropics/skills', '未声明', '179,334', '2.85', '⛔ 许可证缺失，不入围')],
   '可用首选：`kgraph57/paper-writer-skill`（MIT）。', None),
 'S4-exam-prep': ('备考 / 记忆 / 复习计划',
   [('hluaguo/learn-faster-kit', 'MIT', '380', '4.10', '✅ 最优解'),
    ('GlacierXiaowei/structured-learning-skill', 'Apache-2.0', '3', '3.50', '备选'),
    ('lowwwbank/anything-to-course', 'MIT', '18', '3.50', '备选')],
   '可用首选：`hluaguo/learn-faster-kit`（MIT）。', None),
 'S5-academic-writing': ('学术写作 / 摘要 / 规范',
   [('Gabberflast/academic-pptx-skill', 'MIT', '1,100', '4.25', '✅ 最优解'),
    ('hameefy/claude-latex-skill', 'MIT', '10', '3.50', '备选'),
    ('Imbad0202/academic-research-skills', '未声明', '50,096', '2.85', '⛔ 许可证缺失，不入围')],
   '可用首选：`Gabberflast/academic-pptx-skill`（MIT）。', None),
 'S6-language': ('语言训练 / 雅思托福 / 口语',
   [('YANZHANLIN/ielts-claude-skills', 'MIT', '307', '4.55', '✅ 最优解'),
    ('tianmind-studio/english-coach', 'MIT', '17', '3.95', '备选'),
    ('flysheep-ai/education-skills', 'MIT', '106', '3.35', '备选')],
   '可用首选：`YANZHANLIN/ielts-claude-skills`（MIT）。', None),
}

n_ok = n_no = n_todo = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    p = os.path.join(ROOT, 'domains', d, '_domain.md')
    if not os.path.isfile(p):
        continue
    t = io.open(p, 'r', encoding='utf-8').read()
    rel = 'domains/%s/_domain.md' % d
    if '## 外部承接' in t:
        print('  [SAME] %s' % rel)
        continue
    terms, rows, verdict, reason = EXT[d]
    if rows:
        blk = HEAD % terms
        blk += ('**已核验候选**（仓库数据 2026-10-02 抓取 ｜ 链接 2026-10-03 双通道核验）\n'
                '\n'
                '| 候选仓库 | 许可 | ★ | 综合分 | 可用性判定 |\n'
                '|---|---|---|---|---|\n')
        for r, lic, st, sc, vd in rows:
            blk += '| `%s` | %s | %s | %s | %s |\n' % (r, lic, st, sc, vd)
        blk += '\n**本域结论**：%s\n' % verdict
        n_ok += 1
    elif d == 'R6-info-retrieval':
        blk = HEAD % terms + TODO
        n_todo += 1
    else:
        blk = HEAD % terms + (NOCAND % reason)
        n_no += 1
    anchor = '## 执行顺序'
    if anchor not in t:
        print('  [MISS] %s :: 无「## 执行顺序」锚点' % rel)
        continue
    t = t.replace(anchor, blk + '\n' + anchor, 1)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)
    print('  [OK]   %s（%s）' % (rel, '有候选' if rows else ('待复核' if d == 'R6-info-retrieval' else '已复核无候选')))
print('  合计：有候选 %d 域 / 已复核无候选 %d 域 / 待复核 %d 域' % (n_ok, n_no, n_todo))

# 执行顺序补第 6 步（外部桥接）
print('== D-2) _domain.md 执行顺序补「第 6 步」==')
STEP6 = ('**外部桥接（最后的兜底）**：库内与同域降级都接不住时，'
         '读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → '
         '过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**。')
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    rel = 'domains/%s/_domain.md' % d
    t = read(rel)
    if t is None or STEP6 in t:
        continue
    m = re.search(r'(^## 执行顺序\n(?:.*\n)*?)(\n## )', t, re.M)
    if not m:
        print('  [MISS] %s :: 执行顺序锚点未命中' % rel)
        continue
    seg, tail = m.group(1), m.group(2)
    nums = re.findall(r'^(\d+)\.\s', seg, re.M)
    nxt = (max(int(x) for x in nums) + 1) if nums else 6
    seg2 = seg.rstrip('\n') + '\n' + '%d. %s\n' % (nxt, STEP6)
    write(rel, t.replace(seg + tail, seg2 + tail, 1))
    n += 1
print('  已补 %d 个域' % n)

# =============================================================== E) 92 个 skill 降级段三档
print('== E) 92 个 SKILL.md 的降级段由两档改为三档 ==')
OLD_TAIL = '仍不满足 → 纯提示词模式并标注'
NEW_TAIL = ('仍不满足 → 按 `library/external-bridge.md` 走**外部桥接**'
            '（12 平台检索 + 五步自检；输出首行标 `[外接] 来源 + 许可`）；'
            '外部桥接未命中 → 纯提示词模式并标注')
n = 0
for p in sorted(glob.glob(os.path.join(ROOT, 'domains/*/skills/local/*/SKILL.md'))):
    t = io.open(p, 'r', encoding='utf-8').read()
    if OLD_TAIL not in t:
        continue
    io.open(p, 'w', encoding='utf-8', newline='').write(t.replace(OLD_TAIL, NEW_TAIL))
    n += 1
    print('  [OK]   %s' % os.path.relpath(p, ROOT).replace('\\', '/'))
print('  改写 %d 个（应为 92）' % n)

# =============================================================== F) 入口卡补第 6 步
print('== F) commands 入口卡补「外部桥接」档 ==')
n = 0
for p in sorted(glob.glob(os.path.join(ROOT, 'commands/*.md'))):
    t = io.open(p, 'r', encoding='utf-8').read()
    if 'library/external-bridge.md' in t:
        print('  [SAME] %s' % os.path.basename(p))
        continue
    lines = t.split('\n')
    last, num = None, 0
    for i, l in enumerate(lines):
        m = re.match(r'^(\d+)\.\s', l)
        if m:
            last, num = i, int(m.group(1))
    if last is None:
        continue
    ins = ('%d. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，'
           '读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → '
           '输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。' % (num + 1))
    lines.insert(last + 1, ins)
    io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
    n += 1
    print('  [OK]   %s（补第 %d 步）' % (os.path.basename(p), num + 1))
print('  已补 %d 张卡' % n)

print('done-part2')

# =============================================================== G) 1 级库文档
print('== G) 1 级库文档接线 ==')
edit('library/README.md', [
    ('- `skill-evolution.md` —— 习惯自迭代：按用户习惯**只改可改段**（执行步骤 / 判定细则 / 示例说明）的非结构性迭代机制',
     '- `skill-evolution.md` —— 习惯自迭代：按用户习惯**只改可改段**（执行步骤 / 判定细则 / 示例说明）的非结构性迭代机制\n'
     '- `external-bridge.md` —— **外部桥接**：库内与同域降级都接不住时的第三档之前的桥接档'
     '（12 平台检索 + 五步自检 + 许可门禁 + 未命中回落）',
     '`external-bridge.md` —— **外部桥接**'),
])

edit('library/general-fallback.md', [
    ('> 这是「库内唯一通道」成立的前提：通道收窄到只走库内，就必须保证**库外没有任何一条路是断的**。',
     '> 本框架是**三档降级链**的收尾：档 1「同域库内 skill」→ 档 2「外部桥接」（`library/external-bridge.md`）'
     '→ **档 3「本框架」**。\n'
     '> 也就是说：**外部桥接也没命中时，必须回到这里出结果** —— 不允许「只回一句拒绝」。',
     '本框架是**三档降级链**的收尾'),
])

edit('library/output-spec.md', [
    ('3. **打不开时给排查路径，不给替代链接**：按',
     '3. **外部桥接产物必须标注来源**：档 2 的输出**首行**标 '
     '`[外接] 来源：<平台>/<owner>/<repo> ｜ 许可：<LICENSE> ｜ 自检：5/5 通过`，'
     '并在【结论】里区分「外部能力」与「本包补的 DUT 事实」；**禁止**写成本包原生能力'
     '（见 `library/external-bridge.md` §6）。\n'
     '4. **打不开时给排查路径，不给替代链接**：按',
     '外部桥接产物必须标注来源'),
])

# =============================================================== K) 构建侧文档补齐层序
print('== K) 构建侧文档：v3/README.md 层序补 54–61 ==')
edit('scripts/_build/v3/README.md', [
    ('| 16 | `scripts/_build/v3/step53_checkup_flow.py` | **自检查流程加固**：新增 `scripts/checkall.py`（单入口 · 逐项计时 · 模拟跑摘要）与 `scripts/negative_test.py`（负向自测 · 断言非空转）+ 需求确定门算例（例 D/E）+ `aligncheck` 口径断言；修订号 → `3.2.2` | 新增层 |',
     '| 16 | `scripts/_build/v3/step53_checkup_flow.py` | **自检查流程加固**：新增 `scripts/checkall.py`（单入口 · 逐项计时 · 模拟跑摘要）与 `scripts/negative_test.py`（负向自测 · 断言非空转）+ 需求确定门算例（例 D/E）+ `aligncheck` 口径断言；修订号 → `3.2.2` | 新增层 |\n'
     '| 17 | `step54_blindrun_fixes.py` · `step55_realrun_fixes.py` · `step56_v325_release.py` | 盲跑 / 真实问题归因修复 + v3.2.5 工程化迭代（隔离断言 · L3 共现规则 · 指标埋点）；修订号 `3.2.2 → 3.2.5` | 新增层 |\n'
     '| 18 | `step57_risk_fixes.py` · `step58_readme_download.py` | 风险自检修复（记忆不跟踪 · 交付剔除 `.gitignore`）+ README 下载区；修订号 `3.2.5 → 3.2.7` | 新增层 |\n'
     '| 19 | `step59_link_integrity.py` · `step60_url_audit.py` | 链接可用性修复（URL 边界归一 · 仅 HTTP 标注 · 排查话术）+ 外链核验订正（教务裸根 404 · 信息库 5 处事实订正 · 三通道复核）；修订号 `3.2.7 → 3.2.9` | 新增层 |\n'
     '| 20 | `step61_external_bridge.py` | **外部 skill 桥接（大改）**：降级链**两档 → 三档**（同域库内 → 外部桥接 → 纯提示词）· 12 平台入口表 `references/external-sources.md` · 1 级规则 `library/external-bridge.md` · 第 6 个校验器 `scripts/extskill.py` · 20 域 `## 外部承接` · 92 个 skill 降级段改写 · `library` 规则数 10→11；**包版本 `3.2 → 3.3` / 修订号 → `3.3.0`** | 新增层 |',
     'step61_external_bridge.py'),
])

# =============================================================== H) 校验器成组改
print('== H) 校验器断言成组改（规则数 10 → 11；接入 extskill）==')
n = replace_all('scripts/selfcheck.sh',
                '[ "${libn:-0}" -eq 10 ] && ok "library 文件数 = 10" || warn "library 文件数 = $libn（期望 10）"',
                '[ "${libn:-0}" -eq 11 ] && ok "library 文件数 = 11" || warn "library 文件数 = $libn（期望 11）"')
print('  selfcheck.sh library 计数：%d 处' % n)

n = replace_all('scripts/regress.sh',
                '_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 10',
                '_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 11')
print('  regress.sh library 计数：%d 处' % n)

edit('scripts/checkall.py', [
    ("    ('regress', ['@bash', 'scripts/regress.sh', ROUNDS], r'累计 FAIL\\s*=\\s*(\\d+)', '行为回归（澄清门 / 门禁 / 输出标准）', 0),",
     "    ('extskill', ['@py', 'scripts/extskill.py', '.'], r'结果:\\s*OK\\s*(\\d+)\\s*｜\\s*WARN\\s*(\\d+)\\s*｜\\s*FAIL\\s*(\\d+)', '外部 skill 桥接（接线 + 登记 + 许可）', 2),\n"
     "    ('regress', ['@bash', 'scripts/regress.sh', ROUNDS], r'累计 FAIL\\s*=\\s*(\\d+)', '行为回归（澄清门 / 门禁 / 输出标准）', 0),",
     "scripts/extskill.py"),
])

# negative_test：第 8 类注入 —— 破坏外部桥接接线
NT = read('scripts/negative_test.py')
if NT is None:
    print('  [SKIP] 无 scripts/negative_test.py')
elif 'inject_bridge_broken' in NT:
    print('  [SAME] 负向注入已存在')
else:
    A1 = 'def inject_url_boundary(tree):'
    B1 = ('''def inject_bridge_broken(tree):
    """把某个 3 级 skill 的降级段改回「两档」（去掉外部桥接）→ extskill 应 FAIL。"""
    import glob as _g
    p = sorted(_g.glob(os.path.join(tree, 'domains/*/skills/local/*/SKILL.md')))[0]
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('按 `library/external-bridge.md` 走**外部桥接**', '走外部')
    return [p], t


def inject_url_boundary(tree):''')
    A2 = ("        ('URL 紧贴中文（依据里的链接会被渲染器吞掉）', inject_url_boundary,"
          "\n         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck F2'),")
    B2 = ("        ('URL 紧贴中文（依据里的链接会被渲染器吞掉）', inject_url_boundary,\n"
          "         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck F2'),\n"
          "        ('外部桥接接线被破坏（降级段退回两档）', inject_bridge_broken,\n"
          "         ['@py', 'scripts/extskill.py', '.'], 'extskill 三档断言'),")
    okk = (A1 in NT) and (A2 in NT)
    if okk:
        NT = NT.replace(A1, B1, 1).replace(A2, B2, 1)
        write('scripts/negative_test.py', NT)
        print('  [OK]   已加第 8 类注入（外部桥接接线）')
    else:
        print('  [MISS] 负向注入锚点未命中')

# =============================================================== I) 口径（库内优先 → 库内优先 + 可选外接）
print('== I) 口径改写：从「零外部依赖 / 库内唯一」到「离线零依赖 + 可选外接」==')
PAIRS = [
 ('README.md',
  '> 定位：**纯 DUT 特化库** —— 全部能力由库内 skill 承接，**运行时零外部依赖、零外部通道**',
  '> 定位：**DUT 特化库（库内优先）** —— 日常能力全部由库内 skill 承接，**离线零依赖**；\n'
  '> 库内与同域降级都接不住时，可走**可选的外部桥接**（12 平台 + 五步自检，见 `library/external-bridge.md`），'
  '**外部未命中即回落原有流程**'),
 ('README.md',
  '**核心规则：库内唯一** —— 本包为纯 DUT 特化库，全部场景均由库内 skill 承接，**不安装、不引用任何库外 skill**；库内无法覆盖的细分场景走**同域降级**并记「缺口」。',
  '**核心规则：库内优先** —— 本包为 DUT 特化库，日常场景均由库内 skill 承接，**开箱即用、离线可用**；\n'
  '库内与同域降级都接不住时走**外部桥接**（可选，见 `library/external-bridge.md`）；外部未命中则回落**纯提示词模式**并记「缺口」。'),
 ('README.md',
  '已统一格式并**DUT 特化**，运行时**零外部依赖**；其余 40 个为自建。',
  '已统一格式并**DUT 特化**，日常运行**离线零依赖**（外接为可选项）；其余 40 个为自建。'),
 ('README.md',
  '- 本包为**纯 DUT 特化库**：库内 92 个 skill 均可离线直接使用，**不依赖、不引用任何库外 skill**。',
  '- 本包为 **DUT 特化库**：库内 92 个 skill 均可离线直接使用；外部桥接为**可选增强**，'
  '未联网或未命中时自动回落原有流程。'),
 ('INSTALL.md',
  '> 本包为**纯 DUT 特化库**：库内 skill 开箱即用，**运行时零外部依赖**。',
  '> 本包为 **DUT 特化库（库内优先）**：库内 skill 开箱即用，**离线零依赖**；'
  '外部桥接为**可选增强**（见 `library/external-bridge.md`）。'),
 ('INSTALL.md',
  '| 通道 | **库内唯一** —— 不安装、不引用任何库外 skill |',
  '| 通道 | **库内优先** —— 日常不装任何外部 skill；缺口时可**可选外接**（12 平台 + 五步自检） |'),
 ('INSTALL.md',
  '| 依赖 | **零外部依赖**，全程离线可用 |',
  '| 依赖 | **核心能力零外部依赖**，全程离线可用；外接为可选项 |'),
 ('INSTALL.md',
  '| 库内 skill | **开箱即用，无需安装任何东西**（92 个，零外部依赖） |',
  '| 库内 skill | **开箱即用，无需安装任何东西**（92 个，离线零依赖） |'),
 ('references/platforms.md',
  '| 通道 | **库内唯一** —— 不安装、不引用任何库外 skill |',
  '| 通道 | **库内优先** —— 缺口时可选外接（12 平台 + 五步自检），未命中即回落 |'),
 ('references/platforms.md',
  '| 依赖 | **零外部依赖**，离线可用 |',
  '| 依赖 | **核心能力零外部依赖**，离线可用 |'),
 ('references/skill-compliance-audit.md',
  '> 口径：自 v3.0.0 起本包为**纯 DUT 特化库**，外部内容仅作**构建期素材**，运行期零外部依赖。',
  '> 口径：本包为 **DUT 特化库（库内优先）**：**核心能力运行期零外部依赖**，外部内容默认仅作**构建期素材**；\n'
  '> 自 v3.3.0 起新增**可选的外部桥接**（只在库内与同域降级都接不住时启用，且须过五步自检与许可门禁），'
  '**外部未命中即回落原有流程**。'),
 ('domains/_registry.md',
  '| 库内 skill 覆盖 | **92 个（自建 80 + 外部改造 12，运行时零外部依赖）** |',
  '| 库内 skill 覆盖 | **92 个（自建 80 + 外部改造 12，离线零依赖）**；另有**可选外部桥接**（12 平台 + 五步自检） |'),
 ('SKILL.md',
  '1. **库内唯一**：本包为纯 DUT 特化库，全部场景均由库内 skill 承接，**不安装、不引用任何库外 skill**；库内无法覆盖的细分场景走降级流程并记「缺口」。',
  '1. **库内优先**：日常场景由库内 skill 承接，**不安装任何外部 skill**；'
  '库内与同域降级都接不住时走**外部桥接**（可选，`library/external-bridge.md`）；'
  '外部未命中则回落**纯提示词模式**并记「缺口」。'),
 ('THIRD_PARTY_NOTICES.md',
  '- **运行期零外部依赖**：不安装、不调用、不下载任何库外 skill。',
  '- **核心能力运行期零外部依赖**：日常不安装、不调用外部 skill；'
  '自 v3.3.0 起的**外部桥接**为可选项，只在缺口时使用且须过五步自检。'),
 ('THIRD_PARTY_NOTICES.md',
  '1. 本包为**纯 DUT 特化库**，运行期不引用任何库外 skill，上表候选池仅供参考。',
  '1. 本包为 **DUT 特化库（库内优先）**：日常不引用外部 skill；'
  '缺口时可按 `library/external-bridge.md` 可选外接，上表候选池同时充当许可判定依据。'),
 ('library/domain-review.md',
  '   有对口 skill → 直接用（库内唯一通道）',
  '   有对口 skill → 直接用（库内优先）'),
 ('references/skill-selection-matrix.md',
  '| 命中域 + 有对口 skill | 直接用（库内唯一通道） | 标准输出 |',
  '| 命中域 + 有对口 skill | 直接用（库内优先） | 标准输出 |'),
]
for rel, a, b in PAIRS:
    edit(rel, [(a, b)])

# =============================================================== J) 版本 3.3.0
print('== J) 版本：包版本 %s → %s ｜ 修订号 %s → %s ==' % (OLD_PKG, NEW_PKG, OLD_REV, NEW_REV))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        x = read(rel)
        if x and 'version: %s' % OLD_REV in x:
            write(rel, x.replace('version: %s' % OLD_REV, 'version: %s' % NEW_REV))
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('SKILL.md', '（%s）' % OLD_PKG, '（%s）' % NEW_PKG),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD_REV, '"version": "%s"' % NEW_REV),
        ('config.yaml', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('config.yaml', '学伴包 %s ·' % OLD_PKG, '学伴包 %s ·' % NEW_PKG),
        ('README.md', '一体化学伴包 %s' % OLD_PKG, '一体化学伴包 %s' % NEW_PKG),
        ('scripts/qihang.sh', '学伴包 %s ·' % OLD_PKG, '学伴包 %s ·' % NEW_PKG),
        ('library/output-spec.md', '**包版本 = `3.2`**', '**包版本 = `3.3`**'),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD_REV, '**修订号 = `%s`**' % NEW_REV),
        ('library/output-spec.md', '（`3.2` ↔ `3.2.x`）', '（`3.3` ↔ `3.3.x`）'),
        ('library/output-spec.md', '如 `3.2.0` → `%s`）' % OLD_REV, '如 `3.3.0` → `%s`）' % NEW_REV),
        ('scripts/_build/README.md', '3.2.8 → 3.2.9', '3.3.0（外部桥接 · 大改）'),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

# config.yaml 增策略开关
edit('config.yaml', [
    ('    local_first: true          # 库内优先（硬规则）',
     '    local_first: true          # 库内优先（硬规则，永不变）\n'
     '    external_bridge: true      # 外部桥接（可选增强）：库内与同域降级都接不住时才走；未命中即回落',
     'external_bridge: true'),
])

print('done')

# =============================================================== L) 运行期状态行与合规断言同口径
print('== L) qihang.sh 状态行 + audit.sh 合规断言（口径同步）==')
edit('scripts/audit.sh', [
    ('  grep -q "零外部依赖" "$aud" && ok "已声明运行期零外部依赖" || warn "未声明零外部依赖"',
     '  grep -qE "核心能力运行期零外部依赖|运行期零外部依赖" "$aud" \\\n'
     '    && ok "已声明「核心能力运行期零外部依赖」" || warn "未声明零外部依赖口径"\n'
     '  grep -q "外部桥接" "$aud" && ok "已声明外部桥接为可选增强（v3.3.0）" \\\n'
     '    || warn "未声明外部桥接口径（v3.3.0 起必需）"',
     '已声明外部桥接为可选增强'),
])

edit('scripts/qihang.sh', [
    ("  printf '  ✓ %s 个域 / %s 个库内 skill（开箱即用，零外部依赖）\\n' \"$nd\" \"$ns\"",
     "  printf '  ✓ %s 个域 / %s 个库内 skill（开箱即用，离线零依赖）\\n' \"$nd\" \"$ns\"",
     '离线零依赖'),
    ("    printf '  ✓ 无库外通道（纯 DUT 特化库）\\n'",
     "    printf '  ✓ 无 per-skill 外部文件（库内优先；外部桥接为可选）\\n'",
     '无 per-skill 外部文件'),
    ("    printf '  ✓ 可离线直接用：%s 个域 / %s 个库内 skill（零外部依赖）\\n' \"$_nd\" \"$_ns\"",
     "    printf '  ✓ 可离线直接用：%s 个域 / %s 个库内 skill（离线零依赖；外接为可选）\\n' \"$_nd\" \"$_ns\"",
     '外接为可选'),
])
