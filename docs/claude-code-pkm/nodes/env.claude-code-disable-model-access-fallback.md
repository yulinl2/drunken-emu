---
id: env.claude-code-disable-model-access-fallback
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_MODEL_ACCESS_FALLBACK

**Sources:** [S81](src.s81.md)

Set to `1` to stop Claude Code on Amazon Bedrock and Google Cloud's Agent Platform from switching to an older model when your account loses access to a session's model mid-session; the refused request fails at once instead. A fallback model chain you configure still switches on that refusal, and the startup model checks still fall back at launch. Requires Claude Code v2.1.285 or later
