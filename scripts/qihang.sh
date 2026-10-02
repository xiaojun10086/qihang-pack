#!/usr/bin/env bash
# 「启航」学伴包 v2.10.0 · 三级结构管理脚本（LearnBuddy 目标平台）
# 用法: bash qihang.sh {status|platform|probe|install|domains|registry|records|new-term}
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="${ROOT}/config.yaml"
PUBLIC="${ROOT}/references/dlut-official-sites.md"
PRIVATE="${ROOT}/references/dlut-login-sites.md"
DOMAINS_DIR="${ROOT}/domains"
HOME_DIR="${HOME:-$USERPROFILE}"

# ---------- 多平台探测 ----------
# v2.8：本包只适配 LearnBuddy / WorkBuddy 单一目标平台（原多平台探测已移除）
detect_skills_dir() {
  for d in "${HOME_DIR}/.learnbuddy/skills" "${ROOT}/../.learnbuddy/skills"; do
    [ -d "$d" ] && { echo "$d"; return 0; }
  done
  echo "${HOME_DIR}/.learnbuddy/skills"
}
SKILLS_DIR="$(detect_skills_dir)"

# v2.8：只认 LearnBuddy / WorkBuddy（唯一目标平台）
platform_of() {
  case "$1" in
    */.learnbuddy/skills) echo "LearnBuddy / WorkBuddy" ;;
    *) echo "非目标平台（本包只适配 LearnBuddy）" ;;
  esac
}

# v2.7 修复：安装到 ~/.learnbuddy/skills/qihang 时，ROOT/.. = ~/.learnbuddy/skills，
# 旧式 "${ROOT}/../.learnbuddy/memory/qihang" 会解析成 ~/.learnbuddy/skills/.learnbuddy/... （错误路径）。
# 现改为：优先工作区档案目录，其次平台技能目录旁，最后回落到包内 records/。
RECORDS_DIR_DEFAULT=""
for _c in "${ROOT}/../.learnbuddy/memory/qihang" "${ROOT}/../../memory/qihang" "${ROOT}/records"; do
  case "$_c" in *"/skills/.learnbuddy/"*) continue ;; esac   # 排除已知错误拼接
  if [ -d "$(dirname "$_c")" ]; then RECORDS_DIR_DEFAULT="$_c"; break; fi
done
[ -n "$RECORDS_DIR_DEFAULT" ] || RECORDS_DIR_DEFAULT="${ROOT}/records"

# 域ID|目录slug|主库外仓库|安装命令
REGISTRY="S1|course-qa|mattpocock/skills|npx skills add mattpocock/skills@teach
S2|lecture-notes|Jellypod-Inc/school-skills|npx skills add Jellypod-Inc/school-skills
S3|assignment|kgraph57/paper-writer-skill|npx skills add kgraph57/paper-writer-skill
S4|exam-prep|GlacierXiaowei/structured-learning-skill|npx skills add glacierxiaowei/structured-learning
S5|academic-writing|Imbad0202/academic-research-skills|npx skills add Imbad0202/academic-research-skills
S6|language|YANZHANLIN/ielts-claude-skills|npx skills add YANZHANLIN/ielts-claude-skills
F1|campus-affairs|googleworkspace/cli|npx skills add googleworkspace/cli
F2|focus|alirezarezvani/claude-skills|npx skills add alirezarezvani/claude-skills
F7|further-study|Haadhi76/SOP_Consultant|npx skills add Haadhi76/SOP_Consultant
F8|career|Paramchoudhary/ResumeSkills|npx skills add Paramchoudhary/ResumeSkills
R1|literature|xwmxcz/papers-skill|npx skills add xwmxcz/papers-skill
R2|experiment-data|K-Dense-AI/scientific-agent-skills|npx skills add K-Dense-AI/scientific-agent-skills
R3|research-tools|mattpocock/skills|npx skills add mattpocock/skills@teach
R4|publication|Imbad0202/academic-research-skills|npx skills add Imbad0202/academic-research-skills
R5|integrity|NeoLabHQ/context-engineering-kit|npx skills add NeoLabHQ/context-engineering-kit"

# v2.9：公开站「表格数据行」= 去掉分隔行与表头行（表头 = 其下一行为分隔行）。
# 旧版用 `grep -o ✅` 统计会把正文里的标记一并算入（得 71/26），正确口径为 67/21。
pub_rows() {
  awk '{l[NR]=$0} END{for(i=1;i<=NR;i++){ if(l[i]~/^\|/ && l[i]!~/^\|[ :|-]+\|$/ && l[i+1]!~/^\|[ :|-]+\|$/) print l[i] }}' "$PUBLIC"
}

is_installed() { [ -d "${SKILLS_DIR}/$1" ]; }

cmd_platform() {
  echo "「启航」平台探测"
  echo "----------------------------------------"
  echo "当前生效 skills 目录: ${SKILLS_DIR}"
  echo "  → 判定平台: $(platform_of "$SKILLS_DIR")"
  echo ""
  echo "本机可用安装位置："
  for d in "${HOME_DIR}/.learnbuddy/skills" "${ROOT}/../.learnbuddy/skills"; do
    if [ -d "$d" ]; then printf '  ✓ %-46s (%s)\n' "$d" "$(platform_of "$d")"
    else printf '  · %-46s 未安装\n' "$d"; fi
  done
  echo ""
  echo "学习档案目录: ${RECORDS_DIR_DEFAULT}"
  echo "插件清单: $([ -f "$ROOT/.codebuddy-plugin/plugin.json" ] && echo '✓ 已含 .codebuddy-plugin/plugin.json' || echo '✗ 缺失')"
}

cmd_status() {
  echo "「启航」学伴包 v2.10.0 · 状态"
  echo "平台: $(platform_of "$SKILLS_DIR")  |  skills: ${SKILLS_DIR}"
  echo "----------------------------------------"
  echo "[1级] skill 库"
  for f in library/SKILL.md library/clarity.md library/domain-review.md library/output-spec.md \
           library/memory.md library/login-policy.md library/domain-review-cases.md library/output-checklist.md; do
    [ -f "$ROOT/$f" ] && printf '  ✓ %s\n' "$f" || printf '  ✗ %s\n' "$f"
  done
  echo "[2级] 域"
  nd=$(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ')
  ns=$(find "$DOMAINS_DIR" -path '*/skills/local/*/SKILL.md' | wc -l | tr -d ' ')
  printf '  ✓ %s 个域 / %s 个库内 skill\n' "$nd" "$ns"
  echo "[3级] 库外 skill（兜底，可选）"
  local ok=0 total=0
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    total=$((total+1)); is_installed "$(basename "$repo")" && ok=$((ok+1))
  done <<< "$REGISTRY"
  printf '  已装 %s / %s\n' "$ok" "$total"
  echo "[资源]"
  [ -f "$PUBLIC" ]  && printf '  ✓ 公开站 %s 行\n' "$(grep -c '^|' "$PUBLIC")" || echo "  ✗ 公开站缺失"
  [ -f "$PRIVATE" ] && printf '  ✓ 私密站 %s 行\n' "$(grep -c '^|' "$PRIVATE")" || echo "  ✗ 私密站缺失"
  [ -f "$ROOT/references/skill-compliance-audit.md" ] && echo "  ✓ 合规自检已就绪"
}

cmd_probe() {
  echo "探测库外候选缺失项（不执行安装）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    is_installed "$(basename "$repo")" || printf '  %s 域缺 → %s\n      装: %s\n' "$id" "$repo" "$inst"
  done <<< "$REGISTRY"
  echo ""
  echo "提示：库内 skill 已全部就绪，库外仅作增强，可跳过。"
}

cmd_install() {
  echo "安装库外候选（已装跳过；可选）"
  while IFS='|' read -r id slug repo inst; do
    [ -z "$id" ] && continue
    if is_installed "$(basename "$repo")"; then printf '  %s 已装，跳过\n' "$id"; continue; fi
    case "$inst" in
      npx*) printf '  %s 安装中: %s\n' "$id" "$inst"; eval "$inst" || printf '  ! %s 失败，走库内降级\n' "$id" ;;
      *)    printf '  %s 请在 Agent 中执行: %s\n' "$id" "$inst" ;;
    esac
  done <<< "$REGISTRY"
}

cmd_domains() {
  echo "「启航」域清单（Level 2）"
  echo "----------------------------------------"
  for d in "$DOMAINS_DIR"/*/; do
    [ -d "$d" ] || continue
    n=$(find "$d/skills/local" -name SKILL.md 2>/dev/null | wc -l | tr -d ' ')
    printf '  %-24s 库内skill: %s\n' "$(basename "$d")" "$n"
  done
  echo "----------------------------------------"
  echo "共 $(find "$DOMAINS_DIR" -maxdepth 1 -mindepth 1 -type d | wc -l | tr -d ' ') 个域"
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

cmd_new_term() {
  [ -f "$CONFIG" ] && { cp "$CONFIG" "${CONFIG}.bak.$(date +%Y%m%d%H%M%S)"; echo "已备份 config.yaml"; }
  echo "新学期重置：改 ${CONFIG} 的 term / courses / exam_weeks 三项即可。"
  echo "1级库规则、19 个域、DUT 绑定均无需改动。"
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
