---
id: feature.follow-subagent-messages
kind: feature
status: VERIFIED
title: "Follow subagent messages"
sources: [S38]
---

# Follow subagent messages

**Sources:** [S38](src.s38.md)

Messages from subagents and from skills that run in a subagent appear in the stream as `assistant` and `user` messages. Their `parent_tool_use_id` field says which run each one belongs to. Messages from the main conversation carry `null` in that field.
