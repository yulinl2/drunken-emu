---
id: process.ask-user-question-timeout
kind: process
status: VERIFIED
title: "Question auto-continue"
sources: [S6]
---

# Question auto-continue

**Sources:** [S6](src.s6.md)

An unanswered AskUserQuestion can close after 60 seconds, 5 minutes or 10 minutes, and Claude continues on its own judgment. The timer never starts in background sessions, screen-reader mode or Remote Control. See [askUserQuestionTimeout](setting.ask-user-question-timeout.md).
