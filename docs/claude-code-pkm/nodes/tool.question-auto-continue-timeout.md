---
id: tool.question-auto-continue-timeout
kind: tool
status: VERIFIED
title: "Question auto-continue timeout"
sources: [S82]
---

# Question auto-continue timeout

**Sources:** [S82](src.s82.md)

Questions stay open until you answer them. If you want a question you leave unanswered to eventually close and let Claude continue without you, set the `askUserQuestionTimeout` setting to `60s`, `5m`, or `10m`, either in your user `settings.json` or from the Question auto-continue timeout row in `/config`.
