---
id: mod.calls-and-background-work-after-the-user-interrupts-a-turn
kind: mod
status: VERIFIED
title: "Calls and background work after the user interrupts a turn"
sources: [S56]
---

# Calls and background work after the user interrupts a turn

**Sources:** [S56](src.s56.md)

The reason `the session was stopped and nobody has sent input since` in a result or error means the user stopped a running turn, such as with Esc or Stop. After that interruption, calls that start new work in the session are refused until the user's next input, such as a message at the prompt.
