---
id: mod.start-a-turn-from-a-background-job
kind: mod
status: VERIFIED
title: "Start a turn from a background job"
sources: [S56]
---

# Start a turn from a background job

**Sources:** [S56](src.s56.md)

When a background job finds something that needs Claude's attention, it can start a turn by submitting a prompt with `$.prompt.submit({ text })`. Claude reads the text after a sentence that names your mod as the sender. To send it as the user's own words, without that sentence, add `asUser: true`. The call waits until the session is idle and then starts a new turn. It resolves when that turn start
