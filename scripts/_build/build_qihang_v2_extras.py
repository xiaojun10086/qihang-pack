#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「启航」v2.0 外围件生成器：config / commands / scripts / skill-sources / README"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_qihang_v2 import DOMAINS, CATS

OUT = sys.argv[1] if len(sys.argv) > 1 else "qihang-pack-v2"
os.makedirs(OUT, exist_ok=True)

def W(rel, content):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return p

files = []

# ---------------- references/skill-sources.md ----------------
files.append(("references/skill-sources.md", """# Skill 来源清单 · 12 个探测入口

> **用途**：当 19 个域的 `skills/external.md` 都无法满足时，用本表去「找到新 skill」。
> 数据抓取时间：2026-10-01

| # | 平台 | 检索入口 | 规模 | 有使用量? | 有反馈? | 局限 |
|---|---|---|---|---|---|---|
| 1 | **skills.sh** | https://skills.sh/ ｜ `npx skills add <owner>/<repo>` | 1,523,502 | ✅ Installs | ❌ | 只有流行度，无质量 |
| 2 | **GitHub Topics** | https://github.com/topics/agent-skills | 23,419 仓库 | ❌ | ✅ stars/issues | 无使用量 |
| 3 | awesomeskills.dev | https://www.awesomeskills.dev/ | 41,195 | ✅ | ❌ | 教育场景空白 |
| 4 | officialskills.sh | https://officialskills.sh/ | 660 | ❌ | 仅更新时间 | 只收厂商官方 |
| 5 | SkillsMP | https://skillsmp.com/ | 3,296,897 | ❌ | 部分 | 无质量分级 |
| 6 | claude-plugins.dev | https://claude-plugins.dev/skills | 46.9k | ⚠️ 口径不明 | 部分 | 自动索引无把关 |
| 7 | LobeHub Skills | https://lobehub.com/skills | 334,144 | ⚠️ 口径不明 | ❌ | 无教育分类 |
| 8 | ClawHub | https://clawhub.ai/ | 未公开 | ⚠️ 口径不明 | ❌ | OpenClaw 生态 |
| 9 | StudentSuite | https://github.com/StudentSuite/awesome-skills-plugins-for-students | 158 students skills | ❌ | ✅ | 面向 IB/IGCSE |
| 10 | VoltAgent | https://github.com/VoltAgent/awesome-agent-skills | 1000+ ｜ 35,075★ | ❌ | ✅ | 纯清单 |
| 11 | ComposioHQ | https://github.com/ComposioHQ/awesome-claude-skills | 1000+ ｜ 76,231★ | ❌ | ✅ | 偏自动化 |
| 12 | 中文清单 | https://github.com/yzfly/awesome-skills-zh | 精选 | ❌ | ✅（52★） | 活跃度低 |

## 探测流程（新增 skill 必跑）

```
① skills.sh 查使用量
② GitHub API 查 stars / pushed_at / license / open_issues
③ 读 SKILL.md 判可用性（有无标准 frontmatter）
④ 读 scripts/ 判风险（curl|bash / sudo / rm -rf / ~/.ssh / 外发凭证）
⑤ 通过 → 写入对应域的 skills/external.md
```

## 关键结论

- **不存在**既有真实使用量、又深耕教育/校园场景的中文索引站。
- 教育垂类 skill 中，仅 `mattpocock/skills · teach` 进入 skills.sh 榜单（**736.7K installs**）；其余教育类均无公开使用量。
- 因此本包采用「**高星通用底座 + 垂类补充 + 自建库内 skill 兜底**」策略。
"""))

# ---------------- config.yaml ----------------
files.append(("config.yaml", """# 「启航」学伴包 v2.0 · 唯一需要按学期 / 课程修改的文件
# 新学期执行 `bash scripts/qihang.sh new-term` 会先备份再提示重置。

# ============ 学校绑定（强绑定） ============
school:
  name: 大连理工大学
  short: 大工 / DUT
  domain: dlut.edu.cn
  official: https://www.dlut.edu.cn/
  entry_sso: https://sso.dlut.edu.cn/
  entry_portal: https://portal.dlut.edu.cn/
  entry_jwgl: http://jxgl.dlut.edu.cn/student/ucas-sso/login
  webvpn: https://webvpn.dlut.edu.cn/
  app: i大工
  sites_public: references/dlut-official-sites.md
  sites_private: references/dlut-login-sites.md

student:
  # 未经用户确认的个人信息留空；null 表示未知，不得作为事实使用。
  campus: null            # 凌水主校区 / 开发区校区 / 盘锦校区
  college: null           # 用户确认后填写
  grade: null             # 用户确认后填写

# ============ 学期配置 ============
term: null                # 用户确认当前学期后填写
courses: []               # 用户确认修读课程后填写
exam_weeks: []            # 用户提供考试周后填写
sleep_window: null        # 用户确认后填写

# ============ 1 级库参数 ============
library:
  clarity:
    threshold: 0.05
    max_rounds: 3
    max_questions_per_round: 3
    weights: {W: 3.0, O: 2.5, D: 2.0, C: 1.5, B: 1.0, T: 0.5}
    skip_when:
      - 命中校情横切且对象明确
      - 用户显式要求"直接给结果"
  policy:
    local_first: true          # 库内优先（硬规则）
    forbid_fabricate_url: true # 禁止编造 DUT URL
    write_learning_records: true
    never_write_sensitive: [F3]  # 不写入档案的敏感域

# ============ 私密站接入（方案 A · 受控浏览器） ============
private_sites:
  mode: controlled_browser     # A 受控浏览器 | B 手动投喂 | C 仅登记
  user_authorized: true
  read_only: true
  persist_cookies: false
  persist_pages: false
  level_rules:
    L1_auto: [课表, 成绩, 考试安排, 借阅, 一卡通余额, 场馆预约状态]
    L2_confirm: [资助申请状态, 就业投递记录, 培养进度]
    L3_forbidden: [缴费金额, 银行卡, 身份证, 家庭信息, 邮件正文, 心理记录]

# ============ 能力域开关（19 域） ============
domains:
  S1: true   # 课程答疑        S2: true   # 课堂与笔记
  S3: true   # 作业与考核      S4: true   # 备考与记忆
  S5: true   # 学术表达        S6: true   # 语言能力
  F1: true   # 校园事务        F2: true   # 作息与专注
  F3: true   # 身心与社交      F4: true   # 财务与安全
  F5: true   # 健康与运动      F6: true   # 军训与志愿
  F7: true   # 升学深造        F8: true   # 求职与竞赛
  R1: true   # 文献检索与管理  R2: true   # 实验与数据
  R3: true   # 科研工具与代码  R4: true   # 学术产出与投稿
  R5: true   # 学术规范与伦理
"""))

# ---------------- scripts/qihang.sh ----------------
reg_lines = []
for d in DOMAINS:
    if d["external"]:
        nm, repo, inst = d["external"][0]
        reg_lines.append(f'{d["id"]}|{d["slug"]}|{repo}|{inst}')
REG = "\n".join(reg_lines)

files.append(("scripts/qihang.sh", f"""#!/usr/bin/env bash
# 「启航」学伴包 v2.0 · 三级结构管理脚本
# 用法: bash qihang.sh {{status|probe|install|domains|registry|new-term}}
set -uo pipefail

ROOT="$(cd "$(dirname "${{BASH_SOURCE[0]}}")/.." && pwd)"
SKILLS_DIR="${{HOME}}/.claude/skills"
CONFIG="${{ROOT}}/config.yaml"
PUBLIC="${{ROOT}}/references/dlut-official-sites.md"
PRIVATE="${{ROOT}}/references/dlut-login-sites.md"
DOMAINS_DIR="${{ROOT}}/domains"

# 域ID|目录slug|主库外仓库|安装命令   （每个域取第一条库外候选作代表）
REGISTRY="{REG}"

is_installed() {{ [ -d "${{SKILLS_DIR}}/$1" ]; }}

cmd_domains() {{
  echo "「启航」域清单（Level 2）"
  echo "----------------------------------------"
  for d in "$DOMAINS_DIR"/*/; do
    [ -d "$d" ] || continue
    id=$(basename "$d")
    local_file="$d/skills/local"
    n=$(find "$local_file" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    printf '  %-24s 库内skill: %s\\n' "$id" "$n"
  done
  echo "----------------------------------------"
  echo "共 $(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') 个域"
}}

cmd_status() {{
  echo "「启航」学伴包 v2.0 · 状态"
  echo "----------------------------------------"
  echo "[1级] skill 库"
  for f in library/clarity.md library/domain-review.md library/output-spec.md; do
    [ -f "$ROOT/$f" ] && printf '  ✓ %s\\n' "$f" || printf '  ✗ %s\\n' "$f"
  done
  echo "[2级] 域"
  nd=$(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  ns=$(find "$DOMAINS_DIR" -path '*/skills/local/*/SKILL.md' | wc -l | tr -d ' ')
  printf '  ✓ %s 个域 / %s 个库内 skill\\n' "$nd" "$ns"
  echo "[3级] 库外 skill 就绪度"
  local ok=0 total=0
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    total=$((total+1))
    nm=$(basename "$repo")
    if is_installed "$nm"; then ok=$((ok+1)); fi
  done <<< "$REGISTRY"
  printf '  已装 %s / %s（库外为兜底，不装也可用库内）\\n' "$ok" "$total"
  echo "[资源] DUT 信息库"
  [ -f "$PUBLIC" ]  && printf '  ✓ 公开站 %s 行\\n' "$(grep -c '^|' "$PUBLIC")" || echo "  ✗ 公开站缺失"
  [ -f "$PRIVATE" ] && printf '  ✓ 私密站 %s 行\\n' "$(grep -c '^|' "$PRIVATE")" || echo "  ✗ 私密站缺失"
}}

cmd_probe() {{
  echo "探测库外候选缺失项（不执行安装）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    nm=$(basename "$repo")
    is_installed "$nm" || printf '  %s 域缺 → %s\\n      装: %s\\n' "$id" "$repo" "$inst"
  done <<< "$REGISTRY"
  echo ""
  echo "提示：库内 skill 已全部就绪，库外仅作增强，可跳过。"
}}

cmd_install() {{
  echo "安装库外候选（已装跳过；可选）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    nm=$(basename "$repo")
    if is_installed "$nm"; then printf '  %s 已装，跳过\\n' "$id"; continue; fi
    case "$inst" in
      npx*) printf '  %s 安装中: %s\\n' "$id" "$inst"; eval "$inst" || printf '  ! %s 失败，含库内降级\\n' "$id" ;;
      *)    printf '  %s 请在 Agent 中执行: %s\\n' "$id" "$inst" ;;
    esac
  done <<< "$REGISTRY"
}}

cmd_registry() {{
  echo "DUT 公开信息库: $PUBLIC"
  [ -f "$PUBLIC" ] && {{
    echo "  表格行: $(grep -c '^|' "$PUBLIC")"
    echo "  已核验: $(grep -o '✅' "$PUBLIC" | wc -l | tr -d ' ')"
    echo "  待核实: $(grep -o '⚠️' "$PUBLIC" | wc -l | tr -d ' ')"
  }}
  echo "DUT 私密站清单: $PRIVATE"
  [ -f "$PRIVATE" ] && echo "  表格行: $(grep -c '^|' "$PRIVATE")"
}}

cmd_new_term() {{
  [ -f "$CONFIG" ] && {{ cp "$CONFIG" "${{CONFIG}}.bak.$(date +%Y%m%d%H%M%S)"; echo "已备份 config.yaml"; }}
  echo "新学期重置：改 ${{CONFIG}} 的 term / courses / exam_weeks 三项即可。"
  echo "1级库规则、19 个域、DUT 绑定均无需改动。"
}}

case "${{1:-status}}" in
  status)   cmd_status ;;
  probe)    cmd_probe ;;
  install)  cmd_install ;;
  domains)  cmd_domains ;;
  registry) cmd_registry ;;
  new-term) cmd_new_term ;;
  *) echo "用法: bash qihang.sh {{status|probe|install|domains|registry|new-term}}"; exit 1 ;;
esac
"""))

# ---------------- commands ----------------
files.append(("commands/qihang.md", """---
description: 「启航」学伴包入口（1级库）：需求明确 → 锁定域 → 锁定skill → 库内优先
argument-hint: [你的需求，可留空]
---

按 1 级 skill 库规则处理：$ARGUMENTS

1. **需求明确**：读 `~/.claude/skills/qihang/library/clarity.md`，拆 6 槽位，算 `U = 1 − ∏cᵢ`。
   `U > 5%` → 追问（最多 3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。
2. **锁定域**：读 `domains/_registry.md`，用触发词匹配；多域命中走跨域串联。
3. **域审查**：读 `library/domain-review.md`，用该域「不覆盖」条目复核，越界则改锁。
4. **锁定 skill**：读 `domains/<域>/_domain.md` → 用**库内 skill**（`skills/local/`）。
5. **库外兜底**：仅当库内不满足，才读 `skills/external.md` 走安装。
6. **输出**：按 `library/output-spec.md`，≤6 条要点，写入学习档案。
"""))

files.append(("commands/qihang-dlut.md", """---
description: 校情横切：查大连理工大学学院 / 校区 / 教务 / 职能 / 私密站
argument-hint: [要查的单位或服务]
---

查询：$ARGUMENTS

**硬性规则**
1. **先读** `~/.claude/skills/qihang/references/dlut-official-sites.md`（公开站 ACTIVE）；涉及登录项再读 `dlut-login-sites.md`。
2. 命中 → 输出 `【结论】+【网址】+【状态 ✅/⚠️】+【备注】`。
3. **未命中 → 固定回复**：「信息库未收录该条目，建议访问 https://www.dlut.edu.cn/ 核实」。
4. **禁止编造**任何 dlut.edu.cn 下的 URL、电话或单位名。
5. 标 ⚠️ 的条目必须带上「待核实」。

**私密站（方案 A）**：用受控浏览器打开 → 请你本人登录 → 我只读读取 → **不落盘、不外传**。
涉 L3 级（缴费金额/银行卡/身份证/邮件正文/心理记录）**一律不读取**。
"""))

for d in DOMAINS:
    cat = CATS[d["cat"]][0]
    trig = "、".join(d["triggers"][:6])
    files.append((f"commands/qihang-{d['id'].lower()}.md", f"""---
description: {d['id']} {d['name']}（{cat}）：{trig}
argument-hint: [具体需求]
---

命中域 **{d['id']} · {d['name']}**（{cat}）

需求：$ARGUMENTS

1. 读 `~/.claude/skills/qihang/domains/{d['id']}-{d['slug']}/_domain.md` 确认边界
2. 用**库内 skill** `{d['local']['slug']}` 执行（`skills/local/{d['local']['slug']}/SKILL.md`）
3. 库内不满足 → 读 `skills/external.md` 走库外安装
4. 按 `library/output-spec.md` 输出 ≤6 条要点
5. DUT 绑定点见 `_domain.md`，涉及登录用方案 A（只读）
"""))

# ---------------- README ----------------
files.append(("README.md", f"""# 「启航」新生学习生活一体化学伴包 v2.0

> **三级结构：skill 库（1级）→ 域（2级）→ skill（3级）**
> 面向大连理工大学 2026 级本科新生 ｜ 强绑定 DUT 公开站与需登录的私密站
> 适配：连小理 / Claude Code / Codex / Cursor / Copilot

---

## 1. 三级结构

```
qihang-pack/
├── SKILL.md                  入口（安装单元）
├── config.yaml               学校绑定 + 学期配置 + 域开关
├── library/                  ★1 级 · skill 库（既是 skill 也是库）
│   ├── SKILL.md              库本体
│   ├── clarity.md            职责1：需求明确（6 槽位 + 澄清门）
│   ├── domain-review.md      职责2：域审查（锁定/越界/跨域/无域兜底）
│   └── output-spec.md        职责3：输出规范（模板 + 简略原则）
├── domains/                  ★2 级 · 域（{len(DOMAINS)} 个）
│   ├── _registry.md          域总表 + 方向自查
│   └── <域ID>-<slug>/
│       ├── _domain.md        域定义：边界 / 触发词 / DUT 绑定点
│       └── skills/           ★3 级 · skill
│           ├── local/<name>/SKILL.md   库内 skill（优先，无需安装）
│           └── external.md             库外候选（库内不满足才装）
├── references/
│   ├── dlut-official-sites.md   DUT 公开站信息库
│   ├── dlut-login-sites.md      DUT 私密站清单（方案 A）
│   ├── skill-sources.md         12 个 skill 探测平台
│   ├── validation-report.md     验收报告
│   └── 需求确认书-v2三级结构.md
├── commands/                    斜杠命令
└── scripts/
    ├── qihang.sh                管理脚本
    └── build_qihang_v2.py       结构生成器（改域后重跑）
```

## 2. 工作流（严格按序）

```
用户需求
  ↓ ①需求明确  library/clarity.md             6 槽位 + 澄清门，U ≤ 5%
  ↓ ②锁定域    domains/_registry.md            触发词匹配
  ↓ ③域审查    library/domain-review.md        边界复核、越界改锁
  ↓ ④锁定skill domains/<域>/_domain.md         读库内 skill
  ↓ ⑤库内优先  skills/local/                   命中即用，无需安装
  ↓ ⑥库外兜底  skills/external.md              仅库内不满足才安装
  ↓ ⑦输出      library/output-spec.md          ≤6 条要点 + 写学习档案
```

**核心规则：库内优先** —— 库内有就不装库外，避免低星 / 无许可证 / 需 API Key 的第三方风险。

## 3. 19 个域（方向自查：学习 / 生活 / 科研全覆盖）

| 大类 | 域 |
|---|---|
| **S 学习（6）** | {" ｜ ".join(d["id"]+" "+d["name"] for d in DOMAINS if d["cat"]=="S")} |
| **F 生活（8）** | {" ｜ ".join(d["id"]+" "+d["name"] for d in DOMAINS if d["cat"]=="F")} |
| **R 科研（5）** | {" ｜ ".join(d["id"]+" "+d["name"] for d in DOMAINS if d["cat"]=="R")} |

**自查结果**：19 域 × 每域 1 个库内 skill = 19 个库内 skill；{len([d for d in DOMAINS if d["external"]])} 个域有库外候选；**{len([d for d in DOMAINS if not d["external"]])} 个域为方向空白**（{"、".join(d["id"] for d in DOMAINS if not d["external"])}），直接依赖库内自建 skill。

## 4. 安装与使用

```bash
# 1) 放进 skills 目录
cp -r qihang-pack ~/.claude/skills/qihang
# 2) 安装斜杠命令
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/
# 3) 查看状态（库内 skill 开箱即用，库外为可选增强）
bash ~/.claude/skills/qihang/scripts/qihang.sh status
```

```bash
bash scripts/qihang.sh status     # 三级结构完整度
bash scripts/qihang.sh domains    # 19 域清单
bash scripts/qihang.sh probe      # 库外候选缺失项
bash scripts/qihang.sh registry   # DUT 信息库统计
bash scripts/qihang.sh new-term   # 换学期重置
```

## 5. DUT 融入

| 类型 | 文件 | 融入方式 |
|---|---|---|
| 公开站 | `references/dlut-official-sites.md` | 160 条，19 个域的 `_domain.md` 各自标注绑定点 |
| 私密站 | `references/dlut-login-sites.md` | 19 个需登录站点，**方案 A 受控浏览器 + 只读**，分 L1/L2/L3 授权 |

**私密站三条铁律**：① 只读 ② 不外传 ③ 不落盘。L3 级（缴费/银行卡/身份证/邮件正文/心理记录）**一律不读取**。

## 6. 复用

| 换什么 | 改哪里 | 成本 |
|---|---|---|
| 换课程/学期 | `config.yaml` 的 `courses` / `term` / `exam_weeks` | 3 行 |
| 加/改域 | `scripts/_build/build_qihang_v2.py` 的 `DOMAINS` → 重跑 | 改数据即可 |
| 加库内 skill | 对应域 `skills/local/<name>/SKILL.md` | 1 个文件 |
| 加库外候选 | 对应域 `skills/external.md` | 1 行 |
| 扩 DUT 信息库 | `references/dlut-*.md` | 1 行 |

## 7. 免责

- 外部 skill 均为公开开源项目（2026-10-01 检索），安装前请读源码与许可证。
- `CC-BY-NC` 禁止商用；部分仓库无 LICENSE（study-skill / math-skill / gurukul-ai）。
- `sickn33/agentic-awesome-skills`（3113 脚本、含攻击性技能）**禁止整体安装**。
- DUT 信息库中标 ⚠️ 的条目未经核验，请勿直接使用。
- 本包自身：MIT。
"""))

for rel, content in files:
    W(rel, content)

print(f"生成 {len(files)} 个外围件 → {OUT}")
print("含命令:", len([f for f,_ in files if f.startswith("commands/")]))
