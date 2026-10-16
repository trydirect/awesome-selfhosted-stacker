#!/usr/bin/env python3
"""Check that every stack's stacker.yml `version` is semver.

  python3 scripts/stack_versions.py            # CI: fails on any non-semver version

`version` is the stack's own version, MAJOR.MINOR.PATCH (e.g. 1.0.0), not the
app's image tag or an upstream commit. Quick Deploy finds a stack's baked
snapshot by this version, and a snapshot is recorded with the template's
semver version, so any other value finds no snapshot. A stack may leave
`version` out (or null); Quick Deploy then uses the latest snapshot.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STACKS = ROOT / "stacker-projects"

# semver.org 2.0.0
SEMVER = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
TOP_LEVEL_VERSION = re.compile(r"^version:[ \t]*(.*?)[ \t]*(?:#.*)?$", re.MULTILINE)


def version(text):
    """The top-level `version` of a stacker.yml, or None when absent or null."""
    match = TOP_LEVEL_VERSION.search(text)
    if not match:
        return None
    value = match.group(1)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return None if value in ("", "null", "~") else value


def is_semver(value):
    return bool(SEMVER.match(value))


def problems(stacks):
    """`stacks` maps a stack name to its stacker.yml text."""
    found = []
    for name, text in sorted(stacks.items()):
        value = version(text)
        if value is not None and not is_semver(value):
            found.append(f"{name}: version '{value}' is not semver (MAJOR.MINOR.PATCH, e.g. 1.0.0)")
    return found


def main():
    stacks = {p.parent.name: p.read_text() for p in sorted(STACKS.glob("*/stacker.yml"))}
    found = problems(stacks)
    for line in found:
        print(f"❌ {line}")
    if found:
        return 1
    print(f"✅ {len(stacks)} stacks: every version is semver")
    return 0


if __name__ == "__main__":
    sys.exit(main())
