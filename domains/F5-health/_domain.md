# F5 · 健康与运动

> 域 ID `F5` ｜ 所属大类 **生活类** ｜ 目录 `domains/F5-health/`

## 域边界

- **覆盖**：就医路径、医保报销、锻炼计划、作息饮食
- **不覆盖**：不做医疗诊断；不处理心理（→F3）

## 触发词（命中任一即锁定本域）

`生病` ｜ `就医` ｜ `医保` ｜ `锻炼` ｜ `饮食` ｜ `体检` ｜ `运动` ｜ `受伤`

## 库内 skill（优先使用，无需安装）

- **`health-guide`** — 就医与运动指引（自建·DUT）
  症状严重直接给就医路径（校医院 → 附属医院）；不诊断，只给流程与运动处方。

## DUT 绑定点

**公开站（无需登录）**
- 校医院 84708120（24h）/ 84708990（门诊）
- 文体场馆中心 https://tycgzx.dlut.edu.cn/

**私密站（需登录，见 `references/dlut-login-sites.md`）**
- i大工 APP 场馆/浴室预约（仅 APP）

## 执行顺序

1. 1 级库完成**需求明确**（`library/clarity.md`），U ≤ 5% 才继续
2. 1 级库完成**域审查**，确认命中 `F5`（`library/domain-review.md`）
3. 用**库内 skill** `health-guide` 执行（首选）
4. 库内不满足 → 读 `skills/external.md` 走库外安装
5. 按 `library/output-spec.md` 输出，并写入学习档案
