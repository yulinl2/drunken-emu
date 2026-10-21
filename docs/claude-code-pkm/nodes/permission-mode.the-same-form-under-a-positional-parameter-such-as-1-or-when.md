---
id: permission-mode.the-same-form-under-a-positional-parameter-such-as-1-or-when
kind: permission-mode
status: VERIFIED
title: "The same form under a positional parameter such as $1 or $@, when nothing in the command gives it a value"
sources: [S67]
---

# The same form under a positional parameter such as $1 or $@, when nothing in the command gives it a value

**Sources:** [S67](src.s67.md)

example: `rm -rf "$1"/*`; why it counts: The command expands to a removal from the root
