# F4 · 财务与安全

> 域 ID `F4` ｜ 所属大类 **生活类** ｜ 目录 `domains/F4-money-safety/`

## 域边界

- **覆盖**：生活费规划、奖助学金申请、兼职避坑、防诈骗、安全
- **不覆盖**：不做投资建议；不处理心理问题（→F3）

## 触发词（命中任一即锁定本域）

`生活费` ｜ `奖学金` ｜ `助学金` ｜ `兼职` ｜ `诈骗` ｜ `丢卡` ｜ `借钱` ｜ `花呗`

## 库内 skill（优先使用，无需安装）

- **`money-guard`** — 生活费与防诈守门（自建）
  先算月度收支缺口，再给节流方案；遇到可疑信息一律先按诈骗流程核验。

## DUT 绑定点

**公开站（无需登录）**
- 学生资助（学生处）https://xsc.dlut.edu.cn/
- 财务处 http://cw.dlut.edu.cn/
- 保卫处 https://gach.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- 一卡通 https://ecard.dlut.edu.cn/（余额/流水）
- 统一支付 http://pay.dlut.edu.cn/

## 执行顺序

1. 1 级库完成**需求明确**（`library/clarity.md`），U ≤ 5% 才继续
2. 1 级库完成**域审查**，确认命中 `F4`（`library/domain-review.md`）
3. 用**库内 skill** `money-guard` 执行（首选）
4. 库内不满足 → 读 `skills/external.md` 走库外安装
5. 按 `library/output-spec.md` 输出，并写入学习档案
