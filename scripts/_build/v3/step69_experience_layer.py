# -*- coding: utf-8 -*-
"""
step69 —— **学生呈现层（体验层）收口**（零行为变更）

解决的问题（体验层缺陷 · 批次 A + B1）：

  * A1 呈现层无真相源：92 个库内 skill 的 `**输出**` 块同时承担「契约」与「渲染」两职，
    前台白名单 / 禁止物 / 翻译规则散落在 `output-spec.md` 的散文里，没有唯一副本，
    也没有任何断言 —— 这是全包唯一的「零断言层」。
  * A2 安装后体验断崖：装完只回一句「安装完成」，学生不知道能做什么、怎么开口。
  * B1 入口文案四处分叉：`README.md` / `SKILL.md` / `commands/qihang.md` / `scripts/qihang.sh`
    各有一份起始句型清单，条目数与措辞互不相同。

本层只改**呈现层与入口文案**，不触碰触发门、路由、澄清门与记忆默认值 —— 零行为变更。

幂等：全部走「精确串替换 + 已替换即跳过」，重复执行不再改动。
"""

import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))

CHANGED = []
SKIPPED = []


def _p(rel):
    return os.path.join(ROOT, rel)


def read(rel):
    with io.open(_p(rel), encoding='utf-8') as f:
        return f.read()


def write(rel, text):
    with io.open(_p(rel), 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)


def sub_once(rel, old, new, label):
    """精确串替换。

    幂等判定以 **new 是否已在位** 为准（追加式编辑的 new 包含 old，只看 old 会重复插入）。
    """
    t = read(rel)
    if new in t:
        SKIPPED.append('%s (%s)' % (rel, label))
        return False
    if old not in t:
        raise SystemExit('[step69] 锚点未命中：%s :: %s' % (rel, label))
    write(rel, t.replace(old, new, 1))
    CHANGED.append('%s (%s)' % (rel, label))
    return True


def collapse_dup(rel, block, label):
    """合并历史重复插入的追加块（幂等护栏修复前的产物），使本层可自愈到不动点。"""
    t = read(rel)
    for dup in (block + u'\n' + block, block + block):
        if dup in t:
            write(rel, t.replace(dup, block))
            CHANGED.append('%s (%s 合并重复块)' % (rel, label))
            return True
    return False


def sub_re(rel, pattern, repl, label, flags=re.M | re.S):
    t = read(rel)
    nt, n = re.subn(pattern, repl, t, count=1, flags=flags)
    if n == 0:
        raise SystemExit('[step69] 正则未命中：%s :: %s' % (rel, label))
    if nt == t:
        SKIPPED.append('%s (%s)' % (rel, label))
        return False
    write(rel, nt)
    CHANGED.append('%s (%s)' % (rel, label))
    return True


def write_if_changed(rel, text):
    cur = read(rel) if os.path.exists(_p(rel)) else None
    if cur == text:
        SKIPPED.append('%s (未变)' % rel)
        return False
    write(rel, text)
    CHANGED.append(rel)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 0. 唯一副本：六个起始句型
# ─────────────────────────────────────────────────────────────────────────────
ENTRIES = [
    '帮我理解这道题',
    '这节课我没听懂，整理重点和笔记',
    '我有作业，先拆任务，再给检查点',
    '安排一周备考计划',
    '查一下学校通知 / 课程安排 / 教务信息',
    '我需要查学术资料，先给检索思路和可信来源',
]

ONBOARD_1 = '**能做什么**：理解题目、整理课堂笔记、拆作业与检查点、备考计划、查学校与课程信息、查学术资料'
ONBOARD_2 = '**怎么开口**：用自然语言说目标即可，不必先选分类；只有会改变答案的关键信息缺失时才会被追问'
ONBOARD_3 = '**一句话示例**：「帮我理解这道题」／「安排一周备考计划」'


# ─────────────────────────────────────────────────────────────────────────────
# 1. 新增 1 级规则：library/experience.md
# ─────────────────────────────────────────────────────────────────────────────
EXPERIENCE_MD = u'''# 学生呈现层（体验层）规则

> **本文件是「用户看到什么」的唯一副本。** 它管**渲染**，不管**决策**：
> 判断逻辑仍在 `library/output-spec.md`（输出契约）、`library/clarity.md`（澄清门）、
> `library/login-policy.md`（外站交接）与 `config.yaml`（触发门）里。
> 若本文件与它们冲突：**决策以它们为准，措辞以本文件为准**。

本文件回答三个问题：**该说 / 不该说 / 怎么说**。

---

## 1. 前台白名单（学生视图只允许出现这些）

1. **自然语言散文**：完整句子、分点、小标题。默认学生视图是**对话**，不是表格报表。
2. **五种小标题**（超出即视为越界）：`结论` · `要点` · `依据` · `下一步` · `不确定的部分`。
3. **结构化内容**：有序 / 无序列表、表格、时间线、公式、代码块、图示 —— 只要它们承载的是**内容**。
4. **来源与日期（自然语言表述）**：如「来自教务处官网，2026-09-01 发布，已核对页面可打开」。
5. **核验状态（自然语言表述）**：如「这条我没能核到原始出处，建议你以官网为准」。

判断口径：**学生读完能直接行动或直接理解** → 白名单；**学生读完还得先学一套内部术语** → 禁止物。

---

## 2. 前台禁止物（默认学生视图一律不出现）

| 类别 | 禁止出现的形态 | 为什么 |
|---|---|---|
| 域与规则 ID | `S1` `R6` `F3` 这类编号，以及 `U 组` `X 组` 这类组名 | 学生不需要知道内部编号体系 |
| 内部文件名 | `clarity.md`、`trigger`、`aligncheck`、`output-spec.md` | 暴露实现细节，且对学生无意义 |
| 流程术语 | 「澄清门」「6 槽位」「U 值」「降级链三档」「未穷尽档 1」 | 内部决策语言，不是学生语言 |
| 合规标注 | `[已降级]`、`[外接] 许可：MIT`、`[无 skill 流程]` 的**标签本身** | 标签属契约层；能力差异要**翻译**成人话，不是贴标签 |
| 维护者计数 | 「92 个 skill」「219 个触发词」这类统计 | 这是给维护者看的，不是给学生看的 |
| 审计结论 | 自检通过率、逐项 OK / WARN 标记、断言清单 | 内部静默自检结果不外显 |

> 注：`library/output-spec.md` §1.4 要求「降级标注只写能力级」，该要求管的是**契约层**（可审计）；
> 本文件管的是**渲染层**（不可见）。二者不冲突：契约里保留标注，学生视图里翻译成自然语言。

---

## 3. 翻译规则（内部信号 → 学生语言）

| 内部信号（契约层） | 学生视图（渲染层） |
|---|---|
| `[已降级]` | 不贴标签，改说「这块我按通用方法给你讲，不是这门课的专属流程」 |
| `[外接]` / 外部桥接 | 改说「这个我可以接一个外部工具帮你做，需要你先允许我调用它」 |
| `[无 skill 流程]` | 改说「这个问题我这儿没有专门的流程，我按一般思路帮你捋」 |
| 澄清门命中、需要追问 | 直接问那一个问题，**不说**「我触发了澄清门」 |
| U 值 / 理解准确率档位 | 不说数值，改说「我先把你的意思复述一遍，你看对不对」 |
| 未命中后自行生成 | 不说「档 3」，改说「我按我的理解先给一版，你可以纠正我」 |
| 来源核验状态 | 说「已核对」「没核到原始出处」「只有二手转述」三档人话，不写核验字段名 |

总原则：**把内部状态翻译成「我现在能做什么 / 你需要知道什么」，而不是「系统内部发生了什么」。**

---

## 4. 三视图

同一份产物，三种读者。**默认只渲染学生视图**。

| 视图 | 触发条件 | 呈现范围 |
|---|---|---|
| 学生视图 | **默认** | 本文件 §1 白名单；§2 禁止物一律不出现；§3 翻译规则生效 |
| 评审视图 | 用户**明确索要**（如「给我看来源清单 / 降级说明」） | 可展示来源与核验状态明细、降级与外部桥接说明；仍不展示内部文件名与编号体系 |
| 维护者视图 | 运行 `scripts/` 下的校验器，或用户**明确索要**结构自检结果 | 计数、断言、逐项标记可全部展示 |

边界：**切换视图必须由用户发起或由脚本发起**，不得由模型「顺手」把维护者视图混进学生视图。

---

## 5. 反例（以下写法一律不合格）

- ❌ 「已命中 S1 域，走 6 槽位澄清门，输出 U 值 0.72。」 —— 内部语言直接外泄
- ❌ 「本次输出为 `[已降级]`，许可：MIT。」 —— 标签未翻译
- ❌ 「本包含 92 个库内 skill、219 个触发词。」 —— 维护者计数进了学生视图
- ❌ 「自检结果：OK 41 / WARN 3 / FAIL 0。」 —— 审计结论外显
- ✅ 「你说的是「这门课跟不上」，我先确认一下：是听不懂推导，还是记不住公式？」 —— 澄清门翻译成人话
- ✅ 「这块我按通用方法给你讲，不是这门课的专属流程，但结论仍然可用。」 —— 降级翻译成人话

---

## 6. 起始句型（唯一副本）

以下六句是**全包唯一的入口文案副本**。`README.md`、`SKILL.md`、`commands/qihang.md`、
`scripts/qihang.sh` 中的起始句型必须与本清单**逐条一致**（由 `scripts/aligncheck.py` 的 X 组断言）。

1. 「帮我理解这道题」
2. 「这节课我没听懂，整理重点和笔记」
3. 「我有作业，先拆任务，再给检查点」
4. 「安排一周备考计划」
5. 「查一下学校通知 / 课程安排 / 教务信息」
6. 「我需要查学术资料，先给检索思路和可信来源」

维护口径：新增 / 修改入口文案时**只改本清单**，再同步上述四处呈现位；不要在多处各自造句子。
'''


# ─────────────────────────────────────────────────────────────────────────────
# 2. 输出契约两处指针
# ─────────────────────────────────────────────────────────────────────────────
PTR_OUTPUT_SPEC = u'''> **前台渲染口径**：`[已降级]` 属**契约层**标注（可审计）；默认**学生视图不渲染**该标签，
> 由 `library/experience.md` 的「翻译规则」改写为自然语言。契约层保留标注、渲染层翻译人话，二者不冲突。
'''

PTR_LINK = u'''> **前台渲染口径**：`[外接]` 同样属**契约层**标注；默认**学生视图不渲染**该标签，
> 由 `library/experience.md` 的「翻译规则」改写为「可以接一个外部工具，需要你先允许调用」。
'''


def patch_output_spec():
    anchor = u'- ❌ `[已降级: campus-search → org-lookup]` ✗（含 skill 名）\n'
    collapse_dup('library/output-spec.md', PTR_OUTPUT_SPEC, 'A1 指针 §1.4')
    sub_once('library/output-spec.md', anchor, anchor + u'\n' + PTR_OUTPUT_SPEC, 'A1 指针 §1.4')

    anchor2 = u'> 渲染器会把中文一并算进链接地址，点开即 404。以下三条**必须遵守**：\n'
    collapse_dup('library/output-spec.md', PTR_LINK, 'A1 指针 链接呈现规范')
    sub_once('library/output-spec.md', anchor2, anchor2 + u'\n' + PTR_LINK, 'A1 指针 链接呈现规范')


# ─────────────────────────────────────────────────────────────────────────────
# 3. 计数与清单同步
# ─────────────────────────────────────────────────────────────────────────────
def patch_counts():
    # selfcheck.sh REQ 清单
    sub_once('scripts/selfcheck.sh',
             u'library/skill-evolution.md\ndomains/_registry.md\n',
             u'library/skill-evolution.md library/experience.md\ndomains/_registry.md\n',
             'A1 REQ 清单')

    # selfcheck.sh library 文件数期望
    sub_once('scripts/selfcheck.sh',
             u'[ "${libn:-0}" -eq 11 ] && ok "library 文件数 = 11" || warn "library 文件数 = $libn（期望 11）"',
             u'[ "${libn:-0}" -eq 12 ] && ok "library 文件数 = 12" || warn "library 文件数 = $libn（期望 12）"',
             'A1 期望数 11→12')

    # regress.sh library 文件数
    sub_once('scripts/regress.sh',
             u'_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 11',
             u'_chk "library 文件数" "$(ls -1 library/*.md | wc -l | tr -d \' \')" 12',
             'A1 期望数 11→12')

    # INSTALL.md §五
    sub_once('INSTALL.md', u'**11 个** library 文件', u'**12 个** library 文件', 'A1 计数 11→12')

    # README.md 交付树计数（aligncheck 硬断言：声明值必须 == 交付集实测）
    sub_once('README.md', u'**`release` 分支 = 纯净交付树**（176 个文件）',
             u'**`release` 分支 = 纯净交付树**（177 个文件）', 'A1 交付树计数 176→177')

    # qihang.sh status [1级] 清单（aligncheck 硬断言：不得漏列）
    sub_once('scripts/qihang.sh',
             u'library/general-fallback.md; do',
             u'library/general-fallback.md library/experience.md; do',
             'A1 status 清单')

    # library/README.md 导航（bullet 列表）
    anchor = (u'- `external-bridge.md` —— **外部桥接**：库内与同域降级都接不住时的桥接档'
              u'（当前平台目录列出 20 个入口 + 五步自检 + 许可门禁 + 未命中回落）\n')
    sub_once('library/README.md', anchor,
             anchor + u'- `experience.md` —— **学生呈现层**：前台白名单 / 前台禁止物 / '
                      u'翻译规则 / 三视图 / 反例 / 起始句型唯一副本\n',
             'A1 导航')
    collapse_dup('library/README.md',
                 u'- `experience.md` —— **学生呈现层**：前台白名单 / 前台禁止物 / '
                 u'翻译规则 / 三视图 / 反例 / 起始句型唯一副本\n', 'A1 导航')

    # README.md 结构树
    sub_once('README.md',
             u'│   └── general-fallback.md   职责4：通用兜底框架（零 skill 命中也出结果）\n',
             u'│   ├── general-fallback.md   职责4：通用兜底框架（零 skill 命中也出结果）\n'
             u'│   └── experience.md         学生呈现层（前台白名单 / 禁止物 / 翻译规则 / 起始句型唯一副本）\n',
             'A1 结构树')

    # SKILL.md 规则文件表（6 → 7）
    sub_once('SKILL.md', u'## 六份规则文件（1 级库的本体）\n',
             u'## 七份规则文件（1 级库的本体）\n', 'A1 规则文件表标题')
    sub_once('SKILL.md',
             u'| `library/skill-evolution.md` | 习惯自迭代：**只改可改段**（执行步骤 / 判定细则 / 示例说明），'
             u'不改红线 / 输出契约 / 任何事实 |\n',
             u'| `library/skill-evolution.md` | 习惯自迭代：**只改可改段**（执行步骤 / 判定细则 / 示例说明），'
             u'不改红线 / 输出契约 / 任何事实 |\n'
             u'| `library/experience.md` | 学生呈现层：前台白名单 / 禁止物 / 翻译规则 / 三视图 / 起始句型唯一副本 |\n',
             'A1 规则文件表行')
    collapse_dup('SKILL.md',
                 u'| `library/experience.md` | 学生呈现层：前台白名单 / 禁止物 / 翻译规则 / 三视图 / 起始句型唯一副本 |\n',
                 'A1 规则文件表行')


# ─────────────────────────────────────────────────────────────────────────────
# 4. A2 安装后三行首次引导
# ─────────────────────────────────────────────────────────────────────────────
SKILL_INSTALL_BLOCK = u'''## 安装后行为

**安装后输出**：安装完成后回复一句「安装完成」，并附**三行首次使用引导**；其余一律不展示。

首次使用引导固定三行：

1. **能做什么**：理解题目、整理课堂笔记、拆作业与检查点、备考计划、查学校与课程信息、查学术资料。
2. **怎么开口**：直接用自然语言说需求即可，不必先选分类；不确定就照第 3 行的样子说。
3. **一句话示例**：「帮我理解这道题」／「安排一周备考计划」。

| 不做 | 说明 |
|---|---|
| 不报审计结果 | 安全审计 / 合规检查的结论不呈现给用户 |
| 不输出报告 | 不生成、不附带任何校验报告、清单或附件 |
| 不罗列计数 | 不展示结构自检的逐项标记与域 / skill 数量 |

- `scripts/` 下的 `selfcheck.sh` / `audit.sh` / `regress.sh` / `aligncheck.py` / `runcheck.py` 属**内部静默自检**：可运行，但仅**失败**时报错，成功不输出。
- 仅当用户**主动索要**时，才展示上述细节。

'''

INSTALL_NOTE = (u'> **安装后行为（强制）**：安装完成后回复一句「安装完成」，并附**三行首次使用引导**'
                u'（能做什么 / 怎么开口 / 一句话示例）；不展示审计结果、不输出校验报告、不罗列结构计数。'
                u'详见 `SKILL.md`「安装后行为」与本文 §七。')

INSTALL_SEC7 = u'''## 七、安装后行为约定（强制）

1. **一句确认 + 三行引导**：安装完成后回复「安装完成」，并附三行首次使用引导 —— ①能做什么 ②怎么开口 ③一句话示例。不展示安全审计 / 合规检查结论、不输出任何报告或清单、不罗列结构计数。
2. **静默自检**：§五 的校验脚本属**内部自检**，可运行，但**成功时不输出任何内容**，仅在失败时报错。
3. **按需说明**：不主动输出内部自检结果；用户明确索要时可说明已执行的检查及结果。
'''

README_ONBOARD = (u'\n**装完怎么开始**：在宿主里直接说需求即可，不必先选分类或模式。\n\n- '
                  + ONBOARD_1 + u'\n- ' + ONBOARD_2 + u'\n- ' + ONBOARD_3 + u'\n')


def patch_install_behavior():
    sub_re('SKILL.md', u'^## 安装后行为\\n.*?(?=^## 触发门)', SKILL_INSTALL_BLOCK, 'A2 SKILL.md')

    t = read('INSTALL.md')
    m = re.search(u'^> \\*\\*安装后行为（强制）\\*\\*：.*$', t, re.M)
    if not m:
        raise SystemExit('[step69] INSTALL.md 未找到安装后行为提示行')
    if m.group(0).strip() != INSTALL_NOTE:
        write('INSTALL.md', t[:m.start()] + INSTALL_NOTE + t[m.end():])
        CHANGED.append('INSTALL.md (A2 §一 提示)')
    else:
        SKIPPED.append('INSTALL.md (A2 §一 提示)')

    sub_re('INSTALL.md', u'^## 七、安装后行为约定（强制）\\n.*?(?=^## |\\Z)', INSTALL_SEC7, 'A2 §七')

    anchor = u'> 开发树（含生成器链与过程文档）在 [`main` 分支](https://github.com/xiaojun10086/qihang-pack )。\n'
    sub_once('README.md', anchor, anchor + README_ONBOARD, 'A2 README §0')
    collapse_dup('README.md', README_ONBOARD, 'A2 README §0')

    # 断言同步：selfcheck [8c] 与 regress [10]
    sub_once('scripts/selfcheck.sh',
             u'''if grep -qF '只回复一句「安装完成」' SKILL.md 2>/dev/null; then
  ok "SKILL.md 保留安装后简短确认约定"
else
  bad "SKILL.md 缺少安装后行为约定"
fi''',
             u'''if grep -qF '安装完成后回复一句「安装完成」' SKILL.md 2>/dev/null \\
   && grep -qF '首次使用引导' SKILL.md 2>/dev/null; then
  ok "SKILL.md 保留安装后简短确认 + 首次使用引导"
else
  bad "SKILL.md 缺少安装后行为约定（应含确认句与首次使用引导）"
fi''',
             'A2 selfcheck 断言')

    sub_once('scripts/regress.sh',
             u'''  grep -qF '只回复一句「安装完成」' SKILL.md \\
    && _ok "SKILL.md 保留安装后简短确认约定" || _fail "SKILL.md 缺少安装后行为约定"''',
             u'''  grep -qF '安装完成后回复一句「安装完成」' SKILL.md \\
    && grep -qF '首次使用引导' SKILL.md \\
    && _ok "SKILL.md 保留安装后简短确认 + 首次使用引导" || _fail "SKILL.md 缺少安装后行为约定"''',
             'A2 regress 断言')


# ─────────────────────────────────────────────────────────────────────────────
# 5. B1 入口文案收口
# ─────────────────────────────────────────────────────────────────────────────
def patch_entries():
    bullets = u'\n'.join(u'- 「%s」' % e for e in ENTRIES) + u'\n'

    # README.md §2.1
    sub_once('README.md',
             u'''**可直接使用的起始句型**：

- 「帮我理解这道题，告诉我关键思路」
- 「这节课我听不懂，帮我整理重点和笔记」
- 「我有作业，先拆任务，再给我检查点」
- 「给我做一个一周备考计划」
- 「查一下大工公开通知/课程安排，给出处和核验状态」
''',
             u'**可直接使用的起始句型**（唯一副本：`library/experience.md`）：\n\n' + bullets,
             'B1 README §2.1')

    # commands/qihang.md
    sub_once('commands/qihang.md',
             u'''- 「帮我理解这道题」
- 「整理这节课的重点和笔记」
- 「我有作业，先拆任务，再给检查点」
- 「制定一周备考计划」
- 「查一下学校/课程信息，给出处和核验状态」
''',
             bullets,
             'B1 commands/qihang.md')

    # SKILL.md：声明唯一副本（清单本身已是规范口径）
    sub_once('SKILL.md', u'**统一快速入口**：\n',
             u'**统一快速入口**（唯一副本：`library/experience.md`）：\n',
             'B1 SKILL.md 唯一副本声明')

    # scripts/qihang.sh cmd_quick
    sub_once('scripts/qihang.sh',
             u'''  echo "直接输入任一问题即可："
  echo "  1. 帮我理解这道题"
  echo "  2. 整理这节课的笔记"
  echo "  3. 查一下学校通知 / 课程安排"
  echo "  4. 制定一周备考计划"
  echo "  5. 帮我检查作业步骤和风险点"
  echo "  6. 让我看论文/文献/来源"
  echo ""
  echo "在 LearnBuddy 中，直接输入下面的自然语言需求即可；无需先选域。"
  echo "只在关键信息会改变回答时追问；复杂任务按需分轮确认，不为填表而追问。"
  echo "交付可按目标采用学习辅导、事实检索或行动规划；需要时可要求更简洁、更详细或核对来源。"
  echo "此菜单只展示文本示例，不启动对话；会话外记忆仅按用户明确要求处理。"
  echo "----------------------------------------"
  echo "常用起始句型："
  echo "  1) 帮我理解 X 的核心概念和解题思路"
  echo "  2) 我有一份作业，先拆任务再给我检查点"
  echo "  3) 这门课我从零开始，给我一个学习节奏"
  echo "  4) 查一下大工相关的公开信息，给出处和核验状态"
  echo "  5) 我需要论文/参考文献，先给检索思路和可信来源"
''',
             u'''  echo "直接输入任一问题即可（不必先选分类）："
''' + u'\n'.join(u'  echo "  %d. 「%s」"' % (i + 1, e) for i, e in enumerate(ENTRIES)) + u'''
  echo ""
  echo "以上六条与本包入口文案逐条一致（唯一副本：library/experience.md 的起始句型清单）。"
  echo "在 LearnBuddy 中直接输入自然语言需求即可；无需先选域。"
  echo "只在关键信息会改变回答时追问；复杂任务按需分轮确认，不为填表而追问。"
  echo "交付可按目标采用学习辅导、事实检索或行动规划；需要时可要求更简洁、更详细或核对来源。"
  echo "此菜单只展示文本示例，不启动对话；会话外记忆仅按用户明确要求处理。"
''',
             'B1 qihang.sh cmd_quick')


# ─────────────────────────────────────────────────────────────────────────────
# 6. aligncheck X 组断言
# ─────────────────────────────────────────────────────────────────────────────
X_GROUP = u'''    # ---------- X 学生呈现层（体验层）----------
    # 防复发：92 个库内 skill 的输出块同时承担契约与渲染两职，前台白名单 / 禁止物 / 翻译规则
    # 无唯一副本、无断言 —— 体验层曾是全包唯一的「零断言层」。X 组把它钉住。
    XPATH = 'library/experience.md'
    if not os.path.exists(XPATH):
        bad('README.md', '缺少学生呈现层规则 %s（前台白名单 / 禁止物 / 翻译规则无唯一副本）' % XPATH)
    else:
        _xt = rd(XPATH)
        _xsec = (('白名单', r'^##\\s*1[.、]?\\s*前台白名单'),
                 ('禁止物', r'^##\\s*2[.、]?\\s*前台禁止物'),
                 ('翻译规则', r'^##\\s*3[.、]?\\s*翻译规则'),
                 ('三视图', r'^##\\s*4[.、]?\\s*三视图'),
                 ('反例', r'^##\\s*5[.、]?\\s*反例'),
                 ('起始句型', r'^##\\s*6[.、]?\\s*起始句型'))
        for _xk, _xpat in _xsec:
            if not re.search(_xpat, _xt, re.M):
                bad(XPATH, '缺小节「%s」（体验层六要素之一）' % _xk)
        if not _xt.startswith('#'):
            bad(XPATH, '首行不是标题（1 级规则文件不应含 frontmatter）')

        # 1 级清单三处必须同步（status 清单用全路径，库导航与规则文件表用文件名）
        if XPATH not in rd('scripts/qihang.sh'):
            bad('scripts/qihang.sh', 'cmd_status 的 [1级] 清单漏列 %s' % XPATH)
        _xname = os.path.basename(XPATH)
        if _xname not in rd('library/README.md'):
            bad('library/README.md', '1 级库导航漏列 %s' % XPATH)
        if _xname not in rd('SKILL.md'):
            bad('SKILL.md', '1 级规则文件表漏列 %s' % XPATH)

        # 输出契约两处指针必须指向唯一副本（渲染层规则可被 92 个 skill 顺链读到）
        _xops = rd('library/output-spec.md')
        if _xops.count(XPATH) != 2:
            bad('library/output-spec.md',
                '前台渲染口径指针应为 2 处（§1.4 降级标注 + 链接呈现规范外接标注），实测 %d'
                % _xops.count(XPATH))

        # 入口文案唯一副本：四处呈现位必须逐条含全部起始句型
        _xm = re.search(r'^##\\s*6[.、]?\\s*起始句型[^\\n]*\\n(.*?)(?=^##\\s|\\Z)', _xt, re.M | re.S)
        _xcanon = list(dict.fromkeys(re.findall(r'「([^」\\n]+)」', _xm.group(1)))) if _xm else []
        if len(_xcanon) < 5:
            bad(XPATH, '起始句型清单少于 5 条（实测 %d，唯一副本失效）' % len(_xcanon))
        for _xf, _xlbl in (('README.md', 'README §2.1'),
                           ('SKILL.md', 'SKILL.md 统一快速入口'),
                           ('commands/qihang.md', '入口卡'),
                           ('scripts/qihang.sh', 'qihang.sh cmd_quick')):
            _xft = rd(_xf)
            _xmiss = [c for c in _xcanon if ('「%s」' % c) not in _xft]
            if _xmiss:
                bad(_xf, '%s 的起始句型与唯一副本不一致（缺 %s）' % (_xlbl, ' / '.join(_xmiss)))

        # 组数声明同源（防止新增组后文档计数漂移）
        _xngroups = 20
        if ('%d 组断言' % _xngroups) not in rd('README.md') or \\
           ('%d 组断言' % _xngroups) not in rd('INSTALL.md'):
            warn('README.md', 'aligncheck 组数声明与实现不一致（期望「%d 组断言」）' % _xngroups)

'''


def patch_aligncheck():
    sub_once('scripts/aligncheck.py',
             u'检查项（19 组：A–D、F–Q、S–U）：',
             u'检查项（20 组：A–D、F–Q、S–U、X）：',
             'A1 组数声明')

    t = read('scripts/aligncheck.py')
    if u'  X 学生呈现层：' not in t:
        m = re.search(u'^  U 触发门越界表不变式：.*?^    「需求主键」「优先级最高」双处声明\\n', t, re.M | re.S)
        if not m:
            raise SystemExit('[step69] aligncheck 文档字符串 U 组结尾未命中')
        ins = (u'  X 学生呈现层：`library/experience.md` 在位（白名单 / 禁止物 / 翻译规则 / 三视图 / 反例 / 起始句型）·\\n'
               u'    1 级清单三处同步 · 输出契约两处指针在位 · 四处入口文案与唯一副本逐条一致 · 组数声明同源\\n')
        write('scripts/aligncheck.py', t[:m.end()] + ins + t[m.end():])
        CHANGED.append('scripts/aligncheck.py (文档字符串 X 组)')
    else:
        SKIPPED.append('scripts/aligncheck.py (文档字符串 X 组)')

    sub_once('scripts/aligncheck.py',
             u'    # ---------- 汇总 ----------',
             X_GROUP + u'    # ---------- 汇总 ----------',
             'A1 X 组')
    collapse_dup('scripts/aligncheck.py', X_GROUP, 'A1 X 组')

    sub_once('README.md', u'全量文件级对齐审计（18 组断言）',
             u'全量文件级对齐审计（20 组断言）', 'A1 组数声明 README')
    sub_once('INSTALL.md', u'**全量文件级对齐**（18 组断言）',
             u'**全量文件级对齐**（20 组断言）', 'A1 组数声明 INSTALL')


# ─────────────────────────────────────────────────────────────────────────────
# 7. negative_test 注入用例
# ─────────────────────────────────────────────────────────────────────────────
INJECTORS = u'''def inject_experience_pointer_removed(tree):
    """删掉 output-spec.md 的一处前台渲染口径指针 → aligncheck X 组应 FAIL。"""
    p = os.path.join(tree, 'library', 'output-spec.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('`library/experience.md`', '`experience.md`', 1)


def inject_entry_phrase_drift(tree):
    """改掉 README.md 的一个起始句型（与唯一副本分叉）→ aligncheck X 组应 FAIL。"""
    p = os.path.join(tree, 'README.md')
    t = io.open(p, encoding='utf-8').read()
    return [p], t.replace('「安排一周备考计划」', '「给我排一个复习节奏」', 1)'''

NEW_CASES = u'''        ('前台渲染口径指针被删（契约层不再顺链到呈现层）', inject_experience_pointer_removed,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck X 呈现层指针'),
        ('入口文案分叉（README 起始句型与唯一副本不一致）', inject_entry_phrase_drift,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck X 起始句型唯一副本'),
'''


def patch_negative_test():
    if u'def inject_entry_phrase_drift' in read('scripts/negative_test.py'):
        SKIPPED.append('scripts/negative_test.py (X 组注入)')
        return

    sub_once('scripts/negative_test.py', u'\n\ndef main():\n',
             u'\n\n' + INJECTORS + u'\n\n\ndef main():\n',
             '注入函数')

    sub_once('scripts/negative_test.py',
             u'''        ('SKILL.md §1.5 越界词与 config 不同步', inject_oos_skill_md_skew,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck U 越界表同步'),
    ]''',
             u'''        ('SKILL.md §1.5 越界词与 config 不同步', inject_oos_skill_md_skew,
         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck U 越界表同步'),
''' + NEW_CASES + u'    ]',
             '用例登记')


# ─────────────────────────────────────────────────────────────────────────────
# 8. 生成链登记（rebuild LAYERS + _build 变更日志）
# ─────────────────────────────────────────────────────────────────────────────
def patch_build_registry():
    anchor = (u"    ('step68_remove_identity.py',    '**移除强制自我身份声明**：删除配置、文档和安装说明中的人格/改称锁定；"
              u"将自检改为防回归断言；修订号 3.3.8→3.3.9'),\n")
    new = (u"    ('step69_experience_layer.py',   '**学生呈现层收口（零行为变更）**：新增 1 级规则 `library/experience.md`"
           u"（前台白名单 / 禁止物 / 翻译规则 / 三视图 / 起始句型唯一副本）· 输出契约两处指针 · 安装后三行首次引导 · "
           u"四处入口文案收口 · aligncheck X 组 + 2 类负向注入'),\n")
    collapse_dup('scripts/_build/v3/rebuild.py', new, '生成链登记 LAYERS')
    sub_once('scripts/_build/v3/rebuild.py', anchor, anchor + new, '生成链登记 LAYERS')

    anchor2 = (u'| 27 | `step68_remove_identity.py` | **移除强制自我身份声明**：删除身份配置及人格/改称锁定规则；'
               u'自检改为确认其不再出现；保留安装后的简短确认行为；修订号 → `3.3.9` | 新增层 |\n')
    row = (u'| 28 | `step69_experience_layer.py` | **学生呈现层收口（零行为变更）**：新增 1 级规则 '
           u'`library/experience.md`（前台白名单 / 禁止物 / 翻译规则 / 三视图 / 起始句型唯一副本）· '
           u'`output-spec.md` 两处前台渲染口径指针 · 安装后三行首次使用引导（`SKILL.md` / `INSTALL.md` / `README.md`）· '
           u'`library` 文件数 11 → 12 · 四处入口文案收口 · `aligncheck` X 组 + 2 类负向注入 | 新增层 |\n')
    collapse_dup('scripts/_build/v3/README.md', row, '变更日志')
    sub_once('scripts/_build/v3/README.md', anchor2, anchor2 + row, '变更日志')


def main():
    print('step69 —— 学生呈现层（体验层）收口')
    write_if_changed('library/experience.md', EXPERIENCE_MD)
    patch_output_spec()
    patch_counts()
    patch_install_behavior()
    patch_entries()
    patch_aligncheck()
    patch_negative_test()
    patch_build_registry()

    print('\n改动 %d 处：' % len(CHANGED))
    for c in CHANGED:
        print('  ~ %s' % c)
    if SKIPPED:
        print('\n幂等跳过 %d 处：' % len(SKIPPED))
        for c in SKIPPED:
            print('  = %s' % c)


if __name__ == '__main__':
    main()
