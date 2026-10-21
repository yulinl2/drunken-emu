---
id: tool.listagents
kind: tool
status: VERIFIED
title: "ListAgents"
sources: [S82]
---

# ListAgents

**Sources:** [S82](src.s82.md)

Lists the agents Claude can message with `SendMessage`: subagents in the session, agent team teammates, your other local Claude Code sessions, and, while this session is connected to Remote Control, your cloud sessions and your Remote Control sessions on other machines. Backs the `/list-agents` command. See cross-session messaging. Requires Claude Code v2.1.224 or later, and appears only in sessions where cross-session messaging is enabled. Teammate rows and the first line showing this session's own name require v2.1.239 or later (permission required: No)
