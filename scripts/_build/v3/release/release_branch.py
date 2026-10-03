# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------------
# 【v3.2 生成链 · 发布侧 · 单仓库双分支】main → release 分支刷新
#
# 背景：v3.2.5 起，原先的「源仓库目录 + 交付副本目录」两棵树，改为**一个仓库两条分支**：
#   main     = 开发树（含生成器 scripts/_build、记忆 .learnbuddy、过程文档）
#   release  = **纯净交付树**（只含交付物，分发给用户）
#
# 为什么用「临时索引构造树」而不是 checkout / merge：
#   · `git merge main` 不行 —— main 上 `.learnbuddy` 每轮都在改，而 release 上不存在该路径，
#     会反复触发 modify/delete 冲突；且 main 新增的 _build 文件会被并进 release（破坏纯净性）。
#   · `git checkout release` 会**删掉工作树里的 _build/.learnbuddy**（tracked），
#     与本项目「记忆长期留在磁盘」的使用习惯冲突。
#   · 本脚本**从不触碰工作树与真实索引**：用 GIT_INDEX_FILE 指向临时索引，
#     read-tree(main) → rm --cached(排除项) → write-tree → commit-tree → update-ref。
#     因此可随时重跑、零副作用、零数据丢失风险。
#
# 纯净性由 **git 跟踪状态**保证（比手工维护 NOISE_DIRS/排除表更可靠）：
#   · scripts/_build/** （生成器链，不随包）
#   · .learnbuddy/**    （项目记忆，不随包）
#   · references/ 下 8 份过程文档 —— **未被 git 跟踪**（见 .gitignore），天然不进分支
#   · __pycache__ / .idea / .vscode / *.pyc —— 同样未被跟踪
#
# 用法：
#   python scripts/_build/v3/release/release_branch.py            # 只比对，不改任何东西（默认）
#   python scripts/_build/v3/release/release_branch.py --apply    # 刷新 release 分支
#   python scripts/_build/v3/release/release_branch.py --apply --msg "..."   # 自定义提交信息
# 判定口径：**release 分支的树 == main 的树 − 排除项**；报「差异项 = 0」即已同步。
# -------------------------------------------------------------------------------
import os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = 'main'
DST = 'release'
# 排除项：**只允许写「为什么它不随包分发」能说清的东西**
EXCL = [
    'scripts/_build',    # 生成器链：构建期工具，交付物不需要
    '.learnbuddy',       # 项目记忆：含本机路径与过程信息，绝不外发
    # 2026-10-03（R-2 修复）：仅排除 `.gitignore` —— 它会把 8 份内部过程文档的**文件名**
    #   （review-report / stress-test / acceptance / 需求确认书 …）带给用户，暴露内部评审流程。
    #   移出后 `selfcheck.sh [8b]` 会走它的 **else 分支**（「发布副本：无 .gitignore」→ OK），
    #   无需改动任何断言；`_EXDEV` 在交付树里本应为空（交付树不含过程文档）→ 语义更准。
    # ⚠️ **`.gitattributes` 必须留在交付树里**（实测教训）：它锁 `*.sh/*.py/*.md = eol=lf`，
    #   本机 `core.autocrlf=true` 时 `git archive` / fresh clone 会按它决定行尾；
    #   把它移出后交付树**立刻有 160 个文件变 CRLF**（aligncheck `WARN 含 CRLF 行尾` ×160），
    #   而 `*.sh` 带 `\r` 在 bash 下直接 `$'\r': command not found` → 交付包功能损坏。
    #   → 结论：**信息面风险（低）不值得换功能风险（高）**，`.gitattributes` 保留分发。
    '.gitignore',
]

APPLY = '--apply' in sys.argv
MSG = None
if '--msg' in sys.argv:
    MSG = sys.argv[sys.argv.index('--msg') + 1]
VDIR = None
if '--verify-dir' in sys.argv:
    VDIR = sys.argv[sys.argv.index('--verify-dir') + 1]
ALLOW_DELETE = '--allow-delete' in sys.argv
# 交付文件数下界（当前 173）。低于它几乎必然意味着 **main 树被误删过**，而不是「本版真的删了东西」。
MIN_FILES = 150


def norm(b):
    return b.replace(b'\r\n', b'\n')


def verify_dir(d):
    """把 release 分支的树与某个磁盘目录**逐字节**比对（迁移一次性证明 / 事后审计）。"""
    d = os.path.abspath(d)
    ref = DST if ref_exists(DST) else SRC
    tree_files = sorted(x for x in git('ls-tree', '-r', '--name-only', ref).splitlines() if x)
    disk = set()
    for dp, dns, fns in os.walk(d):
        dns[:] = [x for x in dns if x not in ('.git', '__pycache__', '.idea') + tuple(
            os.path.basename(e) for e in EXCL)]
        for f in fns:
            disk.add(os.path.relpath(os.path.join(dp, f), d).replace(os.sep, '/'))
    only_branch = sorted(set(tree_files) - disk)
    only_disk = sorted(disk - set(tree_files))
    diff = []
    for p in sorted(set(tree_files) & disk):
        blob = subprocess.run(['git', 'cat-file', 'blob', '%s:%s' % (ref, p)],
                              cwd=ROOT, stdout=subprocess.PIPE,
                              stderr=subprocess.DEVNULL).stdout
        try:
            with open(os.path.join(d, p), 'rb') as fh:
                cur = fh.read()
        except OSError:
            diff.append(p); continue
        if norm(blob) != norm(cur):
            diff.append(p)
    print('分支 %s：%d 文件 ｜ 目录 %s：%d 文件' % (ref, len(tree_files), d, len(disk)))
    print('仅分支有 %d ｜ 仅目录有 %d ｜ 内容不一致 %d' % (len(only_branch), len(only_disk), len(diff)))
    for p in (only_branch + only_disk + diff)[:20]:
        print('   ! %s' % p)
    ok = not (only_branch or only_disk or diff)
    print('判定：%s' % ('✅ 分支产物与目录逐字节一致' if ok else '❌ 存在差异'))
    return 0 if ok else 1


def git(*args, check=True, env=None, text=True):
    p = subprocess.run(['git'] + list(args), cwd=ROOT, stdout=subprocess.PIPE,
                       stderr=subprocess.STDOUT, env=env)
    out = p.stdout.decode('utf-8', 'replace')
    if check and p.returncode != 0:
        print('!! git %s 失败 rc=%d\n%s' % (' '.join(args), p.returncode, out))
        sys.exit(p.returncode)
    return out.strip()


def ref_exists(ref):
    return subprocess.run(['git', 'rev-parse', '--verify', '--quiet', ref],
                          cwd=ROOT, stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def main():
    if VDIR:
        return verify_dir(VDIR)
    if not ref_exists(SRC):
        print('!! 找不到分支 %s' % SRC); return 1
    src_tree = git('rev-parse', '%s^{tree}' % SRC)

    idx = os.path.join(tempfile.mkdtemp(prefix='qihang-branch-'), 'index')
    env = dict(os.environ)
    env['GIT_INDEX_FILE'] = idx
    git('read-tree', src_tree, env=env)
    have = [p for p in EXCL if git('ls-tree', '-r', '--name-only', src_tree, '--', p, env=env)]
    if have:
        git('rm', '-r', '--cached', '-q', '--ignore-unmatch', *have, env=env)
    dst_tree = git('write-tree', env=env)

    n_src = len(git('ls-tree', '-r', '--name-only', src_tree, env=env).splitlines())
    n_dst = len(git('ls-tree', '-r', '--name-only', dst_tree, env=env).splitlines())
    print('源分支 %s：%d 文件' % (SRC, n_src))
    print('排除项 %s → 交付 %d 文件' % (' + '.join(EXCL), n_dst))

    if ref_exists(DST):
        old_tree = git('rev-parse', '%s^{tree}' % DST)
        if old_tree == dst_tree:
            print('release 分支已是最新（树一致，差异项 = 0）')
            return 0
        raw = git('diff-tree', '-r', '--name-status', old_tree, dst_tree)
        rows = [l.split('\t') for l in raw.splitlines() if l.strip()]
        add = [r for r in rows if r[0].startswith('A')]
        mod = [r for r in rows if r[0].startswith('M')]
        dele = [r for r in rows if r[0].startswith('D')]
        print('差异：新增 %d ｜ 修改 %d ｜ 删除 %d' % (len(add), len(mod), len(dele)))
        for r in (add + mod + dele)[:40]:
            print('   %-3s %s' % (r[0][:1], r[-1]))
    else:
        print('release 分支尚不存在 —— 本次将创建（首次发布）')

    if not APPLY:
        print('（只比对模式；确认无误后加 --apply 执行）')
        _guard(n_dst, locals().get('dele', []), applying=False)
        return 0

    if _guard(n_dst, locals().get('dele', []), applying=True):
        return 2

    base = git('rev-parse', DST) if ref_exists(DST) else git('rev-parse', SRC)
    msg = MSG or ('chore(release): 由 %s 刷新交付分支（%s）' % (SRC, git('rev-parse', '--short', base)))
    commit = git('commit-tree', dst_tree, '-p', base, '-m', msg, env=env)
    git('update-ref', 'refs/heads/%s' % DST, commit)
    print('已更新分支 %s → %s' % (DST, commit[:12]))
    print('提交信息：%s' % msg)
    print('提示：工作树未受影响。分发用 `git archive release | tar -x` 或 `git clone -b release <url>`；')
    print('      推送用 `git push origin %s %s`。' % (SRC, DST))
    return 0


def _guard(n_dst, dele, applying):
    """**防误删闸**（2026-10-03 实测事故换来）。

    事故：worktree 里少了 10 个 `scripts/*`（例如刚 `git checkout release` 过、或写入被打断），
    随后一条 `git commit -a`（= `git add -u`）**把这些「缺失」当成删除提交进 main**（3179 行删除），
    而本脚本会**忠实照搬** → 交付包静默少了 10 个核心脚本。
    工具没错（garbage in, garbage out），但**「照搬误删」必须在 --apply 前挡住**。
    返回 True = 应当中止。
    """
    stop = False
    if n_dst < MIN_FILES:
        print('  ‼️ 交付文件数 %d < 下界 %d —— main 树疑似被误删，已中止。' % (n_dst, MIN_FILES))
        stop = True
    if dele:
        print('  ‼️ 本次刷新包含 %d 个「删除」：%s' % (len(dele), [r[-1] for r in dele][:8]))
        print('     交付物删除必须是**有意的**。若这些文件是「worktree 里缺失后被 git commit -a 提交掉的」，')
        print('     请在 main 上先修回：`git checkout HEAD~1 -- <路径>` 或 `git restore --source=<好提交> -- <路径>`。')
        print('     确认确要删除时：加 `--allow-delete` 重跑。')
        stop = True
    if stop and ALLOW_DELETE:
        print('  → 已按**显式授权**放行（--allow-delete）。请自行确认这份交付包是完整的。')
        return False
    if stop and applying:
        print('  → 未做任何修改（--apply 已被闸门拦下）。')
    elif stop:
        print('  → 以上仅为提示（当前是只比对模式，未改动任何东西）。')
    return stop


if __name__ == '__main__':
    sys.exit(main())
