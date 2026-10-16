"""Unit tests for scripts/stack_maintainers.py.

Run: python3 -m unittest scripts/test_stack_maintainers.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stack_maintainers as sm  # noqa: E402

MAINTAINERS = {"local-ai-packaged": {"coleam00"}, "n8n": {"someone"}}


def of(project):
    return MAINTAINERS.get(project, set())


class Parse(unittest.TestCase):
    def test_one_login_per_line_with_comments_and_at_signs(self):
        text = "# maintainers of this stack\n@ColeAm00\n\n  other-user  # co-maintainer\n"
        self.assertEqual(sm.parse(text), {"coleam00", "other-user"})

    def test_an_empty_file_has_no_maintainers(self):
        self.assertEqual(sm.parse(""), set())


class Scope(unittest.TestCase):
    def test_a_maintainer_changing_only_their_stack(self):
        result = sm.scope(
            "ColeAm00",
            ["stacker-projects/local-ai-packaged/stacker.yml",
             "stacker-projects/local-ai-packaged/README.md"],
            of,
        )
        self.assertTrue(result.maintainer_change)
        self.assertEqual(result.projects, {"local-ai-packaged": {"coleam00"}})

    def test_a_maintainer_also_changing_another_stack(self):
        result = sm.scope(
            "coleam00",
            ["stacker-projects/local-ai-packaged/stacker.yml",
             "stacker-projects/n8n/stacker.yml"],
            of,
        )
        self.assertFalse(result.maintainer_change)
        self.assertEqual(result.others, ["stacker-projects/n8n/stacker.yml"])

    def test_a_maintainer_also_changing_a_file_outside_the_stacks(self):
        result = sm.scope(
            "coleam00",
            ["stacker-projects/local-ai-packaged/stacker.yml", ".github/workflows/ci.yml"],
            of,
        )
        self.assertFalse(result.maintainer_change)
        self.assertEqual(result.others, [".github/workflows/ci.yml"])

    def test_a_change_to_the_maintainers_file_is_never_a_maintainer_change(self):
        result = sm.scope(
            "coleam00", ["stacker-projects/local-ai-packaged/MAINTAINERS"], of
        )
        self.assertFalse(result.maintainer_change)
        self.assertEqual(result.others, ["stacker-projects/local-ai-packaged/MAINTAINERS"])

    def test_someone_else_changing_a_maintained_stack(self):
        result = sm.scope(
            "stranger", ["stacker-projects/local-ai-packaged/stacker.yml"], of
        )
        self.assertFalse(result.maintainer_change)
        self.assertEqual(result.projects, {"local-ai-packaged": {"coleam00"}})

    def test_a_stack_without_maintainers(self):
        result = sm.scope("coleam00", ["stacker-projects/umami/stacker.yml"], of)
        self.assertFalse(result.maintainer_change)
        self.assertEqual(result.projects, {"umami": set()})

    def test_no_changed_files(self):
        self.assertFalse(sm.scope("coleam00", [], of).maintainer_change)


class Summary(unittest.TestCase):
    def test_names_the_maintainers_to_ask_when_someone_else_changes_a_stack(self):
        text = sm.summary(
            "stranger", sm.scope("stranger", ["stacker-projects/local-ai-packaged/x"], of)
        )
        self.assertIn("@coleam00", text)
        self.assertIn("local-ai-packaged", text)

    def test_says_when_the_change_is_the_maintainers_own(self):
        text = sm.summary(
            "coleam00", sm.scope("coleam00", ["stacker-projects/local-ai-packaged/x"], of)
        )
        self.assertIn("only stacks they maintain", text)


if __name__ == "__main__":
    unittest.main()
