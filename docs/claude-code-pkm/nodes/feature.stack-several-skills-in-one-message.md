---
id: feature.stack-several-skills-in-one-message
kind: feature
status: VERIFIED
title: "Stack several skills in one message"
sources: [S32]
---

# Stack several skills in one message

**Sources:** [S32](src.s32.md)

When you type at the Claude Code prompt in your terminal, you can stack several skills at the start of one message. Through the Agent SDK or `claude -p`, Claude Code loads only the first skill, with the rest of the line as its arguments. At the terminal prompt, typing `/write-tests /fix-issue 123` loads both skills and passes the trailing text `123` as `$ARGUMENTS` to each of them.
