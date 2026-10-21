---
id: env.claude-code-enable-feedback-survey-for-otel
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL

**Sources:** [S81](src.s81.md)

Set to `1` to route the "How is Claude doing?" session quality survey to your own OpenTelemetry collector when Anthropic-bound nonessential traffic is blocked. Survey ratings are emitted only as OTEL events to your configured collector. No survey data is sent to Anthropic in this mode. Applies when `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC`, `DISABLE_TELEMETRY`, or `DO_NOT_TRACK` is set, and has no effect otherwise. `CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY` and the organization product feedback policy take precedence
