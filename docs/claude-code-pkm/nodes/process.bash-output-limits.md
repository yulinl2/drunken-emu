---
id: process.bash-output-limits
kind: process
status: VERIFIED
title: "Bash output limits"
sources: [S6]
---

# Bash output limits

**Sources:** [S6](src.s6.md)

A valid result is inline up to about 30,000 characters. Beyond that it is saved to a file, and a 2,000-character preview comes back. A failed result is inline up to about 10,000 characters, as a head-and-tail excerpt with no file path. Exit code 1 counts as valid only for grep, rg, egrep, fgrep, find, diff, test, [, git diff and git grep. Raise the inline ceiling with [bashOutputMaxChars](setting.bash-output-max-chars.md).

## Linked from

- [Bash](tool.bash.md)
- [bashOutputMaxChars](setting.bash-output-max-chars.md)
