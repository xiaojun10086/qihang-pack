#!/usr/bin/env bash
# 「启航」学伴包 v2.0 · 三级结构管理脚本
# 用法: bash qihang.sh {status|probe|install|domains|registry|new-term}
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${HOME}/.claude/skills"
CONFIG="${ROOT}/config.yaml"
PUBLIC="${ROOT}/references/dlut-official-sites.md"
PRIVATE="${ROOT}/references/dlut-login-sites.md"
DOMAINS_DIR="${ROOT}/domains"

# 域ID|目录slug|主库外仓库|安装命令   （每个域取第一条库外候选作代表）
REGISTRY="S1|course-qa|mattpocock/skills|npx skills add mattpocock/skills@teach
S2|lecture-notes|Jellypod-Inc/school-skills|/plugin marketplace add Jellypod-Inc/school-skills
S3|assignment|kgraph57/paper-writer-skill|npx skills add kgraph57/paper-writer-skill
S4|exam-prep|GlacierXiaowei/structured-learning-skill|npx skills add glacierxiaowei/structured-learning
S5|academic-writing|Imbad0202/academic-research-skills|/plugin marketplace add Imbad0202/academic-research-skills
S6|language|YANZHANLIN/ielts-claude-skills|手动复制
F1|campus-affairs|googleworkspace/cli|/plugin marketplace add googleworkspace/cli
F2|focus|alirezarezvani/claude-skills|/plugin marketplace add alirezarezvani/claude-skills
F7|further-study|Haadhi76/SOP_Consultant|npx skills add Haadhi76/SOP_Consultant
F8|career|Paramchoudhary/ResumeSkills|npx skills add Paramchoudhary/ResumeSkills
R1|literature|xwmxcz/papers-skill|npx skills add xwmxcz/papers-skill（需联网）
R2|experiment-data|K-Dense-AI/scientific-agent-skills|/plugin marketplace add K-Dense-AI/scientific-agent-skills
R3|research-tools|mattpocock/skills|npx skills add mattpocock/skills@teach
R4|publication|Imbad0202/academic-research-skills|/plugin marketplace add Imbad0202/academic-research-skills（CC-BY-NC）
R5|integrity|NeoLabHQ/context-engineering-kit|npx skills add NeoLabHQ/context-engineering-kit"

is_installed() { [ -d "${SKILLS_DIR}/$1" ]; }

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
  echo "「启航」学伴包 v2.0 · 状态"
  echo "----------------------------------------"
  echo "[1级] skill 库"
  for f in library/clarity.md library/domain-review.md library/output-spec.md; do
    [ -f "$ROOT/$f" ] && printf '  ✓ %s\n' "$f" || printf '  ✗ %s\n' "$f"
  done
  echo "[2级] 域"
  nd=$(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  ns=$(find "$DOMAINS_DIR" -path '*/skills/local/*/SKILL.md' | wc -l | tr -d ' ')
  printf '  ✓ %s 个域 / %s 个库内 skill\n' "$nd" "$ns"
  echo "[3级] 库外 skill 就绪度"
  local ok=0 total=0
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    total=$((total+1))
    nm=$(basename "$repo")
    if is_installed "$nm"; then ok=$((ok+1)); fi
  done <<< "$REGISTRY"
  printf '  已装 %s / %s（库外为兜底，不装也可用库内）\n' "$ok" "$total"
  echo "[资源] DUT 信息库"
  [ -f "$PUBLIC" ]  && printf '  ✓ 公开站 %s 行\n' "$(grep -c '^|' "$PUBLIC")" || echo "  ✗ 公开站缺失"
  [ -f "$PRIVATE" ] && printf '  ✓ 私密站 %s 行\n' "$(grep -c '^|' "$PRIVATE")" || echo "  ✗ 私密站缺失"
}

cmd_probe() {
  echo "探测库外候选缺失项（不执行安装）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    nm=$(basename "$repo")
    is_installed "$nm" || printf '  %s 域缺 → %s\n      装: %s\n' "$id" "$repo" "$inst"
  done <<< "$REGISTRY"
  echo ""
  echo "提示：库内 skill 已全部就绪，库外仅作增强，可跳过。"
}

cmd_install() {
  echo "安装库外候选（已装跳过；可选）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    nm=$(basename "$repo")
    if is_installed "$nm"; then printf '  %s 已装，跳过\n' "$id"; continue; fi
    case "$inst" in
      npx*) printf '  %s 安装中: %s\n' "$id" "$inst"; eval "$inst" || printf '  ! %s 失败，含库内降级\n' "$id" ;;
      *)    printf '  %s 请在 Agent 中执行: %s\n' "$id" "$inst" ;;
    esac
  done <<< "$REGISTRY"
}

cmd_registry() {
  echo "DUT 公开信息库: $PUBLIC"
  [ -f "$PUBLIC" ] && {
    echo "  表格行: $(grep -c '^|' "$PUBLIC")"
    echo "  已核验: $(grep -o '✅' "$PUBLIC" | wc -l | tr -d ' ')"
    echo "  待核实: $(grep -o '⚠️' "$PUBLIC" | wc -l | tr -d ' ')"
  }
  echo "DUT 私密站清单: $PRIVATE"
  [ -f "$PRIVATE" ] && echo "  表格行: $(grep -c '^|' "$PRIVATE")"
}

cmd_new_term() {
  [ -f "$CONFIG" ] && { cp "$CONFIG" "${CONFIG}.bak.$(date +%Y%m%d%H%M%S)"; echo "已备份 config.yaml"; }
  echo "新学期重置：改 ${CONFIG} 的 term / courses / exam_weeks 三项即可。"
  echo "1级库规则、19 个域、DUT 绑定均无需改动。"
}

case "${1:-status}" in
  status)   cmd_status ;;
  probe)    cmd_probe ;;
  install)  cmd_install ;;
  domains)  cmd_domains ;;
  registry) cmd_registry ;;
  new-term) cmd_new_term ;;
  *) echo "用法: bash qihang.sh {status|probe|install|domains|registry|new-term}"; exit 1 ;;
esac
