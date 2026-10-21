---
id: permission-mode.a-shell-variable-followed-by-one-common-top-level-directory
kind: permission-mode
status: VERIFIED
title: "A shell variable followed by one common top-level directory name, such as mnt, tmp, usr, or Users"
sources: [S67]
---

# A shell variable followed by one common top-level directory name, such as mnt, tmp, usr, or Users

**Sources:** [S67](src.s67.md)

example: `rm -rf "$TMPDIR/mnt"`; why it counts: When the variable expands empty, the command removes `/mnt`
