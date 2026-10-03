# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 15 层 · 需求确定门】clarity.md §3.1（理解准确率 ≥ 95%）+ 阈值入 config.yaml
#   + regress.sh [9] 断言 + 修订号 3.2.0 → 3.2.1（包版本仍两位 3.2）
# 用法：python scripts/_build/v3/step52_requirement_confirm.py [仓库根]
# 幂等：用「完成判据」判定（[9] 段 / §3.1 已在位即跳过；版本号已是 3.2.1 则 MISS）。
#
# 版本口径：**包版本 = 修订号前两位**（`3.2` ↔ `3.2.x`）；同一包版本线内**修订号递增**
#   （本轮为「需求确定门」这一规则变更 → `3.2.0` → `3.2.1`）。展示位仍是 `v3.2`。
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
OLD, NEW, PKG = '3.2.0', '3.2.1', '3.2'

# ---------------------------------------------------------------- clarity.md §3.1 正文
S31 = '''### 3.1 需求确定门（理解准确率 **≥ 95%** 才直接执行）

§3 的 `U` 解决「**能不能问**」，本门解决「**我理解得对不对**」。二者是同一算式的两面：

```
理解准确率  C = 1 − U = Σ(wᵢ · cᵢ) / Σwᵢ
```

| 档 | `C` | 动作 |
|---|---|---|
| **确定档** | `C ≥ 0.95` | **直接执行**，不复述（保住「快速输出」） |
| **复述档** | `0.70 ≤ C < 0.95` | **先用一句话复述**「你要的是 ⟨对象 + 任务⟩，产出 ⟨产出物⟩，约束 ⟨若有且影响执行⟩」；用户不纠正即执行，纠正则按 §4 就缺口追问 |
| **追问档** | `C < 0.70` | 按 §3 / §5 原判定追问（**本门不改变「是否追问」的判定**） |

**复述档的三条硬规格**：

1. **一句话**，且**必须引用用户原话里的词**（≥1 个对象词 + ≥1 个产出词）—— 引用不出即视为「尚未确定」，退回追问档；
2. **不得新增**用户没说过的内容（新增即视为理解错误），只允许删与并；
3. 复述落在输出的 **【假设】** 字段（`library/output-spec.md` 已有该字段）→ **不新增输出字段、不改输出硬契约**，也不出现内部名或过程叙述。

**与既有规则的关系（优先级不变）**：

| 规则 | 关系 |
|---|---|
| **红线**（§5 例外 4 / §7） | **红线优先于本门** —— 命中红线仍**不追问、不复述**，直接拒绝 + 合规替代 |
| **例外 6 通用知识型** | 答案不依赖个人与校情数据 → **视为 `C` 达标**，直接执行（否则会退化成假复述） |
| **例外 3 显式「直接给结果」** | 跳过复述，但**首行**须标假设（与 §8 一致） |
| **例外 5 紧急豁免** | 复述**并入**那 1 个追问，不额外增加打扰 |
| **§8 三轮未达标** | 仍按最大后验执行 + 首行标 `⚠️ 假设`（与复述档**合并**，不重复两次） |

**两个可复现自检问**（任一为「否」→ 不得进入执行）：

1. 我能否用「**做什么 + 给什么**」一句话说清用户要的东西？
2. 用户看到我的产出，会不会说「**我指的不是这个**」？

> **为什么要有这道门**：澄清门允许 `C ≈ 0.70` 就放行（例 A 即 `C = 0.689`）—— 那是「可以问、但不必问」的口径；
> 而「动手前确认理解」是另一件事：**错理解的代价 = 白做一轮**。本门只加「一句话复述」的成本，
> 且**只在 0.70–0.95 这一档**触发，`C ≥ 0.95` 与「通用知识型」都**免复述**。

'''

# ---------------------------------------------------------------- regress [9] 段正文
S9 = '''  echo "[9] 需求确定门（理解准确率 ≥ 95% 才直接执行）"
  _cl="library/clarity.md"
  if grep -q '需求确定门' "$_cl" 2>/dev/null; then _ok "需求确定门已在位"; else _fail "clarity.md 缺需求确定门"; fi
  if grep -qF 'C = 1 − U' "$_cl" 2>/dev/null; then _ok "已声明理解准确率口径 C = 1 − U"; else _fail "未声明 C = 1 − U"; fi
  if grep -qF '0.95' "$_cl" 2>/dev/null; then _ok "已声明 95% 阈值"; else _fail "未声明 0.95 阈值"; fi
  if grep -qF '0.70' "$_cl" 2>/dev/null; then _ok "已声明复述档下界 0.70"; else _fail "未声明 0.70 下界"; fi
  for _t in 确定档 复述档 追问档; do
    if grep -q "$_t" "$_cl" 2>/dev/null; then _ok "三档已定义：$_t"; else _fail "三档缺：$_t"; fi
  done
  # 复述档三条硬规格
  for _t in '一句话' '不得新增' '【假设】'; do
    if grep -qF "$_t" "$_cl" 2>/dev/null; then _ok "复述规格已声明：$_t"; else _fail "复述规格缺：$_t"; fi
  done
  # 红线优先于本门 + 例外 6 视为达标（防「为了确认而削弱合规」与「假复述」）
  grep -qF '红线优先于本门' "$_cl" 2>/dev/null && _ok "红线优先于需求确定门" || _fail "未声明红线优先于本门"
  grep -qF '视为 `C` 达标' "$_cl" 2>/dev/null && _ok "例外 6 视为 C 达标（免复述）" || _fail "未声明例外 6 免复述"
  # 两个可复现自检问
  grep -qF '可复现自检问' "$_cl" 2>/dev/null && _ok "已给出可复现自检问" || _fail "缺可复现自检问"
  # 阈值单一真相源必须在 config.yaml（与 §3 的 U 阈值同源约定）
  if grep -q 'confirm_threshold: 0.95' config.yaml 2>/dev/null; then _ok "config.yaml 声明 confirm_threshold: 0.95"
  else _fail "config.yaml 缺 confirm_threshold: 0.95（阈值未落在单一真相源）"; fi
  echo "=========================================="
  echo ""
  r=$((r + 1))
done

echo "回归测试完毕'''


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def ensure_block(rel, block, anchor, label):
    """保证 block 在 rel 里**恰好出现一次**（折叠重复 + 缺失则插在 anchor 之后）。

    为什么不用裸 `replace(anchor, anchor+block)`：那是**追加型替换**，anchor 不消失
    → 每跑一次多插一份（本层实测把 `confirm_threshold` 插成两份）。同 step50 的口径。"""
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    t = re.sub(r'(?:' + re.escape(block) + r'\n)+', block + '\n', t)
    if block not in t:
        if anchor and anchor in t:
            t = t.replace(anchor, anchor + '\n' + block, 1)
            print('  [OK]   %s :: 插入 %s' % (rel, label))
        else:
            print('  [MISS] %s :: 未找到锚点（%s）' % (rel, label)); return
    elif t != o:
        print('  [FIX]  %s :: 折叠重复的 %s' % (rel, label))
    else:
        print('  [SAME] %s :: %s 已在位' % (rel, label)); return
    write(rel, t)


def edit(rel, pairs, quiet=False):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for a, b in pairs:
        if a not in t:
            if not quiet:
                print('  [MISS] %s :: %r' % (rel, a[:56]))
            continue
        t = t.replace(a, b); print('  [OK]   %s :: %r' % (rel, a[:56]))
    if t != o:
        write(rel, t)


# ---------------------------------------------------------------- 1) clarity.md §3.1
print('== 1) library/clarity.md：新增 §3.1 需求确定门 ==')
_c = read('library/clarity.md')
if _c is None:
    print('  [SKIP] 缺 library/clarity.md')
elif '需求确定门' in _c:
    print('  [SAME] §3.1 已在位')
elif '## 4. 追问优先级（高杠杆优先）' in _c:
    write('library/clarity.md', _c.replace('## 4. 追问优先级（高杠杆优先）', S31 + '## 4. 追问优先级（高杠杆优先）', 1))
    print('  [OK]   已插入 §3.1（需求确定门）')
else:
    print('  [MISS] 未找到 §4 锚点')

# ---------------------------------------------------------------- 2) config.yaml 阈值
print('== 2) config.yaml：阈值进单一真相源 ==')
ensure_block(
    'config.yaml',
    '    # 需求确定门（见 library/clarity.md §3.1）：C = 1 − U 为「理解准确率」\n'
    '    #   C >= 0.95 → 直接执行（免复述）｜0.70 <= C < 0.95 → 一句话复述并落【假设】｜C < 0.70 → 追问\n'
    '    confirm_threshold: 0.95        # 免复述阈值\n'
    '    restate_floor: 0.70            # 复述档下界（低于此值走追问，本门不改变追问判定）',
    '    ask_priority: {W: 3.0, O: 2.5, D: 2.0, C: 1.5, B: 1.0, T: 0.5}',
    '需求确定门阈值块')

# ---------------------------------------------------------------- 3) regress.sh [9] 段
print('== 3) scripts/regress.sh：新增 [9] 需求确定门 ==')
_rg = read('scripts/regress.sh')
_TAIL = '  echo "=========================================="\n  echo ""\n  r=$((r + 1))\ndone\n\necho "回归测试完毕'
if _rg is None:
    print('  [SKIP] 缺 scripts/regress.sh')
elif 'echo "[9] 需求确定门' in _rg:
    print('  [SAME] [9] 段已在位')
elif _TAIL in _rg:
    # 注意：S9 **已自带收尾**（`echo "=====" / r++ / done / echo "回归测试完毕`），
    # 故只能「用 S9 替换 _TAIL」；写成 S9 + _TAIL 会多带一份收尾 → 语法错误
    # （实测被 selfcheck 的「regress.sh 语法错误」当场抓到）。
    write('scripts/regress.sh', _rg.replace(_TAIL, S9, 1))
    print('  [OK]   已插入 [9] 需求确定门 段')
else:
    print('  [MISS] 未找到插入锚点（汇总尾部）')

# ---------------------------------------------------------------- 4) 修订号 3.2.0 → 3.2.1
print('== 4) 修订号 %s → %s（包版本仍 %s）==' % (OLD, NEW, PKG))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        t = read(rel)
        if t is None:
            continue
        if 'version: %s' % OLD in t:
            write(rel, t.replace('version: %s' % OLD, 'version: %s' % NEW)); n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)

edit('SKILL.md', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('.codebuddy-plugin/plugin.json', [('"version": "%s"' % OLD, '"version": "%s"' % NEW)])
edit('config.yaml', [('version: %s' % OLD, 'version: %s' % NEW)])
edit('scripts/aligncheck.py', [
    ("!= '%s':" % OLD, "!= '%s':" % NEW),
    ("（期望 %s）' %% vm.group(1))" % OLD, "（期望 %s）' %% vm.group(1))" % NEW),
    ("vers - {'%s'}" % OLD, "vers - {'%s'}" % NEW),
    ("pv != '%s'" % OLD, "pv != '%s'" % NEW),
    ("（期望 %s）' %% pv)" % OLD, "（期望 %s）' %% pv)" % NEW),
    ("not in ('%s', '%s')" % (PKG, OLD), "not in ('%s', '%s')" % (PKG, NEW)),
    ("m.group(1), '%s', '%s'))" % (PKG, OLD), "m.group(1), '%s', '%s'))" % (PKG, NEW)),
    ("期望包版本 %s 或修订号 %s" % (PKG, OLD), "期望包版本 %s 或修订号 %s" % (PKG, NEW)),
    ("'%s' not in v:" % OLD, "'%s' not in v:" % NEW),
    ("未声明版本 %s" % OLD, "未声明版本 %s" % NEW),
    ("修订号 = 三位（%s）" % OLD, "修订号 = 三位（%s）" % NEW),
])
edit('library/output-spec.md', [
    ('｜**修订号 = `%s`**（三位' % OLD, '｜**修订号 = `%s`**（三位' % NEW),
    ('包 `%s` 对应修订 `%s`' % (PKG, OLD), '包 `%s` 对应修订 `%s`' % (PKG, NEW)),
    ('**已并入 `%s`**，勿再引用 v3.1' % OLD, '**已并入 `%s` 线**（并入时为 `%s`，现 `%s`），勿再引用 v3.1' % (PKG, OLD, NEW)),
])

# ---------------------------------------------------------------- 5) 版本口径说明（同步「包版本 = 修订号前两位」）
print('== 5) 口径文本：包版本 = 修订号前两位 ==')
edit('library/output-spec.md', [
    ('> 本规范**不另设修订号**，随包版本同一条线：包 `%s` 对应修订 `%s`。' % (PKG, NEW),
     '> 本规范**不另设修订号**，随包版本同一条线：**包版本 = 修订号前两位**（`%s` ↔ `%s.x`），'
     '同一包版本线内**修订号递增**（规则变更 +1，如 `%s` → `%s`）。' % (PKG, PKG, OLD, NEW)),
])

print('done')
