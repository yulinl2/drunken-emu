---
id: feature.auto-mode-classifier-allowed-or-blocked-a-tool-call-or-claud
kind: feature
status: VERIFIED
title: "Auto mode classifier allowed or blocked a tool call, or Claude Code denied the call without a classifier verdict"
sources: [S65]
---

# Auto mode classifier allowed or blocked a tool call, or Claude Code denied the call without a classifier verdict

**Sources:** [S65](src.s65.md)

event: `tool_decision` where `classifier_verdict` is present. For a denial without a verdict, `classifier_verdict` is `"no_verdict"` or `"unavailable"`; key attributes: `classifier_verdict`, `permission_mode`, `tool_name`; `classifier_category` when you set `OTEL_LOG_TOOL_DETAILS=1`
