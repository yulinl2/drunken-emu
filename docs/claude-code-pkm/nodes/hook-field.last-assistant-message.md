---
id: hook-field.last-assistant-message
kind: hook-field
status: VERIFIED
title: "last_assistant_message"
sources: [S85]
---

# last_assistant_message

**Sources:** [S85](src.s85.md)

The rendered error text shown in the conversation. Unlike `Stop` and `SubagentStop`, where this field holds Claude's conversational output, for `StopFailure` it contains the API error string itself, such as `"API Error: Rate limit reached"`
