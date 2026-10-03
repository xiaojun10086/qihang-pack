# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 28 层 · 触发门收紧 + 锁定与降级强制（v3.3.3 → v3.3.4）】
#
# 用户指令：修改 skill 触发机制 ——
#   ① **只有**「明确涉及大连理工」或「知识学习」或「对方自述为大连理工大学学生」才触发；
#   ② 触发后**必须走三级结构**；
#   ③ 优化 skill **锁定**与**降级**机制：**外源 skill 检索不成功才能自行生成**；
#   ④ **确保这个流程成立**（= 要有可判定判据 + 断言 + 负向注入 + 亲测）。
#
# 自检（改前现状）：
#   ❌ C1 **触发是软描述**：只写在 frontmatter `description` 一句话里，**无可判定门槛**，
#        也没写「不触发时怎么办」→ 模型很容易对任何问题都套三级结构（或反过来漏触发）。
#   ❌ C2 **「触发即锁定」没有强制句**：工作流虽写"严格按序不可跳步"，但没有「触发门」这一前置判定，
#        也没断言保证它不会被删。
#   ❌ C3 **降级顺序未强制**：三档已存在（同域库内 → 外部桥接 → 纯提示词），
#        但**没有一条明文**规定「未穷尽档 1、未尝试档 2，不得进入档 3 自行生成」。
#   ❌ C4（侦察时顺带发现）`commands/qihang.md` 有**两个「6.」**（身份锁定 / 外部桥接），
#        且外部桥接那行仍写「检索 **12 平台**」（v3.3.1 起已改为「按域指定 2–3 个平台」）。
#
# 本层修法：config.yaml 立 `trigger` 段为**单一真相源**；SKILL.md 增「触发门与接管边界」；
#          三处规则文件补「档序强制」；入口卡补第 0 步并修编号；selfcheck `[8d]` + 负向注入第 11 类。
#
# 用法：python scripts/_build/v3/step65_trigger_gate.py [仓库根]
# -------------------------------------------------------------------------------
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.3', '3.3.4'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='\n').write(t)


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
            print('  [SAME] %s :: %r' % (rel, sent[:44]))
            continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:44]))
            continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:44]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


# =============================================================== A) config.yaml 触发门真相源
print('== A) config.yaml 立 trigger 段（触发门 + 降级顺序的唯一真相源）==')
TRIG = '''# ============ 触发门（强制 · **单一真相源**） ============
# 只有在下列**任一**成立时才「接管」——即走三级结构与本包的输出契约；
# 否则**不接管**：按普通助手直接回答，不套模板、不写档案、不标 [已降级]。
# 由 scripts/selfcheck.sh [8d] 断言本段字段齐全，且 SKILL.md 的触发门与之一致。
trigger:
  when_any:
    - 明确涉及大连理工大学          # 校名/简称/校区/校内系统/校内对象（见 dlut_markers）
    - 知识学习活动                  # 学习/备考/笔记/作业/科研/写作/语言/文献/实验（见 learning_markers）
    - 对方自述为大连理工大学学生     # "我是大工的学生""我们学校…"等自述
  dlut_markers: [大连理工, 大工, DUT, dlut, 凌水, 开发区校区, 盘锦校区, i大工, 本校, 校内, 教务处, 一卡通, 辅导员, 培养方案]
  learning_markers: [学习, 复习, 备考, 笔记, 作业, 课程, 考试, 论文, 文献, 实验, 报告, 科研, 写作, 英语, 雅思, 保研, 考研, 求职, 竞赛]
  # ⚠️ **学习意图**表述（真机演练补的洞）：只列名词会漏掉「我想学 X / 自学 / 入门 / 教我」这类最常见的说法
  #    —— 演练实测「我最近想学 Python，从哪儿开始」被判「不接管」，与「知识学习」口径不符。
  #    注意**不要**把裸词「学」放进来：它会被「同学 / 学校 / 学期」误命中。
  learning_intents: [想学, 自学, 怎么学, 如何学, 入门, 学会, 学不会, 教我, 讲解一下, 帮我理解, 搞懂, 弄懂, 刷题, 做题, 背单词, 补习, 教程]
  not_triggered_behavior: 不接管      # 直接按普通助手回答：不套输出模板 / 不写学习档案 / 不标 [已降级] / 不做域审查
  lock_after_trigger: true           # 触发即锁定：必须走工作流 ①→⑧，不可跳步、不可绕过域审查直接作答
  ladder: [同域库内 skill, 外部桥接, 自生成]   # 降级顺序（1→2→3）；**前一档未穷尽不得进入下一档**
  self_generate_requires: 档 2 已尝试且未命中（或因红线域/离线被明确跳过并在输出中说明）
  skip_ladder_when_redline_or_offline: true    # 红线域（F3/F5）与离线：可跳档 2，但**必须明说**再进档 3

'''
edit('config.yaml', [
    ('# ============ 学校绑定（强绑定） ============',
     TRIG + '# ============ 学校绑定（强绑定） ============',
     '触发门（强制 · **单一真相源**）'),
])

# =============================================================== B) SKILL.md 触发门
print('== B) SKILL.md 增「触发门与接管边界」+ 收紧 frontmatter + 硬规则 1 ==')
GATE = '''## 触发门与接管边界（**先判这里，再谈别的**）

> **本节是硬前置**：不先过触发门，后面 8 步一律不启动。口径真相源 = `config.yaml` 的 `trigger` 段。

### 1. 什么时候**才**接管（三条，**任一**成立即接管）

| # | 条件 | 判据（`config.yaml` 的 markers） |
|---|---|---|
| **T1** | **明确涉及大连理工大学** | 出现校名 / 简称 / 校区 / 校内系统 / 校内对象：大连理工、大工、DUT、凌水、开发区校区、盘锦校区、i大工、本校、一处（教务处 / 一卡通 / 辅导员 / 培养方案）… |
| **T2** | **知识学习活动**（**不要求**与 DUT 相关） | ① 学习类**名词**：学习、复习、备考、笔记、作业、课程、考试、论文、文献、实验、报告、科研、写作、英语、雅思、保研、考研、求职、竞赛；<br>② **学习意图**表述：**想学**、自学、怎么学、入门、教我、讲解一下、帮我理解、搞懂、刷题、背单词…（`trigger.learning_intents`） |
| **T3** | **对方自述为大连理工大学学生** | 「我是大工的学生 / 我们学校 / 我也是凌水的 / 我 2026 级」等**自述**（此后本轮会话默认按 DUT 语境处理） |

### 2. 不触发时**不接管**（硬）

三条都不成立时（例：「帮我写个 Python 冒泡排序」「推荐几部电影」「北京天气怎么样」）：

- ✅ **按普通助手直接回答** —— 正常、完整、有用的回答；
- ❌ **不套** `library/output-spec.md` 的输出模板（不强制【结论】【依据】【下一步】那套）；
- ❌ **不写**学习档案（`library/memory.md`）、**不做**域审查与降级标注（不出现 `[已降级]` / `[外接]`）；
- ❌ **不为了"触发"硬套**：不得把无关问题硬塞进某个域。

> **边界情况**：T2「知识学习活动」很宽 —— 凡属"学东西"的求助都算（含非 DUT 的自学、考研、语言）。
> **但它不覆盖**：闲聊、时政、纯工具性编程问题（与学习无关的）、娱乐与消费推荐。

### 3. 触发后**必须走三级结构**（锁定）

一旦 T1/T2/T3 任一成立 → **锁定**，进入「## 工作流（严格按序，不可跳步）」：

- **不可跳步**：①需求明确 → ②锁定域 → ③域审查 → ④锁定 skill → ⑤执行 → ⑥输出 → ⑦归档 → ⑧自迭代；
- **不可绕过域审查直接作答**（③ 的「有无对口 skill」校验是必经步骤）；
- **不可用"通用常识"替代** 库内 skill / 外部桥接的检索结论。

### 4. 降级顺序（**四级**，`config.yaml` 的 `trigger.ladder`）

```
档 1 · 同域库内 skill      ← 默认，先穷尽本域全部库内 skill
      ↓ 接不住
档 2 · 外部桥接             ← 按 library/external-bridge.md 检索外源 skill（按域指定 2–3 个平台）
      ↓ 未命中
档 3 · **自生成**           ← 纯提示词模式 / 域通用框架 / 六步通用框架（= 自己写）
```

> ⚠️ **硬约束**：**未穷尽档 1、未尝试档 2，不得进入档 3 自行生成。**
> 例外只有两种，且**必须在输出里明说原因**：① 红线域（`F3`/`F5`）**禁外接**；
> ② 环境离线 / 用户禁止联网（探测失败）。除这两种，**"懒得找"不构成跳档理由**。

'''
edit('SKILL.md', [
    ('## 工作流（严格按序，不可跳步）', GATE + '## 工作流（严格按序，不可跳步）',
     '## 触发门与接管边界'),
    ('description: 「启航」大连理工大学新生学习生活一体化学伴包（三级结构）。入口 skill，负责需求明确、域审查、输出规范与路由。当用户提出与大连理工大学校情、课程学习、备考、笔记、作业、科研、校园生活相关的模糊求助时使用。',
     'description: 「启航」大连理工大学新生学习生活一体化学伴包（三级结构）。入口 skill，负责需求明确、域审查、输出规范与路由。'
     '**仅当**①明确涉及大连理工大学（校名/简称/校区/校内系统/校内对象）、'
     '②属于知识学习活动（学习/备考/笔记/作业/科研/写作/语言/文献/实验等，不要求与 DUT 相关）、'
     '或③对方自述为大连理工大学学生时**才接管**；触发后**必须**走三级结构（工作流不可跳步），'
     '降级顺序为 **同域库内 skill → 外部桥接 → 自生成**，**未走完前两档不得自行生成**。'
     '三条都不成立时按普通助手直接回答，不套本包输出模板。',
     '**仅当**①明确涉及大连理工大学'),
    ('1. **库内优先**：日常场景由库内 skill 承接，**不安装任何外部 skill**；库内与同域降级都接不住时走**外部桥接**（可选，`library/external-bridge.md`）；外部未命中则回落**纯提示词模式**并记「缺口」。',
     '1. **库内优先 + 档序强制**：日常场景由库内 skill 承接，**不安装任何外部 skill**；'
     '库内与同域降级都接不住时走**外部桥接**（可选，`library/external-bridge.md`）；'
     '**外部检索未命中**才回落**自生成**（纯提示词模式）并记「缺口」。\n'
     '   - **档序不可颠倒**：同域库内 → 外部桥接 → 自生成。**未穷尽档 1、未尝试档 2，不得自行生成**；'
     '唯一的例外是红线域（`F3`/`F5` 禁外接）与环境离线，且**必须在输出里说明原因**。',
     '**库内优先 + 档序强制**'),
])

# =============================================================== C) 三处规则文件补「档序强制」
print('== C) 规则文件补「档序强制」==')
edit('library/domain-review.md', [
    ('   ❌ **禁止**：跳过本条直接下发 ④ —— 「需求规模超出 skill 定位」也属无对口 skill，同样走降级',
     '   ❌ **禁止**：跳过本条直接下发 ④ —— 「需求规模超出 skill 定位」也属无对口 skill，同样走降级\n'
     '   ❌ **禁止**：跳过 ③ 的降级分支**自行生成答案** —— **档序强制**：同域库内 skill → 外部桥接 → 自生成，\n'
     '        **前一档未穷尽不得进入下一档**；只有在档 2 也未命中（或红线域 / 离线被明确跳过并说明）时，才允许自生成。',
     '档序强制**：同域库内 skill → 外部桥接 → 自生成'),
    ('3. **降级为通用问答**：明确告知「本包暂无该方向的域」，**按 `library/general-fallback.md` §2 六步通用框架**给出结构完整、可执行、标注了不确定性的答复，并在学习档案记录该缺口',
     '3. **降级为通用问答**：明确告知「本包暂无该方向的域」，**按 `library/general-fallback.md` §2 六步通用框架**给出结构完整、可执行、标注了不确定性的答复，并在学习档案记录该缺口\n'
     '   > **档序前提**：进入本条 = **自生成**（档 3）→ 前置必须是「**档 1 已穷尽 + 档 2 已尝试未命中**」，\n'
     '   > 或「红线域（`F3`/`F5`）/ 离线」被明确跳过**且在输出里写明原因**。跳过前置即违规。',
     '档序前提**：进入本条 = **自生成**'),
])
edit('library/general-fallback.md', [
    ('> 本框架是**三档降级链**的收尾：档 1「同域库内 skill」→ 档 2「外部桥接」（`library/external-bridge.md`）→ **档 3「本框架」**。',
     '> 本框架是**三档降级链**的收尾：档 1「同域库内 skill」→ 档 2「外部桥接」（`library/external-bridge.md`）→ **档 3「本框架」（= 自生成）**。\n'
     '>\n'
     '> ⚠️ **档序强制**：本框架是**最后一档**。**未穷尽档 1、未尝试档 2，不得直接跳到本框架自行生成**。\n'
     '> 例外只有两种，且**必须在输出里说明原因**：① 红线域（`F3`/`F5`）禁外接；② 环境离线 / 用户禁止联网。',
     '**档序强制**：本框架是**最后一档**'),
])
edit('library/external-bridge.md', [
    ('| **档 3 · 纯提示词** | 档 2 未找到合格外部 skill | **原有流程**：纯提示词模式，尽力作答并标 `[已降级]` | `[已降级]` |',
     '| **档 3 · 自生成** | 档 2 未找到合格外部 skill | **原有流程**：纯提示词模式，尽力作答并标 `[已降级]` | `[已降级]` |',
     '**档 3 · 自生成**'),
    ('**这是三档，不是两档**：档 3 永远保留。**任何档都不允许"只回一句拒绝"。**',
     '**这是三档，不是两档**：档 3 永远保留。**任何档都不允许"只回一句拒绝"。**\n'
     '\n'
     '> ⚠️ **档序强制（v3.3.4）**：档 3 = **自生成**，是**最后一档**。\n'
     '> **未穷尽档 1、未尝试档 2，不得进入档 3 自行生成** —— 换句话说：\n'
     '> **只有外源 skill 检索不成功，才允许自行生成**。\n'
     '> 例外只有两种且必须明说：① 红线域（`F3`/`F5`）禁外接；② 环境离线 / 用户禁止联网。',
     '**档序强制（v3.3.4）**'),
])

# =============================================================== D) 入口卡：补第 0 步 + 修编号/口径
print('== D) commands/qihang.md 补触发门 + 修重复编号与过期口径 ==')
edit('commands/qihang.md', [
    ('1. **需求明确**：读 `library/clarity.md`，拆 6 槽位，算 `U = 1 − Σ(wᵢcᵢ)/Σwᵢ`。',
     '0. **触发门（先判这个）**：只有 ① 明确涉及大连理工大学、② 属于知识学习活动（不要求与 DUT 相关）、\n'
     '   ③ 对方自述为大连理工大学学生，**任一成立才接管**；否则**不接管** —— 按普通助手直接回答，\n'
     '   不套输出模板、不写学习档案、不标 `[已降级]`。判据见 `config.yaml` 的 `trigger` 段。\n'
     '   触发后即**锁定**：必须走完下面 ①→⑧，不可跳步。\n'
     '1. **需求明确**：读 `library/clarity.md`，拆 6 槽位，算 `U = 1 − Σ(wᵢcᵢ)/Σwᵢ`。',
     '0. **触发门（先判这个）**'),
    ('6. **外部桥接（最后的兜底）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**（原有流程）。',
     '7. **外部桥接（倒数第二档）**：库内 skill 与同域降级都接不住时，读 `library/external-bridge.md` → '
     '按该域**指定的 2–3 个平台**（`references/external-sources.md`）检索 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；\n'
     '   **未命中才允许进第 8 步自行生成**（档序：同域库内 → 外部桥接 → 自生成，不可颠倒；'
     '红线域 `F3`/`F5` 或离线可跳档但须说明）。\n'
     '8. **自生成（最后一档）**：外源检索未命中时，按 `library/general-fallback.md` 六步通用框架尽力作答并标 `[已降级]`。',
     '7. **外部桥接（倒数第二档）**'),
])

# =============================================================== E) selfcheck [8d]
print('== E) selfcheck.sh 新增 [8d] 触发门与降级顺序 ==')
S8D = '''# ---------- 8d. 触发门与降级顺序（v3.3.4） ----------
# 为什么单列：触发口径原先只是 frontmatter 里的一句软描述，**无可判定门槛、也无人保证它不被删**；
#   降级虽已三档，但「未走完前两档不得自生成」没有明文与断言 → 模型很容易直接自生成。
echo "[8d] 触发门与降级顺序"
for _k in '^trigger:' '^  when_any:' '^  dlut_markers:' '^  learning_markers:' '^  learning_intents:' \\
          '^  not_triggered_behavior:' '^  lock_after_trigger:' '^  ladder:' '^  self_generate_requires:'; do
  if grep -q "$_k" config.yaml 2>/dev/null; then ok "config.yaml 含 $_k"
  else bad "config.yaml 缺 $_k（触发门真相源不完整）"; fi
done
for _k in '触发门与接管边界' '不接管' '必须走三级结构' '未穷尽档 1、未尝试档 2，不得进入档 3 自行生成'; do
  if grep -qF "$_k" SKILL.md 2>/dev/null; then ok "SKILL.md 触发门含「$_k」"
  else bad "SKILL.md 触发门缺「$_k」"; fi
done
for _t in 明确涉及大连理工大学 知识学习 自述为大连理工大学学生; do
  if grep -qF "$_t" SKILL.md 2>/dev/null; then ok "触发条件在位：$_t"
  else bad "触发条件缺：$_t"; fi
done
for _f in library/domain-review.md library/general-fallback.md library/external-bridge.md; do
  if grep -qF '档序强制' "$_f" 2>/dev/null; then ok "$(basename "$_f") 已声明「档序强制」"
  else bad "$(basename "$_f") 缺「档序强制」（降级顺序未强制）"; fi
done
if grep -qF '触发门' commands/qihang.md 2>/dev/null; then ok "入口卡已接入触发门"
else bad "commands/qihang.md 未接入触发门"; fi
if grep -qF '检索 12 平台' commands/qihang.md 2>/dev/null; then
  bad "入口卡仍写「检索 12 平台」（v3.3.1 起已改为按域指定 2–3 个）"
else ok "入口卡平台口径已更新"; fi

'''
t = read('scripts/selfcheck.sh')
if t is None:
    print('  [SKIP] 无 scripts/selfcheck.sh')
elif '[8d] 触发门与降级顺序' in t:
    print('  [SAME] [8d] 段已在位')
else:
    A = '# ---------- 9. 库内唯一通道（纯 DUT 特化库） ----------'
    if A in t:
        write('scripts/selfcheck.sh', t.replace(A, S8D + A, 1))
        print('  [OK]   已插入 [8d] 段')
    else:
        print('  [MISS] 未找到 [9] 锚点')

# =============================================================== F) negative_test 第 11 类
print('== F) negative_test 第 11 类注入（触发门被删）==')
NT = read('scripts/negative_test.py')
if NT is None:
    print('  [SKIP] 无 negative_test.py')
elif 'inject_no_gate' in NT:
    print('  [SAME] 已存在')
else:
    A1 = 'def inject_identity_drift(tree):'
    B1 = ('''def inject_no_gate(tree):
    """把 SKILL.md 的触发门整段删掉 → selfcheck [8d] 应 FAIL（防触发门被静默移除）。"""
    p = os.path.join(tree, 'SKILL.md')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('## 触发门与接管边界', '## （已移除）', 1)
    return [p], t


def inject_identity_drift(tree):''')
    A2 = ("        ('身份串漂移（INSTALL.md 与 config.yaml 不一致）', inject_identity_drift,\n"
          "         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8c] 身份串一致性'),")
    B2 = ("        ('身份串漂移（INSTALL.md 与 config.yaml 不一致）', inject_identity_drift,\n"
          "         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8c] 身份串一致性'),\n"
          "        ('触发门被移除（SKILL.md 少了触发门小节）', inject_no_gate,\n"
          "         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8d] 触发门'),")
    if A1 in NT and A2 in NT:
        write('scripts/negative_test.py', NT.replace(A1, B1, 1).replace(A2, B2, 1))
        print('  [OK]   已加第 11 类注入')
    else:
        print('  [MISS] 锚点未命中（A1=%s A2=%s）' % (A1 in NT, A2 in NT))

# =============================================================== G) 构建侧层序
edit('scripts/_build/v3/README.md', [
    ('| 23 | `step64_identity_lock.py` |',
     '| 24 | `step65_trigger_gate.py` | **触发门收紧 + 锁定与降级强制**：config.yaml 立 `trigger` 段为唯一真相源'
     '（三条件 / 标记词 / 不接管行为 / 锁定 / 四级 ladder / 自生成前置）· SKILL.md 增「触发门与接管边界」'
     '（含「未穷尽档 1、未尝试档 2，不得进入档 3 自行生成」）· 三处规则文件补「档序强制」· 入口卡补第 0 步'
     '并修重复编号与「12 平台」旧口径 · selfcheck `[8d]` · 负向注入第 11 类；修订号 → `3.3.4` | 新增层 |\n'
     '| 23 | `step64_identity_lock.py` |',
     'step65_trigger_gate.py'),
])

# =============================================================== H) 版本
print('== H) 修订号 %s → %s ==' % (OLD_REV, NEW_REV))
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
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD_REV, '"version": "%s"' % NEW_REV),
        ('config.yaml', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD_REV, '**修订号 = `%s`**' % NEW_REV),
        ('library/output-spec.md', '如 `3.3.0` → `%s`）' % OLD_REV, '如 `3.3.0` → `%s`）' % NEW_REV),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

print('done')
