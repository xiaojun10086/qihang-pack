#!/usr/bin/env bash
# 「启航」学伴包 · 能力域管理脚本 v1.1
# 用法: bash qihang.sh {probe|install|status|new-term|registry}
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"
CONFIG="${ROOT}/config.yaml"
REGISTRY_FILE="${ROOT}/references/dlut-official-sites.md"

# 域 : 探测目录名 : 安装命令   （G 域为内置数据，不在此列）
REGISTRY="A:gws-calendar:/plugin marketplace add googleworkspace/cli
B:obsidian-skills:/plugin marketplace add kepano/obsidian-skills
C:math-skill:npx skills add googlarz/math-skill
D:structured-learning:npx skills add glacierxiaowei/structured-learning
E:academic-pptx-skill:npx skills add Gabberflast/academic-pptx-skill
F:pomodoro:npx skills add jakedahn/pomodoro"

is_installed() { [ -d "${SKILLS_DIR}/$1" ]; }

cmd_status() {
  echo "「启航」学伴包 · 能力域状态"
  echo "skills 目录: ${SKILLS_DIR}"
  echo "----------------------------------------"
  local ok=0 total=0
  # G 域：内置，检查信息库文件
  total=$((total + 1))
  if [ -f "$REGISTRY_FILE" ]; then
    printf '  G ✓  校情信息（内置）  %s 行\n' "$(grep -c '^|' "$REGISTRY_FILE" 2>/dev/null || echo 0)"
    ok=$((ok + 1))
  else
    printf '  G ✗  校情信息（内置）  信息库文件缺失\n'
  fi
  while IFS=: read -r d name _; do
    [ -z "$d" ] && continue
    total=$((total + 1))
    if is_installed "$name"; then printf '  %s ✓  %s\n' "$d" "$name"; ok=$((ok + 1))
    else printf '  %s ✗  %s\n' "$d" "$name"; fi
  done <<< "$REGISTRY"
  echo "----------------------------------------"
  echo "就绪: ${ok}/${total}"
}

cmd_probe() {
  echo "探测缺失能力域（不执行任何安装）"
  [ -f "$REGISTRY_FILE" ] || echo "  ! G 域信息库文件缺失: ${REGISTRY_FILE}"
  while IFS=: read -r d name inst; do
    [ -z "$d" ] && continue
    if ! is_installed "$name"; then
      printf '  缺 %s 域 → %s\n      装: %s\n' "$d" "$name" "$inst"
    fi
  done <<< "$REGISTRY"
  echo "提示: C 域另有降级件 teach（npx skills add mattpocock/skills@teach）"
}

cmd_install() {
  echo "一键装齐（已装自动跳过）"
  while IFS=: read -r d name inst; do
    [ -z "$d" ] && continue
    if is_installed "$name"; then
      printf '  %s 域已装，跳过\n' "$d"
      continue
    fi
    case "$inst" in
      npx*) printf '  %s 域安装中: %s\n' "$d" "$inst"; eval "$inst" || printf '  ! %s 域失败，请按 routing-table.md §10 降级\n' "$d" ;;
      *)    printf '  %s 域请在 Agent 中执行: %s\n' "$d" "$inst" ;;
    esac
  done <<< "$REGISTRY"
  echo "完成后运行: bash qihang.sh status"
}

cmd_registry() {
  if [ ! -f "$REGISTRY_FILE" ]; then echo "信息库文件缺失: ${REGISTRY_FILE}"; return 1; fi
  echo "DUT 官方信息库: ${REGISTRY_FILE}"
  echo "总条目(表格行): $(grep -c '^|' "$REGISTRY_FILE")"
  echo "已核验(✅):     $(grep -o '✅' "$REGISTRY_FILE" | wc -l)"
  echo "待核实(⚠️):    $(grep -o '⚠️' "$REGISTRY_FILE" | wc -l)"
}

cmd_new_term() {
  if [ -f "$CONFIG" ]; then
    cp "$CONFIG" "${CONFIG}.bak.$(date +%Y%m%d%H%M%S)"
    echo "已备份原 config.yaml"
  fi
  echo "新学期重置：请编辑 ${CONFIG} 中的 term / courses / exam_weeks 三项即可。"
  echo "流程逻辑（澄清门 / 路由 / 输出模板）与 DUT 绑定无需改动。"
}

case "${1:-status}" in
  probe)    cmd_probe ;;
  install)  cmd_install ;;
  status)   cmd_status ;;
  registry) cmd_registry ;;
  new-term) cmd_new_term ;;
  *) echo "用法: bash qihang.sh {probe|install|status|registry|new-term}"; exit 1 ;;
esac
