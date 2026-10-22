---
id: feature.llm-gateway
kind: feature
status: VERIFIED
title: "LLM gateway"
sources: [S26]
---

# LLM gateway

**Sources:** [S26](src.s26.md)

If you route Claude Code through an LLM gateway, put the gateway variables in a settings file's `env` block rather than exporting them in your shell, and background sessions read them with the rest of their settings. Set in a settings file shows the block and which settings file to use for the credential.
