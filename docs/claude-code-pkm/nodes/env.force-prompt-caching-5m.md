---
id: env.force-prompt-caching-5m
kind: env
status: VERIFIED
title: "FORCE_PROMPT_CACHING_5M"
sources: [S81]
---

# FORCE_PROMPT_CACHING_5M

**Sources:** [S81](src.s81.md)

Set to `1` to force the 5-minute prompt cache TTL even when 1-hour TTL would otherwise apply. Overrides `CLAUDE_CODE_PROMPT_CACHE_TTL`, `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, `ENABLE_PROMPT_CACHING_1H`, and the `promptCacheTtl` and `subagentPromptCacheTtl` settings
