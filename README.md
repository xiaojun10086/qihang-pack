# 启航 · DSH 交付树

本分支由 `main` 分支的 `dsh/build_dsh_pack.py` 生成，请勿直接编辑。
它把「启航」技能包原样搬运过来，并叠加一层 DSH（DeepSeek Harness）适配产物。

## 内容

| 路径 | 说明 |
|---|---|
| `skills/` | 25 个业务技能，原样保留，DSH 直接发现 |
| `dsh/commands/` | 7 个命令技能，由 `commands/*.toml` 转换而来（仅用户可调用） |
| `dsh/personas/` | 3 个人设文本，由 `agents/*.md` 转换而来 |
| `dsh/preset.example.yaml` | agent preset + persona 挂载片段 |
| `dsh/config.example.yaml` | skill 发现配置片段 |
| `config.yaml` `references/` | 共享配置与站点资料，供上述技能按原有相对路径读取 |

## 安装

见 [`dsh/README.md`](dsh/README.md)。最短路径：

1. 把本目录放到任意固定位置（路径中避免空格）。
2. 把 `dsh/config.example.yaml` 里的两行改成该位置的绝对路径，并入 DSH 组合。
3. 重启 DSH，确认技能目录里出现 25 个业务技能。

## 边界

* `SKILL.md`、`plugin.json`、`agents/`、`commands/` 是给宿主无关读取与其它宿主用的；
  DSH 不会自动发现它们，DSH 侧一律走 `skills/`、`dsh/commands/`、`dsh/personas/`。
* DSH 处于 developer preview，官方明示会有破坏性变更；升级 DSH 后请在源分支 `main` 上
  重跑 `dsh/build_dsh_pack.py --check`，复核本树是否仍符合 DSH 契约（该脚本不随本分支交付）。
