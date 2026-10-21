---
id: env.claude-code-disable-nonstreaming-fallback
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK

**Sources:** [S81](src.s81.md)

Set to `1` to disable the non-streaming fallback when a streaming request fails mid-stream. Streaming errors propagate to the retry layer instead. Useful when a proxy or gateway causes the fallback to produce duplicate tool execution
