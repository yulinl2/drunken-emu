---
id: env.claude-code-native-cursor
kind: env
status: VERIFIED
title: "CLAUDE_CODE_NATIVE_CURSOR"
sources: [S81]
---

# CLAUDE_CODE_NATIVE_CURSOR

**Sources:** [S81](src.s81.md)

Set to `1` to show the terminal's own cursor at the input caret instead of a drawn block. The cursor respects the terminal's blink, shape, and focus settings. Setting `0` reads the same as leaving the variable unset, so it doesn't bring the drawn block back in a session where the terminal's own cursor is already on
