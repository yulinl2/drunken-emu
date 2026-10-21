---
id: env.claude-code-max-output-tokens
kind: env
status: VERIFIED
title: "CLAUDE_CODE_MAX_OUTPUT_TOKENS"
sources: [S81]
---

# CLAUDE_CODE_MAX_OUTPUT_TOKENS

**Sources:** [S81](src.s81.md)

Set the maximum number of output tokens for most requests. Defaults and caps vary by model; see max output tokens. Claude Code lowers a value above a model's cap to the cap. For a model ID Claude Code can't resolve to a model it knows, the default is 32000 and the cap is 128000. Increasing this value reduces the effective context window available before auto-compaction triggers
