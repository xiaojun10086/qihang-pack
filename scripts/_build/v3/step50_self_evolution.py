# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2.0 生成链 · 第 13 层 · 习惯自迭代机制】新增 1 级库第 6 份规则文件 + 20 域接线 + 校验断言
# 用途：把「按用户习惯对域内 skill 做非结构性自迭代」固化成机制（可重跑、幂等）。
# 用法：python scripts/_build/v3/step50_self_evolution.py [仓库根]
# 幂等：在已达本层的树上重跑应零变更（已接线则跳过；规则文件内容一致则不写）。
# 边界（本层只做机制，不动版本号 / 不动计数 —— 那两项归 step51）：
#   · 只新增「可改段」的迭代权限，禁改结构性 / 合规性 / 事实性内容（规则文件 §2 明文列举）
# -------------------------------------------------------------------------------
import os, io, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))

RULE_REL = 'library/skill-evolution.md'

# ---------------------------------------------------------------- 规则文件正文
RULE = '''# `skill-evolution.md` · 习惯自迭代（1 级库第 6 份规则）

> 1 级 skill 库的第 6 份规则文件。**只授权「改怎么说」，不授权「改说什么」。**

## §0 定位

本文件让域内 skill 能**按用户习惯自我迭代**，服务于三个目标：

| 目标 | 达成方式 |
|---|---|
| **优化思考速度** | 已稳定命中的常规请求走**更短的步骤链**：合并重复说明、把已确认的判定前置、减少无效澄清轮次 |
| **精准化信息获取** | 把用户**常用的入口与字段**固化进执行步骤的检索顺序（先查已核验入口，再兜底），减少盲查 |
| **减少 AI 幻觉** | 迭代**只允许改写措辞与步骤粒度，不允许新增任何事实**；宁少说不补造 |

> 本文件是 1 级库的**横切职责**，与 `clarity.md` / `domain-review.md` / `output-spec.md` / `memory.md` / `login-policy.md` 并列。
> 它**不承载业务**，具体场景一律归 `domains/<域>/skills/local/`。

## §1 两个对象（都在运行时，用户侧）

| 对象 | 位置 | 是否随包分发 |
|---|---|---|
| **习惯画像** | 用户运行环境（如 `~/.qihang/habit-profile.md`） | ❌ **不随包**（保持本包「纯库内、零外部依赖」定位） |
| **迭代日志** | 用户运行环境（如 `~/.qihang/skill-evolution-log.md`） | ❌ **不随包** |

- 交付物里**不含**任何个人习惯数据；包内只有本机制与格式约定。
- 习惯画像**只读来源**：用户显式表达（「以后都这样」「别每次都问」）+ 重复出现的行为模式。
- **禁止**把习惯画像写进 `library/` 或 `domains/`，也**禁止**跨用户共享。

## §2 硬边界：可改段 / 禁改段（**唯一授权范围**）

### §2.1 可改段（只在这三处动手）

| 段 | 允许的动作 |
|---|---|
| `## 执行步骤` | 改写**措辞**、**细化或合并步骤**、调整**步骤内部的说明顺序**；不改步骤数量以外的骨架语义 |
| `## 方法库 · 判定细则` | 追加**判定细则**（如何分辨、优先看哪一项）；**不得**引入任何数值 / 链接 / 单位名 |
| 示例的**说明性文字** | 补充「为什么这样判」的一句话说明；**不得**改动示例的输出块结构 |

### §2.2 禁改段（触碰即拒绝，且必须回滚）

- **frontmatter**（`name` / `description` / `version` / `license` / `tags`）
- **标题与段落顺序**（`## 前置` → `## 边界` → `## 执行步骤` → `## 方法库 · 判定细则` → `## 可执行示例` → `## ⚠️ 红线` → `## 输出` → `## DUT 绑定点` → `## 失败与降级` → `## 与同域其他库内 skill 的分工`）
- **`## ⚠️ 红线`**（须与所属 `_domain.md` 逐条逐字一致）
- **`## 输出`** 与示例的**输出块结构**（【结论】/【下一步】等字段契约，见 `library/output-spec.md`）
- **`## 失败与降级`** 的承接目标（必须指名同域真实 skill）
- **`## 与同域其他库内 skill 的分工`**
- **`## DUT 绑定点`**、`## 边界`、`## 前置`
- **任何事实**：URL / 电话 / 单位名 / 姓名 / 职称 / 阈值 / 计数 / 版本号 / 日期 / 成绩与政策口径
- **跨域、跨级**改动（只能改**本域**库内 skill；不碰 1 级库与别的域）

> **事实类内容要改，走正常生成流程**（改生成链的数据表后重跑；生成链**只在源仓库内、不随包分发**），**不得借自迭代夹带**。

## §3 触发条件（满足其一才生成提案）

1. **重复澄清**：同一域同一 skill 连续 **≥3 次**出现同一个追问，且该追问**不是**关键槽（`O/T/D`）所必需；
2. **重复纠正**：用户对同一输出形态连续 **≥2 次**给出同向修正意见；
3. **显式指令**：用户明说「以后都这样」「不用每次问」；
4. **稳定偏好**：习惯画像里已记录且**近 10 次一致**的入口 / 字段偏好。

> 不满足上述条件 → **不迭代**（宁可慢，不可乱改）。

## §4 执行流程（六步，不可跳步）

1. **读画像**：读习惯画像与迭代日志，确认触发条件成立；
2. **出提案**：写明「域 / skill / 命中哪一条触发条件 / 拟改哪个可改段 / 前后对照」；
3. **边界校验**：逐条对照 §2.2 禁改清单；**命中任一项即拒绝该提案**并记日志；
4. **落盘**：只改 §2.1 允许的段落；单次迭代**≤1 个域 × ≤2 个 skill**；
5. **记日志**：时间 / 域 / skill / 段落 / 前后摘要 / 依据 / 校验结果；
6. **回归确认**：跑 `bash scripts/regress.sh 1`，`[8] 自迭代边界` 段必须 **FAIL 0**；再跑 `scripts/runcheck.py` 确认运行链仍可解。

> **累计阈值**：同一 skill 的 `## 执行步骤` 累计改动超过 **50%** 时，停止自迭代，转人工评审（说明该 skill 的定位可能已变 —— 那是结构性问题）。

## §5 不可让渡的三条（合规优先于速度）

1. **红线优先**：任何迭代都不得削弱红线；红线命中时仍**不追问、直接拒绝 + 给合规替代**。
2. **判定不受习惯影响**：习惯**不影响**「是否追问 / 是否放行 / 是否降级」的判定，**不得**绕过澄清门关键槽 `O/T/D`，也不得绕过登录档位（A/B/C）；它只能让**话术与步骤粒度**更贴人。
3. **输出契约不变**：迭代后的 skill 仍须满足输出形态硬契约（结论清楚前置 / 字段标签不超过 6 个 / 有实质字段 / **零内部名** / 降级只写能力级）；学习详解不以条目上限删减必要知识。

## §6 验收口径

| 目标 | 判据 |
|---|---|
| 思考速度 | 同一类请求的**追问轮次下降**，且**放行错误数不上升** |
| 精准信息 | 检索先命中**已核验 ✅** 入口；**零编造**（URL / 电话 / 单位名 / 政策口径） |
| 减少幻觉 | 每次迭代**新增事实性断言数 = 0**（用 diff 逐条核对） |

## §7 与其他 1 级规则的关系

| 文件 | 关系 |
|---|---|
| `clarity.md` | 自迭代**不得**改动澄清门公式、阈值与例外；只可优化**问法顺序** |
| `domain-review.md` | 域归属不变；自迭代不产生新的跨域分支 |
| `output-spec.md` | 输出契约的**唯一真相源**；自迭代不得与它冲突（冲突以 output-spec 为准） |
| `memory.md` | 习惯画像与学习档案**分开存放**；学习档案不因自迭代而改写 |
| `login-policy.md` | 登录档位判定不变；习惯只可优化**入口提示措辞** |
'''

# ---------------------------------------------------------------- 域接线正文
WIRE = ('5. 按 `library/skill-evolution.md` 记录本域习惯，并**只在可改段内**做非结构性自迭代'
        '（不改红线 / 输出契约 / 任何事实；不满足触发条件则不迭代）')
WIRE_MARK = 'library/skill-evolution.md'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    io.open(p, 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs, label=None):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（文件不存在）' % rel); return
    o = t
    for a, b in pairs:
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:56])); continue
        t = t.replace(a, b, 1); print('  [OK]   %s :: %r' % (rel, a[:56]))
    if t != o:
        write(rel, t)


def ensure_block(rel, block, anchor, label):
    """保证 block 在 rel 里**恰好出现一次**：已重复则折叠成一份，缺失则插在 anchor 行之后。

    为什么不用 `edit()`：`replace(anchor, anchor+block)` 属**追加型替换**，anchor 不消失
    → 每跑一次多插一份（本层实测把 SKILL.md 规则表行与 library/README 清单行各插成两份）。
    故改为「折叠 + 完成判据」写法。"""
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
        print('  [SAME] %s :: %s 已在位' % (rel, label))
        return
    write(rel, t)


# ---------------------------------------------------------------- 1) 规则文件
print('== 1) 写 %s ==' % RULE_REL)
cur = read(RULE_REL)
if cur == RULE:
    print('  [SAME] 内容一致，跳过')
else:
    write(RULE_REL, RULE)
    print('  [WROTE] %s（%d 字节）' % (RULE_REL, len(RULE.encode('utf-8'))))

# ---------------------------------------------------------------- 2) 20 域接线
print('== 2) 20 个 _domain.md 执行顺序接线 ==')
doms = sorted(d for d in os.listdir(os.path.join(ROOT, 'domains'))
              if os.path.isdir(os.path.join(ROOT, 'domains', d)))
wired = 0
for d in doms:
    rel = 'domains/%s/_domain.md' % d
    t = read(rel)
    if t is None:
        print('  [SKIP] %s' % rel); continue
    if WIRE_MARK in t:
        wired += 1; continue
    m = re.search(r'^##\s*⚠️\s*红线', t, re.M)
    if not m:
        print('  [MISS] %s :: 未找到「## ⚠️ 红线」锚点' % rel); continue
    t2 = t[:m.start()].rstrip('\n') + '\n' + WIRE + '\n\n' + t[m.start():]
    write(rel, t2)
    wired += 1
    print('  [OK]   %s' % rel)
print('  已接线域数：%d / %d' % (wired, len(doms)))


def renumber_order(t):
    """把 `## 执行顺序` 段内序号归一为 0..N。

    **为什么需要**：历史层 `step10_de_external.py`（第 2 层）里有一句
    `re.sub(r'^5\\. ', '4. ', t2, count=1, flags=re.M)` —— 那是当年「删库外步骤 4、把原步骤 5 收成 4」
    用的一次性补丁。本层新增了「第 5 步（自迭代）」，于是 step10 会把**新加的那一步**改成 `4.`
    → 出现两个 `4.`（实测：全链第 1 遍改动 20 个 `_domain.md`、并把重号留在了产物里）。
    按本包铁律「**不改历史层**，收敛/修复一律新增一层」，改由本层（更靠后）把序号收敛回 0..N。"""
    m = re.search(r'^(## 执行顺序[^\n]*\n)(.*?)(?=^## )', t, re.M | re.S)
    if not m:
        return t
    out, i = [], 0
    for ln in m.group(2).split('\n'):
        if re.match(r'^\d+\.\s', ln):
            out.append(re.sub(r'^\d+\.', '%d.' % i, ln, count=1))
            i += 1
        else:
            out.append(ln)
    return t[:m.start()] + m.group(1) + '\n'.join(out) + t[m.end():]


print('== 2b) 执行顺序序号归一（抵消 step10 的 `5.`→`4.` 补丁）==')
n_ren = 0
for d in doms:
    rel = 'domains/%s/_domain.md' % d
    t = read(rel)
    if t is None:
        continue
    t2 = renumber_order(t)
    if t2 != t:
        write(rel, t2)
        n_ren += 1
        print('  [FIX]  %s' % rel)
print('  序号归一 %d 个域（0 = 已规范）' % n_ren)

# ---------------------------------------------------------------- 3) library/README.md
print('== 3) library/README.md 登记 ==')
ensure_block(
    'library/README.md',
    '- `skill-evolution.md` —— 习惯自迭代：按用户习惯**只改可改段**（执行步骤 / 判定细则 / 示例说明）的非结构性迭代机制',
    '- `general-fallback.md` —— 通用兜底框架：**需求未命中任何 skill / 域时**仍产出有效结果的六步框架',
    '职责清单行')

# ---------------------------------------------------------------- 4) 包根 SKILL.md
print('== 4) 包根 SKILL.md：规则表 + 工作流 ==')
edit('SKILL.md', [
    ('## 五份规则文件（1 级库的本体）', '## 六份规则文件（1 级库的本体）'),
    ('  ↓ ⑦归档      library/memory.md             写学习档案（F3/F5 敏感域除外）\n```',
     '  ↓ ⑦归档      library/memory.md             写学习档案（F3/F5 敏感域除外）\n'
     '  ↓ ⑧自迭代    library/skill-evolution.md    按习惯只在可改段内迭代（不满足触发条件则不迭代）\n```'),
])
ensure_block(
    'SKILL.md',
    '| `library/skill-evolution.md` | 习惯自迭代：**只改可改段**（执行步骤 / 判定细则 / 示例说明），不改红线 / 输出契约 / 任何事实 |',
    '| `library/login-policy.md` | 登录选择原则：A/B/C 三档 + 标准话术 + 安全保障 |',
    '规则表行')

# ---------------------------------------------------------------- 5) qihang.sh 列表
print('== 5) scripts/qihang.sh status 列表 ==')
edit('scripts/qihang.sh', [
    ('  for f in library/README.md library/clarity.md library/domain-review.md library/output-spec.md \\\n'
     '           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md; do',
     '  for f in library/README.md library/clarity.md library/domain-review.md library/output-spec.md \\\n'
     '           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md \\\n'
     '           library/skill-evolution.md; do'),
])

# ---------------------------------------------------------------- 6) selfcheck REQ
print('== 6) scripts/selfcheck.sh REQ ==')
ensure_block('scripts/selfcheck.sh', 'library/skill-evolution.md',
             'library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md',
             'REQ 必备文件行')

# ---------------------------------------------------------------- 7) regress.sh 新增 [8] 段
print('== 7) scripts/regress.sh：新增 [8] 自迭代边界 段 ==')
S8 = '''  echo "[8] 自迭代边界（习惯自迭代只可改「可改段」）"
  _ev="library/skill-evolution.md"
  if [ -f "$_ev" ]; then _ok "自迭代规则文件在位"; else _fail "缺 library/skill-evolution.md"; fi
  # 三目标必须明文（否则机制退化成泛泛而谈）
  for _g in '优化思考速度' '精准化信息获取' '减少 AI 幻觉'; do
    if grep -q "$_g" "$_ev" 2>/dev/null; then _ok "已声明目标：$_g"
    else _fail "未声明目标：$_g"; fi
  done
  # 可改段 / 禁改段两张清单必须在位
  grep -q '§2.1 可改段' "$_ev" 2>/dev/null && _ok "可改段清单在位" || _fail "缺可改段清单"
  grep -q '§2.2 禁改段' "$_ev" 2>/dev/null && _ok "禁改段清单在位" || _fail "缺禁改段清单"
  # 禁改项必须逐条点名（红线 / 输出 / 失败与降级 / 分工 / frontmatter / 事实）
  for _b in '## ⚠️ 红线' '## 输出' '## 失败与降级' '## 与同域其他库内 skill 的分工' 'frontmatter' '任何事实'; do
    if grep -qF "$_b" "$_ev" 2>/dev/null; then _ok "禁改项已点名：$_b"
    else _fail "禁改项未点名：$_b"; fi
  done
  # 习惯画像必须明确「不随包」，且包内不得出现习惯数据
  grep -q '不随包' "$_ev" 2>/dev/null && _ok "习惯画像声明不随包分发" || _fail "未声明习惯画像不随包"
  # 20 域执行顺序必须全部接上自迭代规则
  _w=$(grep -rl 'library/skill-evolution.md' domains/*/_domain.md 2>/dev/null | wc -l | tr -d ' ')
  _chk "已接线自迭代的域数" "$_w" 20
  # 判定不可被习惯影响（合规优先于速度）
  grep -q '不影响' "$_ev" 2>/dev/null && grep -q '红线优先' "$_ev" 2>/dev/null \\
    && _ok "已声明「习惯不影响判定 / 红线优先」" || _fail "未声明判定不受习惯影响"
  # 规则文件不得引用**只在源仓库存在**的路径（生成器链不随包分发 → 副本会判失效引用）
  if grep -q 'scripts/_build' "$_ev" 2>/dev/null; then
    _fail "规则文件引用了不随包分发的生成器路径（scripts/_build）→ 交付副本会判失效引用"
  else _ok "规则文件未引用生成器路径（副本安全）"; fi
  echo "=========================================="
  echo ""
  r=$((r + 1))
done

echo "回归测试完毕'''
# 插入 [8] 段：用**完成判据**（[8] 标题在位即跳过），避免「追加型替换」重复插入
_TAIL = '  echo "=========================================="\n  echo ""\n  r=$((r + 1))\ndone\n\necho "回归测试完毕'
_rg = read('scripts/regress.sh')
if _rg is None:
    print('  [SKIP] scripts/regress.sh（不存在）')
elif 'echo "[8] 自迭代边界' in _rg:
    print('  [SAME] scripts/regress.sh :: [8] 段已存在，跳过')
elif _TAIL in _rg:
    write('scripts/regress.sh', _rg.replace(_TAIL, S8 + _TAIL, 1))
    print('  [OK]   scripts/regress.sh :: 已插入 [8] 自迭代边界 段')
else:
    print('  [MISS] scripts/regress.sh :: 未找到插入锚点（汇总尾部）')

# ---------------------------------------------------------------- 8) runcheck L2b 断言
print('== 8) scripts/runcheck.py：L2b 增加自迭代接线断言 ==')
ensure_block(
    'scripts/runcheck.py',
    "        if 'library/skill-evolution.md' not in order:\n"
    "            bad(dmf, '执行顺序未接自迭代规则 library/skill-evolution.md')",
    "            bad(dmf, '执行顺序仍含库外通道（应为库内唯一）')",
    'L2b 自迭代接线断言')

print('done')
