---
id: mod.call-a-model
kind: mod
status: VERIFIED
title: "Call a model"
sources: [S56]
---

# Call a model

**Sources:** [S56](src.s56.md)

A mod can send its own requests to a model for a small job such as classifying or summarizing text. `$.model.complete` sends your prompt on its own, and `$.model.fork({ prompt })` sends the current conversation with your prompt at the end.
