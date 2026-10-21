---
id: hook-rule.hook-lifecycle
kind: hook-rule
status: VERIFIED
title: "Hook lifecycle"
sources: [S85]
---

# Hook lifecycle

**Sources:** [S85](src.s85.md)

Claude Code runs hooks at specific points during a session. When an event fires and a matcher matches, Claude Code passes JSON context about the event to your hook handler. For command hooks, input arrives on stdin. For HTTP hooks, it arrives as the POST request body. Your handler can then inspect the input, take action, and optionally return a decision.
