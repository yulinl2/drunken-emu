---
id: env.claude-code-simple-system-prompt
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT"
sources: [S81]
---

# CLAUDE_CODE_SIMPLE_SYSTEM_PROMPT

**Sources:** [S81](src.s81.md)

Choose between Claude Code's full system prompt and a shorter one with abbreviated tool descriptions. When unset, Haiku 4.5, Sonnet 5, Opus 4.7, and earlier models in those families use the full prompt by default, and newer models use the shorter one. Set to `1` to use the shorter prompt on any model. Set to `0`, `false`, `no`, or `off` to use the full prompt on any model, even where an experiment or server configuration would otherwise select the shorter one. Either prompt keeps the full tool set, hooks, MCP servers, and CLAUDE.md discovery
