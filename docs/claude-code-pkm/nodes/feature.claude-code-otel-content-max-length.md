---
id: feature.claude-code-otel-content-max-length
kind: feature
status: VERIFIED
title: "CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH"
sources: [S65]
---

# CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH

**Sources:** [S65](src.s65.md)

Content limit: the maximum length of content-bearing attributes such as model responses, tool content, system prompts, and raw API bodies, truncation marker included, in UTF-16 code units (default: 61440, i.e. 60 KB). The default is sized for backends that cap attribute values at 64 KB; raise it only if your backend accepts larger values, or lower it to cut telemetry volume. When an OpenTelemetry SDK attribute limit, `OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT` or one of its logrecord and span variants, is set lower, Claude Code truncates at that smaller value so the `[TRUNCATED ...]` marker stays within the SDK limit (example values: `262144`)
