---
id: mod.rewrite-or-add-to-a-prompt
kind: mod
status: VERIFIED
title: "Rewrite or add to a prompt"
sources: [S55]
---

# Rewrite or add to a prompt

**Sources:** [S55](src.s55.md)

A `prompt.submit` hook sees each prompt before the turn starts, so it can rewrite the text or add to it. `e.text` is what was typed.
