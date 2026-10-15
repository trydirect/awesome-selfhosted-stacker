#!/usr/bin/env python3
"""Check (and fix) the Quick Deploy links in the stack READMEs.

  python3 scripts/quick_deploy_links.py --check [stack ...]     # CI: all, or the given stacks
  python3 scripts/quick_deploy_links.py --fix --ref <commit>    # rewrite every link

A Quick Deploy link sends try.direct/quick-deploy one `source`, `repo`, `path`
and `ref`; the User Service then fetches `<path>/stacker.yml` at `<ref>`.
--check fails when a link carries any key twice or points at another stack
(40b0da6 duplicated every link with a sed `&`), or when its ref has no
`stacker.yml` for the stack. It warns when that stacker.yml differs from the
one in the working tree: the link still deploys, but an older version.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://try.direct/quick-deploy"
REPO = "trydirect/awesome-selfhosted-stacker"
LINK = re.compile(r"https://try\.direct/quick-deploy\?[^\s)\]]*")


def links(text):
    return LINK.findall(text)


def canonical(stack, ref):
    return f"{BASE}?source=github&repo={REPO}&path=stacker-projects/{stack}&ref={ref}"


def problems(link, stack):
    query = parse_qs(urlsplit(link).query, keep_blank_values=True)
    found = [f"`{key}` given {len(values)} times" for key, values in query.items() if len(values) > 1]
    one = {key: values[0] for key, values in query.items()}
    if one.get("source") != "github":
        found.append(f"`source` is {one.get('source')!r}, expected github")
    if one.get("repo") != REPO:
        found.append(f"`repo` is {one.get('repo')!r}, expected {REPO}")
    expected = f"stacker-projects/{stack}"
    if "path" in one and one["path"] != expected:
        found.append(f"`path` is {one['path']}, expected {expected}")
    elif "path" not in one:
        found.append("`path` is missing")
    ref = one.get("ref")
    if not ref:
        found.append("`ref` is missing")
    elif not re.fullmatch(r"[A-Za-z0-9._/-]+", ref):
        found.append(f"`ref` {ref!r} is not a branch or commit")
    return found


def fix_text(text, stack, ref):
    return LINK.sub(lambda _: canonical(stack, ref), text)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def readmes(stacks=None):
    found = (ROOT / "stacker-projects").glob("*/README.md")
    return sorted(p for p in found
                  if links(p.read_text()) and (not stacks or p.parent.name in stacks))


def check(stacks=None):
    errors, warnings = [], []
    for readme in readmes(stacks):
        stack = readme.parent.name
        rel = readme.relative_to(ROOT)
        for link in links(readme.read_text()):
            found = problems(link, stack)
            errors += [f"{rel}: {p}" for p in found]
            if found:
                continue
            ref = parse_qs(urlsplit(link).query)["ref"][0]
            at_ref = git("show", f"{ref}:stacker-projects/{stack}/stacker.yml")
            if at_ref.returncode != 0:
                errors.append(f"{rel}: no stacker-projects/{stack}/stacker.yml at ref {ref}")
            elif at_ref.stdout != (readme.parent / "stacker.yml").read_text():
                warnings.append(f"{rel}: ref {ref[:12]} deploys an older stacker.yml than this branch")
    for w in sorted(set(warnings)):
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    return not errors


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--fix", action="store_true")
    parser.add_argument("--ref", help="commit every link should deploy (with --fix)")
    parser.add_argument("stacks", nargs="*", help="stack directories to check (default: all)")
    args = parser.parse_args()
    if args.check:
        sys.exit(0 if check(args.stacks) else 1)
    if not args.ref:
        parser.error("--fix needs --ref")
    for readme in readmes():
        text = readme.read_text()
        fixed = fix_text(text, readme.parent.name, args.ref)
        if fixed != text:
            readme.write_text(fixed)
            print(f"fixed {readme.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
