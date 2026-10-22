---
id: hook-rule.agent-hook-configuration
kind: hook-rule
status: VERIFIED
title: "Agent hook configuration"
sources: [S85]
---

# Agent hook configuration

**Sources:** [S85](src.s85.md)

Set `type` to `"agent"` and provide a `prompt` string, using `$ARGUMENTS` as a placeholder for the hook input JSON. The configuration fields are the same as prompt hooks, except that agent hooks have a longer default timeout of 60 seconds and no `continueOnBlock` field.
