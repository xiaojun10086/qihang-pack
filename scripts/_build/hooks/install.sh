#!/bin/sh
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
