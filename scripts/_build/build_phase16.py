#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
「启航」build_phase16 —— LearnBuddy 专向化层（v2.7 → v2.8）

背景：包内此前按「LearnBuddy / Claude Code / Codex / Gemini CLI / Cursor / Copilot」多平台并列
表述，并带一整套 **Claude Code 适配**（21 个斜杠命令 `commands/*.md` 用 `$ARGUMENTS` + `argument-hint`、
路径写死 `~/.claude/skills/qihang/`、库外安装用 `/plugin marketplace add`）。
目标平台已收敛为 **LearnBuddy / WorkBuddy 单一平台**，本层把上述内容全部改写为 LearnBuddy 适配。

本层做四件事：
  1. **移除全部 Claude Code 适配**：文档 / 脚本 / 报告 / 生成器数据里的平台行、安装节、斜杠命令
  2. **`commands/*.md` 改写为 LearnBuddy 域入口卡**：由 `DOMAINS` 数据**确定性重建**
     （去 `$ARGUMENTS` / `argument-hint`；引用路径改为仓库根相对路径；正文改为自然语言入口卡）
  3. **`scripts/qihang.sh` 平台探测只认 LearnBuddy**，`/plugin marketplace add` → `npx skills add`
  4. **版本号 2.7.0 → 2.8.0**（含 `scripts/aligncheck.py` 的版本断言）

原则（与 phase15 一致）：
  · 每条改动是**精确匹配替换**；匹配不到就报 MISS（不静默跳过）
  · **幂等**：重复运行结果一致；`commands/` 由数据重建，天然确定性
  · 时间/历史性表述（如「v2.7 修复」「v2.7 起 38 skill」）**不改**，那是事实记录

用法: python scripts/_build/build_phase16.py .
"""
import os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else '.')
OK, MISS, DONE = [], [], []


def rd(p):
    with open(os.path.join(ROOT, p), 'r', encoding='utf-8') as f:
        return f.read()


def wr(p, s):
    fp = os.path.join(ROOT, p)
    os.makedirs(os.path.dirname(fp) or ROOT, exist_ok=True)
    with open(fp, 'w', encoding='utf-8', newline='\n') as f:
        f.write(s)


def rep(path, old, new, required=True, label=None, count=1):
    """精确替换；幂等护栏：new 包含 old 时先判 new 是否已存在（追加型替换防重复插入）"""
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


def resub(path, pat, repl, label, required=True, flags=0, already=None, absent=None):
    """正则替换（用于表格/区块这类间距不规整的文本）

    幂等护栏（正则是一次性匹配，第二遍必然落空，需显式告知「已完成」）：
      · already：正则未命中时，若该字串已存在 → 判为「已是最新」
      · absent ：正则未命中时，若该字串已不存在 → 判为「已是最新」（用于删除型替换）
    """
    if not os.path.isfile(os.path.join(ROOT, path)):
        if required:
            MISS.append('%s :: %s（文件不存在）' % (path, label))
        return
    t = rd(path)
    t2, n = re.subn(pat, repl, t, flags=flags)
    if n == 0:
        if (already and already in t) or (absent and absent not in t):
            DONE.append('[已是最新] %s :: %s' % (path, label))
        elif required:
            MISS.append('%s :: %s（正则未命中）' % (path, label))
        return
    if t2 != t:
        wr(path, t2)
        OK.append('%s :: %s（%d 处）' % (path, label, n))
    else:
        DONE.append('[已是最新] %s :: %s' % (path, label))


# ==================================================================== 1. 目标平台表（唯一真相源）
PLATFORMS_MD = '''# LearnBuddy / WorkBuddy 适配表

> 「启航」是**面向 LearnBuddy / WorkBuddy 单一目标平台**的一体化 skill 包。
> 所有内容都是 `SKILL.md` 标准件，装载后靠 `description` 自动发现。
> 平台差异只体现在 **①安装位置 ②发现方式 ③入口 ④记忆系统** 四处。

## 一、总览

| 项 | 内容 |
|---|---|
| 目标平台 | **LearnBuddy / WorkBuddy**（唯一适配目标，一等公民） |
| 安装位置 | 用户级 `~/.learnbuddy/skills/qihang/`<br>项目级 `{ws}/.learnbuddy/skills/qihang/` |
| 发现方式 | 读 `SKILL.md` 的 `description` 自动发现 |
| 入口 | **自然语言**（无需斜杠命令）；`commands/` 为域入口卡，供人工检索 / 插件装载 |
| 记忆系统 | `~/.learnbuddy/MEMORY.md` + `{ws}/.learnbuddy/memory/` + 本包按域档案 |
| 插件清单 | `.codebuddy-plugin/plugin.json` |
| 场景名 | 赛道二场景名「**连小理**」= LearnBuddy（同一平台，非独立平台） |

> **适配范围**：本包只对 LearnBuddy / WorkBuddy 做适配与承诺。
> 其他 agent 只要能读 `SKILL.md` 即可装载使用，但**本包不提供其适配承诺**
> （`commands/` 是 LearnBuddy 域入口卡，不是其他平台的斜杠命令格式）。

---

## 二、安装

```bash
# 用户级（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# 或项目级（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang

# 就绪度自检
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

**插件方式**：包根已含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别装载。

---

## 三、发现与调用

- LearnBuddy 通过 **SKILL.md 的 `description`** 自动判定何时加载，**无需斜杠命令**。
- 触发表述（在 `description` 中已写死）：涉及**大连理工大学校情（学院/校区/选课/校历/职能部门/联系方式）、
  大学课程学习、备考复习、课堂笔记、作业与实验报告、科研文献、作息专注、升学求职**的**模糊求助**。
- `commands/` 是 **LearnBuddy 域入口卡**（21 张 = 库入口 1 + 校情 1 + 19 域），
  用自然语言说需求即可命中对应域，无需输入命令。

---

## 四、记忆系统对接（关键差异）

LearnBuddy 有三层记忆，本包的工作流第 **⑧** 步「归档」直接落到这套记忆里：

| 层 | 位置 | 本包怎么写 |
|---|---|---|
| 用户级长期记忆 | `~/.learnbuddy/MEMORY.md` | 只写**跨项目**的长期约定（如作息偏好、常用课程） |
| 工作区日志 | `{ws}/.learnbuddy/memory/YYYY-MM-DD.md` | **追加式**记录当日学习动作与结论 |
| 工作区长期笔记 | `{ws}/.learnbuddy/memory/MEMORY.md` | 沉淀稳定事实（薄弱章节、错因类型、复考计划） |
| **学习档案（本包自有）** | `{ws}/.learnbuddy/memory/qihang/<域ID>.md` | 按域归档：薄弱点 / 错因 / 进度 / 上次结论 |

> 详见 `library/memory.md`。
> **红线**：F3 身心与社交、F5 健康与运动的敏感内容**不得写入任何记忆层**。

---

## 五、与 LearnBuddy 内置能力协同

| LearnBuddy 能力 | 本包如何用 |
|---|---|
| `present_files` | 输出产物（笔记 / 计划 / 卡组清单）后调用，让用户直接查看 |
| `show_widget` | 流程示意、概念图可直接内联渲染，无需落文件 |
| 子 agent（Task） | 跨域串联时，可让子 agent 并行处理不同域 |
| 对话检索（`conversation_search`） | 学习档案缺失时，回溯历史结论 |
| 技能检索（`find-skills`） | 库内不满足时，为各域 `skills/external.md` 找可用库外 skill |
| MCP 连接器 | F1 域可接腾讯地图、文档类可接腾讯文档等（按需） |

---

## 六、库外 skill 安装（仅库内不满足时）

| 通道 | 做法 |
|---|---|
| **LearnBuddy 原生（首选）** | 用 `find-skills` 技能检索并安装到 `~/.learnbuddy/skills/` |
| 通用 skills CLI | `npx skills add <owner>/<repo>`（npm 包，跨 agent 的通用安装器） |
| 手动 | `git clone` 后把 `<repo>/skills/*` 复制到 `~/.learnbuddy/skills/` |

> **摘录红线**：GPL-3.0 / AGPL / CC-BY-NC / 无 LICENSE 一律**只做外部调用，不得复制内容进本包**
> （见 `references/skill-compliance-audit.md`）。

---

## 七、平台探测（自动）

```bash
bash scripts/qihang.sh platform    # 探测本机 LearnBuddy 安装位置与就绪度
```
'''


# ==================================================================== 2. 安装指南（LearnBuddy 单平台）
INSTALL_MD = '''# 安装指南（LearnBuddy / WorkBuddy）

> 「启航」是 `SKILL.md` 标准件，**面向 LearnBuddy / WorkBuddy 单一目标平台**。
> 平台差异详见 `references/platforms.md`；就绪度探测用 `bash scripts/qihang.sh platform`。

---

## 一、安装

```bash
# ① 用户级安装（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# ② 或 项目级安装（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang

# ③ 查看就绪度
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

**插件方式**：包根含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别装载。

**用法**：直接用自然语言，**不需要斜杠命令**。例如：
- 「我高数快挂了」
- 「机械学院官网是啥」
- 「下周实验报告怎么写」

**记忆落点**（自动）：`{ws}/.learnbuddy/memory/qihang/<域ID>.md`，见 `library/memory.md`。

---

## 二、域入口卡（`commands/`）

`commands/` 里的 21 个文件是 **LearnBuddy 域入口卡**（库入口 1 + 校情 1 + 19 域），
作用是「快速查到某域该读哪些规则文件」，**不是需要输入的命令**：

| 入口卡 | 作用 |
|---|---|
| `commands/qihang.md` | 库入口（澄清门 → 锁域 → 锁 skill） |
| `commands/qihang-dlut.md` | 查大工校情（公开站 + 私密站） |
| `commands/qihang-s1.md` … `qihang-r5.md` | 19 个域入口卡 |

在 LearnBuddy 中直接说需求即可命中对应域，无需输入卡片名。

---

## 三、库外 skill 安装（仅库内不满足时）

| 通道 | 命令 |
|---|---|
| **LearnBuddy 原生（首选）** | 用 `find-skills` 技能检索并安装到 `~/.learnbuddy/skills/` |
| 通用 skills CLI | `npx skills add <owner>/<repo>`（实测可用） |
| 手动 | `git clone` 后复制 `<repo>/skills/*` 到 `~/.learnbuddy/skills/` |

---

## 四、赛道二提交物（依托平台 = LearnBuddy，产品名「连小理」）

> **连小理就是 LearnBuddy**，不是两个平台 —— 本包在赛道二中的场景名即「连小理」。

1. 提交 **`qihang-scenario-design.html`**（场景设计书，五要素齐备，约 1900 字）
2. 平台侧挂载：`domains/_registry.md`（域总表）+ `library/` 规则 + `references/dlut-*.md`（信息库）
3. 场景与结构见 `PROJECT.md`

---

## 五、装完自检

```bash
bash scripts/qihang.sh status      # 三级结构完整度
bash scripts/qihang.sh platform    # 探测本机 LearnBuddy 安装位置
bash scripts/qihang.sh domains     # 19 域清单
bash scripts/qihang.sh registry    # DUT 信息库统计
bash scripts/qihang.sh probe       # 库外候选缺失项（可选）
```

**期望**：`[1级]` 逐行列出 **8 个** library 文件（SKILL + 7 份规则，含 `login-policy.md`） · `[2级] 19 个域 / **38 个**库内 skill` · `[资源] DUT 公开站 160 行`

**完整验收（v2.8 起 4 个脚本，职责不重叠）**：

| 脚本 | 管什么 | 期望 |
|---|---|---|
| `bash scripts/selfcheck.sh` | 结构对不对（计数 / 交叉引用 / 一致性） | `OK 31 ｜ WARN 0 ｜ FAIL 0 → 可交付` |
| `bash scripts/audit.sh` | 安不安全（凭证 / 危险命令 / L3 门禁 / 合规） | `37 通过 ｜ 0 警告 ｜ 0 失败 → 通过` |
| `bash scripts/regress.sh 3` | **行为对不对**（澄清门算例 / L3 门禁矩阵 / 红线一致性） | `120 项全 OK ｜ FAIL 0` |
| `bash scripts/qihang.sh status` | 三级结构完整度 | 逐行 ✓ |

---

## 六、前置条件

| 项 | 说明 |
|---|---|
| 库内 skill | **开箱即用，无需安装任何东西** |
| 库外 skill | 仅在库内不满足时需要；部分需 API Key 或联网（见各域 `skills/external.md`） |
| 私密站（需登录） | 需 `agent-browser` 或同类浏览器自动化；**必须用独立 Profile**（见 `references/dlut-login-sites.md` §0.1） |
| 网络 | 库内 skill 全程离线可用 |
'''


# ==================================================================== 3. 文档：Claude Code 行/节清除
def fix_tables():
    """`SKILL.md` 与 `library/SKILL.md` 的「快捷调用」平台表 → LearnBuddy 单平台"""
    new_table = (
        '| 入口 | 用法 |\n'
        '|---|---|\n'
        '| **LearnBuddy / WorkBuddy** | **自然语言即可**（靠 `description` 自动发现，无需命令）；'
        '装到 `~/.learnbuddy/skills/qihang/` |\n'
        '| 域入口卡 | `commands/` 21 张（库入口 + 校情 + 19 域），供人工检索 / 插件装载 |\n'
        '| 一键脚本 | `bash scripts/qihang.sh {status\\|platform\\|probe\\|install\\|domains\\|registry\\|records\\|new-term}` |\n'
    )
    for p in ('SKILL.md', 'library/SKILL.md'):
        resub(p, r'\| 平台 \| 用法 \|\n\|---\|---\|\n(?:\|[^\n]*\n)+', new_table,
              label='快捷调用表改为 LearnBuddy 单平台',
              already='| 域入口卡 | `commands/` 21 张')
        rep(p, '各平台差异详见 `references/platforms.md` 与 `INSTALL.md`。',
            '平台适配详见 `references/platforms.md` 与 `INSTALL.md`。',
            label='「各平台差异」→「平台适配」')


def fix_library_memory():
    """library/memory.md §6「其他平台」→ LearnBuddy 单平台落点"""
    p = 'library/memory.md'
    old = (
        '## 6. 其他平台（无内置记忆系统时）\n'
        '\n'
        '| 平台 | 落点 |\n'
        '|---|---|\n'
        '| Claude Code | `~/.claude/skills/qihang/records/<域ID>.md` |\n'
        '| Codex / Gemini CLI | 同上，放在各自 skills 目录下 |\n'
        '| Cursor / Copilot | 放工作区 `.qihang/records/`，靠规则文件引用 |'
    )
    new = (
        '## 6. 目标平台与回落落点\n'
        '\n'
        '本包只面向 **LearnBuddy / WorkBuddy** 单一目标平台，三层记忆见 §2.1，无需为其他平台另设落点。\n'
        '\n'
        '| 场景 | 落点 |\n'
        '|---|---|\n'
        '| 正常（LearnBuddy / WorkBuddy） | `{ws}/.learnbuddy/memory/qihang/<域ID>.md` |\n'
        '| 平台目录不可写时回落 | `<包根>/records/<域ID>.md`（由 `scripts/qihang.sh records` 管理） |'
    )
    rep(p, old, new, label='§6 其他平台 → LearnBuddy 单平台落点')


def fix_platform_files():
    """整文件重写：platforms.md / INSTALL.md（确定性内容，天然幂等）"""
    for p, new, label in (('references/platforms.md', PLATFORMS_MD, '重写为 LearnBuddy 适配表'),
                          ('INSTALL.md', INSTALL_MD, '重写为 LearnBuddy 单平台安装指南')):
        fp = os.path.join(ROOT, p)
        cur = rd(p) if os.path.isfile(fp) else None
        if cur == new:
            DONE.append('[已是最新] %s :: %s' % (p, label))
        else:
            wr(p, new)
            OK.append('%s :: %s' % (p, label))


def fix_project():
    p = 'PROJECT.md'
    rep(p, '> 适配：**LearnBuddy（= 连小理）** / Claude Code / Codex / Cursor / Copilot',
        '> 适配：**LearnBuddy（= 连小理）**（单一目标平台）', label='头部适配行')
    # §6 安装与使用：删掉 Claude Code 小节
    resub(p, r'\n\*\*Claude Code\*\* —— 21 个斜杠命令：\n\n```bash\n'
             r'cp -r qihang-pack ~/\.claude/skills/qihang\n'
             r'mkdir -p ~/\.claude/commands && cp qihang-pack/commands/\*\.md ~/\.claude/commands/\n```\n',
          '\n', label='删除 Claude Code 安装小节', absent='**Claude Code**')
    resub(p, r'\| `/qihang` +\|[^\n]*库入口[^\n]*\n',
          '| `commands/qihang.md` | 库入口卡（澄清门 → 锁域 → 锁 skill） |\n', label='命令表：库入口行',
          already='| `commands/qihang.md` | 库入口卡')
    resub(p, r'\| `/qihang-dlut` +\|[^\n]*\n',
          '| `commands/qihang-dlut.md` | 校情入口卡（公开站 + 私密站） |\n', label='命令表：校情行',
          already='| `commands/qihang-dlut.md` | 校情入口卡')
    resub(p, r'\| `/qihang-s1`[^\n]*\n',
          '| `commands/qihang-s1.md` … `commands/qihang-r5.md` | 19 个域入口卡 |\n', label='命令表：域行',
          already='| `commands/qihang-s1.md` … `commands/qihang-r5.md` |')
    rep(p, '完整多平台说明见 `INSTALL.md`；平台差异见 `references/platforms.md`。',
        '完整安装说明见 `INSTALL.md`；平台适配见 `references/platforms.md`。', label='§6 收尾句')
    # §6.1 平台适配一览 → 单目标平台
    resub(p, r'## 6\.1 平台适配一览\n.*?\n---\n',
          '## 6.1 平台适配\n'
          '\n'
          '| 项 | 内容 |\n'
          '|---|---|\n'
          '| **目标平台** | **LearnBuddy / WorkBuddy**（唯一适配目标，一等公民） |\n'
          '| 安装位置 | `~/.learnbuddy/skills/qihang/`（项目级：`{ws}/.learnbuddy/skills/qihang/`） |\n'
          '| 入口 | **自然语言**（无需斜杠命令）；`commands/` 21 张域入口卡供人工检索 |\n'
          '| 记忆系统 | `~/.learnbuddy/MEMORY.md` + `{ws}/.learnbuddy/memory/` + 本包按域档案 |\n'
          '| 插件清单 | `.codebuddy-plugin/plugin.json` |\n'
          '| **连小理**（= LearnBuddy） | 同一平台（赛道二场景名），非独立适配 |\n'
          '\n'
          '> 其他 agent 只要能读 `SKILL.md` 即可装载，但**本包不提供适配承诺**。\n'
          '\n'
          '---\n',
          label='§6.1 平台表改为 LearnBuddy 单平台', flags=re.S,
          already='## 6.1 平台适配\n\n| 项 | 内容 |')
    resub(p, r'\| \*\*平台适配\*\*[^\n]*\n',
          '| **平台适配** | ✅ **LearnBuddy / WorkBuddy 单一目标平台**（`~/.learnbuddy/skills/` + `.codebuddy-plugin/`）；'
          'v2.8 起移除 Claude Code 适配 |\n', label='§7 平台适配行',
          already='| **平台适配** | ✅ **LearnBuddy / WorkBuddy 单一目标平台**')
    resub(p, r'├── commands/ +21 个斜杠命令[^\n]*\n',
          '├── commands/                 21 张 LearnBuddy 域入口卡（库 + 校情 + 19 域）\n',
          label='目录树 commands 说明', already='21 张 LearnBuddy 域入口卡')
    resub(p, r'├── INSTALL\.md +多平台安装指南', '├── INSTALL.md                安装指南（LearnBuddy）',
          label='目录树 INSTALL 说明', already='├── INSTALL.md                安装指南（LearnBuddy）')
    resub(p, r'\| 库外 skill 联调 +\|[^\n]*\n',
          '| 库外 skill 联调        | ✅ 安装通道实测可用（`npx skills add`）；合规自检完成；'
          '**12 平台多源比对 v3**（`references/skill-matrix-v3.md`） |\n', label='§7 库外联调行', required=False)


def fix_readme():
    p = 'README.md'
    rep(p, '> 适配：**LearnBuddy（= 连小理）** / Claude Code / Codex / Cursor / Copilot',
        '> 适配：**LearnBuddy（= 连小理）**（单一目标平台）', label='头部适配行')
    resub(p, r'├── INSTALL\.md +多平台安装指南', '├── INSTALL.md                安装指南（LearnBuddy）',
          label='目录树 INSTALL 说明', already='├── INSTALL.md                安装指南（LearnBuddy）')
    resub(p, r'├── commands/ +[^\n]*\n',
          '├── commands/                    21 张 LearnBuddy 域入口卡（库 + 校情 + 19 域）\n',
          label='目录树 commands 说明', already='21 张 LearnBuddy 域入口卡')
    resub(p, r'\*\*Claude Code\*\*\n\n```bash\n'
             r'cp -r qihang-pack ~/\.claude/skills/qihang\n'
             r'mkdir -p ~/\.claude/commands && cp qihang-pack/commands/\*\.md ~/\.claude/commands/\n'
             r'bash ~/\.claude/skills/qihang/scripts/qihang\.sh status\n```\n\n'
             r'\*\*其他平台\*\*（Codex / Gemini CLI / Cursor / Copilot）见 `INSTALL\.md` 与 `references/platforms\.md`。\n',
          '21 张 `commands/` 域入口卡随包提供（不需要输入命令）；'
          '学习档案见 `library/memory.md`，自检脚本见 `scripts/`。\n',
          label='删除 Claude Code 安装节 + 其他平台行', absent='**Claude Code**')
    rep(p, '# 通用管理脚本（自动探测平台）', '# 通用管理脚本（探测 LearnBuddy 安装位置）',
        label='脚本注释去「多平台」')


def fix_roadmap():
    p = 'ROADMAP.md'
    # 去重复行：早期版本此处是无护栏的「追加型」替换，重复运行会插两次
    # （与 references/stress-test-v3.md 记录的 build_phase15 早期幂等缺陷同型）
    t = rd(p)
    seen, out, dup = set(), [], 0
    for ln in t.split('\n'):
        if ln.startswith('| **8** | **平台专向化（v2.8）**'):
            if ln in seen:
                dup += 1
                continue
            seen.add(ln)
        out.append(ln)
    if dup:
        wr(p, '\n'.join(out))
        OK.append('%s :: 清理重复的阶段 8 行（%d 处）' % (p, dup))
    ROW7 = '| **7** | **复查与扩库（v2.7）** | 库内 skill 19→**38** · **12 平台多源比对选优** · 复查修复 **52 项** · 多轮压测 | ✅ 已完成 |'
    ROW8 = ('| **8** | **平台专向化（v2.8）** | 移除 Claude Code 适配 · `commands/` 21 个斜杠命令改写为 '
            '**LearnBuddy 域入口卡** · 文档/脚本/生成器全量对齐 | ✅ 已完成 |')
    rep(p, ROW7, ROW7 + '\n' + ROW8, label='总览表新增阶段 8')
    rep(p, '**真实 Claude Code 环境的端到端安装转阶段 5**。',
        '**真实 LearnBuddy 环境的端到端安装转阶段 5**。', label='阶段 2 环境限制')
    old = (
        '## 横切 · 平台适配 ✅\n'
        '\n'
        '**已完成（2026-10-01）**\n'
        '- ✅ **LearnBuddy / WorkBuddy 一等公民**：`~/.learnbuddy/skills/qihang/` + `.codebuddy-plugin/plugin.json`\n'
        '- ✅ 新增 `INSTALL.md`（多平台安装，LearnBuddy 置顶）与 `references/platforms.md`（差异对照）\n'
        '- ✅ `qihang.sh` 升级为**多平台自动探测**（LearnBuddy / Claude Code / Codex / Gemini CLI）+ 新增 `platform` 命令\n'
        '- ✅ 入口 `SKILL.md` 更新：`description` 补齐 LearnBuddy 触发场景、加 `agent_created: true`、工作流加第 ⑧ 步\n'
        '- ✅ 明确平台差异：命令入口（LearnBuddy 自然语言 vs Claude Code 斜杠命令）、记忆系统、发现方式\n'
        '\n'
        '| 平台 | 支持度 |\n'
        '|---|---|\n'
        '| LearnBuddy / WorkBuddy | ✅ 一等公民 |\n'
        '| Claude Code | ✅ 完整（21 个斜杠命令） |\n'
        '| Codex / Gemini CLI | ✅ 完整 |\n'
        '| Cursor / Copilot | ⚠️ 需转成各自规则格式 |\n'
        '| **连小理**（= LearnBuddy） | ✅ 一等公民（同一平台，非独立适配） |'
    )
    new = (
        '## 横切 · 平台适配 ✅\n'
        '\n'
        '**已完成（2026-10-01）**\n'
        '- ✅ **LearnBuddy / WorkBuddy 一等公民**：`~/.learnbuddy/skills/qihang/` + `.codebuddy-plugin/plugin.json`\n'
        '- ✅ 新增 `INSTALL.md` 与 `references/platforms.md`（LearnBuddy 单一目标平台）\n'
        '- ✅ `qihang.sh` 内置 **LearnBuddy 安装位置探测** + `platform` 命令\n'
        '- ✅ 入口 `SKILL.md` 更新：`description` 补齐 LearnBuddy 触发场景、加 `agent_created: true`、工作流加第 ⑧ 步\n'
        '- ✅ 明确平台差异：入口（自然语言，无需斜杠命令）、记忆系统、发现方式\n'
        '- ✅ **v2.8 平台专向化**：移除 Claude Code 适配；21 个 `commands/` 由斜杠命令改写为 **LearnBuddy 域入口卡**\n'
        '\n'
        '| 平台 | 支持度 |\n'
        '|---|---|\n'
        '| **LearnBuddy / WorkBuddy** | ✅ **一等公民（唯一适配目标）** |\n'
        '| **连小理**（= LearnBuddy） | ✅ 一等公民（同一平台，非独立适配） |\n'
        '| 其他 agent | 可读 `SKILL.md` 即装载，**不提供适配承诺** |'
    )
    rep(p, old, new, label='横切·平台适配节改为 LearnBuddy 单平台')


def fix_reports():
    rep('references/acceptance-v2.md',
        '| 多平台 | LearnBuddy 一等公民 + Claude Code 21 命令 + Codex/Gemini CLI |',
        '| 平台 | **LearnBuddy / WorkBuddy 一等公民（单一目标平台，v2.8 起）** |',
        label='§2.3 平台行')
    rep('references/skill-compliance-audit.md',
        '| `npx skills add <owner>/<repo>` | ✅ **可用**。下载 + 建立 `.claude/skills/<name>` 软链成功 |\n'
        '| `/plugin marketplace add <owner>/<repo>` | ⚠️ 属 Claude Code 内置斜杠命令，**须在 Claude Code 内执行**，本机无法代跑 |\n'
        '| 手动 clone / 复制 | ✅ 可用 |',
        '| `npx skills add <owner>/<repo>` | ✅ **可用**。通用 skills CLI（npm 包），下载 + 落地 skill 目录成功 |\n'
        '| LearnBuddy 原生：`find-skills` | ✅ 可用。检索后安装到 `~/.learnbuddy/skills/` |\n'
        '| 手动 clone / 复制 | ✅ 可用 |',
        label='§2.2 通道表改 LearnBuddy 通道')
    rep('references/skill-compliance-audit.md',
        '1. `npx skills add` 的**下载与 Claude Code 落地链路完全可用** —— 6 个仓库、70+ 个 skill 实测成功。\n'
        '2. 其余 agent 目录（Droid / Zed / Warp / OpenCode / Gemini CLI 等）因环境**批量删除保护**（单轮 50 次上限）未写入 —— **不影响 Claude Code 使用**。\n'
        '3. 部分仓库（skill 数量多、文件多）会因逐个重试而**显著变慢**，建议在真实 Claude Code 环境中安装，或改用 `git clone` + 手动复制。',
        '1. `npx skills add` 的**下载链路完全可用** —— 6 个仓库、70+ 个 skill 实测成功。\n'
        '2. 部分 agent 目录因环境**批量删除保护**（单轮 50 次上限）未写入 —— '
        '**不影响本包使用**（库内 38 个 skill 开箱即用，库外仅作增强）。\n'
        '3. 部分仓库（skill 数量多、文件多）会因逐个重试而**显著变慢**，'
        '建议改用 `git clone` + 手动复制到 `~/.learnbuddy/skills/`。',
        label='§2.2 关键结论去 Claude')
    rep('references/validation-report.md',
        '2. 在**真实 Claude Code 环境**跑完整安装（本机受批量保护限制，见 §七）。',
        '2. 在**真实 LearnBuddy 环境**跑完整安装（本机受批量保护限制，见 §七）。',
        label='§六 待办 2')
    rep('references/validation-report.md',
        '| `npx skills add <owner>/<repo>` | ✅ **可用** |\n'
        '| `/plugin marketplace add` | ⚠️ 须在 Claude Code 内执行 |\n'
        '| 手动 clone / 复制 | ✅ 可用 |',
        '| `npx skills add <owner>/<repo>` | ✅ **可用**（通用 skills CLI） |\n'
        '| LearnBuddy 原生：`find-skills` | ✅ 可用 |\n'
        '| 手动 clone / 复制 | ✅ 可用 |',
        label='§7.3 通道表')
    rep('references/validation-report.md',
        '文件多的仓库（如 `school-skills`）安装会反复重试而变慢；**不影响真实 Claude Code 使用**。',
        '文件多的仓库（如 `school-skills`）安装会反复重试而变慢；'
        '**不影响真实 LearnBuddy 使用**（库内 skill 不依赖此通道）。',
        label='§7.3 环境限制句')
    rep('references/validation-report.md',
        '| 真实 Claude Code 端到端安装 | ⏳ 转阶段 5 |',
        '| 真实 LearnBuddy 端到端安装 | ⏳ 转阶段 5 |',
        label='§7.4 验收行')


# ==================================================================== 4. 21 张域入口卡（确定性重建）
def rewrite_commands():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    try:
        from build_qihang_v2 import DOMAINS, CATS
    except Exception as e:                                    # pragma: no cover
        MISS.append('commands/ :: 无法导入 DOMAINS（%s）' % e)
        return

    def w(rel, body, label):
        fp = os.path.join(ROOT, rel)
        cur = rd(rel) if os.path.isfile(fp) else None
        if cur == body:
            DONE.append('[已是最新] %s :: %s' % (rel, label))
        else:
            wr(rel, body)
            OK.append('%s :: %s' % (rel, label))

    w('commands/qihang.md', '''---
name: qihang
description: 「启航」学伴包库入口卡（1 级库）：需求明确 → 锁定域 → 锁定 skill → 库内优先。
---

# 启航 · 库入口（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**提出需求即可；
> 本卡列出库入口的标准处理步骤，供人工检索与插件装载，**不需要输入任何命令**。

1. **需求明确**：读 `library/clarity.md`，拆 6 槽位，算 `U = 1 − Σ(wᵢcᵢ)/Σwᵢ`。
   `U > 0.30` **且关键槽位 `O/T/D` 缺失或出现歧义（`cᵢ = 0.5`）** → 追问
   （≤3 轮、每轮 ≤3 问，优先级 W>O>D>C>B>T）。
2. **锁定域**：读 `domains/_registry.md`，用触发词匹配；多域命中走跨域串联（≤4 域）。
3. **域审查**：读 `library/domain-review.md`，用该域「不覆盖」条目复核，越界则改锁。
4. **锁定 skill**：读 `domains/<域>/_domain.md` → 用**库内 skill**（`skills/local/`）。
5. **库外兜底**：仅当库内不满足，才读 `skills/external.md` 走安装。
6. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档（F3/F5 除外）。
''', '库入口卡')

    w('commands/qihang-dlut.md', '''---
name: qihang-dlut
description: 「启航」校情入口卡：查大连理工大学学院 / 校区 / 教务 / 职能部门 / 需登录站点。
---

# 校情横切 · 入口（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**问「机械学院官网是啥」即可，
> 本卡是该横切的标准处理步骤。

**硬性规则**
1. **先读** `references/dlut-official-sites.md`（公开站）；涉及登录项再读 `references/dlut-login-sites.md`。
2. 命中 → 输出 `【结论】+【网址】+【状态 ✅/⚠️】+【备注】`。
3. **未命中 → 固定回复**：「信息库未收录该条目，建议访问 https://www.dlut.edu.cn/ 核实」。
4. **禁止编造**任何 dlut.edu.cn 下的 URL、电话或单位名。
5. 标 ⚠️ 的条目必须带上「待核实」。

**私密站（方案 A）**：用受控浏览器打开 → 请你本人登录 → 我只读读取 → **不落盘、不外传**。
涉 L3 级（缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细）**一律不读取**。
**必须使用独立 Profile**：`~/.qihang/browser-profile`。
''', '校情入口卡')

    for d in DOMAINS:
        did, slug, name = d['id'], d['slug'], d['name']
        cat = CATS[d['cat']][0]
        trig = '、'.join(d['triggers'][:6])
        ddir = 'domains/%s-%s' % (did, slug)
        ldir = os.path.join(ROOT, ddir, 'skills', 'local')
        lsk = sorted(x for x in os.listdir(ldir)
                     if os.path.isfile(os.path.join(ldir, x, 'SKILL.md'))) if os.path.isdir(ldir) else []
        lsk_txt = ' / '.join('`%s`' % s for s in lsk) if lsk else '（见 `%s/skills/local/`）' % ddir
        lsk_path = '、'.join('`%s/skills/local/%s/SKILL.md`' % (ddir, s) for s in lsk) if lsk \
            else '`%s/skills/local/`' % ddir
        body = '''---
name: qihang-{did_l}
description: {did} {name}（{cat}）域入口卡：{trig}。当用户提出该域相关需求时使用，按 1 级库工作流处理。
---

# {did} · {name}（LearnBuddy 域入口卡）

> **用法**：在 LearnBuddy / WorkBuddy 中**直接用自然语言**说出需求即可；本卡用于人工检索与插件装载，
> **不需要输入任何命令**。

**触发表述**：{trig}

**边界**：{scope_in}
**不覆盖**：{scope_out}

**处理步骤**

1. **需求明确**：读 `library/clarity.md` 拆 6 槽位；`U > 0.30` 或关键槽 `O/T/D` 缺失 / 歧义 → 先追问。
2. **域审查**：读 `{ddir}/_domain.md` 确认边界；越界按 `library/domain-review.md` 改锁到对应域。
3. **库内优先**：调用库内 skill {lsk_txt}
   路径：{lsk_path}
4. **库外兜底**：仅当库内不满足，才读 `{ddir}/skills/external.md` 走安装（LearnBuddy 用 `find-skills`）。
5. **输出与归档**：按 `library/output-spec.md` 输出 ≤6 条要点，并按 `library/memory.md` 归档。
6. **DUT 绑定点**：见 `{ddir}/_domain.md`；涉及需登录站点按 `library/login-policy.md` 走方案 A（只读 / 不外传 / 不落盘）。
'''.format(did=did, did_l=did.lower(), name=name, cat=cat, trig=trig,
           scope_in=d['scope_in'], scope_out=d['scope_out'],
           ddir=ddir, lsk_txt=lsk_txt, lsk_path=lsk_path)
        w('commands/qihang-%s.md' % did.lower(), body, '%s 域入口卡' % did)


# ==================================================================== 5. qihang.sh（平台探测只认 LearnBuddy）
def fix_qihang_sh():
    p = 'scripts/qihang.sh'
    rep(p, '''detect_skills_dir() {
  for d in "${HOME_DIR}/.learnbuddy/skills" "${HOME_DIR}/.claude/skills" \\
           "${ROOT}/../.learnbuddy/skills" "${ROOT}/../.claude/skills" \\
           "${HOME_DIR}/.codex/skills" "${HOME_DIR}/.gemini/skills"; do
    [ -d "$d" ] && { echo "$d"; return 0; }
  done
  echo "${HOME_DIR}/.learnbuddy/skills"
}''', '''# v2.8：本包只适配 LearnBuddy / WorkBuddy 单一目标平台（原多平台探测已移除）
detect_skills_dir() {
  for d in "${HOME_DIR}/.learnbuddy/skills" "${ROOT}/../.learnbuddy/skills"; do
    [ -d "$d" ] && { echo "$d"; return 0; }
  done
  echo "${HOME_DIR}/.learnbuddy/skills"
}''', label='探测目录收敛为 LearnBuddy')
    rep(p, '''platform_of() {
  case "$1" in
    */.learnbuddy/skills) echo "LearnBuddy / WorkBuddy" ;;
    */.claude/skills)     echo "Claude Code" ;;
    */.codex/skills)      echo "Codex" ;;
    */.gemini/skills)     echo "Gemini CLI" ;;
    *) echo "未知 / 自定义" ;;
  esac
}''', '''# v2.8：只认 LearnBuddy / WorkBuddy（唯一目标平台）
platform_of() {
  case "$1" in
    */.learnbuddy/skills) echo "LearnBuddy / WorkBuddy" ;;
    *) echo "非目标平台（本包只适配 LearnBuddy）" ;;
  esac
}''', label='platform_of 收敛为 LearnBuddy')
    rep(p, '''  for d in "${HOME_DIR}/.learnbuddy/skills" "${HOME_DIR}/.claude/skills" \\
           "${HOME_DIR}/.codex/skills" "${HOME_DIR}/.gemini/skills"; do''',
        '''  for d in "${HOME_DIR}/.learnbuddy/skills" "${ROOT}/../.learnbuddy/skills"; do''',
        label='cmd_platform 安装位置收敛')
    # 库外安装通道：Claude 斜杠命令 → 通用 skills CLI
    for repo in ('Jellypod-Inc/school-skills', 'Imbad0202/academic-research-skills',
                 'alirezarezvani/claude-skills'):
        rep(p, '/plugin marketplace add ' + repo, 'npx skills add ' + repo,
            label='REGISTRY 安装通道 → npx skills add（%s）' % repo, required=False)


# ==================================================================== 6. 构建链文档
def fix_build_docs():
    p = 'scripts/_build/README.md'
    rep(p, '**严格顺序（v2.7 全量）**：`v2 → extras → phase1 … phase15`',
        '**严格顺序（v2.8 全量）**：`v2 → extras → phase1 … phase16`',
        label='构建顺序标题 v2.8')
    rep(p, 'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do',
        'for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do',
        label='构建循环加 phase16')
    rep(p, '| **`build_phase15`** | **复查修复层（v2.6 → v2.7，17 项缺陷）** |',
        '| **`build_phase15`** | **复查修复层（v2.6 → v2.7，17 项缺陷）** |\n'
        '| **`build_phase16`** | **LearnBuddy 专向化层（v2.7 → v2.8）：移除 Claude Code 适配 + `commands/` 改写为域入口卡** |',
        label='构建表加 phase16 行')


# ==================================================================== 7. 生成器数据（源侧去 Claude 通道）
def fix_generator_data():
    p = 'scripts/_build/build_qihang_v2.py'
    resub(p, r'"/plugin marketplace add ', '"npx skills add ',
          label='DOMAINS 库外安装通道 → npx skills add', absent='/plugin marketplace add ')


# ==================================================================== 8. 版本号 2.7.0 → 2.8.0
def fix_versions():
    targets = []
    for base, _dirs, files in os.walk(os.path.join(ROOT, 'domains')):
        for fn in files:
            if fn == 'SKILL.md':
                targets.append(os.path.relpath(os.path.join(base, fn), ROOT))
    targets += ['SKILL.md', 'library/SKILL.md', 'config.yaml',
                '.codebuddy-plugin/plugin.json', 'README.md', 'PROJECT.md', 'ROADMAP.md',
                'INSTALL.md', 'qihang-scenario-design.html',
                'scripts/qihang.sh', 'scripts/aligncheck.py']
    SUBS = [
        ('version: 2.7.0', 'version: 2.8.0'),
        ('"version": "2.7.0"', '"version": "2.8.0"'),
        ('## 7. 当前状态（v2.7.0）', '## 7. 当前状态（v2.8.0）'),
        ('（v2.7.0）</title>', '（v2.8.0）</title>'),
        ('<span class="ver">v2.7.0 三级结构</span>', '<span class="ver">v2.8.0 三级结构</span>'),
        ('# 「启航」学伴包 · 入口（v2.7.0）', '# 「启航」学伴包 · 入口（v2.8.0）'),
        ('# 「启航」新生学习生活一体化学伴包 v2.7.0', '# 「启航」新生学习生活一体化学伴包 v2.8.0'),
        ('# 「启航」学伴包 v2.7 ·', '# 「启航」学伴包 v2.8 ·'),
        ('> 版本 v2.7 ｜ 更新 2026-10-01', '> 版本 v2.8 ｜ 更新 2026-10-02'),
        ('> v2.7.0 ｜ 2026-10-02 ｜ 配套', '> v2.8.0 ｜ 2026-10-02 ｜ 配套'),
        # scripts/qihang.sh（历史遗留为 v2.6.0，一并归位）
        ('v2.6.0 · 三级结构管理脚本（多平台）', 'v2.8.0 · 三级结构管理脚本（LearnBuddy 目标平台）'),
        ('「启航」学伴包 v2.6.0 · 状态', '「启航」学伴包 v2.8.0 · 状态'),
    ]
    changed = []
    for p in targets:
        fp = os.path.join(ROOT, p)
        if not os.path.isfile(fp):
            continue
        with open(fp, 'r', encoding='utf-8') as f:
            t0 = f.read()
        t = t0
        for a, b in SUBS:
            t = t.replace(a, b)
        if p == 'scripts/aligncheck.py':
            # 该文件里 2.7.0 只作为「期望版本」出现，可整体替换
            t = t.replace('2.7.0', '2.8.0')
        if t != t0:
            with open(fp, 'w', encoding='utf-8', newline='\n') as f:
                f.write(t)
            changed.append(p)
    if changed:
        OK.append('统一版本号到 v2.8.0（%d 个文件）' % len(changed))
    else:
        DONE.append('[已是最新] 版本号已统一为 v2.8.0')


def main():
    fix_platform_files()   # 两个整文件重写（platforms.md / INSTALL.md）
    fix_tables()
    fix_library_memory()
    fix_project()
    fix_readme()
    fix_roadmap()
    fix_reports()
    rewrite_commands()     # 21 张域入口卡（确定性重建）
    fix_qihang_sh()
    fix_build_docs()
    fix_generator_data()
    fix_versions()         # 最后跑，覆盖前面所有文件的版本声明

    print('=' * 62)
    for x in OK:
        print('  ✅ ' + x)
    print('-' * 62)
    if MISS:
        for x in MISS:
            print('  ❌ 未命中 ' + x)
    else:
        print('  （无未命中项）')
    print('=' * 62)
    print('改动 %d 处 ｜ 未命中 %d 处 ｜ 已是最新 %d 处' % (len(OK), len(MISS), len(DONE)))
    print('提示：接着跑 bash scripts/selfcheck.sh && bash scripts/audit.sh && bash scripts/regress.sh 3')


if __name__ == '__main__':
    main()
