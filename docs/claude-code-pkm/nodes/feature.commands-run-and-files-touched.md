---
id: feature.commands-run-and-files-touched
kind: feature
status: VERIFIED
title: "Commands run and files touched"
sources: [S65]
---

# Commands run and files touched

**Sources:** [S65](src.s65.md)

event: `tool_result` (executed) or `tool_decision` (rejected) with `OTEL_LOG_TOOL_DETAILS=1`; key attributes: `tool_parameters`; `tool_input` (`tool_result` only)
