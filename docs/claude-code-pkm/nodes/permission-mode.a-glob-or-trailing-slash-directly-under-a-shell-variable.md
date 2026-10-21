---
id: permission-mode.a-glob-or-trailing-slash-directly-under-a-shell-variable
kind: permission-mode
status: VERIFIED
title: "A glob or trailing slash directly under a shell variable"
sources: [S67]
---

# A glob or trailing slash directly under a shell variable

**Sources:** [S67](src.s67.md)

example: `rm -rf "$DIR"/*`; why it counts: The command becomes a removal from the filesystem root when the variable is empty
