#!/usr/bin/env bash
# 「启航」DUT 私密站访问辅助（方案 A · 受控浏览器）
#
# 用法: bash dlut-read.sh <目标> [--yes] [--dry-run]
#   目标: 门户 | 课表 | 成绩等级 | 借阅 | 一卡通 | 网费 | 日程 | 邮箱提示 | 资助申请状态 | 就业投递记录 | 培养进度
#
# 本工具只打开独立浏览器供用户查看，不读取或输出网页内容。
# 铁律：① 只读 ② 不外传 ③ 临时 Profile 用后删除 ④ 不复用或关闭用户的其他浏览器会话
# 访问分级：L1 可自行查看 | L2 需 --yes 确认后打开 | L3 一律拒绝
# 退出码：0 成功或 L1 | 1 用法错误或需区分 | 2 L2 未确认 | 3 L3 拒绝 | 4 未装 agent-browser | 5 隔离校验失败 | 6 打开或清理失败
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-${USERPROFILE:-}}"
QIHANG_DIR="${HOME_DIR}/.qihang"
PROFILE_DIR=""
SESSION_ID="qihang-${PPID}-${RANDOM}-${RANDOM}"
SESSION_STARTED=0
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
  L1 可自行查看：课表 / 成绩等级 / 考试安排 / 借阅 / 一卡通余额 / 场馆预约状态 / 网费 / 日程
  L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读条数
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
  一卡通)    LEVEL=L1; URL="$PORTAL";        DESC="一卡通余额 / 账户有效期（不含消费明细）" ;;
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
  echo "   将打开的页面用途：$DESC"
  echo "   确认请加 --yes 重跑：bash dlut-read.sh '$TARGET' --yes"
  exit 2
fi

# ---------- 定位 agent-browser ----------
AB_BIN=""
AB_ARGS=()
if command -v agent-browser >/dev/null 2>&1; then
  AB_BIN="$(command -v agent-browser)"
else
  for base in "${HOME_DIR}/.workbuddy/binaries/node/versions"/*; do
    cand="${base}/node_modules/agent-browser/bin/agent-browser.js"
    if [ -f "$cand" ]; then
      AB_BIN="node"
      AB_ARGS=("$cand")
      break
    fi
  done
fi
if [ -z "$AB_BIN" ]; then
  # 不在此处直接退出：--dry-run 只是「打印执行计划」，不该被「本机是否装了浏览器」绑死。
  # 否则受限环境里 L1 的 dry-run 契约（独立 Profile / 未启动浏览器）无法被回归验证。
  AB_PENDING=1
  AB_LABEL="agent-browser（本机未安装）"
else
  AB_PENDING=0
  AB_LABEL="$AB_BIN"
fi

ab() {
  "$AB_BIN" "${AB_ARGS[@]}" --session "$SESSION_ID" "$@"
}

cleanup() {
  rc=$?
  trap - EXIT
  if [ "$SESSION_STARTED" -eq 1 ]; then
    if ! ab close >/dev/null 2>&1; then
      echo "❌ 无法确认独立浏览器会话已关闭；请检查并关闭会话「$SESSION_ID」。" >&2
      rc=6
    fi
  fi
  if [ -n "$PROFILE_DIR" ]; then
    if [ "$(dirname "$PROFILE_DIR")" != "$QIHANG_DIR" ] || \
       [ "$(basename "$PROFILE_DIR")" != browser-profile.* ]; then
      echo "❌ 拒绝清理路径不符合预期的临时 Profile。" >&2
      rc=6
    elif ! rm -rf -- "$PROFILE_DIR"; then
      echo "❌ 临时 Profile 清理失败：$PROFILE_DIR" >&2
      rc=6
    fi
  fi
  exit "$rc"
}

# ---------- 执行计划 ----------
cat <<EOF
「启航」DUT 私密站访问辅助 · 方案 A
----------------------------------------
目标      : $TARGET（$LEVEL）
说明      : $DESC
入口      : $URL
浏览器    : $AB_LABEL
Profile   : 每次新建临时目录，结束后删除
隐私      : 只读 · 不采集页面内容 · 不复用/关闭其他浏览器会话
----------------------------------------
EOF

if [ "$DRYRUN" -eq 1 ]; then
  echo "[dry-run] 将执行："
  echo "  1) 创建一次性独立会话与临时 Profile"
  echo "  2) $AB_LABEL --session <随机会话> open <入口> --headed --profile <临时目录>"
  echo "  3) 若未登录 → 提示你本人登录（本工具不接触凭证）"
  echo "  4) 你在浏览器窗口查看所需信息；工具不读取或输出页面内容"
  echo "  5) 结束时只关闭本次会话并删除临时 Profile"
  [ "$AB_PENDING" -eq 1 ] && \
    echo "[dry-run] ⚠️ 本机未安装 agent-browser；正式读取前先执行：npm install -g agent-browser && agent-browser install"
  echo "[dry-run] 未启动浏览器，未读任何数据。"
  exit 0
fi

if [ "$AB_PENDING" -eq 1 ]; then
  echo "❌ 未找到 agent-browser。安装：npm install -g agent-browser && agent-browser install" >&2
  exit 4
fi

if [ -z "$HOME_DIR" ]; then
  echo "❌ 无法确定用户目录，不能安全创建临时 Profile。" >&2
  exit 6
fi

if [ ! -t 0 ]; then
  echo "❌ 需要交互式终端，以便你在浏览器内自行查看信息。" >&2
  exit 6
fi

umask 077
mkdir -p "$QIHANG_DIR" || { echo "❌ 无法创建临时目录：$QIHANG_DIR" >&2; exit 6; }
PROFILE_DIR="$(mktemp -d "$QIHANG_DIR/browser-profile.XXXXXX")" || {
  echo "❌ 无法创建一次性浏览器 Profile。" >&2
  exit 6
}
trap cleanup EXIT

echo "▶ 打开独立入口（若未登录，请在弹出的窗口里自行登录）..."
SESSION_STARTED=1
OPEN_OUT="$(ab open "$URL" --headed --profile "$PROFILE_DIR" 2>&1)"
OPEN_RC=$?
if [ "$OPEN_RC" -ne 0 ]; then
  printf '%s\n' "$OPEN_OUT" >&2
  echo "❌ 独立浏览器启动失败。" >&2
  exit 6
fi

# ---------- 隔离校验：会话独立且 Profile 未被忽略 ----------
if printf '%s' "$OPEN_OUT" | grep -qiE 'profile[[:space:]]+ignored|daemon already running'; then
  cat >&2 <<EOF
❌ 中止：本次会话未使用独立 Profile（检测到 profile 被忽略 / daemon 已在运行）。
   隐私隔离已失效，不继续读取；退出时将尝试关闭本次会话并删除临时 Profile。
EOF
  exit 5
fi
echo "隔离校验: ✅ 使用随机命名的独立会话与一次性 Profile"

echo ""
echo "▶ 请只在浏览器窗口查看「$DESC」所需信息；本工具不会读取、复制或输出页面内容。"
echo "   请勿在聊天中粘贴密码、验证码或其他无关敏感信息。"
echo "   查看完成后按回车关闭本次会话并清理临时 Profile。"
read -r _ || true
SESSION_STARTED=0
if ! ab close; then
  echo "❌ 本次浏览器会话关闭失败；清理时将再次尝试。" >&2
  SESSION_STARTED=1
  exit 6
fi
echo "✅ 本次会话已关闭；临时 Profile 将在退出时删除。"
