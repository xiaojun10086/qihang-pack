# 启航 · DSH（DeepSeek Harness）适配

本目录是「启航」技能包面向 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) 的**增量适配层**。

适配原则：**不改动原有结构**。`skills/`、`agents/`、`commands/`、`config.yaml`、`plugin.json`
一个字节都不动，原有目录几何与包内相对路径全部保持成立；DSH 专属产物只新增在 `dsh/` 之下。

## 为什么需要适配层

启航是宿主无关的扁平技能包：`skills/<name>/SKILL.md`。DSH 的发现规则与它有两处硬差异：

| 差异 | 启航原包 | DSH |
|---|---|---|
| 发现深度 | 包根 `plugin.json` 声明 `"skills": "./skills"` | 只在扫描根的**直属**子目录找 `<name>/SKILL.md`，**不支持**递归 `**/SKILL.md` |
| 命令 | `commands/*.toml`（`description` + `prompt`） | 命令是插件注册的 TS 对象，**不是**文件式 |
| 人格 | `agents/*.md` | `@deepseek-ai/dsh-persona` 的 preset 插件行 |

所以：**25 个业务技能可以原样复用**，只需把扫描根指到 `skills/`；
7 个命令与 3 个人格需要一层转换，转换产物由 `build_dsh_pack.py` 生成。

## 能力映射

| 启航资产 | DSH 侧形态 | 状态 |
|---|---|---|
| `skills/<name>/SKILL.md` × 25 | 同一份文件，`customSkillDirs` 指向 `skills/` | ✅ 原样可用 |
| `commands/<name>.toml` × 7 | `dsh/commands/<name>/SKILL.md`，`user-invocable: true` + `disable-model-invocation: true` | ✅ 生成 |
| `agents/<name>.md` × 3 | `dsh/personas/<name>.md` + `dsh/preset.example.yaml` 里的 `@deepseek-ai/dsh-persona` 行 | ✅ 生成 |
| `config.yaml`、`references/*.md` | 原样保留在包根；业务技能仍按 `../../config.yaml`、`../../references/*.md` 读取 | ✅ 原样可用 |
| `SKILL.md`（包根入口） | DSH 不发现（扫描根本身不是 bundle）；保留为人类可读入口 | ➖ 仅文档 |
| `plugin.json`、`.codebuddy-plugin/` | DSH 不读 | ➖ 无影响 |

## 安装

### 1. 取包

```bash
git clone -b dsh-qihang-release https://github.com/xiaojun10086/qihang-pack.git qihang-pack
```

或直接用 `dsh-qihang` 分支的开发树，或由 `python -B dsh/build_dsh_pack.py --out dist/dsh` 落盘一份。

把整包放到任意固定位置，**路径中避免空格**。

### 2. 挂载扫描根

把 `dsh/config.example.yaml` 的两行占位路径换成该位置的绝对路径，并入 DSH 的 Cordis 组合：

```yaml
- name: '@deepseek-ai/dsh-skill-filesystem'
  config:
    customSkillDirs:
      - 'C:\Users\me\qihang-pack\skills'
      - 'C:\Users\me\qihang-pack\dsh\commands'
```

Windows 路径用单引号包住，反斜杠不会被 YAML 转义。

> `customSkillDirs` 的相对路径按 DSH 进程的工作目录解析，**务必写绝对路径**。

### 3. 挂载人格（可选）

把 `dsh/preset.example.yaml` 的内容并入同一个组合。它会注册
`agent-preset-registry` 与三个 preset（`study-coach`、`research-librarian`、`campus-concierge`），
每个 preset 内部挂一行 `@deepseek-ai/dsh-persona`。

人设必须挂在 preset 组装内部——`dsh-persona` 在 agent scope 之外挂载会与提示词注册表自身的
`deployment:persona-prefix` 注册相撞并报错。

### 4. 验收

重启 DSH 后逐项确认，不要推定「装了就等于生效」：

1. 技能目录里出现 **25 个业务技能**（`using-qihang`、`portal-operator`、`exam-sprint` …）；
2. 技能目录里出现 **7 个命令技能**（`campus`、`code`、`exam`、`learn`、`notes`、`paper`、`search`），
   且它们**不参与模型自动路由**（`disable-model-invocation: true`），只由用户显式调用；
3. 随便调一个业务技能，确认其正文里的 `` `../using-qihang/SKILL.md` ``、
   `` `../../config.yaml` `` 能按包内相对路径读到；
4. 若要用人格，确认 preset 出现在会话的 preset 选择里，且切换后系统提示词确实变了。

任一项不成立就停下排查，不要凭名称或 `description` 声称技能已注册。

## 包内相对路径在 DSH 下的行为

业务技能与命令技能的正文都用包内相对路径读共享资产：

| 引用 | 起点 | 解析结果 |
|---|---|---|
| `` `../using-qihang/SKILL.md` `` | `skills/<name>/SKILL.md` | `skills/using-qihang/SKILL.md` ✅ |
| `` `../../config.yaml` `` | `skills/<name>/SKILL.md` | `config.yaml` ✅ |
| `` `../../references/dlut-*.md` `` | `skills/portal-operator/SKILL.md` | `references/dlut-*.md` ✅ |
| `` `../../skills/using-qihang/SKILL.md` `` | `dsh/commands/<name>/SKILL.md` | `skills/using-qihang/SKILL.md` ✅ |
| `` `../../config.yaml` `` | `dsh/commands/<name>/SKILL.md` | `config.yaml` ✅ |

这些路径成立的前提是**交付树保持原包的目录几何**：`skills/`、`references/`、`config.yaml`
必须始终相对包根同层存在。所以生成器只允许搬运和新增，不做移动或扁平化。

DSH 每个技能只有一个 `resourceBase`（即技能目录），目录本身对模型隐藏，资源按需解析。
`../../` 逃逸出 `resourceBase` 属于「按显式相对路径读取」，不是 DSH 的设计用法；
若某个 DSH 版本改为只允许 `resourceBase` 内解析，需把 `config.yaml` 与 `references/`
复制进各技能目录，或改用 `whenToUse` + 技能内联。届时 `build_dsh_pack.py --check` 会暴露断链。

## 维护

```bash
py -3.13 -B dsh/build_dsh_pack.py --check          # 校验当前工作树
py -3.13 -B dsh/build_dsh_pack.py --out dist/dsh   # 落盘可安装交付树
py -3.13 -B -m unittest discover -s dsh/tests      # 适配层回归测试
```

`--check` 按 DSH 的真实契约校验，而不是「文件存在就算过」：

- 扫描根下每个条目都是 `<name>/SKILL.md`，且 `name` 匹配 `^[a-z0-9]+(?:-[a-z0-9]+)*$`；
- frontmatter 首行恰为 `---`，YAML 解析为普通对象，键集不越界；
- 不含 DSH 显式拒绝的遗留键（`disableModelInvocation` / `modelInvocable` / `userInvocable`）；
- `description` 非空且不超过目录上限 500 字符；
- 没有扫描根之下超过一层的 `SKILL.md`（DSH 不支持递归发现）；
- 正文里每个 `../`、`./` 相对引用都能在交付树里解析到真实文件；
- preset 片段是合法 YAML，persona 行有非空 `prefix` 且不含 `{{...}}`。

发布流程见 `dsh/sync_dsh_release.py`：从 `dsh-qihang` 装配并推送到 `dsh-qihang-release`。
CI 见 `.github/workflows/sync-dsh-release.yml`。

## 已知限制

1. **DSH 处于 developer preview**，官方明示会有破坏性变更。升级 DSH 后请重跑 `--check`，
   并复核扫描根、frontmatter 键集与 `customSkillDirs` 语义是否仍成立。
2. **命令语义变了**。原包 `commands/*.toml` 由宿主注册成斜杠命令；DSH 的命令是 TS 插件，
   无法由文件生成。这里把命令降级为「仅用户可调用的技能」，斜杠触发形式取决于 DSH 当前版本，
   不保证与原宿主一致。
3. **人格是 system prompt 段落，不是文件**。`dsh/personas/*.md` 里已把包内相对路径改写成
   技能名引用（人设文本没有 `resourceBase`，相对路径在那里没有意义）。
4. **`SKILL.md`（包根）在 DSH 下不会被注册**。原包文档已说明「根入口兼容读取不等于子技能已注册」，
   这里同样成立：DSH 侧的路由完全由 `using-qihang` 技能承担。
5. **未做真实 DSH 环境实测**。本适配层只依据官方源码与文档实现并静态校验，
   尚未在运行中的 DSH 实例上跑过端到端验收。安装后请按上面「验收」一节逐项确认。
