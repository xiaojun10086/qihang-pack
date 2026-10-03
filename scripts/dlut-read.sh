#!/usr/bin/env bash
# 「启航」DUT 私密站只读取数（方案 A · 受控浏览器）
#
# 用法: bash dlut-read.sh <目标> [--yes] [--dry-run]
#   目标: 门户 | 课表 | 成绩等级 | 借阅 | 一卡通 | 网费 | 日程 | 邮箱提示 | 资助申请状态 | 就业投递记录 | 培养进度
#
# 铁律：① 只读 ② 不外传 ③ 不落盘  ④ 必须用独立 Profile
# 授权分级：L1 直接读 | L2 需 --yes 确认 | L3 一律拒绝
# 退出码：0 成功或 L1 | 1 用法错误或需区分 | 2 L2 未确认 | 3 L3 拒绝 | 4 未装 agent-browser | 5 隔离校验失败
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-$USERPROFILE}"
PROFILE_DIR="${HOME_DIR}/.qihang/browser-profile"
SSO="https://sso.dlut.edu.cn/"
PORTAL="https://portal.dlut.edu.cn/"
XSC="https://xsc.dlut.edu.cn/"      # 学生工作系统（资助/评奖）
JOB="https://job.dlut.edu.cn/"      # 就业信息网（投递记录）
GS="https://gs.dlut.edu.cn/"        # 研究生系统（培养进度）

TARGET="${1:-}"
shift || true
CONFIRM=0; DRYRUN=0
for a in "$@"; do
  [ "$a" = "--yes" ] && CONFIRM=1
  [ "$a" = "--dry-run" ] && DRYRUN=1
done

# ---------- L3 禁止清单（**语义匹配**：先拦，绝不打开页面） ----------
# 旧版用精确 case 匹配，导致「缴费金额」「银行卡号」「身份证号」「邮件内容」
# 这类**变体写法绕开拒绝分支**（落到 usage，退出码 1）。改为关键词包含匹配，闭合绕过面。
# 清单与 config.yaml 的 L3_forbidden 严格对齐（7 项 + 语义变体）：
#   缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细
# 变体补充：金额、家庭、邮件内容、成绩单、绩点（「绩点」属成绩明细，曾漏拦）。
L3_KEYS="缴费 金额 银行卡 身份证 家庭信息 家庭 邮件正文 邮件内容 心理记录 成绩明细 成绩单 绩点"
L3_HIT=""
for _k in $L3_KEYS; do
  case "$TARGET" in *"$_k"*) L3_HIT="$_k"; break ;; esac
done
# ---------- 类 B：宽松名词 × 明细语义（**共现**才判 L3，避免误伤公开信息）----------
# 只「收紧」不「放松」：不删除既有词，也不改 rc 语义。
# 反向保护：单说「心理咨询讲座」「成绩公布时间」等公开信息**不得**被拦。
if [ -z "$L3_HIT" ]; then
  case "$TARGET" in
    *心理*)
      case "$TARGET" in *记录*|*档案*|*测评结果*) L3_HIT="心理·插入型变体" ;; esac ;;
  esac
fi
if [ -z "$L3_HIT" ]; then
  case "$TARGET" in
    *成绩*)
      case "$TARGET" in *明细*|*单科*|*分数*|*绩点*) L3_HIT="成绩·插入型变体" ;; esac ;;
  esac
fi
if [ -z "$L3_HIT" ]; then
  case "$TARGET" in
    *各科*)
      case "$TARGET" in *分数*|*得分*|*成绩单*|*明细*) L3_HIT="各科·插入型变体" ;; esac ;;
  esac
fi
if [ -n "$L3_HIT" ]; then
  cat <<EOF
❌ 拒绝执行：目标「$TARGET」属于 L3 禁止读取级别（命中关键词「$L3_HIT」）。

「启航」私密站授权分级：
  L1 直接读   ：课表 / 成绩等级 / 考试安排 / 借阅 / 一卡通余额 / 场馆预约状态 / 网费 / 日程
  L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示
  L3 一律拒绝 ：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细

匹配口径：**关键词包含**（不再是精确等于）。含「绩点」也一律拒绝（属成绩明细）。
请自行到 https://portal.dlut.edu.cn/ 查看；本工具不代读、不代操作。
EOF
  exit 3
fi

# ---------- 裸词澄清（不得直接判级，必须先让用户区分） ----------
# 依据 library/login-policy.md「裸词澄清」：
#   裸「成绩」——L1 含「成绩等级」、L3 含「成绩明细」，两者都不是 → 必须先区分；
#   裸「邮件 / 邮箱」——L2 含「邮箱未读提示」、L3 含「邮件正文」→ 必须先区分。
# 此处的 rc=1 带**可判定的语义**（提示区分），与兜底 usage 的 rc=1 不同。
case "$TARGET" in
  成绩)
    cat <<EOF
⚠️ 「成绩」是裸词，不能直接判级 —— 请先区分你要哪一种：
     · 成绩等级 / 是否通过  → L1，可直接读（重跑：bash dlut-read.sh 成绩等级）
     · 单科分数 / 绩点明细  → L3，一律不读
   依据：config.yaml 的 L1_auto 含「成绩等级」、L3_forbidden 含「成绩明细」。
EOF
    exit 1 ;;
  邮件|邮箱)
    cat <<EOF
⚠️ 「邮件 / 邮箱」是裸词，不能直接判级 —— 请先区分你要哪一种：
     · 邮箱未读提示（只看未读条数）→ L2，加 --yes 可读（重跑：bash dlut-read.sh 邮箱提示 --yes）
     · 邮件正文                      → L3，一律不读
   依据：config.yaml 的 L2_confirm 含「邮箱未读提示」、L3_forbidden 含「邮件正文」。
EOF
    exit 1 ;;
esac

case "$TARGET" in
  门户)      LEVEL=L1; URL="$PORTAL";        DESC="门户首页（课表/借阅/一卡通/网费/日程 聚合）" ;;
  课表)      LEVEL=L1; URL="$PORTAL";        DESC="我的课表（门户首页区块）" ;;
  成绩等级)  LEVEL=L1; URL="$PORTAL";        DESC="成绩等级 / 是否通过（**不含单科分数明细**）" ;;
  借阅)      LEVEL=L1; URL="$PORTAL";        DESC="我的借阅（当前借阅册数）" ;;
  一卡通)    LEVEL=L1; URL="$PORTAL";        DESC="一卡通（当日消费/账户有效期，不含金额明细）" ;;
  网费)      LEVEL=L1; URL="$PORTAL";        DESC="网络自助（余额/流量）" ;;
  日程)      LEVEL=L1; URL="$PORTAL";        DESC="我的日程 / 校内通知" ;;
  邮箱提示)  LEVEL=L2; URL="$PORTAL";        DESC="邮箱未读提示（**不读邮件正文**）" ;;
  资助申请状态) LEVEL=L2; URL="$XSC";       DESC="资助 / 评奖申请状态（只看办理进度，不看数额与家庭信息）" ;;
  就业投递记录) LEVEL=L2; URL="$JOB";       DESC="就业投递记录（只看投递与面试状态，不看个人经历正文）" ;;
  培养进度)     LEVEL=L2; URL="$GS";        DESC="研究生培养进度（学分完成度 / 开题状态）" ;;
  ""|*)
    sed -n '3,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    echo ""
    echo "可用目标: 门户 课表 成绩等级 借阅 一卡通 网费 日程 邮箱提示 资助申请状态 就业投递记录 培养进度"
    exit 1 ;;
esac

# ---------- L2 需确认 ----------
if [ "$LEVEL" = "L2" ] && [ "$CONFIRM" -ne 1 ]; then
  echo "⚠️ 目标「$TARGET」属于 L2 级别（需确认）。"
  echo "   将读取：$DESC"
  echo "   确认请加 --yes 重跑：bash dlut-read.sh '$TARGET' --yes"
  exit 2
fi

# ---------- 定位 agent-browser ----------
AB=""
if command -v agent-browser >/dev/null 2>&1; then
  AB="agent-browser"
else
  for base in "${HOME_DIR}/.workbuddy/binaries/node/versions"/*; do
    cand="${base}/node_modules/agent-browser/bin/agent-browser.js"
    if [ -f "$cand" ]; then
      AB="node ${cand}"
      break
    fi
  done
fi
if [ -z "$AB" ]; then
  # 不在此处直接退出：--dry-run 只是「打印执行计划」，不该被「本机是否装了浏览器」绑死。
  # 否则受限环境里 L1 的 dry-run 契约（独立 Profile / 未启动浏览器）无法被回归验证。
  AB_PENDING=1
  AB="agent-browser（本机未安装）"
else
  AB_PENDING=0
fi

# ---------- 执行计划 ----------
cat <<EOF
「启航」DUT 只读取数 · 方案 A
----------------------------------------
目标      : $TARGET（$LEVEL）
说明      : $DESC
入口      : $URL
浏览器    : $AB
独立Profile: $PROFILE_DIR   ← 强制隔离（绝不复用真实 Chrome profile）
隐私      : 只读 · 不外传 · 不落盘 · 结束即 close --all
----------------------------------------
EOF

if [ "$DRYRUN" -eq 1 ]; then
  echo "[dry-run] 将执行："
  echo "  0) $AB close --all           # 先清既有会话，保证下一步 --profile 不被忽略"
  echo "  1) $AB open <入口> --headed --profile \"$PROFILE_DIR\""
  echo "  2) 若未登录 → 提示你本人登录（本工具不接触凭证）"
  echo "  3) $AB snapshot -c           # 只读读取当前页面"
  echo "  4) 抽取「$DESC」相关字段后直接输出"
  echo "  5) $AB close --all           # 结束会话，不保存 Cookie"
  [ "$AB_PENDING" -eq 1 ] && \
    echo "[dry-run] ⚠️ 本机未安装 agent-browser；正式读取前先执行：npm install -g agent-browser && agent-browser install"
  echo "[dry-run] 未启动浏览器，未读任何数据。"
  exit 0
fi

if [ "$AB_PENDING" -eq 1 ]; then
  echo "❌ 未找到 agent-browser。安装：npm install -g agent-browser && agent-browser install" >&2
  exit 4
fi

mkdir -p "$PROFILE_DIR"

# ---------- 隔离前置：先关掉既有 daemon 会话（否则 --profile 会被静默忽略） ----------
$AB close --all >/dev/null 2>&1 || true

echo "▶ 打开入口（若未登录，请在弹出的窗口里自行登录）..."
OPEN_OUT="$($AB open "$URL" --headed --profile "$PROFILE_DIR" 2>&1 | head -20)"
echo "$OPEN_OUT"

# ---------- 隔离校验：--profile 必须真的生效（失效即中止，不在未隔离窗口继续读）----------
PROFILE_BASE="$(basename "$PROFILE_DIR")"
if printf '%s' "$OPEN_OUT" | grep -qiE 'profile[[:space:]]+ignored|daemon already running'; then
  cat >&2 <<EOF
❌ 中止：本次会话未使用独立 Profile（检测到 profile 被忽略 / daemon 已在运行）。
   隐私隔离已失效，不继续读取。请先执行：$AB close --all，再重跑本命令。
EOF
  exit 5
fi
if printf '%s' "$OPEN_OUT" | grep -qF "$PROFILE_BASE"; then
  echo "隔离校验: ✅ 独立 Profile 已生效（$PROFILE_DIR）"
else
  echo "隔离校验: ⚠️ 浏览器未回显 Profile 路径，无法从输出直接确认；"
  echo "          已通过「打开前 close --all」保证无既有会话可复用（凭据隔离成立）。"
fi

echo ""
echo "▶ 等待页面就绪（加载完成后回车继续）..."
read -r _ || true

echo ""
echo "▶ 只读读取 ..."
$AB snapshot -c 2>&1 | head -200

echo ""
echo "▶ 关闭会话 ..."
$AB close --all 2>&1 | head -3
echo "会话状态: $($AB session list 2>&1 | head -1)"
echo ""
echo "✅ 完成。以上内容仅服务本次回答，未写入任何文件。"
echo "   如需写入学习档案，由 1 级库按 library/memory.md 规则处理（本脚本不写）。"
