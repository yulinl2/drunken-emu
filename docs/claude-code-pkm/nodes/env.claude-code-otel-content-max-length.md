---
id: env.claude-code-otel-content-max-length
kind: env
status: VERIFIED
title: "CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH"
sources: [S81]
---

# CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH

**Sources:** [S81](src.s81.md)

Maximum length of content-bearing OpenTelemetry attributes (model responses, tool content, system prompts, raw API bodies), truncation marker included, in UTF-16 code units (default: 61440, i.e. 60 KB). Raise it only if your telemetry backend accepts attribute values larger than 64 KB, or lower it to cut telemetry volume. Requires Claude Code v2.1.214 or later. See Monitoring
