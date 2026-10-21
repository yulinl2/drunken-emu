---
id: env.claude-code-workflow-prefix-stagger-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS"
sources: [S81]
---

# CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS

**Sources:** [S81](src.s81.md)

Upper bound in milliseconds on how long a workflow agent waits for a same-prefix sibling's first response to begin before sending its own first request. When a fan-out starts several agents that share a prompt-cache prefix, Claude Code holds all but the first agent for up to this long so the rest read the cached prefix instead of each processing it uncached. Default `5000`. Set to `0` to disable the wait. When `DISABLE_PROMPT_CACHING` is set, agents never wait. Requires Claude Code v2.1.229 or later
