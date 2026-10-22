---
id: env.claude-project-dir
kind: env
status: VERIFIED
title: "CLAUDE_PROJECT_DIR"
sources: [S2]
---

# CLAUDE_PROJECT_DIR

**Sources:** [S2](src.s2.md)

Project root where the session started. Available to command hooks, to stdio MCP servers and to plugin LSP servers. It does not move into a worktree; use cwd for the current directory. Not set in the Bash tool here ([Observation: CLAUDE_PROJECT_DIR unset in the Bash tool](obs.claude-project-dir-unset-in-bash.md)).

## Linked from

- [Observation: CLAUDE_PROJECT_DIR unset in the Bash tool](obs.claude-project-dir-unset-in-bash.md)
