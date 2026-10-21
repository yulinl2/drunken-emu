---
id: mod.send-one-prompt
kind: mod
status: VERIFIED
title: "Send one prompt"
sources: [S56]
---

# Send one prompt

**Sources:** [S56](src.s56.md)

Pass `model` and `prompt` to `$.model.complete`. `prompt` becomes the user message. To give the model instructions, such as a role or an output format, also pass `system`, which becomes the system prompt.
