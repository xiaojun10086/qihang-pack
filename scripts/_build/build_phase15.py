#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」build_phase15 —— 复查修复层（v2.6 → v2.7）

只做「已被证伪」的修复，每条都对应复查报告里的一个可复现缺陷。
原则：
  · 每条修复是**精确匹配替换**；匹配不到就报告（说明文档已漂移，需人工看），不静默跳过
  · 幂等：重复运行结果一致
  · 修完打印「实测证据」，不靠自称

用法: python scripts/_build/build_phase15.py .
"""
import os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
OK, MISS, DONE = [], [], []

def rd(p):
    with open(os.path.join(ROOT, p), 'r', encoding='utf-8') as f:
        return f.read()

def wr(p, s):
    with open(os.path.join(ROOT, p), 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)

def rep(path, old, new, required=True, label=None, count=1):
    """精确替换；required=True 时匹配不到会记入 MISS

    幂等护栏：**当 new 包含 old 时**（即"在旧内容后追加"型替换），
    先判 new 是否已整体出现在文件里 —— 出现过就跳过，避免重复追加。

    退役护栏（与 phase16/17/18 对齐）：目标文件若已被后续提交删除
    （如 `PROJECT.md` / `ROADMAP.md`），记 MISS 并跳过，**不抛 FileNotFoundError**。
    """
    if not os.path.isfile(os.path.join(ROOT, path)):
        if required:
            MISS.append('%s :: %s（文件不存在）' % (path, (label or old)[:58]))
        return
    t = rd(path)
    label = label or (old.strip().splitlines() or ['?'])[0][:58]
    if old in new and new in t:
        DONE.append('[已是最新] %s :: %s' % (path, label))
        return
    if old not in t:
        if new in t or not required:
            DONE.append('[已是最新/已被后续替换] %s :: %s' % (path, label))
        else:
            MISS.append('%s :: %s' % (path, label))
        return
    t = t.replace(old, new, count if count > 0 else -1)
    wr(path, t)
    OK.append('%s :: %s' % (path, label))

def resub(path, pat, repl, label, required=True, flags=0):
    if not os.path.isfile(os.path.join(ROOT, path)):
        if required:
            MISS.append('%s :: %s（文件不存在）' % (path, label))
        return
    t = rd(path)
    t2, n = re.subn(pat, repl, t, flags=flags)
    if n == 0:
        MISS.append('%s :: %s（正则未命中）' % (path, label))
        return
    if t2 != t:
        wr(path, t2)
        OK.append('%s :: %s（%d 处）' % (path, label, n))
    else:
        DONE.append('[已是最新] %s :: %s' % (path, label))

# ==================================================================== 1. L3 门禁语义化
def fix_l3_gate():
    p = 'scripts/dlut-read.sh'
    old = '''# ---------- L3 禁止清单（先拦，绝不打开页面） ----------
case "$TARGET" in
  缴费|金额|银行卡|身份证|家庭信息|邮件正文|心理记录|成绩明细|简历)
    cat <<EOF
❌ 拒绝执行：目标「$TARGET」属于 L3 禁止读取级别。

「启航」私密站授权分级：
  L1 直接读   ：课表 / **成绩等级** / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态
  L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示 / 邮箱未读提示
  L3 一律拒绝 ：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细 / 成绩明细

请自行到 https://portal.dlut.edu.cn/ 查看；本工具不代读、不代操作。
EOF
    exit 3 ;;
esac'''
    new = '''# ---------- L3 禁止清单（**语义匹配**：先拦，绝不打开页面） ----------
# v2.7 修复：旧版用精确 case 匹配，导致「缴费金额」「银行卡号」「身份证号」「邮件内容」
# 这类**变体写法绕开拒绝分支**（落到 usage，退出码 1）。改为关键词包含匹配，闭合绕过面。
L3_KEYS="缴费 金额 银行卡 身份证 家庭信息 家庭 邮件正文 邮件内容 心理记录 成绩明细 成绩单 简历"
L3_HIT=""
for _k in $L3_KEYS; do
  case "$TARGET" in *"$_k"*) L3_HIT="$_k"; break ;; esac
done
if [ -n "$L3_HIT" ]; then
  cat <<EOF
❌ 拒绝执行：目标「$TARGET」属于 L3 禁止读取级别（命中关键词「$L3_HIT」）。

「启航」私密站授权分级：
  L1 直接读   ：课表 / 成绩等级 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态
  L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示
  L3 一律拒绝 ：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细

匹配口径：**关键词包含**（不再是精确等于）。含「简历」也一律拒绝（个人经历数据）。
请自行到 https://portal.dlut.edu.cn/ 查看；本工具不代读、不代操作。
EOF
  exit 3
fi'''
    rep(p, old, new, label='L3 门禁：精确匹配 → 语义关键词匹配')

# ==================================================================== 2. config.yaml 去重
def fix_config():
    rep('config.yaml',
        '    L1_auto: [课表 / 成绩等级 / 考试安排 / 借阅 / 一卡通余额 / 场馆预约状态 / 网费 / 日程, 网费, 日程]\n'
        '    L2_confirm: [资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示, 邮箱未读提示]\n'
        '    L3_forbidden: [缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细, 成绩明细]',
        '    # v2.7 修复：去掉生成器拼接残留的重复项（原为 "…网费, 网费, 日程"）\n'
        '    L1_auto: [课表, 成绩等级, 考试安排, 借阅, 一卡通余额, 场馆预约状态, 网费, 日程]\n'
        '    L2_confirm: [资助申请状态, 就业投递记录, 培养进度, 邮箱未读提示]\n'
        '    # 口径：成绩「等级/是否通过」可读；「明细」禁读（见 references/dlut-field-map.md）\n'
        '    L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录, 成绩明细]',
        label='去重 L1/L2/L3 列表')

# ==================================================================== 3. 三份 L3 清单去重
def fix_l3_lists():
    rep('references/dlut-field-map.md',
        '3. **L3 一律拒绝**：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细 / 成绩明细。',
        '3. **L3 一律拒绝**：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细。\n'
        '   匹配口径为**关键词包含**（见 `scripts/dlut-read.sh`），故「缴费金额」「银行卡号」等变体同样被拒。',
        label='L3 去重 + 匹配口径')
    rep('references/dlut-login-sites.md',
        '| **L3 禁止自动** | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细、成绩明细 | **方案 C**，只给入口不读取 |',
        '| **L3 禁止自动** | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细 | **方案 C**，只给入口不读取（关键词包含匹配） |',
        label='L3 去重')
    # L1 口径：把含糊的「成绩」改为「成绩等级」
    rep('references/dlut-login-sites.md',
        '| **L1 只读·自动** | 课表、成绩、考试安排、借阅、一卡通余额、场馆预约状态 | 方案 A，可直接读取 |',
        '| **L1 只读·自动** | 课表、**成绩等级（含是否通过）**、考试安排、借阅、一卡通余额、场馆预约状态、网费、日程 | 方案 A，可直接读取 |',
        label='L1 口径统一（成绩→成绩等级）')
    rep('library/SKILL.md',
        '| **L3 禁读** | 私密站 | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细 / 成绩明细 |',
        '| **L3 禁读** | 私密站 | 缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细（**关键词包含匹配，变体同样拦截**） |',
        label='L3 去重')

# ==================================================================== 4. 方案 A/C 与 L1/L2/L3 冲突
def fix_scheme_conflict():
    rep('references/dlut-login-sites.md',
        '| 9 | 就业信息网 | https://job.dlut.edu.cn/ | 招聘、宣讲会、投递记录 | F8 | 方案 A |',
        '| 9 | 就业信息网 | https://job.dlut.edu.cn/ | 招聘、宣讲会、投递记录 | F8 | 方案 A（投递记录属 **L2 需确认**） |',
        label='job 站 方案与级别对齐')
    rep('references/dlut-login-sites.md',
        '| 10 | 研究生系统 | https://gs.dlut.edu.cn/ | 培养、导师、开题 | R4 R5 F7 | 方案 A |',
        '| 10 | 研究生系统 | https://gs.dlut.edu.cn/ | 培养、导师、开题 | R4 R5 F7 | 方案 A（培养进度属 **L2 需确认**） |',
        label='gs 站 方案与级别对齐')
    rep('references/dlut-login-sites.md',
        '| 17 | 网络与信息化中心 | https://its.dlut.edu.cn/ | 网费、VPN、软件正版化 | R3 F1 | 方案 C |',
        '| 17 | 网络与信息化中心 | https://its.dlut.edu.cn/ | 网费、VPN、软件正版化 | R3 F1 | 方案 A（**网费属 L1**；涉账号类走方案 C） |',
        label='its 站 方案与级别对齐')
    rep('references/dlut-login-sites.md',
        '| 6 | 学生工作系统 | https://xsc.dlut.edu.cn/ | 资助、评奖、请假、第二课堂 | F1 F3 F4 F6 | 方案 A |',
        '| 6 | 学生工作系统 | https://xsc.dlut.edu.cn/ | 资助、评奖、请假、第二课堂 | F1 F3 F4 F6 | 方案 A（资助/评奖状态属 **L2 需确认**；**心理记录 L3 禁读**） |',
        label='xsc 站 方案与级别对齐')

# ==================================================================== 5. 澄清门逻辑漏洞
def fix_clarity_hole():
    p = 'library/clarity.md'
    rep(p,
        '**简记：关键槽齐 = 放行；关键槽缺 = 追问，`U` 只用于缺哪个槽时的取舍。**',
        '**简记（v2.7 加固）：关键槽「齐全且不歧义」= 放行；关键槽缺**或**出现歧义（`cᵢ = 0.5`）= 追问。**\n\n'
        '> **v2.7 修复的逻辑漏洞**：旧版「关键槽齐全即放行」只判「有没有」，不判「清不清楚」。\n'
        '> 反例：`O/T/D` 都填了但都是歧义（各 `cᵢ=0.5`）→ `U = 1 − (1.5×0.5×3)/6.1 = 0.63`，\n'
        '> 按旧版仍会**放行**，与「避免答错」目标相反。故补一条硬条件：\n'
        '> **关键槽判「已填」时必须 `cᵢ ≥ 0.8`（显式或唯一推断）；出现 `0.5` 视同「缺」，必须追问。**',
        label='关闭「关键槽齐全=放行」漏洞')
    rep(p,
        '2. **`O` `T` `D` 三关键槽位齐全** —— 缺 `W/C/B` 一律不追问',
        '2. **`O` `T` `D` 三关键槽位齐全且均 `cᵢ ≥ 0.8`** —— 缺 `W/C/B` 一律不追问；'
        '若某关键槽只有 `0.5`（歧义），**不适用本例外**，按 §3 追问',
        label='例外 2 加歧义条件')
    rep(p,
        '**例 B**「高数快挂了」',
        '**例 C（v2.7 新增 · 漏洞反例）**「帮我写点东西」\n\n'
        '| 槽位 | 判定 | cᵢ |\n|---|---|---|\n'
        '| O | 「东西」= 无具体对象 → 歧义 | 0.5 |\n'
        '| T | 「写」→ 可推断为写作，但导向 S3/S5 两域 | 0.5 |\n'
        '| D | 完全缺失 | 0.0 |\n\n'
        '`U = 1 − (0.75+0.75+0)/6.1 = 0.75 > 0.30`，且关键槽含歧义 → **必须追问**。\n'
        '若按旧版「三关键槽都非空」判，会误放行 —— 这正是 v2.7 要修掉的洞。\n\n'
        '**例 B**「高数快挂了」',
        label='新增漏洞反例')

# ==================================================================== 6. output-spec 算术与跨域自相矛盾
def fix_output_spec():
    p = 'library/output-spec.md'
    rep(p,
        '**标准输出 = 5 条**（依据+步骤+产物+下一步，缺省无假设）。仍有 1 条余量。',
        '**标准输出 = 4 条**（依据 + 步骤 + 产物 + 下一步；缺省无【假设】）。上限 6 条 → 仍有 **2 条余量**。\n\n'
        '> **v2.7 修复**：原文写「= 5 条」但列举的字段只有 4 个（【结论】按 §1.1 不计），\n'
        '> 属算术错误；余量应为 2 条而非 1 条。',
        label='修正要点计数算术（5→4，余量 1→2）')
    rep(p,
        '> **口径统一**：跨域时**各域结论计入要点数**（与 §1.1「除【结论】外的字段行」一致 ——\n'
        '> 此处每个域的结论即该域的【结论】字段，合并展示时计入）。4 域 + 清单 = 5 条 ✅；\n'
        '> **5 域须压缩**：把最弱的 1 条结论并入行动清单。',
        '> **口径统一**：跨域时**各域结论计入要点数**（每个域 1 条），行动清单另计 1 条。\n'
        '> 于是 **域数 + 1 ≤ 5**（把 1 条余量留给【假设】或【红线】）→ **域数上限 = 4**。\n'
        '> 4 域 + 清单 = 5 条 ✅；**5 域须压缩**：把最弱的 1 条结论并入行动清单。\n\n'
        '> **v2.7 修复**：原文一处写「上界 = 域数 + 1 ≤ 6 → 域数上限 = 5」，另一处写「5 域须压缩」，\n'
        '> 自相矛盾且会挤掉【假设】/【红线】条。现统一为**域数上限 = 4**，与 6 条上限、'
        '> 标准输出 4 条、以及 `e2e-scenarios.md` 演示 1（4 域）完全自洽。',
        label='修正跨域域数上限矛盾（5→4）')

# ==================================================================== 7. qihang.sh
def fix_qihang_sh():
    p = 'scripts/qihang.sh'
    rep(p,
        '  for f in library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md \\\n'
        '           library/memory.md library/domain-review-cases.md library/output-checklist.md; do',
        '  for f in library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md \\\n'
        '           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md; do',
        label='status 补漏 library/login-policy.md（8 个文件）')
    rep(p,
        'RECORDS_DIR_DEFAULT="${ROOT}/../.learnbuddy/memory/qihang"\n'
        '[ -d "${ROOT}/../.learnbuddy" ] || RECORDS_DIR_DEFAULT="${ROOT}/records"',
        '# v2.7 修复：安装到 ~/.learnbuddy/skills/qihang 时，ROOT/.. = ~/.learnbuddy/skills，\n'
        '# 旧式 "${ROOT}/../.learnbuddy/memory/qihang" 会解析成 ~/.learnbuddy/skills/.learnbuddy/... （错误路径）。\n'
        '# 现改为：优先工作区档案目录，其次平台技能目录旁，最后回落到包内 records/。\n'
        'RECORDS_DIR_DEFAULT=""\n'
        'for _c in "${ROOT}/../.learnbuddy/memory/qihang" "${ROOT}/../../memory/qihang" "${ROOT}/records"; do\n'
        '  case "$_c" in *"/skills/.learnbuddy/"*) continue ;; esac   # 排除已知错误拼接\n'
        '  if [ -d "$(dirname "$_c")" ]; then RECORDS_DIR_DEFAULT="$_c"; break; fi\n'
        'done\n'
        '[ -n "$RECORDS_DIR_DEFAULT" ] || RECORDS_DIR_DEFAULT="${ROOT}/records"',
        label='修正学习档案目录解析')
    rep(p,
        'R3|research-tools|egouilliard-leyton/python-tutor-skill|npx skills add egouilliard-leyton/python-tutor-skill',
        'R3|research-tools|mattpocock/skills|npx skills add mattpocock/skills@teach',
        label='R3 主候选对齐 external.md 首选（原为第 2 项）')

# ==================================================================== 8. 文档计数刷新
def fix_counts():
    rep('PROJECT.md',
        '| 三级结构               | ✅ 完成（125 文件，生成器驱动）',
        '| 三级结构               | ✅ 完成（生成器驱动 · 19 域 / **38 库内 skill** / **155+ 文件**）',
        label='文件数与结构口径（去硬编码数，防漂移）')
    rep('PROJECT.md',
        '| 19 域 + 19 库内 skill | ✅ **已产品化**：每域含可执行示例 + 4 域含安全护栏',
        '| 19 域 + **38 库内 skill** | ✅ **已产品化**：**每域 2 个**、均含可执行示例；4 空白域含安全护栏',
        label='库内 skill 19→38')
    rep('PROJECT.md',
        '| 越界用例集 / 输出校验清单     | ✅ 73 条用例· 7 项硬校验',
        '| 越界用例集 / 输出校验清单     | ✅ **22 条**用例（含 3 反例）· **7 项**硬校验',
        label='用例数 73→22')
    rep('PROJECT.md',
        '| DUT 公开信息库          | ✅ 73 条',
        '| DUT 公开信息库          | ✅ **160 条**表格行（✅ 69 / ⚠️ 26）',
        label='公开站 73→160')
    rep('PROJECT.md',
        '| DUT 私密站清单          | ✅ 73 站 + 方案 A',
        '| DUT 私密站清单          | ✅ **19 站** + 方案 A + L1/L2/L3',
        label='私密站 73→19')
    rep('PROJECT.md',
        '| **160 条**表格行（✅ 73 / ⚠️ 23 / 学院类 65），三校区 + 全部学院 + 职能部门 |',
        '| **160 条**表格行（✅ 69 / ⚠️ 26），三校区 + 全部学院 + 职能部门 |',
        label='公开站计数口径修正（73/23/65 → 69/26）')
    rep('PROJECT.md',
        '| 库外 skill 联调        | ✅ 安装通道实测可用（`npx skills add`）；合规自检完成',
        '| 库外 skill 联调        | ✅ 安装通道实测可用（`npx skills add`）；合规自检完成；**12 平台多源比对 v3**（`references/skill-matrix-v3.md`）',
        label='补记多源比对')
    rep('README.md',
        '**自查结果**：19 域 × 每域 1 个库内 skill = 19 个库内 skill；15 个域有库外候选；**4 个域为方向空白**（F3、F4、F5、F6），直接依赖库内自建 skill。',
        '**自查结果**：19 域 × 每域 **2 个**库内 skill = **38 个库内 skill**；**14 个域**有「合规且适配 DUT」的库外候选；'
        '**7 个域为纯自建**（F1、F3、F4、F5、F6、F7、R5 —— 库外要么许可证不清、要么环境错位）。详见 `references/skill-matrix-v3.md`。',
        label='README 自查结果刷新')
    rep('README.md',
        '│   ├── SKILL.md              库本体',
        '│   ├── SKILL.md              库本体\n│   ├── login-policy.md       登录选择原则（A/B/C 三档）',
        label='README 目录树补 login-policy')
    rep('README.md',
        '│   ├── skill-sources.md            12 个 skill 探测平台',
        '│   ├── skill-sources.md            12 个 skill 探测平台（含可达性实测）\n'
        '│   ├── skill-matrix-v3.md          **库外候选多源比对矩阵（19 域选优）**',
        label='README 目录树补 skill-matrix-v3')
    rep('README.md',
        '│   ├── validation-report.md        阶段 1/2 验收报告',
        '│   ├── validation-report.md        阶段 1/2 验收报告\n'
        '│   ├── review-report-v2.2.md      复查报告 v2.2\n'
        '│   ├── review-report-v2.3.md      复查报告 v2.3\n'
        '│   ├── review-report-v2.4.md      **复查报告 v2.4（本轮）**\n'
        '│   ├── stress-test-v3.md          **多轮压测报告**\n'
        '│   ├── browser-matrix.md / dlut-site-profiles.md / dlut-url-verification.md',
        label='README 目录树补 5 份未登记文档')
    rep('README.md',
        '```bash\nbash scripts/qihang.sh status     # 三级结构完整度',
        '```bash\nbash scripts/selfcheck.sh         # 结构与计数自检（v2.7 起 38 skill）\nbash scripts/audit.sh             # 安全审计 + L3 门禁实测\nbash scripts/qihang.sh status     # 三级结构完整度',
        label='README 补自检命令')
    rep('ROADMAP.md',
        '| — | **平台适配（横切）** | LearnBuddy 一等公民 | ✅ 已完成 |',
        '| — | **平台适配（横切）** | LearnBuddy 一等公民 | ✅ 已完成 |\n'
        '| **7** | **复查与扩库（v2.7）** | 库内 skill 19→**38** · **12 平台多源比对选优** · 复查修复 **52 项** · 多轮压测 | ✅ 已完成 |',
        label='ROADMAP 新增阶段 7')

# ==================================================================== 9. install / 平台说明
def fix_install():
    rep('INSTALL.md',
        '**期望**：`[1级] 7 个 library 文件 ✓`（逐行列出 SKILL + 6 份规则） · `[2级] 19 个域 / 19 个库内 skill ✓` · `[资源] DUT 公开站 160 行 ✓`',
        '**期望**：`[1级]` 逐行列出 **8 个** library 文件（SKILL + 7 份规则，含 `login-policy.md`） · '
        '`[2级] 19 个域 / **38 个**库内 skill` · `[资源] DUT 公开站 160 行`\n'
        '\n'
        '**完整验收（v2.7 起 4 个脚本，职责不重叠）**：\n'
        '\n'
        '| 脚本 | 管什么 | 期望 |\n'
        '|---|---|---|\n'
        '| `bash scripts/selfcheck.sh` | 结构对不对（计数 / 交叉引用 / 一致性） | `OK 31 ｜ WARN 0 ｜ FAIL 0 → 可交付` |\n'
        '| `bash scripts/audit.sh` | 安不安全（凭证 / 危险命令 / L3 门禁 / 合规） | `37 通过 ｜ 0 警告 ｜ 0 失败 → 通过` |\n'
        '| `bash scripts/regress.sh 3` | **行为对不对**（澄清门算例 / L3 门禁矩阵 / 红线一致性） | `120 项全 OK ｜ FAIL 0` |\n'
        '| `bash scripts/qihang.sh status` | 三级结构完整度 | 逐行 ✓ |',
        label='INSTALL 期望值修正 + 4 脚本验收表')

# ==================================================================== 10. e2e 修正
def fix_e2e():
    rep('references/e2e-scenarios.md',
        '| 槽位 | 值 | cᵢ |\n|---|---|---|\n| 槽位 | 值 | cᵢ | wᵢ |\n|---|---|---|---|\n',
        '| 槽位 | 值 | cᵢ | wᵢ |\n|---|---|---|---|\n',
        label='去掉重复表头行')
    rep('references/e2e-scenarios.md',
        '**② 锁定域** → **R1 文献检索** + **S5 学术表达**',
        '**② 锁定域** → **R1 文献检索** + **S5 学术表达**（域审查后追加 **R5 学术规范** 做引用/查重/AI 声明自查 → 共 3 域）',
        label='演示3 域锁定与执行域数对齐（2→3）')
    rep('references/e2e-scenarios.md',
        '`U ≈ 0.30` → **边界值，直接放行**（不追问，避免打扰）',
        '关键槽 `O/T/D` 齐全且无歧义（`cᵢ = 1.0`）→ 按 `clarity.md` §5 例外 2 **放行**（不追问，避免打扰）\n'
        '（原写「U ≈ 0.30 边界值放行」与 §3 的严格阈值口径易冲突，v2.7 改为按例外 2 判定）',
        label='演示2 放行理由改为按例外2')

# ==================================================================== 11. registry 消歧补漏
def fix_registry():
    rep('domains/_registry.md',
        '| **「求」类动词** | S1 | 「求推荐/求资源」不是 S1；仅「求解/求证」才属 `S1` |',
        '| **「求」类动词** | S1 | 「求推荐/求资源」不是 S1；仅「求解/求证」才属 `S1` |\n'
        '| **证明** | S1 / F1 | 数学证明、证明某命题 → `S1`；**开具证明**（在学/成绩/党团） → `F1` |\n'
        '| **失眠 / 睡不着** | F2 / F3 | 想调作息、作息紊乱 → `F2`；**持续失眠 + 情绪/危机信号** → `F3`（并触发危机红线） |\n'
        '| **预算 / 记账** | F4 / F2 | 钱怎么花 → `F4`；时间怎么安排 → `F2` |',
        label='补 3 条消歧（证明 / 失眠 / 预算）')
    rep('domains/_registry.md',
        '> 共 **19 个域** ｜ 生成自 `scripts/_build/build_qihang_v2.py`',
        '> 共 **19 个域 / 38 个库内 skill（每域 2 个）** ｜ 生成自 `scripts/_build/build_qihang_v2.py`，'
        '扩库层 `build_phase13.py`\n'
        '> 库外候选的选优结论见 `references/skill-matrix-v3.md`',
        label='registry 头部对齐 38 skill')

# ==================================================================== 12. 自检脚本
def fix_selfcheck():
    p = 'scripts/selfcheck.sh'
    # a) 38 skill（单遍 awk 统计，避免逐域起子进程）
    rep(p,
        'nsk=$(find domains -path \'*skills/local*\' -name SKILL.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "${nsk:-0}" -eq 19 ] && ok "库内 skill = 19" || bad "库内 skill = $nsk（期望 19）"',
        'nsk=$(find domains -path \'*skills/local*\' -name SKILL.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "${nsk:-0}" -eq 38 ] && ok "库内 skill = 38（每域 2 个）" || bad "库内 skill = $nsk（期望 38）"\n'
        '# 单遍统计每域 skill 数（避免逐域起子进程）\n'
        '_pbad=$(find domains -path \'*skills/local/*/SKILL.md\' 2>/dev/null | awk -F/ \'{print $2}\' \\\n'
        '        | sort | uniq -c | awk \'$1!=2\' | wc -l | tr -d \' \')\n'
        '[ "${_pbad:-0}" -eq 0 ] && ok "每域均为 2 个库内 skill" || bad "$_pbad 个域的库内 skill 数 ≠ 2"',
        label='计数 19→38 + 每域 2 个断言（单遍统计）')
    # a2) 必备文件清单补 regress.sh
    rep(p,
        '.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh scripts/audit.sh"',
        '.codebuddy-plugin/plugin.json scripts/qihang.sh scripts/dlut-read.sh scripts/selfcheck.sh scripts/audit.sh scripts/regress.sh"',
        label='必备文件清单补 regress.sh',
        required=False)   # 会被 fix_official_sites 的 aligncheck 版本进一步取代

    # b) 每域 external 必须含选优结论
    rep(p,
        '# ---------- 汇总 ----------',
        '# ---------- 9. 多源比对与 DUT 适配 ----------\n'
        'echo "[9] 库外多源比对"\n'
        '# grep -L 一次列出缺失文件（2 个子进程，替代逐域循环）\n'
        '_ma=$(grep -L "综合分" domains/*/skills/external.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '_mb=$(grep -L "DUT 落地评估" domains/*/skills/external.md 2>/dev/null | wc -l | tr -d \' \')\n'
        'if [ "${_ma:-0}" -eq 0 ] && [ "${_mb:-0}" -eq 0 ]; then\n'
        '  ok "19 域 external.md 均含「多源比对 + DUT 落地评估」"\n'
        'else\n'
        '  bad "external.md 缺项：多源比对 $_ma 个 / DUT 评估 $_mb 个"\n'
        'fi\n'
        'if [ -f references/skill-matrix-v3.md ]; then ok "存在 skill-matrix-v3.md"\n'
        'else bad "缺 references/skill-matrix-v3.md"; fi\n'
        '\n'
        '# ---------- 10. 仓库清洁度（临时文件零残留） ----------\n'
        'echo "[10] 临时文件残留"\n'
        '_tmp=$(find . -maxdepth 2 -name ".selfcheck.tmp*" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "${_tmp:-0}" -eq 0 ] && ok "无 .selfcheck.tmp* 残留" || bad "仍有 $_tmp 个自检临时文件残留"\n'
        '\n'
        '# ---------- 汇总 ----------',
        label='新增第 9/10 节：多源比对 + 临时文件断言')
    # c) 砍掉全部临时文件依赖（v2.7 关键修复）
    rep(p,
        'TMP="${ROOT}/.selfcheck.tmp"',
        '# v2.7：本脚本**不创建任何临时文件**（旧版为 TMP="${ROOT}/.selfcheck.tmp"）。\n'
        '# 原因（实测）：部分受限环境把 rm 做成"失败即封"的拦截器，\n'
        '# 旧版在 EXIT trap 里 rm 临时文件，会导致**整个脚本静默失败、零输出**；\n'
        '# 旧版还把 .selfcheck.tmp / .selfcheck.tmp.refs 留在仓库根目录。',
        label='声明零临时文件（并移除 TMP 定义）')
    rep(p,
        '''# ---------- 4. 交叉引用 ----------
echo "[4] 文档交叉引用"
: > "$TMP"
for f in $(find . -name '*.md' -not -path './dev/*' -not -path './proc/*' 2>/dev/null | sort); do
  grep -oE '(library|references|domains|scripts|commands)/[A-Za-z0-9_./-]+\\.md' "$f" 2>/dev/null | sort -u > "${TMP}.refs"
  while IFS= read -r p; do
    [ -n "$p" ] || continue
    [ -e "$p" ] || echo "BROKEN|$p|$f" >> "$TMP"
  done < "${TMP}.refs"
done
nbroke=$(grep -c '^BROKEN' "$TMP" 2>/dev/null)
nbroke=${nbroke:-0}
if [ "$nbroke" -eq 0 ]; then ok "无失效引用"
else bad "$nbroke 处失效引用"; grep '^BROKEN' "$TMP" | head -8 | sed 's/^BROKEN|/       /'; fi''',
        '''# ---------- 4. 交叉引用（零临时文件版） ----------
echo "[4] 文档交叉引用"
nbroke=0; nref=0
for f in $(find . -name '*.md' -not -path './dev/*' -not -path './proc/*' 2>/dev/null | sort); do
  for p in $(grep -oE '(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*]+[.]md' "$f" 2>/dev/null | sort -u); do
    nref=$((nref+1))
    if [ ! -e "$p" ]; then
      nbroke=$((nbroke+1))
      [ "$nbroke" -le 8 ] && printf '       %s  ← %s\\n' "$p" "$f"
    fi
  done
done
# 说明：路径字符集排除了 </>* 等，故「domains/<域>/_domain.md」这类**占位符**不会被误判为失效引用。
if [ "$nbroke" -eq 0 ]; then ok "无失效引用（检查 $nref 处）"
else bad "$nbroke 处失效引用"; fi''',
        label='交叉引用检查改为零临时文件（并支持中文路径）',
        required=False)   # 会被 fix_selfcheck_perf 的单遍版进一步取代
    rep(p,
        ': > "$TMP" 2>/dev/null || true\necho "========================================"',
        'echo "========================================"',
        label='去掉结尾 TMP 清空语句',
        required=False)

# ==================================================================== 13. 审计脚本
def fix_audit():
    p = 'scripts/audit.sh'
    rep(p,
        'nred2=$(grep -rl \'红线\\|安全护栏\' domains/*/skills/local/*/SKILL.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "$nred" -eq "$nd" ] && ok "域文件红线覆盖 $nred/$nd" || bad "域文件红线覆盖 $nred/$nd（应全覆盖）"\n'
        '[ "$nred2" -eq "$nd" ] && ok "库内 skill 红线覆盖 $nred2/$nd" || bad "库内 skill 红线覆盖 $nred2/$nd"',
        'nred2=$(grep -rl \'红线\\|安全护栏\' domains/*/skills/local/*/SKILL.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "$nred" -eq "$nd" ] && ok "域文件红线覆盖 $nred/$nd" || bad "域文件红线覆盖 $nred/$nd（应全覆盖）"\n'
        '# v2.7：每域 2 个库内 skill，故期望 2×域数\n'
        '_want=$((nd*2))\n'
        '[ "$nred2" -eq "$_want" ] && ok "库内 skill 红线覆盖 $nred2/$_want（每域 2 个）" || bad "库内 skill 红线覆盖 $nred2/$_want"',
        label='红线覆盖期望 19→38')
    rep(p,
        '  out=$(bash scripts/dlut-read.sh 邮箱提示 </dev/null 2>&1); [ $? -eq 2 ] \\\n'
        '    && ok "L2 需确认（退出码 2）" || bad "L2 未要求确认"',
        '  out=$(bash scripts/dlut-read.sh 邮箱提示 </dev/null 2>&1); [ $? -eq 2 ] \\\n'
        '    && ok "L2 需确认（退出码 2）" || bad "L2 未要求确认"\n'
        '  # v2.7 新增：L3 语义变体必须同样被拒（旧版精确匹配可被「缴费金额」等绕开）\n'
        '  for t in 缴费金额 银行卡号 身份证号 邮件内容 成绩单 家庭信息卡; do\n'
        '    out=$(bash scripts/dlut-read.sh "$t" </dev/null 2>&1); rc=$?\n'
        '    if [ "$rc" -eq 3 ] && echo "$out" | grep -q "拒绝执行"; then ok "L3 变体拦截 [$t]"\n'
        '    else bad "L3 变体未拦截 [$t]（退出码 $rc）"; fi\n'
        '  done',
        label='新增 L3 语义变体回归测试')
    rep(p,
        '# ---------- 9. 脚本可执行性 ----------',
        '# ---------- 9. 多源比对与 DUT 适配 ----------\n'
        'echo "[8b] 库外候选合规与 DUT 适配"\n'
        'if [ -f references/skill-matrix-v3.md ]; then\n'
        '  grep -q "DUT 适配" references/skill-matrix-v3.md && ok "矩阵含 DUT 适配维度" || warn "矩阵缺 DUT 适配维度"\n'
        '  if grep -q "环境错位清单" references/skill-matrix-v3.md; then ok "含环境错位清单（防误装）"; fi\n'
        'else\n'
        '  bad "缺 references/skill-matrix-v3.md"\n'
        'fi\n'
        '\n'
        '# ---------- 9b. 脚本可执行性 ----------',
        label='新增多源比对/DUT 适配检查')

# ==================================================================== 14. 目录与忽略
def fix_misc():
    p = '.gitignore'
    cur = rd(p) if os.path.exists(os.path.join(ROOT, p)) else ''
    if '.selfcheck.tmp' not in cur:
        wr(p, (cur.rstrip() + '\n' if cur else '') +
            '# 自检脚本历史遗留的临时文件\n.selfcheck.tmp\n.selfcheck.tmp.refs\n\n'
            '# 构建缓存\n__pycache__/\n*.pyc\n')
        OK.append('%s :: 新增 .gitignore（临时文件 + 缓存）' % p)
    else:
        DONE.append('[已是最新] %s' % p)

    rep('README.md',
        '└── scripts/\n'
        '    ├── qihang.sh                管理脚本（多平台探测）\n'
        '    ├── dlut-read.sh             DUT 私密站只读取数（L1/L2/L3 硬拦截）\n'
        '    └── build_*.py               结构生成器（改域后重跑）',
        '└── scripts/\n'
        '    ├── qihang.sh                管理脚本（多平台探测）\n'
        '    ├── dlut-read.sh             DUT 私密站只读取数（L1/L2/L3 硬拦截）\n'
        '    ├── selfcheck.sh             结构自检（计数 / 交叉引用 / 红线一致性）\n'
        '    ├── audit.sh                 安全审计（危险命令 / 凭证 / L3 门禁实测）\n'
        '    ├── regress.sh               **行为回归**（澄清门算例 / L3 门禁矩阵，支持多轮）\n'
        '    └── _build/build_*.py        结构生成器（改域后按序重跑）',
        label='README 目录树补 selfcheck/audit/regress 脚本')

    rep('scripts/_build/README.md',
        '**严格顺序**：`v2 → extras → phase1 → phase2 → phase3`\n'
        '\n'
        '```bash\n'
        'python scripts/_build/build_qihang_v2.py .\n'
        'python scripts/_build/build_qihang_v2_extras.py .\n'
        'python scripts/_build/build_phase1.py .\n'
        'python scripts/_build/build_phase2.py .\n'
        'python scripts/_build/build_phase3.py .\n'
        'bash scripts/selfcheck.sh      # 跑完必自检\n'
        '```',
        '**严格顺序（v2.7 全量）**：`v2 → extras → phase1 … phase15`\n'
        '\n'
        '```bash\n'
        'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do\n'
        '  case "$p" in v2|v2_extras) f="build_qihang_${p}.py" ;; *) f="build_phase${p}.py" ;; esac\n'
        '  python "scripts/_build/$f" .\n'
        'done\n'
        'bash scripts/selfcheck.sh && bash scripts/audit.sh   # 跑完必自检\n'
        '```\n'
        '\n'
        '| 层 | 作用 |\n'
        '|---|---|\n'
        '| `build_phase4`–`build_phase12` | 复核修复与文档同步（v2.2–v2.6 各轮） |\n'
        '| **`build_phase13`** | **库内 skill 扩容：每域 1 → 2（共 38）** |\n'
        '| **`build_phase14`** | **库外候选多源比对 + 选优 + 生成 `skill-matrix-v3.md`** |\n'
        '| **`build_phase15`** | **复查修复层（v2.6 → v2.7，17 项缺陷）** |',
        label='补全构建顺序表（phase4–15）')

    rep('references/skill-sources.md',
        '## 关键结论',
        '## 平台可达性实测（2026-10-02 · 本机）\n'
        '\n'
        '| 平台 | HTTP | 结论 |\n'
        '|---|---|---|\n'
        '| skills.sh | ✅ 200 | 可达，1.5M 条目 |\n'
        '| officialskills.sh | ✅ 200 | 可达，仅厂商官方 |\n'
        '| claude-plugins.dev | ✅ 200 | 可达，自动索引 |\n'
        '| ClawHub | ✅ 200 | 可达，OpenClaw 生态 |\n'
        '| GitHub Topics / awesomeskills.dev / SkillsMP / LobeHub / StudentSuite / VoltAgent / ComposioHQ / yzfly | ❌ 超时 | **本机不可达**（`github.com` HTML 亦超时，但 `api.github.com` 正常） |\n'
        '\n'
        '**由此修正探测流程**：原流程把「浏览平台页」当第一步，在本机不可靠；\n'
        '现改为 **`api.github.com` 为主干**（可核验 stars/license/pushed_at/archived），平台页仅作发现渠道。\n'
        '\n'
        '## 关键结论',
        label='补平台可达性实测')
    rep('references/skill-sources.md',
        '- 教育垂类 skill 中，仅 `mattpocock/skills · teach` 进入 skills.sh 榜单（**736.7K installs**）；其余教育类均无公开使用量。',
        '- 教育垂类 skill 中，仅 `mattpocock/skills · teach` 进入 skills.sh 榜单（**736.7K installs**）。\n'
        '- **v2.7 更正**：此前「教育场景空白」的结论已过时 —— GitHub 检索发现多个千星级教育垂类：\n'
        '  `bevibing/tutor-skills`（1,313★）、`GarethManning/education-agent-skills`（817★，教师侧）、\n'
        '  `bevibing/socrates-skill`（326★）、`Lucaswangzcx/literature-downloader-skill`（230★，中文）、\n'
        '  `flysheep-ai/education-skills`（106★，中文）。但**适配 DUT 本科新生**的仍以中文垂类为主，'
        '且整体占比不高（见 `skill-matrix-v3.md` 量化结论）。',
        label='更正「教育场景空白」过时结论')

# ==================================================================== 19. DUT 公开信息库数据修复
def fix_official_sites():
    p = 'references/dlut-official-sites.md'
    # 状态单元格被污染（"✅ 73" 疑似历史计数误并入）
    rep(p,
        '| 学生公寓服务中心 | 挂靠 https://houqin.dlut.edu.cn/ | ✅ 73 |',
        '| 学生公寓服务中心 | 挂靠 https://houqin.dlut.edu.cn/ | ✅ |',
        label='清理被污染的状态单元格（"✅ 73" → "✅"）')
    # 「财务处」在 §3 与 §5 重复；§5 才是其正确归属 → 删除 §3 副本（count=1 只替换首次出现=§3）
    rep(p,
        '| 财务处 | http://cw.dlut.edu.cn/ | ⚠️ **登录后仍受限**（实测仍返回「系统提示」）→ 需校内网/VPN |\n'
        '| 离校系统 | http://lx.dlut.edu.cn/ | ✅ |',
        '| 离校系统 | http://lx.dlut.edu.cn/ | ✅ |',
        label='删除 §3 中重复登记的「财务处」行（保留 §5 正式条目）')
    rep(p,
        '| 迎新网 | https://yx.dlut.edu.cn/ | ✅ |',
        '| 迎新网 | https://yx.dlut.edu.cn/ | ✅ |\n'
        '\n'
        '> **服务类站点的完整清单见 §5 职能部门与服务**（本节只保留与教学直接相关的入口，避免同一单位两处登记）。',
        label='§3 末尾加服务类站点指针')

    # 归档版验收报告加「历史文档」横幅（避免与 v2.7 现状冲突）
    rep('references/acceptance-v2.md',
        '> 验收日期：2026-10-01 ｜ 对象：`qihang-pack` v2.6.0',
        '> ⚠️ **历史文档**：本报告验收的是 **v2.6.0**，其中 L3 门禁与计数类结论已被\n'
        '> `references/review-report-v2.4.md` 修订。**现行状态以 v2.7.0 为准。**\n'
        '>\n'
        '> 验收日期：2026-10-01 ｜ 对象：`qihang-pack` v2.6.0',
        label='acceptance-v2 加「历史文档」横幅')

    # aligncheck.py 纳入必备文件；.idea 等 IDE 目录加入忽略
    rep('scripts/selfcheck.sh',
        'scripts/audit.sh scripts/regress.sh"',
        'scripts/audit.sh scripts/regress.sh scripts/aligncheck.py"',
        label='必备文件清单补 aligncheck.py')
    rep('.gitignore',
        '__pycache__/',
        '__pycache__/\n\n# IDE\n.idea/\n.vscode/',
        label='.gitignore 补 IDE 目录',
        required=False)


# ==================================================================== 20. 第二轮对齐（全量重开每个文件后发现）
def fix_align_round2():
    # D1/D2 工作流已扩到 8 步，旧文档仍写「第 ⑦ 步 写入学习档案」
    rep('library/memory.md',
        '> 1 级 skill 库的第 4 份规则文件。负责工作流第 ⑦ 步「写入学习档案」，并与',
        '> 1 级 skill 库的第 4 份规则文件。负责工作流第 **⑧** 步「归档（写入学习档案）」，并与',
        label='memory.md 工作流步号 ⑦→⑧')
    rep('references/platforms.md',
        'LearnBuddy 有三层记忆，本包的工作流第 ⑦ 步「写入学习档案」直接落到这套记忆里：',
        'LearnBuddy 有三层记忆，本包的工作流第 **⑧** 步「归档」直接落到这套记忆里：',
        label='platforms.md 工作流步号 ⑦→⑧')
    # D3 library 规则文件数已由 3 增至 7
    rep('references/platforms.md',
        '| **连小理**（= LearnBuddy） | 把 `domains/_registry.md` + `library/` 三份规则挂到平台的知识库；场景设计见 `qihang-scenario-design.html` |',
        '| **连小理**（= LearnBuddy） | 把 `domains/_registry.md` + `library/` **7 份规则文件** 挂到平台的知识库；场景设计见 `qihang-scenario-design.html` |',
        label='platforms.md 规则文件数 3→7')
    # D4 赛道二提交物（HTML）仍称 19 个库内 skill
    for old, new, lb in [
        ('19 域 × 每域 1 个库内 skill = <b>19 个库内 skill</b>（已全部产品化，含可执行示例）；',
         '19 域 × 每域 2 个库内 skill = <b>38 个库内 skill</b>（已全部产品化，含可执行示例）；',
         'HTML 库内 skill 数 19→38'),
        ('<li><b>许可证</b>：19 个库内 skill 中仅 2 个是摘录（MIT / Apache-2.0，均合法）',
         '<li><b>许可证</b>：38 个库内 skill 中仅 2 个是摘录（MIT / Apache-2.0，均合法）',
         'HTML 摘录校验基数 19→38'),
        ('可行性：19 个库内 skill 已产品化，库外均开源',
         '可行性：38 个库内 skill 已产品化，库外均开源',
         'HTML 可行性标签 19→38'),
    ]:
        rep('qihang-scenario-design.html', old, new, label=lb)
    # D5 话术模板里的占位符 XXX（易被误读为未填）
    rep('library/login-policy.md',
        '具体到你个人的信息需要你自己在 `XXX` 查看。',
        '具体到你个人的信息需要你自己在**对应系统**（如教务系统 / 校园门户）查看。',
        label='login-policy 去占位符 XXX')
    # D6 通用表述「A 域/B 域」会被误读为 v1.1 遗留域名 → 改「甲域/乙域」
    for p in ('library/domain-review-cases.md', 'scripts/_build/build_phase1.py'):
        rep(p,
            '## 一、改锁类（表面像 A 域，实际属 B 域）',
            '## 一、改锁类（表面像甲域，实际属乙域）',
            label='%s 去 A/B 域表述' % p)
    # D7 自检只查了「D 域」，B/C/D/G 域同样要查
    rep('scripts/selfcheck.sh',
        "_od=$(grep -rlnE '\\bD 域\\b' domains/ library/ SKILL.md 2>/dev/null | wc -l | tr -d ' ')",
        "_od=$(grep -rlnE '\\b[A-G] 域\\b' domains/ library/ SKILL.md 2>/dev/null | wc -l | tr -d ' ')",
        label='自检旧域名匹配扩展为 [A-G] 域')
    # D8 生成链无法复现现行 SKILL.md：v2 模板仍是 v1.1 的 7 步 / 三份规则
    rep('scripts/_build/build_qihang_v2.py',
        '  ↓ ⑦输出      library/output-spec.md        ≤6 条要点，写入学习档案\n'
        '```\n'
        '\n'
        '## 三份规则文件（1 级库的本体）\n'
        '\n'
        '| 文件 | 职责 |\n'
        '|---|---|\n'
        '| `library/clarity.md` | 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级 |\n'
        '| `library/domain-review.md` | 域审查：锁定 / 跨域 / 越界 / 无域兜底 |\n'
        '| `library/output-spec.md` | 输出规范：统一模板 + 简略原则 |',
        '  ↓ ⑦输出      library/output-spec.md        ≤6 条要点，过 output-checklist 校验\n'
        '  ↓ ⑧归档      library/memory.md             写学习档案（F3/F5 敏感域除外）\n'
        '```\n'
        '\n'
        '## 五份规则文件（1 级库的本体）\n'
        '\n'
        '| 文件 | 职责 |\n'
        '|---|---|\n'
        '| `library/clarity.md` | 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级 |\n'
        '| `library/domain-review.md` | 域审查：锁定 / 跨域 / 越界 / 无域兜底 |\n'
        '| `library/output-spec.md` | 输出规范：统一模板 + 简略原则 + 交付前校验 |\n'
        '| `library/memory.md` | 学习档案：四类内容 + 分层落点 + 敏感域红线 |\n'
        '| `library/login-policy.md` | 登录选择原则：A/B/C 三档 + 标准话术 + 安全保障 |',
        label='v2 模板对齐现行 SKILL.md（8 步 + 五份规则）')


# ==================================================================== 21. 公开站计数统一（去重后 160 → 159）
def fix_counts_159():
    """去重 §3 的「财务处」后，表格行由 160 降为 159，✅69 / ⚠️25 / 数据条目 146。
    所有「现行口径」的文档必须同步；历史报告保留其历史值。"""
    pairs = [
        ('INSTALL.md',
         '`[资源] DUT 公开站 160 行`', '`[资源] DUT 公开站 159 行`', 'INSTALL 159 行'),
        ('library/login-policy.md',
         '（信息库 160 条覆盖大量问题）', '（信息库 159 条覆盖大量问题）', 'login-policy 159 条'),
        ('PROJECT.md',
         '| 公开站      | `references/dlut-official-sites.md`    | **160 条**表格行（✅ 69 / ⚠️ 26），三校区 + 全部学院 + 职能部门 |',
         '| 公开站      | `references/dlut-official-sites.md`    | **159 条**表格行（✅ 69 / ⚠️ 25），三校区 + 全部学院 + 职能部门 |',
         'PROJECT §5 159 行'),
        ('PROJECT.md',
         '| DUT 公开信息库          | ✅ **160 条**表格行（✅ 69 / ⚠️ 26）',
         '| DUT 公开信息库          | ✅ **159 条**表格行（✅ 69 / ⚠️ 25）',
         'PROJECT §7 159 行'),
        ('PROJECT.md',
         '│   ├── dlut-official-sites.md     公开站 160 条',
         '│   ├── dlut-official-sites.md     公开站 159 条',
         'PROJECT 目录树 159 条'),
        ('README.md',
         '│   ├── dlut-official-sites.md      DUT 公开站信息库（160 条）',
         '│   ├── dlut-official-sites.md      DUT 公开站信息库（159 条）',
         'README 目录树 159 条'),
        ('README.md',
         '| 公开站 | `references/dlut-official-sites.md` | 160 条，19 个域的 `_domain.md` 各自标注绑定点 |',
         '| 公开站 | `references/dlut-official-sites.md` | 159 条，19 个域的 `_domain.md` 各自标注绑定点 |',
         'README §5 159 条'),
        ('qihang-scenario-design.html',
         '学院官网、教务处、一卡通、报修电话散落在 160+ 个站点',
         '学院官网、教务处、一卡通、报修电话散落在 150+ 个站点',
         'HTML 站点规模 150+'),
        ('qihang-scenario-design.html',
         '<tr><td>公开站</td><td><b>160 条</b>：三校区 + 全部学部学院 + 教务处/研院/图书馆/就业/保卫等职能部门</td>',
         '<tr><td>公开站</td><td><b>159 条</b>：三校区 + 全部学部学院 + 教务处/研院/图书馆/就业/保卫等职能部门</td>',
         'HTML 159 条'),
        ('qihang-scenario-design.html',
         '<td>160 条信息库 + 强制查表规则',
         '<td>159 条信息库 + 强制查表规则',
         'HTML 准确率行 159 条'),
        ('references/dlut-official-sites.md',
         '- 表格总行数：**160 条**',
         '- 表格总行数：**159 条**（数据条目 146，含 ✅69 / ⚠️25）\n'
         '- 维护口径：同一单位**只在最贴切的小节登记一次**（如「财务处」只出现在 §5）',
         '信息库自述行数 159'),
        ('references/stress-test-v3.md',
         '| DUT 公开站表格行 | 160 ✅ |',
         '| DUT 公开站表格行 | 159 ✅ |',
         '压测报告 159 行'),
        ('scripts/regress.sh',
         '公开站表格行" "$(grep -c \'^|\' references/dlut-official-sites.md | tr -d \' \')" 160',
         '公开站表格行" "$(grep -c \'^|\' references/dlut-official-sites.md | tr -d \' \')" 159',
         'regress 期望值 160→159'),
        ('scripts/selfcheck.sh',
         '_pub=$(grep -c \'^|\' references/dlut-official-sites.md 2>/dev/null); pub=${pub:-0}',
         '_pub=$(grep -c \'^|\' references/dlut-official-sites.md 2>/dev/null); pub=${pub:-0}',
         '（占位，无改动）', False),
    ]
    for item in pairs:
        p, o, n, lb = item[0], item[1], item[2], item[3]
        rep(p, o, n, label=lb, required=(item[4] if len(item) > 4 else True))
    # 复查报告补一行口径更新说明（避免报告里的旧值与现状冲突）
    rep('references/review-report-v2.4.md',
        '| **P2-14** | `PROJECT.md` 数字连环错',
        '> **口径更新（v2.7 终版）**：本节修复后，因 §3 去重了重复登记的「财务处」一行，'
        '表格行由 160 降为 **159**（✅69 / ⚠️25，数据条目 146）；全包声明已同步。\n\n'
        '| **P2-14** | `PROJECT.md` 数字连环错',
        label='复查报告补 159 口径说明')


# ==================================================================== 22. 公开站口径终版（表格行 159 / 条目 139 / ✅67 · ⚠️21）
def fix_counts_final():
    """统一到**可复算**的口径：
       表格行 159（含 表头 10 + 分隔 10）· 数据条目 139（✅67 / ⚠️21 / 未标注 51）。
       此前用「✅/⚠️ 全文出现次数」当口径，会被正文里的标记污染，已弃用。"""
    F = '**159 条**表格行 / **139 条**条目（✅ 67 / ⚠️ 21）'
    pairs = [
        ('PROJECT.md', '**159 条**表格行（✅ 69 / ⚠️ 25）', F, 'PROJECT §5 口径终版'),
        ('PROJECT.md', '✅ **159 条**表格行（✅ 69 / ⚠️ 25）', '✅ ' + F, 'PROJECT §7 口径终版'),
        ('PROJECT.md', '│   ├── dlut-official-sites.md     公开站 159 条',
         '│   ├── dlut-official-sites.md     公开站 139 条条目', 'PROJECT 目录树'),
        ('README.md', '│   ├── dlut-official-sites.md      DUT 公开站信息库（159 条）',
         '│   ├── dlut-official-sites.md      DUT 公开站信息库（139 条条目）', 'README 目录树'),
        ('README.md', '| 公开站 | `references/dlut-official-sites.md` | 159 条，19 个域的 `_domain.md` 各自标注绑定点 |',
         '| 公开站 | `references/dlut-official-sites.md` | **139 条**条目（表格行 159），19 个域的 `_domain.md` 各自标注绑定点 |',
         'README §5 口径终版'),
        ('INSTALL.md', '`[资源] DUT 公开站 159 行`', '`[资源] DUT 公开站 139 条条目`', 'INSTALL 口径终版'),
        ('library/login-policy.md', '（信息库 159 条覆盖大量问题）', '（信息库 139 条条目覆盖大量问题）',
         'login-policy 口径终版'),
        ('qihang-scenario-design.html', '<tr><td>公开站</td><td><b>159 条</b>：三校区',
         '<tr><td>公开站</td><td><b>139 条</b>：三校区', 'HTML 条目数终版'),
        ('qihang-scenario-design.html', '<td>159 条信息库 + 强制查表规则', '<td>139 条信息库 + 强制查表规则',
         'HTML 准确率行终版'),
        ('references/dlut-official-sites.md',
         '- 表格总行数：**159 条**（数据条目 146，含 ✅69 / ⚠️25）',
         '- 表格总行数：**159 条**（= 表头 10 + 分隔 10 + **数据条目 139**）\n'
         '- 数据条目核验分布：**✅ 67 / ⚠️ 21 / 未标注 51**（合计 139）\n'
         '- 计数口径：一律按**表格行/数据行**统计；不采用「✅ 全文出现次数」（会被正文标记污染）',
         '信息库自述口径终版'),
        ('references/stress-test-v3.md', '| DUT 公开站表格行 | 159 ✅ |',
         '| DUT 公开站表格行 / 数据条目 | 159 / 139 ✅ |', '压测报告口径终版'),
    ]
    for p, o, n, lb in pairs:
        rep(p, o, n, label=lb)
    # 回归脚本：同时钉住「表格行」与「数据条目」两个数
    rep('scripts/regress.sh',
        '  _chk "公开站表格行" "$(grep -c \'^|\' references/dlut-official-sites.md | tr -d \' \')" 159',
        '  _chk "公开站表格行" "$(grep -c \'^|\' references/dlut-official-sites.md | tr -d \' \')" 159\n'
        '  _chk "公开站数据条目" "$(awk \'/^\\|/{if($0 ~ /^\\|[-: ]+\\|$/)next; print}\' references/dlut-official-sites.md \\\n'
        '     | grep -vc \'名称\\|学院\\|站点\\|区块\\|平台\\|级别\\|网址\\|序号\' )" 139',
        label='regress 增钉数据条目 139',
        required=False)


# ==================================================================== 17. 版本号统一（v2.7）
def fix_versions():
    """把全包版本号统一到 v2.7.0（旧 19 个 skill 仍为 2.6.0，会与新版混用）"""
    changed = []
    targets = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, 'domains')):
        for fn in files:
            if fn == 'SKILL.md':
                targets.append(os.path.relpath(os.path.join(base, fn), ROOT))
    targets += ['SKILL.md', 'library/SKILL.md', 'config.yaml',
                '.codebuddy-plugin/plugin.json', 'README.md', 'PROJECT.md', 'ROADMAP.md',
                'INSTALL.md', 'qihang-scenario-design.html']
    SUBS = [
        ('version: 2.6.0', 'version: 2.7.0'),
        # JSON 风格（plugin.json）：与 YAML 风格写法不同，早期版本漏改
        ('"version": "2.6.0"', '"version": "2.7.0"'),
        # 当前状态 / 提交物的版本声明（易漂移点；用精确串，避免误改历史修订注记）
        ('## 7. 当前状态（v2.6.0）', '## 7. 当前状态（v2.7.0）'),
        ('（v2.6.0）</title>', '（v2.7.0）</title>'),
        ('<span class="ver">v2.6.0 三级结构</span>', '<span class="ver">v2.7.0 三级结构</span>'),
        ('版本 v2 ｜', '版本 v2.7 ｜'),
        ('# 「启航」学伴包 v2.6 ·', '# 「启航」学伴包 v2.7 ·'),
        ('「启航」学伴包 v2.6.0 ·', '「启航」学伴包 v2.7.0 ·'),
        ('「启航」新生学习生活一体化学伴包 v2.6.0', '「启航」新生学习生活一体化学伴包 v2.7.0'),
        ('> v2.6.0 ｜ 2026-10-01', '> v2.7.0 ｜ 2026-10-02'),
        ('v2.6.0 ｜ 2026-10-01 ｜ 配套', 'v2.7.0 ｜ 2026-10-02 ｜ 配套'),
        ('# 「启航」学伴包 · 入口（v2.5.0）', '# 「启航」学伴包 · 入口（v2.7.0）'),
        ('> 版本 v2 ｜ 更新 2026-10-01', '> 版本 v2.7 ｜ 更新 2026-10-02'),
    ]
    for p in targets:
        fp = os.path.join(ROOT, p)
        if not os.path.isfile(fp):
            continue
        with open(fp, 'r', encoding='utf-8') as f:
            t0 = f.read()
        t = t0
        for a, b in SUBS:
            t = t.replace(a, b)
        if t != t0:
            with open(fp, 'w', encoding='utf-8', newline='\n') as f:
                f.write(t)
            changed.append(p)
    if changed:
        OK.append('统一版本号到 v2.7.0（%d 个文件）' % len(changed))
    else:
        DONE.append('[已是最新] 版本号已统一为 v2.7.0')

# ==================================================================== 18. 自检脚本性能优化（消除子进程膨胀）
def fix_selfcheck_perf():
    p = 'scripts/selfcheck.sh'
    # [2] 逐域循环 → 单遍统计
    rep(p,
        'nd=0; nbad=0\n'
        'for d in domains/*/; do\n'
        '  [ -d "$d" ] || continue\n'
        '  b=$(basename "$d"); nd=$((nd+1))\n'
        '  [ -f "${d}_domain.md" ] || { bad "$b 缺 _domain.md"; nbad=$((nbad+1)); }\n'
        '  [ -f "${d}skills/external.md" ] || { bad "$b 缺 skills/external.md"; nbad=$((nbad+1)); }\n'
        '  n=$(find "${d}skills/local" -name SKILL.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '  [ "${n:-0}" -ge 1 ] || { bad "$b 无库内 skill"; nbad=$((nbad+1)); }\n'
        'done\n'
        '[ "$nd" -eq 19 ] && ok "域数 = 19" || bad "域数 = $nd（期望 19）"\n'
        '[ "$nbad" -eq 0 ] && ok "所有域三级结构完整" || bad "$nbad 处缺失"',
        '# v2.7：改为单遍统计（原逐域循环会起 ~60 个子进程，受限环境易被中断）\n'
        'nd=$(find domains -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d \' \')\n'
        'n_dom=$(find domains -maxdepth 2 -name \'_domain.md\' 2>/dev/null | wc -l | tr -d \' \')\n'
        'n_ext=$(find domains -maxdepth 3 -path \'*/skills/external.md\' 2>/dev/null | wc -l | tr -d \' \')\n'
        'n_lsk=$(find domains -path \'*skills/local/*/SKILL.md\' 2>/dev/null | wc -l | tr -d \' \')\n'
        'nbad=0\n'
        '[ "$nd" -eq 19 ] && ok "域数 = 19" || { bad "域数 = $nd（期望 19）"; nbad=$((nbad+1)); }\n'
        '[ "$n_dom" -eq 19 ] && ok "19 个 _domain.md 在位" || { bad "_domain.md = $n_dom（期望 19）"; nbad=$((nbad+1)); }\n'
        '[ "$n_ext" -eq 19 ] && ok "19 个 skills/external.md 在位" || { bad "external.md = $n_ext（期望 19）"; nbad=$((nbad+1)); }\n'
        '[ "$n_lsk" -eq 38 ] && ok "38 个库内 skill 在位" || { bad "库内 skill = $n_lsk（期望 38）"; nbad=$((nbad+1)); }\n'
        '[ "$nbad" -eq 0 ] && ok "所有域三级结构完整" || bad "$nbad 处缺失"',
        label='[2] 单遍统计（消除 60 个子进程）')
    # [3] frontmatter：逐文件 3 次 grep → 单次 awk
    rep(p,
        'nf=0; nfm=0\n'
        'for f in $(find . -name SKILL.md -not -path \'./dev/*\' -not -path \'./proc/*\' 2>/dev/null | sort); do\n'
        '  nf=$((nf+1))\n'
        '  head -1 "$f" | grep -q \'^---$\' || { bad "无 frontmatter: $f"; nfm=$((nfm+1)); continue; }\n'
        '  grep -q \'^name:\' "$f" || { bad "缺 name: $f"; nfm=$((nfm+1)); }\n'
        '  grep -q \'^description:\' "$f" || { bad "缺 description: $f"; nfm=$((nfm+1)); }\n'
        'done\n'
        '[ "$nfm" -eq 0 ] && ok "$nf 个 SKILL.md frontmatter 全部合规" || bad "$nfm 处不合规"',
        '# v2.7：单次 awk 取代「逐文件 3 次 grep」（原为 ~120 个子进程）\n'
        '_ff=$(awk \'\n'
        '  FNR==1{if(fn!="")chk(); fn=FILENAME; first=0; hasname=0; hasdesc=0}\n'
        '  FNR==1 && $0 ~ /^---[[:space:]]*$/{first=1}\n'
        '  /^name:/{hasname=1}\n'
        '  /^description:/{hasdesc=1}\n'
        '  END{if(fn!="")chk()}\n'
        '  function chk(){ if(fn !~ /SKILL[.]md$/)return; if(!first||!hasname||!hasdesc) print fn }\n'
        '\' $(find . -name SKILL.md -not -path \'./dev/*\' -not -path \'./proc/*\' 2>/dev/null | sort) 2>/dev/null)\n'
        'nf=$(find . -name SKILL.md -not -path \'./dev/*\' -not -path \'./proc/*\' 2>/dev/null | wc -l | tr -d \' \')\n'
        'nfm=$(printf \'%s\\n\' "$_ff" | grep -c . )\n'
        'nfm=${nfm:-0}\n'
        'if [ "$nfm" -eq 0 ]; then ok "$nf 个 SKILL.md frontmatter 全部合规"\n'
        'else bad "$nfm 处不合规"; printf \'%s\\n\' "$_ff" | head -6 | sed \'s/^/       /\'; fi',
        label='[3] 单次 awk 取代逐文件 grep')
    # [7] 红线重复检测：逐文件 grep → 单遍
    rep(p,
        '_dup=0\n'
        'for f in $(find domains -name \'*.md\' 2>/dev/null); do\n'
        '  c=$(grep -c \'^## ⚠️ 红线（不得绕过）\' "$f" 2>/dev/null)\n'
        '  c=${c:-0}\n'
        '  [ "$c" -gt 1 ] && { bad "红线段重复: $f（$c 段）"; _dup=$((_dup+1)); }\n'
        'done\n'
        '[ "$_dup" -eq 0 ] && ok "无重复红线段"',
        '# v2.7：单遍统计（原逐文件 grep 为 ~95 个子进程）\n'
        '_dup=$(grep -rc \'^## ⚠️ 红线（不得绕过）\' domains --include=\'*.md\' 2>/dev/null \\\n'
        '       | awk -F: \'$2>1\' | wc -l | tr -d \' \')\n'
        '[ "${_dup:-0}" -eq 0 ] && ok "无重复红线段" || bad "$_dup 个文件红线段重复"',
        label='[7] 红线段重复改单遍统计')
    rep(p,
        '_di=0\n'
        'for f in $(find domains -path \'*skills/local*\' -name SKILL.md 2>/dev/null); do\n'
        '  d=$(grep -E \'^- \' "$f" 2>/dev/null | sort | uniq -d | wc -l | tr -d \' \')\n'
        '  d=${d:-0}\n'
        '  [ "$d" -gt 0 ] && { bad "红线条目重复: $f（$d 条）"; _di=$((_di+1)); }\n'
        'done\n'
        '[ "$_di" -eq 0 ] && ok "红线条目无重复"',
        '# v2.7：单次 awk 检测「同一 skill 内红线条目重复」\n'
        '_di=$(awk \'/^## ⚠️ 红线/{inr=1;next} inr&&/^## /{inr=0}\n'
        '  inr&&/^- /{k=FILENAME "|" $0; if(seen[k]++){print FILENAME; print FILENAME > "/dev/stderr"}}\n'
        '\' $(find domains -path \'*skills/local*\' -name SKILL.md 2>/dev/null | sort) 2>/dev/null \\\n'
        '  | sort -u | wc -l | tr -d \' \')\n'
        '[ "${_di:-0}" -eq 0 ] && ok "红线条目无重复" || bad "$_di 个文件红线条目重复"',
        label='[7] 红线条目重复改单次 awk')
    # [4] 再优化：单遍 grep 取代逐文件 grep
    rep(p,
        'nbroke=0; nref=0\n'
        'for f in $(find . -name \'*.md\' -not -path \'./dev/*\' -not -path \'./proc/*\' 2>/dev/null | sort); do\n'
        '  for p in $(grep -oE \'(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*]+[.]md\' "$f" 2>/dev/null | sort -u); do\n'
        '    nref=$((nref+1))\n'
        '    if [ ! -e "$p" ]; then\n'
        '      nbroke=$((nbroke+1))\n'
        '      [ "$nbroke" -le 8 ] && printf \'       %s  ← %s\\n\' "$p" "$f"\n'
        '    fi\n'
        '  done\n'
        'done',
        '# v2.7：单遍 grep -r 取全部引用，再在 shell 内用内建 test 判定（原为逐文件 ~280 个子进程）\n'
        '# v2.10：扫描范围排除 .learnbuddy / .git / .idea —— 记忆日志会「提及」文件名，不属产品文档引用\n'
        '_refs=$(grep -rhoE \'(library|references|domains|scripts|commands)/[^ )），、；;"“”<>*]+[.]md\' \\\n'
        '        --include=\'*.md\' --exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | sort -u)\n'
        'nbroke=0; nref=0\n'
        'while IFS= read -r p; do\n'
        '  [ -n "$p" ] || continue\n'
        '  nref=$((nref+1))\n'
        '  if [ ! -e "$p" ]; then\n'
        '    nbroke=$((nbroke+1))\n'
        '    [ "$nbroke" -le 8 ] && printf \'       %s\\n\' "$p"\n'
        '  fi\n'
        'done <<< "$_refs"\n'
        '# v2.10 新增：**裸文件名**引用（无目录前缀，如 `xxx-review.md`）同样必须存在。\n'
        '# 原正则只认「带目录前缀」的路径，此类断链会被漏检（实测：曾有文件引用不存在的 review 副本）。\n'
        '# 口径：只取反引号内、不含斜杠的 *.md 名，按「全仓库是否存在同名文件」判定。\n'
        '# _BARE_SKIP = 故意不存在于仓库的名字（见 [5] 陈旧文件清单中的历史文件名）。\n'
        '_BARE_SKIP="references/routing-table.md routing-table.md"\n'
        '_bare=$(grep -rhoE \'`[A-Za-z0-9][A-Za-z0-9_.-]*[.]md`\' --include=\'*.md\' \\\n'
        '        --exclude-dir=.learnbuddy --exclude-dir=.git --exclude-dir=.idea . 2>/dev/null | tr -d \'`\' | sort -u)\n'
        'while IFS= read -r b; do\n'
        '  [ -n "$b" ] || continue\n'
        '  case " $_BARE_SKIP " in *" $b "*) continue ;; esac\n'
        '  nref=$((nref+1))\n'
        '  if [ -z "$(find . -name "$b" -not -path \'./.git/*\' -print -quit 2>/dev/null)" ]; then\n'
        '    nbroke=$((nbroke+1))\n'
        '    [ "$nbroke" -le 8 ] && printf \'       %s（裸文件名，全仓库无同名文件）\\n\' "$b"\n'
        '  fi\n'
        'done <<< "$_bare"',
        label='[4] 交叉引用改单遍 grep（消除逐文件子进程）')


def fix_redline_drift():
    # S3 库内 skill 与域文件**内容+顺序**均漂移（域：不代提交作业/报告；skill：不代提交；且条目顺序不同）
    rep('domains/S3-assignment/skills/local/lab-report/SKILL.md',
        '- **不代写正文**（只给 IMRAD 骨架与自查）\n'
        '- **不代操作教学平台**（不代提交）\n'
        '- **不编造实验数据** —— 属学术不端，须改锁并提示 `R5`',
        '- **不代写正文**（只给 IMRAD 骨架与自查）\n'
        '- **不编造实验数据** —— 属学术不端，须改锁并提示 `R5`\n'
        '- **不代操作教学平台**（不代提交作业/报告）',
        label='S3 skill 红线内容+顺序对齐域文件')
    # S2 只是条目顺序不同，统一为域文件顺序（便于机器比对）
    rep('domains/S2-lecture-notes/skills/local/lecture-to-notes/SKILL.md',
        '- **不代操作教学平台**（不代提交作业、不代上传超星/雨课堂）\n'
        '- 产出若用于**提交**，须改锁 `S3`；本域只做自用笔记\n'
        '- 不做题目讲解（→`S1`）',
        '- 产出若用于**提交**，须改锁 `S3`；本域只做自用笔记\n'
        '- **不代操作教学平台**（不代提交作业、不代上传超星/雨课堂）\n'
        '- 不做题目讲解（→`S1`）',
        label='S2 skill 红线条目顺序对齐域文件')

    # 在 selfcheck.sh 增加「域 ↔ 库内 skill 红线逐条一致」的硬断言
    p = 'scripts/selfcheck.sh'
    rep(p,
        '_nr=$(grep -rl \'## ⚠️ 红线\' domains/*/_domain.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "${_nr:-0}" -eq 19 ] && ok "域文件红线覆盖 19/19" || bad "域文件红线覆盖 $_nr/19"',
        '_nr=$(grep -rl \'## ⚠️ 红线\' domains/*/_domain.md 2>/dev/null | wc -l | tr -d \' \')\n'
        '[ "${_nr:-0}" -eq 19 ] && ok "域文件红线覆盖 19/19" || bad "域文件红线覆盖 $_nr/19"\n'
        '\n'
        '# v2.7 新增：库内 skill 的红线条目必须与所属域**逐条一致**（防措辞漂移）\n'
        '# 单次 awk 完成全部比对：既快，也避免受限环境对子进程数的限制\n'
        '_rd=$(awk \'\n'
        '  function save(f){S[f]=sig}\n'
        '  FNR==1{if(prev!="")save(prev);prev=FILENAME;sig="";inred=0}\n'
        '  /^## ⚠️ 红线/{inred=1;next}\n'
        '  inred&&/^## /{inred=0;next}\n'
        '  inred&&/^- /{sig=sig $0 "\\n"}\n'
        '  END{\n'
        '    if(prev!="")save(prev)\n'
        '    fail=0\n'
        '    for(f in S){split(f,a,"/"); if(a[length(a)]!="_domain.md")continue\n'
        '      d=a[1] "/" a[2]; ref=S[f]\n'
        '      for(g in S){if(g==f)continue; split(g,b,"/")\n'
        '        if(b[1] "/" b[2]!=d)continue; if(b[3]!="skills")continue\n'
        '        if(S[g]!=ref)fail++}}\n'
        '    print fail\n'
        '  }\' $(find domains -name \'_domain.md\' -o -name \'SKILL.md\' 2>/dev/null | sort) 2>/dev/null)\n'
        'if [ "${_rd:-0}" -eq 0 ]; then ok "库内 skill 红线与域文件逐条一致"\n'
        'else bad "$_rd 处红线漂移"; fi',
        label='新增红线一致性硬断言（域 ↔ skill）')

    # 文件总数口径已在 fix_counts 注释中说明（避免硬编码数字漂移）


def fix_acceptance():
    rep('references/acceptance-v2.md',
        '| 6 | DUT 公开信息库 | ✅ | 160 条表格行，✅ 73 / ⚠️23 / 学院类 65 |',
        '| 6 | DUT 公开信息库 | ✅ | **160 条**表格行（✅ 69 / ⚠️ 26） |',
        label='公开站计数修正')
    rep('references/acceptance-v2.md',
        '| 8 | L3 硬拦截 | ✅ | `dlut-read.sh 缴费` → **退出码 3，拒绝执行** |',
        '| 8 | L3 硬拦截 | ✅ | `dlut-read.sh 缴费` / `缴费金额` / `银行卡号` / `邮件内容` → **均退出码 3**（v2.7 语义匹配后） |',
        label='L3 证据补语义变体')
    rep('references/acceptance-v2.md',
        '- 规则文件：`library/` 7 份（clarity / domain-review / output-spec / memory / cases / checklist / SKILL）',
        '- 规则文件：`library/` **8 份**（clarity / domain-review / output-spec / memory / **login-policy** / cases / checklist / SKILL）',
        label='library 7→8 份')

def main():
    fix_l3_gate()
    fix_config()
    fix_l3_lists()
    fix_scheme_conflict()
    fix_clarity_hole()
    fix_output_spec()
    fix_qihang_sh()
    fix_counts()
    fix_install()
    fix_e2e()
    fix_registry()
    fix_selfcheck()
    fix_selfcheck_perf()   # 必须在 fix_selfcheck 之后（优化其产出的循环）
    fix_audit()
    fix_misc()
    fix_acceptance()
    fix_redline_drift()   # 必须在 fix_counts 之后（依赖其写入的「文件数」中间值）
    fix_versions()        # 版本号统一到 v2.7.0（最后跑，覆盖前面所有文件）
    fix_official_sites()  # DUT 公开信息库的数据级修复（污染单元格 / 重复登记）
    fix_align_round2()    # 第二轮全量对齐（工作流步号 / 计数 / 提交物 / 生成器模板）
    fix_counts_159()      # 公开站去重后 160→159，全包声明同步
    fix_counts_final()    # 口径终版：表格行 159 / 条目 139 / ✅67 · ⚠️21

    print('=' * 62)
    for x in OK:   print('  ✅ ' + x)
    print('-' * 62)
    if MISS:
        for x in MISS: print('  ❌ 未命中 ' + x)
    else:
        print('  （无未命中项）')
    print('=' * 62)
    print('修复 %d 处 ｜ 未命中 %d 处 ｜ 已是最新 %d 处' % (len(OK), len(MISS), len(DONE)))
    print('提示：接着跑 bash scripts/selfcheck.sh && bash scripts/audit.sh')

if __name__ == '__main__':
    main()
