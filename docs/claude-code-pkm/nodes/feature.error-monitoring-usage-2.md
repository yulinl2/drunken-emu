---
id: feature.error-monitoring-usage-2
kind: feature
status: VERIFIED
title: "error"
sources: [S65]
---

# error

**Sources:** [S65](src.s65.md)

Error category string when execution failed, such as `Error:ENOENT` or `ShellError`. Contains the full error message instead when the gate is set (gated by: `OTEL_LOG_TOOL_DETAILS`)
