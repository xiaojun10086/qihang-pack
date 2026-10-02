# 构建期生成器（非运行期）

> **修改 19 个域时用这里，不用于日常运行。**

| 脚本 | 作用 | 何时跑 |
|---|---|---|
| `build_qihang_v2.py` | 生成 1 级库 + 19 域骨架 + 私密站清单 | 改 `DOMAINS` 后 |
| `build_qihang_v2_extras.py` | 生成 config / 21 个命令 / qihang.sh / README | 接上一个 |
| `build_phase1.py` | 给 19 个库内 skill 补可执行示例 + 4 域安全护栏 + 用例集/校验清单 | 接上一个 |
| `build_phase2.py` | 给 19 个 external.md 补许可证列与合规标注 | 接上一个 |
| `build_phase3.py` | **复核修复层**：澄清门公式 / 红线体系(19域) / 域档案矛盾 / 触发词消歧 / 降级链 / 校验清单扩展 | 接上一个 |

**严格顺序**：`v2 → extras → phase1 → phase2 → phase3`

```bash
python scripts/_build/build_qihang_v2.py .
python scripts/_build/build_qihang_v2_extras.py .
python scripts/_build/build_phase1.py .
python scripts/_build/build_phase2.py .
python scripts/_build/build_phase3.py .
bash scripts/selfcheck.sh      # 跑完必自检
```

⚠️ **重跑 `build_qihang_v2.py` 会覆盖 `references/dlut-login-sites.md`** 的手工增补（§0.1 Profile 隔离 / §0.2 实测记录）。
重跑前先备份该文件。
