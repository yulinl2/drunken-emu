---
id: permission-rule.wrappers
kind: permission-rule
status: VERIFIED
title: "Wrappers"
sources: [S66]
---

# Wrappers

**Sources:** [S66](src.s66.md)

Before matching Bash rules, Claude Code strips a fixed set of wrappers, so a rule like `Bash(npm test *)` also matches `timeout 30 npm test`. The stripped wrappers are `timeout`, `time`, `nice`, `nohup`, and `stdbuf`, plus the shell builtins `command` and `builtin`, and zsh's `noglob`. Each runs its argument as the actual command. Two related forms aren't stripped: the query form `command -v`, whi
