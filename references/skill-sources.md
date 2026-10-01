# Skill 来源清单 · 12 个探测入口

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
