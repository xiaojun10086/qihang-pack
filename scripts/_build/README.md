# 构建期生成器（非运行期）

> **修改 19 个域时用这里，不用于日常运行。**

| 脚本 | 作用 | 何时跑 |
|---|---|---|
| `build_qihang_v2.py` | 生成 1 级库 + 19 域骨架 + 私密站清单 | 改 `DOMAINS` 后 |
| `build_qihang_v2_extras.py` | 生成 config / 21 个命令 / qihang.sh / README | 接上一个 |
| `build_phase1.py` | 给 19 个库内 skill 补可执行示例 + 4 域安全护栏 + 用例集/校验清单 | 接上一个 |
| `build_phase2.py` | 给 19 个 external.md 补许可证列与合规标注 | 接上一个 |
| `build_phase3.py` | **复核修复层**：澄清门公式 / 红线体系(19域) / 域档案矛盾 / 触发词消歧 / 降级链 / 校验清单扩展 | 接上一个 |

**严格顺序（v2.7 全量）**：`v2 → extras → phase1 … phase15`

```bash
for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
  case "$p" in v2|v2_extras) f="build_qihang_${p}.py" ;; *) f="build_phase${p}.py" ;; esac
  python "scripts/_build/$f" .
done
bash scripts/selfcheck.sh && bash scripts/audit.sh   # 跑完必自检
```

| 层 | 作用 |
|---|---|
| `build_phase4`–`build_phase12` | 复核修复与文档同步（v2.2–v2.6 各轮） |
| **`build_phase13`** | **库内 skill 扩容：每域 1 → 2（共 38）** |
| **`build_phase14`** | **库外候选多源比对 + 选优 + 生成 `skill-matrix-v3.md`** |
| **`build_phase15`** | **复查修复层（v2.6 → v2.7，17 项缺陷）** |

⚠️ **重跑 `build_qihang_v2.py` 会覆盖 `references/dlut-login-sites.md`** 的手工增补（§0.1 Profile 隔离 / §0.2 实测记录）。
重跑前先备份该文件。
