---
id: setting.ask-user-question-timeout
kind: setting
status: VERIFIED
title: "askUserQuestionTimeout"
sources: [S6]
---

# askUserQuestionTimeout

**Sources:** [S6](src.s6.md)

60s, 5m or 10m auto-continues an unanswered AskUserQuestion. It can also be set from the /config row. Background sessions, screen-reader mode and Remote Control never start the timer. See [AskUserQuestion](tool.ask-user-question.md).

## Linked from

- [AskUserQuestion](tool.ask-user-question.md)
- [Question auto-continue](process.ask-user-question-timeout.md)
