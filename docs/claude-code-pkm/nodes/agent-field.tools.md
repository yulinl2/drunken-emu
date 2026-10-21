---
id: agent-field.tools
kind: agent-field
status: VERIFIED
title: "tools"
sources: [S25]
---

# tools

**Sources:** [S25](src.s25.md)

Tools the subagent can use, as a comma-separated string such as `Read, Grep, Bash` or a YAML list. Inherits every tool available to subagents if omitted. If no entry in the list resolves to a tool, the subagent usually fails to launch with an error naming the entries. To preload Skills into context, use the `skills` field rather than listing `Skill` here (required: No)
