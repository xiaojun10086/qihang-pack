#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把启航技能包装配成 DSH（DeepSeek Harness）可发现的交付树。

只做增量：不改写 `skills/`、`agents/`、`commands/`、`config.yaml`、`plugin.json`
的任何原有文件；DSH 专属产物全部落在 `dsh/` 之下。原有目录几何保持不变，
所以包内既有的 `../using-qihang/SKILL.md`、`../../config.yaml`、
`../../references/*.md` 相对路径在交付树里仍然成立。

    python -B dsh/build_dsh_pack.py --check          # 校验当前工作树
    python -B dsh/build_dsh_pack.py --out dist/dsh   # 落盘一份可安装交付树

DSH 侧约束来自 deepseek-ai/deepseek-harness 源码与文档：

* 技能发现只在扫描根的**直属**子目录（`<name>/SKILL.md`）或直属平铺
  （`<name>.md`）进行，不支持递归 `**/SKILL.md`；
* frontmatter 首行必须恰为 `---`，闭合行亦然，YAML 必须解析为普通对象；
* `name` 必须匹配 `^[a-z0-9]+(?:-[a-z0-9]+)*$`，`description` 必填；
* 遗留驼峰键 `disableModelInvocation` / `modelInvocable` / `userInvocable`
  会被显式拒绝，导致整个技能被忽略；
* 模型侧目录只取 `name` + `description`，`catalogDescriptionMaxLength` 默认 500；
* 人设文本是 system prompt 模板，`{{...}}` 会在渲染时严格解析为提示词变量。

Python >= 3.11；仓库维护依赖见 requirements-dev.txt（不随交付下发）。
"""

import argparse
import os
from pathlib import Path
import posixpath
import re
import sys
import tomllib

try:
    import yaml
except ImportError as exc:  # pragma: no cover - 依赖缺失时的显式提示
    raise SystemExit(
        "缺少仓库维护依赖；请在隔离虚拟环境运行 python -m pip install -r requirements-dev.txt"
    ) from exc

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "dsh-qihang"
TARGET = "dsh-qihang-release"

#: 原样搬运的路径；目录以 `/` 结尾。dsh/ 下只有对外文档与配置样例进入交付。
CARRY = (
    "SKILL.md", "plugin.json", "config.yaml", "LICENSE", "THIRD_PARTY_NOTICES.md",
    "skills/", "references/", "agents/", "commands/", ".codebuddy-plugin/",
    "docs/skill-anatomy.md",
    "dsh/README.md", "dsh/config.example.yaml",
)

COMMAND_ROOT = "dsh/commands"
PERSONA_ROOT = "dsh/personas"
PRESET_FILE = "dsh/preset.example.yaml"

#: DSH 会把这些目录当作扫描根：每个直属子目录的 SKILL.md 注册为一个技能。
SCAN_ROOTS = ("skills", COMMAND_ROOT)

CATALOG_DESCRIPTION_MAX = 500
SKILL_NAME = re.compile(r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FRONTMATTER = re.compile(r"\A\ufeff?---[ \t]*\r?\n(.*?)^---[ \t]*(?:\r?\n|\Z)", re.M | re.S)
ALLOWED_KEYS = frozenset((
    "name", "description", "whenToUse", "metadata",
    "disable-model-invocation", "user-invocable",
))
REJECTED_KEYS = frozenset(("disableModelInvocation", "modelInvocable", "userInvocable"))
LINK = re.compile(r"\]\(([^)\s]+)\)")
CODE_PATH = re.compile(r"`([^`\s]+\.(?:md|ya?ml|json|toml|py|txt|sh))`", re.I)
PLACEHOLDER = re.compile(r"[<>*{}$]")
#: 匹配相对路径的起始 `../`，前一个字符不能是词字符、点或斜杠。
REL_START = re.compile(r"(?<![\w./])\.\./")

#: agents/*.md 共有的执行前置块（逐字匹配后整块改写为 DSH 语义）。
AGENT_PREAMBLE = "\n".join((
    "- 本文所有包内相对路径均以本文件所在目录为基准，不以用户当前工作目录（cwd）为基准。",
    "- 执行任何业务步骤前，先完整读取并遵守 `../skills/using-qihang/SKILL.md` 中的共享行为准则及安全兜底，再完整读取 `../config.yaml`。这里只加载共享规则和配置，不重复总入口路由；未完成读取不得执行。",
    "- 本会话已完整加载上述文件时可复用；必需文件不可读时，停止本包执行并说明缺失或不可读的文件，不猜测规则。",
    "- 每次调用业务 skill 前，完整读取对应的 `../skills/<name>/SKILL.md` 正文并遵守其执行前置，不得只凭名称或 description 执行；正文不可读时停止本包执行并说明缺失或不可读的文件。",
))
PERSONA_PREAMBLE = "\n".join((
    "- 本文是 DSH 人设文本（system prompt 段落），没有文件相对路径基准；读取包内技能一律通过 `skill` 工具按技能名加载，不要用文件系统路径。",
    "- 执行任何业务步骤前，先完整加载并遵守 `using-qihang` 技能（共享行为准则与安全兜底的唯一权威），再按该技能正文给出的方式完整读取包根 `config.yaml`。这里只加载共享规则和配置，不重复总入口路由；未完成读取不得执行。",
    "- 本会话已完整加载上述内容时可复用；必需内容不可读时，停止本包执行并说明缺失或不可读的技能，不猜测规则。",
    "- 每次调用业务技能前，完整加载该技能正文并遵守其执行前置，不得只凭名称或 description 执行；正文不可读时停止本包执行并说明缺失或不可读的技能。",
))
#: 兜底替换表：人格正文里其余位置的包内路径改写成 DSH 语义（技能名 / 资源名）。
PERSONA_REPLACEMENTS = (
    ("`../skills/using-qihang/SKILL.md`", "`using-qihang` 技能"),
    ("`../skills/<name>/SKILL.md`", "对应业务技能的正文"),
    ("`../skills/", "`skills/"),
    ("`../config.yaml`", "包根 `config.yaml`"),
    ("`../references/", "`references/"),
    ("`../agents/", "`agents/"),
    ("`../commands/", "`commands/"),
    ("`../.codebuddy-plugin/plugin.json`", "`.codebuddy-plugin/plugin.json`"),
    ("`../plugin.json`", "`plugin.json`"),
)


class Block(str):
    """让 PyYAML 用字面块（`|`）输出，避免长人设文本被折行。"""


class _Dumper(yaml.SafeDumper):
    pass


def _represent_block(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", str(data), style="|")


_Dumper.add_representer(Block, _represent_block)


def dump_yaml(value):
    return yaml.dump(
        value, Dumper=_Dumper, allow_unicode=True, sort_keys=False, width=10 ** 9,
    )


def wanted(path):
    return any(
        path == item or (item.endswith("/") and path.startswith(item))
        for item in CARRY
    )


def parse_frontmatter(text):
    """返回 frontmatter 映射；不符合 DSH 契约时抛 ValueError。"""
    match = FRONTMATTER.match(text)
    if not match:
        raise ValueError("frontmatter 缺失或首行不是独占的 ---")
    loaded = yaml.safe_load(match.group(1))
    if not isinstance(loaded, dict):
        raise ValueError("frontmatter 必须解析为普通对象")
    return loaded


def rebase(text, extra):
    """把包内 `../` 相对路径整体下移 extra 层。"""
    if extra <= 0:
        return text
    return REL_START.sub("../" * (extra + 1), text)


def skill_document(name, description, body, invocation=None):
    mapping = {"name": name, "description": description}
    mapping.update(invocation or {})
    return "---\n%s---\n\n%s" % (dump_yaml(mapping), body.strip() + "\n")


def command_skills(files):
    """把 commands/*.toml 转成 DSH 技能：仅用户可调用，不参与模型自动路由。"""
    generated = {}
    for path in sorted(files):
        if not path.startswith("commands/") or not path.endswith(".toml"):
            continue
        name = posixpath.basename(path)[: -len(".toml")]
        data = tomllib.loads(files[path].decode("utf-8"))
        description = data.get("description")
        prompt = data.get("prompt")
        if not isinstance(description, str) or not description.strip():
            raise SystemExit("commands/%s.toml 缺少可用的 description" % name)
        if not isinstance(prompt, str) or not prompt.strip():
            raise SystemExit("commands/%s.toml 缺少可用的 prompt" % name)
        if not SKILL_NAME.match(name):
            raise SystemExit("commands/%s.toml 的文件名不是合法 DSH 技能名" % name)
        generated["%s/%s/SKILL.md" % (COMMAND_ROOT, name)] = skill_document(
            name, description, rebase(prompt, 2),
            {"disable-model-invocation": True, "user-invocable": True},
        )
    return generated


def _heading(text, fallback):
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def persona_documents(files):
    """把 agents/*.md 转成 DSH 人设文本。返回 {name: (标题, 描述, 正文)}。"""
    personas = {}
    for path in sorted(files):
        if not path.startswith("agents/") or not path.endswith(".md"):
            continue
        text = files[path].decode("utf-8")
        try:
            meta = parse_frontmatter(text)
        except ValueError as exc:
            raise SystemExit("agents/%s 无法解析：%s" % (posixpath.basename(path), exc)) from exc
        name = meta.get("name")
        description = meta.get("description")
        if not isinstance(name, str) or not isinstance(description, str):
            raise SystemExit("agents/%s 缺少 name 或 description" % posixpath.basename(path))
        body = FRONTMATTER.sub("", text).strip()
        if AGENT_PREAMBLE not in body:
            raise SystemExit(
                "agents/%s 的执行前置块与预期不符，改写人设前请先核对" % posixpath.basename(path)
            )
        body = body.replace(AGENT_PREAMBLE, PERSONA_PREAMBLE)
        for old, new in PERSONA_REPLACEMENTS:
            body = body.replace(old, new)
        if "../" in body:
            raise SystemExit(
                "agents/%s 仍含未改写的包内相对路径，人设文本无法解析该基准" % posixpath.basename(path)
            )
        if "{{" in body:
            raise SystemExit(
                "agents/%s 含 {{...}}，DSH 会在渲染时按提示词变量严格解析" % posixpath.basename(path)
            )
        personas[name] = (_heading(body, name), description, body)
    return personas


def preset_composition(personas):
    """按 @deepseek-ai/dsh-agent-preset + @deepseek-ai/dsh-persona 的文档形态生成片段。"""
    if not personas:
        raise SystemExit("没有可用的 agents/*.md，无法生成 preset 片段")
    lines = [
        "# DSH agent preset 片段：把启航的人格挂成可切换的 preset。",
        "# 把下面的列表并入 DSH 的 Cordis 组合（composition）后重启。",
        "# 需要 agentPresets 服务；重复的 preset id 会导致声明加载失败。",
        "# 人设必须挂在 preset 组装内部：全局挂载会与提示词注册表的人设槽位相撞。",
        "",
    ]
    order = sorted(personas)
    composition = [{
        "id": "agent-preset-registry",
        "name": "@deepseek-ai/dsh-agent-preset-registry",
        "config": {"default": order[0]},
    }]
    for name in order:
        title, description, body = personas[name]
        composition.append({
            "id": "preset-" + name,
            "name": "@deepseek-ai/dsh-agent-preset",
            "config": {
                "id": name,
                "name": title,
                "description": description,
                "plugins": [{
                    "name": "@deepseek-ai/dsh-persona",
                    "config": {"prefix": Block(body + "\n")},
                }],
            },
        })
    return "\n".join(lines) + dump_yaml(composition)


def release_readme(tree):
    skills = [name for name in tree if name.startswith("skills/") and name.endswith("/SKILL.md")]
    commands = [
        name for name in tree
        if name.startswith(COMMAND_ROOT + "/") and name.endswith("/SKILL.md")
    ]
    personas = [name for name in tree if name.startswith(PERSONA_ROOT + "/")]
    return """# 启航 · DSH 交付树

本分支由 `%s` 分支的 `dsh/build_dsh_pack.py` 生成，请勿直接编辑。
它把「启航」技能包原样搬运过来，并叠加一层 DSH（DeepSeek Harness）适配产物。

## 内容

| 路径 | 说明 |
|---|---|
| `skills/` | %d 个业务技能，原样保留，DSH 直接发现 |
| `%s/` | %d 个命令技能，由 `commands/*.toml` 转换而来（仅用户可调用） |
| `%s/` | %d 个人设文本，由 `agents/*.md` 转换而来 |
| `%s` | agent preset + persona 挂载片段 |
| `dsh/config.example.yaml` | skill 发现配置片段 |
| `config.yaml` `references/` | 共享配置与站点资料，供上述技能按原有相对路径读取 |

## 安装

见 [`dsh/README.md`](dsh/README.md)。最短路径：

1. 把本目录放到任意固定位置（路径中避免空格）。
2. 把 `dsh/config.example.yaml` 里的两行改成该位置的绝对路径，并入 DSH 组合。
3. 重启 DSH，确认技能目录里出现 %d 个业务技能。

## 边界

* `SKILL.md`、`plugin.json`、`agents/`、`commands/` 是给宿主无关读取与其它宿主用的；
  DSH 不会自动发现它们，DSH 侧一律走 `skills/`、`%s/`、`%s/`。
* DSH 处于 developer preview，官方明示会有破坏性变更；升级 DSH 后请在源分支 `%s` 上
  重跑 `dsh/build_dsh_pack.py --check`，复核本树是否仍符合 DSH 契约（该脚本不随本分支交付）。
""" % (
        SOURCE, len(skills), COMMAND_ROOT, len(commands), PERSONA_ROOT, len(personas),
        PRESET_FILE, len(skills), COMMAND_ROOT, PERSONA_ROOT, SOURCE,
    )


def build(files):
    """files: {posix 相对路径: bytes} -> 交付树（同样是 {路径: bytes}）。"""
    tree = {path: data for path, data in files.items() if wanted(path)}
    for path, text in command_skills(files).items():
        tree[path] = text.encode("utf-8")
    personas = persona_documents(files)
    for name, (_title, description, body) in personas.items():
        tree["%s/%s.md" % (PERSONA_ROOT, name)] = skill_document(
            name, description, body
        ).encode("utf-8")
    tree[PRESET_FILE] = preset_composition(personas).encode("utf-8")
    tree["README.md"] = release_readme(tree).encode("utf-8")
    return tree


def iter_relative_references(text):
    for pattern in (LINK, CODE_PATH):
        for match in pattern.finditer(text):
            candidate = match.group(1)
            if candidate.startswith(("../", "./")) and not PLACEHOLDER.search(candidate):
                yield candidate


def validate(tree):
    """按 DSH 契约校验交付树；返回错误列表（空列表表示通过）。"""
    errors = []
    for root in SCAN_ROOTS:
        prefix = root + "/"
        entries = sorted({
            path[len(prefix):].split("/")[0]
            for path in tree
            if path.startswith(prefix) and path[len(prefix):]
        })
        if not entries:
            errors.append("扫描根 %s/ 下没有任何技能" % root)
        for name in entries:
            document = "%s/%s/SKILL.md" % (root, name)
            if document not in tree:
                errors.append("%s 不是 <name>/SKILL.md 形态，DSH 不会发现" % document)
                continue
            if not SKILL_NAME.match(name):
                errors.append("%s 的技能名不符合 DSH 的 kebab-case 契约" % document)
            errors.extend(_check_document(document, tree[document].decode("utf-8"), name, tree))
    for path in sorted(tree):
        if not path.endswith("/SKILL.md"):
            continue
        parent = posixpath.dirname(posixpath.dirname(path))
        if parent not in SCAN_ROOTS:
            errors.append("%s 不在任何 DSH 扫描根的直属子目录下，不会被发现" % path)
    errors.extend(_check_preset(tree))
    errors.extend(_check_personas(tree))
    return errors


def _check_document(path, text, expected_name, tree):
    errors = []
    try:
        meta = parse_frontmatter(text)
    except ValueError as exc:
        return ["%s：%s" % (path, exc)]
    unknown = set(meta) - ALLOWED_KEYS
    if unknown:
        errors.append("%s 含 DSH 不认识的 frontmatter 键：%s" % (path, "、".join(sorted(unknown))))
    rejected = set(meta) & REJECTED_KEYS
    if rejected:
        errors.append("%s 含 DSH 显式拒绝的遗留键，技能会被忽略：%s" % (path, "、".join(sorted(rejected))))
    name = meta.get("name")
    if not isinstance(name, str) or not SKILL_NAME.match(name):
        errors.append("%s 的 name 不符合 DSH 契约" % path)
    elif name != expected_name:
        errors.append("%s 的 name（%s）与目录名不一致" % (path, name))
    description = meta.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("%s 缺少非空 description" % path)
    elif len(description) > CATALOG_DESCRIPTION_MAX:
        errors.append("%s 的 description 超过 DSH 目录上限 %d 字符" % (path, CATALOG_DESCRIPTION_MAX))
    directory = posixpath.dirname(path)
    for reference in iter_relative_references(text):
        target = posixpath.normpath(posixpath.join(directory, reference))
        if target not in tree:
            errors.append("%s 引用了交付树中不存在的路径：%s" % (path, reference))
    return errors


def _check_preset(tree):
    text = tree.get(PRESET_FILE)
    if text is None:
        return ["缺少 %s" % PRESET_FILE]
    try:
        loaded = yaml.safe_load(text.decode("utf-8"))
    except yaml.YAMLError as exc:
        return ["%s 不是合法 YAML：%s" % (PRESET_FILE, exc)]
    if not isinstance(loaded, list):
        return ["%s 的顶层必须是插件行列表" % PRESET_FILE]
    errors = []
    persona_rows = []
    ids = {}

    def walk(rows):
        for row in rows:
            if not isinstance(row, dict):
                errors.append("%s 含非映射的插件行" % PRESET_FILE)
                continue
            if "name" not in row:
                errors.append("%s 含缺少 name 的插件行" % PRESET_FILE)
                continue
            if row["name"] == "@deepseek-ai/dsh-persona":
                persona_rows.append(row)
            if isinstance(row.get("id"), str):
                ids[row["id"]] = ids.get(row["id"], 0) + 1
            nested = (row.get("config") or {}).get("plugins")
            if nested is not None:
                if not isinstance(nested, list):
                    errors.append("%s 的 %s 行 plugins 必须是列表" % (PRESET_FILE, row["name"]))
                    continue
                walk(nested)

    walk(loaded)
    for value, count in sorted(ids.items()):
        if count > 1:
            errors.append(
                "%s 的插件行 id（%s）重复 %d 次，DSH 会拒绝加载该声明"
                % (PRESET_FILE, value, count)
            )
    for row in persona_rows:
        prefix = (row.get("config") or {}).get("prefix")
        if not isinstance(prefix, str) or not prefix.strip():
            errors.append("%s 的 persona 行缺少非空 prefix" % PRESET_FILE)
        elif "{{" in prefix:
            errors.append("%s 的 persona prefix 含 {{...}}，会被当作提示词变量解析" % PRESET_FILE)
    if not persona_rows:
        errors.append("%s 没有挂载任何 @deepseek-ai/dsh-persona 行" % PRESET_FILE)
    return errors


def _check_personas(tree):
    errors = []
    names = [path for path in tree if path.startswith(PERSONA_ROOT + "/")]
    if not names:
        errors.append("%s/ 下没有生成任何人设文本" % PERSONA_ROOT)
    for path in sorted(names):
        body = tree[path].decode("utf-8")
        try:
            meta = parse_frontmatter(body)
        except ValueError as exc:
            errors.append("%s：%s" % (path, exc))
            continue
        if not SKILL_NAME.match(str(meta.get("name", ""))):
            errors.append("%s 的 name 不符合 DSH 契约" % path)
        if "../" in FRONTMATTER.sub("", body):
            errors.append("%s 仍含包内相对路径" % path)
    return errors


def worktree_files():
    files = {}
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(
            name for name in dirs
            if name not in {".git", "__pycache__", "dist", "outputs", "tmp"}
        )
        for name in sorted(names):
            full = Path(base) / name
            rel = full.relative_to(ROOT).as_posix()
            if wanted(rel):
                files[rel] = full.read_bytes()
    return files


def write_tree(tree, target):
    target = Path(target)
    for path, data in sorted(tree.items()):
        destination = target / Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", help="把交付树落盘到该目录")
    parser.add_argument("--check", action="store_true", help="校验当前工作树（默认行为）")
    args = parser.parse_args(argv)

    tree = build(worktree_files())
    errors = validate(tree)
    skills = [path for path in tree if path.startswith("skills/") and path.endswith("/SKILL.md")]
    commands = [
        path for path in tree
        if path.startswith(COMMAND_ROOT + "/") and path.endswith("/SKILL.md")
    ]
    print("检查对象：当前工作树")
    print("交付树：%d 个文件（%d 个业务技能，%d 个命令技能）" % (len(tree), len(skills), len(commands)))
    for path in sorted(tree):
        print("  " + path)
    if errors:
        print("\n校验失败：")
        for error in errors:
            print("  [E] " + error)
        return 1
    print("\n校验通过：DSH 扫描根、frontmatter、命名、目录上限与相对引用均符合契约")
    if args.out:
        target = write_tree(tree, args.out)
        print("已落盘交付树：%s" % target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
