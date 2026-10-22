---
id: mod.hold-a-tool-call-until-the-user-decides
kind: mod
status: VERIFIED
title: "Hold a tool call until the user decides"
sources: [S55]
---

# Hold a tool call until the user decides

**Sources:** [S55](src.s55.md)

A hook can pause a tool call and ask the user what to do before it goes ahead. A `tool.call` hook can `await` before it calls `next` or returns, and the tool call stays pending until then. To put the question to the user, call `$.ui.ask`. It shows your question above a numbered list of your options, in the dialog Claude uses to ask you something, and resolves to the label the user picks. After you
