---
id: feature.choose-and-weight-graders
kind: feature
status: VERIFIED
title: "Choose and weight graders"
sources: [S47]
---

# Choose and weight graders

**Sources:** [S47](src.s47.md)

A grader's frontmatter sets its `type`, and optionally a `weight` that makes it count for more of the run's score and an `arm` that controls how it's scored against the baseline. Of the six types, `regex`, `tool_used`, `tool_order`, and `file_exists` are computed from the transcript and files and cost nothing, while `llm` and `baseline` call a judge model and add to the run's cost.
