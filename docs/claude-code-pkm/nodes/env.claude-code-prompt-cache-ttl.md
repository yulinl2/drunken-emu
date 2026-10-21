---
id: env.claude-code-prompt-cache-ttl
kind: env
status: VERIFIED
title: "CLAUDE_CODE_PROMPT_CACHE_TTL"
sources: [S81]
---

# CLAUDE_CODE_PROMPT_CACHE_TTL

**Sources:** [S81](src.s81.md)

Set `5m` or `1h`, the only values Claude Code accepts, to choose the prompt cache TTL for the main conversation: your interactive, `-p`, and SDK turns, plus the helpers that run inline with them. Takes precedence over the `promptCacheTtl` setting and over `ENABLE_PROMPT_CACHING_1H`, and `FORCE_PROMPT_CACHING_5M` overrides it. The API bills 1-hour cache writes at a higher rate. Requires Claude Code v2.1.242 or later
