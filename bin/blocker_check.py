#!/usr/bin/env python3
"""blocker_check — which open entries name a file that has since changed?

P-9cef: the session that clears a blocker is rarely the session that recorded
it, and nothing links the two. P5 sat three sessions after its blocker was
describable; P8 and P9 read as "the convention is unwritten" after the
convention had been written by someone else.

This does not decide whether a block is cleared — that needs reading. It turns
"re-check everything" into a short list, which is a task a session can finish.

  python3 bin/blocker_check.py            list entries worth re-reading
  python3 bin/blocker_check.py --all      include CLOSED entries too

Exit code is always 0. A hard failure here would go red on every edit to
CONTRIBUTING.md, and a check that is red by default is a check people learn to
skip.
"""
import re
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "docs", "OPEN-PROBLEMS.md")


def last_commit(path):
    r = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%ct|%h|%ad",
                        "--date=short", "--", path],
                       capture_output=True, text=True)
    out = r.stdout.strip()
    return out.split("|") if out else None


def tracked():
    r = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True)
    return set(r.stdout.split())


def entries(text):
    parts = re.split(r"^## ", text, flags=re.M)[1:]
    for p in parts:
        head = p.split("\n", 1)[0]
        m = re.match(r"(P[-0-9a-f]+)\s+—\s+(.*?)\s*`(OPEN|CLOSED|SPEC'D)`", head)
        if m:
            yield m.group(1), m.group(2), m.group(3), p


def main():
    show_all = "--all" in sys.argv
    text = open(LEDGER, encoding="utf-8").read()
    files = tracked()
    led = last_commit("docs/OPEN-PROBLEMS.md")
    led_t = int(led[0]) if led else 0

    rows = []
    for pid, title, state, body in entries(text):
        if state == "CLOSED" and not show_all:
            continue
        named = {f for f in re.findall(r"`([A-Za-z0-9_./-]+\.(?:md|py|sh|yml|cff))`", body)
                 if f in files}
        for f in sorted(named):
            c = last_commit(f)
            if not c:
                continue
            t, sha, date = int(c[0]), c[1], c[2]
            # The ledger is edited constantly, so "newer than the ledger" is too
            # loose. What matters is a blocker file touched by a commit that did
            # not also touch this ledger — i.e. by some other session's work.
            same = subprocess.run(
                ["git", "-C", ROOT, "show", "--name-only", "--format=", sha],
                capture_output=True, text=True).stdout.split()
            if "docs/OPEN-PROBLEMS.md" not in same:
                rows.append((pid, state, title, f, date, sha))

    if not rows:
        print("no open entry names a file that moved independently of this ledger")
        return 0

    print(f"{len(rows)} entr{'y' if len(rows)==1 else 'ies'} worth re-reading — "
          "the named file changed in a commit that did not touch the ledger:\n")
    last = None
    for pid, state, title, f, date, sha in rows:
        if pid != last:
            print(f"  {pid}  [{state}]  {title}")
            last = pid
        print(f"      {f}  last changed {date} in {sha}")
    print("\nThis is advisory. Read the entry and the file; close, amend, or leave it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
