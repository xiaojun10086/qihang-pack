#!/usr/bin/env bash
# 「启航」DUT 私密站只读取数（方案 A · 受控浏览器）
#
# 用法: bash dlut-read.sh <目标> [--yes] [--dry-run]
#   目标: 门户 | 课表 | 借阅 | 一卡通 | 网费 | 日程 | 邮箱提示
#
# 铁律：① 只读 ② 不外传 ③ 不落盘  ④ 必须用独立 Profile
# 授权分级：L1 直接读 | L2 需 --yes 确认 | L3 一律拒绝
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOME_DIR="${HOME:-$USERPROFILE}"
PROFILE_DIR="${HOME_DIR}/.qihang/browser-profile"
SSO="https://sso.dlut.edu.cn/"
PORTAL="https://portal.dlut.edu.cn/"

TARGET="${1:-}"
shift || true
CONFIRM=0; DRYRUN=0
for a in "$@"; do
  [ "$a" = "--yes" ] && CONFIRM=1
  [ "$a" = "--dry-run" ] && DRYRUN=1
done

# ---------- L3 禁止清单（**语义匹配**：先拦，绝不打开页面） ----------
# v2.7 修复：旧版用精确 case 匹配，导致「缴费金额」「银行卡号」「身份证号」「邮件内容」
# 这类**变体写法绕开拒绝分支**（落到 usage，退出码 1）。改为关键词包含匹配，闭合绕过面。
L3_KEYS="缴费 金额 银行卡 身份证 家庭信息 家庭 邮件正文 邮件内容 心理记录 成绩明细 成绩单 简历"
L3_HIT=""
for _k in $L3_KEYS; do
  case "$TARGET" in *"$_k"*) L3_HIT="$_k"; break ;; esac
done
if [ -n "$L3_HIT" ]; then
  cat <<EOF
❌ 拒绝执行：目标「$TARGET」属于 L3 禁止读取级别（命中关键词「$L3_HIT」）。

「启航」私密站授权分级：
  L1 直接读   ：课表 / 成绩等级 / 借阅 / 一卡通余额 / 网费 / 日程 / 场馆预约状态
  L2 需确认   ：资助申请状态 / 就业投递记录 / 培养进度 / 邮箱未读提示
  L3 一律拒绝 ：缴费金额 / 银行卡 / 身份证 / 家庭信息 / 邮件正文 / 心理记录 / 成绩明细

匹配口径：**关键词包含**（不再是精确等于）。含「简历」也一律拒绝（个人经历数据）。
请自行到 https://portal.dlut.edu.cn/ 查看；本工具不代读、不代操作。
EOF
  exit 3
fi

case "$TARGET" in
  门户)      LEVEL=L1; URL="$PORTAL";        DESC="门户首页（课表/借阅/一卡通/网费/日程 聚合）" ;;
  课表)      LEVEL=L1; URL="$PORTAL";        DESC="我的课表（门户首页区块）" ;;
  借阅)      LEVEL=L1; URL="$PORTAL";        DESC="我的借阅（当前借阅册数）" ;;
  一卡通)    LEVEL=L1; URL="$PORTAL";        DESC="一卡通（当日消费/账户有效期，不含金额明细）" ;;
  网费)      LEVEL=L1; URL="$PORTAL";        DESC="网络自助（余额/流量）" ;;
  日程)      LEVEL=L1; URL="$PORTAL";        DESC="我的日程 / 校内通知" ;;
  邮箱提示)  LEVEL=L2; URL="$PORTAL";        DESC="邮箱未读提示（**不读邮件正文**）" ;;
  ""|*)
    sed -n '3,10p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
    echo ""
    echo "可用目标: 门户 课表 借阅 一卡通 网费 日程 邮箱提示"
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
  echo "❌ 未找到 agent-browser。安装：npm install -g agent-browser && agent-browser install" >&2
  exit 4
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
  echo "  1) $AB open <入口> --headed --profile \"$PROFILE_DIR\""
  echo "  2) 若未登录 → 提示你本人登录（本工具不接触凭证）"
  echo "  3) $AB snapshot -c           # 只读读取当前页面"
  echo "  4) 抽取「$DESC」相关字段后直接输出"
  echo "  5) $AB close --all           # 结束会话，不保存 Cookie"
  echo "[dry-run] 未启动浏览器，未读任何数据。"
  exit 0
fi

mkdir -p "$PROFILE_DIR"

echo "▶ 打开入口（若未登录，请在弹出的窗口里自行登录）..."
$AB open "$URL" --headed --profile "$PROFILE_DIR" 2>&1 | head -5

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
