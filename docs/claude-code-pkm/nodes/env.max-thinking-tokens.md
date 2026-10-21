---
id: env.max-thinking-tokens
kind: env
status: VERIFIED
title: "MAX_THINKING_TOKENS"
sources: [S81]
---

# MAX_THINKING_TOKENS

**Sources:** [S81](src.s81.md)

Fixed token budget for extended thinking. Claude Code caps it at one token below the request's max output tokens and never below 1,024. See `CLAUDE_CODE_MAX_OUTPUT_TOKENS` for how that limit is set. When unset and thinking is enabled, models with adaptive reasoning choose their own thinking depth, and other models use the cap. Set to `0` to disable thinking on the Anthropic API, except on Opus 5.5, Sonnet 5.5, Haiku 5.5, and the Fable models, which can't have thinking turned off. On third-party providers, `0` omits the `thinking` parameter instead. With thinking turned off on the Anthropic API, Claude Code sends effort `high` instead of a higher level to models it knows don't accept that combination, such as Opus 5. For a positive value, Claude Code ignores the number itself on adaptive reasoning models, except when `CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING` turns adaptive reasoning off
