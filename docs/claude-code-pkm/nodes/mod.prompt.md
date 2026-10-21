---
id: mod.prompt
kind: mod
status: VERIFIED
title: "$.prompt"
sources: [S54]
---

# $.prompt

**Sources:** [S54](src.s54.md)

methods: `submit`, `read`, `fill`, `suggest`, `compose`. Claude reads text from `submit({ text })` after a sentence that names your mod as the sender. `submit({ text, asUser: true })` sends the text as the user's own words, without that sentence.
