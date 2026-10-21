---
id: env.claude-code-enable-prompt-suggestion
kind: env
status: VERIFIED
title: "CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION"
sources: [S81]
---

# CLAUDE_CODE_ENABLE_PROMPT_SUGGESTION

**Sources:** [S81](src.s81.md)

Set to `false` to turn off prompt suggestions, the grayed-out predictions that appear in your prompt input. Takes precedence over the `promptSuggestionEnabled` setting, which is what the Prompt suggestions toggle in `/config` writes. Claude Code also pauses suggestions while your account is close to or at its usage limit. Set to `true` to keep that pause from applying until you reach the limit. Requires Claude Code v2.1.238 or later. See Prompt suggestions
