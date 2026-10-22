---
id: tool.sendmessage
kind: tool
status: VERIFIED
title: "SendMessage"
sources: [S82]
---

# SendMessage

**Sources:** [S82](src.s82.md)

Sends a message to another agent: an agent team teammate, a subagent it resumes by agent ID or name, or one of your other Claude Code sessions, on this machine or beyond it. Messaging other sessions requires Claude Code v2.1.224 or later. Cross-session messaging covers which sessions Claude can reach, what a message looks like when it arrives, and how Claude gets a notice when another session goes idle. Claude can include an optional `summary` input, typically 5-10 words, that Claude Code shows as a one-line preview. When Claude omits it on a plain-text message, Claude Code uses the first line of the message as the summary. Claude Code truncates a summary longer than 200 characters with an ellipsis (permission required: No)
