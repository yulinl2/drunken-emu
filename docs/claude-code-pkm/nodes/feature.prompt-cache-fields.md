---
id: feature.prompt-cache-fields
kind: feature
status: VERIFIED
title: "Prompt cache fields"
sources: [S78]
---

# Prompt cache fields

**Sources:** [S78](src.s78.md)

The `prompt_cache` object summarizes how the session's main conversation is using the prompt cache. Claude Code computes it from the cache token counts in the API's responses, so it works on every provider.
