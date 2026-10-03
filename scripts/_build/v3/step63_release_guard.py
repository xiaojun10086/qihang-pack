# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3 生成链 · 第 26 层 · 交付分支护栏（v3.3.1 → v3.3.2）】
#
# 触发（**同一类事故已发生两次**）：
#   2026-10-03 · 第 1 次：commit `2ace1fd「对齐」` 把 **17 个**不随包的文件（.idea×6 +
#     .learnbuddy/memory×3 + 8 份过程文档）强加进 `release` 分支并推送 → 公开分支泄露本机路径。
#   2026-10-03 · 第 2 次：commit `074ed37「对齐」` 又加了 **5 个**（.idea×2 + .learnbuddy/memory×3，
#     共 2458 行）并推送。
#   两次都是 `git add -f`（这些路径**都在 `.gitignore` 里**，`git add -A` 不会收）绕过了忽略规则。
#
# 本轮装**两道闸**，把「靠自觉」换成「靠机制」：
#   ① **提交时拦截**：git `pre-commit` 钩子 —— 暂存区出现「不随包」路径即拒绝提交。
#      分支感知：`release` 分支连 `scripts/_build/` 也拦；其他分支只拦 `.learnbuddy/`、`.idea/`、过程文档。
#   ② **自检可见**：`selfcheck.sh` 新增 `[11]` 段 —— 若存在 `release` 分支，
#      断言「release 树 == main 交付集」，不一致即 FAIL 并列出多余路径。
#
# 用法：python scripts/_build/v3/step63_release_guard.py [仓库根]
# 幂等：文件「存在即跳过」；selfcheck 段带哨兵；版本号全部替换。
# -------------------------------------------------------------------------------
import io
import os
import shutil
import stat
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith('-')
                       else os.path.join(HERE, '..', '..', '..'))
OLD_REV, NEW_REV = '3.3.1', '3.3.2'


def read(rel):
    p = os.path.join(ROOT, rel)
    return io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None


def write(rel, t, mode=None):
    p = os.path.join(ROOT, rel)
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    cur = io.open(p, 'r', encoding='utf-8').read() if os.path.isfile(p) else None
    if cur == t:
        print('  [SAME] %s（内容一致）' % rel)
    else:
        io.open(p, 'w', encoding='utf-8', newline='\n').write(t)
        print('  [OK]   %s' % rel)
    if mode:
        os.chmod(p, mode)


def edit(rel, pairs):
    t = read(rel)
    if t is None:
        print('  [SKIP] %s（不存在）' % rel)
        return
    o = t
    for item in pairs:
        a, b = item[0], item[1]
        sent = item[2] if len(item) > 2 else None
        if sent and sent in t:
            print('  [SAME] %s :: %r' % (rel, sent[:46]))
            continue
        if a not in t:
            print('  [MISS] %s :: %r' % (rel, a[:46]))
            continue
        t = t.replace(a, b, 1)
        print('  [OK]   %s :: %r' % (rel, a[:46]))
    if t != o:
        write(rel, t)


def replace_all(rel, a, b):
    t = read(rel)
    if t is None or a not in t:
        return 0
    n = t.count(a)
    write(rel, t.replace(a, b))
    return n


# =============================================================== A) pre-commit 钩子
print('== A) pre-commit 钩子（提交时拦截不随包路径）==')
HOOK = '''#!/bin/sh
# ---------------------------------------------------------------------------
# 「启航」提交护栏 —— 禁止把「不随包分发」的路径提交进仓库（尤其 release 分支）。
#
# 为什么必须有它（不是靠自觉）：
#   2026-10-03 一天之内发生 **两次** 同类事故 —— 有人用 `git add -f` 绕过 .gitignore，
#   把 `.learnbuddy/memory/`（含本机路径，共 2200+ 行）、`.idea/` 与 8 份内部过程文档
#   强加进 `release` 交付分支**并推送**。release 是公开分支，且 README 的「下载交付包」
#   直链就是它的 zip → 等于公网泄露。第二次发生在第一次修好之后 15 分钟内。
#   → 结论：**只靠流程约束不可靠，必须在提交动作上设闸**。
#
# 规则（分支感知）：
#   · 任何分支：`.learnbuddy/`、`.idea/`、`.vscode/`、8 份内部过程文档 一律禁止提交；
#   · `release` 分支：**额外**禁止 `scripts/_build/` 与 `.gitignore`（交付树不含开发物与元数据）。
#
# 用法：本文件由 `scripts/_build/hooks/install.sh` 安装到 `.git/hooks/pre-commit`。
#       确需绕过时用 `git commit --no-verify`，并请在提交信息里写明理由。
# ---------------------------------------------------------------------------
BLOCKED_ANY='^(\\.learnbuddy/|\\.idea/|\\.vscode/|references/(validation-report|acceptance-v2|review-report-v2\\.2|review-report-v2\\.3|review-report-v2\\.4|stress-test-v3|alignment-audit-v3|需求确认书-v2三级结构)\\.md$)'
BLOCKED_REL='^(\\.learnbuddy/|\\.idea/|\\.vscode/|scripts/_build/|\\.gitignore$|references/(validation-report|acceptance-v2|review-report-v2\\.2|review-report-v2\\.3|review-report-v2\\.4|stress-test-v3|alignment-audit-v3|需求确认书-v2三级结构)\\.md$)'

branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null || echo '')
case "$branch" in
  release) pattern="$BLOCKED_REL" ;;
  *)       pattern="$BLOCKED_ANY" ;;
esac

staged=$(git diff --cached --name-only --diff-filter=ACMR 2>/dev/null || true)
[ -z "$staged" ] && exit 0
bad=$(printf '%s\\n' "$staged" | grep -E "$pattern" || true)

if [ -n "$bad" ]; then
  echo "✖ 提交被拦下（分支：${branch:-detached}）" >&2
  echo "  下列路径属「不随包分发」，禁止提交：" >&2
  printf '    %s\\n' $bad >&2
  echo "  依据：scripts/_build/README.md「发布方式」段；交付分支刷新只走 release_branch.py。" >&2
  echo "  确需绕过：git commit --no-verify（并在提交信息里写明理由）。" >&2
  exit 1
fi
exit 0
'''
write('scripts/_build/hooks/pre-commit', HOOK, mode=0o755)

INSTALL = '''#!/bin/sh
# 安装「启航」提交护栏到 .git/hooks/pre-commit（幂等）。
# 用法：bash scripts/_build/hooks/install.sh [仓库根]
set -eu
ROOT="${1:-$(cd "$(dirname "$0")/../../.." && pwd)}"
SRC="$ROOT/scripts/_build/hooks/pre-commit"
DST="$ROOT/.git/hooks/pre-commit"
[ -d "$ROOT/.git" ] || { echo "跳过：$ROOT 不是 git 仓库"; exit 0; }
cp "$SRC" "$DST"
chmod +x "$DST"
echo "已安装：$DST"
echo "自测：在 release 分支上 git add -f .learnbuddy/memory/MEMORY.md && git commit 应被拒绝。"
'''
write('scripts/_build/hooks/install.sh', INSTALL, mode=0o755)

hook_src = os.path.join(ROOT, 'scripts', '_build', 'hooks', 'pre-commit')
hook_dst = os.path.join(ROOT, '.git', 'hooks', 'pre-commit')
if os.path.isdir(os.path.join(ROOT, '.git')):
    same = os.path.isfile(hook_dst) and \
        io.open(hook_dst, encoding='utf-8', errors='replace').read() == HOOK
    if same:
        print('  [SAME] .git/hooks/pre-commit（已安装）')
    else:
        shutil.copyfile(hook_src, hook_dst)
        os.chmod(hook_dst, 0o755)
        print('  [OK]   已安装 .git/hooks/pre-commit')
else:
    print('  [SKIP] 无 .git（交付树）：钩子不适用')

# =============================================================== B) .gitattributes 锁 LF
# 实测踩到：`scripts/_build/hooks/pre-commit` **没有扩展名**，不匹配任何 `*.xx` 规则
# → `* text=auto` + 本机 `core.autocrlf=true` 会在 checkout 时写成 **CRLF**
# → 钩子带 \r 在 sh 下报 `$'\r': command not found`，**护栏本身就是坏的**。
print('== B) .gitattributes：为无扩展名的钩子锁 LF ==')
edit('.gitattributes', [
    ('LICENSE         text eol=lf',
     'LICENSE         text eol=lf\n'
     '# 无扩展名的可执行脚本（git 钩子等）：不匹配上面的 *.xx 规则，\n'
     '# 若不显式锁定，checkout 时会被写成 CRLF → 钩子在 sh 下不可执行（实测踩到）。\n'
     'scripts/_build/hooks/*   text eol=lf',
     'scripts/_build/hooks/*'),
])

# =============================================================== C) selfcheck [11]
print('== C) selfcheck.sh 新增 [11] 交付分支一致性 ==')
S11 = '''# ---------- 11. 交付分支一致性（有 .git 时才查；交付树无 .git → 跳过） ----------
# 事故驱动（2026-10-03 两次）：release 分支被 git add -f 塞进 .learnbuddy/.idea/过程文档。
# 判据：release 树里**每个**文件都必须存在于 main（release ⊆ main 恒成立）——「只在 release 出现」即污染。
# ⚠️ 首版曾把 `.learnbuddy/` 等**预先过滤掉**，而它恰恰是最常见的污染源 → 断言对真实事故完全无效；
#    实测（故意污染 release 后 [11] 仍报 OK）发现后改为**不预先过滤**，
#    这正是本项目「断言必须经负向自检，否则可能是空转」的又一实例。
echo "[11] 交付分支一致性"
if [ -d .git ] && git rev-parse --verify --quiet release >/dev/null 2>&1; then
  _extra=$(git ls-tree -r release --name-only | while IFS= read -r _f; do
             git cat-file -e "main:$_f" 2>/dev/null || echo "$_f"
           done)
  if [ -n "$_extra" ]; then
    _n=$(printf '%s\\n' "$_extra" | grep -c . )
    bad "release 分支含 $_n 个不随包文件（应为 0）"
    printf '%s\\n' "$_extra" | head -8 | while IFS= read -r _l; do echo "       + $_l"; done
    echo "       → 修法：python scripts/_build/v3/release/release_branch.py --apply --allow-delete"
  else
    ok "release 树 == main 交付集（无多余文件）"
  fi
else
  ok "无 .git 或无 release 分支 → 跳过（交付树正常路径）"
fi

'''
t = read('scripts/selfcheck.sh')
if t is None:
    print('  [SKIP] 无 scripts/selfcheck.sh')
else:
    # 旧版（含预先过滤 .learnbuddy 的 bug）必须被替换，不能只判「段是否存在」
    _buggy = "grep -vE '^(scripts/_build/|\\.learnbuddy/|\\.gitignore$)'"
    A = '# ---------- 汇总 ----------'
    m = re.search(r'# ---------- 11\. 交付分支一致性.*?(?=# ---------- 汇总 ----------)', t, re.S)
    if m and _buggy not in t and S11.strip() == m.group(0).strip():
        print('  [SAME] [11] 段已在位且为修正后版本')
    elif m:
        write('scripts/selfcheck.sh', t[:m.start()] + S11 + t[m.end():])
        print('  [OK]   已替换 [11] 段（修正「预先过滤污染源」的 bug）')
    elif A in t:
        write('scripts/selfcheck.sh', t.replace(A, S11 + A, 1))
        print('  [OK]   已插入 [11] 段')
    else:
        print('  [MISS] 未找到汇总锚点')

# =============================================================== C) 构建侧文档
edit('scripts/_build/README.md', [
    ('## v2.11 链末结构层（`build_phase19.py`）',
     '## 提交护栏（v3.3.2 新增 · 事故驱动）\n'
     '\n'
     '`scripts/_build/hooks/pre-commit` 是一道**提交时拦截**的闸：暂存区出现「不随包」路径即拒绝提交。\n'
     '**为什么必须有它**：2026-10-03 一天内发生 **两次** `git add -f` 绕过 `.gitignore`、\n'
     '把 `.learnbuddy/memory/`（含本机路径）与 `.idea/` 强加进 **公开的 `release` 分支并推送** 的事故\n'
     '（第二次距第一次修好不到 15 分钟）。**只靠流程约束不可靠，必须设在提交动作上。**\n'
     '\n'
     '```bash\n'
     'bash scripts/_build/hooks/install.sh        # 安装到 .git/hooks/pre-commit（幂等）\n'
     '```\n'
     '\n'
     '配套：`scripts/selfcheck.sh` 的 `[11]` 段断言「`release` 树 == `main` 交付集」，\n'
     '于是任何一次 `checkall` 都能发现交付分支被污染。\n'
     '\n'
     '## v2.11 链末结构层（`build_phase19.py`）',
     '## 提交护栏（v3.3.2 新增'),
])

edit('scripts/_build/v3/README.md', [
    ('| 21 | `step62_source_expand.py` |',
     '| 22 | `step63_release_guard.py` | **交付分支护栏（事故驱动）**：git `pre-commit` 钩子（提交时拦截不随包路径，分支感知）'
     '+ `selfcheck [11]`（断言 release 树 == main 交付集）+ 安装脚本；修订号 → `3.3.2` | 新增层 |\n'
     '| 21 | `step62_source_expand.py` |',
     'step63_release_guard.py'),
])

# =============================================================== D) 版本 3.3.2
print('== D) 修订号 %s → %s ==' % (OLD_REV, NEW_REV))
n = 0
for d in sorted(os.listdir(os.path.join(ROOT, 'domains'))):
    loc = os.path.join(ROOT, 'domains', d, 'skills', 'local')
    if not os.path.isdir(loc):
        continue
    for s in sorted(os.listdir(loc)):
        rel = 'domains/%s/skills/local/%s/SKILL.md' % (d, s)
        x = read(rel)
        if x and 'version: %s' % OLD_REV in x:
            write(rel, x.replace('version: %s' % OLD_REV, 'version: %s' % NEW_REV))
            n += 1
print('  库内 SKILL.md 改写 %d 个（应为 92）' % n)
for rel, a, b in (
        ('SKILL.md', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('.codebuddy-plugin/plugin.json', '"version": "%s"' % OLD_REV, '"version": "%s"' % NEW_REV),
        ('config.yaml', 'version: %s' % OLD_REV, 'version: %s' % NEW_REV),
        ('library/output-spec.md', '**修订号 = `%s`**' % OLD_REV, '**修订号 = `%s`**' % NEW_REV),
        ('library/output-spec.md', '如 `3.3.0` → `%s`）' % OLD_REV, '如 `3.3.0` → `%s`）' % NEW_REV),
):
    k = replace_all(rel, a, b)
    print('  [%s]   %s ×%d' % ('OK' if k else '--', rel, k))

print('done')
