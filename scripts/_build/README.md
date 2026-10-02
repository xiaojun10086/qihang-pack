# 构建期生成器（非运行期）

> **修改 19 个域时用这里，不用于日常运行。**

| 脚本 | 作用 | 何时跑 |
|---|---|---|
| `build_qihang_v2.py` | 生成 1 级库 + 19 域骨架 + 私密站清单 | 改 `DOMAINS` 后 |
| `build_qihang_v2_extras.py` | 生成 config / 21 个命令 / qihang.sh / README | 接上一个 |
| `build_phase1.py` | 给 19 个库内 skill 补可执行示例 + 4 域安全护栏 + 用例集/校验清单 | 接上一个 |
| `build_phase2.py` | 给 19 个 external.md 补许可证列与合规标注 | 接上一个 |
| `build_phase3.py` | **复核修复层**：澄清门公式 / 红线体系(19域) / 域档案矛盾 / 触发词消歧 / 降级链 / 校验清单扩展 | 接上一个 |

**严格顺序（v2.9 全量）**：`v2 → extras → phase1 … phase17`

```bash
for p in v2 v2_extras 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17; do
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
| **`build_phase15`** | **复查修复层（v2.6 → v2.7，21 条缺陷 / 20 组修复）** |
| **`build_phase16`** | **LearnBuddy 专向化层（v2.7 → v2.8）：移除 Claude Code 适配 + `commands/` 改写为域入口卡** |
| **`build_phase17`** | **漏检缺陷修复层（v2.8 → v2.9）：检查器全量化 · L3 清单去重 · 口径统一 · `qihang.sh` 可复现性** |

✅ **全量重跑已安全**（v2.9 起）：
- `build_qihang_v2.py` 改为**暂存目录生成 + 逐文件覆盖**，不再 `rmtree` 目标目录
  （旧版会把整个仓库删空，含 `.git`，实测 161 文件 → 0）；
- `references/dlut-login-sites.md` 的 §0.1/§0.2 手工增补由 `build_phase17.py` **幂等补回**；
- 链末 `build_phase17.py` 负责平台口径兜底、授权清单收敛、计数与去重归一化。

**验证口径**：全链连跑两遍，逐文件哈希应**完全一致**（实测 161 文件 0 变更），
且产物需通过 `selfcheck.sh` / `audit.sh` / `regress.sh` / `aligncheck.py` 四项。
