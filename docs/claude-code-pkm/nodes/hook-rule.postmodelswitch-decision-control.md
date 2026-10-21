---
id: hook-rule.postmodelswitch-decision-control
kind: hook-rule
status: VERIFIED
title: "PostModelSwitch decision control"
sources: [S85]
---

# PostModelSwitch decision control

**Sources:** [S85](src.s85.md)

Claude Code takes your hook's plain-text stdout on exit 0, or `additionalContext` from JSON output, and delivers it to Claude with the next request after the switch. In addition to the JSON output fields available to all hooks, you can return:
