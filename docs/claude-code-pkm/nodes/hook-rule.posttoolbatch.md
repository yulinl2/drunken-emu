---
id: hook-rule.posttoolbatch
kind: hook-rule
status: VERIFIED
title: "PostToolBatch"
sources: [S85]
---

# PostToolBatch

**Sources:** [S85](src.s85.md)

Runs once after every tool call in a batch has resolved, before Claude Code sends the next request to the model. `PostToolUse` fires once per tool, which means it fires concurrently when Claude makes parallel tool calls. `PostToolBatch` fires exactly once with the full batch, so it is the right place to inject context that depends on the set of tools that ran rather than on any single tool. There
