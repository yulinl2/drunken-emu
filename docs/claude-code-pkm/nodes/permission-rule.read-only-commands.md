---
id: permission-rule.read-only-commands
kind: permission-rule
status: VERIFIED
title: "Read-only commands"
sources: [S66]
---

# Read-only commands

**Sources:** [S66](src.s66.md)

Claude Code recognizes a built-in set of Bash commands as read-only and runs them without a permission prompt in every mode, except as `permissions.blockReadsOutsideWorkingDirectories` changes for paths outside your working directories. The set includes `ls`, `cat`, `echo`, `pwd`, `head`, `tail`, `grep`, `find`, `wc`, `which`, `diff`, `stat`, `du`, `cd`, and read-only forms of `git`. The set is no
