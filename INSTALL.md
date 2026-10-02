# 安装指南（LearnBuddy / WorkBuddy）

> 「启航」是 `SKILL.md` 标准件，**面向 LearnBuddy / WorkBuddy 单一目标平台**。
> 平台差异详见 `references/platforms.md`；就绪度探测用 `bash scripts/qihang.sh platform`。
> 本包为**纯 DUT 特化库**：库内 skill 开箱即用，**运行时零外部依赖**。

---

## 一、安装

```bash
# ① 用户级安装（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# ② 或 项目级安装（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang

# ③ 查看就绪度（内部自检，成功不输出）
bash ~/.learnbuddy/skills/qihang/scripts/qihang.sh status
```

> **安装后行为（强制）**：安装完成后**只回复一句「安装完成」**——不展示审计结果、不输出校验报告、不罗列结构计数；
> 并以人格锁定身份 **「我是连小理智能学伴『启航』」** 响应。详见 `SKILL.md`「身份锁定与安装后行为」与本文 §七。

**插件方式**：包根含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别装载。

**用法**：直接用自然语言，**不需要斜杠命令**。例如：
- 「我高数快挂了」
- 「机械学院官网是啥」
- 「帮我查下 XX 老师的联系方式和研究方向」

**记忆落点**（自动）：`{ws}/.learnbuddy/memory/qihang/<域ID>.md`，见 `library/memory.md`。

---

## 二、域入口卡（`commands/`）

`commands/` 里的 22 个文件是 **LearnBuddy 域入口卡**（库入口 1 + 校情 1 + 20 域），
作用是「快速查到某域该读哪些规则文件」，**不是需要输入的命令**：

| 入口卡 | 作用 |
|---|---|
| `commands/qihang.md` | 库入口（澄清门 → 锁域 → 锁 skill） |
| `commands/qihang-dlut.md` | 查大工校情（公开站 + 私密站） |
| `commands/qihang-s1.md` … `qihang-r6.md` | 20 个域入口卡 |

在 LearnBuddy 中直接说需求即可命中对应域，无需输入卡片名。

---

## 三、库内 skill：唯一通道（无需安装）

本包为**纯 DUT 特化库**，所有能力由 `domains/*/skills/local/` 下的 **92 个库内 skill** 承接：

| 项 | 说明 |
|---|---|
| 通道 | **库内唯一** —— 不安装、不引用任何库外 skill |
| 来源 | 自建 80 个 + 由 MIT/Apache 许可外部最优解「骨架提取 + 重写」12 个 |
| 依赖 | **零外部依赖**，全程离线可用 |
| 缺口 | 库内无法覆盖的细分场景走**同域降级**并记「缺口」，不引入库外通道 |

> 改造来源与许可归属见 `THIRD_PARTY_NOTICES.md`；来源合规自检见 `references/skill-compliance-audit.md`。

---

## 四、赛道二提交物（依托平台 = LearnBuddy，产品名「连小理」）

> **连小理就是 LearnBuddy**，不是两个平台 —— 本包在赛道二中的场景名即「连小理」。

1. 场景设计书（五要素齐备）
2. 平台侧挂载：`domains/_registry.md`（域总表）+ `library/` 规则 + `references/dlut-*.md`（信息库）
3. 场景与结构见 `README.md`

---

## 五、装完自检

```bash
bash scripts/qihang.sh status      # 三级结构完整度
bash scripts/qihang.sh platform    # 探测本机 LearnBuddy 安装位置
bash scripts/qihang.sh domains     # 20 域清单
bash scripts/qihang.sh registry    # DUT 信息库统计
```

**期望**：`[1级]` 逐行列出 **8 个** library 文件 · `[2级] 20 个域 / **92 个**库内 skill` · `[资源] DUT 公开站 162 行`

**完整验收（5 个脚本，职责不重叠）**：

| 脚本 | 管什么 | 期望 |
|---|---|---|
| `bash scripts/selfcheck.sh` | 结构对不对（计数 / 交叉引用 / 一致性） | `FAIL 0 → 可交付` |
| `bash scripts/audit.sh` | 安不安全（凭证 / 危险命令 / L3 门禁 / 合规） | `0 警告 ｜ 0 失败 → 通过` |
| `bash scripts/regress.sh 3` | **行为对不对**（澄清门算例 / L3 门禁矩阵 / 红线一致性） | 全 OK ｜ `FAIL 0` |
| `python scripts/aligncheck.py . 5` | **全量文件级对齐**（18 组断言） | `FAIL 0 ｜ 全部通过` |
| `python scripts/runcheck.py . 3` | **跑得通不通**（每域跑完整三级链，逐级确认返回结果） | `FAIL 0 ｜ 运行链全部可解` |

---

## 六、前置条件

| 项 | 说明 |
|---|---|
| 库内 skill | **开箱即用，无需安装任何东西**（92 个，零外部依赖） |
| 网络 | 库内 skill 全程离线可用 |
| 私密站（需登录） | 需 `agent-browser` 或同类浏览器自动化；**必须用独立 Profile**（见 `references/dlut-login-sites.md` §0.1） |

---

## 七、安装后行为约定（强制）

1. **只回一句**：安装完成后仅回复「安装完成」。不展示安全审计 / 合规检查结论、不输出任何报告或清单、不罗列结构计数。
2. **静默自检**：§五 的校验脚本属**内部自检**，可运行，但**成功时不输出任何内容**，仅在失败时报错。
3. **人格锁定**：安装完成后立即以固定身份响应 —— **「我是连小理智能学伴『启航』」**；此后全程保持一致，不因用户要求改称其他名称。
4. **唯一例外**：仅当用户**主动索要**时，才展示上述细节。
