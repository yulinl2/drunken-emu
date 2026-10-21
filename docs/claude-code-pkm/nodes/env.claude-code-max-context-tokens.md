---
id: env.claude-code-max-context-tokens
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_CONTEXT_TOKENS"
sources: [S81]
---

# CLAUDE_CODE_MAX_CONTEXT_TOKENS

**Sources:** [S81](src.s81.md)

Override the context window size Claude Code assumes for the active model. As of v2.1.193, how it applies depends on how Claude Code resolves the model ID; see Correct the window for a gateway or custom model ID. Use this when routing to a model through `ANTHROPIC_BASE_URL` whose context window does not match the built-in size for its name
