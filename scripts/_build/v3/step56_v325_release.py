# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 第 19 层 · v3.2.5 工程化迭代（诊断驱动 · 最小改动）】
# 依据：对 v3.2.4 树的**只读诊断**（9 条失败模式 FM-1…FM-9），每条改动都对应一条失败模式。
# 用法：python scripts/_build/v3/step56_v325_release.py [仓库根]
# 幂等：
#   · 内容补丁为「整段替换 + 目标态守卫」——目标态已存在即 SAME，不重复插入；
#   · 版本号用 **全部替换**（replace(a,b)，绝不 count=1）——本项目两次踩过「只换首处」的坑；
#   · 新增文件先判存在，一致即 SAME，不一致则 WARN 不覆盖。
#
# 本轮改动（对应交付物《迭代方案-v3.2.5》§2 失败归因表）：
#   FM-1  dlut-read.sh：隔离前置 + 隔离校验 + 新增 rc=5              （P0 安全）
#   FM-2  dlut-read.sh：L3 补「插入型变体」共现规则（只收紧）          （P1 安全）
#   FM-3  scripts/metrics.py 新增 + selfcheck 埋点/隔离/L3 断言       （P1 可观测）
#   FM-4  aligncheck.py：版本期望值改为从 config.yaml 派生            （P0 发布）
#   FM-5  roommate-mediate：步骤 5 去掉「信息库未收录的入口」          （P1 知识）
#   FM-6  F7 域边界：去空洞覆盖 + 明示降级                           （P1 规划）
#   FM-7  _registry：引用行接线「并列双诉求」                         （P2 路由）
#   FM-8  INSTALL.md §四：悬空引用修正（方案 A）                      （P0 交付）
#   FM-9  发布工艺（影子/灰度/门禁/回滚）见交付物 RUNBOOK.md —— 不随包，不进本层
#   P9    修订号 3.2.4 → 3.2.5（92 库内 skill + 4 处字段 + 1 份规范）
#   ※ 不放宽任何既有断言；不新增/删除域或 skill；不改阈值与任何事实。
# -------------------------------------------------------------------------------
import os, io, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD, NEW, PKG = '3.2.4', '3.2.5', '3.2'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t):
    io.open(os.path.join(ROOT, rel), 'w', encoding='utf-8', newline='').write(t)


def edit(rel, pairs):
    """整段替换。

    pairs 元素可为 (旧串, 新串) 或 (旧串, 新串, **哨兵**)。
    哨兵用于**插入型**改动：只要哨兵已在文件里就判 SAME（幂等）。
    为什么必须有它（本轮实测踩到）：插入块的**内容**一旦调整，`新串 in 文件` 不再成立，
    而旧串仍在 → 会**再插一份**（本项目已第四次踩「追加型替换复发」）。
    所以凡「插入新段落」的改动，一律给哨兵，守卫判据不看整块内容。
    """
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel); return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r（哨兵已存在）' % (rel, sent[:40])); continue
        if b in t:
            print('  [SAME] %s :: %r' % (rel, a[:44])); continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:44])); continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:44]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    """**全部替换**（同一字面量出现多次时必须用它）。"""
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


def add_file(rel, body):
    p = os.path.join(ROOT, rel)
    if os.path.isfile(p):
        cur = io.open(p, 'r', encoding='utf-8').read()
        if cur == body:
            print('  [SAME] %s（内容一致）' % rel)
        else:
            print('  [WARN] %s 已存在且内容不同 —— 不覆盖（需人工确认）' % rel)
        return
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    io.open(p, 'w', encoding='utf-8', newline='\n').write(body)
    print('  [NEW]  %s（%d 字节）' % (rel, len(body.encode('utf-8'))))


# ================================================================================
# FM-1 · dlut-read.sh：隔离前置 + 隔离校验 + rc=5
# ================================================================================
print('== FM-1) dlut-read.sh：隔离前置 + 隔离校验 + rc=5 ==')
edit('scripts/dlut-read.sh', [
    ('# 授权分级：L1 直接读 | L2 需 --yes 确认 | L3 一律拒绝\nset -uo pipefail',
     '# 授权分级：L1 直接读 | L2 需 --yes 确认 | L3 一律拒绝\n'
     '# 退出码：0 成功或 L1 | 1 用法错误或需区分 | 2 L2 未确认 | 3 L3 拒绝 | 4 未装 agent-browser | 5 隔离校验失败\n'
     'set -uo pipefail'),
    ('  echo "[dry-run] 将执行："\n'
     '  echo "  1) $AB open <入口> --headed --profile \\"$PROFILE_DIR\\""',
     '  echo "[dry-run] 将执行："\n'
     '  echo "  0) $AB close --all           # 先清既有会话，保证下一步 --profile 不被忽略"\n'
     '  echo "  1) $AB open <入口> --headed --profile \\"$PROFILE_DIR\\""'),
    ('echo "▶ 打开入口（若未登录，请在弹出的窗口里自行登录）..."\n'
     '$AB open "$URL" --headed --profile "$PROFILE_DIR" 2>&1 | head -5',
     '# ---------- 隔离前置：先关掉既有 daemon 会话（否则 --profile 会被静默忽略） ----------\n'
     '$AB close --all >/dev/null 2>&1 || true\n'
     '\n'
     'echo "▶ 打开入口（若未登录，请在弹出的窗口里自行登录）..."\n'
     'OPEN_OUT="$($AB open "$URL" --headed --profile "$PROFILE_DIR" 2>&1 | head -20)"\n'
     'echo "$OPEN_OUT"\n'
     '\n'
     '# ---------- 隔离校验：--profile 必须真的生效（失效即中止，不在未隔离窗口继续读）----------\n'
     'PROFILE_BASE="$(basename "$PROFILE_DIR")"\n'
     'if printf \'%s\' "$OPEN_OUT" | grep -qiE \'profile[[:space:]]+ignored|daemon already running\'; then\n'
     '  cat >&2 <<EOF\n'
     '❌ 中止：本次会话未使用独立 Profile（检测到 profile 被忽略 / daemon 已在运行）。\n'
     '   隐私隔离已失效，不继续读取。请先执行：$AB close --all，再重跑本命令。\n'
     'EOF\n'
     '  exit 5\n'
     'fi\n'
     'if printf \'%s\' "$OPEN_OUT" | grep -qF "$PROFILE_BASE"; then\n'
     '  echo "隔离校验: ✅ 独立 Profile 已生效（$PROFILE_DIR）"\n'
     'else\n'
     '  echo "隔离校验: ⚠️ 浏览器未回显 Profile 路径，无法从输出直接确认；"\n'
     '  echo "          已通过「打开前 close --all」保证无既有会话可复用（凭据隔离成立）。"\n'
     'fi',
     '隔离校验：--profile 必须真的生效'),
])

# ================================================================================
# FM-2 · dlut-read.sh：L3 插入型变体（共现规则）
# ================================================================================
print('== FM-2) dlut-read.sh：L3 插入型变体 ==')
edit('scripts/dlut-read.sh', [
    ('for _k in $L3_KEYS; do\n'
     '  case "$TARGET" in *"$_k"*) L3_HIT="$_k"; break ;; esac\n'
     'done\n'
     'if [ -n "$L3_HIT" ]; then',
     'for _k in $L3_KEYS; do\n'
     '  case "$TARGET" in *"$_k"*) L3_HIT="$_k"; break ;; esac\n'
     'done\n'
     '# ---------- 类 B：宽松名词 × 明细语义（**共现**才判 L3，避免误伤公开信息）----------\n'
     '# 只「收紧」不「放松」：不删除既有词，也不改 rc 语义。\n'
     '# 反向保护：单说「心理咨询讲座」「成绩公布时间」等公开信息**不得**被拦。\n'
     'if [ -z "$L3_HIT" ]; then\n'
     '  case "$TARGET" in\n'
     '    *心理*)\n'
     '      case "$TARGET" in *记录*|*档案*|*测评结果*) L3_HIT="心理·插入型变体" ;; esac ;;\n'
     '  esac\n'
     'fi\n'
     'if [ -z "$L3_HIT" ]; then\n'
     '  case "$TARGET" in\n'
     '    *成绩*)\n'
     '      case "$TARGET" in *明细*|*单科*|*分数*|*绩点*) L3_HIT="成绩·插入型变体" ;; esac ;;\n'
     '  esac\n'
     'fi\n'
     'if [ -n "$L3_HIT" ]; then',
     '类 B：宽松名词 × 明细语义'),
    # 类 B-3：「各科」×「分数 / 得分」——补「成绩」二字被省略、但语义仍是本人明细的写法
    # （如「各科分数」不含「成绩」，类 B-2 抓不到；实测 rc=1 → 应 rc=3）
    ('      case "$TARGET" in *明细*|*单科*|*分数*|*绩点*) L3_HIT="成绩·插入型变体" ;; esac ;;\n'
     '  esac\n'
     'fi\n'
     'if [ -n "$L3_HIT" ]; then',
     '      case "$TARGET" in *明细*|*单科*|*分数*|*绩点*) L3_HIT="成绩·插入型变体" ;; esac ;;\n'
     '  esac\n'
     'fi\n'
     'if [ -z "$L3_HIT" ]; then\n'
     '  case "$TARGET" in\n'
     '    *各科*)\n'
     '      case "$TARGET" in *分数*|*得分*|*成绩单*|*明细*) L3_HIT="各科·插入型变体" ;; esac ;;\n'
     '  esac\n'
     'fi\n'
     'if [ -n "$L3_HIT" ]; then',
     '类 B：宽松名词 × 明细语义'),
])

# ================================================================================
# FM-2 (续) · regress.sh：L3 共现规则的行为断言（2 正 + 2 反）
# ================================================================================
print('== FM-2) regress.sh：L3 共现规则行为断言 ==')
edit('scripts/regress.sh', [
    ('成绩|1\n邮件|1"',
     '成绩|1\n邮件|1\n'
     '心理咨询记录|3\n各科分数|3\n'
     '心理咨询讲座时间|1\n成绩公布时间|1"',
     '心理咨询记录|3'),
])

# ================================================================================
# FM-1 (续) · negative_test.py：新增第 7 类注入「隔离校验缺失」
# ================================================================================
print('== FM-1) negative_test.py：隔离校验缺失注入 ==')
edit('scripts/negative_test.py', [
    ('def inject_missing_fallback(tree):',
     "def inject_no_isolation(tree):\n"
     "    \"\"\"移除隔离前置与隔离校验，模拟「--profile 可被 daemon 静默忽略」的回归。\n"
     "    期望：selfcheck [7c] 断言 FAIL（证明该断言不是装饰）。\"\"\"\n"
     "    p = os.path.join(tree, 'scripts', 'dlut-read.sh')\n"
     "    t = io.open(p, encoding='utf-8').read()\n"
     "    out, skipping = [], False\n"
     "    for ln in t.split('\\n'):\n"
     "        if 'close --all >/dev/null 2>&1 || true' in ln:\n"
     "            out.append('')\n"
     "            continue\n"
     "        if 'grep -qiE' in ln and 'profile' in ln:\n"
     "            skipping = True\n"
     "        if skipping:\n"
     "            if ln.strip() == 'fi':\n"
     "                skipping = False\n"
     "            continue\n"
     "        out.append(ln)\n"
     "    return [p], '\\n'.join(out)\n"
     "\n"
     "\n"
     "def inject_missing_fallback(tree):",
     'def inject_no_isolation(tree):'),
    ("        ('生成器段重复插入（同一行两份）', inject_dup_row,\n"
     "         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),",
     "        ('生成器段重复插入（同一行两份）', inject_dup_row,\n"
     "         ['@py', 'scripts/aligncheck.py', '.'], 'aligncheck'),\n"
     "        ('隔离校验缺失（--profile 可被 daemon 静默忽略）', inject_no_isolation,\n"
     "         ['@bash', 'scripts/selfcheck.sh'], 'selfcheck [7c]'),",
     '隔离校验缺失（--profile 可被 daemon 静默忽略）'),
])

# ================================================================================
# FM-3 · scripts/metrics.py（新增）+ selfcheck 的 4 条新断言 + REQ 登记
# ================================================================================
print('== FM-3) scripts/metrics.py 新增 ==')
_tpl = os.path.join(HERE, 'metrics_template.py')
_body = io.open(_tpl, 'r', encoding='utf-8').read() if os.path.isfile(_tpl) else None
if _body is None:
    print('  [MISS] 缺 metrics_template.py（应与本层同目录）')
else:
    add_file('scripts/metrics.py', _body)

print('== FM-3/FM-1/FM-2) selfcheck.sh：REQ + [7c] 四条断言 ==')
edit('scripts/selfcheck.sh', [
    ('scripts/checkall.py scripts/negative_test.py"',
     'scripts/checkall.py scripts/negative_test.py scripts/metrics.py"'),
])
edit('scripts/selfcheck.sh', [
    ('# ---------- 8. 计数 ----------',
     '# ---------- 7c. 隔离 / L3 判级 / 指标埋点（v3.2.5 新增）----------\n'
     '# 依据：FM-1（隔离可被静默绕过）/ FM-2（L3 插入型变体失配）/ FM-3（零可观测）。\n'
     '# 这四条断言的作用是把「承诺」变成「可判 FAIL 的检查」，而不是装饰性描述。\n'
     'echo "[7c] 隔离 / L3 判级 / 指标埋点"\n'
     '_iso1=$(grep -c \'close --all >/dev/null 2>&1 || true\' scripts/dlut-read.sh 2>/dev/null); _iso1=${_iso1:-0}\n'
     '[ "$_iso1" -ge 1 ] && ok "私密站读取前先关闭既有会话（隔离前置）" \\\n'
     '  || bad "dlut-read.sh 缺隔离前置（--profile 可被 daemon 静默忽略）"\n'
     '_iso2=$(grep -cE \'profile\\[\\[:space:\\]\\]\\+ignored\' scripts/dlut-read.sh 2>/dev/null); _iso2=${_iso2:-0}\n'
     '_iso3=$(grep -c \'^  exit 5$\' scripts/dlut-read.sh 2>/dev/null); _iso3=${_iso3:-0}\n'
     '[ "$_iso2" -ge 1 ] && [ "$_iso3" -ge 1 ] \\\n'
     '  && ok "隔离校验生效（扫描 ignored 警告 + rc=5 中止）" \\\n'
     '  || bad "dlut-read.sh 缺隔离校验（警告扫描 $_iso2 / rc=5 $_iso3）"\n'
     '_l3b=$(grep -c \'插入型变体\' scripts/dlut-read.sh 2>/dev/null); _l3b=${_l3b:-0}\n'
     '[ "$_l3b" -ge 3 ] && ok "L3 类 B 共现规则齐备（$_l3b 条）" \\\n'
     '  || bad "L3 类 B 共现规则不足（$_l3b 条，期望 ≥3）"\n'
     '_mt1=$(grep -c \'"leak":\' scripts/metrics.py 2>/dev/null); _mt1=${_mt1:-0}\n'
     '_mt2=$(grep -c \'QIHANG_TRACE\' scripts/metrics.py 2>/dev/null); _mt2=${_mt2:-0}\n'
     '[ "$_mt1" -ge 1 ] && [ "$_mt2" -ge 1 ] \\\n'
     '  && ok "指标脚本就位（机制字段埋点 + 可一键关闭）" \\\n'
     '  || bad "指标脚本缺埋点字段或开关（$_mt1 / $_mt2）"\n'
     '\n'
     '# ---------- 8. 计数 ----------',
     '[7c] 隔离 / L3 判级 / 指标埋点'),
])

# ================================================================================
# FM-4 · aligncheck.py：版本期望值改为从 config.yaml 派生（消除 10 处字面量）
# ================================================================================
print('== FM-4) aligncheck.py：版本期望值派生 ==')
edit('scripts/aligncheck.py', [
    ("def rd(p):\n"
     "    with open(p, 'r', encoding='utf-8', errors='replace') as fh:\n"
     "        return fh.read()\n",
     "def rd(p):\n"
     "    with open(p, 'r', encoding='utf-8', errors='replace') as fh:\n"
     "        return fh.read()\n"
     "\n"
     "# ---------- 版本号：**单一真相源 = config.yaml**（v3.2.5 起，勿再写死字面量）----------\n"
     "# 为什么改：修订号字面量曾硬编码在 101 个文件 / 120 处，其中本文件 10 处；\n"
     "# 两次迭代各因「同一字面量多处出现、只换首处」而报出自相矛盾的 FAIL。\n"
     "# 现在改版本只需改 config.yaml 一处 + 生成器全量替换，断言强度不变。\n"
     "_cv = re.search(r'^version:\\s*([\\d.]+)', rd('config.yaml'), re.M) if os.path.isfile('config.yaml') else None\n"
     "REV = _cv.group(1) if _cv else '3.2.5'      # 修订号（三位，用于字段与断言）\n"
     "PKG = '.'.join(REV.split('.')[:2])          # 包版本（两位，用于展示位）\n"),
    ("if vm and vm.group(1) != '3.2.4':", "if vm and vm.group(1) != REV:"),
    ("bad(f, '版本号 %s（期望 3.2.4）' % vm.group(1))",
     "bad(f, '版本号 %s（期望 %s）' % (vm.group(1), REV))"),
    ("if vers - {'3.2.4'}:", "if vers - {REV}:"),
    ("if pv != '3.2.4':", "if pv != REV:"),
    ("bad('.codebuddy-plugin/plugin.json', 'version = %s（期望 3.2.4）' % pv)",
     "bad('.codebuddy-plugin/plugin.json', 'version = %s（期望 %s）' % (pv, REV))"),
    ("if m and m.group(1) not in ('3.2', '3.2.4'):",
     "if m and m.group(1) not in (PKG, REV):"),
    ("bad(_vf, '版本声明 %s（期望包版本 3.2 或修订号 3.2.4）' % (m.group(1), '3.2', '3.2.4'))",
     "bad(_vf, '版本声明 %s（期望包版本 %s 或修订号 %s）' % (m.group(1), PKG, REV))"),
    ("    # 版本号口径（v3.2 起统一）：包版本 = 两位（3.2）｜修订号 = 三位（3.2.4）",
     "    # 版本号口径（v3.2 起统一）：包版本 = 两位（前两位）｜修订号 = 三位（见 config.yaml）"),
    ("if '3.2.4' not in v:", "if REV not in v:"),
    ("warn('.codebuddy-plugin/plugin.json', '未声明版本 3.2.4')",
     "warn('.codebuddy-plugin/plugin.json', '未声明版本 %s' % REV)"),
])

# ================================================================================
# FM-5 · roommate-mediate 步骤 5
# ================================================================================
print('== FM-5) roommate-mediate 步骤 5 ==')
edit('domains/F3-wellbeing/skills/local/roommate-mediate/SKILL.md', [
    ('5. 约定试行期与复盘时间，必要时给辅导员介入入口',
     '5. 约定试行期与复盘时间；需要辅导员 / 学工介入时，**不得编造联系方式** ——\n'
     '   按本包固定口径回复「信息库未收录，建议访问 https://www.dlut.edu.cn/ 核实」，\n'
     '   并给出**所在学院官网 + 学生工作部门**两个已核验入口（见 `references/dlut-official-sites.md`），\n'
     '   由用户自行查号。'),
])

# ================================================================================
# FM-6 · F7 域边界
# ================================================================================
print('== FM-6) F7 域边界 ==')
edit('domains/F7-further-study/_domain.md', [
    ('- **不覆盖**：不写文书代笔（只给结构与自查）；不求职（→F8）；升学类面试与材料 → 本域（考研复试属本域，非 `F8`）',
     '- **不覆盖**：不写文书代笔（只给结构与自查）；不求职（→F8）；升学类**材料与时间线** → 本域（考研复试属本域，非 `F8`）\n'
     '- **本域无对口 skill 的场景**（升学面试的**模拟问答 / 追问演练**）：按 `library/general-fallback.md` §3\n'
     '  用**本域通用框架**承接（面试流程 · 评分维度 · 材料核验），**明确标注降级**，不假装覆盖；\n'
     '  **不**改锁到求职面试域（语境错配）。'),
])

# ================================================================================
# FM-7 · _registry 「引用」消歧行
# ================================================================================
print('== FM-7) _registry 引用消歧 ==')
edit('domains/_registry.md', [
    ('要**降重/规避查重** → `R5`（红线） |',
     '要**降重/规避查重** → `R5`（红线）。**并列双诉求**（如「查重没过，顺便把引用格式也改一遍」）→ '
     '先按 `R5` 给**规范与自查**（红线只禁「代改以规避查重」，给规范**不拦**），再按 `S5` 给格式规范，'
     '**两域结论并列输出** —— 不得因其中之一涉红线就整体沉默（对齐 `library/output-spec.md` §2「混合请求」） |'),
])

# ================================================================================
# FM-8 · INSTALL.md §四（方案 A）
# ================================================================================
print('== FM-8) INSTALL.md §四 ==')
edit('INSTALL.md', [
    ('1. 场景设计书（五要素齐备）',
     '1. 场景设计书（五要素齐备）—— **随赛事材料单独提交，本包不附带该文件**'),
])

# ================================================================================
# P4 · 根 SKILL.md
# ================================================================================
print('== P4) 根 SKILL.md ==')
edit('SKILL.md', [
    ('> 判据：`explain-stepwise` 这类 **单点** skill 不得直接承接**整门课 / 整本书**级需求。',
     '> 判据：`explain-stepwise` 这类 **单点** skill 不得直接承接**整门课 / 整本书**级需求。\n'
     '\n'
     '> **⑧ 之后、结束本次会话前**：按 `scripts/metrics.py` 的 trace 规范追加 **1 行**记录\n'
     '> （格式见该脚本头部注释）。**埋点失败不得影响交付** —— 记不到就跳过，**不得**因此中断、\n'
     '> 也**不得**向用户展示埋点内容。详见「硬规则 5」。',
     '按 `scripts/metrics.py` 的 trace 规范追加'),
    ('| 一键脚本 | `bash scripts/qihang.sh {status\\|platform\\|domains\\|registry\\|new-term}` |',
     '| 一键脚本 | `bash scripts/qihang.sh {status\\|platform\\|domains\\|registry\\|new-term}` |\n'
     '| 指标与门禁 | `python scripts/metrics.py report`（读本机 trace → 成功率 / 追问率 / 降级率 / 红线拦截率 / P95 耗时）'
     '｜`python scripts/metrics.py check`（对发布门禁阈值做 PASS/FAIL 判定） |\n'
     '\n'
     '> trace 目录位于**用户运行环境**（`~/.qihang/trace/`），**不随包分发**；包内只有记录格式与解析器。',
     '| 指标与门禁 |'),
    ('3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件（见 `references/dlut-login-sites.md`）。\n'
     '4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心。',
     '3. **私密站只读**：涉及需登录站点时，只读、不外传、不写入文件（见 `references/dlut-login-sites.md`）。\n'
     '   - **独立 Profile 必须校验生效**：`scripts/dlut-read.sh` 在打开入口前**先关闭全部既有会话**，'
     '并在打开后校验输出中**未出现**「profile ignored / daemon already running」类警告；'
     '出现即**立即中止**（`rc=5`），**不得**在未隔离的窗口里继续读取。\n'
     '4. **F3 域红线**：不做心理诊断、不做危机干预；识别危机信号立即转介心理中心。\n'
     '5. **指标埋点（本机、最小、可关）**：每次会话结束追加 **1 行** trace（格式见 `scripts/metrics.py` 头部），'
     '只记**机制字段** —— 域 ID / 澄清判定档 / 是否降级 / 是否命中红线 / 各阶段耗时 / 是否被用户纠正。\n'
     '   - **禁止**记录：用户原话、产出正文、任何敏感域（F3 / F5）内容、第三方隐私、任何 URL 与凭证。\n'
     '   - 埋点在**用户运行环境**（`~/.qihang/trace/`，**不随包分发**）；用户可用 `QIHANG_TRACE=0` 关闭。\n'
     '   - **埋点失败不得影响交付**：写不进去就跳过，**不得**因埋点报错而中断或降级输出。',
     '5. **指标埋点（本机、最小、可关）**'),
])

# ================================================================================
# P9 · 修订号 3.2.4 → 3.2.5（全部替换）
# ================================================================================
print('== P9) 修订号 %s → %s ==' % (OLD, NEW))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        if replace_all('domains/%s/skills/local/%s/SKILL.md' % (d, s), 'version: %s' % OLD, 'version: %s' % NEW):
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD, 'version: %s' % NEW),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD, '"version": "%s"' % NEW),
        ('config.yaml', 'version: %s' % OLD, 'version: %s' % NEW),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD, '**修订号 = `%s`**' % NEW),
        ('library/output-spec.md', '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % OLD,
         '（规则/工具变更 +1，如 `3.2.0` → `%s`）' % NEW),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s :: %r ×%d' % ('OK' if k else '--', rel, a[:44], k))

print('done')
