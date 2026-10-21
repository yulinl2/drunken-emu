---
id: feature.workflow-name-monitoring-usage
kind: feature
status: VERIFIED
title: "workflow.name"
sources: [S65]
---

# workflow.name

**Sources:** [S65](src.s65.md)

Name of the workflow that spawned this agent. User-authored names are replaced with `custom` unless the gate is set (gated by: `OTEL_LOG_TOOL_DETAILS`)
