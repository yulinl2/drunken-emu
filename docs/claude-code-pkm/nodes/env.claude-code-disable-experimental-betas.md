---
id: env.claude-code-disable-experimental-betas
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS

**Sources:** [S81](src.s81.md)

Set to `1` to strip pre-release `anthropic-beta` request headers, the body fields that pair with them, and beta tool-schema fields such as `defer_loading` and `eager_input_streaming` from API requests. Use this when a proxy gateway rejects requests with an `Unexpected value(s)` error for the `anthropic-beta` header or an `Extra inputs are not permitted` error. Disable pre-release capabilities lists what the variable removes, including MCP tool search, and what Claude Code keeps sending
