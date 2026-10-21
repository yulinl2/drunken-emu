---
id: tool.sendfeedback-tool-behavior
kind: tool
status: VERIFIED
title: "SendFeedback tool behavior"
sources: [S82]
---

# SendFeedback tool behavior

**Sources:** [S82](src.s82.md)

Claude-drafted feedback is a feedback report about Claude Code that Claude writes for you. It requires Claude Code v2.1.238 or later. Claude Code saves each draft on your machine under `~/.claude/feedback/drafts/`, and nothing reaches Anthropic until you send it. Claude drafts one with the SendFeedback tool when:
