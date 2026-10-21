---
id: env.claude-code-disable-unknown-model-window-enforcement
kind: env
status: VERIFIED
title: "CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT"
sources: [S81]
---

# CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT

**Sources:** [S81](src.s81.md)

Set to `1` to skip proactive auto-compaction when Claude Code doesn't recognize the model ID, such as an LLM gateway alias. Without this variable, Claude Code compacts at the context window it assumes for the ID. `CLAUDE_CODE_MAX_CONTEXT_TOKENS` can correct the assumed window instead; see Correct the window for a gateway or custom model ID for when each variable applies. Requires Claude Code v2.1.223 or later
