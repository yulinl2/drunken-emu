---
id: permission-mode.a-variable-that-the-same-command-assigns-from-a-directory-pr
kind: permission-mode
status: VERIFIED
title: "A variable that the same command assigns from a directory-printing substitution, such as $(pwd) or $(git rev-parse --show-toplevel)"
sources: [S67]
---

# A variable that the same command assigns from a directory-printing substitution, such as $(pwd) or $(git rev-parse --show-toplevel)

**Sources:** [S67](src.s67.md)

example: `D=$(pwd); rm -rf "$D"`; why it counts: The value can name your working directory or repository root
