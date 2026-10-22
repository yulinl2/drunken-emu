---
id: permission-rule.compound-commands
kind: permission-rule
status: VERIFIED
title: "Compound commands"
sources: [S66]
---

# Compound commands

**Sources:** [S66](src.s66.md)

Deny and ask rules apply when any subcommand matches them, including a command nested inside a subshell, a command substitution, or a control-flow body such as a `for` loop. An ask rule like `Bash(git clean *)` still prompts you for `cd /tmp && git clean -f` or `echo "$(git clean -f)"`, even in auto mode.
