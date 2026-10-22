---
id: hook-rule.subagentstart
kind: hook-rule
status: VERIFIED
title: "SubagentStart"
sources: [S85]
---

# SubagentStart

**Sources:** [S85](src.s85.md)

Runs when Claude spawns a subagent with the Agent tool, when Claude resumes a subagent, and each time an in-process agent team teammate handles a new message. Supports matchers to filter by agent type name. For built-in agents, this is the agent name like `general-purpose`, `Explore`, or `Plan`. For custom subagents, this is the `name` field from the agent's frontmatter, not the filename.
