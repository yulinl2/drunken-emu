---
id: feature.ended-on-an-api-error-and-scored-0-without-grading
kind: feature
status: VERIFIED
title: "\"ended on an API error and scored 0 without grading\""
sources: [S47]
---

# "ended on an API error and scored 0 without grading"

**Sources:** [S47](src.s47.md)

This stderr warning means the API answered at least one run's last request with an HTTP error, such as a rate limit or a plan usage limit. Such a run scores 0 with no grader results, and the command exits non-zero whatever the scores and `--threshold` are.
