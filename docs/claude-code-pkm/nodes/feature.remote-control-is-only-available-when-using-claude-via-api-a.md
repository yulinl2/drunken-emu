---
id: feature.remote-control-is-only-available-when-using-claude-via-api-a
kind: feature
status: VERIFIED
title: "\"Remote Control is only available when using Claude via api.anthropic.com\""
sources: [S21]
---

# "Remote Control is only available when using Claude via api.anthropic.com"

**Sources:** [S21](src.s21.md)

The session isn't talking to the Anthropic API directly, which Remote Control requires. This happens on Amazon Bedrock, Google Cloud's Agent Platform, and Microsoft Foundry. It also happens when `ANTHROPIC_BASE_URL` points at a host other than `api.anthropic.com`, such as an LLM gateway or proxy, even if you sign in with claude.ai. See the error reference for the full cause list.
