---
id: permission-mode.a-trailing-command-substitution-after-a-critical-path
kind: permission-mode
status: VERIFIED
title: "A trailing command substitution after a critical path"
sources: [S67]
---

# A trailing command substitution after a critical path

**Sources:** [S67](src.s67.md)

example: `rm -rf ~/$(cmd)`; why it counts: Claude Code checks the path that would remain if the substitution expanded empty, here your home directory
