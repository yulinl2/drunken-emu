---
id: feature.context-window-behind-an-llm-gateway
kind: feature
status: VERIFIED
title: "Context window behind an LLM gateway"
sources: [S70]
---

# Context window behind an LLM gateway

**Sources:** [S70](src.s70.md)

If you set `ANTHROPIC_BASE_URL` to an LLM gateway or another proxy, Claude Code gives each model it recognizes the same context window the model has on the Anthropic API. Fable 5.1, Fable 5, Sonnet 5 and later, Haiku 5.5, and Opus 4.7 and later get the 1M window with no `[1m]` variant to select, and a model that reaches 1M only through its `[1m]` variant, such as Opus 4.6, runs at 200K without it.
