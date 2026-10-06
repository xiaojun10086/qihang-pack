"""技能正文契约回归：登录判断（共享行为准则第四条）必须整体成立。

发布校验 `scripts/sync_release.py` 只覆盖 frontmatter、前置加载依赖与文件引用，
不检查本契约的任何一条；技能正文改了却没人拦得住，所以在此独立锁定。

契约来自 `skills/using-qihang/SKILL.md` 的共享行为准则第四条：

1. 12 个查询型 skill 各含一行以 `**登录判断**：` 开头的正文，给出「公开可查 / 需登录」双向分流；
2. 该行自「需登录时按」起的后段是**逐字一致**的共享样板（只有前段按 skill 定制；
   样板自 v4.2.1 起含「Chrome / Edge 136 起必须用独立配置目录」的前提说明）；
3. 样板声明用**用户自己的浏览器**登录，本包不代开浏览器、不代填凭证；
4. 样板把完整流程指向 `../portal-operator/SKILL.md`；
5. 总入口确实定义了第四条，且声明了共享准则的条数；
6. 每个查询型 skill 的 `## 常见误判` 各有一条登录相关的纠偏。

后三条若失效，前两条就只是空话，所以一并锁定。
"""

from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[1]
SKILLS = PROJECT / "skills"
ENTRY = "skills/using-qihang/SKILL.md"

QUERY_SKILLS = (
    "advisor-finder", "assignment-plan", "campus-desk", "campus-proof-guide",
    "campus-search", "citation-verify", "course-select", "dorm-life",
    "exam-sprint", "faster-cycle", "lit-fetch", "notice-track",
)

MARKER = "**登录判断**："
SUFFIX_START = "需登录时按"
SHARED_SUFFIX = (
    "需登录时按 `../using-qihang/SKILL.md` 共享行为准则第四条给出登录要求"
    "（**先给最快捷做法**：让用户用**独立配置目录**加 `--remote-debugging-port=0` 启动一次，"
    "登录一次即长期免登录，端口写入该目录的 `DevToolsActivePort`"
    "（**Chrome / Edge 136 起会忽略默认配置目录上的调试端口，必须用独立目录**，"
    "理由见共享行为准则第四条）；"
    "用户本人用**自己的浏览器**登录，本包不代开浏览器、不代填凭证；"
    "要本包直接操作页面需带调试端口启动，用户确认已登录后本包才接入）；"
    "完整流程见 `../portal-operator/SKILL.md`。"
)
SHARED_PRINCIPLE = "**四、涉及查询先判是否需要登录。**"
SHARED_COUNT = "统一四条共享行为准则"


def skill_path(name):
    return "skills/%s/SKILL.md" % name


def login_line(text):
    """返回正文里 `**登录判断**：` 那一行的后半段；没有该行则返回 None。"""
    for line in text.split("\n"):
        if line.startswith(MARKER):
            return line[len(MARKER):]
    return None


def common_mistakes(text):
    """返回 `## 常见误判` 段落的正文；没有该段则返回空串。"""
    lines, collected, inside = text.split("\n"), [], False
    for line in lines:
        if line.startswith("## "):
            inside = line.strip() == "## 常见误判"
            continue
        if inside:
            collected.append(line)
    return "\n".join(collected)


def contract_errors(files):
    """files 为 {相对路径: 正文}。返回契约违背清单，空列表表示全部成立。"""
    errors, judged = [], {}
    for path, text in sorted(files.items()):
        if not (path.startswith("skills/") and path.endswith("/SKILL.md")):
            continue
        line = login_line(text)
        if line is None:
            continue
        judged[path.split("/")[1]] = (line, text)

    if tuple(sorted(judged)) != tuple(sorted(QUERY_SKILLS)):
        errors.append("带登录判断的 skill 集合与契约不符：%s" % sorted(judged))

    suffixes = set()
    for name in QUERY_SKILLS:
        if name not in judged:
            continue
        line, text = judged[name]
        if "公开可查" not in line or "需登录，转" not in line:
            errors.append("%s 的登录判断未给出「公开可查 / 需登录」双向分流" % skill_path(name))
        index = line.find(SUFFIX_START)
        if index < 0:
            errors.append("%s 的登录判断缺少共享样板（未出现「%s」）" % (skill_path(name), SUFFIX_START))
        else:
            suffixes.add(line[index:])
        if "登录" not in common_mistakes(text):
            errors.append("%s 的常见误判缺少登录相关纠偏" % skill_path(name))

    if len(suffixes) > 1:
        errors.append("登录判断的共享样板不是逐字一致，出现 %d 个变体" % len(suffixes))
    elif suffixes and suffixes.pop() != SHARED_SUFFIX:
        errors.append("登录判断的共享样板与契约文本不一致")

    entry = files.get(ENTRY, "")
    if SHARED_PRINCIPLE not in entry:
        errors.append("%s 未定义共享行为准则第四条" % ENTRY)
    if SHARED_COUNT not in entry:
        errors.append("%s 未声明共享行为准则的条数" % ENTRY)
    return errors


class LoginJudgmentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = {path.relative_to(PROJECT).as_posix(): path.read_text(encoding="utf-8")
                     for path in sorted(SKILLS.glob("*/SKILL.md"))}
        cls.files[ENTRY] = (PROJECT / ENTRY).read_text(encoding="utf-8")

    def mutate(self, relative, old, new, count=1):
        files = dict(self.files)
        self.assertIn(old, files[relative])
        files[relative] = files[relative].replace(old, new, count)
        return files

    def test_current_tree_satisfies_login_contract(self):
        self.assertEqual([], contract_errors(self.files))

    def test_query_skill_set_is_exactly_the_contract_set(self):
        judged = sorted(login_line(text) is not None for text in
                        (self.files[skill_path(name)] for name in QUERY_SKILLS))
        self.assertEqual([True] * len(QUERY_SKILLS), judged)
        self.assertIsNone(login_line(self.files[ENTRY]))

    def test_shared_suffix_is_verbatim(self):
        for name in QUERY_SKILLS:
            with self.subTest(skill=name):
                line = login_line(self.files[skill_path(name)])
                self.assertTrue(line.endswith(SHARED_SUFFIX), line)

    def test_suffix_forbids_acting_as_the_user(self):
        for phrase in ("自己的浏览器", "不代开浏览器", "不代填凭证"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, SHARED_SUFFIX)
        self.assertIn("../portal-operator/SKILL.md", SHARED_SUFFIX)

    def test_entry_defines_the_shared_principle(self):
        entry = self.files[ENTRY]
        self.assertIn(SHARED_PRINCIPLE, entry)
        self.assertIn(SHARED_COUNT, entry)

    def test_every_query_skill_has_a_local_mistake_entry(self):
        for name in QUERY_SKILLS:
            with self.subTest(skill=name):
                self.assertIn("登录", common_mistakes(self.files[skill_path(name)]))

    def test_divergent_suffix_is_detected(self):
        files = self.mutate(skill_path("dorm-life"), "不代填凭证", "可代填凭证")
        self.assertTrue(any("逐字一致" in e for e in contract_errors(files)))

    def test_missing_judgment_line_is_detected(self):
        files = self.mutate(skill_path("exam-sprint"), MARKER, "**登录说明**：")
        self.assertTrue(any("集合与契约不符" in e for e in contract_errors(files)))

    def test_one_sided_judgment_is_detected(self):
        path = skill_path("campus-search")
        line = login_line(self.files[path])
        files = self.mutate(path, line, line.replace("需登录，转", "视情况转"))
        self.assertTrue(any("双向分流" in e for e in contract_errors(files)))

    def test_dropped_local_mistake_entry_is_detected(self):
        path = skill_path("lit-fetch")
        files = dict(self.files)
        files[path] = files[path].replace(
            common_mistakes(files[path]), "- ❌ 无关条目 → ✅ 无关结论")
        self.assertTrue(any("缺少登录相关纠偏" in e for e in contract_errors(files)))

    def test_missing_shared_principle_is_detected(self):
        files = self.mutate(ENTRY, SHARED_PRINCIPLE, "**四、涉及查询视情况处理。**")
        self.assertTrue(any("未定义共享行为准则第四条" in e for e in contract_errors(files)))

    def test_undeclared_principle_count_is_detected(self):
        files = self.mutate(ENTRY, SHARED_COUNT, "统一若干条共享行为准则")
        self.assertTrue(any("未声明共享行为准则的条数" in e for e in contract_errors(files)))


FASTEST_COMMAND = "--remote-debugging-port=0"
PORT_FILE = "DevToolsActivePort"


def fastest_login_errors(files):
    """files 为 {相对路径: 正文}。返回 v4.2.1 最快捷登入路径的违背清单。"""
    errors = []
    for path in (ENTRY, "skills/portal-operator/SKILL.md"):
        text = files.get(path, "")
        if FASTEST_COMMAND not in text:
            errors.append("%s 未给出 %s 的最快捷启动命令" % (path, FASTEST_COMMAND))
        if PORT_FILE not in text:
            errors.append("%s 未说明端口从 %s 自动发现" % (path, PORT_FILE))
    if "browser/edge" not in files.get(ENTRY, "") or "browser/chrome" not in files.get(ENTRY, ""):
        errors.append("%s 未给出 Edge / Chrome 两套专用配置目录" % ENTRY)
    if "先给最快捷做法" not in SHARED_SUFFIX or FASTEST_COMMAND not in SHARED_SUFFIX:
        errors.append("共享样板未要求先给最快捷做法")
    if PORT_FILE not in SHARED_SUFFIX:
        errors.append("共享样板未说明端口从 %s 自动发现" % PORT_FILE)
    for name in QUERY_SKILLS:
        text = files.get(skill_path(name), "")
        if "9222" in text:
            errors.append("%s 仍写死调试端口 9222" % skill_path(name))
    return errors


class FastestLoginPathTests(unittest.TestCase):
    """v4.2.1：登录要求必须先给「独立配置目录 + 自动端口」的最快捷做法。"""

    @classmethod
    def setUpClass(cls):
        cls.files = {path.relative_to(PROJECT).as_posix(): path.read_text(encoding="utf-8")
                     for path in sorted(SKILLS.glob("*/SKILL.md"))}
        cls.files[ENTRY] = (PROJECT / ENTRY).read_text(encoding="utf-8")
        cls.files["skills/portal-operator/SKILL.md"] = (
            PROJECT / "skills/portal-operator/SKILL.md").read_text(encoding="utf-8")

    def test_current_tree_satisfies_fastest_login_contract(self):
        self.assertEqual([], fastest_login_errors(self.files))

    def test_no_hardcoded_debug_port_in_any_skill(self):
        offenders = sorted(path for path, text in self.files.items() if "9222" in text)
        self.assertEqual([], offenders)

    def test_dropped_zero_port_command_is_detected(self):
        files = dict(self.files)
        files[ENTRY] = files[ENTRY].replace(FASTEST_COMMAND, "--remote-debugging-port=9222")
        self.assertIn("未给出", " ".join(fastest_login_errors(files)))

    def test_dropped_port_file_discovery_is_detected(self):
        files = dict(self.files)
        files[ENTRY] = files[ENTRY].replace(PORT_FILE, "端口文件")
        self.assertIn("未说明端口", " ".join(fastest_login_errors(files)))


if __name__ == "__main__":
    unittest.main()
