---
id: permission-rule.symlinks
kind: permission-rule
status: VERIFIED
title: "Symlinks"
sources: [S66]
---

# Symlinks

**Sources:** [S66](src.s66.md)

When a file path Claude requests goes through a symlink, the permission check covers two paths: the one Claude requested and the file it resolves to. This applies to symbolic links on macOS, Linux, and Windows, and to directory junctions on Windows.
