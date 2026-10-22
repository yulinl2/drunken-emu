---
id: plugin.check-when-the-prompt-appears
kind: plugin
status: VERIFIED
title: "Check when the prompt appears"
sources: [S48]
---

# Check when the prompt appears

**Sources:** [S48](src.s48.md)

The prompt appears only in interactive terminal sessions. In `claude -p` runs, in subagent runs, and in hook command output, the tag is stripped and no prompt is shown. All of these checks must also pass:
