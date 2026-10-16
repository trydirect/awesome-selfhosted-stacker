"""Unit tests for scripts/stack_versions.py.

Run: python3 -m unittest scripts/test_stack_versions.py
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import stack_versions as sv  # noqa: E402


class Version(unittest.TestCase):
    def test_reads_quoted_and_bare_values(self):
        self.assertEqual(sv.version('name: x\nversion: "1.0.0"\n'), "1.0.0")
        self.assertEqual(sv.version("name: x\nversion: 1.0.0\n"), "1.0.0")
        self.assertEqual(sv.version("name: x\nversion: '0.1.0'\n"), "0.1.0")

    def test_no_version_or_null_is_none(self):
        self.assertIsNone(sv.version("name: x\n"))
        self.assertIsNone(sv.version("name: x\nversion: null\n"))
        self.assertIsNone(sv.version("name: x\nversion: ~\n"))

    def test_only_the_top_level_key_counts(self):
        self.assertIsNone(sv.version("name: x\nservices:\n  - name: a\n    version: latest\n"))


class Semver(unittest.TestCase):
    def test_accepts_semver(self):
        for good in ["1.0.0", "0.1.0", "10.20.30", "1.0.0-rc.1", "1.0.0+build.5", "2.0.0-beta+exp.sha.5114f85"]:
            self.assertTrue(sv.is_semver(good), good)

    def test_refuses_everything_else(self):
        for bad in ["2c541913", "latest", "v1.5.7", "1.2", "2.1", "stable-9191-1",
                    "240721-a0e3e14", "management-ui-v1", "01.0.0", "1.0", ""]:
            self.assertFalse(sv.is_semver(bad), bad)


class Problems(unittest.TestCase):
    def test_names_each_stack_with_a_non_semver_version(self):
        found = sv.problems({
            "good": 'version: "1.0.0"\n',
            "none": "name: none\n",
            "hash": 'version: "2c541913"\n',
        })
        self.assertEqual(found, ["hash: version '2c541913' is not semver (MAJOR.MINOR.PATCH, e.g. 1.0.0)"])


if __name__ == "__main__":
    unittest.main()
