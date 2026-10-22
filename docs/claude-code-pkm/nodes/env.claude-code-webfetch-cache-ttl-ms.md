---
id: env.claude-code-webfetch-cache-ttl-ms
kind: env
status: VERIFIED
title: "CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS"
sources: [S81]
---

# CLAUDE_CODE_WEBFETCH_CACHE_TTL_MS

**Sources:** [S81](src.s81.md)

Set to the number of milliseconds WebFetch keeps each fetched URL's response cached. The default is `900000`, which is 15 minutes. Takes plain digits only; `0`, a decimal, or any other spelling keeps the default. Claude Code reads the value once per launch, so a change in a settings `env` block applies when you next launch `claude`. Requires Claude Code v2.1.233 or later
