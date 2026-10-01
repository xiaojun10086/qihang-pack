# F1 · 校园事务

> 域 ID `F1` ｜ 所属大类 **生活类** ｜ 目录 `domains/F1-campus-affairs/`

## 域边界

- **覆盖**：选课、学籍、证明打印、一卡通、报修、公寓、离校等事务办理路径
- **不覆盖**：不涉及健康（→F5）；不涉及钱（→F4）

## 触发词（命中任一即锁定本域）

`选课` ｜ `学籍` ｜ `证明` ｜ `一卡通` ｜ `报修` ｜ `宿舍` ｜ `离校` ｜ `校园卡` ｜ `办事`

## 库内 skill（优先使用，无需安装）

- **`campus-desk`** — 校园事务办理台（自建·DUT）
  先查 DUT 信息库锁定入口与电话，再给「去哪办 / 带什么 / 多久」，查不到就明说未收录。

## DUT 绑定点

**公开站（无需登录）**
- 校园门户 https://portal.dlut.edu.cn/
- 学生工作处 https://xsc.dlut.edu.cn/
- 后勤处 https://houqin.dlut.edu.cn/
- 保卫处 https://gach.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- 一卡通 https://ecard.dlut.edu.cn/
- 校园门户办事大厅
- 离校系统 http://lx.dlut.edu.cn/

## 执行顺序

1. 1 级库完成**需求明确**（`library/clarity.md`），U ≤ 5% 才继续
2. 1 级库完成**域审查**，确认命中 `F1`（`library/domain-review.md`）
3. 用**库内 skill** `campus-desk` 执行（首选）
4. 库内不满足 → 读 `skills/external.md` 走库外安装
5. 按 `library/output-spec.md` 输出，并写入学习档案
