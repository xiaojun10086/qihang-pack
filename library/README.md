# library/ · 1 级 skill 库（Level 1）

> **本目录是规则本体，不是安装入口。** 唯一安装单元与唯一入口是**包根 `SKILL.md`**。

## 本目录的职责

- `clarity.md` —— 需求明确：6 槽位拆解 + 澄清门公式 + 追问优先级
- `domain-review.md` —— 域审查：锁定 / 跨域 / 越界 / 无域兜底
- `domain-review-cases.md` —— 配套：22 条越界用例（含 3 条反例）
- `output-spec.md` —— 输出规范：统一模板 + 简略原则 + 交付前校验
- `output-checklist.md` —— 配套：7 项硬校验
- `memory.md` —— 学习档案：四类内容 + 分层落点 + 敏感域红线
- `login-policy.md` —— 登录选择原则：A/B/C 三档 + 标准话术 + 安全保障

## 边界（硬规则）

- **只做横切职责，不承载业务**。具体场景的处理一律归 `domains/<域>/skills/local/`。
- 一旦这里开始写「怎么做某件事」，1 级库就退化成普通 skill，三级结构随之失效。

## 与包根 `SKILL.md` 的分工

| 位置 | 定位 | frontmatter |
|---|---|---|
| 包根 `SKILL.md` | 唯一入口 / 唯一安装单元（含红线总览与硬规则） | ✅ `name: qihang` |
| `library/README.md`（本文件） | 库内导航页，供人检索 | ❌ 刻意不带 `name`，避免第二个同名入口 |

完整链路（入口 → 红线 → 登录档位 → 澄清门 → 锁域 → 锁 skill → 输出 → 归档）见包根 `SKILL.md`。
