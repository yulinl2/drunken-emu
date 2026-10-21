---
id: hook.user-prompt-submit
kind: hook
status: VERIFIED
title: "UserPromptSubmit"
sources: [S2]
---

# UserPromptSubmit

**Sources:** [S2](src.s2.md)

Fires when a prompt is submitted, before processing, including turns Claude starts itself. No matcher. Exit 2 blocks the prompt. Plain stdout is added to context. Top-level decision block: [Output: top-level block](hook-rule.output-top-level-block.md).
