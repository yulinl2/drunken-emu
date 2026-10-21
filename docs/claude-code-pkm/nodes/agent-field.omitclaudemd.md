---
id: agent-field.omitclaudemd
kind: agent-field
status: VERIFIED
title: "omitClaudeMd"
sources: [S25]
---

# omitClaudeMd

**Sources:** [S25](src.s25.md)

Set to `true` to start this subagent without the user, project, and local CLAUDE.md files in its initial context; managed policy files still load, except for managed subagents. Use it for subagents that take everything they need from the delegation prompt. Ignored when the agent runs as the main session agent via `--agent` or the `agent` setting. Requires Claude Code v2.1.271 or later (required: No)
