"""发布校验回归。所有写入和推送测试只针对 tmp/ 下新建的本地仓库。"""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tomllib
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sync_release", PROJECT / "scripts/sync_release.py")
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


def delivery_contents():
    paths, reader = release.worktree_snapshot()
    return {path: reader(key) for key, path in paths}


class ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = delivery_contents()

    def verify(self, changes=None, missing=()):
        contents = dict(self.base)
        contents.update(changes or {})
        for path in missing:
            contents.pop(path, None)
        return release.verify([(p, p) for p in contents], contents.__getitem__)[0]

    def test_current_delivery(self):
        self.assertEqual([], self.verify())
        self.assertEqual(25, sum(p.startswith("skills/") and p.endswith("/SKILL.md")
                                 for p in self.base))

    def test_version_copies(self):
        self.assertEqual({"4.1.0"}, {release.read_version(k, self.base[p])
                                    for p, k in release.VERSION_FILES})

    def test_version_mismatch(self):
        value = json.loads(self.base["plugin.json"])
        value["version"] = "0.0.0"
        self.assertTrue(any("版本号不一致" in e for e in
                            self.verify({"plugin.json": json.dumps(value)})))

    def test_invalid_versions_are_rejected_without_crashing(self):
        for value in (None, [], {}, True, 4, "", "v4.0.2", "04.0.2", "4.0.2-01", "4.0.2-"):
            with self.subTest(value=value):
                self.assertIsNone(release.read_version("json", json.dumps({"version": value})))

    def test_valid_quoted_yaml_semver(self):
        for value in ("4.0.2", "4.0.2-rc.1", "4.0.2+build.02"):
            with self.subTest(value=value):
                self.assertEqual(value, release.read_version("yaml", "version: " + json.dumps(value)))

    def test_invalid_version_yaml(self):
        for text in ("version: [", "version: 4.0.2\nversion: 4.0.2", "- 4.0.2"):
            with self.subTest(text=text):
                self.assertIsNone(release.read_version("yaml", text))

    def test_all_broken_markdown_forms(self):
        links = (
            "[x](missing.md)", "[x](missing.md#section)",
            '[x](missing.md "title")', "[x][missing]\n\n[missing]: missing.md",
            "[missing][]\n\n[missing]: missing.md", "[missing]\n\n[missing]: missing.md",
            "[x](missing.md?raw=1#heading)", "[x](<missing file.md>)",
            "[x](missing%20file.md)", "![preview](missing.png)",
            "`missing.py`", "`missing.md#heading`",
        )
        path = "docs/skill-anatomy.md"
        for link in links:
            with self.subTest(link=link):
                errors = self.verify({path: self.base[path] + "\n\n" + link})
                self.assertTrue(any("引用不存在的文件" in e for e in errors), errors)

    def test_code_fences_and_indented_examples_are_not_links(self):
        path = "docs/skill-anatomy.md"
        text = self.base[path] + "\n\n```md\n[x](fake.md)\n`fake.py`\n```\n\n    [x](fake.md)\n"
        self.assertEqual([], self.verify({path: text}))

    def test_malformed_targets_do_not_crash(self):
        # urlsplit 对 IPv6 括号和会触发 NFKC 归一化的字符会抛 ValueError。
        path = "docs/skill-anatomy.md"
        for target in ("`//[x.md`", "`//a\uff20b/c.md`", "`//[::1]x.md`", "`//%zz.md`"):
            with self.subTest(target=target):
                self.assertEqual([], self.verify({path: self.base[path] + "\n\n" + target}))

    def test_external_links_and_anchor_only_are_not_local(self):
        path = "docs/skill-anatomy.md"
        text = self.base[path] + "\n\n[x](https://example.com/file.md#part) [x](#local)\n"
        self.assertEqual([], self.verify({path: text}))

    def test_real_relative_links(self):
        path = "docs/skill-anatomy.md"
        text = self.base[path] + '\n\n[x](../SKILL.md#section "title") [x](../skills/)\n'
        self.assertEqual([], self.verify({path: text}))

    def test_wrong_relative_path_cannot_fall_back_to_root(self):
        path = "docs/skill-anatomy.md"
        for link in ("[x](config.yaml)", "`config.yaml`"):
            with self.subTest(link=link):
                self.assertTrue(any("引用不存在的文件" in e for e in
                                    self.verify({path: self.base[path] + "\n\n" + link})))

    def test_registered_repository_reference(self):
        path = "docs/skill-anatomy.md"
        self.assertEqual([], self.verify({path: self.base[path] +
                                          "\n\n[x](../scripts/sync_release.py#main)\n"}))
        self.assertTrue(any("引用不存在的文件" in e for e in self.verify({
            path: self.base[path] + "\n\n[x](../scripts/not-delivered.py)\n"})))

    def test_frontmatter_negative_matrix(self):
        path = "skills/assignment-plan/SKILL.md"
        variants = (
            "name: assignment-plan", "name: assignment-plan\ndescription: [",
            "name: assignment-plan\ndescription: test\nallowed-tools: Bash",
            "name: assignment-plan\ndescription: " + "x" * 1025,
            "name: wrong-name\ndescription: test", "name: assignment-plan\ndescription: 123",
            "name: assignment-plan\ndescription: true", "name: assignment-plan\ndescription: []",
            "name: assignment-plan\ndescription: {}", "name: assignment-plan\ndescription: ''",
            "name: assignment-plan\ndescription: test\ndescription: again",
            "name: Assignment-Plan\ndescription: test", "[name, description]",
        )
        for frontmatter in variants:
            with self.subTest(frontmatter=frontmatter[:80]):
                self.assertTrue(release.check_frontmatter(
                    path, "---\n" + frontmatter + "\n---\n# Test", "assignment-plan"))

    def test_valid_frontmatter_forms(self):
        for description in ('"quoted text"', ">-\n  multiline\n  description", '"' + "x" * 1024 + '"'):
            with self.subTest(description=description[:40]):
                text = '---\nname: "assignment-plan"\ndescription: ' + description + "\n---\n# Test"
                self.assertEqual([], release.check_frontmatter(
                    "skills/assignment-plan/SKILL.md", text, "assignment-plan"))

    def test_frontmatter_must_be_at_file_start(self):
        self.assertTrue(release.check_frontmatter("x", "preface\n---\nname: x\ndescription: y\n---", "x"))

    def test_nested_skill_is_rejected_not_keyerror(self):
        self.assertTrue(any("扁平" in e for e in self.verify({
            "skills/a/b/SKILL.md": "---\nname: b\ndescription: x\n---\n"})))

    def test_every_entry_dependency_is_enforced(self):
        examples = (
            ("SKILL.md", "skills/using-qihang/SKILL.md"),
            ("skills/using-qihang/SKILL.md", "../../config.yaml"),
            ("skills/assignment-plan/SKILL.md", "../using-qihang/SKILL.md"),
            ("agents/study-coach.md", "../config.yaml"),
            ("commands/notes.toml", "../skills/using-qihang/SKILL.md"),
            ("skills/portal-operator/SKILL.md", "../../references/dlut-login-sites.md"),
            ("skills/portal-operator/SKILL.md", "../../references/dlut-field-map.md"),
        )
        for path, target in examples:
            with self.subTest(path=path, target=target):
                errors = self.verify({path: self.base[path].replace(target, "removed")})
                self.assertTrue(any("前置加载" in e for e in errors), errors)

    def test_missing_dependency_file_is_rejected(self):
        self.assertTrue(any("引用不存在" in e for e in self.verify(
            missing=("skills/using-qihang/SKILL.md",))))

    def test_command_prompt_links_are_checked(self):
        path = "commands/notes.toml"
        text = self.base[path].replace('prompt = """', 'prompt = """\n`missing.md`\n', 1)
        self.assertTrue(any("引用不存在" in e for e in self.verify({path: text})))

    def test_command_toml_and_required_fields(self):
        for text in ("prompt = [", 'description = "x"\nprompt = 123', 'prompt = "x"'):
            with self.subTest(text=text):
                self.assertTrue(self.verify({"commands/notes.toml": text}))

    def test_s3_route_removed(self):
        self.assertNotIn("`S3`", self.base["skills/reading-note/SKILL.md"])
        self.assertIn("assignment-plan", self.base["skills/reading-note/SKILL.md"])
        self.assertIn("paper-outline", self.base["skills/reading-note/SKILL.md"])

    def test_notes_respects_requested_granularity(self):
        prompt = tomllib.loads(self.base["commands/notes.toml"])["prompt"]
        self.assertIn("按用户指定的粒度整理", prompt)
        self.assertIn("一页版", prompt)
        self.assertIn("分批", prompt)
        self.assertIn("不把摘要当完整笔记", prompt)
        self.assertNotIn("给出可复习的最小版本", prompt)

    def test_campus_requires_explicit_authorization(self):
        prompt = tomllib.loads(self.base["commands/campus.toml"])["prompt"]
        self.assertIn("礼貌措辞", prompt)
        self.assertIn("授权", prompt)
        self.assertIn("不登录", prompt)
        portal = self.base["skills/portal-operator/SKILL.md"]
        self.assertIn("心理服务只给入口", portal)
        self.assertIn("school.entry_jwgl", portal)
        self.assertNotIn("http://jxgl.dlut.edu.cn", portal)


class GitBoundaryTests(unittest.TestCase):
    def test_missing_main_falls_back_to_head(self):
        def run(*args, **kwargs):
            success = args[-1] == "HEAD^{commit}"
            return subprocess.CompletedProcess(args, 0 if success else 1,
                                               b"abc123\n" if success else b"", b"")
        with patch.object(release, "run_git", side_effect=run) as call:
            self.assertEqual("abc123", release.resolve_source())
            self.assertEqual(2, call.call_count)

    def test_explicit_missing_ref_does_not_fallback(self):
        with patch.object(release, "probe_commit", return_value=None) as call:
            with self.assertRaises(SystemExit):
                release.resolve_source(ref="missing")
            self.assertEqual(1, call.call_count)

    def test_no_source_fails_clearly(self):
        with patch.object(release, "probe_commit", return_value=None):
            with self.assertRaisesRegex(SystemExit, "找不到源提交"):
                release.resolve_source()

    def test_unexpected_git_failure_is_not_missing_ref(self):
        result = subprocess.CompletedProcess([], 128, b"", b"not a git repository")
        with patch.object(release, "run_git", return_value=result):
            with self.assertRaisesRegex(SystemExit, "128"):
                release.probe_commit("main")

    def test_remote_missing_is_not_error_and_ignores_stale_tracking(self):
        result = subprocess.CompletedProcess([], 2, b"", b"")
        with patch.object(release, "run_git", return_value=result), patch.object(release, "git") as git:
            self.assertIsNone(release.fetch_release_parent())
            git.assert_not_called()

    def test_remote_permission_failure_is_fatal(self):
        result = subprocess.CompletedProcess([], 128, b"", b"denied")
        with patch.object(release, "run_git", return_value=result):
            with self.assertRaisesRegex(SystemExit, "denied"):
                release.fetch_release_parent()

    def test_worktree_check_never_calls_publish_build_or_network(self):
        with patch.object(release, "build_tree") as build, patch.object(release, "publish") as publish:
            with patch.object(release, "run_git", wraps=release.run_git) as calls:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(0, release.main([]))
                self.assertTrue(all(call.args[0] == "ls-files" for call in calls.call_args_list))
            build.assert_not_called()
            publish.assert_not_called()

    def test_failed_validation_blocks_publish(self):
        with patch.object(release, "resolve_source", return_value="abc"), \
             patch.object(release, "source_entries", return_value=[]), \
             patch.object(release, "publish") as publish, contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, release.main(["--push"]))
            publish.assert_not_called()

    def test_temporary_index_cleaned_on_error(self):
        seen = []
        def fail(*args, **kwargs):
            seen.append(Path(kwargs["env"]["GIT_INDEX_FILE"]).parent)
            raise SystemExit("test failure")
        with patch.object(release, "git", side_effect=fail):
            with self.assertRaises(SystemExit):
                release.build_tree([("100644", "a" * 40, "SKILL.md")])
        self.assertTrue(seen)
        self.assertFalse(seen[0].exists())


class LocalRepositoryTests(unittest.TestCase):
    """真实 Git 集成，只使用 tmp/ 下可复用的本地仓库。

    目录跨用例复用并由 git 自身重置，避免宿主批量删除护栏干扰测试，
    也避免在一次测试运行中反复创建上千个消失的对象文件。
    """

    IT_ROOT = PROJECT / "tmp" / "release-it"

    @classmethod
    def setUpClass(cls):
        cls.base = delivery_contents()

    def setUp(self):
        self.root = self.IT_ROOT / "source"
        self.remote = self.IT_ROOT / "origin.git"
        self.stamp = self.IT_ROOT / "base.sha"
        self.env = release.git_env()
        # 防止外部会话的 Git 定位变量把测试写入真实工作区。
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES"):
            self.env.pop(key, None)
        self.IT_ROOT.mkdir(parents=True, exist_ok=True)
        self.prepare_source()
        self.patch_root = patch.object(release, "ROOT", str(self.root))
        self.patch_root.start()
        self.addCleanup(self.patch_root.stop)
        # 返回值必须是副本：被测代码会向环境里写入索引变量。
        self.patch_env = patch.object(release, "git_env", side_effect=lambda: dict(self.env))
        self.patch_env.start()
        self.addCleanup(self.patch_env.stop)

    def git(self, *args, input=None, cwd=None, check=True):
        result = subprocess.run(["git", *args], cwd=cwd or self.root,
                                env=self.env, input=input, capture_output=True)
        if check:
            self.assertEqual(0, result.returncode, result.stderr.decode("utf-8", "replace"))
        return result.stdout.decode("utf-8").strip()

    def prepare_source(self):
        """把本地仓库重置到基准提交状态，并清空 bare origin 的所有引用。"""
        if not (self.root / ".git").exists():
            self.root.mkdir(parents=True, exist_ok=True)
            self.git("init", "-b", "main")
            for path, text in self.base.items():
                file = self.root / path
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text(text, encoding="utf-8")
            (self.root / "development.txt").write_text("must not ship", encoding="utf-8")
            (self.root / ".gitignore").write_text("skills/ignored/\n", encoding="utf-8")
            self.git("add", ".")
            self.git("commit", "-m", "isolated test snapshot")
            self.stamp.write_text(self.git("rev-parse", "HEAD"), encoding="ascii")
        base = self.stamp.read_text(encoding="ascii").strip()
        self.git("update-ref", "refs/heads/main", base)
        self.git("checkout", "-q", "-f", "main")
        self.git("reset", "-q", "--hard", base)
        self.git("clean", "-qfdx")
        self.git("remote", "remove", "origin", check=False)
        for ref in self.git("for-each-ref", "--format=%(refname)",
                            "refs/remotes/origin").split():
            self.git("update-ref", "-d", ref)
        if (self.remote / "HEAD").exists():
            for ref in self.git("for-each-ref", "--format=%(refname)", cwd=self.remote).split():
                self.git("update-ref", "-d", ref, cwd=self.remote)
        self.source = base

    def commit_snapshot(self, parent=None):
        tree = self.git("write-tree")
        args = ["commit-tree", tree]
        if parent:
            args += ["-p", parent]
        commit = self.git(*args, input=b"isolated test snapshot\n")
        self.git("update-ref", "refs/heads/main", commit)
        return commit

    def init_remote(self):
        if not (self.remote / "HEAD").exists():
            self.remote.mkdir(parents=True, exist_ok=True)
            self.git("init", "--bare", str(self.remote))
        self.git("remote", "add", "origin", str(self.remote))

    def main(self, args):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            result = release.main(args)
        return result, output.getvalue()

    def git_fingerprint(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in (self.root / ".git").rglob("*") if path.is_file()}

    def test_default_check_without_origin_is_read_only(self):
        before = self.git_fingerprint()
        self.assertEqual(0, self.main([])[0])
        self.assertEqual(before, self.git_fingerprint())

    def test_ref_check_is_read_only(self):
        before = self.git_fingerprint()
        self.assertEqual(0, self.main(["--ref", "HEAD"])[0])
        self.assertEqual(before, self.git_fingerprint())

    def test_worktree_and_committed_checks_are_distinct(self):
        path = self.root / "skills/assignment-plan/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8").replace("description:", "removed:"), encoding="utf-8")
        self.assertEqual(1, self.main([])[0])
        self.assertEqual(0, self.main(["--ref", "HEAD"])[0])

    def test_untracked_whitelisted_file_is_checked_and_ignored_file_is_not(self):
        for name in ("new", "ignored"):
            path = self.root / "skills" / name / "SKILL.md"
            path.parent.mkdir()
            path.write_text("invalid skill", encoding="utf-8")
        kept, _reader = release.worktree_snapshot()
        paths = {path for _, path in kept}
        self.assertIn("skills/new/SKILL.md", paths)
        self.assertNotIn("skills/ignored/SKILL.md", paths)
        self.assertEqual(1, self.main([])[0])

    def test_deleted_required_file_is_rejected(self):
        (self.root / "config.yaml").unlink()
        self.assertEqual(1, self.main([])[0])

    def test_detached_head_without_main_falls_back(self):
        self.git("checkout", "--detach", self.source)
        self.git("update-ref", "-d", "refs/heads/main")
        self.assertEqual(self.source, release.resolve_source())
        self.assertEqual(0, self.main(["--ref", "HEAD"])[0])

    def test_first_publish_and_noop_only_to_local_remote(self):
        self.init_remote()
        self.assertEqual(0, self.main(["--push"])[0])
        first = self.git("rev-parse", "refs/heads/release", cwd=self.remote)
        shipped = self.git("ls-tree", "-r", "--name-only", "release", cwd=self.remote).splitlines()
        self.assertEqual(sorted(self.base), sorted(shipped))
        self.assertNotIn("development.txt", shipped)
        index_before = (self.root / ".git/index").read_bytes()
        self.assertEqual(0, self.main(["--push"])[0])
        self.assertEqual(first, self.git("rev-parse", "refs/heads/release", cwd=self.remote))
        self.assertEqual(index_before, (self.root / ".git/index").read_bytes())

    def test_publish_ignores_dirty_worktree(self):
        self.init_remote()
        (self.root / "config.yaml").write_text("broken: [", encoding="utf-8")
        self.assertEqual(0, self.main(["--push"])[0])
        shipped = self.git("show", "release:config.yaml", cwd=self.remote)
        self.assertEqual(self.base["config.yaml"].strip(), shipped)

    def test_publish_continues_release_history(self):
        self.init_remote()
        self.assertEqual(0, self.main(["--push"])[0])
        first = self.git("rev-parse", "refs/heads/release", cwd=self.remote)
        path = self.root / "skills/assignment-plan/SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nExtra test paragraph.\n", encoding="utf-8")
        self.git("add", ".")
        self.commit_snapshot(self.source)
        self.assertEqual(0, self.main(["--push"])[0])
        self.assertEqual(first, self.git("rev-parse", "release^", cwd=self.remote))

    def test_stale_remote_tracking_does_not_break_first_publish(self):
        self.init_remote()
        self.git("update-ref", "refs/remotes/origin/release", self.source)
        self.assertEqual(0, self.main(["--push"])[0])
        parents = self.git("rev-list", "--parents", "-n", "1", "release", cwd=self.remote).split()
        self.assertEqual(1, len(parents))


if __name__ == "__main__":
    unittest.main()
