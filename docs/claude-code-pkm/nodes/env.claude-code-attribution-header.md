---
id: env.claude-code-attribution-header
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ATTRIBUTION_HEADER"
sources: [S81]
---

# CLAUDE_CODE_ATTRIBUTION_HEADER

**Sources:** [S81](src.s81.md)

Set to `0` to omit the attribution block, which carries the client version and a prompt fingerprint, from the start of the system prompt. Caching on a direct connection to the Anthropic API is unaffected either way. In some direct-connection setups, Claude Code keeps the block on auto mode classifier requests even when you set `0`. In System prompt attribution block, check which connections and credentials this covers. Before v2.1.181 the block included a per-request token on custom base URLs and Microsoft Foundry connections, so on those versions set it to `0` when your LLM gateway caches on the request body or forwards requests to a third-party provider, or when you connect to Microsoft Foundry directly
