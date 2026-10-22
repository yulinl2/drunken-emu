---
id: feature.tool-call-allowed-or-denied-and-where-the-decision-came-from
kind: feature
status: VERIFIED
title: "Tool call allowed or denied, and where the decision came from, such as a rule, a hook, or the user"
sources: [S65]
---

# Tool call allowed or denied, and where the decision came from, such as a rule, a hook, or the user

**Sources:** [S65](src.s65.md)

event: `tool_decision`; key attributes: `decision`, `source`, `classifier_verdict`, `permission_mode`, `tool_name`; `tool_parameters` when you set `OTEL_LOG_TOOL_DETAILS=1`
