---
id: env.enable-prompt-caching-1h
kind: env
status: VERIFIED
title: "ENABLE_PROMPT_CACHING_1H"
sources: [S81]
---

# ENABLE_PROMPT_CACHING_1H

**Sources:** [S81](src.s81.md)

Set to `1` to request a 1-hour prompt cache TTL instead of the default 5 minutes. Intended for API key, Amazon Bedrock, Google Cloud's Agent Platform, Microsoft Foundry, and Claude Platform on AWS users. For subscription users within included usage, Claude Code requests the 1-hour TTL automatically on the main conversation. Subscription users drawing on usage credits can set it to keep the 1-hour TTL. 1-hour cache writes are billed at a higher rate. To choose the TTL separately for the main conversation and for requests outside it, use `CLAUDE_CODE_PROMPT_CACHE_TTL` and `CLAUDE_CODE_SUBAGENT_PROMPT_CACHE_TTL`, which take precedence over this variable
