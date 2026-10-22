---
id: hook.post-tool-use
kind: hook
status: VERIFIED
title: "PostToolUse"
sources: [S2]
---

# PostToolUse

**Sources:** [S2](src.s2.md)

Fires after a tool call succeeds. Matcher: tool name. Exit 2 does not block; stderr goes to Claude. Top-level decision block and additionalContext apply. Can replace the tool result with updatedToolOutput.
