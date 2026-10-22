---
id: feature.prompt-rejected-as-too-short
kind: feature
status: VERIFIED
title: "Prompt rejected as too short"
sources: [S26]
---

# Prompt rejected as too short

**Sources:** [S26](src.s26.md)

The dispatch input expects a task description, not a conversational opener. A prompt shorter than four characters is rejected with a `Too short` hint so a stray keystroke doesn't start a session. Describe what you want the session to do, such as `investigate the flaky checkout test`.
