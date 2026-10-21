---
id: feature.where-the-keyword-works
kind: feature
status: VERIFIED
title: "Where the keyword works"
sources: [S29]
---

# Where the keyword works

**Sources:** [S29](src.s29.md)

The keyword is an opt-in only in a prompt you type yourself: at the interactive prompt, in an IDE extension panel, in a Remote Control client, or in an Agent SDK application that stamps your keyboard input's `origin` as `{ kind: "human" }`. It doesn't start a workflow when it reaches the session another way:
