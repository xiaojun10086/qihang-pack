#!/usr/bin/env bash
# 「启航」学伴包 v2.11.0 · 三级结构管理脚本
# 用法: bash qihang.sh {status|platform|probe|install|domains|registry|records|new-term}
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="${HOME}/.learnbuddy/skills"
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

# 域ID|目录slug|主库外仓库|安装命令   （每个域取第一条库外候选作代表）
REGISTRY="S1|course-qa|mattpocock/skills|npx skills add mattpocock/skills@teach
S2|lecture-notes|Jellypod-Inc/school-skills|npx skills add Jellypod-Inc/school-skills
S3|assignment|kgraph57/paper-writer-skill|npx skills add kgraph57/paper-writer-skill
S4|exam-prep|GlacierXiaowei/structured-learning-skill|npx skills add glacierxiaowei/structured-learning
S5|academic-writing|Imbad0202/academic-research-skills|npx skills add Imbad0202/academic-research-skills
S6|language|YANZHANLIN/ielts-claude-skills|手动复制
F1|campus-affairs|googleworkspace/cli|npx skills add googleworkspace/cli
F2|focus|alirezarezvani/claude-skills|npx skills add alirezarezvani/claude-skills
F7|further-study|Haadhi76/SOP_Consultant|npx skills add Haadhi76/SOP_Consultant
F8|career|Paramchoudhary/ResumeSkills|npx skills add Paramchoudhary/ResumeSkills
R1|literature|xwmxcz/papers-skill|npx skills add xwmxcz/papers-skill（需联网）
R2|experiment-data|K-Dense-AI/scientific-agent-skills|npx skills add K-Dense-AI/scientific-agent-skills
R3|research-tools|mattpocock/skills|npx skills add mattpocock/skills@teach
R4|publication|Imbad0202/academic-research-skills|npx skills add Imbad0202/academic-research-skills（CC-BY-NC）
R5|integrity|NeoLabHQ/context-engineering-kit|npx skills add NeoLabHQ/context-engineering-kit"

# 公开站「表格数据行」= 去掉分隔行与表头行（表头 = 其下一行为分隔行）。
# 旧版用 `grep -o ✅` 统计会把正文里的标记一并算入（得 71/26），正确口径为 67/21。
pub_rows() {
  awk '{l[NR]=$0} END{for(i=1;i<=NR;i++){ if(l[i]~/^\|/ && l[i]!~/^\|[ :|-]+\|$/ && l[i+1]!~/^\|[ :|-]+\|$/) print l[i] }}' "$PUBLIC"
}

# 推断库外候选在 ${SKILLS_DIR} 下真正落地的目录名。
# 优先级：① 安装命令里的显式 @skill 名；② `skills add <owner>/<name>` 的 <name>；③ 仓库末段。
# 旧实现直接取仓库名（mattpocock/skills → "skills"），与实际安装目录不符，导致 status 恒报「已装 0」。
cand_name() {
  local repo="$1" inst="$2" n=""
  n=$(printf '%s\n' "$inst" | sed -n 's/.*@\([A-Za-z0-9._-][A-Za-z0-9._-]*\).*/\1/p' | head -1)
  [ -n "$n" ] || n=$(printf '%s\n' "$inst" | sed -n 's#.*skills add [^ ]*/\([A-Za-z0-9._-][A-Za-z0-9._-]*\).*#\1#p' | head -1)
  [ -n "$n" ] || n=$(basename "$repo")
  printf '%s' "$n"
}

is_installed() { [ -d "${SKILLS_DIR}/$(cand_name "$1" "$2")" ]; }

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
  echo "「启航」学伴包 v2.11.0 · 状态"
  echo "----------------------------------------"
  echo "[1级] skill 库"
  for f in library/README.md library/clarity.md library/domain-review.md library/output-spec.md \
           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md; do
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
    if is_installed "$repo" "$inst"; then ok=$((ok+1)); fi
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
    is_installed "$repo" "$inst" || printf '  %s 域缺 → %s\n      期望目录: %s\n      装: %s\n' \
      "$id" "$repo" "$(cand_name "$repo" "$inst")" "$inst"
  done <<< "$REGISTRY"
  echo ""
  echo "提示：库内 skill 已全部就绪，库外仅作增强，可跳过。"
}

cmd_install() {
  echo "安装库外候选（已装跳过；可选）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    if is_installed "$repo" "$inst"; then printf '  %s 已装，跳过\n' "$id"; continue; fi
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
  echo "1级库规则、19 个域、DUT 绑定均无需改动。"
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
  if [ -d "$SKILLS_DIR" ]; then
    printf '  ✓ skills 目录  %s（已装 %s 个）\n' "$SKILLS_DIR" \
      "$(find "$SKILLS_DIR" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')"
  else
    printf '  · skills 目录未创建  %s\n' "$SKILLS_DIR"
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
    printf '  ✓ 可离线直接用：%s 个域 / %s 个库内 skill（不依赖库外安装）\n' "$_nd" "$_ns"
  else
    printf '  ✗ 包结构不完整，请重新解压后再试\n'
  fi
}

case "${1:-status}" in
  status)   cmd_status ;;
  platform) cmd_platform ;;
  probe)    cmd_probe ;;
  install)  cmd_install ;;
  domains)  cmd_domains ;;
  registry) cmd_registry ;;
  records)  shift; cmd_records "$@" ;;
  new-term) cmd_new_term ;;
  *) echo "用法: bash qihang.sh {status|platform|probe|install|domains|registry|records|new-term}"; exit 1 ;;
esac
