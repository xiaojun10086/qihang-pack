"""DSH 适配层回归。只读当前工作树，不写盘、不碰 git。"""

import importlib.util
from pathlib import Path
import posixpath
import unittest

import yaml

PROJECT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "build_dsh_pack", PROJECT / "dsh" / "build_dsh_pack.py"
)
pack = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pack)


def load_yaml(path, data):
    return yaml.safe_load(data.decode("utf-8"))


class BuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = pack.worktree_files()
        cls.tree = pack.build(cls.files)

    def text(self, path):
        return self.tree[path].decode("utf-8")

    def errors(self, changes=None, missing=()):
        tree = dict(self.tree)
        tree.update(changes or {})
        for path in missing:
            tree.pop(path, None)
        return pack.validate(tree)

    def test_current_tree_is_valid(self):
        self.assertEqual([], pack.validate(self.tree))

    def test_deterministic(self):
        self.assertEqual(self.tree, pack.build(self.files))

    def test_scan_roots_and_counts(self):
        skills = [p for p in self.tree
                  if p.startswith("skills/") and p.endswith("/SKILL.md")]
        commands = [p for p in self.tree
                    if p.startswith(pack.COMMAND_ROOT + "/") and p.endswith("/SKILL.md")]
        self.assertEqual(25, len(skills))
        self.assertEqual(7, len(commands))
        self.assertEqual({"skills", pack.COMMAND_ROOT}, set(pack.SCAN_ROOTS))

    def test_original_geometry_is_preserved(self):
        for path in ("SKILL.md", "plugin.json", "config.yaml", "LICENSE",
                     "THIRD_PARTY_NOTICES.md"):
            self.assertIn(path, self.tree)
        for path in ("skills/", "references/", "agents/", "commands/",
                     ".codebuddy-plugin/"):
            self.assertTrue(any(p.startswith(path) for p in self.tree), path)

    def test_carried_files_are_byte_identical(self):
        for path, data in self.files.items():
            if path.startswith("dsh/"):
                continue
            if path in ("README.md",):
                continue
            self.assertEqual(data, self.tree[path], path)

    def test_package_relative_paths_resolve(self):
        """包内 ../ 引用必须逐条在交付树里落地，否则 DSH 侧读不到共享资产。"""
        for path in ("skills/using-qihang/SKILL.md", "skills/portal-operator/SKILL.md"):
            directory = posixpath.dirname(path)
            for reference in pack.iter_relative_references(self.text(path)):
                target = posixpath.normpath(posixpath.join(directory, reference))
                self.assertIn(target, self.tree, "%s -> %s" % (path, reference))

    def test_no_original_file_was_modified(self):
        for path, data in self.files.items():
            if path.startswith(("skills/", "agents/", "commands/")):
                self.assertEqual(data, self.tree[path], path)


class CommandSkillTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = pack.build(pack.worktree_files())

    def test_every_command_becomes_a_skill(self):
        names = sorted(
            p.split("/")[2] for p in self.tree
            if p.startswith(pack.COMMAND_ROOT + "/") and p.endswith("/SKILL.md")
        )
        self.assertEqual(
            ["campus", "code", "exam", "learn", "notes", "paper", "search"], names
        )

    def test_invocation_flags_keep_user_only_semantics(self):
        for path in sorted(self.tree):
            if not path.startswith(pack.COMMAND_ROOT + "/"):
                continue
            meta = pack.parse_frontmatter(self.tree[path].decode("utf-8"))
            with self.subTest(path=path):
                self.assertIs(True, meta["disable-model-invocation"])
                self.assertIs(True, meta["user-invocable"])
                self.assertTrue(meta["description"].strip())

    def test_relative_paths_are_rebased_two_levels(self):
        for path in sorted(self.tree):
            if not path.startswith(pack.COMMAND_ROOT + "/"):
                continue
            body = self.tree[path].decode("utf-8")
            with self.subTest(path=path):
                self.assertIn("`../../../skills/using-qihang/SKILL.md`", body)
                self.assertIn("`../../../config.yaml`", body)
                self.assertNotIn("`../skills/", body)

    def test_missing_description_is_rejected(self):
        files = dict(pack.worktree_files())
        files["commands/campus.toml"] = b'prompt = "x"\n'
        with self.assertRaises(SystemExit):
            pack.build(files)

    def test_invalid_command_name_is_rejected(self):
        files = dict(pack.worktree_files())
        files["commands/Bad_Name.toml"] = files.pop("commands/campus.toml")
        with self.assertRaises(SystemExit):
            pack.build(files)


class PersonaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = pack.worktree_files()
        cls.tree = pack.build(cls.files)

    def test_every_agent_becomes_a_persona(self):
        names = sorted(p.rsplit("/", 1)[1][: -len(".md")] for p in self.tree
                       if p.startswith(pack.PERSONA_ROOT + "/"))
        self.assertEqual(["campus-concierge", "research-librarian", "study-coach"], names)

    def test_personas_carry_no_relative_paths(self):
        for path in sorted(self.tree):
            if not path.startswith(pack.PERSONA_ROOT + "/"):
                continue
            body = pack.FRONTMATTER.sub("", self.tree[path].decode("utf-8"))
            with self.subTest(path=path):
                self.assertNotIn("../", body)

    def test_personas_avoid_template_braces(self):
        for path in sorted(self.tree):
            if not path.startswith(pack.PERSONA_ROOT + "/"):
                continue
            with self.subTest(path=path):
                self.assertNotIn("{{", self.tree[path].decode("utf-8"))

    def test_persona_preamble_is_rewritten(self):
        body = self.tree[pack.PERSONA_ROOT + "/study-coach.md"].decode("utf-8")
        self.assertIn("DSH 人设文本", body)
        self.assertIn("`using-qihang` 技能", body)
        self.assertNotIn(pack.AGENT_PREAMBLE.splitlines()[1], body)

    def test_drifted_preamble_is_rejected(self):
        files = dict(self.files)
        files["agents/study-coach.md"] = files["agents/study-coach.md"].replace(
            b"- \xe6\x9c\xac\xe6\x96\x87\xe6\x89\x80\xe6\x9c\x89", b"- \xe6\x94\xb9\xe8\xbf\x87"
        )
        with self.assertRaises(SystemExit):
            pack.build(files)

    def test_remaining_relative_path_is_rejected(self):
        files = dict(self.files)
        files["agents/study-coach.md"] += b"\nsee `../nope.md`\n"
        with self.assertRaises(SystemExit):
            pack.build(files)


class PresetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = pack.build(pack.worktree_files())
        cls.loaded = yaml.safe_load(cls.tree[pack.PRESET_FILE].decode("utf-8"))

    def rows(self, loaded=None):
        found = []

        def walk(rows):
            for row in rows:
                found.append(row)
                nested = (row.get("config") or {}).get("plugins")
                if isinstance(nested, list):
                    walk(nested)

        walk(loaded if loaded is not None else self.loaded)
        return found

    def test_top_level_is_a_plugin_row_list(self):
        self.assertIsInstance(self.loaded, list)
        self.assertEqual("agent-preset-registry", self.loaded[0]["id"])
        self.assertEqual(
            "@deepseek-ai/dsh-agent-preset-registry", self.loaded[0]["name"]
        )

    def test_one_preset_per_persona(self):
        presets = [r for r in self.loaded if r.get("name") == "@deepseek-ai/dsh-agent-preset"]
        self.assertEqual(3, len(presets))
        self.assertEqual(
            ["campus-concierge", "research-librarian", "study-coach"],
            sorted(r["config"]["id"] for r in presets),
        )
        self.assertEqual(4, len({r["id"] for r in self.loaded}))

    def test_default_points_at_a_registered_preset(self):
        default = self.loaded[0]["config"]["default"]
        ids = [r["config"]["id"] for r in self.loaded if "config" in r and "id" in r["config"]]
        self.assertIn(default, ids)

    def test_persona_rows_have_non_empty_prefixes(self):
        personas = [r for r in self.rows() if r.get("name") == "@deepseek-ai/dsh-persona"]
        self.assertEqual(3, len(personas))
        for row in personas:
            prefix = row["config"]["prefix"]
            with self.subTest(prefix=prefix[:20]):
                self.assertTrue(prefix.strip())
                self.assertNotIn("{{", prefix)

    def test_prefix_is_a_literal_block(self):
        text = self.tree[pack.PRESET_FILE].decode("utf-8")
        self.assertIn("prefix: |", text)

    def test_preset_id_collision_is_rejected(self):
        text = self.tree[pack.PRESET_FILE].decode("utf-8")
        loaded = yaml.safe_load(text)
        loaded[1]["id"] = loaded[0]["id"]
        errors = pack.validate({**self.tree,
                                pack.PRESET_FILE: yaml.dump(loaded).encode("utf-8")})
        self.assertTrue(any("重复" in e for e in errors))

    def test_template_braces_in_prefix_are_rejected(self):
        loaded = yaml.safe_load(self.tree[pack.PRESET_FILE].decode("utf-8"))
        for row in self.rows(loaded):
            if row.get("name") == "@deepseek-ai/dsh-persona":
                row["config"]["prefix"] += "\n{{unknown}}\n"
                break
        errors = pack.validate({**self.tree,
                                pack.PRESET_FILE: yaml.dump(loaded).encode("utf-8")})
        self.assertTrue(any("{{...}}" in e for e in errors))

    def test_empty_prefix_is_rejected(self):
        loaded = yaml.safe_load(self.tree[pack.PRESET_FILE].decode("utf-8"))
        for row in self.rows(loaded):
            if row.get("name") == "@deepseek-ai/dsh-persona":
                row["config"]["prefix"] = "   "
                break
        errors = pack.validate({**self.tree,
                                pack.PRESET_FILE: yaml.dump(loaded).encode("utf-8")})
        self.assertTrue(any("非空 prefix" in e for e in errors))

    def test_missing_preset_is_reported(self):
        self.assertTrue(any("preset" in e for e in
                            pack.validate({k: v for k, v in self.tree.items()
                                           if k != pack.PRESET_FILE})))


class ContractTests(unittest.TestCase):
    def test_skill_name_contract(self):
        for value in ("using-qihang", "a", "a1-b2"):
            self.assertTrue(pack.SKILL_NAME.match(value), value)
        for value in ("Using-Qihang", "using_qihang", "-a", "a-", "a--b", "a b", ""):
            self.assertFalse(pack.SKILL_NAME.match(value), value)

    def test_parse_frontmatter_contract(self):
        self.assertEqual({"name": "a"}, pack.parse_frontmatter("---\nname: a\n---\nbody"))
        for text in ("name: a\n---\n", "---\nname: a\n", "---\n- a\n---\n",
                     "---\n---\n", "---\nnull\n---\n"):
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    pack.parse_frontmatter(text)

    def test_rebase_shifts_every_relative_path(self):
        text = "读 `../skills/x/SKILL.md` 与 `../config.yaml`；保留 a/b 与 ./x"
        self.assertEqual(
            "读 `../../../skills/x/SKILL.md` 与 `../../../config.yaml`；保留 a/b 与 ./x",
            pack.rebase(text, 2),
        )
        self.assertEqual(text, pack.rebase(text, 0))
        self.assertEqual(text, pack.rebase(text, -1))

    def test_iter_relative_references_skips_placeholders_and_absolute(self):
        text = "见 `../a.md`、[x](../b.md)、`<name>/SKILL.md`、`/abs/c.md`、`../d/`"
        self.assertEqual(["../b.md", "../a.md"], list(pack.iter_relative_references(text)))

    def test_carry_covers_exactly_the_package_assets(self):
        for path in ("SKILL.md", "config.yaml", "skills/x/SKILL.md", "references/a.md",
                     "agents/a.md", "commands/a.toml", "docs/skill-anatomy.md",
                     "dsh/README.md", "dsh/config.example.yaml"):
            self.assertTrue(pack.wanted(path), path)
        for path in ("scripts/sync_release.py", "tests/test_sync_release.py",
                     "dsh/build_dsh_pack.py", "dsh/tests/test_dsh_pack.py",
                     ".github/workflows/sync-release.yml", "docs/index.html",
                     "dsh/preset.example.yaml", "dsh/commands/campus/SKILL.md"):
            self.assertFalse(pack.wanted(path), path)

    def test_branch_names(self):
        self.assertEqual("main", pack.SOURCE)
        self.assertEqual("dsh-qihang-release", pack.TARGET)


class RejectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tree = pack.build(pack.worktree_files())

    def errors(self, changes=None, missing=()):
        tree = dict(self.tree)
        tree.update(changes or {})
        for path in missing:
            tree.pop(path, None)
        return pack.validate(tree)

    def test_nested_skill_is_reported(self):
        errors = self.errors({"skills/a/b/SKILL.md": b"---\nname: b\ndescription: d\n---\n"})
        self.assertTrue(any("扫描根的直属子目录" in e for e in errors))

    def test_flat_skill_markdown_is_reported(self):
        errors = self.errors({"skills/flat.md": b"---\nname: flat\ndescription: d\n---\n"})
        self.assertTrue(any("不是 <name>/SKILL.md 形态" in e for e in errors))

    def test_non_kebab_name_is_reported(self):
        errors = self.errors({"skills/Bad_Name/SKILL.md":
                              b"---\nname: Bad_Name\ndescription: d\n---\n"})
        self.assertTrue(any("kebab-case" in e for e in errors))

    def test_name_must_match_directory(self):
        errors = self.errors({"skills/mismatch/SKILL.md":
                              b"---\nname: other\ndescription: d\n---\n"})
        self.assertTrue(any("与目录名不一致" in e for e in errors))

    def test_legacy_keys_are_reported(self):
        errors = self.errors({"skills/legacy/SKILL.md":
                              b"---\nname: legacy\ndescription: d\ndisableModelInvocation: true\n---\n"})
        self.assertTrue(any("显式拒绝" in e for e in errors))

    def test_unknown_keys_are_reported(self):
        errors = self.errors({"skills/unknown/SKILL.md":
                              b"---\nname: unknown\ndescription: d\nlicense: MIT\n---\n"})
        self.assertTrue(any("不认识的 frontmatter 键" in e for e in errors))

    def test_when_to_use_is_accepted(self):
        errors = self.errors({"skills/ok/SKILL.md":
                              b"---\nname: ok\ndescription: d\nwhenToUse: e\n---\n"})
        self.assertEqual([], errors)

    def test_description_length_is_enforced(self):
        payload = ("---\nname: long\ndescription: %s\n---\n" % ("x" * 501)).encode()
        errors = self.errors({"skills/long/SKILL.md": payload})
        self.assertTrue(any("目录上限" in e for e in errors))
        payload = ("---\nname: long\ndescription: %s\n---\n" % ("x" * 500)).encode()
        self.assertEqual([], self.errors({"skills/long/SKILL.md": payload}))

    def test_empty_description_is_reported(self):
        errors = self.errors({"skills/empty/SKILL.md":
                              b'---\nname: empty\ndescription: "  "\n---\n'})
        self.assertTrue(any("缺少非空 description" in e for e in errors))

    def test_broken_reference_is_reported(self):
        original = self.tree["skills/using-qihang/SKILL.md"]
        errors = self.errors({"skills/using-qihang/SKILL.md":
                              original.replace(b"../../config.yaml", b"../../gone.yaml")})
        self.assertTrue(any("不存在的路径" in e for e in errors))

    def test_empty_scan_root_is_reported(self):
        tree = {k: v for k, v in self.tree.items()
                if not k.startswith(pack.COMMAND_ROOT + "/")}
        errors = pack.validate(tree)
        self.assertTrue(any("没有任何技能" in e for e in errors))

    def test_missing_personas_are_reported(self):
        tree = {k: v for k, v in self.tree.items()
                if not k.startswith(pack.PERSONA_ROOT + "/")}
        errors = pack.validate(tree)
        self.assertTrue(any("没有生成任何人设文本" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
