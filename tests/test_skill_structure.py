"""技能正文结构回归：`docs/skill-anatomy.md` 的「执行前置 + 四段式」必须整体成立。

发布校验 `scripts/sync_release.py` 只覆盖 frontmatter、前置加载依赖与文件引用，
不检查正文章节结构；而结构最复杂的几个学习 / 产出类 skill（`code-mentor`、
`data-lab`、`lang-drill`、`paper-outline`、`explain-stepwise`、`lecture-to-notes`）
原先在 `tests/` 与 `dsh/tests/` 里没有任何断言，改了没人拦得住。契约来自
`docs/skill-anatomy.md`：

1. 每个 `skills/<name>/SKILL.md` 先有 `## 执行前置`，再有四段式
   `## Overview` → `## When to Use` → `## 执行流程` → `## 常见误判`；
2. 执行前置声明相对路径基准，并声明「本会话已加载可复用 / 不可读则停止」；
3. 业务 skill 的执行前置显式声明完整加载 `../using-qihang/SKILL.md` 与
   `../../config.yaml`；总入口是共享规则的唯一权威，不把自己当共享规则来源加载；
4. `## 常见误判` 至少 4 条 `- ❌`，且每条都给出 `✅` 正确做法；
5. 正文建议少于 500 行，超过时考虑拆分。

第 1 条若失效，后四条就只是散落在文件里的句子，所以一并锁定。
"""

from pathlib import Path
import re
import unittest

PROJECT = Path(__file__).resolve().parents[1]
SKILLS = PROJECT / "skills"
ENTRY = "skills/using-qihang/SKILL.md"

PRE = "## 执行前置"
SECTIONS = ("## Overview", "## When to Use", "## 执行流程", "## 常见误判")

PATH_BASELINE = ("本文所有包内相对路径均以本 `SKILL.md` 所在目录为基准，"
                 "不以用户当前工作目录（cwd）为基准")
REUSE_RULE = ("本会话已完整加载上述文件时可复用；必需文件不可读时，"
              "停止本包执行并说明缺失或不可读的文件，不猜测规则。")
SHARED_RULE_REF = "`../using-qihang/SKILL.md`"
CONFIG_REF = "`../../config.yaml`"

BAD = "- ❌"
GOOD = "✅"
MAX_LINES = 500


def split_h2(text):
    """按 `## ` 标题切分正文，返回 [(标题, 正文行列表)] 并保持原顺序。"""
    out, current, body = [], None, []
    for line in text.split("\n"):
        if line.startswith("## "):
            if current is not None:
                out.append((current, body))
            current, body = line.strip(), []
        elif current is not None:
            body.append(line)
    if current is not None:
        out.append((current, body))
    return out


def body_of(sections, title):
    """返回某个 h2 标题下的正文（同名标题全部拼接）；不存在则返回空串。"""
    return "\n".join(line for current, body in sections if current == title
                     for line in body)


def structure_errors(files):
    """files 为 {相对路径: 正文}。返回结构违背清单，空列表表示全部成立。"""
    errors = []
    skills = {path: text for path, text in files.items()
              if path.startswith("skills/") and path.endswith("/SKILL.md")}
    if not skills:
        return ["交付树里没有 skills/<name>/SKILL.md"]

    for path, text in sorted(skills.items()):
        sections = split_h2(text)
        titles = [title for title, _ in sections]

        missing = [title for title in SECTIONS if title not in titles]
        if missing:
            errors.append("%s 缺少四段式章节：%s" % (path, "、".join(missing)))
        elif [title for title in titles if title in SECTIONS] != list(SECTIONS):
            errors.append("%s 四段式章节顺序不符：%s" % (path, titles))

        if PRE not in titles:
            errors.append("%s 缺少 `%s` 章节" % (path, PRE))
        elif "## Overview" in titles and titles.index(PRE) > titles.index("## Overview"):
            errors.append("%s 的 `%s` 必须排在 `## Overview` 之前" % (path, PRE))

        preamble = "\n".join(line for line in body_of(sections, PRE).split("\n")
                             if line.strip())
        if PATH_BASELINE not in preamble:
            errors.append("%s 的执行前置未声明相对路径基准" % path)
        if REUSE_RULE not in preamble:
            errors.append("%s 的执行前置未声明「已加载可复用 / 不可读则停止」" % path)
        if path == ENTRY:
            if CONFIG_REF not in preamble:
                errors.append("%s 的执行前置未声明完整加载 %s" % (path, CONFIG_REF))
            if SHARED_RULE_REF in preamble:
                errors.append("%s 是共享规则的唯一权威，不应把自身当共享规则来源加载" % path)
        else:
            for target in (SHARED_RULE_REF, CONFIG_REF):
                if target not in preamble:
                    errors.append("%s 的执行前置未声明完整加载 %s" % (path, target))

        mistakes = [line.strip() for line in body_of(sections, "## 常见误判").split("\n")
                    if line.strip().startswith(BAD)]
        if len(mistakes) < 4:
            errors.append("%s 的常见误判少于 4 条（%d 条）" % (path, len(mistakes)))
        for line in mistakes:
            if GOOD not in line:
                errors.append("%s 的常见误判有缺正确做法的条目：%s" % (path, line[:48]))

        lines = len(text.split("\n"))
        if lines >= MAX_LINES:
            errors.append("%s 正文 %d 行，达到 %d 行上限，应考虑拆分" % (path, lines, MAX_LINES))

    entry = files.get(ENTRY, "")
    declared = re.search(r"本包共 (\d+) 个 skill", entry)
    if declared is None:
        errors.append("%s 未声明本包的 skill 数量" % ENTRY)
    elif int(declared.group(1)) != len(skills):
        errors.append("%s 声明 %s 个 skill，实际有 %d 个"
                      % (ENTRY, declared.group(1), len(skills)))
    return errors


class SkillStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {path.relative_to(PROJECT).as_posix(): path.read_text(encoding="utf-8")
                     for path in sorted(SKILLS.glob("*/SKILL.md"))}

    def mutate(self, relative, old, new, count=1):
        files = dict(self.files)
        self.assertIn(old, files[relative])
        files[relative] = files[relative].replace(old, new, count)
        return files

    def test_current_tree_satisfies_structure_contract(self):
        self.assertEqual([], structure_errors(self.files))

    def test_every_skill_declares_the_four_sections_in_order(self):
        for path, text in sorted(self.files.items()):
            with self.subTest(path=path):
                titles = [title for title, _ in split_h2(text)]
                self.assertEqual(list(SECTIONS),
                                 [title for title in titles if title in SECTIONS])
                self.assertIn(PRE, titles)

    def test_preamble_precedes_overview_everywhere(self):
        for path, text in sorted(self.files.items()):
            with self.subTest(path=path):
                titles = [title for title, _ in split_h2(text)]
                self.assertLess(titles.index(PRE), titles.index("## Overview"))

    def test_business_skills_load_shared_rules_and_config(self):
        for path, text in sorted(self.files.items()):
            if path == ENTRY:
                continue
            with self.subTest(path=path):
                preamble = body_of(split_h2(text), PRE)
                self.assertIn(SHARED_RULE_REF, preamble)
                self.assertIn(CONFIG_REF, preamble)

    def test_entry_is_the_authority_and_does_not_load_itself(self):
        preamble = body_of(split_h2(self.files[ENTRY]), PRE)
        self.assertIn(CONFIG_REF, preamble)
        self.assertNotIn(SHARED_RULE_REF, preamble)

    def test_mistakes_pair_a_failure_with_a_correct_action(self):
        for path, text in sorted(self.files.items()):
            with self.subTest(path=path):
                mistakes = [line for line in body_of(split_h2(text), "## 常见误判").split("\n")
                            if line.strip().startswith(BAD)]
                self.assertGreaterEqual(len(mistakes), 4)
                for line in mistakes:
                    self.assertIn(GOOD, line)

    def test_skill_count_matches_the_declaration(self):
        declared = re.search(r"本包共 (\d+) 个 skill", self.files[ENTRY])
        self.assertIsNotNone(declared)
        self.assertEqual(int(declared.group(1)), len(self.files))

    def test_no_body_reaches_the_line_limit(self):
        for path, text in sorted(self.files.items()):
            with self.subTest(path=path):
                self.assertLess(len(text.split("\n")), MAX_LINES)

    def test_missing_preamble_is_detected(self):
        files = self.mutate("skills/code-mentor/SKILL.md", PRE, "## 前置说明")
        self.assertIn("缺少 `%s` 章节" % PRE, " ".join(structure_errors(files)))

    def test_preamble_after_overview_is_detected(self):
        path = "skills/data-lab/SKILL.md"
        files = dict(self.files)
        files[path] = (files[path].replace(PRE, "@@swap@@", 1)
                       .replace("## Overview", PRE, 1)
                       .replace("@@swap@@", "## Overview", 1))
        self.assertIn("必须排在", " ".join(structure_errors(files)))

    def test_reordered_sections_are_detected(self):
        path = "skills/paper-outline/SKILL.md"
        files = dict(self.files)
        files[path] = files[path].replace("## Overview", "## 概览", 1)
        self.assertIn("缺少四段式章节", " ".join(structure_errors(files)))

    def test_dropped_shared_rule_load_is_detected(self):
        files = self.mutate("skills/lang-drill/SKILL.md", SHARED_RULE_REF, "共享规则")
        self.assertIn("未声明完整加载", " ".join(structure_errors(files)))

    def test_dropped_config_load_is_detected(self):
        files = self.mutate("skills/explain-stepwise/SKILL.md", CONFIG_REF, "配置")
        self.assertIn("未声明完整加载", " ".join(structure_errors(files)))

    def test_entry_loading_itself_is_detected(self):
        path = ENTRY
        text = self.files[path]
        files = dict(self.files)
        files[path] = text.replace(
            "## Overview", "- 先完整读取 `%s`。\n\n## Overview" % SHARED_RULE_REF, 1)
        self.assertIn("唯一权威", " ".join(structure_errors(files)))

    def test_dropped_path_baseline_is_detected(self):
        files = self.mutate("skills/lecture-to-notes/SKILL.md", PATH_BASELINE, "路径以本文件为基准")
        self.assertIn("未声明相对路径基准", " ".join(structure_errors(files)))

    def test_dropped_reuse_rule_is_detected(self):
        files = self.mutate("skills/reading-note/SKILL.md", REUSE_RULE, "可复用。")
        self.assertIn("已加载可复用", " ".join(structure_errors(files)))

    def test_too_few_mistakes_is_detected(self):
        path = "skills/recall-schedule/SKILL.md"
        head = self.files[path].partition("## 常见误判")[0]
        files = dict(self.files)
        files[path] = head + "## 常见误判\n\n- ❌ 只答一次 → ✅ 给出排程\n"
        self.assertIn("少于 4 条", " ".join(structure_errors(files)))

    def test_mistake_without_correct_action_is_detected(self):
        files = self.mutate("skills/portal-operator/SKILL.md",
                            "- ❌ 登录不上就编一个成绩或课表 → ✅ ",
                            "- ❌ 登录不上就编一个成绩或课表 → ")
        self.assertIn("缺正确做法", " ".join(structure_errors(files)))

    def test_oversized_body_is_detected(self):
        path = "skills/code-mentor/SKILL.md"
        files = dict(self.files)
        files[path] = files[path] + "\n".join("补充说明 %d" % i for i in range(MAX_LINES))
        self.assertIn("行上限", " ".join(structure_errors(files)))

    def test_wrong_declared_skill_count_is_detected(self):
        files = self.mutate(ENTRY, "本包共 25 个 skill", "本包共 26 个 skill")
        self.assertIn("实际有", " ".join(structure_errors(files)))


if __name__ == "__main__":
    unittest.main()
