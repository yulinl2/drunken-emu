---
id: mod.replace-bold-with-weight
kind: mod
status: VERIFIED
title: "Replace bold with weight"
sources: [S54]
---

# Replace bold with weight

**Sources:** [S54](src.s54.md)

`bold` on a `Text` is deprecated in favor of `weight` and still works. To replace it on a `Text` with no `weight`, change `bold: true` to `weight: 'semibold'` for the same result on Claude Code v2.1.299 or later.
