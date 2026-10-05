# 安装与使用

> 「启航」v4.0 是扁平 skill 包，25 个 skill 位于 `skills/<name>/SKILL.md`。
> 文本资产离线可读；实际执行依赖宿主平台的模型与工具能力。

---

## 一、安装

```bash
# ① 用户级（所有项目可用）
cp -r qihang-pack ~/.learnbuddy/skills/qihang

# ② 项目级（仅当前工作区）
mkdir -p .learnbuddy/skills && cp -r qihang-pack .learnbuddy/skills/qihang

# ③ 或从 release 分支直接下载
git clone -b release https://github.com/xiaojun10086/qihang-pack.git
```

**插件方式**：包根含 `plugin.json`，声明 `"skills": "./skills"`；支持 skill 目录发现的主机可直接装载，无需复制。

**依赖**：无。不需要安装任何包。需要代为操作校内平台时，使用宿主平台自带的浏览器能力即可。

---

## 二、用法

直接用自然语言说需求，**不需要记分类名，也不需要斜杠命令**。

| 你想做什么 | 直接这样说 |
|---|---|
| 搞懂一个概念 | 「这步怎么来的，没听懂」 |
| 系统学一门课 | 「我这学期要自学信号与系统」 |
| 整理笔记 | 「把这份讲义整理成笔记」 |
| 备考 | 「下周考高数，怎么复习」 |
| 写实验报告 | 「实验报告的数据处理部分怎么写」 |
| 查校务 | 「转专业需要什么材料」 |
| 查通知 | 「最近有什么奖学金通知」 |
| 查文献 | 「帮我找关于柔性传感器的综述」 |
| 代操作平台 | 「帮我上教务系统查一下这学期课表」 |

**斜杠命令**（可选，`commands/`）：`/learn` `/notes` `/exam` `/paper` `/code` `/search` `/campus`

---

## 三、配置

`config.yaml` 是唯一需要按学期修改的文件：

```yaml
school:
  name: 大连理工大学
  domain: dlut.edu.cn
student:
  campus: null      # 凌水主校区 / 开发区校区 / 盘锦校区
  college: null
  grade: null
term: null
courses: []
exam_weeks: []
```

`null` 表示未知，**不会被当作事实使用**。只有用户明确确认的信息才作为个人背景。

---

## 四、校内平台代操作

用户明确授权后，`portal-operator` 直接打开目标平台并执行操作，然后回报结果。

| 类别 | 处理 |
|---|---|
| 查询类（课表、成绩、通知、借阅） | 直接执行 |
| 涉及支付金额 | 复述金额与用途，确认后继续 |
| 不可撤销操作（提交报名、退课、退宿） | 复述操作内容与后果，确认后提交 |

**凭证处理**：用户名、密码、验证码只留在浏览器会话里，不写入任何文件、日志或回复正文。页面上的身份证号、银行卡、家庭信息不主动读取也不转述。

**平台打不开时**：需要短信验证码、人脸识别等用户本人环节 → 停下请用户完成再继续；系统维护或校外不可达 → 说明原因并给替代路径（WebVPN / 线下窗口 / 公开来源）。

平台清单见 `references/dlut-login-sites.md`。

---

## 五、安全兜底

| 情形 | 联系方式 |
|---|---|
| 自伤 / 轻生念头 | **12356**（24 小时）、**010-82951332**；已有具体计划 → **110 / 120** |
| 转账被骗 | 挂失银行卡 + **96110** + **110** |
| 急症、外伤、意识异常 | **120** |

---

## 六、扩展

| 换什么 | 改哪里 |
|---|---|
| 换学期 / 课程 | `config.yaml` 的 `term` / `courses` / `exam_weeks` |
| 加 skill | 新建 `skills/<name>/SKILL.md`，frontmatter 只写 `name` + `description` |
| 扩 DUT 信息库 | `references/dlut-*.md` |
| 换学校 | `config.yaml` 的 `school` 段 + `references/dlut-*.md` |

新增 skill 的章节规范见 [`docs/skill-anatomy.md`](docs/skill-anatomy.md)。
