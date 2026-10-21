---
id: feature.audit-security-events
kind: feature
status: VERIFIED
title: "Audit security events"
sources: [S65]
---

# Audit security events

**Sources:** [S65](src.s65.md)

OpenTelemetry events are the audit data source for Claude Code activity. Every event carries identity attributes that tie tool calls, MCP activity, and permission decisions back to the user who triggered them. The OTLP logs exporter can deliver these events to any Security Information and Event Management (SIEM) platform with an OTLP receiver, or to an OpenTelemetry Collector that forwards to your
