#!/usr/bin/env bash
# 「启航」学伴包 v3.2 · 三级结构管理脚本
# 用法: bash qihang.sh {status|platform|domains|registry|records|new-term}
# 定位：纯 DUT 特化库 —— 库内 skill 唯一通道，无任何库外安装通道。
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT}/config.yaml"
PUBLIC="${ROOT}/references/dlut-official-sites.md"
PRIVATE="${ROOT}/references/dlut-login-sites.md"
DOMAINS_DIR="${ROOT}/domains"

# 学习档案目录（见 `library/memory.md` §2.2 / §5）：
#   正常 → {ws}/.learnbuddy/memory/qihang/<域ID>.md ｜ 回落 → <包根>/records/<域ID>.md
# 包以「项目级」方式装在 {ws}/.learnbuddy/skills/qihang 时自动定位 {ws}；
# 用户级安装（~/.learnbuddy/skills/...）不写进平台托管的 ~/.learnbuddy/memory/，直接走包根回落。
RECORDS_DIR_DEFAULT=""
case "$ROOT" in
  "${HOME}/.learnbuddy/skills/"*) : ;;
  */.learnbuddy/skills/*) RECORDS_DIR_DEFAULT="${ROOT%%/.learnbuddy/skills/*}/.learnbuddy/memory/qihang" ;;
esac
[ -n "$RECORDS_DIR_DEFAULT" ] || RECORDS_DIR_DEFAULT="${ROOT}/records"

# 公开站「表格数据行」= 去掉分隔行与表头行（表头 = 其下一行为分隔行）。
pub_rows() {
  awk '{l[NR]=$0} END{for(i=1;i<=NR;i++){ if(l[i]~/^\|/ && l[i]!~/^\|[ :|-]+\|$/ && l[i+1]!~/^\|[ :|-]+\|$/) print l[i] }}' "$PUBLIC"
}

cmd_domains() {
  echo "「启航」域清单（Level 2）"
  echo "----------------------------------------"
  for d in "$DOMAINS_DIR"/*/; do
    [ -d "$d" ] || continue
    id=$(basename "$d")
    local_file="$d/skills/local"
    n=$(find "$local_file" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    printf '  %-24s 库内skill: %s\n' "$id" "$n"
  done
  echo "----------------------------------------"
  echo "共 $(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') 个域"
}

cmd_status() {
  echo "「启航」学伴包 v3.2 · 状态"
  echo "----------------------------------------"
  echo "[1级] skill 库"
  for f in library/README.md library/clarity.md library/domain-review.md library/output-spec.md \
           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md \
           library/skill-evolution.md; do
    [ -f "$ROOT/$f" ] && printf '  ✓ %s\n' "$f" || printf '  ✗ %s\n' "$f"
  done
  echo "[2级] 域（库内唯一通道）"
  nd=$(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  ns=$(find "$DOMAINS_DIR" -path '*/skills/local/*/SKILL.md' | wc -l | tr -d ' ')
  printf '  ✓ %s 个域 / %s 个库内 skill（开箱即用，零外部依赖）\n' "$nd" "$ns"
  _ext=$(find "$DOMAINS_DIR" -path '*/skills/external.md' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$_ext" -eq 0 ]; then
    printf '  ✓ 无库外通道（纯 DUT 特化库）\n'
  else
    printf '  ✗ 检出 %s 个库外通道 external.md（应为 0）\n' "$_ext"
  fi
  echo "[资源] DUT 信息库"
  [ -f "$PUBLIC" ]  && printf '  ✓ 公开站 %s 行\n' "$(grep -c '^|' "$PUBLIC")" || echo "  ✗ 公开站缺失"
  [ -f "$PRIVATE" ] && printf '  ✓ 私密站 %s 行\n' "$(grep -c '^|' "$PRIVATE")" || echo "  ✗ 私密站缺失"
}

cmd_registry() {
  echo "DUT 公开信息库: $PUBLIC"
  [ -f "$PUBLIC" ] && {
    echo "  表格行: $(grep -c '^|' "$PUBLIC")"
    _pr="$(pub_rows | wc -l | tr -d ' ')"
    echo "  数据条目: ${_pr}"
    echo "  已核验: $(pub_rows | grep -o '✅' | wc -l | tr -d ' ')"
    echo "  待核实: $(pub_rows | grep -o '⚠️' | wc -l | tr -d ' ')"
    _ok="$(pub_rows | grep -o '✅' | wc -l | tr -d ' ')"
    _wn="$(pub_rows | grep -o '⚠️' | wc -l | tr -d ' ')"
    echo "  未标注: $(( _pr - _ok - _wn ))"
  }
  echo "DUT 私密站清单: $PRIVATE"
  [ -f "$PRIVATE" ] && echo "  表格行: $(grep -c '^|' "$PRIVATE")"
}

cmd_new_term() {
  [ -f "$CONFIG" ] && { cp "$CONFIG" "${CONFIG}.bak.$(date +%Y%m%d%H%M%S)"; echo "已备份 config.yaml"; }
  echo "新学期重置：改 ${CONFIG} 的 term / courses / exam_weeks 三项即可。"
  echo "1级库规则、20 个域、DUT 绑定均无需改动。"
}

cmd_records() {
  case "${1:-list}" in
    --clear)
      # 安全实现：用「改名归档」替代「删除」，全程不调用 rm
      # （旧实现 cp + rm -rf "$变量" 属危险模式，变量为空时会误删上层目录）
      if [ -z "${RECORDS_DIR_DEFAULT:-}" ] || [ "$RECORDS_DIR_DEFAULT" = "/" ]; then
        echo "路径不安全，终止"; return 1
      fi
      if [ -d "$RECORDS_DIR_DEFAULT" ]; then
        BAK="${RECORDS_DIR_DEFAULT}.bak.$(date +%Y%m%d%H%M%S)"
        mv "$RECORDS_DIR_DEFAULT" "$BAK" && \
          echo "已归档学习档案（未删除，可自行清理）: $BAK"
      else
        echo "学习档案目录不存在: $RECORDS_DIR_DEFAULT"
      fi ;;
    *)
      echo "学习档案目录: ${RECORDS_DIR_DEFAULT}"
      if [ -d "$RECORDS_DIR_DEFAULT" ]; then
        ls -1 "$RECORDS_DIR_DEFAULT" 2>/dev/null | sed 's/^/  /'
        echo "共 $(ls -1 "$RECORDS_DIR_DEFAULT" 2>/dev/null | wc -l | tr -d ' ') 个域档案"
      else
        echo "  （尚未创建，首次写入时自动生成）"
      fi
      echo "清空: bash qihang.sh records --clear" ;;
  esac
}

cmd_platform() {
  echo "「启航」平台探测（LearnBuddy / WorkBuddy）"
  echo "----------------------------------------"
  echo "[运行环境]"
  printf '  OS        : %s\n' "$(uname -s 2>/dev/null || echo 未知)"
  printf '  Bash      : %s\n' "${BASH_VERSION:-未知}"
  printf '  HOME      : %s\n' "${HOME:-（未设置）}"
  printf '  包根      : %s\n' "$ROOT"
  echo "[平台目录]"
  if [ -d "${HOME}/.learnbuddy" ]; then
    printf '  ✓ 配置目录    %s\n' "${HOME}/.learnbuddy"
  else
    printf '  · 配置目录未创建  %s（首次使用平台时自动生成）\n' "${HOME}/.learnbuddy"
  fi
  echo "[本包安装位置]"
  _hit=0
  if [ -d "${HOME}/.learnbuddy/skills/qihang" ]; then
    printf '  ✓ 用户级  %s\n' "${HOME}/.learnbuddy/skills/qihang"; _hit=1
  fi
  case "$ROOT" in
    */.learnbuddy/skills/*)
      printf '  ✓ 项目级  %s\n' "$ROOT"; _hit=1 ;;
  esac
  [ "$_hit" = 0 ] && printf '  · 未在标准安装位检出（当前直接运行于 %s，不影响使用）\n' "$ROOT"
  echo "[记忆层]"
  if [ -f "${HOME}/.learnbuddy/MEMORY.md" ]; then
    printf '  ✓ 用户级长期记忆  %s/.learnbuddy/MEMORY.md\n' "$HOME"
  else
    printf '  · 用户级长期记忆未创建  %s/.learnbuddy/MEMORY.md\n' "$HOME"
  fi
  printf '  · 学习档案目录  %s\n' "$RECORDS_DIR_DEFAULT"
  if [ -d "$RECORDS_DIR_DEFAULT" ]; then
    printf '    已有 %s 个域档案\n' "$(ls -1 "$RECORDS_DIR_DEFAULT" 2>/dev/null | wc -l | tr -d ' ')"
  else
    printf '    （尚未创建，首次归档时自动生成）\n'
  fi
  echo "[就绪度]"
  _nd=$(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  _ns=$(find "$DOMAINS_DIR" -path '*/skills/local/*/SKILL.md' 2>/dev/null | wc -l | tr -d ' ')
  if [ "$_nd" -gt 0 ] && [ "$_ns" -gt 0 ]; then
    printf '  ✓ 可离线直接用：%s 个域 / %s 个库内 skill（零外部依赖）\n' "$_nd" "$_ns"
  else
    printf '  ✗ 包结构不完整，请重新解压后再试\n'
  fi
}

case "${1:-status}" in
  status)   cmd_status ;;
  platform) cmd_platform ;;
  domains)  cmd_domains ;;
  registry) cmd_registry ;;
  records)  shift; cmd_records "$@" ;;
  new-term) cmd_new_term ;;
  *) echo "用法: bash qihang.sh {status|platform|domains|registry|records|new-term}"; exit 1 ;;
esac
