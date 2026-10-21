---
id: feature.a-background-session-shows-no-llm-gateway
kind: feature
status: VERIFIED
title: "A background session shows No LLM gateway"
sources: [S26]
---

# A background session shows No LLM gateway

**Sources:** [S26](src.s26.md)

If a background session shows `No LLM gateway`, it didn't get your gateway `ANTHROPIC_BASE_URL`, so its requests fail. Claude Code withheld it because you dispatched, woke, or restarted the session from a directory other than the folder the message names.
