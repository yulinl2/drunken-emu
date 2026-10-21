---
id: feature.complete-a-command-mid-prompt
kind: feature
status: VERIFIED
title: "Complete a command mid-prompt"
sources: [S83]
---

# Complete a command mid-prompt

**Sources:** [S83](src.s83.md)

Command completion also works partway through a prompt: type `/` after a space, then the first letters of a name, as in `run the tests, then /com`. Only commands whose names start with those letters match, so a file path such as `/tmp/notes.md` doesn't keep a list open. Claude Code runs a command itself only when the command starts your message.
