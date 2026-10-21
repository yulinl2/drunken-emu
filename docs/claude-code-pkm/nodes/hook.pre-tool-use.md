---
id: hook.pre-tool-use
kind: hook
status: VERIFIED
title: "PreToolUse"
sources: [S2]
---

# PreToolUse

**Sources:** [S2](src.s2.md)

Fires before a tool call runs. Matcher: tool name. Exit 2 blocks the call. Decisions: allow, deny, ask or defer ([Output: PreToolUse decision](hook-rule.output-pre-tool-use.md)). A timeout does not block. EndConversation calls skip it. The if field applies here: [Hook field: if](hook-rule.if-field.md).

## Linked from

- [Hook](term.hook.md)
- [Observation: disarmed hook overhead](obs.hook-overhead-55ms.md)
