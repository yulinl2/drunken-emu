---
id: env.claude-code-disable-feedback-survey
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_FEEDBACK_SURVEY

**Sources:** [S81](src.s81.md)

Set to `1` to disable the "How is Claude doing?" session quality surveys. Surveys are also disabled when `DISABLE_TELEMETRY`, `DO_NOT_TRACK`, or `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` is set, unless `CLAUDE_CODE_ENABLE_FEEDBACK_SURVEY_FOR_OTEL` opts back in. To set a sample rate instead of disabling outright, use the `feedbackSurveyRate` setting. See Session quality surveys
