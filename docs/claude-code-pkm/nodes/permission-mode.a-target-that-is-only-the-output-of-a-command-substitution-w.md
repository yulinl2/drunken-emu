---
id: permission-mode.a-target-that-is-only-the-output-of-a-command-substitution-w
kind: permission-mode
status: VERIFIED
title: "A target that is only the output of a command substitution, when the rm is recursive"
sources: [S67]
---

# A target that is only the output of a command substitution, when the rm is recursive

**Sources:** [S67](src.s67.md)

example: `rm -rf "$(pwd)"`; why it counts: Claude Code can't check the target before the command runs
