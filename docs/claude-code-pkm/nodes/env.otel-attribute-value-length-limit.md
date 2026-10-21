---
id: env.otel-attribute-value-length-limit
kind: env
status: VERIFIED
title: "OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT"
sources: [S81]
---

# OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT

**Sources:** [S81](src.s81.md)

Standard OpenTelemetry SDK limit on attribute value length. Claude Code caps content-bearing telemetry attributes at the smaller of this and `CLAUDE_CODE_OTEL_CONTENT_MAX_LENGTH`, so the truncation marker stays within the SDK limit. Claude Code reads the `OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT` and `OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT` variants the same way, and the smallest set value applies to all signals. Requires Claude Code v2.1.214 or later. See Monitoring
