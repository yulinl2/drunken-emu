---
id: process.build
kind: process
status: REPO
title: "Build the node set"
sources: [S9]
---

# Build the node set

**Sources:** [S9](src.s9.md)

Edit build/src/*.txt, then run python3 docs/claude-code-pkm/build/build_nodes.py. The builder checks duplicate IDs, unknown kinds, statuses and sources, and dangling links. If any check fails, it writes nothing. Run it with --check to confirm that nodes/ and INDEX.md match the sources, without writing. Then regenerate docs/TREE.md with bin/gen_tree.py --write, and check it with --check.

## Linked from

- [CI asserts the tree index](git-rule.tree-index-ci.md)
- [D11: One node per concept, generated from build/src](dec.d11.md)
- [D1: Location in docs/ on the designated branch](dec.d1.md)
- [D9: Regenerate docs/TREE.md and check it](dec.d9.md)
