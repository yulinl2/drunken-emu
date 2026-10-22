---
id: env.claude-code-disable-adaptive-thinking
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_ADAPTIVE_THINKING

**Sources:** [S81](src.s81.md)

Set to `1` to disable adaptive reasoning on Opus 4.6 and Sonnet 4.6 and fall back to the fixed thinking budget controlled by `MAX_THINKING_TOKENS`. Has no effect on Fable models, Sonnet 5 and later, Haiku 5.5, or Opus 4.7 and later, which always use adaptive reasoning
