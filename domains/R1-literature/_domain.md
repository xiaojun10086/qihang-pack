# R1 · 文献检索与管理

> 域 ID `R1` ｜ 所属大类 **科研类** ｜ 目录 `domains/R1-literature/`

## 域边界

- **覆盖**：文献检索式设计、筛选、引文核验、文献管理
- **不覆盖**：不写论文正文（→S5/R4）

## 触发词（命中任一即锁定本域）

`文献` ｜ `综述` ｜ `引用` ｜ `Zotero` ｜ `知网` ｜ `参考文献` ｜ `查文献` ｜ `DOI`

## 库内 skill（唯一通道，无需安装）

- **`lit-map`** — 文献地图（自建）
  先出检索式与纳排标准，再按「主题—方法—结论」矩阵整理；每条引文给可核验锚点。

- **`citation-verify`** — 引文核验（自建）
  逐条核验引文（题名/作者/年/卷期页/DOI）并标回源状态，不生成、不补全。

- **`lit-fetch`** — （改造自外部 MIT 最优解 + DUT 特化）
  分层检索 + 合法全文路线（开放获取优先，绝不绕付费墙）+ 去重与状态记录

- **`review-method`** — 系统综述（自建）
  按 PRISMA 流程给系统综述 / 范围综述的操作框架：检索式、去重、筛选标准、流程图与偏倚评估，不代写正文。

- **`lit-manage`** — 文献库管理（自建）
  给 Zotero 文献库的分类、标签、命名与去重规范，把散乱文献整理成可检索、可回溯的结构。

## DUT 绑定点

**公开站（无需登录）**
- 图书馆 https://lib.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- 图书馆电子资源校外访问 https://lib.dlut.edu.cn/wxzy1/xwfw.htm

## 外部承接（库内与同域降级都接不住时才启用）

> **第三档入口**：先读 `library/external-bridge.md`（触发条件 + 五步自检 + 许可门禁），
> 再按 `references/external-sources.md` §1 的顺序检索 **12 个平台**。
> **库内优先不变**：本域仍先用库内 skill；外部桥接只在**同域降级也接不住**时启用。
> **禁止编造**外部链接（硬规则 2）；候选仓库已逐个双通道核验（2026-10-03）。

**检索词**：文献检索 / 下载 / 管理 / 引用
**平台检索式（英文，≤3 词）**：`literature review`
**适配词表（英文，候选 name+description 命中任一即算适配）**：`literature` ｜ `review` ｜ `zotero` ｜ `citation`
**指定检索平台（只查这几个，不穷举）**：`skillselion.com` ｜ `officialskills.sh` ｜ `skillsmp.com`（共 3 个）

**已核验候选**（仓库数据 2026-10-02 抓取 ｜ 链接 2026-10-03 双通道核验）

| 候选仓库 | 许可 | ★ | 综合分 | 可用性判定 |
|---|---|---|---|---|
| `Lucaswangzcx/literature-downloader-skill` | MIT | 230 | 4.55 | ✅ 最优解 |
| `WenyuChiou/zotero-skills` | MIT | 55 | 4.40 | 备选 |
| `xwmxcz/papers-skill` | MIT | 1 | 3.35 | 备选 |

**本域结论**：可用首选：`Lucaswangzcx/literature-downloader-skill`（MIT）。

## 执行顺序

0. **先判红线**（见下文 `## ⚠️ 红线` 节）—— 命中则**拒绝并给合规替代**，**不追问**
1. 1 级库完成**需求明确**（`library/clarity.md`）：先过 §5 例外，未命中的再按关键槽与 `U` 判定
2. 1 级库完成**域审查**，确认命中 `R1`（`library/domain-review.md`）
3. 用**库内 skill**（库内 5 个：`lit-map` · `citation-verify` · `lit-fetch` · `lit-manage` · `review-method`；按需求择一）执行
4. 按 `library/output-spec.md` 输出，并写入学习档案
5. 按 `library/skill-evolution.md` 记录本域习惯，并**只在可改段内**做非结构性自迭代（不改红线 / 输出契约 / 任何事实；不满足触发条件则不迭代）
6. **外部桥接（最后的兜底）**：库内与同域降级都接不住时，读 `library/external-bridge.md` → 按 `references/external-sources.md` 检索 12 平台 → 过五步自检 → 输出首行标 `[外接] 来源 + 许可`；**未命中则回落「纯提示词模式」**。

## ⚠️ 红线（不得绕过）

- **不生成、不补全任何未核验的引文**（标题 / 作者 / 卷期页 / DOI）
- 每条引文必须可回源；无法定位的条目一律删除，不放「凑数文献」

