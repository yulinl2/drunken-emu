---
id: feature.how-an-eval-run-works
kind: feature
status: VERIFIED
title: "How an eval run works"
sources: [S47]
---

# How an eval run works

**Sources:** [S47](src.s47.md)

An eval suite lives in a directory called `evals/` inside your plugin, laid out as Write and refine cases shows. Each case is its own subdirectory with a prompt and one or more graders. The prompt is something a person using your plugin might type, such as a request one of its skills should handle.
