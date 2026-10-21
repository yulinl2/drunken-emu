---
id: permission-rule.bash-permissions
kind: permission-rule
status: VERIFIED
title: "Bash"
sources: [S66]
---

# Bash

**Sources:** [S66](src.s66.md)

Bash rules match the whole command text, with `*` standing in for any text. Wildcard patterns shows which commands each rule shape matches and where to put the `*`. The rest of this section covers how Claude Code matches compound commands and wrappers, which wrappers and `find` actions a prefix rule can't approve, what a rule doesn't match, read-only commands, and redirections.
