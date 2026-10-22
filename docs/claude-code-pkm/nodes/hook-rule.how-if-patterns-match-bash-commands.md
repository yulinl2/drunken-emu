---
id: hook-rule.how-if-patterns-match-bash-commands
kind: hook-rule
status: VERIFIED
title: "How if patterns match Bash commands"
sources: [S85]
---

# How if patterns match Bash commands

**Sources:** [S85](src.s85.md)

For Bash patterns in the `if` field, whether your hook command runs depends on the shape of the pattern and the Bash command Claude is invoking. Leading `VAR=value` assignments are stripped before matching.
