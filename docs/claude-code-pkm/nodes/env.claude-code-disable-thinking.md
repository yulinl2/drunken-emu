---
id: env.claude-code-disable-thinking
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_THINKING"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_THINKING

**Sources:** [S81](src.s81.md)

Set to `1` to omit the `thinking` parameter from API requests entirely. This is a compatibility option for proxies and gateways that reject the parameter. On models that think by default, omitting the parameter means the model may still think. To explicitly disable extended thinking on the Anthropic API, use `MAX_THINKING_TOKENS=0` instead. Neither variable turns thinking off on Opus 5.5, Sonnet 5.5, Haiku 5.5, or the Fable models, which can't have thinking turned off. On third-party providers, `MAX_THINKING_TOKENS=0` likewise omits the parameter, so the two variables behave the same there
