---
id: agent-field.name
kind: agent-field
status: VERIFIED
title: "name"
sources: [S25]
---

# name

**Sources:** [S25](src.s25.md)

Unique identifier of at most 256 characters, such as `code-reviewer` or `reviewer-v2`. Hooks receive this value as `agent_type`. The filename doesn't have to match. Names can't contain `:`, which is reserved for plugin-scoped identifiers such as `my-plugin:reviewer` (required: Yes)
