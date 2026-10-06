#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""离线校验启航技能包；仅显式 --push 才联网并构建、推送交付树。

Python >= 3.11；仓库维护依赖见 requirements-dev.txt（不随 release 交付）。

    python -B scripts/sync_release.py             # 当前工作树，含未忽略的新文件
    python -B scripts/sync_release.py --ref HEAD  # 指定提交；仍然离线只读
    python -B scripts/sync_release.py --push      # 已提交 main，缺失时回退 HEAD

白名单是交付范围的唯一真相源。检查模式不 fetch、不建树、不创建临时索引，
不要求 origin 或 release 存在；发布模式绝不包含未提交修改。
"""

import argparse
import fnmatch
import json
import os
from pathlib import Path
import posixpath
import re
import subprocess
import sys
import tempfile
import tomllib
from urllib.parse import unquote, urlsplit

try:
    import yaml
    from markdown_it import MarkdownIt
except ImportError as exc:
    raise SystemExit(
        "缺少仓库维护依赖；请在隔离虚拟环境运行 python -m pip install -r requirements-dev.txt"
    ) from exc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = "main"
TARGET = "release"
WHITELIST = (
    "SKILL.md", "plugin.json", "config.yaml", "LICENSE", "THIRD_PARTY_NOTICES.md",
    "skills/", "references/", "agents/", "commands/", ".codebuddy-plugin/",
    "docs/skill-anatomy.md",
)
BOT_NAME = "github-actions[bot]"
BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
REPO_ONLY_REFS = (
    "scripts/sync_release.py", ".github/workflows/sync-release.yml",
    "requirements-dev.txt", "scripts/browser-bridge/", "scripts/jxgl/",
)
VERSION_FILES = (
    ("plugin.json", "json"), (".codebuddy-plugin/plugin.json", "json"),
    ("config.yaml", "yaml"),
)
REF_EXT = "md|py|ya?ml|json|sh|toml|html|txt"
CODE_REF = re.compile(r"^[^\s`]+\.(?:%s)(?:[?#][^\s`]*)?$" % REF_EXT, re.I)
FRONTMATTER = re.compile(r"\A\ufeff?---[ \t]*\r?\n(.*?)^---[ \t]*(?:\r?\n|\Z)", re.M | re.S)
SKILL_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SEMVER = re.compile(
    r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
)
MARKDOWN = MarkdownIt("commonmark")


class UniqueKeyLoader(yaml.SafeLoader):
    """使用安全 YAML 解析，并拒绝静默覆盖的重复键。"""

    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                repeated = key in result
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    None, None, "YAML 键必须可哈希", key_node.start_mark
                ) from exc
            if repeated:
                raise yaml.constructor.ConstructorError(
                    None, None, "重复的 YAML 键：%s" % key, key_node.start_mark
                )
            result[key] = self.construct_object(value_node, deep=deep)
        return result


def load_yaml(text):
    return yaml.load(text, Loader=UniqueKeyLoader)


def git_env():
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env["GIT_OPTIONAL_LOCKS"] = "0"
    for key, default in (
        ("GIT_AUTHOR_NAME", BOT_NAME), ("GIT_AUTHOR_EMAIL", BOT_EMAIL),
        ("GIT_COMMITTER_NAME", BOT_NAME), ("GIT_COMMITTER_EMAIL", BOT_EMAIL),
    ):
        env[key] = env.get(key) or default
    return env


def run_git(*args, env=None, stdin=None):
    return subprocess.run(
        ["git"] + list(args), cwd=ROOT, env=env or git_env(), input=stdin,
        capture_output=True,
    )


def git_error(args, result):
    message = result.stderr.decode("utf-8", "replace").strip()
    raise SystemExit("git %s 失败（退出码 %s）：%s" % (
        " ".join(args), result.returncode, message or "无错误详情",
    ))


def git(*args, env=None, stdin=None):
    result = run_git(*args, env=env, stdin=stdin)
    if result.returncode:
        git_error(args, result)
    return result.stdout.decode("utf-8", "strict")


def probe_commit(ref, env=None):
    """返回不可变提交 SHA；仅预期的不存在（退出码 1）返回 None。"""
    args = ("rev-parse", "--verify", "--quiet", "--end-of-options", ref + "^{commit}")
    result = run_git(*args, env=env)
    if result.returncode == 1:
        return None
    if result.returncode:
        git_error(args, result)
    return result.stdout.decode("ascii").strip()


def resolve_source(env=None, ref=None):
    # 默认源只接受 main 分支，不把同名 tag 错当成 main；显式 ref 则精确尊重用户。
    candidates = (ref,) if ref is not None else ("refs/heads/" + SOURCE, "HEAD")
    for candidate in candidates:
        commit = probe_commit(candidate, env)
        if commit:
            return commit
    raise SystemExit("找不到源提交：%s" % " / ".join(candidates))


def wanted(path):
    return any(path == item or (item.endswith("/") and path.startswith(item))
               for item in WHITELIST)


def repo_only(path):
    return any(path == item or (item.endswith("/") and path.startswith(item))
               for item in REPO_ONLY_REFS)


def read_version(kind, text):
    try:
        data = json.loads(text) if kind == "json" else load_yaml(text)
    except (ValueError, yaml.YAMLError):
        return None
    value = data.get("version") if isinstance(data, dict) else None
    if not isinstance(value, str):
        return None
    match = SEMVER.fullmatch(value)
    if not match:
        return None
    prerelease = match.group(1)
    if prerelease and any(part.isdigit() and len(part) > 1 and part.startswith("0")
                          for part in prerelease.split(".")):
        return None
    return value


def source_entries(env, ref):
    entries = []
    for item in git("ls-tree", "-r", "-z", ref, env=env).split("\0"):
        if not item:
            continue
        meta, _, path = item.partition("\t")
        mode, kind, sha = meta.split()
        if wanted(path) and (kind != "blob" or mode not in ("100644", "100755")):
            raise SystemExit("交付文件不支持符号链接或子模块：%s" % path)
        entries.append((mode, sha, path))
    return entries


def worktree_snapshot():
    """读取当前磁盘快照；不更新 index，不跟随白名单文件的符号链接。"""
    root = Path(ROOT).resolve()
    listed = git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    contents = {}
    for path in sorted(set(listed.split("\0"))):
        if not path or not wanted(path):
            continue
        filename = root / path
        # 不仅拒绝文件自身，也拒绝通过上级目录链接读取包外文件。
        if any(parent.is_symlink() for parent in (filename, *filename.parents)
               if parent != root and root in parent.parents):
            raise SystemExit("交付文件不支持符号链接：%s" % path)
        if not filename.resolve().is_relative_to(root):
            raise SystemExit("交付路径超出包根：%s" % path)
        if not filename.exists():
            continue  # 工作树中删除的受管文件不再属于本次交付快照。
        if not filename.is_file():
            raise SystemExit("交付路径不是普通文件：%s" % path)
        contents[path] = filename.read_bytes()
    return [(path, path) for path in contents], lambda key: contents[key].decode("utf-8-sig")


def blob(sha):
    return git("cat-file", "blob", sha)


def iter_references(text):
    """提取真实 Markdown 链接、图片、引用式定义以及行内文件路径；忽略代码块。"""
    env = {}
    tokens = MARKDOWN.parse(text, env)
    for token in tokens:
        for child in token.children or ():
            if child.type == "link_open":
                yield child.attrGet("href"), True
            elif child.type == "image":
                yield child.attrGet("src"), True
            elif child.type == "code_inline" and CODE_REF.fullmatch(child.content):
                yield child.content, False
    # 包括暂未使用的定义，避免声明的本地来源悄悄悬空。
    for definition in env.get("references", {}).values():
        yield definition["href"], True


def reference_candidates(path, target, relative):
    if not target or "<" in target or ">" in target:
        return set()  # 模板占位符不是实际文件。
    try:
        parsed = urlsplit(target)
    except ValueError:
        return set()  # 畸形输入（IPv6 括号、NFKC 归一化等）不是本地文件引用。
    if parsed.scheme or parsed.netloc or not parsed.path:
        return set()
    target = unquote(parsed.path).replace("\\", "/")
    if target.startswith("/"):
        return {posixpath.normpath(target.lstrip("/"))}
    local = posixpath.normpath(posixpath.join(posixpath.dirname(path), target))
    # 链接和行内路径均严格按所在文件解析，不回退到包根掩盖错误。
    return {local}


def exists_in_pack(candidate, paths):
    if candidate == ".." or candidate.startswith("../"):
        return False
    if "*" in candidate:
        return any(fnmatch.fnmatchcase(path, candidate) for path in paths)
    return (candidate in paths or candidate == "." or
            any(path.startswith(candidate.rstrip("/") + "/") for path in paths))


def check_frontmatter(path, text, expected_name):
    errors = []
    match = FRONTMATTER.match(text)
    if not match:
        return ["%s 缺少文件开头的 YAML frontmatter" % path]
    try:
        data = load_yaml(match.group(1))
    except yaml.YAMLError as exc:
        return ["%s frontmatter YAML 非法：%s" % (path, str(exc).splitlines()[0])]
    if not isinstance(data, dict):
        return ["%s frontmatter 必须是映射" % path]
    extras = set(data) - {"name", "description"}
    if extras:
        errors.append("%s frontmatter 存在不允许的字段：%s" %
                      (path, ", ".join(sorted(map(str, extras)))))
    name = data.get("name")
    if not isinstance(name, str) or not SKILL_NAME.fullmatch(name):
        errors.append("%s name 必须是小写连字符字符串" % path)
    elif name != expected_name:
        errors.append("%s 的 name=%s 与预期名称 %s 不一致" % (path, name, expected_name))
    description = data.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("%s description 必须是非空字符串" % path)
    elif len(description) > 1024:
        errors.append("%s description 超过 1024 字符" % path)
    return errors


def check_entry_dependencies(contents):
    """静态检查依赖声明，不能替代宿主实际加载与权限验收。"""
    errors = []
    for path, text in contents.items():
        if path == "SKILL.md":
            required = ("skills/using-qihang/SKILL.md", "config.yaml")
        elif path == "skills/using-qihang/SKILL.md":
            required = ("../../config.yaml",)
        elif path.startswith("skills/") and path.endswith("/SKILL.md"):
            required = ("../using-qihang/SKILL.md", "../../config.yaml")
        elif path.startswith("agents/") and path.endswith(".md"):
            required = ("../skills/using-qihang/SKILL.md", "../config.yaml")
        elif path.startswith("commands/") and path.endswith(".toml"):
            required = ("../skills/using-qihang/SKILL.md", "../config.yaml")
        else:
            continue
        if path == "skills/portal-operator/SKILL.md":
            required += (
                "../../references/dlut-login-sites.md", "../../references/dlut-field-map.md",
            )
        for target in required:
            if "`" + target + "`" not in text:
                errors.append("%s 缺少必需的前置加载依赖声明：%s" % (path, target))
    return errors


def verify(kept, read_blob=None):
    """校验内容快照，不修改 Git、文件或环境。"""
    read_blob = read_blob or blob
    errors, repo_refs = [], []
    by_path = {path: key for key, path in kept}
    paths = set(by_path)
    for item in WHITELIST:
        if not any(path == item or (item.endswith("/") and path.startswith(item))
                   for path in paths):
            errors.append("白名单条目未匹配到文件：%s" % item)
    contents = {}
    for path, key in by_path.items():
        if not path.endswith((".md", ".json", ".yaml", ".yml", ".toml")):
            continue
        try:
            contents[path] = read_blob(key)
        except (OSError, UnicodeError) as exc:
            errors.append("无法读取 UTF-8 文件 %s：%s" % (path, exc))
    for path, text in contents.items():
        markdown = text if path.endswith(".md") else None
        if path.startswith("commands/") and path.endswith(".toml"):
            try:
                command = tomllib.loads(text)
                if not all(isinstance(command.get(key), str) and command[key].strip()
                           for key in ("description", "prompt")):
                    errors.append("%s 缺少非空 description/prompt" % path)
                else:
                    markdown = command["prompt"]
            except tomllib.TOMLDecodeError as exc:
                errors.append("%s TOML 非法：%s" % (path, exc))
        if markdown is None:
            continue
        for target, relative in iter_references(markdown):
            candidates = reference_candidates(path, target, relative)
            if not candidates or any(exists_in_pack(candidate, paths) for candidate in candidates):
                continue
            registered = sorted(candidate for candidate in candidates if repo_only(candidate))
            if registered:
                repo_refs.append("%s → %s" % (path, registered[0]))
            else:
                errors.append("%s 引用不存在的文件：%s" % (path, target))
    skill_paths = sorted(path for path in paths
                         if path.startswith("skills/") and path.endswith("/SKILL.md"))
    names = []
    if not skill_paths:
        errors.append("交付树里没有 skills/<name>/SKILL.md")
    for path in skill_paths:
        if path.count("/") != 2:
            errors.append("技能必须采用扁平 skills/<name>/SKILL.md 结构：%s" % path)
            continue
        name = path.split("/")[1]
        names.append(name)
        if path in contents:
            errors.extend(check_frontmatter(path, contents[path], name))
    if "SKILL.md" in contents:
        errors.extend(check_frontmatter("SKILL.md", contents["SKILL.md"], "qihang"))
    for path, text in contents.items():
        if path.startswith("agents/") and path.endswith(".md"):
            errors.extend(check_frontmatter(path, text, posixpath.basename(path)[:-3]))
    versions = {}
    for path, kind in VERSION_FILES:
        version = read_version(kind, contents.get(path, ""))
        if version is None:
            errors.append("版本一致性：%s 缺少合法的 SemVer 字符串或文档不可解析" % path)
        else:
            versions[path] = version
    if len(set(versions.values())) > 1:
        errors.append("版本一致性：交付文件版本号不一致 —— " +
                      "、".join("%s=%s" % pair for pair in sorted(versions.items())))
    errors.extend(check_entry_dependencies(contents))
    return sorted(set(errors)), sorted(names), sorted(set(repo_refs))


def build_tree(entries):
    """仅发布路径调用；临时索引在成功和失败时均自动清理。"""
    if not entries:
        raise SystemExit("白名单没有匹配到任何文件")
    with tempfile.TemporaryDirectory(prefix="qihang-release-") as directory:
        env = dict(git_env())  # 复制后写入索引变量，不改动调用方环境。
        env["GIT_INDEX_FILE"] = os.path.join(directory, "index")
        git("read-tree", "--empty", env=env)
        payload = b"".join(("%s %s\t%s\0" % entry).encode("utf-8") for entry in entries)
        git("update-index", "-z", "--index-info", env=env, stdin=payload)
        return git("write-tree", env=env).strip()


def fetch_release_parent(env=None):
    """仅发布时探测真实远端；不存在与网络/权限错误分开处理。"""
    remote_ref = "refs/heads/" + TARGET
    args = ("ls-remote", "--exit-code", "--heads", "origin", remote_ref)
    result = run_git(*args, env=env)
    if result.returncode == 2:
        return None  # 明确没有该分支，忽略可能残留的 origin/release。
    if result.returncode:
        git_error(args, result)
    # 不写远端跟踪引用；FETCH_HEAD 只在显式发布路径更新。
    git("fetch", "--quiet", "--no-tags", "origin", remote_ref, env=env)
    parent = probe_commit("FETCH_HEAD", env)
    if parent is None:
        raise SystemExit("已抓取 release，但 FETCH_HEAD 不可解析，停止发布")
    return parent


def publish(entries, source, skill_count):
    env = git_env()
    parent = fetch_release_parent(env)
    tree = build_tree(entries)
    if parent and git("rev-parse", parent + "^{tree}", env=env).strip() == tree:
        print("release 已与所选源提交对齐，无需新提交")
        return 0
    message = ("chore(release): 同步交付分支（%s）\n\n"
               "交付 %d 个文件，%d 个 skill。\n" %
               (source[:12], len(entries), skill_count)).encode("utf-8")
    args = ["commit-tree", tree]
    if parent:
        args += ["-p", parent]
    commit = git(*args, env=env, stdin=message).strip()
    # 首次发布也使用空期望值 lease，避免探测后他人创建分支被覆盖。
    git("push", "--quiet", "--force-with-lease=refs/heads/%s:%s" % (TARGET, parent or ""),
        "origin", "%s:refs/heads/%s" % (commit, TARGET), env=env)
    print("已推送 release：%s" % commit[:12])
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--push", action="store_true", help="校验已提交版本后联网发布")
    parser.add_argument("--ref", help="检查/发布指定已提交版本；默认检查当前工作树")
    args = parser.parse_args(argv)
    if args.push or args.ref is not None:
        source = resolve_source(git_env(), args.ref)
        entries = [entry for entry in source_entries(git_env(), source) if wanted(entry[2])]
        kept = [(sha, path) for _mode, sha, path in entries]
        reader = blob
        label = "已提交版本 %s（不含工作树修改）" % source[:12]
    else:
        kept, reader = worktree_snapshot()
        source, entries = None, None
        label = "当前工作树（含未忽略的新文件及未提交修改）"
    errors, skills, repo_refs = verify(kept, reader)
    print("检查对象：%s" % label)
    print("交付清单：%d 个文件（%d 个 skill）" % (len(kept), len(skills)))
    for _key, path in sorted(kept, key=lambda item: item[1]):
        print("  " + path)
    for reference in repo_refs:
        print("  [i] 已登记的仓库专用引用：" + reference)
    if errors:
        print("\n校验失败：")
        for error in errors:
            print("  [E] " + error)
        return 1
    print("\n校验通过：白名单、引用、元数据、版本及前置加载依赖声明均符合规则")
    if not args.push:
        print("离线只读检查结束；未联网、未构建交付树、未创建临时索引")
        return 0
    return publish(entries, source, len(skills))


if __name__ == "__main__":
    sys.exit(main())
