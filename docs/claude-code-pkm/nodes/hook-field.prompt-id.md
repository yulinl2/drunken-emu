---
id: hook-field.prompt-id
kind: hook-field
status: VERIFIED
title: "prompt_id"
sources: [S85]
---

# prompt_id

**Sources:** [S85](src.s85.md)

UUID identifying the user prompt currently being processed. Matches the `prompt.id` attribute on OpenTelemetry events, so you can correlate hook output with telemetry for a single prompt. Absent until the first user input
