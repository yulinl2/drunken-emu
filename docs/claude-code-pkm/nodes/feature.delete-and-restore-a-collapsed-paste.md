---
id: feature.delete-and-restore-a-collapsed-paste
kind: feature
status: VERIFIED
title: "Delete and restore a collapsed paste"
sources: [S74]
---

# Delete and restore a collapsed paste

**Sources:** [S74](src.s74.md)

When you delete with a word or line shortcut such as `Ctrl+W` or `Ctrl+K`, or with a vim delete through an `f`/`t` motion such as `df]`, and the deleted range reaches inside a `[Pasted text #N]` placeholder, Claude Code removes the placeholder whole. To restore it, paste the deletion back with `Ctrl+Y` after a word or line shortcut, or with `p` in NORMAL mode after a vim delete.
