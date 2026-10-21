---
id: feature.span-attributes
kind: feature
status: VERIFIED
title: "Span attributes"
sources: [S65]
---

# Span attributes

**Sources:** [S65](src.s65.md)

Every span carries the standard attributes plus a `span.type` attribute matching its name. The tables below list the additional attributes set on each span. The `llm_request`, `tool.execution`, and `hook` spans set OpenTelemetry status `ERROR` when they record a failure; the other spans always end with status `UNSET`.
