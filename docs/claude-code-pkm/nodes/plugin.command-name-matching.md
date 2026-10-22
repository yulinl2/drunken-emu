---
id: plugin.command-name-matching
kind: plugin
status: VERIFIED
title: "Command name matching"
sources: [S60]
---

# Command name matching

**Sources:** [S60](src.s60.md)

Claude Code records one command name for each shell command Claude runs: the first token after any leading environment variable assignments and `sudo`. Compound commands contribute only their leading command, so `cd infra && terraform plan` records `cd`, not `terraform`.
