---
id: env.claude-code-always-enable-effort
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ALWAYS_ENABLE_EFFORT"
sources: [S81]
---

# CLAUDE_CODE_ALWAYS_ENABLE_EFFORT

**Sources:** [S81](src.s81.md)

Set to `1` to send the effort parameter with every request, even when Claude Code does not recognize the model ID as effort-capable. Use this when routing through an LLM gateway or third-party provider that serves models under custom identifiers. Models that reject the effort parameter at the API, including Claude Opus 4.1, Claude Sonnet 4.5, Claude Haiku 4.5, and earlier models, are still excluded so requests do not fail
