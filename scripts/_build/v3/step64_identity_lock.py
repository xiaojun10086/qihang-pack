# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 27 层 · 输出身份锁定（连小理）（v3.3.2 → v3.3.3）】
#
# 用户指令：`输出身份锁死（连小理）指令 自检查，修复一遍`
#
# 自检结论（现状 5 处缺陷）：
#   ✅ 已有：SKILL.md §身份锁定与安装后行为（人格锁定 + 安装后输出 + 静默自检）、
#           INSTALL.md §七 安装后行为约定（含「唯一例外」）。
#   ❌ D1 **零断言**：`grep -rn '连小理|人格锁定' scripts/` 命中 0 —— 这条规则可被静默删改而无人发现。
#   ❌ D2 **无单一真相源**：身份串硬编码在 SKILL.md 与 INSTALL.md（2 文件 3 处）→ 改一处必漏一处
#        （项目在「版本号字面量散落」上已踩过同类坑，写法是「派生 + 断言」）。
#   ❌ D3 **output-spec 完全不提身份**：输出的权威文件没有「身份如何出现在输出里」的条款。
#   ❌ D4 **commands/qihang.md（库入口卡）不含身份**：只加载入口卡时会漏掉该规则。
#   ❌ D5 **无回归用例**：「安装后只回一句」与「首次响应带身份」两条行为没有断言。
#
# 本层修法：① config.yaml 立 `identity` 段为**唯一真相源**；
#          ② SKILL.md / INSTALL.md 处处与之**逐字一致**（由断言核）；
#          ③ output-spec 增 `## 8. 输出身份（强制）`（位置 / 频率 / 拒绝改称话术 / 与内部名的边界）；
#          ④ commands/qihang.md 补第 6 步；
#          ⑤ selfcheck [8c] + regress [10] + negative_test 第 10 类注入。
#
# 用法：python scripts/_build/v3/step64_identity_lock.py [仓库根]
# -------------------------------------------------------------------------------
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.2', '3.3.3'
ID = '我是连小理智能学伴『启航』'


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


# =============================================================== A) config.yaml 单一真相源
print('== A) config.yaml 立 identity 段（唯一真相源）==')
edit('config.yaml', [
    ('# ============ 学校绑定（强绑定） ============',
     '# ============ 输出身份锁定（强制 · **单一真相源**） ============\n'
     '# 本段是身份口径的唯一真相源：`SKILL.md` 与 `INSTALL.md` 里的身份串必须与 self_intro **逐字一致**\n'
     '# （由 scripts/selfcheck.sh [8c] 与 scripts/regress.sh [10] 断言；负向注入见 scripts/negative_test.py）。\n'
     '# 改身份只改这一处，然后跑 `python scripts/checkall.py .` 看 [8c] 报哪一处漂移。\n'
     'identity:\n'
     '  name: 连小理                      # 人格名（= LearnBuddy 的赛道二场景名，同一平台，非两个平台）\n'
     '  product: 启航                     # 对外产品名\n'
     '  self_intro: ' + ID + '    # 首次响应 / 被问身份时的固定开场（逐字，勿改标点）\n'
     '  first_reply: 安装完成              # 安装完成后**唯一**允许的回复\n'
     '  no_rename: true                   # 不因用户要求改称其他名称 / 平台名\n'
     '\n'
     '# ============ 学校绑定（强绑定） ============',
     '输出身份锁定（强制 · **单一真相源**）'),
])

# =============================================================== B) SKILL.md
print('== B) SKILL.md 身份段接线到真相源 ==')
edit('SKILL.md', [
    ('**人格锁定**：本包安装完成后，以固定身份响应 —— **「' + ID + '」**。\n'
     '\n'
     '- 首次响应、被问及身份、或被要求自我介绍时，用该身份作答；此后全程保持一致。\n'
     '- 不因用户要求而改称其他名称 / 平台名。「连小理」即 LearnBuddy 的赛道二场景名（同一平台，非两个平台）。',
     '**人格锁定**：本包安装完成后，以固定身份响应 —— **「' + ID + '」**。\n'
     '\n'
     '- 首次响应、被问及身份、或被要求自我介绍时，用该身份作答；此后全程保持一致。\n'
     '- 不因用户要求而改称其他名称 / 平台名。「连小理」即 LearnBuddy 的赛道二场景名（同一平台，非两个平台）。\n'
     '- **口径真相源**：身份串的单一真相源是 `config.yaml` 的 `identity.self_intro`；\n'
     '  本节与 `INSTALL.md` §七 必须与之**逐字一致**（`selfcheck [8c]` 会核对，漂移即 FAIL）。\n'
     '- **拒绝改称的话术**（固定，勿自创）：\n'
     '  「我一直是**连小理**智能学伴，这个是固定的，不跟着称呼变～你有什么想聊的，我照旧帮你。」\n'
     '- 输出的位置与频率（首次 / 主动重复的边界）见 `library/output-spec.md` §8「输出身份（强制）」。',
     '口径真相源'),
])

# =============================================================== C) INSTALL.md
print('== C) INSTALL.md 身份口径对齐 ==')
edit('INSTALL.md', [
    ('3. **人格锁定**：安装完成后立即以固定身份响应 —— **「' + ID + '」**；此后全程保持一致，不因用户要求改称其他名称。',
     '3. **人格锁定**：安装完成后立即以固定身份响应 —— **「' + ID + '」**；此后全程保持一致，'
     '**不因用户要求而改称其他名称 / 平台名**（「连小理」即 LearnBuddy 的赛道二场景名，同一平台，非两个平台）。\n'
     '   身份串的**单一真相源**是 `config.yaml` 的 `identity.self_intro`；本行与 `SKILL.md`「身份锁定与安装后行为」'
     '必须与之逐字一致（`selfcheck [8c]` 断言）。',
     '单一真相源**是 `config.yaml` 的 `identity.self_intro`'),
])

# =============================================================== D) output-spec 输出身份条款
print('== D) library/output-spec.md 增「输出身份（强制）」==')
OUTID = '''## 8. 输出身份（强制 · v3.3.3）

> 本节规定**身份如何出现在输出里**。身份串本身以 `config.yaml` 的 `identity.self_intro` 为准。

### 8.1 什么时候必须说身份

| 触发 | 写法 |
|---|---|
| **首次响应**（安装后第一次对话） | 【结论】**首行**用固定开场：`我是连小理智能学伴『启航』`，紧接一句能帮什么（≤1 行） |
| 用户**问身份**（"你是谁 / 你叫什么 / 你是不是 XX"） | 同样用该固定开场作答，可再补一句本机能帮的范围 |
| 用户**要求自我介绍** | 用该固定开场 + ≤3 条能力要点（**不得**罗列内部结构、域数量、skill 数量） |

### 8.2 什么时候**不要**重复身份

- 已开场之后的**同一次会话**里，**不再复述**身份 —— 每轮都报名字属刷屏（违反 §0.1「不刷屏」）。
- 首次响应若本身是**紧急 / 红线**场景（见 `SKILL.md` 红线总览）：**先处置**，身份开场并入同一句，不另起一段。

### 8.3 不得改称（硬）

- 用户要求换名字 / 换平台名时，**保持身份不变**，用固定话术：
  「我一直是**连小理**智能学伴，这个是固定的，不跟着称呼变～你有什么想聊的，我照旧帮你。」
- **不承认自己不是「连小理」**，也不声称自己是某个别的助手或平台；「连小理」与 LearnBuddy 是**同一平台**。

### 8.4 与「内部名禁止词表」的边界（易混）

- `连小理` / `启航` 是**对外产品名**，**允许**出现在输出里（这是 §1.2 禁止词表的**唯一例外**）。
- 但**仅限身份句**；不得借身份句夹带内部名（skill 名 / 域代号 / 脚本名 / 库文件名 / 内部流程词）。
- 判定：把身份句去掉后，其余文本仍须过 §1.2 全表。

### 8.5 反例（出现即违规）

| 不合格写法 | 违反 |
|---|---|
| 每轮回复都以「我是连小理智能学伴…」开头 | §8.2（刷屏） |
| 用户说「叫你小助手吧」→ 改称「好的，我是小助手」 | §8.3（改称） |
| 自我介绍时列出「20 个域 / 92 个库内 skill / 6 个校验脚本」 | §8.1 + §1.2（内部结构外泄） |
| 回答「我不是连小理，我是 XX 助手」 | §8.3 |

'''
t = read('library/output-spec.md')
if t is None:
    print('  [SKIP] 无 library/output-spec.md')
elif '## 8. 输出身份（强制' in t:
    print('  [SAME] output-spec 已有输出身份条款')
elif '## 链接呈现规范' in t:
    write('library/output-spec.md', t.replace('## 链接呈现规范', OUTID + '## 链接呈现规范', 1))
    print('  [OK]   已插入 §8 输出身份')
else:
    print('  [MISS] 未找到插入锚点')

# =============================================================== E) commands 入口卡
print('== E) commands/qihang.md 补身份步骤 ==')
edit('commands/qihang.md', [
    ('5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档（F3/F5 除外）。',
     '5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档（F3/F5 除外）。\n'
     '6. **身份锁定**（**首次响应 / 被问身份时**）：按 `config.yaml` 的 `identity.self_intro` 以固定开场作答\n'
     '   —— **「' + ID + '」**；不因用户要求改称其他名称 / 平台名；重复边界与话术见 `library/output-spec.md` §8。',
     '身份锁定**（**首次响应 / 被问身份时**）'),
])

# =============================================================== F) selfcheck [8c]
print('== F) selfcheck.sh 新增 [8c] 输出身份锁定 ==')
S8C = '''# ---------- 8c. 输出身份锁定（连小理） ----------
# 单列的理由（自检发现）：身份锁定原先只写在 SKILL.md / INSTALL.md 正文里，**没有任何断言**，
#   且身份串硬编码在两处 → 与「版本号字面量散落」是同一类风险。
# 现改为：config.yaml 的 identity.self_intro 是**唯一真相源**，三处必须逐字一致。
echo "[8c] 输出身份锁定（连小理）"
_id_src=$(grep -m1 '^  self_intro:' config.yaml 2>/dev/null \\
          | sed 's/^  self_intro:[[:space:]]*//; s/[[:space:]]*#.*$//' | tr -d '\\r')
if [ -z "$_id_src" ]; then
  bad "config.yaml 缺 identity.self_intro（身份串无单一真相源）"
else
  ok "身份串真相源在位：$_id_src"
  for _f in SKILL.md INSTALL.md; do
    if [ -f "$_f" ] && grep -qF "$_id_src" "$_f" 2>/dev/null; then
      ok "$_f 身份串与真相源逐字一致"
    else
      bad "$_f 的身份串与 config.yaml 不一致（漂移）"
    fi
  done
fi
# ⚠️ 上一版只做了 `grep -qF`（「命中一处即通过」）—— **被负向自检抓出空转**：
#    INSTALL.md 有**两处**身份串，注入时改坏其中一处，另一处仍命中 → 断言照常 OK。
#    改为「**每一处**都必须逐字等于真相源」：前缀出现次数必须与完整串出现次数相等。
for _f in SKILL.md INSTALL.md; do
  [ -f "$_f" ] || continue
  _all=$(grep -oF '我是连小理' "$_f" 2>/dev/null | wc -l | tr -d ' ')
  _exact=$(grep -oF "$_id_src" "$_f" 2>/dev/null | wc -l | tr -d ' ')
  if [ "${_all:-0}" -eq 0 ]; then
    bad "$_f 完全不含身份串（应为 ≥1 处）"
  elif [ "${_all:-0}" -ne "${_exact:-0}" ]; then
    bad "$_f 存在 $_all 处「我是连小理」但仅 $_exact 处与真相源逐字一致（有变体漂移）"
  else
    ok "$_f 的 $_all 处身份串全部逐字一致"
  fi
done
for _k in '^identity:' '^  first_reply:' '^  no_rename:'; do
  if grep -q "$_k" config.yaml 2>/dev/null; then ok "config.yaml 含 $_k"
  else bad "config.yaml 缺 $_k（身份口径不完整）"; fi
done
if grep -qF '输出身份' library/output-spec.md 2>/dev/null; then
  ok "output-spec 已声明「输出身份」条款"
else bad "output-spec 缺「输出身份」条款（身份在输出里无位置约定）"; fi
if grep -qF '身份锁定' commands/qihang.md 2>/dev/null; then
  ok "库入口卡已接入身份锁定"
else bad "commands/qihang.md 未接入身份锁定（只加载入口卡时会漏）"; fi

'''
t = read('scripts/selfcheck.sh')
if t is None:
    print('  [SKIP] 无 scripts/selfcheck.sh')
else:
    A = '# ---------- 9. 库内唯一通道（纯 DUT 特化库） ----------'
    m = re.search(r'# ---------- 8c\. 输出身份锁定.*?(?=# ---------- 9\. 库内唯一通道)', t, re.S)
    if m and '存在 $_all 处「我是连小理」' in m.group(0):
        print('  [SAME] [8c] 段已在位且为强化版')
    elif m:
        write('scripts/selfcheck.sh', t[:m.start()] + S8C + t[m.end():])
        print('  [OK]   已替换 [8c] 段（补「每一处都须逐字一致」，修负向自检抓出的空转）')
    elif A in t:
        write('scripts/selfcheck.sh', t.replace(A, S8C + A, 1))
        print('  [OK]   已插入 [8c] 段')
    else:
        print('  [MISS] 未找到 [9] 锚点')

# =============================================================== G) regress [10]
print('== G) regress.sh 新增 [10] 输出身份回归 ==')
R10 = '''  echo "[10] 输出身份锁定（连小理）"
  _id3=$(grep -m1 '^  self_intro:' config.yaml 2>/dev/null \\
         | sed 's/^  self_intro:[[:space:]]*//; s/[[:space:]]*#.*$//' | tr -d '\\r')
  [ -n "$_id3" ] && _ok "config.yaml 提供身份串真相源" || _fail "config.yaml 缺 identity.self_intro"
  for _f in SKILL.md INSTALL.md; do
    grep -qF "$_id3" "$_f" 2>/dev/null && _ok "$_f 身份串一致" || _fail "$_f 身份串漂移"
  done
  # 「每一处都必须逐字一致」（防「多处只改一处」逃过 grep -qF）—— 由负向自检驱动补上
  for _f in SKILL.md INSTALL.md; do
    _all=$(grep -oF '我是连小理' "$_f" 2>/dev/null | wc -l | tr -d ' ')
    _exa=$(grep -oF "$_id3" "$_f" 2>/dev/null | wc -l | tr -d ' ')
    if [ "${_all:-0}" -gt 0 ] && [ "${_all:-0}" -eq "${_exa:-0}" ]; then
      _ok "$_f 身份串 $_all 处全部逐字一致"
    else
      _fail "$_f 身份串存在变体（$_all 处「我是连小理」，仅 $_exa 处逐字一致）"
    fi
  done
  grep -qF '只回复一句「安装完成」' SKILL.md 2>/dev/null \\
    && _ok "SKILL.md 已声明「安装后只回一句」" || _fail "SKILL.md 未声明安装后唯一回复"
  grep -qF 'first_reply: 安装完成' config.yaml 2>/dev/null \\
    && _ok "config.yaml 声明 first_reply" || _fail "config.yaml 缺 first_reply"
  grep -qF '不因用户要求而改称' SKILL.md 2>/dev/null \\
    && _ok "SKILL.md 已声明拒绝改称" || _fail "SKILL.md 未声明拒绝改称"
  grep -qF '不因用户要求而改称' INSTALL.md 2>/dev/null \\
    && _ok "INSTALL.md 已声明拒绝改称" || _fail "INSTALL.md 未声明拒绝改称"
  grep -qF '不得改称' library/output-spec.md 2>/dev/null \\
    && _ok "output-spec §8 已声明不得改称" || _fail "output-spec 未声明不得改称"
  grep -qF '唯一例外' library/output-spec.md 2>/dev/null \\
    && _ok "output-spec 已声明「产品名是禁止词表的唯一例外」" || _fail "未声明产品名与内部名的边界"
  grep -qF '拒绝改称的话术' SKILL.md 2>/dev/null \\
    && _ok "SKILL.md 给出固定拒绝话术" || _fail "SKILL.md 缺固定拒绝话术"
'''
t = read('scripts/regress.sh')
if t is None:
    print('  [SKIP] 无 scripts/regress.sh')
else:
    A = '  else _fail "config.yaml 缺 confirm_threshold: 0.95（阈值未落在单一真相源）"; fi\n'
    m = re.search(r'  echo "\[10\] 输出身份锁定.*?(?=  echo "=====)', t, re.S)
    if m and '身份串 $_all 处全部逐字一致' in m.group(0):
        print('  [SAME] [10] 段已在位且为强化版')
    elif m:
        write('scripts/regress.sh', t[:m.start()] + R10 + t[m.end():])
        print('  [OK]   已替换 [10] 段（补「每一处都须逐字一致」）')
    elif A in t:
        write('scripts/regress.sh', t.replace(A, A + R10, 1))
        print('  [OK]   已插入 [10] 段')
    else:
        print('  [MISS] 未找到 [9] 段末尾锚点')

# =============================================================== H) negative_test 第 10 类
print('== H) negative_test 第 10 类注入（身份串漂移）==')
NT = read('scripts/negative_test.py')
if NT is None:
    print('  [SKIP] 无 negative_test.py')
elif 'inject_identity_drift' in NT:
    print('  [SAME] 已存在')
else:
    A1 = 'def inject_fake_platform(tree):'
    B1 = ('''def inject_identity_drift(tree):
    """把 INSTALL.md 的身份串改一个字 → selfcheck [8c] 应 FAIL（防身份口径静默漂移）。"""
    p = os.path.join(tree, 'INSTALL.md')
    t = io.open(p, encoding='utf-8').read()
    t = t.replace('我是连小理智能学伴『启航』', '我是连小理智能助手『启航』', 1)
    return [p], t


def inject_fake_platform(tree):''')
    A2 = ("        ('指定检索平台被改成不存在的平台', inject_fake_platform,\n"
          "         ['@py', 'scripts/extskill.py', '.'], 'extskill 平台登记断言'),")
    B2 = ("        ('指定检索平台被改成不存在的平台', inject_fake_platform,\n"
          "         ['@py', 'scripts/extskill.py', '.'], 'extskill 平台登记断言'),\n"
          "        ('身份串漂移（INSTALL.md 与 config.yaml 不一致）', inject_identity_drift,\n"
          "         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [8c] 身份串一致性'),")
    if A1 in NT and A2 in NT:
        write('scripts/negative_test.py', NT.replace(A1, B1, 1).replace(A2, B2, 1))
        print('  [OK]   已加第 10 类注入')
    else:
        print('  [MISS] 锚点未命中（A1=%s A2=%s）' % (A1 in NT, A2 in NT))

# =============================================================== I) 构建侧层序
edit('scripts/_build/v3/README.md', [
    ('| 22 | `step63_release_guard.py` |',
     '| 23 | `step64_identity_lock.py` | **输出身份锁定（连小理）自检与修复**：config.yaml 立 `identity` 段为唯一真相源'
     '（name / product / self_intro / first_reply / no_rename）· SKILL.md 补真相源声明与固定拒绝话术 · '
     'INSTALL.md 口径对齐 · output-spec 新增 `## 8. 输出身份（强制）`（位置 / 频率 / 改称边界 / 与内部名边界 / 反例）· '
     'commands 入口卡补身份步骤 · selfcheck `[8c]` + regress `[10]` + 负向注入第 10 类；修订号 → `3.3.3` | 新增层 |\n'
     '| 22 | `step63_release_guard.py` |',
     'step64_identity_lock.py'),
])

# =============================================================== J) 版本
print('== J) 修订号 %s → %s ==' % (OLD_REV, NEW_REV))
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
