---
id: env.claude-code-disable-legacy-model-remap
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_LEGACY_MODEL_REMAP

**Sources:** [S81](src.s81.md)

Set to `1` to prevent automatic remapping of Opus 4 and Opus 4.1 to the current Opus version on the Anthropic API. Use when you intentionally want to pin an older model. The remap does not run on Amazon Bedrock, Google Cloud's Agent Platform, or Microsoft Foundry
