---
id: feature.which-ids-claude-code-max-context-tokens-applies-to
kind: feature
status: VERIFIED
title: "Which IDs CLAUDE_CODE_MAX_CONTEXT_TOKENS applies to"
sources: [S70]
---

# Which IDs CLAUDE_CODE_MAX_CONTEXT_TOKENS applies to

**Sources:** [S70](src.s70.md)

On an LLM gateway or other custom deployment, Claude Code can assume a context window for the model ID that differs from the model's real window, whether or not it resolves the ID to a Claude model. Set `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to the window Claude Code should assume instead.
