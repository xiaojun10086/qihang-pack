#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 DSH 适配层装配成交付树，推送到 dsh-qihang-release 分支。

仓库维护脚本，不随任何交付分支发布。Python >= 3.11；依赖见 requirements-dev.txt。

    python -B dsh/sync_dsh_release.py             # 校验当前工作树，离线只读
    python -B dsh/sync_dsh_release.py --ref HEAD  # 校验指定已提交版本
    python -B dsh/sync_dsh_release.py --push      # 从 main 装配并联网推送

装配规则与校验契约的唯一真相源是 dsh/build_dsh_pack.py；本脚本只负责取源、建树、推送。
推送模式绝不包含未提交修改，且只接受 main 分支或显式 --ref。
"""

import argparse
import importlib.util
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


release = _load("sync_release", ROOT / "scripts" / "sync_release.py")
pack = _load("build_dsh_pack", ROOT / "dsh" / "build_dsh_pack.py")

REMOTE_REF = "refs/heads/" + pack.TARGET


def resolve_source(env, ref=None):
    """默认只接受 main 分支，不把同名 tag 错当成源分支。"""
    candidates = (ref,) if ref is not None else ("refs/heads/" + pack.SOURCE, "HEAD")
    for candidate in candidates:
        commit = release.probe_commit(candidate, env)
        if commit:
            return commit
    raise SystemExit("找不到源提交：%s" % " / ".join(candidates))


def source_files(env, ref):
    """读取已提交版本中属于 DSH 交付范围的普通文件。"""
    files = {}
    for item in release.git("ls-tree", "-r", "-z", ref, env=env).split("\0"):
        if not item:
            continue
        meta, _, path = item.partition("\t")
        mode, kind, sha = meta.split()
        if not pack.wanted(path):
            continue
        if kind != "blob" or mode not in ("100644", "100755"):
            raise SystemExit("DSH 交付不支持符号链接或子模块：%s" % path)
        files[path] = release.run_git("cat-file", "blob", sha, env=env).stdout
    return files


def build_tree(entries):
    """仅发布路径调用；临时索引在成功和失败时均自动清理。"""
    if not entries:
        raise SystemExit("交付树为空")
    with tempfile.TemporaryDirectory(prefix="qihang-dsh-") as directory:
        env = dict(release.git_env())
        env["GIT_INDEX_FILE"] = os.path.join(directory, "index")
        release.git("read-tree", "--empty", env=env)
        payload = b"".join(("%s %s\t%s\0" % entry).encode("utf-8") for entry in entries)
        release.git("update-index", "-z", "--index-info", env=env, stdin=payload)
        return release.git("write-tree", env=env).strip()


def hash_entries(tree, env):
    """把 {路径: bytes} 写成 git 对象，返回 build_tree 需要的索引条目。"""
    entries = []
    for path, data in sorted(tree.items()):
        sha = release.git("hash-object", "-w", "-t", "blob", "--stdin",
                          env=env, stdin=data).strip()
        entries.append(("100644", sha, path))
    return entries


def fetch_target_parent(env):
    """探测远端交付分支；不存在与网络/权限错误分开处理。"""
    args = ("ls-remote", "--exit-code", "--heads", "origin", REMOTE_REF)
    result = release.run_git(*args, env=env)
    if result.returncode == 2:
        return None
    if result.returncode:
        release.git_error(args, result)
    release.git("fetch", "--quiet", "--no-tags", "origin", REMOTE_REF, env=env)
    parent = release.probe_commit("FETCH_HEAD", env)
    if parent is None:
        raise SystemExit("已抓取 %s，但 FETCH_HEAD 不可解析，停止发布" % pack.TARGET)
    return parent


def publish(tree, source, skill_count):
    env = release.git_env()
    parent = fetch_target_parent(env)
    root = build_tree(hash_entries(tree, env))
    if parent and release.git("rev-parse", parent + "^{tree}", env=env).strip() == root:
        print("%s 已与所选源提交对齐，无需新提交" % pack.TARGET)
        return 0
    message = ("chore(dsh): 同步 DSH 适配交付分支（%s）\n\n"
               "交付 %d 个文件，%d 个 DSH 技能。\n" %
               (source[:12], len(tree), skill_count)).encode("utf-8")
    args = ["commit-tree", root]
    if parent:
        args += ["-p", parent]
    commit = release.git(*args, env=env, stdin=message).strip()
    # 首次发布也使用空期望值 lease，避免探测后他人创建分支被覆盖。
    release.git("push", "--quiet",
                "--force-with-lease=%s:%s" % (REMOTE_REF, parent or ""),
                "origin", "%s:%s" % (commit, REMOTE_REF), env=env)
    print("已推送 %s：%s" % (pack.TARGET, commit[:12]))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--push", action="store_true", help="校验已提交版本后联网发布")
    parser.add_argument("--ref", help="检查/发布指定已提交版本；默认检查当前工作树")
    args = parser.parse_args(argv)

    if args.push or args.ref is not None:
        source = resolve_source(release.git_env(), args.ref)
        files = source_files(release.git_env(), source)
        label = "已提交版本 %s（不含工作树修改）" % source[:12]
    else:
        source = None
        files = pack.worktree_files()
        label = "当前工作树（含未提交修改）"

    tree = pack.build(files)
    errors = pack.validate(tree)
    skills = [p for p in tree
              if p.startswith(pack.COMMAND_ROOT + "/") and p.endswith("/SKILL.md")]
    catalog = [p for p in tree if p.startswith("skills/") and p.endswith("/SKILL.md")]

    print("检查对象：%s" % label)
    print("交付清单：%d 个文件（%d 个业务技能 + %d 个命令技能）"
          % (len(tree), len(catalog), len(skills)))
    for path in sorted(tree):
        print("  " + path)
    if errors:
        print("\n校验失败：")
        for error in errors:
            print("  [E] " + error)
        return 1
    print("\n校验通过：DSH 扫描根、frontmatter、目录上限、相对引用与 preset 组合均符合契约")
    if not args.push:
        print("离线只读检查结束；未联网、未构建交付树、未创建临时索引")
        return 0
    return publish(tree, source, len(catalog) + len(skills))


if __name__ == "__main__":
    sys.exit(main())
