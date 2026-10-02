# 安装指南（多平台）

> 「启航」是 `SKILL.md` 标准件，装到哪个平台就用在哪个平台。
> 平台差异详见 `references/platforms.md`；自动探测用 `bash scripts/qihang.sh platform`。

---

## 一、LearnBuddy / WorkBuddy（推荐，一等公民）

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

## 二、Claude Code

```bash
cp -r qihang-pack ~/.claude/skills/qihang
mkdir -p ~/.claude/commands && cp qihang-pack/commands/*.md ~/.claude/commands/
bash ~/.claude/skills/qihang/scripts/qihang.sh status
```

**用法**：
| 命令 | 作用 |
|---|---|
| `/qihang` | 库入口（澄清门 → 锁域 → 锁 skill） |
| `/qihang-dlut` | 查大工校情 |
| `/qihang-s1` … `/qihang-r5` | 19 个域命令 |

**库外 skill 安装**（库内不满足时才需要）：
```bash
npx skills add <owner>/<repo>              # 实测可用
/plugin marketplace add <owner>/<repo>     # 备选
```

---

## 三、Codex / Gemini CLI

```bash
# Codex
cp -r qihang-pack ~/.codex/skills/qihang

# Gemini CLI
cp -r qihang-pack ~/.gemini/skills/qihang
```

用自然语言触发即可。

---

## 四、Cursor / GitHub Copilot

这两个平台不吃 `SKILL.md`，需把入口内容转成它们的规则格式：

```bash
# Cursor
mkdir -p .cursor/rules && cp qihang-pack/SKILL.md .cursor/rules/qihang.mdc

# Copilot
mkdir -p .github && cp qihang-pack/SKILL.md .github/copilot-instructions.md
```

再把 `qihang-pack/library/` 与 `domains/_registry.md` 作为附属文档放在仓库内，供引用。

---

## 五、赛道二提交物（依托平台 = LearnBuddy，产品名「连小理」）

> **连小理就是 LearnBuddy**，不是两个平台 —— 本包在赛道二中的场景名即「连小理」。

1. 提交 **`qihang-scenario-design.html`**（场景设计书，五要素齐备，约 1900 字）
2. 平台侧挂载：`domains/_registry.md`（域总表）+ `library/` 规则 + `references/dlut-*.md`（信息库）
3. 场景与结构见 `PROJECT.md`

安装与使用**完全按第一节（LearnBuddy / WorkBuddy）**即可，无需另做适配。


## 六、装完自检

```bash
bash scripts/qihang.sh status      # 三级结构完整度
bash scripts/qihang.sh platform    # 探测本机平台与安装路径
bash scripts/qihang.sh domains     # 19 域清单
bash scripts/qihang.sh registry    # DUT 信息库统计
bash scripts/qihang.sh probe       # 库外候选缺失项（可选）
```

**期望**：`[1级]` 逐行列出 **8 个** library 文件（SKILL + 7 份规则，含 `login-policy.md`） · `[2级] 19 个域 / **38 个**库内 skill` · `[资源] DUT 公开站 160 行`

**完整验收（v2.7 起 4 个脚本，职责不重叠）**：

| 脚本 | 管什么 | 期望 |
|---|---|---|
| `bash scripts/selfcheck.sh` | 结构对不对（计数 / 交叉引用 / 一致性） | `OK 31 ｜ WARN 0 ｜ FAIL 0 → 可交付` |
| `bash scripts/audit.sh` | 安不安全（凭证 / 危险命令 / L3 门禁 / 合规） | `37 通过 ｜ 0 警告 ｜ 0 失败 → 通过` |
| `bash scripts/regress.sh 3` | **行为对不对**（澄清门算例 / L3 门禁矩阵 / 红线一致性） | `120 项全 OK ｜ FAIL 0` |
| `bash scripts/qihang.sh status` | 三级结构完整度 | 逐行 ✓ |

---

## 七、前置条件

| 项 | 说明 |
|---|---|
| 库内 skill | **开箱即用，无需安装任何东西** |
| 库外 skill | 仅在库内不满足时需要；部分需 API Key 或联网（见各域 `skills/external.md`） |
| 私密站（需登录） | 需 `agent-browser` 或同类浏览器自动化；**必须用独立 Profile**（见 `references/dlut-login-sites.md` §0.1） |
| 网络 | 库内 skill 全程离线可用 |
