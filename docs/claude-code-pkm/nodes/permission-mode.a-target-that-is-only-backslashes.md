---
id: permission-mode.a-target-that-is-only-backslashes
kind: permission-mode
status: VERIFIED
title: "A target that is only backslashes"
sources: [S67]
---

# A target that is only backslashes

**Sources:** [S67](src.s67.md)

example: `rm -rf "\\"`; why it counts: Git Bash on Windows reads a lone backslash as the current drive's root, so the check applies on every platform
