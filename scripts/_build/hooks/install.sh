#!/bin/sh
# 安装「启航」仓库护栏到 .git/hooks/（幂等）。
# 用法：bash scripts/_build/hooks/install.sh [仓库根]
set -eu
ROOT="${1:-$(cd "$(dirname "$0")/../../.." && pwd)}"
[ -d "$ROOT/.git" ] || { echo "跳过：$ROOT 不是 git 仓库"; exit 0; }
for _h in pre-commit post-checkout; do
  [ -f "$ROOT/scripts/_build/hooks/$_h" ] || continue
  cp "$ROOT/scripts/_build/hooks/$_h" "$ROOT/.git/hooks/$_h"
  chmod +x "$ROOT/.git/hooks/$_h"
  echo "已安装：$ROOT/.git/hooks/$_h"
done
echo "自测：在 release 分支上 git add -f .learnbuddy/memory/MEMORY.md && git commit 应被拒绝。"
