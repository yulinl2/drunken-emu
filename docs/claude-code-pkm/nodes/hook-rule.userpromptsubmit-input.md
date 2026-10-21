---
id: hook-rule.userpromptsubmit-input
kind: hook-rule
status: VERIFIED
title: "UserPromptSubmit input"
sources: [S85]
---

# UserPromptSubmit input

**Sources:** [S85](src.s85.md)

In addition to the common input fields, UserPromptSubmit hooks receive the `prompt` field containing the submitted text. Pasted content that collapsed to a `[Pasted text #N]` placeholder arrives expanded in place. In sessions where Claude Code marks pasted text for Claude, that expanded content sits between a `` line and a `` line, so account for those lines if your hook parses the prompt.
