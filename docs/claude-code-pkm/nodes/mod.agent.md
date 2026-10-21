---
id: mod.agent
kind: mod
status: VERIFIED
title: "$.agent"
sources: [S54]
---

# $.agent

**Sources:** [S54](src.s54.md)

methods: `register`, `spawn`, `list`. `list()` returns this session's subagents and teammates, each with a `status` of `pending`, `running`, `waiting`, `idle`, `completed`, `failed`, or `killed`, where `idle` and `waiting` require Claude Code v2.1.289 or later.
