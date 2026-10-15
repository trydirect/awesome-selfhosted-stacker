"""Unit tests for scripts/quick_deploy_links.py.

Run: python3 -m unittest scripts/test_quick_deploy_links.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import quick_deploy_links as qd  # noqa: E402

GOOD = ("https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker"
        "&path=stacker-projects/immich&ref=206881a13b81ab43aaeca1316403e1343763f261")

# What 40b0da6 left in the READMEs: `&` in a sed replacement repeats the match.
GARBLED = ("https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker"
           "&path=stacker-projects/immichquick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker"
           "&path=stacker-projects/immich&ref=mainref=e68926c")


class Problems(unittest.TestCase):
    def test_a_well_formed_link_has_none(self):
        self.assertEqual(qd.problems(GOOD, "immich"), [])

    def test_the_garbled_link_is_reported(self):
        found = qd.problems(GARBLED, "immich")
        self.assertIn("`repo` given 2 times", found)
        self.assertIn("`path` given 2 times", found)
        self.assertTrue(any("ref" in p for p in found), found)

    def test_a_link_to_another_stack_is_reported(self):
        self.assertEqual(
            qd.problems(GOOD, "mealie"),
            ["`path` is stacker-projects/immich, expected stacker-projects/mealie"],
        )

    def test_a_link_without_ref_is_reported(self):
        link = GOOD.split("&ref=")[0]
        self.assertEqual(qd.problems(link, "immich"), ["`ref` is missing"])


class Fix(unittest.TestCase):
    def test_every_link_in_a_readme_is_rewritten(self):
        text = f"[![Deploy]({GARBLED})](x)\n\nOpen:\n\n{GARBLED}\n"
        fixed = qd.fix_text(text, "immich", "206881a13b81ab43aaeca1316403e1343763f261")
        self.assertEqual(fixed, f"[![Deploy]({GOOD})](x)\n\nOpen:\n\n{GOOD}\n")

    def test_links_are_found_in_markdown(self):
        text = f"[![Deploy to TryDirect](https://img.shields.io/badge/x)]({GOOD})\n{GOOD}\n"
        self.assertEqual(qd.links(text), [GOOD, GOOD])


if __name__ == "__main__":
    unittest.main()
