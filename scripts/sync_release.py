#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 main 的内容按白名单同步到 release 交付分支。

release 是给使用者直接 clone 的交付分支，只保留 skill 运行所需内容、
结构规范与法务声明；仓库自身的说明文档与开发文件不进 release。

白名单是唯一真相源：以后新增的开发文件默认不会进 release，只有显式
加进 WHITELIST 才会被交付。

校验项：白名单覆盖完整、引用不悬空（指向仓库维护文件的引用须登记于
REPO_ONLY_REFS）、skill 名与目录一致、交付文件版本号一致。

用法：
    python scripts/sync_release.py            # 只校验并打印交付清单
    python scripts/sync_release.py --push     # 重建 release 并推送
"""

import argparse
import fnmatch
import json
import os
import posixpath
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = "main"
TARGET = "release"

# 白名单：以 "/" 结尾表示整个目录，其余为精确路径。
WHITELIST = (
    "SKILL.md",
    "plugin.json",
    "config.yaml",
    "LICENSE",
    "THIRD_PARTY_NOTICES.md",
    "skills/",
    "references/",
    "agents/",
    "commands/",
    ".codebuddy-plugin/",
    "docs/skill-anatomy.md",
)

# 自动化同步提交统一署名为机器人，避免把维护者本机身份带进交付历史。
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"

# 引用检查覆盖的扩展名：只收代码 / 配置 / 文档类，避免把域名（*.edu.cn）误判成文件路径。
REF_EXT = "md|py|ya?ml|json|sh|toml|html|txt"
REF = re.compile(r"`([A-Za-z0-9_./*<>-]+\.(?:%s))`"
                 r"|\[[^\]]*\]\(([^)#\s]+\.(?:%s))\)" % (REF_EXT, REF_EXT))
FM_NAME = re.compile(r"^---\s*$(.*?)^---\s*$", re.M | re.S)

# 有意引用、但不随包交付的仓库维护文件：交付树内的引用必须精确命中这些路径才算
# 已登记。任何新出现的、指向未交付文件的引用都会直接报错，必须在此登记才放行。
# 以 "/" 结尾表示整个目录，但默认逐条列举，避免整目录豁免把新引用一并放过。
REPO_ONLY_REFS = (
    "scripts/sync_release.py",
    ".github/workflows/sync-release.yml",
)

# 版本必须一致的交付文件：(路径, 解析方式)。多源副本靠断言保持一致，避免手工同步漂移。
VERSION_FILES = (
    ("plugin.json", "json"),
    (".codebuddy-plugin/plugin.json", "json"),
    ("config.yaml", "yaml"),
)


def resolve_source(env):
    """优先用 main 分支；工作流里若只有 detached HEAD 则退回 HEAD。"""
    for ref in (SOURCE, "HEAD"):
        if git("rev-parse", "--verify", "--quiet", "%s^{commit}" % ref, env=env).strip():
            return ref
    raise SystemExit("找不到源提交：%s / HEAD" % SOURCE)


def git_env():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["GIT_AUTHOR_NAME"] = env.get("GIT_AUTHOR_NAME") or BOT_NAME
    env["GIT_AUTHOR_EMAIL"] = env.get("GIT_AUTHOR_EMAIL") or BOT_EMAIL
    env["GIT_COMMITTER_NAME"] = env.get("GIT_COMMITTER_NAME") or BOT_NAME
    env["GIT_COMMITTER_EMAIL"] = env.get("GIT_COMMITTER_EMAIL") or BOT_EMAIL
    return env


def git(*args, **kw):
    env = kw.pop("env", None) or git_env()
    stdin = kw.pop("stdin", None)
    check = kw.pop("check", True)
    p = subprocess.run(["git"] + list(args), cwd=ROOT, env=env, input=stdin,
                       capture_output=True)
    if check and p.returncode:
        raise SystemExit("git %s 失败：%s" % (" ".join(args),
                                              p.stderr.decode("utf-8", "replace").strip()))
    return p.stdout.decode("utf-8", "replace")


def wanted(path):
    return any(path == w or (w.endswith("/") and path.startswith(w)) for w in WHITELIST)


def repo_only(path):
    """是否属于「有意引用但不交付」的仓库维护路径。"""
    return any(path == r or (r.endswith("/") and path.startswith(r)) for r in REPO_ONLY_REFS)


def read_version(kind, text):
    """从交付文件里取出声明的版本号；取不到或格式非法返回 None。"""
    if kind == "json":
        try:
            data = json.loads(text)
        except ValueError:
            return None
        return data.get("version") if isinstance(data, dict) else None
    m = re.search(r"^version:\s*(\S+)\s*$", text, re.M)
    return m.group(1) if m else None


def source_entries(env, ref):
    out = git("ls-tree", "-r", "-z", ref, env=env)
    entries = []
    for item in out.split("\0"):
        if not item:
            continue
        meta, _, path = item.partition("\t")
        mode, _type, sha = meta.split()
        entries.append((mode, sha, path))
    return entries


def build_tree(ref):
    """按白名单构建交付树，返回 (tree_sha, [(sha, path), ...])。"""
    env = git_env()
    idx = os.path.join(tempfile.mkdtemp(prefix="qihang-release-"), "index")
    env["GIT_INDEX_FILE"] = idx
    git("read-tree", "--empty", env=env)
    kept = [e for e in source_entries(env, ref) if wanted(e[2])]
    if not kept:
        raise SystemExit("白名单没有匹配到任何文件，检查 WHITELIST 与源分支名")
    payload = "".join("%s %s\t%s\n" % (mode, sha, path) for mode, sha, path in kept)
    git("update-index", "--index-info", env=env, stdin=payload.encode("utf-8"))
    tree = git("write-tree", env=env).strip()
    return tree, [(sha, path) for _mode, sha, path in kept]


def blob(sha):
    return git("cat-file", "blob", sha)


def verify(kept):
    """校验交付树自洽：白名单覆盖、引用不悬空、skill 名与目录一致、版本号一致。"""
    errs = []
    repo_refs = []
    paths = {p for _s, p in kept}
    fileset = list(paths)
    by_path = {p: s for s, p in kept}

    for w in WHITELIST:
        if not any(p == w or (w.endswith("/") and p.startswith(w)) for p in paths):
            errs.append("白名单条目未匹配到文件：%s（可能被重命名）" % w)

    for sha, path in kept:
        if not path.endswith(".md"):
            continue
        text = blob(sha)
        base = posixpath.dirname(path)
        for m in REF.finditer(text):
            target = m.group(1) or m.group(2)
            if target.startswith("http") or "<" in target or ">" in target:
                continue
            cands = {posixpath.normpath(posixpath.join(base, target)),
                     posixpath.normpath(target)}
            for cand in cands:
                if "*" in cand:
                    if any(fnmatch.fnmatch(f, cand) for f in fileset):
                        break
                elif cand in paths:
                    break
            else:
                # 指向仓库维护文件（有意不交付）→ 登记后放行，避免静默误判为悬空。
                hit = sorted(c for c in cands if repo_only(c))
                if hit:
                    repo_refs.append("%s → %s" % (path, hit[0]))
                else:
                    errs.append("%s 引用不存在的文件：%s" % (path, target))

    skill_names = sorted(p.split("/")[1] for p in paths
                         if p.startswith("skills/") and p.endswith("/SKILL.md"))
    if not skill_names:
        errs.append("交付树里没有 skills/<name>/SKILL.md")
    for name in skill_names:
        text = blob(by_path["skills/%s/SKILL.md" % name])
        fm = FM_NAME.search(text)
        if not fm:
            errs.append("skills/%s/SKILL.md 缺 frontmatter" % name)
            continue
        got = re.search(r"^name:\s*(\S+)\s*$", fm.group(1), re.M)
        if not got:
            errs.append("skills/%s/SKILL.md frontmatter 缺 name" % name)
        elif got.group(1) != name:
            errs.append("skills/%s/SKILL.md 的 name=%s 与目录名不一致" % (name, got.group(1)))

    versions = {}
    for vpath, kind in VERSION_FILES:
        if vpath not in by_path:
            errs.append("版本一致性：%s 不在交付树中" % vpath)
            continue
        v = read_version(kind, blob(by_path[vpath]))
        if v is None:
            errs.append("版本一致性：%s 里没有可解析的 version 字段" % vpath)
        else:
            versions[vpath] = v
    if len(set(versions.values())) > 1:
        errs.append("版本一致性：交付文件版本号不一致 —— "
                    + "、".join("%s=%s" % (p, v) for p, v in sorted(versions.items())))

    return errs, skill_names, repo_refs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="重建 release 并推送")
    args = ap.parse_args()

    env = git_env()
    ref = resolve_source(env)
    git("fetch", "--quiet", "origin",
        "+refs/heads/%s:refs/remotes/origin/%s" % (TARGET, TARGET), env=env, check=False)

    tree, kept = build_tree(ref)
    errs, skills, repo_refs = verify(kept)
    src = git("rev-parse", "--short", ref, env=env).strip()

    print("源分支 %s @ %s" % (ref, src))
    print("交付树 %s：%d 个文件（%d 个 skill）" % (tree, len(kept), len(skills)))
    for _sha, path in sorted(kept, key=lambda x: x[1]):
        print("  " + path)

    if repo_refs:
        print("\n有意引用仓库维护文件（不交付，已登记，不计为悬空）：")
        for r in sorted(set(repo_refs)):
            print("  [i] " + r)

    if errs:
        print("\n交付树校验失败：")
        for e in errs:
            print("  [E] " + e)
        return 1
    print("\n交付树校验通过：白名单覆盖完整、无未登记悬空引用、skill 名与目录一致、版本号一致")

    parent = git("rev-parse", "--verify", "--quiet",
                 "refs/remotes/origin/%s^{commit}" % TARGET, env=env).strip()
    if parent and git("rev-parse", "%s^{tree}" % parent, env=env).strip() == tree:
        print("release 已与当前 main 对齐，无需新提交")
        return 0
    if not args.push:
        print("（未加 --push，仅检查）")
        return 0

    msg = ("chore(release): 由 main 同步交付分支（%s）\n\n"
           "交付 %d 个文件：%d 个 skill + references/agents/commands + 结构规范与法务声明\n\n"
           "Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>\n"
           % (src, len(kept), len(skills))).encode("utf-8")
    cmd = ["commit-tree", tree]
    if parent:
        cmd += ["-p", parent]
    commit = git(*cmd, env=env, stdin=msg).strip()

    if parent:
        git("push", "--quiet", "--force-with-lease=refs/heads/%s:%s" % (TARGET, parent),
            "origin", "%s:refs/heads/%s" % (commit, TARGET), env=env)
    else:
        git("push", "--quiet", "origin", "%s:refs/heads/%s" % (commit, TARGET), env=env)
    print("已推送 release：%s" % commit[:7])
    return 0


if __name__ == "__main__":
    sys.exit(main())
