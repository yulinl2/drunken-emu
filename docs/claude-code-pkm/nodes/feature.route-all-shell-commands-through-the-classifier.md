---
id: feature.route-all-shell-commands-through-the-classifier
kind: feature
status: VERIFIED
title: "Route all shell commands through the classifier"
sources: [S64]
---

# Route all shell commands through the classifier

**Sources:** [S64](src.s64.md)

By default, narrow Bash and PowerShell allow rules such as `Bash(npm test)` stay in effect in auto mode. Claude Code resolves them before the classifier runs, unless the command carries per-command allowed domains. Claude Code suspends only the broad rules that grant arbitrary code execution, such as `Bash(*)` or wildcarded interpreters, together with every rule that names `Monitor`, because Monit
