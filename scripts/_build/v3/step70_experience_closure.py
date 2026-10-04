#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
step70_experience_closure.py — 体验层收口 ②（B2 / B3 / C1 / C2 / C3）

本层必须在 step52–step55（澄清门历史）、step56（metrics 模板）、step67（触发门同源）、
step68（移除身份）、step69（学生呈现层）之后执行；它是对这些层既有文本的**最终覆盖**。

收口内容：
  B2 澄清门：复述档改为「**实质歧义驱动**」——关键槽齐全即免复述，消除「白复述一遍」的空转感；
             同步 `config.yaml` 注释 / `library/clarity.md` §3.1 / `regress.sh [9]` / `aligncheck` L 组。
  B3 记忆口径：新增 `library/memory.md` §3.2「续接固定回话」唯一副本，三处口径指向同一句；
             `SKILL.md` 会话连续性与硬规则 3 补「看完之后的交还」。
  C1 越界仲裁：`trigger.arbitration` 唯一副本（越界表 = **初筛**，需求主键 T+O = **终判**），
             `SKILL.md` §1.5 / `library/domain-review.md` §2.1 同步，去掉「优先级最高」的单点误读。
  C2 登录回交：`library/login-policy.md` §4.1「看完之后的交还（三步）」+ 固定一句话唯一副本。
  C3 体验指标：`library/experience.md` §7「体验层自检指标」（5 项，静态零数据、默认不记录）。

  Y 组断言（新增，21 组）+ 5 类负向注入。

幂等：可重复执行；第二次应报「改动 0 处」。
"""

import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))


def _p(*a):
    return os.path.join(ROOT, *a)


def read(rel):
    with io.open(_p(*rel.split('/')), encoding='utf-8') as f:
        return f.read()


def write(rel, text):
    path = _p(*rel.split('/'))
    d = os.path.dirname(path)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def sub_once(rel, old, new, label):
    t = read(rel)
    if new in t:
        return 0
    if old not in t:
        raise SystemExit('anchor missing [%s] in %s' % (label, rel))
    write(rel, t.replace(old, new, 1))
    return 1


def collapse_dup(rel, block, label):
    t = read(rel)
    for dup in (block + '\n' + block, block + block):
        if dup in t:
            write(rel, t.replace(dup, block, 1))
            return 1
    return 0


def sub_re(rel, pattern, repl, label):
    t = read(rel)
    n = len(t)
    t2 = re.sub(pattern, repl, t)
    if t2 != t:
        write(rel, t2)
    return 1 if t2 != t else 0


import re  # noqa: E402  (used by sub_re / patches)


# ============================================================================
# B2 —— 澄清门：复述档改为实质歧义驱动
# ============================================================================

CONFIG_COMMENT_OLD = """    # 需求确定门（见 library/clarity.md §3.1）：C = 1 − U 为「理解准确率」
    #   C >= 0.95 → 直接执行（免复述）｜0.70 <= C < 0.95 → 一句话复述并落【假设】｜C < 0.70 → 追问
"""

CONFIG_COMMENT_NEW = """    # 需求确定门（见 library/clarity.md §3.1）：C = 1 − U 为「理解准确率」
    #   C >= 0.95 → 直接执行（免复述）
    #   0.70 <= C < 0.95 → **仅当存在实质歧义时**一句话复述（并入【结论】首行）；无实质歧义 → 直接执行
    #   C < 0.70 → 仅当澄清门本就要追问时才追问；澄清门已放行 → 直接执行
"""

CLARITY_HEAD_OLD = """### 3.1 需求确定门（理解准确率 **≥ 95%** 才直接执行）
"""
CLARITY_HEAD_NEW = """### 3.1 需求确定门（理解准确率 **≥ 95%** 才直接执行 · **实质歧义驱动**）
"""

CLARITY_RESTATE_ROW_OLD = """| **复述档** | `0.70 ≤ C < 0.95` | **先用一句话复述**「你要的是 ⟨对象 + 任务⟩，产出 ⟨产出物⟩，约束 ⟨若有且影响执行⟩」；用户不纠正即执行，纠正则按 §4 就缺口追问 |
"""
CLARITY_RESTATE_ROW_NEW = """| **复述档** | `0.70 ≤ C < 0.95` **且存在实质歧义** | **先用一句话复述**「你要的是 ⟨对象 + 任务⟩，产出 ⟨产出物⟩，约束 ⟨若有且影响执行⟩」；用户不纠正即执行，纠正则按 §4 就缺口追问 |
| **确定档**（降级） | `0.70 ≤ C < 0.95` **但无实质歧义** | **直接执行，不复述** —— 关键槽齐全、产物形态唯一时，复述只是空转（见下方硬规格 1） |
"""

CLARITY_ASK_ROW_OLD = """| **追问档** | `C < 0.70` | **仅当澄清门本就要追问时才追问**（判定不变）；若澄清门已放行（如例 A：关键槽齐全、仅次要槽缺）→ 按**复述档**处理，**不得新增追问** |
"""
CLARITY_ASK_ROW_NEW = """| **追问档** | `C < 0.70` | **仅当澄清门本就要追问时才追问**（判定不变）；若澄清门已放行（如例 A：关键槽齐全、仅次要槽缺、**无实质歧义**）→ **直接执行**，**不得新增追问、不得复述** |
"""

CLARITY_SPEC_OLD = """**复述档的三条硬规格**：

1. **一句话**，且**必须引用用户原话里的词**（≥1 个对象词 + ≥1 个产出词）—— 引用不出即视为「尚未确定」，退回追问档；
2. **不得新增**用户没说过的内容（新增即视为理解错误），只允许删与并；
3. 复述**并入【结论】首行的前置短句**（形如「按你给的 ⟨引用原话里的词⟩ —— ⟨结论⟩」）：**不新增输出字段、不改输出硬契约**，也不出现内部名或过程叙述。
"""
CLARITY_SPEC_NEW = """**复述档的四条硬规格**（**实质歧义驱动** —— 判据一句话：**能直接做就不复述；可能做偏才复述**）：

1. **有实质歧义**（决定性条件）：`T`(任务) / `O`(对象) / 产出物形态三者中，**至少一个有两种以上合理读法**，且不同读法会产出**不同的产物**。
   - **不构成实质歧义**（→ **直接执行，免复述**）：关键槽齐全；只是表述口语化；只是没说要什么格式（默认按 `library/output-spec.md` 交付）；只是信息不全但**不改变产物形态**。
2. **一句话**，且**必须引用用户原话里的词**（≥1 个对象词 + ≥1 个产出词）—— 引用不出即视为「尚未确定」，退回追问档；
3. **不得新增**用户没说过的内容（新增即视为理解错误），只允许删与并；
4. 复述**并入【结论】首行的前置短句**（形如「按你给的 ⟨引用原话里的词⟩ —— ⟨结论⟩」）：**不新增输出字段、不改输出硬契约**，也不出现内部名或过程叙述。
"""

CLARITY_WHY_OLD = """且**只在 0.70–0.95 这一档**触发，`C ≥ 0.95` 与「通用知识型」都**免复述**。"""
CLARITY_WHY_NEW = """且**只在 0.70–0.95 这一档、并且确实存在实质歧义时**才触发，`C ≥ 0.95`、关键槽齐全与「通用知识型」都**免复述**。"""

CLARITY_CASEA_OLD = """| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689`（数值 <0.70，**但澄清门已放行 → 按复述档处理**，见下方前置约定 ②） | 放行（例外 2） | **复述档**（一句话复述并入【结论】首行） |
"""
CLARITY_CASEA_NEW = """| 例 A | 「x→0 时 (sin x − x)/x³ 为什么不能等价无穷小？」 | `0.689`（数值 <0.70，**但澄清门已放行**，见下方前置约定 ②） | 放行（例外 2） | **确定档（降级为执行）** —— 对象 / 任务 / 产出唯一，**无实质歧义** → 直接执行 |
"""

CLARITY_NOTE_OLD = """> **注意例 A**：澄清门判「放行」（关键槽齐全），而 `C = 0.689 < 0.70` —— 此时**只复述、不追问**（复述并入【结论】首行），
> 这正是「本门不改变追问判定」的含义，也避免了与例外 2「缺 `W/C/B` 一律不追问」冲突。
"""
CLARITY_NOTE_NEW = """> **注意例 A**：澄清门判「放行」（关键槽齐全），而 `C = 0.689 < 0.70` —— 此时**直接执行，既不复述也不追问**
> （关键槽齐全 = **无实质歧义**），这正是「本门不改变追问判定」的含义，也避免了与例外 2「缺 `W/C/B` 一律不追问」冲突。
>
> **例 F（实质歧义 → 复述档）**：「帮我整理一下这学期的重点」—— 澄清门放行（对象「这学期」明确），
> 但「这学期」可指 3 门课或全部课程，**读法不同 → 产物不同** → **有实质歧义** → **复述档**
> （一句话复述并入【结论】首行）。这才是复述档唯一该被触发的情形。
"""


def patch_clarity():
    n = 0
    for old, new, label, rel in (
            (CLARITY_HEAD_OLD, CLARITY_HEAD_NEW, 'B2 clarity §3.1 标题', 'library/clarity.md'),
            (CLARITY_RESTATE_ROW_OLD, CLARITY_RESTATE_ROW_NEW, 'B2 clarity 复述档行', 'library/clarity.md'),
            (CLARITY_ASK_ROW_OLD, CLARITY_ASK_ROW_NEW, 'B2 clarity 追问档行', 'library/clarity.md'),
            (CLARITY_SPEC_OLD, CLARITY_SPEC_NEW, 'B2 clarity 四条硬规格', 'library/clarity.md'),
            (CLARITY_WHY_OLD, CLARITY_WHY_NEW, 'B2 clarity 为什么要有这道门', 'library/clarity.md'),
            (CLARITY_CASEA_OLD, CLARITY_CASEA_NEW, 'B2 clarity 例 A 行', 'library/clarity.md'),
            (CLARITY_NOTE_OLD, CLARITY_NOTE_NEW, 'B2 clarity 例 A 注意 + 例 F', 'library/clarity.md'),
            (CONFIG_COMMENT_OLD, CONFIG_COMMENT_NEW, 'B2 config 注释', 'config.yaml'),
    ):
        n += sub_once(rel, old, new, label)
    return n


# ============================================================================
# B3 —— 记忆口径：续接固定回话唯一副本
# ============================================================================

MEMORY_S32_ANCHOR = """## 4. 红线"""

MEMORY_S32_BLOCK = """### 3.2 续接固定回话（唯一副本）

用户说「**接着上次**」「**继续上次那个**」「**你之前不是说过吗**」，而当前会话没有相关上下文时，
**先说实话，再给出路**，不得含糊暗示「我可能记得」：

> 「我没有跨会话的记忆，上次的内容我这边没留存 —— 你把上次的结论贴一句，我接着往下做。
> 也可以说一句「**记住这次**」，我就把这次的结果存进档案，下次你自己指定读取。」

**三条硬约束**：
1. **不得假称记得**：不说「我记得」「上次我们聊到」，也不猜内容填空。
2. **不得只说「不行」**：必须同时给出**两条出路**（贴摘要 / 明确要求写入档案）。
3. **不主动读档**：即使档案存在，也要用户明确指定才读（见 §5 用户控制）。

**口径单一来源**：`SKILL.md` 会话连续性段落与 `README.md` §2.2 只描述**规则**，
**回话措辞以本节为准**，三处不得各写一套。

"""


def patch_memory():
    n = 0
    n += sub_once('library/memory.md', MEMORY_S32_ANCHOR, MEMORY_S32_BLOCK + MEMORY_S32_ANCHOR,
                  'B3 memory §3.2')
    n += sub_once(
        'SKILL.md',
        '用户要求续接但当前会话没有相关上下文时，简短说明缺少的材料，请其提供摘要或明确指定可读取的档案。',
        '用户要求续接但当前会话没有相关上下文时，按 `library/memory.md` §3.2 的**续接固定回话**'
        '说明缺少的材料，并给出两条出路（贴上一轮摘要 / 说一句「记住这次」）。',
        'B3 SKILL 会话连续性')
    return n


# ============================================================================
# C1 —— 越界仲裁顺序
# ============================================================================

CONFIG_OOS_OLD = """  # **越界信号**：与 DUT、学习、校园生活均无关的通用事务 → **命中即不接管**（优先级最高，压过宽词表）
  # ⚠️ **互斥不变式**：本表必须与 learning_markers / dlut_markers / learning_intents **零交集**，
  #    否则「优先级最高」会吞掉合法域路由（实例：「基金」既在 R4 触发词、又曾在本表 → R4 grant-apply 永不可达）。
  #    多义词（金融基金 / 面试用途）不入本表，归属交由**主键 T+O** 判定（同 boundary_note 的「面试」先例）。
"""

CONFIG_OOS_NEW = """  # **越界信号**：与 DUT、学习、校园生活均无关的通用事务 → **命中只做初筛，归属由下面的仲裁顺序定**
  # ⚠️ **互斥不变式**：本表必须与 learning_markers / dlut_markers / learning_intents **零交集**，
  #    否则越界硬停会吞掉合法域路由（实例：「基金」既在 R4 触发词、又曾在本表 → R4 grant-apply 永不可达）。
  #    多义词（金融基金 / 面试用途）不入本表，归属交由**主键 T+O** 判定（同 boundary_note 的「面试」先例）。
"""

CONFIG_ARB_ANCHOR = """  boundary_note: 单词命中不等于该接管"""

CONFIG_ARB_BLOCK = """  # **越界仲裁顺序**（唯一副本）：`out_of_scope_markers` 只做**初筛**，不具终判效力。归属按以下顺序判：
  #   1. **需求主键 T(任务) + O(对象)** 落在 20 域之一 → **接管**（越界词只是用途或背景）；
  #   2. 主键落不到任何域 → 再看是否命中越界词 → 命中则**不接管**；
  #   3. 两者都不成立 → **不接管**（宁可不接管，也不硬塞域）。
  #   顺序**不可交换**；多义词归属**只由主键决定**，不得由单词命中决定。
  arbitration: [需求主键 T+O, 越界词命中, 都不成立则不接管]
"""

SKILL_S15_OLD = """### 1.5 越界信号（命中即**不接管**，优先级最高）"""

SKILL_S15_NEW = """### 1.5 越界信号（初筛 · 归属按仲裁顺序）"""

SKILL_ARB_ANCHOR = """> ⚠️ **单词命中 ≠ 该接管**：判据是**需求主键 T(任务) + O(对象)**。"""

SKILL_ARB_BLOCK = """**仲裁顺序（唯一副本 = `config.yaml` 的 `trigger.arbitration`）**：

1. 先看**需求主键 `T`(任务) + `O`(对象)** 是否落在 20 域之一 → 落得到 → **接管**（越界词只是用途或背景）；
2. 主键落不到任何域 → 再看是否命中上表 → 命中 → **不接管**；
3. 两者都不成立 → **不接管**。

> **顺序不可交换**：越界表 = **初筛**，需求主键 = **终判**。多义词（「基金」「面试」）的归属
> **只由主键决定**；不得因为命中一个越界词就把整条请求硬停。

"""

DOMAIN_S2_ANCHOR = """## 3. 无域兜底"""

DOMAIN_S21_BLOCK = """### 2.1 越界词只是初筛（仲裁顺序）

`trigger.out_of_scope_markers` 命中的词**不具终判效力**。归属按固定**仲裁顺序**：

1. **需求主键 `T`(任务) + `O`(对象)** 落在 20 域之一 → **接管**（越界词只是用途或背景）；
2. 主键落不到任何域 → 再看是否命中越界词 → 命中则**不接管**；
3. 两者都不成立 → **不接管**（宁可不接管，也不硬塞域）。

> **顺序不可交换**：越界表 = **初筛**，主键 = **终判**；多义词归属**只由主键决定**。
> 唯一副本 = `config.yaml` 的 `trigger.arbitration`；不变式由 `scripts/aligncheck.py` U 组断言。

"""


def patch_oos():
    n = 0
    n += sub_once('config.yaml', CONFIG_OOS_OLD, CONFIG_OOS_NEW, 'C1 config oos comment')
    n += sub_once('config.yaml', CONFIG_ARB_ANCHOR, CONFIG_ARB_BLOCK + CONFIG_ARB_ANCHOR,
                  'C1 config arbitration')
    n += sub_once('SKILL.md', SKILL_S15_OLD, SKILL_S15_NEW, 'C1 SKILL §1.5 title')
    n += sub_once('SKILL.md', SKILL_ARB_ANCHOR, SKILL_ARB_BLOCK + SKILL_ARB_ANCHOR,
                  'C1 SKILL arbitration')
    n += sub_once('library/domain-review.md', DOMAIN_S2_ANCHOR, DOMAIN_S21_BLOCK + DOMAIN_S2_ANCHOR,
                  'C1 domain-review §2.1')
    return n


# ============================================================================
# C2 —— 登录回交
# ============================================================================

LOGIN_S41_ANCHOR = """### L3 禁读（无论用户是否登录，一律不读）"""

LOGIN_S41_BLOCK = """### 4.1 看完之后的交还（三步，防「打开就结束」）

登录窗口打开**不等于交付完成**。用户看完之后，控制权必须回到对话里。固定走三步：

1. **要最少的必要信息**：「你看完了就把回答需要的部分贴给我（比如课表里的周次和节次），我接着做。」
2. **给不登录的出路**：「不想登录也行，我按通用流程给你（去哪办、带什么材料、找哪个部门）。」
3. **给替代来源**：「或者我换公开来源（学院通知 / 公开课表 / 信息公开）再试一次。」

**交还三步**的固定一句话（唯一副本，措辞不得改写）：

> 「你看完了把关键信息贴给我就行，我接着做；不想登录也告诉我，我给通用流程。」

> **禁止**把「本次会话已关闭 / Profile 已删除」当成交付终点 —— 那是**过程**，不是**结果**。
> 用户没拿到答案就关窗口 = 本次交付失败；交还话术**优先于**权限与安全叙事（安全细节在用户问起时再说）。

"""


def patch_login():
    n = 0
    n += sub_once('library/login-policy.md', LOGIN_S41_ANCHOR, LOGIN_S41_BLOCK + LOGIN_S41_ANCHOR,
                  'C2 login §4.1')
    return n


# ============================================================================
# C3 —— 体验层自检指标（experience.md §7）+ 硬规则 3 交还
# ============================================================================

EXPERIENCE_S7_ANCHOR = """维护口径：新增 / 修改入口文案时**只改本清单**，再同步上述四处呈现位；不要在多处各自造句子。"""

EXPERIENCE_S7_BLOCK = EXPERIENCE_S7_ANCHOR + """

---

## 7. 体验层自检指标（维护者视图 · 静态零数据）

体验层不是「感觉好不好」，而是**可核对的 5 项**。全部由 `scripts/` 下的校验器静态计算，
**零用户数据、零运行时采集**，与硬规则 5「本地指标默认不记录」一致 —— 本组指标**不需要用户开启任何开关**。

| # | 指标 | 合格判据（可复现） | 断言源 |
|---|---|---|---|
| 1 | **呈现层零内部名** | 全部输出块内不出现内部名（域与规则 ID / 内部文件名 / 流程术语 / 合规标注 / 维护者计数） | `scripts/aligncheck.py` X 组「输出块泄漏内部名」 |
| 2 | **入口文案单源** | 四处呈现位的起始句型与 §6 唯一副本**逐条一致** | `scripts/aligncheck.py` X 组「的起始句型与唯一副本不一致」 |
| 3 | **澄清门歧义驱动** | 复述只在存在**实质歧义**时发生；关键槽齐全即免复述 | `scripts/regress.sh` `[9]`「实质歧义」 |
| 4 | **越界仲裁单点** | 越界词只做初筛；归属由固定**仲裁顺序**定，且越界表与 20 域词表零交集 | `scripts/aligncheck.py` U 组「仲裁顺序」 |
| 5 | **交还与记忆口径** | 登录后必有「**交还三步**」；续接请求必有「**续接固定回话**」 | `scripts/aligncheck.py` Y 组「续接固定回话」 |

**口径**：本组只衡量**本包资产的一致性**，不衡量模型输出质量，也不作为真实成效证据。
**默认不记录**：本组不写任何文件、不产生 trace；需要运行时指标时另见 `scripts/metrics.py`
（仍需用户明确启用，见 `SKILL.md` 硬规则 5）。
**维护**：新增或修改体验规则时，必须同时更新本表与对应断言，否则 `scripts/aligncheck.py` Y 组会 FAIL。"""

EXPERIENCE_S3_ANCHOR = """| 来源核验状态 | 说「已核对」「没核到原始出处」「只有二手转述」三档人话，不写核验字段名 |
"""

EXPERIENCE_S3_NEW = EXPERIENCE_S3_ANCHOR + """| 登录后交还 | 不说「会话已关闭 / Profile 已删除」，改说「你看完了把关键信息贴给我就行，我接着做；不想登录也告诉我，我给通用流程」 |
| 续接请求 | 不说「无跨会话记忆 / 未命中档案」，改说「我没有跨会话的记忆，你把上次的结论贴一句，我接着往下做」 |
"""

SKILL_HR3_ANCHOR = """   - **会话与 Profile 隔离**："""

SKILL_HR3_BLOCK = """   - **看完之后的交还**：用户看完后按 `library/login-policy.md` §4.1 的**交还三步**回到对话
     （要最少的必要信息 → 或改走通用流程 → 或换公开来源）；不把「会话已关闭」当成交付终点。
"""


def patch_metrics_face():
    n = 0
    n += sub_once('library/experience.md', EXPERIENCE_S7_ANCHOR, EXPERIENCE_S7_BLOCK,
                  'C3 experience §7')
    n += sub_once('library/experience.md', EXPERIENCE_S3_ANCHOR, EXPERIENCE_S3_NEW,
                  'C3 experience §3 rows')
    n += sub_once('SKILL.md', SKILL_HR3_ANCHOR, SKILL_HR3_BLOCK + SKILL_HR3_ANCHOR,
                  'C2/C3 SKILL 硬规则 3 交还')
    return n


# ============================================================================
# 校验器同步：regress.sh [9] / aligncheck U 组 · 文档计数
# ============================================================================

REGRESS_OLD = """  # 红线优先于本门 + 例外 6 视为达标（防「为了确认而削弱合规」与「假复述」）"""

REGRESS_SPEC_OLD = """  # 复述档三条硬规格"""

REGRESS_SPEC_NEW = """  # 复述档四条硬规格（第 1 条 = 存在实质歧义，决定性条件）"""

REGRESS_NEW = """  # 实质歧义驱动：无实质歧义即免复述（防「关键槽齐全还白复述一遍」）
  if grep -qF '实质歧义' "$_cl" 2>/dev/null; then _ok "复述档 = 实质歧义驱动"; else _fail "未声明实质歧义驱动（复述会退化为白复述）"; fi
  if grep -qF '免复述' "$_cl" 2>/dev/null; then _ok "已声明无实质歧义 → 免复述"; else _fail "缺「无实质歧义 → 免复述」降级路径"; fi
  if grep -qF '复述档的四条硬规格' "$_cl" 2>/dev/null; then _ok "复述规格已升级为四条"; else _fail "复述规格未升级为四条（歧义判据不在首位）"; fi
  # 越界表只做初筛，终判看需求主键 T+O（防「单词命中即不接管」）
  if grep -qF 'arbitration:' config.yaml 2>/dev/null; then _ok "config.yaml 声明越界仲裁顺序"; else _fail "缺 trigger.arbitration（越界表被当成终判）"; fi
  if grep -qF '优先级最高' config.yaml 2>/dev/null; then _fail "config.yaml 仍残留「优先级最高」（越界表压过主键）"; else _ok "config.yaml 已撤下「优先级最高」"; fi
  if grep -qF '初筛' library/domain-review.md 2>/dev/null; then _ok "domain-review 已声明越界 = 初筛"; else _fail "domain-review 未声明初筛语义"; fi
  # 记忆口径单源：续接固定回话只在 memory.md 存一份
  if grep -qF '续接固定回话' library/memory.md 2>/dev/null; then _ok "memory.md 有「续接固定回话」唯一副本"; else _fail "缺「续接固定回话」（记忆口径分裂）"; fi
  if grep -qF '不得假称记得' library/memory.md 2>/dev/null; then _ok "续接回话不得假称记得"; else _fail "缺「不得假称记得」硬约束"; fi
  # 红线优先于本门 + 例外 6 视为达标（防「为了确认而削弱合规」与「假复述」）"""

ALIGNCHK_GROUPS_OLD = """检查项（20 组：A–D、F–Q、S–U、X）："""
ALIGNCHK_GROUPS_NEW = """检查项（21 组：A–D、F–Q、S–U、X、Y）："""

ALIGNCHK_XDOC_OLD = (
    "  X 学生呈现层：`library/experience.md` 在位（白名单 / 禁止物 / 翻译规则 / 三视图 / 反例 / 起始句型）·\\n"
    "    1 级清单三处同步 · 输出契约两处指针在位 · 四处入口文案与唯一副本逐条一致 · 组数声明同源\\n\"\"\""
)
ALIGNCHK_XDOC_NEW = (
    "  X 学生呈现层：`library/experience.md` 在位（白名单 / 禁止物 / 翻译规则 / 三视图 / 反例 / 起始句型）·\n"
    "    1 级清单三处同步 · 输出契约两处指针在位 · 四处入口文案与唯一副本逐条一致 · 组数声明同源\n"
    "  Y 体验层闭环：澄清门实质歧义驱动（免白复述）· 记忆口径单源（续接固定回话）· 越界仲裁顺序（初筛→终判）·\n"
    "    登录交还三步（交还优先于权限叙事）· 体验层自检指标表（零用户数据 / 默认不记录）\n\"\"\""
)

ALIGNCHK_U_OLD = """        # 判据双处声明：单词命中≠接管（主键 T+O）；越界优先级最高
        for _f8, _t8, _needs in (('config.yaml', cfg, ('需求主键', '优先级最高')),
                                 ('SKILL.md', _sk, ('归属由主键定', '优先级最高'))):
            for _n8 in _needs:
                if _n8 not in _t8:
                    bad(_f8, '触发门判据缺「%s」（单词命中≠接管 / 越界优先）' % _n8)
"""

ALIGNCHK_U_NEW = """        # 判据双处声明：单词命中≠接管（主键 T+O）；越界只做初筛、归属按仲裁顺序
        for _f8, _t8, _needs in (('config.yaml', cfg, ('需求主键', '仲裁顺序')),
                                 ('SKILL.md', _sk, ('归属由主键定', '仲裁顺序'))):
            for _n8 in _needs:
                if _n8 not in _t8:
                    bad(_f8, '触发门判据缺「%s」（单词命中≠接管 / 越界按仲裁顺序）' % _n8)
        # 越界词只做初筛：仲裁顺序唯一副本在位，且不再自称「优先级最高」
        if not re.search(r'^\\s*arbitration:', cfg, re.M):
            bad('config.yaml', '缺 trigger.arbitration（越界仲裁顺序唯一副本）')
        if '优先级最高' in cfg or '优先级最高' in _sk:
            bad('config.yaml', '越界表仍自称「优先级最高」（应为初筛，归属由主键终判）')
        if '初筛' not in _sk or '初筛' not in rd('library/domain-review.md'):
            bad('SKILL.md', '越界初筛语义未在 SKILL.md / domain-review.md 双处声明')
"""

ALIGNCHK_UMSG_OLD = "            bad('config.yaml', '越界词与接管词冲突 %d 个（越界优先级最高，会吞掉域路由）: %s'"

ALIGNCHK_UMSG_NEW = "            bad('config.yaml', '越界词与接管词冲突 %d 个（越界为初筛，冲突即吞掉域路由）: %s'"

ALIGNCHK_XNG_OLD = """        _xngroups = 20"""
ALIGNCHK_XNG_NEW = """        _xngroups = 21"""

Y_GROUP_ANCHOR = """    # ---------- 汇总 ----------"""

Y_GROUP = r"""    # ---------- Y 体验层闭环（B2/B3/C1/C2/C3）----------
    # 体验层的五条规则各自「只有一个副本 + 至少一处断言」，防止再次退化成零断言层。
    _cf = rd('config.yaml')
    _cl = rd('library/clarity.md')
    _mm = rd('library/memory.md')
    _lp = rd('library/login-policy.md')
    _sk = rd('SKILL.md')
    _xt = rd(XPATH)

    # [Y1] B2 澄清门：复述档必须是「实质歧义驱动」，且降级路径写清
    if '实质歧义' not in _cl:
        bad('library/clarity.md', '复述档未声明「实质歧义」判据（会退化为白复述）')
    if '无实质歧义' not in _cl or '免复述' not in _cl:
        bad('library/clarity.md', '复述档缺少「无实质歧义 → 直接执行（免复述）」降级路径')
    if '实质歧义' not in _cf:
        bad('config.yaml', '澄清门阈值注释未同步「实质歧义」语义')
    _y1 = section(_cl, r'^###\s*3\.1\s')
    if not _y1 or '**确定档**（降级）' not in _y1:
        bad('library/clarity.md', '§3.1 关系表缺少「确定档（降级）」一行')
    if not _y1 or '复述档的四条硬规格' not in _y1:
        bad('library/clarity.md', '§3.1 未把复述规格升级为「四条（含实质歧义）」')

    # [Y2] B3 记忆口径：续接固定回话唯一副本 + 三处同源
    _y2 = section(_mm, r'^###\s*3\.2\s*[^\n]*续接')
    if '续接固定回话' not in _mm:
        bad('library/memory.md', '缺少 §3.2「续接固定回话」唯一副本')
    if not _y2 or '不得假称记得' not in _y2:
        bad('library/memory.md', '§3.2 缺少「不得假称记得」硬约束')
    if not _y2 or '两条出路' not in _y2:
        bad('library/memory.md', '§3.2 缺少「必须给出两条出路」硬约束')
    if '`library/memory.md` §3.2' not in _sk:
        bad('SKILL.md', '会话连续性段落未指向 `library/memory.md` §3.2（口径未同源）')

    # [Y3] C1 越界仲裁：初筛 → 终判，且「优先级最高」已彻底退场
    if '仲裁顺序' not in _cf or '仲裁顺序' not in _sk:
        bad('config.yaml', '越界「仲裁顺序」未在 config.yaml / SKILL.md 双处声明')
    if '优先级最高' in _cf or '优先级最高' in _sk:
        bad('SKILL.md', '越界表仍自称「优先级最高」（应降级为初筛）')
    if not re.search(r'^\s*arbitration:', _cf, re.M):
        bad('config.yaml', '缺少 trigger.arbitration 键')
    _y3 = section(rd('library/domain-review.md'), r'^###\s*2\.1\s')
    if not _y3 or '初筛' not in _y3 or '终判' not in _y3:
        bad('library/domain-review.md', '§2.1 未声明「初筛 → 终判」仲裁语义')

    # [Y4] C2 登录交还：三步 + 固定一句话 + 交还优先于权限叙事
    if '交还三步' not in _lp:
        bad('library/login-policy.md', '缺少「交还三步」')
    if '看完了' not in _lp:
        bad('library/login-policy.md', '缺少交还固定一句话（唯一副本）')
    if '不想登录也告诉我，我给通用流程' not in _lp:
        bad('library/login-policy.md', '交还固定一句话措辞被改写（唯一副本失效）')
    if '交还话术**优先于**权限与安全叙事' not in _lp:
        bad('library/login-policy.md', '缺少「交还优先于权限叙事」的顺序声明')
    if '交还' not in section(_sk, r'^##\s*硬规则'):
        bad('SKILL.md', '硬规则未声明「看完之后的交还」')

    # [Y5] C3 体验层自检指标：5 项静态指标 + 零数据承诺 + 断言源交叉在位
    _y5 = section(_xt, r'^##\s*7[.、]?\s*体验层自检指标')
    if not _y5:
        bad(XPATH, '缺少 §7「体验层自检指标」')
    for _m in ('呈现层零内部名', '入口文案单源', '澄清门歧义驱动', '越界仲裁单点', '交还与记忆口径'):
        if _m not in _y5:
            bad(XPATH, '§7 指标表缺项：%s' % _m)
    if '零用户数据' not in _y5 or '默认不记录' not in _y5:
        bad(XPATH, '§7 未声明「零用户数据 / 默认不记录」')
    _y5src = rd('scripts/aligncheck.py') + rd('scripts/regress.sh')
    for _k in ('输出块泄漏内部名', '的起始句型与唯一副本不一致', '实质歧义', '仲裁顺序', '续接固定回话'):
        if _k not in _y5src:
            bad(XPATH, '§7 指标断言的断言源不成立（缺 %s）' % _k)

"""


def patch_validators():
    n = 0
    n += sub_once('scripts/regress.sh', REGRESS_SPEC_OLD, REGRESS_SPEC_NEW, 'B2 regress 规格数注释')
    n += sub_once('scripts/regress.sh', REGRESS_OLD, REGRESS_NEW, 'B2 regress [9]')
    n += sub_once('scripts/aligncheck.py', ALIGNCHK_GROUPS_OLD, ALIGNCHK_GROUPS_NEW, 'aligncheck 组数 docstring')
    n += sub_once('scripts/aligncheck.py', ALIGNCHK_XDOC_OLD, ALIGNCHK_XDOC_NEW, 'aligncheck X/Y docstring')
    n += sub_once('scripts/aligncheck.py', ALIGNCHK_U_OLD, ALIGNCHK_U_NEW, 'aligncheck U 组仲裁')
    n += sub_once('scripts/aligncheck.py', ALIGNCHK_UMSG_OLD, ALIGNCHK_UMSG_NEW, 'aligncheck U 组冲突文案')
    n += sub_once('scripts/aligncheck.py', ALIGNCHK_XNG_OLD, ALIGNCHK_XNG_NEW, 'aligncheck _xngroups')
    n += sub_once('scripts/aligncheck.py', Y_GROUP_ANCHOR, Y_GROUP + Y_GROUP_ANCHOR, 'aligncheck Y 组')
    n += collapse_dup('scripts/aligncheck.py', Y_GROUP, 'aligncheck Y 组去重')
    n += sub_re('scripts/aligncheck.py', r'检查项（20 组：', '检查项（21 组：', 'aligncheck 组数 docstring 兜底')
    return n


def patch_counts():
    n = 0
    for rel in ('README.md', 'INSTALL.md'):
        t = read(rel)
        if '20 组断言' in t:
            write(rel, t.replace('20 组断言', '21 组断言'))
            n += 1
    return n


# ============================================================================
# 负向测试：5 类新注入
# ============================================================================

INJECTORS = '''def inject_restate_no_ambiguity(tree):
    """B2 回归：复述档退回「档位驱动」，删掉实质歧义判据。"""
    p = os.path.join(tree, 'library', 'clarity.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('实质歧义', '档位条件')


def inject_memory_no_fixed_reply(tree):
    """B3 回归：§3.2 续接固定回话被改写（唯一副本失效）。"""
    p = os.path.join(tree, 'library', 'memory.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('不得假称记得', '尽量不要说得太肯定')


def inject_login_no_handback(tree):
    """C2 回归：登录后不再交还（删掉交还三步与固定一句话）。"""
    p = os.path.join(tree, 'library', 'login-policy.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('交还三步', '权限说明').replace(
        '不想登录也告诉我，我给通用流程', '需重新授权后继续')


def inject_oos_priority_supreme(tree):
    """C1 回归：越界表改回「优先级最高」（单词命中即终判）。"""
    p = os.path.join(tree, 'config.yaml')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('arbitration:', 'x_arbitration:')
    return [p], t.replace('命中只做初筛，归属由下面的仲裁顺序定',
                          '命中即不接管（优先级最高，压过宽词表）')


def inject_experience_no_metrics(tree):
    """C3 回归：§7 体验层自检指标被删除（体验层重新退化为零指标层）。"""
    p = os.path.join(tree, 'library', 'experience.md')
    t = io.open(p, encoding='utf-8').read()
    i = t.find('## 7. 体验层自检指标')
    return [p], (t[:i] if i >= 0 else t)


'''


NEW_CASES = """        ('澄清门复述档失去歧义判据（B2）', inject_restate_no_ambiguity,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 澄清门实质歧义'),
        ('续接固定回话被改写（B3）', inject_memory_no_fixed_reply,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 记忆口径单源'),
        ('登录后不再交还（C2）', inject_login_no_handback,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 登录交还三步'),
        ('越界表改回优先级最高（C1）', inject_oos_priority_supreme,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 越界仲裁顺序'),
        ('体验层自检指标被删除（C3）', inject_experience_no_metrics,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck Y 体验层自检指标'),
"""

NT_ANCHOR = """    ('入口文案分叉（README 起始句型与唯一副本不一致）', inject_entry_phrase_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck X 起始句型唯一副本'),
"""

NT_NEW = NT_ANCHOR + NEW_CASES

NT_FN_ANCHOR = """def inject_entry_phrase_drift(tree):"""


def patch_negative_test():
    n = 0
    n += sub_once('scripts/negative_test.py', NT_FN_ANCHOR, INJECTORS + NT_FN_ANCHOR,
                  'negative_test injectors')
    n += sub_once('scripts/negative_test.py', NT_ANCHOR, NT_NEW, 'negative_test cases')
    return n


# ============================================================================
# 构建登记
# ============================================================================

REG_OLD = """    ('step69_experience_layer.py',   '**学生呈现层收口（零行为变更）**：新增 1 级规则 `library/experience.md`（前台白名单 / 禁止物 / 翻译规则 / 三视图 / 起始句型唯一副本）· 输出契约两处指针 · 安装后三行首次引导 · 四处入口文案收口 · aligncheck X 组 + 2 类负向注入'),
"""

REG_NEW = REG_OLD + """    ('step70_experience_closure.py', '**体验层收口 ②（B2/B3/C1/C2/C3）**：澄清门改为**实质歧义驱动**（关键槽齐全即免复述，消除白复述空转）· 记忆新增 §3.2「续接固定回话」唯一副本 · 越界新增 `trigger.arbitration` 仲裁顺序（越界表=初筛，需求主键=终判，撤下「优先级最高」）· 登录新增 §4.1「交还三步」+ 固定一句话 · `experience.md` §7 体验层自检指标（5 项静态零数据）· aligncheck Y 组 + 5 类负向注入'),
"""

BUILD_README_OLD = """| 28 | `step69_experience_layer.py` |"""

BUILD_README_NEW = """| 29 | `step70_experience_closure.py` | **体验层收口 ②（B2/B3/C1/C2/C3）**：澄清门改为**实质歧义驱动**（`clarity.md` §3.2 四条硬规格 + 关系表降级行；关键槽齐全即免复述）· `memory.md` §3.2「续接固定回话」唯一副本 · `config.yaml` `trigger.arbitration` 仲裁顺序（越界表 = 初筛，需求主键 T+O = 终判；撤下「优先级最高」）· `login-policy.md` §4.1「交还三步」+ 固定一句话 · `experience.md` §7 体验层自检指标（5 项 / 零用户数据 / 默认不记录）· `aligncheck` Y 组 + 5 类负向注入 · 组数 20 → 21 | 新增层 |
| 28 | `step69_experience_layer.py` |"""


def patch_build_registry():
    n = 0
    n += sub_once('scripts/_build/v3/rebuild.py', REG_OLD, REG_NEW, 'rebuild LAYERS')
    n += sub_once('scripts/_build/v3/README.md', BUILD_README_OLD, BUILD_README_NEW, 'build README row')
    return n


# ============================================================================

def main():
    steps = [
        ('B2 澄清门实质歧义驱动', patch_clarity),
        ('B3 续接固定回话唯一副本', patch_memory),
        ('C1 越界仲裁顺序', patch_oos),
        ('C2 登录交还三步', patch_login),
        ('C3 体验层自检指标', patch_metrics_face),
        ('校验器同步（regress/aligncheck Y 组）', patch_validators),
        ('文档计数同步', patch_counts),
        ('负向注入登记', patch_negative_test),
        ('构建登记', patch_build_registry),
    ]
    total = 0
    for label, fn in steps:
        c = fn()
        total += c
        print('  %-34s 改动 %d 处' % (label, c))
    print('-' * 60)
    if total == 0:
        print('step70：改动 0 处（幂等跳过，已是固定点）')
    else:
        print('step70：改动 %d 处' % total)
    return 0


if __name__ == '__main__':
    sys.exit(main())
