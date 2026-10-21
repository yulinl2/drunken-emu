---
id: hook-field.effort
kind: hook-field
status: VERIFIED
title: "effort"
sources: [S85]
---

# effort

**Sources:** [S85](src.s85.md)

Object with a `level` field holding the effort level in effect when the hook runs: `"low"`, `"medium"`, `"high"`, `"xhigh"`, or `"max"`. If you set a level the active model doesn't support, `level` reports the level Claude Code ran instead; Adjust effort level says how it picks that level. The object matches the status line `effort` field. Present for events that fire within a tool-use context, such as `PreToolUse`, `PostToolUse`, `Stop`, and `SubagentStop`, when the current model supports the effort parameter. The level is also available to hook commands and the Bash tool as the `$CLAUDE_EFFORT` environment variable.
