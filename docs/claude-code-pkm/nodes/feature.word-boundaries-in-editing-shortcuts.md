---
id: feature.word-boundaries-in-editing-shortcuts
kind: feature
status: VERIFIED
title: "Word boundaries in editing shortcuts"
sources: [S83]
---

# Word boundaries in editing shortcuts

**Sources:** [S83](src.s83.md)

The word shortcuts `Alt+B`, `Alt+F`, `Alt+D`, `Option+Delete`, and `Ctrl+Backspace` treat a word as a run of letters and digits, so punctuation such as `_`, `.`, and `/` separates words. With `src/utils/foo.ts` in the prompt, repeated presses of `Alt+B` stop at the start of `ts`, `foo`, `utils`, and `src`.
