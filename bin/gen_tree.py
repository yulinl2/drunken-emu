#!/usr/bin/env python3
"""gen_tree — render the tracked file set as a tree, deterministically.

Why this exists rather than a `tree` invocation: docs/TREE.md previously carried
a regeneration command that could not produce its own content (`tree` hides
dotfiles without -a, so .github/ and .gitignore were invisible), and nothing
checked the two against each other. The index therefore drifted silently for
three commits.

Source of truth is `git ls-files`: the tree then means exactly "what a clone
receives", which is both unambiguous and cheap to assert in CI.

  python3 bin/gen_tree.py            # print the tree
  python3 bin/gen_tree.py --check    # exit 1 if docs/TREE.md disagrees
"""
import subprocess
import sys
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOC = ROOT / "docs" / "TREE.md"


def tracked():
    out = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted(p for p in out.splitlines() if p)


def build(paths):
    tree = {}
    for p in paths:
        node = tree
        for part in p.split("/"):
            node = node.setdefault(part, {})
    return tree


def render(node, prefix=""):
    lines = []
    # directories (non-empty dicts) first, then files; each group alphabetical
    items = sorted(node.items(), key=lambda kv: (not kv[1], kv[0]))
    for i, (name, child) in enumerate(items):
        last = i == len(items) - 1
        lines.append(f"{prefix}{'`-- ' if last else '|-- '}{name}{'/' if child else ''}")
        if child:
            lines.extend(render(child, prefix + ("    " if last else "|   ")))
    return lines


def tree_text():
    paths = tracked()
    body = "\n".join(["."] + render(build(paths)))
    ndirs = len({"/".join(p.split("/")[:i])
                 for p in paths for i in range(1, len(p.split("/")))})
    return f"{body}\n\n{ndirs} directories, {len(paths)} files tracked"


def doc_block():
    m = re.findall(r"```text\n(.*?)```", DOC.read_text(), re.S)
    return m[-1].rstrip("\n") if m else None


if __name__ == "__main__":
    current = tree_text()
    if "--check" in sys.argv:
        recorded = doc_block()
        if recorded is None:
            print("FAIL tree-index: no ```text block in docs/TREE.md")
            sys.exit(1)
        if recorded != current:
            print("FAIL tree-index: docs/TREE.md disagrees with `git ls-files`")
            import difflib
            for line in difflib.unified_diff(
                recorded.splitlines(), current.splitlines(),
                fromfile="docs/TREE.md", tofile="git ls-files", lineterm="",
            ):
                print("  " + line)
            print("\n  regenerate with: python3 bin/gen_tree.py --write")
            sys.exit(1)
        print(f"PASS  tree-index  docs/TREE.md matches {len(tracked())} tracked files")
        sys.exit(0)
    if "--write" in sys.argv:
        txt = DOC.read_text()
        new = re.sub(r"(```text\n)(.*?)(```)", lambda m: m.group(1) + current + "\n" + m.group(3),
                     txt, count=1, flags=re.S)
        DOC.write_text(new)
        print(f"wrote docs/TREE.md ({len(tracked())} tracked files)")
        sys.exit(0)
    print(current)
