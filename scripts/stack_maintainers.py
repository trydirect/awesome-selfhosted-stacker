#!/usr/bin/env python3
"""Tell a pull request's reviewers who maintains the stacks it changes.

  python3 scripts/stack_maintainers.py --author <login> --base origin/main

A stack can name its maintainers in stacker-projects/<stack>/MAINTAINERS, one
GitHub login per line (`#` starts a comment). A maintainer does not need write
access to this repository: they send pull requests from a fork, and a
maintainer of this repository reviews and merges them.

The check never fails a pull request. It writes to the job summary either that
the author changes only stacks they maintain, or which maintainers to ask
about the stacks someone else changes. MAINTAINERS is read from the base
branch, so a pull request cannot make its author a maintainer, and a change to
a MAINTAINERS file always gets a full review.
"""

import argparse
import os
import subprocess
import sys
from dataclasses import dataclass, field

STACKS = "stacker-projects/"


def parse(text):
    """The logins listed in a MAINTAINERS file, lower-cased."""
    logins = set()
    for line in text.splitlines():
        login = line.split("#", 1)[0].strip().lstrip("@").lower()
        if login:
            logins.add(login)
    return logins


@dataclass
class Scope:
    # stack -> its maintainers, for every stack the pull request changes
    projects: dict = field(default_factory=dict)
    # changed files no maintainer of the author's covers
    others: list = field(default_factory=list)
    maintainer_change: bool = False


def scope(author, changed, maintainers_of):
    """Which stacks `changed` touches and whether `author` maintains them all."""
    author = author.lower()
    result = Scope()
    for path in changed:
        parts = path.split("/")
        if not path.startswith(STACKS) or len(parts) < 3:
            result.others.append(path)
            continue
        stack = parts[1]
        if stack not in result.projects:
            result.projects[stack] = maintainers_of(stack)
        if parts[-1] == "MAINTAINERS" or author not in result.projects[stack]:
            result.others.append(path)
    result.maintainer_change = bool(changed) and not result.others
    return result


def summary(author, result):
    if result.maintainer_change:
        stacks = ", ".join(sorted(result.projects))
        return f"@{author} changes only stacks they maintain: {stacks}.\n"
    lines = []
    for stack, logins in sorted(result.projects.items()):
        if logins and author.lower() not in logins:
            names = ", ".join(f"@{login}" for login in sorted(logins))
            lines.append(f"- `{stack}` is maintained by {names}: ask them to review.")
    if not lines:
        return "No stack maintainers to ask.\n"
    return "Stack maintainers:\n" + "\n".join(lines) + "\n"


def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout


def maintainers_on(base):
    def of(stack):
        try:
            return parse(git("show", f"{base}:{STACKS}{stack}/MAINTAINERS"))
        except subprocess.CalledProcessError:
            return set()

    return of


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--author", required=True)
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()

    changed = [p for p in git("diff", "--name-only", f"{args.base}...HEAD").splitlines() if p]
    text = summary(args.author, scope(args.author, changed, maintainers_on(args.base)))
    print(text, end="")
    out = os.environ.get("GITHUB_STEP_SUMMARY")
    if out:
        with open(out, "a") as f:
            f.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
