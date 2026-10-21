---
id: env.claude-code-skip-model-access-memory
kind: env
status: VERIFIED
title: "CLAUDE_CODE_SKIP_MODEL_ACCESS_MEMORY"
sources: [S81]
---

# CLAUDE_CODE_SKIP_MODEL_ACCESS_MEMORY

**Sources:** [S81](src.s81.md)

The startup model checks on Amazon Bedrock and Google Cloud's Agent Platform remember on this machine which models they found your account can't invoke, for up to a day. Set to `1` to turn that memory off. Requires Claude Code v2.1.285 or later
