---
id: feature.auto-approve-tools
kind: feature
status: VERIFIED
title: "Auto-approve tools"
sources: [S38]
---

# Auto-approve tools

**Sources:** [S38](src.s38.md)

Use `--allowedTools` to let Claude use certain tools without prompting. Listing `Read` and `Edit` lets Claude read and edit files without asking for permission, apart from reads from network paths. Listing `Bash` does the same for shell commands, except in a run that starts in auto mode, where Claude Code drops a bare `Bash` entry as a broad allow rule and auto mode evaluates each command instead.
