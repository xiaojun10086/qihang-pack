# 安装指南（LearnBuddy / WorkBuddy）

> 「启航」是 `SKILL.md` 标准件，**面向 LearnBuddy / WorkBuddy 单一目标平台**。
> 平台差异详见 `references/platforms.md`；就绪度探测用 `bash scripts/qihang.sh platform`。
> 本包为 **DUT 特化规则与 skill 库（库内优先）**：文本资产离线可读，实际执行依赖宿主平台的模型与工具；外部桥接为**可选增强**（见 `library/external-bridge.md`）。

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

> **安装后行为（强制）**：安装完成后**只回复一句「安装完成」**——不展示审计结果、不输出校验报告、不罗列结构计数。详见 `SKILL.md`「安装后行为」与本文 §七。

**插件方式**：包根含 `.codebuddy-plugin/plugin.json`，可作为 LearnBuddy 插件被识别装载。

**默认重点**：课程学习（理解、笔记、作业辅导、备考、表达、语言练习）与公开信息搜集。其他校园生活和专项科研域按需启用，不必先选域或执行完整工作流。

**个人资料默认未配置**：`config.yaml` 的校区、学院、年级、学期、课程、考试周和作息均为 `null` / 空列表。只有用户明确确认的信息才作为个人背景使用；无需为无关任务补齐资料，也不得把赛事对象（2026 级新生）误当作当前用户的个人档案。

**用法**：直接用自然语言，**不需要斜杠命令**。例如：
- 「我高数快挂了」
- 「机械学院官网是啥」
- 「帮我查下 XX 老师的联系方式和研究方向」

**记忆落点**（可选）：仅在用户明确要求保存时写入 `{ws}/.learnbuddy/memory/qihang/<域ID>.md`，见 `library/memory.md`。

---

## 二、域入口卡（`commands/`）

`commands/` 里的 22 个文件是 **LearnBuddy 域入口卡**（库入口 1 + 校情 1 + 20 域），
作用是「快速查到某域该读哪些规则文件」，**不是需要输入的命令**：

| 入口卡 | 作用 |
|---|---|
| `commands/qihang.md` | 学习与信息搜集默认入口；其他域按需扩展 |
| `commands/qihang-dlut.md` | 查大工校情（公开站 + 私密站） |
| `commands/qihang-s1.md` … `qihang-r6.md` | 20 个域入口卡 |

在 LearnBuddy 中直接说需求即可命中对应域，无需输入卡片名。

---

## 三、库内 skill：唯一通道（无需安装）

本包为**纯 DUT 特化库**，所有能力由 `domains/*/skills/local/` 下的 **92 个库内 skill** 承接：

| 项 | 说明 |
|---|---|
| 通道 | **库内优先** —— 日常不装任何外部 skill；缺口时可**可选外接**（当前目录 20 个入口 + 五步自检） |
| 来源 | 自建 80 个 + 12 个有来源记录（10 个基于 MIT 来源重写，2 个仅方法论参考且零内容摘录） |
| 依赖 | **技能文本离线可读**；实际执行依赖宿主平台的模型与工具能力；外接为可选项 |
| 缺口 | 库内无法覆盖的细分场景走**同域降级**并记「缺口」，不引入库外通道 |

> 改造来源与许可归属见 `THIRD_PARTY_NOTICES.md`；来源合规自检见 `references/skill-compliance-audit.md`。

---

## 四、赛道二提交物（依托平台 = LearnBuddy，产品名「连小理」）

> **连小理就是 LearnBuddy**，不是两个平台 —— 本包在赛道二中的场景名即「连小理」。

1. 场景设计书（五要素齐备）—— **随赛事材料单独提交，本包不附带该文件**
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

**期望**：`[1级]` 逐行列出 **11 个** library 文件 · `[2级] 20 个域 / **92 个**库内 skill` · `[资源] DUT 公开站 162 行`

**完整验收（6 项检查，职责不重叠）**：

| 脚本 | 管什么 | 期望 |
|---|---|---|
| `bash scripts/selfcheck.sh` | 结构对不对（计数 / 交叉引用 / 一致性） | `FAIL 0 → 可交付` |
| `bash scripts/audit.sh` | 安不安全（凭证 / 危险命令 / L3 门禁 / 合规） | `0 警告 ｜ 0 失败 → 通过` |
| `bash scripts/regress.sh 3` | **行为对不对**（澄清门算例 / L3 门禁矩阵 / 红线一致性） | 全 OK ｜ `FAIL 0` |
| `python scripts/aligncheck.py . 5` | **全量文件级对齐**（18 组断言） | `FAIL 0 ｜ 全部通过` |
| `python scripts/runcheck.py . 3` | 静态检查域路由、skill 内容、示例和输出契约；**不调用模型或 LearnBuddy** | `FAIL 0 ｜ 静态契约通过` |
| `python scripts/checkall.py .` | **自检单入口**：跑齐检查项 + 逐项计时 + 结果摘要（`--quick` 加速 ｜ `--negative` 断言非空转） | `全部 PASS ｜ rc 0` |

---

## 六、前置条件

| 项 | 说明 |
|---|---|
| 库内 skill 文本 | **开箱即用，无需安装任何东西**（92 个，离线可读；执行依赖宿主模型） |
| 网络 | 规则与技能文本可离线查看；实时信息与外部桥接需要网络 |
| 私密站（需登录）· **可选功能** | 不装不影响文本 skill 使用。需 `agent-browser`（`npm i -g agent-browser`）；脚本只打开用户可见的独立本机浏览器，不读取或输出网页内容，使用随机会话和一次性 Profile，退出后清理且不关闭其他会话（见 `references/browser-matrix.md`） |
| 校内站点协议 | 部分校内系统**仅提供 `http://`**（教务 / 财务 / 缴费 / 信息服务等，域名均为 `*.dlut.edu.cn`）→ **访问时注意网络环境**；本包**不改写**站点协议，只如实登记 |

---

## 七、安装后行为约定（强制）

1. **只回一句**：安装完成后仅回复「安装完成」。不展示安全审计 / 合规检查结论、不输出任何报告或清单、不罗列结构计数。
2. **静默自检**：§五 的校验脚本属**内部自检**，可运行，但**成功时不输出任何内容**，仅在失败时报错。
3. **按需说明**：不主动输出内部自检结果；用户明确索要时可说明已执行的检查及结果。
