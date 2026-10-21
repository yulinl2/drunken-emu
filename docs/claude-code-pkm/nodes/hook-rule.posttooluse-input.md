---
id: hook-rule.posttooluse-input
kind: hook-rule
status: VERIFIED
title: "PostToolUse input"
sources: [S85]
---

# PostToolUse input

**Sources:** [S85](src.s85.md)

`PostToolUse` hooks fire after a tool has already executed successfully. The input includes both `tool_input`, the arguments sent to the tool, and `tool_response`, the result it returned. The exact schema for both depends on the tool. File-tool `tool_input` paths arrive in the same format as for PreToolUse: always absolute, with the platform's native separators, so backslashes on Windows. For an M
