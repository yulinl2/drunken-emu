---
id: hook-rule.check-multiple-conditions-before-stopping
kind: hook-rule
status: VERIFIED
title: "Check multiple conditions before stopping"
sources: [S85]
---

# Check multiple conditions before stopping

**Sources:** [S85](src.s85.md)

This `Stop` hook uses a detailed prompt to check three conditions before allowing Claude to stop. `SubagentStop` hooks use the same format to evaluate whether a subagent should stop. If the model returns `"ok": false` because the condition isn't met yet, Claude continues working with the provided reason as its next instruction:
